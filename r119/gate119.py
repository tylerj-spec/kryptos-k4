#!/usr/bin/env python3
"""R119 sealed synthetic gate, the pilot (PREREGISTRATION section 3). Synthetic only: reads no K4 file and no published
letter or position. Usage: python3 -I r119/gate119.py OUT.json"""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r117"), str(ROOT / "r112"), str(ROOT / "r98")]
import routes119 as RT  # noqa: E402
import gate117 as G7  # noqa: E402
import slidefair98 as SF  # noqa: E402
import x112 as X  # noqa: E402
import ref112 as RF  # noqa: E402

SEED = 1190901
AZ = SF.AZ
P_NAT = list(range(1, 13)) + [16, 24, 36, 47, None]
SOURCES = ("routes119.py", "gate119.py", "run_target119.py", "evaluate119.py", "crosscheck119.py")


def plant(rng, txt, k, route):
    PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
    conv = SF.CONVENTIONS[k % 16]
    pt = G7.window(rng, txt)
    pos = G7.mask(rng)
    p = P_NAT[k % len(P_NAT)] if k % 2 == 0 else None
    keys = G7.make_keys(rng, PA, CA, conv, pt, p, force_pos=pos if p is None else None)
    ct = RT.route(SF.encrypt(pt, PA, CA, conv, keys), route["perm"])
    hyp = [pt[i] if i in pos else None for i in range(97)]
    return ct, hyp, pt, pos, conv, p


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = G7.corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R119", "gate_type": "EXACT_CHECKER_CORRECTNESS", "seed": SEED}
    routes = RT.routes()
    f = 0
    for _ in range(100):
        s = "".join(rng.choice(AZ) for _ in range(97))
        f += sum(RT.unroute(RT.route(s, r["perm"]), r["perm"]) != s for r in routes)
    rep["G1_routes"] = {"routes": len(routes), "names": [r["name"] for r in routes], "roundtrip_failures": f,
                        "pass": f == 0 and len(routes) == 26}

    bad = bad_drop = 0
    k = 0
    for r in routes:
        for _ in range(10):
            ct, hyp, pt, pos, conv, p = plant(rng, txt, k, r)
            k += 1
            xs = RT.unroute(ct, r["perm"])
            bad += X.check(xs, hyp, conv, p) != "OPEN"
            j = rng.choice(sorted(pos))
            h2 = list(hyp)
            h2[j] = rng.choice([c for c in AZ if c != pt[j]])
            bad_drop += X.check(xs, h2, conv, p, allow_drop=True) != "OPEN"
    rep["G2_soundness"] = {"plants": k, "excluded_true": bad, "excluded_drop_with_one_error": bad_drop,
                           "pass": bad == 0 and bad_drop == 0}

    dis = cells = 0
    for r in routes:
        for _ in range(2):
            ct, hyp, pt, pos, _, _ = plant(rng, txt, k, r)
            k += 1
            xs = RT.unroute(ct, r["perm"])
            conv = rng.choice(SF.CONVENTIONS)
            p = rng.choice(P_NAT)
            cells += 1
            dis += X.check(xs, hyp, conv, p) != RF.check(xs, hyp, conv, p)
    rep["G3_two_implementations"] = {"cells": cells, "disagreements": dis, "pass": dis == 0}

    rep["status"] = "COMPLETE"
    rep["gate_verdict"] = "GO" if all(rep[g]["pass"] for g in ("G1_routes", "G2_soundness", "G3_two_implementations")) \
        else "NO-GO"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {s: hashlib.sha256((HERE / s).read_bytes()).hexdigest() for s in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["gate_verdict"], json.dumps({g: rep[g]["pass"] for g in ("G1_routes", "G2_soundness",
                                                                         "G3_two_implementations")}))


if __name__ == "__main__":
    main()
