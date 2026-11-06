#!/usr/bin/env python3
"""R68 freeze verifier (no published letters, no truth): manifests, every work file, and EVERY saved decode (each row's
best per family and convention, 21 rows x 48 per ciphertext) re-encrypts through its path and model to the input.
Usage: verify.py INPUT.tsv RUN_DIR REPORT.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, sha, witness_ok  # noqa: E402

LOCAL = {"solver_source": ROOT / "r68/blind/keyed_solve.cpp", "routes": ROOT / "r61/routes.txt",
         "runner": ROOT / "r68/blind/run.py", "protocol": ROOT / "r68/PREREGISTRATION.md"}


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
    paths = ["ID"] + [l.split()[0] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (run / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    if set(rows) != set(cts):
        problems.append("ids differ")
    nwit = 0
    for rid, ans in rows.items():
        raw = [json.loads(l) for l in (run / "work" / f"{rid}.jsonl").read_text().splitlines() if l.strip()]
        if len(raw) != 21:
            problems.append(f"not 21 rows: {rid}")
        best = {}
        for r in raw:
            _, pi, model = r["id"].rsplit("__", 2)
            for b in [r["best"]] + r["by_family_convention"]:
                nwit += 1
                if not witness_ok(cts[rid], paths[int(pi)], model, b["family"], b["convention"], b["param"], b["key"],
                                  b["plaintext"]):
                    problems.append(f"witness failed: {rid} {r['id']} {b['family']} {b['convention']}")
            for b in r["by_family_convention"]:
                if b["family"] not in best or b["total"] > best[b["family"]][0]:
                    best[b["family"]] = (b["total"], paths[int(pi)], model, b["plaintext"])
        for f, (tot, path, model, pt) in best.items():
            a = ans["families"][f]
            if (a["path"], a["model"], a["plaintext"]) != (path, model, pt):
                problems.append(f"family answer is not the best raw row: {rid} {f}")
    out = {"ciphertexts": len(rows), "work_files": len(listed), "witnesses_checked": nwit, "problems": problems,
           "passed": not problems}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(f"R68 verify: {len(rows)} ciphertexts, {len(listed)} work files, {nwit} witnesses; "
          f"{'PASSED' if not problems else 'FAILED'}")
    for p in problems[:20]:
        print(" ", p)
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
