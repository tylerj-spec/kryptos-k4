#!/usr/bin/env python3
"""R87 blind sandbox builder (R53 isolation without Docker; r84/sealed/make_sandbox.py with R87's allowlist). Copies
ONLY the files the blind runner needs into BOX (same relative paths), plus the letter model and one input TSV, and
checks every copied repository file against r87/PROTOCOL.sha256. r87/sealed/run_isolated87.sh then runs the runner in
a new mount and network namespace in which /workspace, /tmp/claude-0 and /root are hidden and there is no network.
Tripwire (not a proof): no copied code file or input may contain a published K4 plaintext word or carry a clue-like
file name. The two generic scorer tables are exempt; their hits are reported (the R59 word model is a 226k-entry
generic English list that contains EAST, NORTH, NORTHEAST, BERLIN, CLOCK as ordinary words; r84 "Disclosures").
Usage: make_sandbox87.py BOX LM.bin INPUT.tsv"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ["r87/blind/run87.py", "r87/blind/solve87.py", "r87/blind/anneal.c", "r87/rotor87.py", "r75/core.py",
        "r59/blind/LM_SHA256"]
DICTS = ["k4kit/data/word_model_orth.tsv", "k4kit/data/quad_log10.f32"]
CLUE = re.compile(rb"EASTNORTHEAST|NORTHEAST|BERLINCLOCK|BERLIN|CLOCK", re.I)
CLUE_NAME = re.compile(r"reveal|clue|crib|known.?plain|anchor|truth", re.I)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build(box, lm, inp, protocol=ROOT / "r87/PROTOCOL.sha256"):
    box, lm, inp = Path(box), Path(lm), Path(inp)
    if box.exists():
        raise SystemExit("refusing to reuse an existing sandbox")
    data = inp.read_bytes()
    if CLUE.search(data):
        raise SystemExit("tripwire: published word in the input")
    lines = data.decode().splitlines()
    if not (lines and lines[0] == "id\tciphertext" and
            all(re.fullmatch(r"[A-Z0-9_]+\t[A-Z]{97}", l) for l in lines[1:] if l)):
        raise SystemExit("input must be id<TAB>97 letters only (no key, plaintext, mask or position fields)")
    lm_want = (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]
    if sha(lm) != lm_want:
        raise SystemExit("letter model hash mismatch")
    pinned = {l.split()[-1]: l.split()[0] for l in Path(protocol).read_text().splitlines() if l.strip()}
    rep = {"files": {}, "dictionary_clue_word_hits": {}, "input": None}
    for rel in CODE + DICTS:
        if pinned.get(rel) != sha(ROOT / rel):
            raise SystemExit(f"{rel} not pinned or changed")
        if CLUE_NAME.search(rel):
            raise SystemExit(f"clue-like name {rel}")
        body = (ROOT / rel).read_bytes()
        if rel in CODE:
            if CLUE.search(body):
                raise SystemExit(f"tripwire: published word in {rel}")
        else:
            rep["dictionary_clue_word_hits"][rel] = len(CLUE.findall(body))
        (box / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, box / rel)
        rep["files"][rel] = sha(box / rel)
    (box / "input").mkdir()
    shutil.copyfile(inp, box / "input/TARGET.tsv")
    (box / "lm").mkdir()
    shutil.copyfile(lm, box / "lm/lm6.v2.bin")
    (box / "out").mkdir()
    rep["input"] = {"source": inp.name, "sha256": sha(box / "input/TARGET.tsv"), "rows": len(lines) - 1}
    rep["letter_model_sha256"] = lm_want
    (box / "SANDBOX.json").write_text(json.dumps(rep, indent=1) + "\n")
    return rep


def main():
    rep = build(*sys.argv[1:4])
    print(json.dumps({"copied": len(rep["files"]), "input_rows": rep["input"]["rows"],
                      "dictionary_hits": rep["dictionary_clue_word_hits"]}))


if __name__ == "__main__":
    main()
