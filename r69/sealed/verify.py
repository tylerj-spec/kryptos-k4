#!/usr/bin/env python3
"""R69 freeze verifier (no published letters, no truth): manifests match, every work file is listed, and EVERY raw
stage-1 decomposition (each reading's best and per-convention bests) re-encrypts to the input ciphertext through its
reading: CT[j] = X[perm[j]], X[i] = S(P[i], K[i]). Also checks that RESULTS.jsonl reports each reading's raw best.
Usage: verify.py INPUT.tsv RUN_DIR REPORT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r64/sealed"))
from common import forward, sha  # noqa: E402

LOCAL = {"solver_source": ROOT / "r63/blind/rk2_solve.cpp", "patterns": ROOT / "r69/data/patterns.txt",
         "runner": ROOT / "r69/blind/run.py", "r64_runner": ROOT / "r64/blind/run.py",
         "protocol": ROOT / "r69/PREREGISTRATION.md"}


def main():
    tsv, run, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    problems = []
    for line in (run / "FROZEN.sha256").read_text().splitlines():
        h, lab, name = line.split("  ")
        p = tsv if lab == "input" else run / "RESULTS.jsonl" if lab == "results" else LOCAL.get(lab)
        if p is not None and sha(p) != h:
            problems.append(f"FROZEN mismatch: {lab}")
    listed = {}
    for line in (run / "WORK.sha256").read_text().splitlines():
        h, name = line.split("  ")
        listed[name] = h
        if sha(run / "work" / name) != h:
            problems.append(f"WORK mismatch: {name}")
    if {p.name for p in (run / "work").iterdir()} != set(listed):
        problems.append("WORK listing differs from disk")
    pats = {}
    for line in LOCAL["patterns"].read_text().splitlines():
        n, _, p = line.split()
        pats[n] = [int(x) for x in p.split(",")]
    inp = {l.split("\t")[0]: l.split("\t") for l in tsv.read_text().splitlines()[1:] if l}
    rows = {json.loads(l)["id"]: json.loads(l) for l in (run / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    if set(rows) != set(inp):
        problems.append("ids differ")
    nwit = 0
    for rid, ans in rows.items():
        _, ct, sset = inp[rid]
        want = [n for n in pats if sset == "A" or n.startswith("F_")]
        uniq, alias = [], {}
        for n in want:
            k = tuple(pats[n])
            if k not in alias:
                alias[k] = len(uniq)
                uniq.append(pats[n])
        s1in = [l.split("\t") for l in (run / "work" / f"{rid}.s1.tsv").read_text().splitlines() if l]
        raw = {int(json.loads(l)["id"].rsplit("__", 1)[1]): json.loads(l)
               for l in (run / "work" / f"{rid}.s1.jsonl").read_text().splitlines() if l.strip()}
        if sorted(raw) != list(range(len(uniq))) or len(s1in) != len(uniq):
            problems.append(f"raw rows incomplete: {rid}")
            continue
        for i, perm in enumerate(uniq):
            for b in [raw[i]["best"]] + raw[i]["per_convention"]:
                nwit += 1
                if forward(b["plaintext"], b["key"], b["convention"], perm) != ct:
                    problems.append(f"witness failed: {rid} {i} {b['convention']}")
        if set(ans["readings"]) != set(want):
            problems.append(f"reading set differs: {rid}")
        for n in want:
            b = raw[alias[tuple(pats[n])]]["best"]
            a = ans["readings"].get(n, {})
            if (a.get("total"), a.get("convention")) != (b["total"], b["convention"]):
                problems.append(f"result is not the raw best: {rid} {n}")
    out = {"ciphertexts": len(rows), "work_files": len(listed), "witnesses_checked": nwit, "problems": problems,
           "passed": not problems}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(f"R69 verify: {len(rows)} ciphertexts, {len(listed)} work files, {nwit} witnesses; "
          f"{'PASSED' if not problems else 'FAILED'}")
    for p in problems[:20]:
        print(" ", p)
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
