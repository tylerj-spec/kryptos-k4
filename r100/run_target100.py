#!/usr/bin/env python3
"""R100 target (PREREGISTRATION section 5). Runs once, only after the checker gate's GO and its freeze are committed
and pushed. Writes counts only: no plaintext, key, alphabet name or setting list.
Usage: python3 -I r100/run_target100.py --out-dir r100/k4"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):   # before numpy: the CPU cap is aggregate
    os.environ[_v] = "1"
import argparse  # noqa: E402
import ast  # noqa: E402
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
sys.path[:0] = [str(HERE), str(ROOT / "r76")]
import autokey100 as AK  # noqa: E402
import checker100 as CK  # noqa: E402
import alphabets as AL  # noqa: E402

PREREG_SHA = "4306a43dfec243b491ba6440be3e4426345c74b013917d16f2e9aca992104580"
CT_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"
TIER_SHA = "563ae44ae9a47539e0e01cabc1415e42619bdf3e906ff1f47b11f2d0bede2233"
SHUFFLE_SEED = 1000400
GATE = "r100/holdout/CHECKER_GATE.json"
GATE_LOG = "r100/holdout/VALIDATION_RESOURCE.json"
GATE_FREEZE = "r100/holdout/GATE_FROZEN.sha256"


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    return sha_bytes(Path(p).read_bytes())


def need(cond, msg):
    if not cond:
        raise SystemExit("REFUSED: " + msg)


def verify_manifest(rel):
    entries = {}
    for line in (ROOT / rel).read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        need(name not in entries, f"{rel}: duplicate {name}")
        need(sha_file(ROOT / name) == digest, f"{rel}: hash mismatch for {name}")
        entries[name] = digest
    return entries


def committed(rel):
    out = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
    need(out.returncode == 0 and out.stdout == (ROOT / rel).read_bytes(), f"{rel} is not committed as on disk")


def prerequisites():
    qa = json.loads((HERE / "QA_MANIFEST.json").read_text())
    need(qa.get("gate_verdict") == "GO" and qa.get("mode") == "crib_assisted", "QA manifest does not say GO")
    need(qa.get("preregistration_sha256") == PREREG_SHA == sha_file(HERE / "PREREGISTRATION.md"),
         "preregistration hash mismatch")
    b = qa["resource_budget"]
    need((b["max_wall_seconds"], b["max_cpu_seconds"], b["max_ram_mb"], b["max_retries"],
          b["max_decoded_candidates"], b["max_surviving_setting_outputs"]) == (1800, 1200, 1024, 0, 0, 0),
         "target budget differs from registration")
    protocol = verify_manifest("r100/PROTOCOL.sha256")
    source = verify_manifest("r100/SOURCE.sha256")
    gate = json.loads((ROOT / GATE).read_text())
    need(gate.get("gate_verdict") == "GO" and gate.get("status") == "COMPLETE", "gate is not a complete GO")
    need(all(gate["source_sha256"][f] == source[f"r100/{f}"] for f in gate["source_sha256"]),
         "gate covers different source")
    log = json.loads((ROOT / GATE_LOG).read_text())
    need(log["status"] == "COMPLETE" and log["wall_seconds"] <= 300 and log["cpu_seconds"] <= 240
         and log["max_rss_mb"] <= 1024, "gate did not complete inside its registered budget")
    frozen = verify_manifest(GATE_FREEZE)
    need({GATE, GATE_LOG, "r100/PROTOCOL.sha256", "r100/SOURCE.sha256"} <= set(frozen), "incomplete gate freeze")
    for rel in (GATE, GATE_LOG, GATE_FREEZE, "r100/SOURCE.sha256", "r100/PROTOCOL.sha256", "r100/QA_MANIFEST.json"):
        committed(rel)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"head_commit": head, "protocol_files": len(protocol), "source_files": len(source),
            "gate_sha256": sha_file(ROOT / GATE)}


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
    need(len(obs) == 24 and all(0 <= p < 97 and c in AK.AZ for p, c in obs.items()), "invalid observations")
    return obs


def target_inputs():
    raw = (ROOT / "r39/ic_gate/k4_ciphertext.txt").read_bytes()
    need(sha_bytes(raw) == CT_SHA, "ciphertext source hash mismatch")
    ct = raw.decode("ascii").strip()
    need(len(ct) == 97 and all(c in AK.AZ for c in ct), "invalid ciphertext")
    rng = random.Random(SHUFFLE_SEED)
    inputs, seen, draws = [("K4", ct)], {ct}, 0
    while len(inputs) < 101 and draws < 10000:
        letters = list(ct)
        rng.shuffle(letters)
        draws += 1
        s = "".join(letters)
        if s in seen:
            continue
        seen.add(s)
        inputs.append((f"SHUF_{len(inputs) - 1:03d}", s))
    need(len(inputs) == 101, "shuffle draw cap exhausted")
    need(all(Counter(s) == Counter(ct) for _, s in inputs), "shuffle frequency mismatch")
    return inputs, draws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.out_dir
    need(not (out / "INPUTS.tsv").exists() and not (out / "AGGREGATES.json").exists(),
         "outputs already exist; no overwrite or retry")
    t0w, t0c = time.time(), time.process_time()
    receipt = prerequisites()
    tier = [a for _, a in AL.large_tier()]
    need(sha_bytes("\n".join(tier).encode()) == TIER_SHA and len(tier) == 77229, "alphabet tier mismatch")
    IT = CK.tier_idxt(tier)
    inputs, draws = target_inputs()
    out.mkdir(parents=True, exist_ok=True)
    (out / "INPUTS.tsv").write_text("id\tciphertext\n" + "".join(f"{i}\t{s}\n" for i, s in inputs))
    obs = observations()
    link_counts = {L: len(CK.links(obs, L)) for L in range(1, 97)}
    lags = [L for L, k in link_counts.items() if k >= 10]
    drop_lags = [L for L, k in link_counts.items() if k >= 14]
    need(lags == [1, 2, 3, 4, 5, 6, 7, 39, 40, 41, 42, 43] and drop_lags == [1, 2, 3, 4, 5],
         "scanned lags differ from registration")
    rows = []
    for name, ct in inputs:
        res = CK.scan(ct, obs, IT, lags, drop_lags)
        per = {}
        for (L, s1, s2, F), (k, e, d) in res.items():
            r = per.setdefault(str(L), {"links": k, "exact": 0, "drop": 0 if d is not None else None})
            r["exact"] += e
            if d is not None:
                r["drop"] += d
        rows.append({"id": name, "lags": per})
    agg = {"round": "R100", "mode": "crib_assisted aggregate-only", "tier": len(tier), "signs": 4,
           "feedback_conventions": list(CK.FEEDBACK), "scanned_lags": lags, "drop_lags": drop_lags,
           "link_counts": {str(L): link_counts[L] for L in lags}, "settings_per_lag": 12 * len(tier) ** 2,
           "shuffle_seed": SHUFFLE_SEED, "shuffle_draws": draws, "inputs": rows, "receipt": receipt,
           "wall_s": round(time.time() - t0w, 2), "cpu_s": round(time.process_time() - t0c, 2)}
    (out / "AGGREGATES.json").write_text(json.dumps(agg, indent=1) + "\n")
    print("COMPLETE", len(rows))


if __name__ == "__main__":
    main()
