#!/usr/bin/env python3
"""K3-style double rotation + two-free-alphabet Gromark (ledger L94, L99, L100). Toolkit version of ChatGPT R27
r27_routes.py (feasibility) and Claude R28C r28c_run.py (English search).

  python3 route_gromark.py passes OUT.csv            # all 20 R27 routes x 2 orders x 100,000 primers (~2 min)
  python3 route_gromark.py calib [RESTARTS]          # planted messages under R24x8/CW/inv, true setting given
  python3 route_gromark.py search PASSES.csv OUT.json --routes R24x8/CW/inv [--orders S_then_T,T_then_S]
                                  [--min-cycles 0] [--restarts 16] [--limit N]

Known results: 65,968 passes (59,322 with 0 crib cycles, 6,607 with 1, 39 with 2; cycles depend only on route and
order). Calibration under R24x8/CW/inv: readable 9/20 at 16 restarts, 15/20 at 64 (W -69 to -79). English search of
the 39 two-cycle settings and all 3,212 R24x8/CW/inv settings: best -141.43, no candidate (R29)."""
import csv
import json
import random
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from k4common import ANCH, AZ, BIN, DATA, K4, R27_ROUTES, gromark_key, route, setup, solver_line  # noqa: E402
from key_oracle import checks, possible  # noqa: E402


def run_solver(lines, tag, restarts, workers=2):
    parts = [lines[i::workers] for i in range(workers)]
    procs = []
    for h, part in enumerate(parts):
        Path(f"{tag}_in{h}.txt").write_text("\n".join(part) + "\n")
        procs.append(subprocess.Popen([str(BIN / "solver_s2kp"), str(DATA / "word_model_orth.tsv"),
                                       str(DATA / "quad_log10.f32"), f"{tag}_in{h}.txt", f"{tag}_out{h}.jsonl",
                                       str(restarts), "40000", "0.05", "0"]))
    assert all(p.wait() == 0 for p in procs)
    best = {}
    for h in range(workers):
        for ln in open(f"{tag}_out{h}.jsonl"):
            r = json.loads(ln)
            if r["id"] not in best or r["W"] > best[r["id"]]["W"]:
                best[r["id"]] = r
    return best


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "passes":
        with open(sys.argv[2], "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["route", "order", "primer", "checks"])
            total = 0
            for name in R27_ROUTES:
                perm = route(name)
                for order in ("S_then_T", "T_then_S"):
                    ci, an, _ = setup(K4, perm, order)
                    cyc = checks(None, ct=ci, anch=an)
                    for pr in range(100000):
                        if possible(gromark_key(pr), ct=ci, anch=an):
                            w.writerow([name, order, f"{pr:05d}", cyc])
                            total += 1
        print("passes:", total, "(expected 65,968)")
    elif mode == "calib":
        restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 64
        bases = json.loads((DATA / "reference_messages.json").read_text())["calibration"]
        rng = random.Random(28028)
        perm = route("R24x8/CW/inv")
        lines, truth = [], {}
        for i, P in enumerate(bases):
            order = "T_then_S" if i % 2 == 0 else "S_then_T"
            pa, ca = list(AZ), list(AZ)
            rng.shuffle(pa)
            rng.shuffle(ca)
            k = gromark_key(rng.randrange(100000))
            if order == "S_then_T":
                X = "".join(ca[(pa.index(P[t]) + k[t]) % 26] for t in range(97))
                ct = "".join(X[perm[j]] for j in range(97))
            else:
                ct = "".join(ca[(pa.index(P[perm[j]]) + k[j]) % 26] for j in range(97))
            ci, an, ps = setup(ct, perm, order)
            assert possible(k, ct=ci, anch=an)
            lab = f"PLANT{i:02d}/{order}"
            truth[lab] = P
            lines.append(solver_line(lab, k, ci, an, rng.randrange(1, 2 ** 63), ps))
        best = run_solver(lines, f"calib{restarts}", restarts)
        err = {lab: sum(a != b for a, b in zip(best[lab]["plaintext"], truth[lab])) for lab in truth}
        print(f"calibration at {restarts} restarts: readable (<=5 wrong letters) {sum(e <= 5 for e in err.values())}/20")
    elif mode == "search":
        args = sys.argv[2:]
        src, out = args[0], args[1]
        opt = lambda k, d: args[args.index(k) + 1] if k in args else d  # noqa: E731
        routes = opt("--routes", "R24x8/CW/inv").split(",")
        orders = opt("--orders", "S_then_T,T_then_S").split(",")
        mincyc = int(opt("--min-cycles", "0"))
        restarts = int(opt("--restarts", "16"))
        limit = int(opt("--limit", "0"))
        sel = [r for r in csv.DictReader(open(src)) if r["route"] in routes and r["order"] in orders
               and int(r["checks"]) >= mincyc]
        sel = sel[:limit] if limit else sel
        lines = []
        for r in sel:
            ci, an, ps = setup(K4, route(r["route"]), r["order"])
            lab = f"{r['route']}|{r['order']}|{r['primer']}"
            lines.append(solver_line(lab, gromark_key(r["primer"]), ci, an, random.Random(lab).randrange(1, 2 ** 63), ps))
        print(f"searching {len(lines)} settings at {restarts} restarts", flush=True)
        best = run_solver(lines, "search", restarts)
        ranked = sorted(best.values(), key=lambda x: -x["W"])
        json.dump(ranked, open(out, "w"), indent=1)
        for x in ranked[:10]:
            print(f"   {x['W']:8.2f} {x['id']}  {x['plaintext']}")
        print("candidates need W > -114.9 AND the same text (<= 5 letters) on a 64-restart re-run with new seeds")
