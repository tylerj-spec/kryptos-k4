#!/usr/bin/env python3
"""R99 post-freeze cross-check: recompute K4's per-lag counts from the FROZEN inputs with the second checker path
(checker99.scan_lag_simple: brute force over c with step-by-step propagation, no masks or closed-form sums) and
compare with the frozen aggregates. Counts only. Usage: python3 -I r99/crosscheck99.py OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r76")]
import alphabets as AL  # noqa: E402
import checker99 as CK  # noqa: E402
import run_target99 as RT  # noqa: E402


def main():
    out = Path(sys.argv[1])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    tier = [a for _, a in AL.large_tier()]
    assert hashlib.sha256("\n".join(tier).encode()).hexdigest() == RT.TIER_SHA
    IDX = CK.tier_idx(tier)
    obs = RT.observations()
    name, ct = (HERE / "k4/INPUTS.tsv").read_text().splitlines()[1].split("\t")
    assert name == "K4"
    res = CK.scan(ct, obs, IDX, fast=False)
    lags = {}
    for (L, s1, s2), (k, e, d) in res.items():
        r = lags.setdefault(str(L), {"links": k, "exact": 0, "drop": 0})
        r["exact"] += e
        r["drop"] += d
    frozen = json.loads((HERE / "k4/AGGREGATES.json").read_text())["inputs"][0]
    agree = frozen["id"] == "K4" and frozen["lags"] == lags
    out.write_text(json.dumps({"implementation": "checker99.scan_lag_simple (second path)", "input": "K4",
                               "agree_with_frozen": agree, "lags": lags}, indent=1) + "\n")
    print("AGREE" if agree else "DISAGREE")


if __name__ == "__main__":
    main()
