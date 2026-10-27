#!/usr/bin/env python3
"""R30 K4 searches (PREREGISTRATION_R30.md).
  python3 search.py e1 MODEL       all E1 chain-addition passes (16-restart screen, top 20 replicated at 64)
  python3 search.py e2 MODEL       all one-cycle R27 route + Gromark settings (same)
  python3 search.py g5 MODEL       39 feasible 5-digit Gromark primers, 64 restarts (+ replication above the bar)
  python3 search.py r2 MODEL       39 two-cycle R27 route settings, 64 restarts (+ replication above the bar)
Every reported row is independently re-encrypted to K4 (verify_row) and carries its forced-letter mask."""
import csv
import json
import sys
import time

from r30lib import (ANCH, BAR_ORTH, K4, RUNS, assert_protocol, chain_key, ensure_models, forced_mask, possible,
                    route, run_solver, seed, setup, solver_line, verify_row)


def settings(family):
    """Yield (label, key, ct_sub, anch_sub, perm_token, perm, order)."""
    if family == "e1":
        for r in csv.DictReader(open(RUNS / "e1_passes.csv")):
            b = int(r["b"])
            yield f"E1|b{b}|{r['primer']}", chain_key(int(r["primer"]), b), K4, dict(ANCH), "-", None, None
    elif family == "g5":
        for p in range(10 ** 5):
            k = chain_key(p, 5)
            if possible(k):
                yield f"G5|{p:05d}", k, K4, dict(ANCH), "-", None, None
    elif family in ("e2", "r2"):
        want = 1 if family == "e2" else 2
        for r in csv.DictReader(open(RUNS / "r27_passes.csv")):
            if int(r["checks"]) != want:
                continue
            perm = route(r["route"])
            ci, an, ps = setup(K4, perm, r["order"])
            yield (f"R27|{r['route']}|{r['order']}|{r['primer']}", chain_key(int(r["primer"]), 5), ci, an, ps,
                   perm, r["order"])


def describe(row, s):
    lab, k, ci, an, ps, perm, order = s
    assert verify_row(row, k, K4, perm, order or "T_then_S"), lab
    fm = forced_mask(k, ci, an, perm if order == "T_then_S" else None)
    extra = sum(1 for i, c in enumerate(fm) if c != "?" and i not in ANCH)
    return {"id": lab, "W": row["W"], "plaintext": row["plaintext"], "forced_mask": fm, "forced_beyond_clues": extra,
            "plaintext_alphabet": row["plaintext_alphabet"], "ciphertext_alphabet": row["ciphertext_alphabet"]}


def errs(a, b):
    return sum(x != y for x, y in zip(a, b))


if __name__ == "__main__":
    sha = assert_protocol()
    hashes = ensure_models()
    family, model = sys.argv[1], sys.argv[2]
    bar = BAR_ORTH
    if model == "ORTHXQ":
        c2 = json.load(open(RUNS / "c2.json"))["result"]["ORTHXQ"]
        bar = max(BAR_ORTH, c2["best_wrong_W_fixtures"])
    S = list(settings(family))
    R = 64 if family in ("g5", "r2") else 16
    t0 = time.time()
    print(f"{family}/{model}: {len(S)} settings at {R} restarts; bar {bar:.2f}", flush=True)
    lines = [solver_line(s[0], s[1], s[2], s[3], seed(f"{model}|{s[0]}"), s[4]) for s in S]
    best, _ = run_solver(lines, f"{family}_{model}_screen", R, model=model)
    byid = {s[0]: s for s in S}
    ranked = sorted((describe(best[s[0]], s) for s in S), key=lambda x: -x["W"])
    # replication: top 20 (screens) or everything above the bar (64-restart families), new seeds, 64 restarts
    rep_ids = [x["id"] for x in ranked[:20]] if R == 16 else [x["id"] for x in ranked if x["W"] > bar]
    rep = {}
    if rep_ids:
        L = [solver_line(i, byid[i][1], byid[i][2], byid[i][3], seed(f"{model}|{i}|rep"), byid[i][4]) for i in rep_ids]
        rb, _ = run_solver(L, f"{family}_{model}_rep", 64, model=model)
        for i in rep_ids:
            d = describe(rb[i], byid[i])
            first = next(x for x in ranked if x["id"] == i)
            d["letters_changed_vs_screen"] = errs(d["plaintext"], first["plaintext"])
            rep[i] = d
    cands = [i for i, d in rep.items() if max(d["W"], next(x["W"] for x in ranked if x["id"] == i)) > bar
             and d["letters_changed_vs_screen"] <= 5]
    W = sorted(x["W"] for x in ranked)
    summary = {"protocol": sha, "models": hashes, "family": family, "model": model, "settings": len(S),
               "restarts": R, "bar": bar, "best_W": W[-1], "median_W": W[len(W) // 2], "n_above_bar": sum(w > bar for w in W),
               "candidates": cands, "seconds": round(time.time() - t0)}
    json.dump({"summary": summary, "ranked": ranked, "replication": rep},
              open(RUNS / f"{family}_{model}.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))
    for x in ranked[:10]:
        r = rep.get(x["id"])
        tail = f" | rep {r['W']:.2f} changed {r['letters_changed_vs_screen']}" if r else ""
        print(f"  {x['W']:8.2f} +{x['forced_beyond_clues']:2d} {x['id']:<32} {x['plaintext']}{tail}")
