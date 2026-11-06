#!/usr/bin/env python3
"""R70 BLIND runner. Reads only an "id<TAB>ciphertext" TSV, the five pinned normalised source texts, r61/routes.txt and
the generic R59 English models; no K4 clue data. For each ciphertext it runs r70/blind/rk_text_scan.cpp once (every
source x offset x 21 rows x 6 conventions; see that file), keeps the top TOPOUT decodes in OUTDIR/work/<id>.jsonl and
reports the best (rank 0) in RESULTS.jsonl.
Usage: python3 -I r70/blind/run.py IN.tsv OUTDIR ENGLISH_LM NORM_DIR SCANNER [THREADS=4]
A finished ciphertext is reused after an interruption only if its stored digest matches."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORDS_EN = ROOT / "k4kit/data/word_model_orth.tsv"
ROUTES = ROOT / "r61/routes.txt"
SOURCES = ("BERLIN_1912", "EGYPT_1908", "MURRAY_1907", "COOK_1876", "BUDGE_1898")
NORM_SHA256 = {"BERLIN_1912": "0f4f4718ecf0fe6c4a8d800c1a25757c4e0a7eebf751c36981a8d680b9883f7d",
               "EGYPT_1908": "c88ef5e1681fc60ea19808f94124f5bce840dcd979e5738355f35f36b04aa918",
               "MURRAY_1907": "7aa620482cd7144fd2aed1b815443232aac816ed97556428fd027b4566b0184a",
               "COOK_1876": "bb3e3e3c1047e334d79f694c3b2ee07e78de93c4f3742f64eab2e6e0f12e830e",
               "BUDGE_1898": "373f57b9fef6f6b9c1a561a8ff51451c043eca11847748069474d4630cb44e61"}
TOPA, TOPOUT = "1000", "200"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    inp, out, lm_en, norm, scanner = (Path(a) for a in sys.argv[1:6])
    threads = sys.argv[6] if len(sys.argv) > 6 else "4"
    if sha(lm_en) != (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]:
        raise SystemExit("English LM sha256 mismatch")
    for k, h in NORM_SHA256.items():
        if sha(norm / f"{k}.txt") != h:
            raise SystemExit(f"source sha256 mismatch: {k}")
    hashes = {"english_lm": sha(lm_en), "words_en": sha(WORDS_EN), "routes": sha(ROUTES), "scanner": sha(scanner),
              **NORM_SHA256}
    out.mkdir(parents=True, exist_ok=True)
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    work = out / "work"
    work.mkdir(exist_ok=True)
    rows = [l.split("\t") for l in inp.read_text().splitlines() if l and not l.startswith("id\t")]
    ids = [r[0] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate ids")
    res = {}
    for rid, ct in rows:
        if len(ct) != 97 or not ct.isalpha() or not ct.isupper():
            raise SystemExit(f"bad ciphertext {rid}")
        dig = hashlib.sha256(json.dumps({"ct": ct, "hashes": hashes, "topa": TOPA, "topout": TOPOUT},
                                        sort_keys=True).encode()).hexdigest()
        done = work / f"{rid}.digest"
        jl = work / f"{rid}.jsonl"
        if not (done.exists() and done.read_text().strip() == dig and jl.exists()):
            args = [str(scanner), str(lm_en), str(WORDS_EN), str(ROUTES), ct, str(jl), threads, TOPA, TOPOUT] + \
                   [f"{k}={norm / (k + '.txt')}" for k in SOURCES]
            with open(work / f"{rid}.log", "w") as lg:
                if subprocess.run(args, stderr=lg).returncode != 0:
                    raise RuntimeError(f"scanner failed: {rid}")
            done.write_text(dig + "\n")
        top = [json.loads(l) for l in jl.read_text().splitlines() if l.strip()]
        if len(top) != int(TOPOUT):
            raise RuntimeError(f"short output: {rid}")
        res[rid] = {k: top[0][k] for k in ("source", "offset", "path", "model", "convention", "lm6", "word", "total",
                                           "plaintext", "keytext")}
        print(f"R70 {rid} {res[rid]['total']:.2f} {res[rid]['source']}@{res[rid]['offset']} {res[rid]['path']} "
              f"{res[rid]['model']} {res[rid]['convention']}", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps({"id": i, **res[i]}, separators=(",", ":")) + "\n" for i in ids))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r70/blind/rk_text_scan.cpp", "scanner_source"),
           (scanner, "scanner_binary"), (lm_en, "english_lm"), (WORDS_EN, "english_words"), (ROUTES, "routes")] + \
          [(norm / f"{k}.txt", "source") for k in SOURCES] + \
          [(Path(__file__), "runner"), (ROOT / "r70/PREREGISTRATION.md", "protocol")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    (out / "WORK.sha256").write_text("".join(f"{sha(p)}  {p.name}\n" for p in sorted(work.iterdir())))
    print(f"R70 froze {len(ids)} results in {out}")


if __name__ == "__main__":
    main()
