#!/usr/bin/env python3
"""R66 freeze verifier (no published letters, no truth). For a frozen run directory: FROZEN.sha256 entries for the input,
results, solver source, routes, runner and protocol match; every WORK.sha256 entry matches; EVERY saved decode (each
route's best and top 8) is a valid homophonic witness through its route (cap 4); each answer is the best route row.
Usage: verify.py INPUT.tsv RUN_DIR REPORT.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, routes, sha, witness_ok  # noqa: E402

LOCAL = {"solver_source": ROOT / "r66/blind/hom_solve.cpp", "routes": ROOT / "r61/routes.txt",
         "runner": ROOT / "r66/blind/run.py", "protocol": ROOT / "r66/PREREGISTRATION.md"}


def main():
    tsv, run, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    problems = []
    for line in (run / "FROZEN.sha256").read_text().splitlines():
        h, lab, name = line.split("  ")
        p = tsv if lab == "input" else run / "RESULTS.jsonl" if lab == "results" else LOCAL.get(lab)
        if p is not None and sha(p) != h:
            problems.append(f"FROZEN mismatch: {lab} {name}")
    listed = {}
    for line in (run / "WORK.sha256").read_text().splitlines():
        h, name = line.split("  ")
        listed[name] = h
        if sha(run / "work" / name) != h:
            problems.append(f"WORK mismatch: {name}")
    if {p.name for p in (run / "work").iterdir()} != set(listed):
        problems.append("WORK listing differs from disk")
    R = routes()
    names = list(R)
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (run / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    if set(rows) != set(cts):
        problems.append("ids differ")
    nwit = 0
    for rid, ans in rows.items():
        raw = [json.loads(l) for l in (run / "work" / f"{rid}.jsonl").read_text().splitlines() if l.strip()]
        if len(raw) != 10:
            problems.append(f"not 10 routes: {rid}")
        best = None
        for r in raw:
            i = int(r["id"].rsplit("__", 1)[1])
            for w in [r["best"]] + r["top"]:
                nwit += 1
                if not witness_ok(cts[rid], R[names[i]], w["plaintext"], w["map"]):
                    problems.append(f"witness failed: {rid} {names[i]}")
            if best is None or (r["best"]["total"], -i) > (best[0], -best[1]):
                best = (r["best"]["total"], i, r["best"])
        if names[best[1]] != ans["route"] or best[2]["plaintext"] != ans["plaintext"]:
            problems.append(f"answer is not the best route row: {rid}")
    out = {"ciphertexts": len(rows), "work_files": len(listed), "witnesses_checked": nwit, "problems": problems,
           "passed": not problems}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(f"R66 verify: {len(rows)} ciphertexts, {len(listed)} work files, {nwit} witnesses; "
          f"{'PASSED' if not problems else 'FAILED'}")
    for p in problems[:20]:
        print(" ", p)
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
