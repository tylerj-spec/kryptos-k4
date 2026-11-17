#!/usr/bin/env python3
"""R84 blind sandbox builder (R53 isolation, without Docker). Copies ONLY the allowlisted files the blind runner needs
into BOX (same relative paths), plus the letter model and one input TSV, and checks every copied repository file
against r84/PROTOCOL.sha256. r84/sealed/run_isolated.sh then runs the unchanged R80a runner inside a new mount and
network namespace in which /workspace, /tmp/claude-0 and /root are hidden and there is no network, so the process can
read nothing but BOX and the system's Python, numpy and gcc.
Tripwire (not a proof): every copied code file and the input must not contain a published K4 plaintext word or a
clue-like file name. The two generic dictionaries (word model, Kryptos K1-K3 word list) are exempt and their hits are
reported: the R59 word model is a 226k-entry generic English list that contains EAST, NORTH, NORTHEAST, BERLIN, CLOCK
as ordinary words (r84/PREREGISTRATION.md, "Disclosures").
Usage: make_sandbox.py BOX LM.bin INPUT.tsv"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ["r80a/blind/run.py", "r80a/two80.py", "r80a/twostage.c", "r79/solver.py", "r79/slotsolve.c", "r75/core.py",
        "r76/alphabets.py", "r38/aca_alphabet.py", "r59/blind/LM_SHA256"]
DICTS = ["r75/data/kryptos_words.txt", "k4kit/data/word_model_orth.tsv", "k4kit/data/quad_log10.f32"]
CLUE = re.compile(rb"EASTNORTHEAST|NORTHEAST|BERLINCLOCK|BERLIN|CLOCK", re.I)
CLUE_NAME = re.compile(r"reveal|clue|crib|known.?plain|anchor|truth", re.I)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    box, lm, inp = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    if box.exists():
        raise SystemExit("refusing to reuse an existing sandbox")
    data = inp.read_bytes()
    assert not CLUE.search(data), "tripwire: published word in the input"
    lines = data.decode().splitlines()
    assert lines[0] == "id\tciphertext" and all(re.fullmatch(r"[A-Z0-9_]+\t[A-Z]{97}", l) for l in lines[1:] if l), \
        "input must be id<TAB>97 letters only (no key, plaintext, mask or position fields)"
    lm_want = (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]
    assert sha(lm) == lm_want, "letter model hash mismatch"
    pinned = {l.split()[-1]: l.split()[0] for l in (ROOT / "r84/PROTOCOL.sha256").read_text().splitlines() if l}
    rep = {"files": {}, "dictionary_clue_word_hits": {}, "input": None}
    for rel in CODE + DICTS:
        assert pinned.get(rel) == sha(ROOT / rel), f"{rel} not pinned or changed"
        assert not CLUE_NAME.search(rel), rel
        data = (ROOT / rel).read_bytes()
        if rel in CODE:
            assert not CLUE.search(data), f"tripwire: published word in {rel}"
        else:
            rep["dictionary_clue_word_hits"][rel] = len(CLUE.findall(data))
        (box / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, box / rel)
        rep["files"][rel] = sha(box / rel)
    (box / "input").mkdir()
    shutil.copyfile(inp, box / "input/TARGET.tsv")
    (box / "lm").mkdir()
    shutil.copyfile(lm, box / "lm/lm6.v2.bin")
    (box / "out").mkdir()
    rep["input"] = {"source": str(inp), "sha256": sha(box / "input/TARGET.tsv"), "rows": len(lines) - 1}
    rep["letter_model_sha256"] = lm_want
    (box / "SANDBOX.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({"copied": len(rep["files"]), "input_rows": rep["input"]["rows"],
                      "dictionary_hits": rep["dictionary_clue_word_hits"]}))


if __name__ == "__main__":
    main()
