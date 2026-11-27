#!/usr/bin/env python3
"""R109 target (PREREGISTRATION section 4). Runs once, only after the gate's GO and its freeze are committed and pushed.
Writes verdicts and counts only: no witness, no alphabet. Usage: python3 -I r109/run_target109.py --out-dir r109/k4"""
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
sys.path[:0] = [str(HERE)]
import check109 as K  # noqa: E402

CT_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"
SHUFFLE_SEED, N_SHUF = 1090400, 20
GATE, GATE_LOG, GATE_FREEZE = "r109/holdout/GATE.json", "r109/holdout/GATE_RESOURCE_LOG.json", "r109/holdout/GATE_FROZEN.sha256"
CELLS = [(L, s1, s2, F) for L in range(1, 97) for s1, s2 in K.SIGNS for F in K.FEEDBACK]


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
    verify_manifest("r109/PROTOCOL.sha256")
    source = verify_manifest("r109/SOURCE.sha256")
    gate = json.loads((ROOT / GATE).read_text())
    need(gate.get("gate_verdict") == "GO" and gate.get("status") == "COMPLETE", "gate is not a complete GO")
    need(all(gate["source_sha256"][f] == source[f"r109/{f}"] for f in gate["source_sha256"]), "gate covers other source")
    need(json.loads((ROOT / GATE_LOG).read_text())["status"] == "COMPLETE", "gate run was not COMPLETE")
    frozen = verify_manifest(GATE_FREEZE)
    need({GATE, GATE_LOG, "r109/PROTOCOL.sha256", "r109/SOURCE.sha256"} <= set(frozen), "incomplete gate freeze")
    for rel in (GATE, GATE_LOG, GATE_FREEZE, "r109/SOURCE.sha256", "r109/PROTOCOL.sha256", "r109/QA_MANIFEST.json"):
        committed(rel)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def observations():
    path = ROOT / "r73/sealed/reveal_k4.py"
    need(sha_file(path) == CLUE_SHA, "published observation source changed")
    found = [ast.literal_eval(n.value) for n in ast.parse(path.read_text()).body
             if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CLUES" for t in n.targets)]
    need(len(found) == 1, "expected one literal CLUES assignment")
    obs = {s + i: ch for s, text in found[0] for i, ch in enumerate(text)}
    need(len(obs) == 24, "invalid observations")
    return obs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    out = ap.parse_args().out_dir
    need(not (out / "VERDICTS.json").exists(), "outputs already exist; no overwrite or retry")
    t0w, t0c = time.time(), time.process_time()
    head = prerequisites()
    raw = (ROOT / "r39/ic_gate/k4_ciphertext.txt").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CT_SHA, "ciphertext source hash mismatch")
    ct = raw.decode("ascii").strip()
    need(len(ct) == 97 and all(c in K.AZ for c in ct), "invalid ciphertext")
    rng = random.Random(SHUFFLE_SEED)
    rows, seen = [("K4", ct)], {ct}
    while len(rows) < N_SHUF + 1:
        lst = list(ct)
        rng.shuffle(lst)
        s = "".join(lst)
        if s not in seen:
            seen.add(s)
            rows.append((f"SHUF_{len(rows) - 1:02d}", s))
    need(all(Counter(s) == Counter(ct) for _, s in rows), "shuffle frequency mismatch")
    out.mkdir(parents=True, exist_ok=True)
    (out / "INPUTS.tsv").write_text("id\tciphertext\n" + "".join(f"{i}\t{s}\n" for i, s in rows))
    obs = observations()
    hyp = [obs.get(i) for i in range(97)]
    cells = {}
    for L, s1, s2, F in CELLS:
        v, prim, _ = K.exact(ct, hyp, L, s1, s2, F)
        rec = {"exact": v, "primary": prim}
        if v == "INCONSISTENT":
            rec["dfs_crosscheck"] = K.dfs_crosscheck(ct, hyp, L, s1, s2, F)
            rec["drop"] = K.drop(ct, hyp, L, s1, s2, F)
        cells[f"L{L}_s{s1:+d}{s2:+d}_F{F}"] = rec
    prim_counts = []
    for name, s in rows:
        h = hyp
        c = Counter(K.primary_only(s, h, L, s1, s2, F) for L, s1, s2, F in CELLS) if name != "K4" else \
            Counter(r["primary"] for r in cells.values())
        prim_counts.append({"id": name, "primary_counts": dict(c)})
    res = {"round": "R109", "head_commit_at_start": head, "ciphertext_sha256": CT_SHA, "clue_source_sha256": CLUE_SHA,
           "shuffle_seed": SHUFFLE_SEED, "K4_cells": cells, "primary_only_counts": prim_counts,
           "wall_s": round(time.time() - t0w, 2), "cpu_s": round(time.process_time() - t0c, 2)}
    (out / "VERDICTS.json").write_text(json.dumps(res, indent=1) + "\n")
    tot = Counter(r["exact"] for r in cells.values())
    print("K4 exact", dict(tot), "drop", sum(r.get("drop", False) for r in cells.values()),
          "dfs disagreements", sum(r.get("dfs_crosscheck") == "CONSISTENT" for r in cells.values()))


if __name__ == "__main__":
    main()
