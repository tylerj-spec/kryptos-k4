#!/usr/bin/env python3
"""R30 calibrations (PREREGISTRATION_R30.md).
  python3 calib.py c1     chain addition b=6/b=7, true key given, 16 and 64 restarts (ORTH)
  python3 calib.py c3     one-cycle R27 routes + 5-digit Gromark, true setting given, 16 and 64 restarts (ORTH)
  python3 calib.py c2     blind punctuation test: 22 fresh fixtures, true + <=19 wrong feasible primers, both models
Results go to runs/<name>.json."""
import json
import random
import sys

from r30lib import (AZ, ANCH, DATA, HERE, RUNS, assert_protocol, chain_key, encrypt, ensure_models, possible, route,
                    run_solver, seed, setup, solver_line, verify_row)

ONE_CYCLE = ["R23x8/CCW/fwd", "R24x7/CCW/inv", "R24x7/CW/fwd", "R24x7/CW/inv", "R24x9/CCW/inv", "R24x9/CW/inv"]
BASES = json.loads((DATA / "reference_messages.json").read_text())["calibration"]


def errs(a, b):
    return sum(x != y for x, y in zip(a, b))


def planted_recovery(name, items):
    """items: list of (label, truth, key, ct_sub, anch_sub, perm_token, perm, order, ct)."""
    out = {}
    for R in (16, 64):
        lines = [solver_line(lab, k, ci, an, seed(f"{name}|{lab}|{R}"), ps) for lab, P, k, ci, an, ps, *_ in items]
        best, _ = run_solver(lines, f"{name}_{R}", R)
        rows = {}
        for lab, P, k, ci, an, ps, perm, order, ct in items:
            r = best[lab]
            assert verify_row(r, k, ct, perm, order), lab
            rows[lab] = {"W": r["W"], "wrong_letters": errs(r["plaintext"], P), "plaintext": r["plaintext"]}
        n = sum(v["wrong_letters"] <= 5 for v in rows.values())
        out[R] = {"readable": n, "of": len(items), "rows": rows}
        print(f"{name}: {R} restarts readable {n}/{len(items)}; truth W range "
              f"{min(v['W'] for v in rows.values()):.1f} .. {max(v['W'] for v in rows.values()):.1f}", flush=True)
    return out


def c1():
    rng = random.Random(30001)
    items = []
    for i, P in enumerate(BASES):
        b = 6 if i < 10 else 7
        pa, ca = list(AZ), list(AZ)
        rng.shuffle(pa)
        rng.shuffle(ca)
        k = chain_key(rng.randrange(10 ** b), b)
        ct = encrypt(P, k, pa, ca)
        assert possible(k, ct=ct)
        items.append((f"C1_{i:02d}_b{b}", P, k, ct, dict(ANCH), "-", None, "T_then_S", ct))
    return planted_recovery("c1", items)


def c3():
    rng = random.Random(30003)
    items = []
    for i, P in enumerate(BASES):
        name = ONE_CYCLE[i % len(ONE_CYCLE)]
        order = "T_then_S" if i % 2 == 0 else "S_then_T"
        perm = route(name)
        pa, ca = list(AZ), list(AZ)
        rng.shuffle(pa)
        rng.shuffle(ca)
        k = chain_key(rng.randrange(10 ** 5), 5)
        ct = encrypt(P, k, pa, ca, perm, order)
        ci, an, ps = setup(ct, perm, order)
        assert possible(k, ct=ci, anch=an)
        items.append((f"C3_{i:02d}_{name}_{order}", P, k, ci, an, ps, perm, order, ct))
    return planted_recovery("c3", items)


def c2():
    fixtures = json.loads((HERE / "fixtures_punct.json").read_text())["messages"]
    rng = random.Random(30002)
    lines, meta = [], {}
    sets = [("F", fixtures), ("U", BASES)]
    for tag, msgs in sets:
        for i, P in enumerate(msgs):
            pa, ca = list(AZ), list(AZ)
            rng.shuffle(pa)
            rng.shuffle(ca)
            true = rng.randrange(10 ** 5)
            ct = encrypt(P, chain_key(true, 5), pa, ca)
            if tag == "F":
                feas = [p for p in range(10 ** 5) if possible(chain_key(p, 5), ct=ct)]
                assert true in feas
                wrong = [p for p in feas if p != true]
                rng.shuffle(wrong)
                prim = [true] + sorted(wrong[:19])
            else:   # unpunctuated R21 passages: true primer given only
                prim = [true]
            for p in prim:
                lab = f"{tag}{i:02d}@{p:05d}"
                meta[lab] = {"fixture": f"{tag}{i:02d}", "true": p == true, "primer": p, "ct": ct, "truth": P}
                lines.append((lab, chain_key(p, 5), ct))
    print(f"c2: {len(lines)} lines ({sum(1 for m in meta.values() if m['fixture'][0] == 'F')} fixture lines)",
          flush=True)
    out = {}
    for model in ("ORTH", "ORTHXQ"):
        L = [solver_line(lab, k, ct, ANCH, seed(f"c2|{lab}"), "-") for lab, k, ct in lines]
        best, _ = run_solver(L, f"c2_{model}", 64, model=model)
        for lab, k, ct in lines:
            assert verify_row(best[lab], k, ct), lab
        fx = {}
        for lab, m in meta.items():
            fx.setdefault(m["fixture"], []).append((best[lab]["W"], lab))
        blind, true_read, wrong_best, detail = 0, 0, -1e9, {}
        for f, lst in sorted(fx.items()):
            lst.sort(reverse=True)
            top = lst[0][1]
            truth = meta[top]["truth"]
            tl = [lab for _, lab in lst if meta[lab]["true"]][0]
            tr = errs(best[tl]["plaintext"], truth) <= 5
            ok = meta[top]["true"] and errs(best[top]["plaintext"], truth) <= 5
            wr = [w for w, lab in lst if not meta[lab]["true"]]
            if f[0] == "F":
                blind += ok
                true_read += tr
                if wr:
                    wrong_best = max(wrong_best, max(wr))
            detail[f] = {"blind_readable": ok, "true_line_readable": tr, "true_W": best[tl]["W"],
                         "best_wrong_W": max(wr) if wr else None, "true_text": best[tl]["plaintext"]}
        unp = sum(v["true_line_readable"] for f, v in detail.items() if f[0] == "U")
        out[model] = {"fixtures_blind_readable": blind, "fixtures_true_line_readable": true_read, "of": 22,
                      "best_wrong_W_fixtures": wrong_best, "unpunctuated_true_line_readable": unp, "unp_of": 20,
                      "detail": detail}
        print(f"c2 {model}: blind readable {blind}/22, true line readable {true_read}/22, best wrong W "
              f"{wrong_best:.2f}; unpunctuated R21 passages (true primer) readable {unp}/20", flush=True)
    return out


if __name__ == "__main__":
    sha = assert_protocol()
    hashes = ensure_models()
    which = sys.argv[1]
    res = {"c1": c1, "c3": c3, "c2": c2}[which]()
    json.dump({"protocol": sha, "models": hashes, "result": res}, open(RUNS / f"{which}.json", "w"), indent=1)
