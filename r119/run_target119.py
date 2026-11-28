#!/usr/bin/env python3
"""R119 target (PREREGISTRATION section 4). Runs once, only after the gate's GO and its freeze are committed and pushed.
For each of the 26 routes, un-routes K4 and writes the 768 per-cell X112 verdicts and their counts: no plaintext, no key,
no alphabet. No shuffles (the null is R117's frozen 200). 3 worker processes, results kept in route order.
Usage: python3 -I r119/run_target119.py --out-dir r119/k4"""
import argparse
import ast
import hashlib
import json
import random
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r117"), str(ROOT / "r112"), str(ROOT / "r98")]
import slidefair98 as SF  # noqa: E402
import routes119 as RT  # noqa: E402
import run_target117 as T7  # noqa: E402

CT_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"
WORKERS = 3
P_ALL = list(range(1, 48)) + [None]
GATE, GATE_LOG, GATE_FREEZE = "r119/holdout/GATE.json", "r119/holdout/GATE_RESOURCE_LOG.json", "r119/holdout/GATE_FROZEN.sha256"
VERDICTS = ("EXCL_DROP", "EXCL", "OPEN")


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def need(cond, msg):
    if not cond:
        raise SystemExit("REFUSED: " + msg)


def verify_manifest(rel):
    entries = {}
    for line in (ROOT / rel).read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        need(sha_file(ROOT / name) == digest, f"{rel}: hash mismatch for {name}")
        entries[name] = digest
    return entries


def committed(rel):
    out = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
    need(out.returncode == 0 and out.stdout == (ROOT / rel).read_bytes(), f"{rel} is not committed as on disk")


def prerequisites():
    qa = json.loads((HERE / "QA_MANIFEST.json").read_text())
    need(qa.get("gate_verdict") == "GO" and qa.get("mode") == "crib_assisted", "QA manifest does not say GO")
    need(qa.get("preregistration_sha256") == sha_file(HERE / "PREREGISTRATION.md"), "preregistration hash mismatch")
    verify_manifest("r119/PROTOCOL.sha256")
    source = verify_manifest("r119/SOURCE.sha256")
    gate = json.loads((ROOT / GATE).read_text())
    need(gate.get("gate_verdict") == "GO" and gate.get("status") == "COMPLETE", "gate is not a complete GO")
    need(all(gate["source_sha256"][f] == source[f"r119/{f}"] for f in gate["source_sha256"]), "gate covers other source")
    need(json.loads((ROOT / GATE_LOG).read_text())["status"] == "COMPLETE", "gate run was not COMPLETE")
    frozen = verify_manifest(GATE_FREEZE)
    need({GATE, GATE_LOG, "r119/PROTOCOL.sha256", "r119/SOURCE.sha256"} <= set(frozen), "incomplete gate freeze")
    for rel in (GATE, GATE_LOG, GATE_FREEZE, "r119/SOURCE.sha256", "r119/PROTOCOL.sha256", "r119/QA_MANIFEST.json"):
        committed(rel)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def observations():
    path = ROOT / "r73/sealed/reveal_k4.py"
    need(sha_file(path) == CLUE_SHA, "published observation source changed")
    found = [ast.literal_eval(n.value) for n in ast.parse(path.read_text()).body
             if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CLUES" for t in n.targets)]
    need(len(found) == 1, "expected one literal CLUES assignment")
    obs = {}
    for start, text in found[0]:
        for off, ch in enumerate(text):
            need(start + off not in obs, "overlapping observations")
            obs[start + off] = ch
    need(len(obs) == 24, "invalid observations")
    return obs


def k4_ciphertext():
    raw = (ROOT / "r39/ic_gate/k4_ciphertext.txt").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CT_SHA, "ciphertext source hash mismatch")
    ct = raw.decode("ascii").strip()
    need(len(ct) == 97 and all(c in SF.AZ for c in ct), "invalid ciphertext")
    return ct


def main():
    import multiprocessing as mp
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    out = ap.parse_args().out_dir
    need(not (out / "AGGREGATES.json").exists(), "outputs already exist; no overwrite or retry")
    t0w, t0c = time.time(), time.process_time()
    head = prerequisites()
    ct = k4_ciphertext()
    routes = RT.routes()
    obs = observations()
    hyp = [obs.get(i) for i in range(97)]
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(RT.unroute(ct, r["perm"]), hyp, True) for r in routes]
    rows = []
    with mp.get_context("fork").Pool(WORKERS) as pool:
        for r, (counts, cells) in zip(routes, pool.imap(T7.scan_input, jobs)):
            tot = {v: sum(c[v] for c in counts.values()) for v in T7.VERDICTS}
            rows.append({"route": r["name"], "status": r["status"], "totals": tot, "by_key_structure": counts,
                         "cells": cells})
            print(r["name"], json.dumps(tot), flush=True)
    res = {"round": "R119", "head_commit_at_start": head, "ciphertext_sha256": CT_SHA, "clue_source_sha256": CLUE_SHA,
           "workers": WORKERS, "routes": rows, "wall_s": round(time.time() - t0w, 2),
           "cpu_s_parent": round(time.process_time() - t0c, 2)}
    (out / "AGGREGATES.json").write_text(json.dumps(res, indent=1) + "\n")
    print("routes", len(rows), "OPEN max", max(x["totals"]["OPEN"] for x in rows))


if __name__ == "__main__":
    main()
