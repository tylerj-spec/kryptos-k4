#!/usr/bin/env python3
"""R70 freeze verifier (no published letters, no truth): manifests match, every work file is listed, and EVERY frozen
decode (top 200 per ciphertext) is a forward witness: its keytext is the source window at its offset and the plaintext
re-encrypts to the input ciphertext through its row and convention. RESULTS.jsonl must equal each file's rank 0.
Usage: verify.py INPUT.tsv RUN_DIR NORM_DIR REPORT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import sha, witness_ok  # noqa: E402

LOCAL = {"scanner_source": ROOT / "r70/blind/rk_text_scan.cpp", "routes": ROOT / "r61/routes.txt",
         "runner": ROOT / "r70/blind/run.py", "protocol": ROOT / "r70/PREREGISTRATION.md"}


def main():
    tsv, run, norm, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    problems = []
    for line in (run / "FROZEN.sha256").read_text().splitlines():
        h, lab, name = line.split("  ")
        p = tsv if lab == "input" else run / "RESULTS.jsonl" if lab == "results" else \
            norm / name if lab == "source" else LOCAL.get(lab)
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
    src = {p.stem: p.read_text().strip() for p in norm.glob("*.txt")}
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (run / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    if set(rows) != set(cts):
        problems.append("ids differ")
    nwit = 0
    for rid, ans in rows.items():
        top = [json.loads(l) for l in (run / "work" / f"{rid}.jsonl").read_text().splitlines() if l.strip()]
        if len(top) != 200 or [d["rank"] for d in top] != list(range(200)):
            problems.append(f"not 200 ranked decodes: {rid}")
        if any(top[i]["total"] < top[i + 1]["total"] for i in range(len(top) - 1)):
            problems.append(f"not sorted by total: {rid}")
        for d in top:
            nwit += 1
            if not witness_ok(cts[rid], src[d["source"]], d):
                problems.append(f"witness failed: {rid} rank {d['rank']}")
        if {k: top[0][k] for k in ans if k != "id"} != {k: v for k, v in ans.items() if k != "id"}:
            problems.append(f"RESULTS row is not rank 0: {rid}")
    out = {"ciphertexts": len(rows), "work_files": len(listed), "witnesses_checked": nwit, "problems": problems,
           "passed": not problems}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(f"R70 verify: {len(rows)} ciphertexts, {len(listed)} work files, {nwit} witnesses; "
          f"{'PASSED' if not problems else 'FAILED'}")
    for p in problems[:20]:
        print(" ", p)
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
