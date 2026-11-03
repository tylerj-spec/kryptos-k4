#!/usr/bin/env python3
"""R64 freeze verifier (no published letters, no truth). For a frozen run directory:
  1. every FROZEN.sha256 entry that lives in the repository or the run directory matches (input, results, solver
     source, routes, runner, protocol), and every WORK.sha256 entry matches the raw work file;
  2. EVERY saved witness in every raw solver output (stage 1: 10 routes x {best, per_convention, top}; stage 2 likewise)
     re-encrypts, through its own route, to the input ciphertext: CT[j] = X[perm[j]], X = S(P, K);
  3. each RESULTS.jsonl answer equals the best stage-2 row of its job, and the stage-1 ranking in the result file
     matches the raw stage-1 output.
Usage: verify.py INPUT.tsv RUN_DIR REPORT.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, forward, routes, sha  # noqa: E402

LOCAL = {"input": None, "results": "RESULTS.jsonl", "solver_source": ROOT / "r63/blind/rk2_solve.cpp",
         "routes": ROOT / "r61/routes.txt", "runner": ROOT / "r64/blind/run.py", "protocol": ROOT / "r64/PREREGISTRATION.md"}


def main():
    tsv, run, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    problems = []
    for line in (run / "FROZEN.sha256").read_text().splitlines():
        h, lab, name = line.split("  ")
        if lab in LOCAL:
            p = tsv if lab == "input" else run / LOCAL[lab] if lab == "results" else LOCAL[lab]
            if sha(p) != h:
                problems.append(f"FROZEN mismatch: {lab} {name}")
    work = run / "work"
    listed = {}
    for line in (run / "WORK.sha256").read_text().splitlines():
        h, name = line.split("  ")
        listed[name] = h
        if sha(work / name) != h:
            problems.append(f"WORK mismatch: {name}")
    on_disk = {p.name for p in work.iterdir()}
    if on_disk != set(listed):
        problems.append(f"WORK listing differs from disk: {sorted(on_disk ^ set(listed))[:5]}")
    R = routes()
    names = list(R)
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (run / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    if set(rows) != set(cts):
        problems.append("RESULTS ids differ from input ids")
    nwit = 0
    for rid, row in rows.items():
        for m, ans in row["models"].items():
            base = work / f"{rid.replace('/', '_')}.{m}"
            raw = {}
            for stage in ("s1", "s2"):
                lines = [json.loads(l) for l in Path(f"{base}.{stage}.jsonl").read_text().splitlines() if l.strip()]
                raw[stage] = lines
                for r in lines:
                    rname = names[int(r["id"].rsplit("__", 1)[1])]
                    for w in [r["best"]] + r["per_convention"] + r["top"]:
                        nwit += 1
                        if forward(w["plaintext"], w["key"], w["convention"], R[rname]) != cts[rid]:
                            problems.append(f"witness failed: {rid} {m} {stage} {rname} {w['convention']}")
            if len(raw["s1"]) != 10:
                problems.append(f"stage 1 not 10 routes: {rid} {m}")
            s1 = sorted(((-r["best"]["total"], int(r["id"].rsplit("__", 1)[1])) for r in raw["s1"]))
            if [names[i] for _, i in s1] != [d["route"] for d in ans["stage1"]]:
                problems.append(f"stage-1 ranking differs: {rid} {m}")
            s2 = sorted(raw["s2"], key=lambda r: (-r["best"]["total"], int(r["id"].rsplit("__", 1)[1])))
            top = s2[0]
            if (names[int(top["id"].rsplit("__", 1)[1])] != ans["route"] or top["best"]["plaintext"] != ans["plaintext"]
                    or top["best"]["key"] != ans["key"] or top["best"]["convention"] != ans["convention"]):
                problems.append(f"answer is not the best stage-2 row: {rid} {m}")
            if forward(ans["plaintext"], ans["key"], ans["convention"], R[ans["route"]]) != cts[rid]:
                problems.append(f"answer witness failed: {rid} {m}")
    out = {"ciphertexts": len(rows), "work_files": len(listed), "witnesses_checked": nwit,
           "problems": problems, "passed": not problems}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(f"R64 verify: {len(rows)} ciphertexts, {len(listed)} work files, {nwit} witnesses; "
          f"{'PASSED' if not problems else 'FAILED'}")
    for p in problems[:20]:
        print(" ", p)
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
