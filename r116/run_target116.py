#!/usr/bin/env python3
"""R116 target (PREREGISTRATION section 4). Runs once, only after the gate's GO and its freeze are committed and pushed.
Writes verdict counts per input and order, and for K4 the per-vector verdicts at L 1-2 and the structured L 3-4
verdicts: no plaintext, no key, no alphabet.
Usage: python3 -I r116/run_target116.py --out-dir r116/k4"""
import argparse
import ast
import hashlib
import itertools
import json
import random
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r115")]
import x115 as X  # noqa: E402

CT_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"
SHUFFLE_SEED, N_SHUF, N_SHUF_L4 = 1160400, 200, 20
STRUCTURED_HIGH = [(0, 0, 1), (3, 23, 1), (1, 1, 1), (0, 0, 0, 1), (4, 20, 4, 25), (1, 1, 1, 1)]
GATE, GATE_LOG, GATE_FREEZE = "r116/holdout/GATE.json", "r116/holdout/GATE_RESOURCE_LOG.json", "r116/holdout/GATE_FROZEN.sha256"
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
    verify_manifest("r116/PROTOCOL.sha256")
    source = verify_manifest("r116/SOURCE.sha256")
    gate = json.loads((ROOT / GATE).read_text())
    need(gate.get("gate_verdict") == "GO" and gate.get("status") == "COMPLETE", "gate is not a complete GO")
    need(all(gate["source_sha256"][f] == source[f"r116/{f}"] for f in gate["source_sha256"]), "gate covers other source")
    need(json.loads((ROOT / GATE_LOG).read_text())["status"] == "COMPLETE", "gate run was not COMPLETE")
    frozen = verify_manifest(GATE_FREEZE)
    need({GATE, GATE_LOG, "r116/PROTOCOL.sha256", "r116/SOURCE.sha256"} <= set(frozen), "incomplete gate freeze")
    for rel in (GATE, GATE_LOG, GATE_FREEZE, "r116/SOURCE.sha256", "r116/PROTOCOL.sha256", "r116/QA_MANIFEST.json"):
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


def inputs():
    raw = (ROOT / "r39/ic_gate/k4_ciphertext.txt").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CT_SHA, "ciphertext source hash mismatch")
    ct = raw.decode("ascii").strip()
    need(len(ct) == 97 and all(c in X.AZ for c in ct), "invalid ciphertext")
    rng = random.Random(SHUFFLE_SEED)
    rows, seen = [("K4", ct)], {ct}
    while len(rows) < N_SHUF + 1:
        lst = list(ct)
        rng.shuffle(lst)
        s = "".join(lst)
        if s not in seen:
            seen.add(s)
            rows.append((f"SHUF_{len(rows) - 1:03d}", s))
    need(all(Counter(s) == Counter(ct) for _, s in rows), "shuffle frequency mismatch")
    return rows


def scan_input(ct, obs, orders, keep):
    """Verdict counts per order; with keep, also the per-vector verdicts at L 1-2 and the structured L 3-4 verdicts."""
    C = X.Checker(ct, obs)
    counts, cells, struct = {}, {}, {}
    for L in orders:
        c = dict.fromkeys(VERDICTS, 0)
        for a in itertools.product(range(26), repeat=L):
            v = C.verdict(a, allow_drop=True)
            c[v] += 1
            if keep and L <= 2:
                cells[",".join(map(str, a))] = v
            if keep and a in STRUCTURED_HIGH:
                struct[",".join(map(str, a))] = v
        counts[str(L)] = c
        C.memo.clear()
    return counts, cells, struct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    out = ap.parse_args().out_dir
    need(not (out / "AGGREGATES.json").exists(), "outputs already exist; no overwrite or retry")
    t0w, t0c = time.time(), time.process_time()
    head = prerequisites()
    rows = inputs()
    out.mkdir(parents=True, exist_ok=True)
    (out / "INPUTS.tsv").write_text("id\tciphertext\n" + "".join(f"{i}\t{s}\n" for i, s in rows))
    obs = observations()
    aggs, k4cells, k4struct = [], {}, {}
    for idx, (name, ct) in enumerate(rows):
        orders = (1, 2, 3, 4) if idx <= N_SHUF_L4 else (1, 2, 3)
        counts, cells, struct = scan_input(ct, obs, orders, keep=name == "K4")
        if name == "K4":
            k4cells, k4struct = cells, struct
        aggs.append({"id": name, "by_order": counts})
        print(name, json.dumps(counts), flush=True)
    res = {"round": "R116", "head_commit_at_start": head, "ciphertext_sha256": CT_SHA, "clue_source_sha256": CLUE_SHA,
           "shuffle_seed": SHUFFLE_SEED, "shuffles": N_SHUF, "shuffles_at_L4": N_SHUF_L4, "inputs": aggs,
           "K4_cells_L1_L2": k4cells, "K4_structured_L3_L4": k4struct,
           "wall_s": round(time.time() - t0w, 2), "cpu_s": round(time.process_time() - t0c, 2)}
    (out / "AGGREGATES.json").write_text(json.dumps(res, indent=1) + "\n")
    print("K4", json.dumps(aggs[0]["by_order"]))


if __name__ == "__main__":
    main()
