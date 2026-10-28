#!/usr/bin/env python3
"""E5 (AMENDMENT_R30_1.md): one mis-carved clue letter, two-free-alphabet 5-digit Gromark, in place.
  python3 e5.py c5     calibration: planted messages with one corrupted clue-position ciphertext letter
  python3 e5.py run    oracle stage over all (dropped clue, primer) pairs, then the English search"""
import hashlib
import json
import random
import sys
import time
from multiprocessing import Pool

from r30lib import (ANCH, AZ, BAR_ORTH, DATA, HERE, K4, RUNS, assert_protocol, chain_key, checks, encrypt,
                    ensure_models, forced_mask, possible, run_solver, seed, solver_line, verify_row)

AMEND = "cf583846b942acad815c0c53448c573df92932a199662123a2f460adc594b343"
BUDGET = 8000


def assert_amendment():
    got = hashlib.sha256((HERE / "AMENDMENT_R30_1.md").read_bytes()).hexdigest()
    assert got == AMEND, "amendment changed"
    return got


def without(d):
    return {i: c for i, c in ANCH.items() if i != d}


def scan_d(d):
    an = without(d)
    return d, [p for p in range(10 ** 5) if possible(chain_key(p, 5), anch=an)]


def errs(a, b):
    return sum(x != y for x, y in zip(a, b))


def c5():
    bases = json.loads((DATA / "reference_messages.json").read_text())["calibration"]
    rng = random.Random(30005)
    items = []
    for i, P in enumerate(bases):
        pa, ca = list(AZ), list(AZ)
        rng.shuffle(pa)
        rng.shuffle(ca)
        k = chain_key(rng.randrange(10 ** 5), 5)
        ct = list(encrypt(P, k, pa, ca))
        d = rng.choice(sorted(ANCH))
        ct[d] = rng.choice([c for c in AZ if c != ct[d]])
        items.append((f"C5_{i:02d}_pos{d + 1}", P, k, "".join(ct), without(d)))
    out = {}
    for R in (16, 64):
        lines = [solver_line(lab, k, ct, an, seed(f"c5|{lab}|{R}")) for lab, P, k, ct, an in items]
        best, _ = run_solver(lines, f"c5_{R}", R)
        rows = {lab: {"W": best[lab]["W"], "wrong_letters": errs(best[lab]["plaintext"], P)}
                for lab, P, k, ct, an in items}
        n = sum(v["wrong_letters"] <= 5 for v in rows.values())
        out[R] = {"readable": n, "of": 20, "rows": rows}
        print(f"c5: {R} restarts readable {n}/20", flush=True)
    return out


def run():
    t0 = time.time()
    full = {p for p in range(10 ** 5) if possible(chain_key(p, 5))}
    assert len(full) == 39
    with Pool(4) as pool:
        res = dict(pool.map(scan_d, sorted(ANCH)))
    S = []
    per_d = {}
    for d in sorted(ANCH):
        an = without(d)
        cyc = checks(None, anch=an)
        new = [p for p in res[d] if p not in full]
        per_d[d + 1] = {"passes": len(res[d]), "new": len(new), "cycles": cyc}
        S += [(cyc, d, p) for p in new]
    total = len(S)
    S.sort(key=lambda x: (-x[0], x[1], x[2]))
    S = S[:BUDGET]
    print(f"E5 oracle: {total} new settings ({len(S)} searched); per dropped position (1-based): "
          f"{json.dumps(per_d)}", flush=True)
    lab = lambda d, p: f"E5|pos{d + 1}|{p:05d}"  # noqa: E731
    lines = [solver_line(lab(d, p), chain_key(p, 5), K4, without(d), seed(f"ORTH|{lab(d, p)}")) for _, d, p in S]
    best, _ = run_solver(lines, "e5_screen", 16)
    ranked = []
    for cyc, d, p in S:
        r, k, an = best[lab(d, p)], chain_key(p, 5), without(d)
        assert verify_row(r, k, K4, anch=an), lab(d, p)
        fm = forced_mask(k, K4, an)
        ranked.append({"id": lab(d, p), "W": r["W"], "plaintext": r["plaintext"], "forced_mask": fm,
                       "forced_beyond_clues": sum(1 for i, c in enumerate(fm) if c != "?" and i not in an),
                       "cycles": cyc, "plaintext_alphabet": r["plaintext_alphabet"],
                       "ciphertext_alphabet": r["ciphertext_alphabet"]})
    ranked.sort(key=lambda x: -x["W"])
    rep = {}
    top = ranked[:20]
    L = []
    for x in top:
        d, p = int(x["id"].split("|")[1][3:]) - 1, int(x["id"].split("|")[2])
        L.append(solver_line(x["id"], chain_key(p, 5), K4, without(d), seed(f"ORTH|{x['id']}|rep")))
    rb, _ = run_solver(L, "e5_rep", 64) if L else ({}, [])
    for x in top:
        rep[x["id"]] = {"W": rb[x["id"]]["W"], "plaintext": rb[x["id"]]["plaintext"],
                        "letters_changed_vs_screen": errs(rb[x["id"]]["plaintext"], x["plaintext"])}
    cands = [i for i, d in rep.items() if max(d["W"], next(x["W"] for x in ranked if x["id"] == i)) > BAR_ORTH
             and d["letters_changed_vs_screen"] <= 5]
    W = sorted(x["W"] for x in ranked)
    summary = {"family": "e5", "model": "ORTH", "settings": len(S), "settings_total": total, "per_dropped": per_d,
               "restarts": 16, "bar": BAR_ORTH, "best_W": W[-1] if W else None,
               "median_W": W[len(W) // 2] if W else None, "n_above_bar": sum(w > BAR_ORTH for w in W),
               "candidates": cands, "seconds": round(time.time() - t0)}
    return summary, ranked, rep


if __name__ == "__main__":
    sha, amend = assert_protocol(), assert_amendment()
    ensure_models()
    if sys.argv[1] == "c5":
        out = c5()
        json.dump({"protocol": sha, "amendment": amend, "result": out}, open(RUNS / "c5.json", "w"), indent=1)
    else:
        summary, ranked, rep = run()
        summary.update({"protocol": sha, "amendment": amend})
        json.dump({"summary": summary, "ranked": ranked, "replication": rep}, open(RUNS / "e5_ORTH.json", "w"),
                  indent=1)
        print(json.dumps(summary, indent=1))
        for x in ranked[:10]:
            r = rep.get(x["id"])
            tail = f" | rep {r['W']:.2f} changed {r['letters_changed_vs_screen']}" if r else ""
            print(f"  {x['W']:8.2f} +{x['forced_beyond_clues']:2d} {x['id']:<20} {x['plaintext']}{tail}")
