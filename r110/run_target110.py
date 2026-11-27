#!/usr/bin/env python3
"""R110 target (PREREGISTRATION section 3). Runs once, only after the gate's GO and its freeze are committed and pushed.
BLIND: reads only the K4 ciphertext (hash-checked). Usage: python3 -I r110/run_target110.py --out-dir r110/k4"""
import argparse
import hashlib
import json
import random
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE)]
import lagpair110 as LP  # noqa: E402

CT_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
SHUFFLE_SEED, N_SHUF, LAGS = 1100400, 100000, range(1, 25)
GATE, GATE_LOG, GATE_FREEZE = "r110/holdout/GATE.json", "r110/holdout/GATE_RESOURCE_LOG.json", "r110/holdout/GATE_FROZEN.sha256"


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
    verify_manifest("r110/PROTOCOL.sha256")
    source = verify_manifest("r110/SOURCE.sha256")
    gate = json.loads((ROOT / GATE).read_text())
    need(gate.get("gate_verdict") == "GO" and gate.get("status") == "COMPLETE", "gate is not a complete GO")
    need(all(gate["source_sha256"][f] == source[f"r110/{f}"] for f in gate["source_sha256"]), "gate covers other source")
    need(json.loads((ROOT / GATE_LOG).read_text())["status"] == "COMPLETE", "gate run was not COMPLETE")
    frozen = verify_manifest(GATE_FREEZE)
    need({GATE, GATE_LOG, "r110/PROTOCOL.sha256", "r110/SOURCE.sha256"} <= set(frozen), "incomplete gate freeze")
    for rel in (GATE, GATE_LOG, GATE_FREEZE, "r110/SOURCE.sha256", "r110/PROTOCOL.sha256", "r110/QA_MANIFEST.json"):
        committed(rel)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    out = ap.parse_args().out_dir
    need(not (out / "STATISTICS.json").exists(), "outputs already exist; no overwrite or retry")
    t0w, t0c = time.time(), time.process_time()
    head = prerequisites()
    raw = (ROOT / "r39/ic_gate/k4_ciphertext.txt").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CT_SHA, "ciphertext source hash mismatch")
    ct = raw.decode("ascii").strip()
    need(len(ct) == 97 and all("A" <= c <= "Z" for c in ct), "invalid ciphertext")
    obs = {L: LP.R_counter(ct, L) for L in LAGS}
    need(all(obs[L] == LP.R_sorted(ct, L) for L in LAGS), "the two implementations disagree on K4")
    rng = random.Random(SHUFFLE_SEED)
    ge = dict.fromkeys(LAGS, 0)
    hist = {L: {} for L in LAGS}
    lst = list(ct)
    for _ in range(N_SHUF):
        rng.shuffle(lst)
        for L in LAGS:
            r = LP.R_counter(lst, L)
            ge[L] += r >= obs[L]
            hist[L][r] = hist[L].get(r, 0) + 1
    p = {L: (1 + ge[L]) / (N_SHUF + 1) for L in LAGS}
    res = {"round": "R110", "head_commit_at_start": head, "ciphertext_sha256": CT_SHA, "shuffle_seed": SHUFFLE_SEED,
           "shuffles": N_SHUF, "R_K4": {str(L): obs[L] for L in LAGS}, "p_one_sided": {str(L): p[L] for L in LAGS},
           "shuffle_mean": {str(L): round(sum(k * v for k, v in hist[L].items()) / N_SHUF, 4) for L in LAGS},
           "shuffle_histogram": {str(L): {str(k): v for k, v in sorted(hist[L].items())} for L in LAGS},
           "wall_s": round(time.time() - t0w, 2), "cpu_s": round(time.process_time() - t0c, 2)}
    out.mkdir(parents=True, exist_ok=True)
    (out / "STATISTICS.json").write_text(json.dumps(res, indent=1) + "\n")
    print("R_1(K4)", obs[1], "p_1", round(p[1], 5), "min p", round(min(p.values()), 5))


if __name__ == "__main__":
    main()
