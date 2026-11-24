#!/usr/bin/env python3
"""R99 decision (PREREGISTRATION section 5), from the frozen aggregates only. Run after k4/FROZEN.sha256 is pushed.
Usage: python3 -I r99/evaluate99.py r99/k4/AGGREGATES.json OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXACT_DECIDED = 6     # links
DROP_DECIDED = 9


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    frozen = {}
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        frozen[name] = digest
    for name, digest in frozen.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    if "r99/k4/AGGREGATES.json" not in frozen:
        raise SystemExit("REFUSED: aggregates are not frozen")
    agg = json.loads(src.read_text())
    rows = agg["inputs"]
    assert rows[0]["id"] == "K4" and len(rows) == 201
    k4, shuf = rows[0]["lags"], [r["lags"] for r in rows[1:]]
    links = {L: v["links"] for L, v in k4.items()}
    dE = sorted((L for L, k in links.items() if k >= EXACT_DECIDED), key=int)
    dD = sorted((L for L, k in links.items() if k >= DROP_DECIDED), key=int)
    per_lag = {}
    for L in sorted(k4, key=int):
        e, d = k4[L]["exact"], k4[L]["drop"]
        per_lag[L] = {"links": links[L], "exact": e, "drop": d,
                      "exact_status": "EXCL" if e == 0 else "FEAS", "drop_status": "EXCL" if d == 0 else "FEAS",
                      "shuffles_exact_ge_k4": sum(s[L]["exact"] >= e for s in shuf),
                      "shuffles_drop_ge_k4": sum(s[L]["drop"] >= d for s in shuf),
                      "shuffle_exact_max": max(s[L]["exact"] for s in shuf),
                      "shuffle_drop_max": max(s[L]["drop"] for s in shuf)}
    tE = lambda r: sum(r[L]["exact"] for L in dE)  # noqa: E731
    tD = lambda r: sum(r[L]["drop"] for L in dD)  # noqa: E731
    kE, kD = tE(k4), tD(k4)
    if kE == 0 and kD == 0:
        decision = "EXCLUDED"
    elif (kE > 0 and all(tE(s) < kE for s in shuf)) or (kD > 0 and all(tD(s) < kD for s in shuf)):
        decision = "LEAD"
    else:
        decision = "CHANCE"
    res = {"decision": decision, "exact_decided_lags": [int(L) for L in dE], "drop_decided_lags": [int(L) for L in dD],
           "k4_exact_total_decided": kE, "k4_drop_total_decided": kD,
           "shuffles_exact_total_decided_max": max(tE(s) for s in shuf),
           "shuffles_drop_total_decided_max": max(tD(s) for s in shuf),
           "shuffles_with_exact_decided": sum(tE(s) > 0 for s in shuf),
           "shuffles_with_drop_decided": sum(tD(s) > 0 for s in shuf),
           "per_lag": per_lag, "aggregates_sha256": hashlib.sha256(src.read_bytes()).hexdigest()}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(decision, json.dumps({k: v for k, v in res.items() if k not in ("per_lag", "aggregates_sha256")}))


if __name__ == "__main__":
    main()
