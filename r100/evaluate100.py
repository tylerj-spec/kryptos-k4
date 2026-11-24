#!/usr/bin/env python3
"""R100 decision (PREREGISTRATION section 5), from the frozen aggregates only. Run after k4/FROZEN.sha256 is pushed.
Usage: python3 -I r100/evaluate100.py r100/k4/AGGREGATES.json OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    agg = json.loads(src.read_text())
    rows = agg["inputs"]
    assert rows[0]["id"] == "K4" and len(rows) == 101
    k4, shuf = rows[0]["lags"], [r["lags"] for r in rows[1:]]
    dl = [str(L) for L in agg["drop_lags"]]
    tE = lambda r: sum(v["exact"] for v in r.values())  # noqa: E731
    tD = lambda r: sum(r[L]["drop"] for L in dl)  # noqa: E731
    kE, kD = tE(k4), tD(k4)
    if kE == 0 and kD == 0:
        decision = "EXCLUDED"
    elif (kE > 0 and all(tE(s) < kE for s in shuf)) or (kD > 0 and all(tD(s) < kD for s in shuf)):
        decision = "LEAD"
    else:
        decision = "CHANCE"
    per_lag = {L: {"links": v["links"], "exact": v["exact"], "drop": v["drop"],
                   "shuffles_exact_max": max(s[L]["exact"] for s in shuf),
                   "shuffles_with_exact": sum(s[L]["exact"] > 0 for s in shuf),
                   "shuffles_drop_max": max(s[L]["drop"] for s in shuf) if v["drop"] is not None else None}
               for L, v in sorted(k4.items(), key=lambda kv: int(kv[0]))}
    res = {"decision": decision, "k4_exact_total": kE, "k4_drop_total": kD,
           "shuffles_exact_total_max": max(tE(s) for s in shuf), "shuffles_drop_total_max": max(tD(s) for s in shuf),
           "shuffles_with_exact": sum(tE(s) > 0 for s in shuf), "shuffles_with_drop": sum(tD(s) > 0 for s in shuf),
           "per_lag": per_lag, "aggregates_sha256": hashlib.sha256(src.read_bytes()).hexdigest()}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(decision, json.dumps({k: v for k, v in res.items() if k not in ("per_lag", "aggregates_sha256")}))


if __name__ == "__main__":
    main()
