#!/usr/bin/env python3
"""R111 target (PREREGISTRATION section 4). Runs once, only after the gate's GO and its freeze are committed and pushed.
BLIND: reads only the K4 ciphertext (hash-checked); no published plaintext letter or position.
Usage: python3 -I r111/run_target111.py --out-dir r111/k4"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE)]
import cells111 as C  # noqa: E402

CT_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
SHUFFLE_SEED, SOLVER_SEED, N_NULL = 1110400, 1110402, 15
GATE, GATE_LOG, GATE_FREEZE = "r111/holdout/GATE.json", "r111/holdout/GATE_RESOURCE_LOG.json", "r111/holdout/GATE_FROZEN.sha256"


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
    need(qa.get("gate_verdict") == "GO" and qa.get("mode") == "blind", "QA manifest does not say GO / blind")
    need(qa.get("preregistration_sha256") == sha_file(HERE / "PREREGISTRATION.md"), "preregistration hash mismatch")
    verify_manifest("r111/PROTOCOL.sha256")
    source = verify_manifest("r111/SOURCE.sha256")
    gate = json.loads((ROOT / GATE).read_text())
    need(gate.get("gate_verdict") == "GO" and gate.get("status") == "COMPLETE", "gate is not a complete GO")
    need(all(gate["source_sha256"][f] == source[f"r111/{f}"] for f in gate["source_sha256"]), "gate covers other source")
    log = json.loads((ROOT / GATE_LOG).read_text())
    need(log["status"] == "COMPLETE", "gate run was not COMPLETE")
    frozen = verify_manifest(GATE_FREEZE)
    need({GATE, GATE_LOG, "r111/PROTOCOL.sha256", "r111/SOURCE.sha256"} <= set(frozen), "incomplete gate freeze")
    for rel in (GATE, GATE_LOG, GATE_FREEZE, "r111/SOURCE.sha256", "r111/PROTOCOL.sha256", "r111/QA_MANIFEST.json"):
        committed(rel)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    out = ap.parse_args().out_dir
    need(not (out / "CANDIDATES.json").exists(), "outputs already exist; no overwrite or retry")
    t0w, t0c = time.time(), time.process_time()
    head = prerequisites()
    raw = (ROOT / "r39/ic_gate/k4_ciphertext.txt").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CT_SHA, "ciphertext source hash mismatch")
    ct = raw.decode("ascii").strip()
    need(len(ct) == 97 and all(ch in C.AZ for ch in ct), "invalid ciphertext")
    rng = random.Random(SHUFFLE_SEED)
    inputs, seen = [("K4", ct)], {ct}
    while len(inputs) < N_NULL + 1:
        lst = list(ct)
        rng.shuffle(lst)
        s = "".join(lst)
        if s not in seen:
            seen.add(s)
            inputs.append((f"SHUF_{len(inputs) - 1:02d}", s))
    need(all(Counter(s) == Counter(ct) for _, s in inputs), "shuffle frequency mismatch")
    out.mkdir(parents=True, exist_ok=True)
    (out / "INPUTS.tsv").write_text("id\tciphertext\n" + "".join(f"{i}\t{s}\n" for i, s in inputs))
    srng = random.Random(SOLVER_SEED)
    cand, nulls = None, []
    for name, s in inputs:
        T, rows = C.search(s, srng, keep_text=(name == "K4"))
        if name == "K4":
            cand = {"T": T, "cells": rows}
        else:
            nulls.append({"id": name, "T": T, "cell_scores": [r["score"] for r in rows],
                          "reencrypt_all": all(r["reencrypts"] for r in rows)})
    meta = {"round": "R111", "head_commit_at_start": head, "ciphertext_sha256": CT_SHA, "shuffle_seed": SHUFFLE_SEED,
            "solver_seed": SOLVER_SEED, "cells": [list(x) for x in C.CELLS],
            "wall_s": round(time.time() - t0w, 2), "cpu_s": round(time.process_time() - t0c, 2)}
    (out / "CANDIDATES.json").write_text(json.dumps({**meta, "K4": cand}, indent=1) + "\n")
    (out / "NULLS.json").write_text(json.dumps({**meta, "nulls": nulls}, indent=1) + "\n")
    print("K4 T", cand["T"], "null max", max(n["T"] for n in nulls))


if __name__ == "__main__":
    main()
