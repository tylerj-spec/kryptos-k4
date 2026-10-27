#!/usr/bin/env python3
"""E6 (AMENDMENT_R30_4.md): German, Dutch and mixed word models.
  python3 e6.py c6     calibration on fresh DE/NL fixtures (+ 10 R21 English passages for MIX), blind among wrong primers
  python3 e6.py run    K4: all 585 Carter passes + 39 Gromark primers under each model, 64 restarts"""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e4_book as eb  # noqa: E402
import r30lib  # noqa: E402
from r30lib import (ANCH, AZ, DATA, HERE, K4, RUNS, assert_protocol, chain_key, encrypt, forced_mask, possible,  # noqa: E402
                    run_solver, seed, solver_line, verify_row)

AMEND4 = "AMENDMENT_R30_4.md"
r30lib.MODELS.update({m: RUNS / f"word_model_{m.lower()}.tsv" for m in ("DE", "NL", "MIX")})
BOOK = HERE.parents[1] / "archive" / "sources" / "carter_mace_1923_v1_doran_google_ocr.txt"


def check_amendment():
    want = [ln.split()[0] for ln in (HERE / "AMENDMENT.sha256").read_text().splitlines() if ln.endswith(AMEND4)][0]
    assert hashlib.sha256((HERE / AMEND4).read_bytes()).hexdigest() == want, "amendment 4 changed"
    meta = json.load(open(RUNS / "lang_models.json"))
    for m in ("de", "nl", "mix"):
        assert hashlib.sha256((RUNS / f"word_model_{m}.tsv").read_bytes()).hexdigest() == meta[m]["sha256"]
    return want


def errs(a, b):
    return sum(x != y for x, y in zip(a, b))


def c6():
    fx = json.loads((HERE / "fixtures_lang.json").read_text())
    en = json.loads((DATA / "reference_messages.json").read_text())["calibration"][:10]
    rng = random.Random(30006)
    msgs = [("DE", i, P) for i, P in enumerate(fx["DE"])] + [("NL", i, P) for i, P in enumerate(fx["NL"])] + \
           [("EN", i, P) for i, P in enumerate(en)]
    cases = []
    for lang, i, P in msgs:
        pa, ca = list(AZ), list(AZ)
        rng.shuffle(pa)
        rng.shuffle(ca)
        true = rng.randrange(10 ** 5)
        ct = encrypt(P, chain_key(true, 5), pa, ca)
        feas = [p for p in range(10 ** 5) if possible(chain_key(p, 5), ct=ct)]
        wrong = [p for p in feas if p != true]
        rng.shuffle(wrong)
        cases.append((f"{lang}{i:02d}", lang, P, ct, [true] + sorted(wrong[:9]), true))
    out = {}
    for model, langs in (("DE", {"DE"}), ("NL", {"NL"}), ("MIX", {"DE", "NL", "EN"})):
        lines, meta = [], {}
        for fid, lang, P, ct, prims, true in cases:
            if lang not in langs:
                continue
            for p in prims:
                lab = f"{fid}@{p:05d}"
                meta[lab] = (fid, p == true, P, ct, p)
                lines.append(solver_line(lab, chain_key(p, 5), ct, ANCH, seed(f"c6|{model}|{lab}")))
        best, _ = run_solver(lines, f"c6_{model}", 64, model=model)
        per, wrong_best = {}, -1e9
        for lab, (fid, is_true, P, ct, p) in meta.items():
            assert verify_row(best[lab], chain_key(p, 5), ct), lab
            per.setdefault(fid, []).append((best[lab]["W"], lab))
            if not is_true:
                wrong_best = max(wrong_best, best[lab]["W"])
        blind, detail = 0, {}
        for fid, lst in sorted(per.items()):
            lst.sort(reverse=True)
            top = lst[0][1]
            ok = meta[top][1] and errs(best[top]["plaintext"], meta[top][2]) <= 5
            blind += ok
            tl = [lab for _, lab in lst if meta[lab][1]][0]
            detail[fid] = {"blind_readable": ok, "true_W": best[tl]["W"], "true_text": best[tl]["plaintext"],
                           "true_wrong_letters": errs(best[tl]["plaintext"], meta[tl][2])}
        out[model] = {"blind_readable": blind, "of": len(per), "bar": wrong_best, "detail": detail}
        print(f"c6 {model}: blind readable {blind}/{len(per)}; best wrong-primer W {wrong_best:.2f}", flush=True)
    return out


def run():
    c6r = json.load(open(RUNS / "c6.json"))["result"]
    text, _ = eb.normalise(BOOK.read_bytes().decode("utf-8", errors="replace"))
    prev = json.load(open(RUNS / "e4_carter_v1_doran.json"))
    S = []
    for x in prev["ranked"]:
        _, _, d, a, off = x["id"].split("|")
        S.append((x["id"], eb.key_of(text, d, a, int(off))))
    S += [(f"G5|{p:05d}", chain_key(p, 5)) for p in range(10 ** 5) if possible(chain_key(p, 5))]
    keys = dict(S)
    res = {}
    for model in ("DE", "NL", "MIX"):
        t0 = time.time()
        bar = c6r[model]["bar"]
        gate = c6r[model]["blind_readable"] >= (15 if model == "MIX" else 5)
        L = [solver_line(i, k, K4, ANCH, seed(f"{model}|{i}")) for i, k in S]
        best, _ = run_solver(L, f"e6_{model}", 64, model=model)
        ranked = []
        for i, k in S:
            assert verify_row(best[i], k, K4), i
            fm = forced_mask(k, K4, ANCH)
            ranked.append({"id": i, "W": best[i]["W"], "plaintext": best[i]["plaintext"], "forced_mask": fm,
                           "forced_beyond_clues": sum(1 for j, c in enumerate(fm) if c != "?" and j not in ANCH)})
        ranked.sort(key=lambda x: -x["W"])
        above = [x for x in ranked if x["W"] > bar]
        rep_ids = list(dict.fromkeys([x["id"] for x in above] + [x["id"] for x in ranked[:5]]))
        rb, _ = run_solver([solver_line(i, keys[i], K4, ANCH, seed(f"{model}|{i}|rep")) for i in rep_ids],
                           f"e6_{model}_rep", 64, model=model)
        rep = {i: {"W": rb[i]["W"], "plaintext": rb[i]["plaintext"],
                   "letters_changed_vs_screen": errs(rb[i]["plaintext"], next(x for x in ranked if x["id"] == i)["plaintext"])}
               for i in rep_ids}
        cands = [x["id"] for x in above if rep[x["id"]]["letters_changed_vs_screen"] <= 5]
        W = sorted(x["W"] for x in ranked)
        summ = {"family": "e6", "model": model, "gate_passed": gate, "settings": len(S), "restarts": 64, "bar": bar,
                "best_W": W[-1], "median_W": W[len(W) // 2], "n_above_bar": len(above), "candidates": cands,
                "best_book_W": max(x["W"] for x in ranked if x["id"].startswith("BOOK")),
                "best_g5_W": max(x["W"] for x in ranked if x["id"].startswith("G5")), "seconds": round(time.time() - t0)}
        json.dump({"summary": summ, "ranked": ranked, "replication": rep}, open(RUNS / f"e6_{model}.json", "w"), indent=1)
        print(json.dumps(summ), flush=True)
        for x in ranked[:5]:
            print(f"  {x['W']:8.2f} +{x['forced_beyond_clues']:2d} {x['id']:<36} {x['plaintext']} | rep "
                  f"{rep[x['id']]['W']:.2f} changed {rep[x['id']]['letters_changed_vs_screen']}", flush=True)
        res[model] = summ
    return res


if __name__ == "__main__":
    sha, a4 = assert_protocol(), check_amendment()
    if sys.argv[1] == "c6":
        json.dump({"protocol": sha, "amendment4": a4, "result": c6()}, open(RUNS / "c6.json", "w"), indent=1)
    else:
        run()
