#!/usr/bin/env python3
"""R42 BLIND runner. Reads only the *_ct.txt ciphertexts in EXPDIR, the quadgram table and the two key texts.
Stage 1 (ca_screen): every setting of the declared family (fixed plaintext alphabet, free cipher alphabet),
global top 20,000 by the unigram-optimal assignment score.
Stage 2 (casolve): those 20,000 annealed over the cipher alphabet, 8 restarts each.
Stage 3: the 50 best stage-2 rows re-solved with 64 restarts. Then everything is hashed into FROZEN.sha256.
Usage: python3 -I r42/blind/run.py EXPDIR"""
import csv
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R42 = HERE.parent
REPO = R42.parent
QUAD = REPO / "k4kit/data/quad_log10.f32"
CARTER = REPO / "r34/carter_az.txt"
K1K3 = REPO / "k4kit/data/k1k3_plaintext.txt"
HASHES = {CARTER: "6761a5075869325f708e1d81f8bd0efeeab5aaaad43206e1551ed53243f13ee0"}
TOPK, S2_RESTARTS, S3_ROWS, S3_RESTARTS, WORKERS = 20000, 8, 50, 64, 4
EXPECTED = 31294872   # settings per ciphertext, as pre-registered


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parallel(cmds):
    """Run commands, at most WORKERS at a time; any failure aborts."""
    running = []
    for c in cmds:
        while len(running) >= WORKERS:
            running.pop(0).wait() == 0 or sys.exit(f"FAILED: {c}")
        running.append(subprocess.Popen([str(x) for x in c]))
    for p in running:
        if p.wait() != 0:
            sys.exit("FAILED: a worker")


def main():
    exp = Path(sys.argv[1]).resolve()
    proto = (R42 / "PROTOCOL.sha256").read_text().split()[0]
    assert sha(R42 / "PREREGISTRATION.md") == proto, "PREREGISTRATION.md does not match PROTOCOL.sha256"
    for p, h in HASHES.items():
        assert sha(p) == h, f"hash mismatch {p}"
    out = exp / "out"
    if (exp / "FROZEN.sha256").exists() or out.exists():
        sys.exit("refusing to overwrite an existing run")
    out.mkdir()
    src = out / "blind_src"
    src.mkdir()
    for name in ("ca_screen.cpp", "casolve.cpp", "run.py"):
        shutil.copy2(HERE / name, src / name)
    for name in ("ca_screen", "casolve"):
        subprocess.run(["g++", "-std=c++17", "-O3", "-march=native", str(src / f"{name}.cpp"), "-o", str(out / name)], check=True)
    tags = sorted(f.name[:-len("_ct.txt")] for f in exp.glob("*_ct.txt"))
    print("ciphertexts:", tags, flush=True)
    parallel([[out / "ca_screen", exp / f"{t}_ct.txt", QUAD, CARTER, K1K3, TOPK, out / f"{t}_top.tsv", out / f"{t}_hist.tsv"] for t in tags])
    for t in tags:
        n = int((out / f"{t}_hist.tsv").read_text().split()[2])
        assert n == EXPECTED, (t, n)
    print("stage 1 done", flush=True)
    parallel([[out / "casolve", exp / f"{t}_ct.txt", QUAD, out / f"{t}_top.tsv", out / f"{t}_s2.tsv", S2_RESTARTS, "s2", TOPK] for t in tags])
    print("stage 2 done", flush=True)
    for t in tags:
        rows = list(csv.DictReader(open(out / f"{t}_s2.tsv"), delimiter="\t"))
        assert len(rows) == TOPK, (t, len(rows))
        rows.sort(key=lambda r: (-float(r["score"]), r["setting"]))
        keys = {r["setting"]: r["key"] for r in csv.DictReader(open(out / f"{t}_top.tsv"), delimiter="\t")}
        with open(out / f"{t}_s3_in.tsv", "w") as f:
            f.write("rank\tL1\tsetting\tkey\n")
            for r in rows[:S3_ROWS]:
                f.write(f"{r['rank']}\t{r['L1']}\t{r['setting']}\t{keys[r['setting']]}\n")
    parallel([[out / "casolve", exp / f"{t}_ct.txt", QUAD, out / f"{t}_s3_in.tsv", out / f"{t}_s3.tsv", S3_RESTARTS, "s3", S3_ROWS] for t in tags])
    print("stage 3 done", flush=True)
    for t in tags:
        s2 = list(csv.DictReader(open(out / f"{t}_s2.tsv"), delimiter="\t"))
        s3 = {r["setting"]: r for r in csv.DictReader(open(out / f"{t}_s3.tsv"), delimiter="\t")}
        final = []
        for r in s2:
            b = r
            if r["setting"] in s3 and float(s3[r["setting"]]["score"]) > float(r["score"]):
                b = s3[r["setting"]]
            final.append({"L1_rank": r["rank"], "L1": r["L1"], "setting": r["setting"], "s2_score": r["score"],
                          "s3_score": s3[r["setting"]]["score"] if r["setting"] in s3 else "",
                          "score": b["score"], "plaintext": b["plaintext"], "cipher_alphabet": b["cipher_alphabet"]})
        final.sort(key=lambda r: (-float(r["score"]), r["setting"]))
        cols = ["L1_rank", "L1", "setting", "s2_score", "s3_score", "score", "plaintext", "cipher_alphabet"]
        for name, rows in ((f"{t}_final.tsv", final), (f"{t}_top100.tsv", final[:100])):
            with open(out / name, "w") as f:
                f.write("\t".join(cols) + "\n")
                for r in rows:
                    f.write("\t".join(r[c] for c in cols) + "\n")
        print(t, "best", final[0]["score"], final[0]["setting"], flush=True)
    frozen = sorted(out.glob("*.tsv")) + sorted(exp.glob("*_ct.txt")) + sorted(src.iterdir())
    frozen += [out / "ca_screen", out / "casolve", QUAD, CARTER, K1K3, R42 / "PREREGISTRATION.md"]
    lines = [f"{sha(p)}  {Path(p).resolve().relative_to(REPO)}" for p in frozen]
    (exp / "FROZEN.sha256").write_text("\n".join(lines) + "\n")
    print("FROZEN", len(lines), "files ->", exp / "FROZEN.sha256")


if __name__ == "__main__":
    main()
