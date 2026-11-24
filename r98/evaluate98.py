#!/usr/bin/env python3
"""R98 decision (PREREGISTRATION section 4), from the frozen aggregates only. Run after k4/FROZEN.sha256 is pushed.
Usage: python3 -I r98/evaluate98.py r98/k4/AGGREGATES.json OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    frozen = {}
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        frozen[name] = digest
    for name, digest in frozen.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    if "r98/k4/AGGREGATES.json" not in frozen:
        raise SystemExit("REFUSED: aggregates are not frozen")
    agg = json.loads(src.read_text())
    rows = agg["inputs"]
    k4 = rows[0]
    assert k4["id"] == "K4" and len(rows) == 201
    shuf = rows[1:]
    ke, kd = k4["exact_feasible_settings"], k4["drop_feasible_setting_pair_omissions"]
    # AMENDMENT_1 section 4: "K4's count" is EXACT when K4 has any EXACT setting, else DROP
    key, kv = ("exact_feasible_settings", ke) if ke > 0 else ("drop_feasible_setting_pair_omissions", kd)
    reach = sum(r[key] >= kv for r in shuf)
    if ke == 0 and kd == 0:
        decision = "EXCLUDED"
    elif reach == 0:
        decision = "LEAD"
    else:
        decision = "CHANCE"
    res = {"decision": decision,
           "k4": {"exact": ke, "drop": kd, "conventions_with_any": k4["conventions_with_any_feasible"]},
           "shuffles": {"n": len(shuf),
                        "with_exact": sum(r["exact_feasible_settings"] > 0 for r in shuf),
                        "with_drop": sum(r["drop_feasible_setting_pair_omissions"] > 0 for r in shuf),
                        "max_exact": max(r["exact_feasible_settings"] for r in shuf),
                        "max_drop": max(r["drop_feasible_setting_pair_omissions"] for r in shuf),
                        "total_exact": sum(r["exact_feasible_settings"] for r in shuf),
                        "total_drop": sum(r["drop_feasible_setting_pair_omissions"] for r in shuf),
                        "reaching_k4_count": reach, "count_compared": key},
           "aggregates_sha256": hashlib.sha256(src.read_bytes()).hexdigest()}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(decision, json.dumps(res["k4"]), json.dumps(res["shuffles"]))


if __name__ == "__main__":
    main()
