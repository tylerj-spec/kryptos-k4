#!/usr/bin/env python3
"""R81a post-freeze CROSS-CHECK of g5x.py's hash join against the explicit cipher (synthetic only; no K4 ciphertext).
Added after review of PR #76. Nothing here changes the frozen K4 outcome or any pre-registered rule.

g5x.py decides consistency from difference signatures (published positions in one slot must imply one shift). This
script decides the same question a second way, through R79's explicit decrypt (r79/families.py), never using the
difference equations:
  * for each key letter k, decrypt with k in every slot: P_k[i] is position i's plaintext under key letter k;
  * decrypt once more with a different letter in each slot: the letter that position i used gives its slot;
  * a setting is consistent iff every slot has one key letter k with P_k[i] equal to the published letter at all of
    its published positions.
36 plants: H7CT, H7TXT and LIB x keyword lengths 1..12 x both modes (plaintext-side or ciphertext-side alphabet free)
x all three operations, with and without ciphertext feedback. Each plant has its own small alphabet set: the planted
alphabet, its reverse, three rotations, sixteen two-letter swaps and six random orderings (27 alphabets), so some
neighbours of the true alphabet stay consistent and others do not. Domain checked exhaustively per plant: the plant's
family, every keyword length (LIB: the plant's rule and 11 random ones), the plant's stream and one other, and every
convention g5x.py runs (12 with a stream; LIB without one: 4), times the 27 alphabets.
Pass rules, for every plant, with the plant's own letters ("plant") and with letters from another stretch of text
("wrong"):
  agree    the explicit check and g5x.py's hash join (run on the same 27 alphabets) find the same settings in the domain;
  true     the true setting is found with the plant's letters and not with the wrong letters.
Usage: crosscheck_g5x.py OUT.json [PROCS=4]"""
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g5x as G  # noqa: E402

F79, core = G.F79, G.core
SEED = 810700
OPS3 = ("VIG", "BEAU", "VARB")
A2 = G.A2
AZ = core.AZ
FREE = "XFREE"


def small_tier(rng, A):
    out = [("PLANT", A), ("REV", A[::-1])]
    for r in rng.sample(range(1, 26), 3):
        out.append((f"ROT{r}", A[r:] + A[:r]))
    seen = set()
    while len(seen) < 16:
        x, y = sorted(rng.sample(range(26), 2))
        if (x, y) in seen:
            continue
        seen.add((x, y))
        L = list(A)
        L[x], L[y] = L[y], L[x]
        out.append((f"SWAP{A[x]}{A[y]}", "".join(L)))
    for k in range(6):
        L = list(AZ)
        rng.shuffle(L)
        out.append((f"RAND{k}", "".join(L)))
    names = [n for n, _ in out]
    TI = np.stack([np.array([a.index(ch) for ch in AZ]) for _, a in out]).astype(np.int64)
    return out, names, TI


def plants(rng, big_names, big_TI):
    defs = [d for d in F79.mapdefs() if not d[3]]
    stream_names = F79.streams()[0]
    out = []
    for fam in ("H7CT", "H7TXT", "LIB"):
        for j in range(12):
            m = j + 1
            mode = "PA-free" if j % 2 == 0 else "CA-free"
            op = OPS3[j % 3]
            fixed = A2[(j // 2) % 2]
            ka = A2[(j // 3) % 2]
            st = {"fam": fam}
            if fam == "LIB":
                cand = [d for d in defs if d[2] == m] or [d for d in F79.mapdefs() if d[2] == m]
                r, p, m, _ = cand[rng.randrange(len(cand))]
                L = 0 if (op != "VARB" and j % 4 in (0, 1)) else rng.randint(1, 7)
                if L == 0:
                    ka = "AZ"
                st.update({"rule": r, "rp": list(p), "m": m, "L": L, "control": False})
            elif fam == "H7CT":
                st.update({"m": m, "L": rng.randint(1, 48)})
            else:
                tn, d, o = stream_names[rng.randrange(len(stream_names))]
                st.update({"m": m, "text": tn, "d": d, "o": o})
            k = rng.randrange(len(big_names))
            A = "".join(AZ[v] for v in np.argsort(big_TI[k]))
            st.update({"pa": FREE if mode == "PA-free" else fixed, "ca": FREE if mode == "CA-free" else fixed,
                       "ka": ka, "op": op, "key": "".join(rng.choice(AZ) for _ in range(st["m"]))})
            off = rng.randrange(0, 600)
            out.append({"st": st, "mode": mode, "fixed": fixed, "alphabet": A, "alphabet_name": big_names[k],
                        "off": off, "wrong_off": (off + 211) % 600, "seed": rng.randrange(1 << 30)})
    return out


def domain(rng, item):
    """Settings (without key and free alphabet) for the plant's family, as g5x.py would enumerate them."""
    st = item["st"]
    fam = st["fam"]
    convs = [(ka, op, fx) for ka in A2 for op in OPS3 for fx in A2]
    dom = []
    if fam == "H7CT":
        Ls = sorted({st["L"], rng.choice([x for x in range(1, 49) if x != st["L"]])})
        for m in range(1, 13):
            for L in Ls:
                for ka, op, fx in convs:
                    dom.append({"fam": fam, "m": m, "L": L, "ka": ka, "op": op, "fixed": fx})
    elif fam == "H7TXT":
        names = F79.streams()[0]
        other = names[rng.randrange(len(names))]
        for m in range(1, 13):
            for tn, d, o in sorted({(st["text"], st["d"], st["o"]), tuple(other)}):
                for ka, op, fx in convs:
                    dom.append({"fam": fam, "m": m, "text": tn, "d": d, "o": o, "ka": ka, "op": op, "fixed": fx})
    else:
        defs = F79.mapdefs()
        rules = [(st["rule"], tuple(st["rp"]), st["m"])]
        while len(rules) < 12:
            r, p, m, _ = defs[rng.randrange(len(defs))]
            if (r, tuple(p), m) not in rules:
                rules.append((r, tuple(p), m))
        Ls = sorted({st["L"], 0 if st["L"] else rng.randint(1, 7)})
        for r, p, m in rules:
            for L in Ls:
                cv = convs if L else [("AZ", op, fx) for op in ("VIG", "BEAU") for fx in A2]
                for ka, op, fx in cv:
                    dom.append({"fam": fam, "rule": r, "rp": list(p), "m": m, "L": L, "control": False, "ka": ka,
                                "op": op, "fixed": fx})
    return dom


def key_of(d, mode, free_name):
    fam = d["fam"]
    if fam == "LIB":
        rule, stream = [d["rule"], list(d["rp"]), d["m"]], ["L", d["L"]]
    else:
        rule = ["REP", [], d["m"]]
        stream = ["L", d["L"]] if fam == "H7CT" else ["T", d["text"], d["d"], d["o"]]
    pa, ca = (free_name, d["fixed"]) if mode == "PA-free" else (d["fixed"], free_name)
    return json.dumps([fam, rule, stream, d["ka"], d["op"], pa, ca])


def key_of_found(f):
    return json.dumps([f["family"], f["rule"], f["stream"], f["ka"], f["op"], f["pa"], f["ca"]])


def explicit(ct, dom, mode, tier, wants):
    """Consistent settings by the explicit cipher, for each list of published letters in wants."""
    found = [set() for _ in wants]
    for d in dom:
        m = d["m"]
        KA = core.ALPH[d["ka"]]
        base = {x: y for x, y in d.items() if x != "fixed"}
        base["pa"], base["ca"] = (FREE, d["fixed"]) if mode == "PA-free" else (d["fixed"], FREE)
        for name, A in tier:
            core.ALPH[FREE] = A
            P = [F79.decrypt(ct, dict(base, key=KA[k] * m)) for k in range(26)]
            Q = F79.decrypt(ct, dict(base, key=KA[:m]))
            slot = {}
            for i in G.POS:
                js = [j for j in range(m) if P[j][i] == Q[i]]
                assert len(js) == 1, (d, i, js)
                slot[int(i)] = js[0]
            for w, W in enumerate(wants):
                ok = True
                for j in set(slot.values()):
                    pos = [i for i in slot if slot[i] == j]
                    if not any(all(P[k][i] == W[i] for i in pos) for k in range(26)):
                        ok = False
                        break
                if ok:
                    found[w].add(key_of(d, mode, name))
    return found


def run_item(item):
    rng = random.Random(item["seed"])
    st = item["st"]
    core.ALPH[FREE] = item["alphabet"]
    pt = F79.texts()["K13PT"][item["off"]:item["off"] + 97]
    wrong = F79.texts()["K13PT"][item["wrong_off"]:item["wrong_off"] + 97]
    ct = F79.encrypt(pt, st)
    assert F79.decrypt(ct, st) == pt
    tier, names, TI = small_tier(rng, item["alphabet"])
    dom = domain(rng, item)
    wants = [{int(i): pt[i] for i in G.POS}, {int(i): wrong[i] for i in G.POS}]
    ex = explicit(ct, dom, item["mode"], tier, wants)
    domkeys = {key_of(d, item["mode"], n) for d in dom for n, _ in tier}
    true_key = key_of(dict({x: y for x, y in st.items() if x not in ("pa", "ca", "key")}, fixed=item["fixed"]),
                      item["mode"], "PLANT")
    assert true_key in domkeys
    res = {}
    for w, (lab, text) in enumerate((("plant", pt), ("wrong", wrong))):
        G.WANT = np.array([ord(text[p]) - 65 for p in G.POS])
        _, fd = G.run_ct(ct, names, TI)
        hj_all = {key_of_found(f) for f in fd[item["mode"]]}
        hj = hj_all & domkeys
        res[lab] = {"explicit": len(ex[w]), "hash_join": len(hj), "hash_join_outside_domain": len(hj_all - domkeys),
                    "agree": hj == ex[w], "true_found": true_key in ex[w],
                    "only_explicit": sorted(ex[w] - hj)[:5], "only_hash_join": sorted(hj - ex[w])[:5],
                    "alphabets_found": sorted({json.loads(k)[5 if item["mode"] == "PA-free" else 6] for k in ex[w]})}
    ok = (res["plant"]["agree"] and res["wrong"]["agree"] and res["plant"]["true_found"]
          and not res["wrong"]["true_found"])
    return {"family": st["fam"], "m": st["m"], "mode": item["mode"], "op": st["op"], "ka": st["ka"],
            "fixed": item["fixed"], "stream": st.get("L", [st.get("text"), st.get("d"), st.get("o")]),
            "rule": [st.get("rule", "REP"), st.get("rp", [])], "plant_alphabet": item["alphabet_name"],
            "domain_settings": len(dom), "domain_pairs": len(dom) * len(tier), **res, "ok": ok}


def main():
    from multiprocessing import Pool
    outp = sys.argv[1]
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    rng = random.Random(SEED)
    big_names, big_TI = G.tier()
    items = plants(rng, big_names, big_TI)
    with Pool(procs) as pool:
        rows = pool.map(run_item, items, chunksize=1)
    allok = all(r["ok"] for r in rows)
    for r in rows:
        print(f"{r['family']:5s} m={r['m']:2d} {r['mode']} {r['op']:4s} pairs {r['domain_pairs']:5d} | plant: explicit "
              f"{r['plant']['explicit']} hash-join {r['plant']['hash_join']} agree {r['plant']['agree']} true "
              f"{r['plant']['true_found']} | wrong: {r['wrong']['explicit']}/{r['wrong']['hash_join']} agree "
              f"{r['wrong']['agree']} | {'OK' if r['ok'] else 'FAIL'}", flush=True)
    summ = {"plants": len(rows), "ok": sum(r["ok"] for r in rows),
            "pairs_checked": sum(r["domain_pairs"] for r in rows),
            "consistent_found_plant": sum(r["plant"]["explicit"] for r in rows),
            "consistent_found_wrong": sum(r["wrong"]["explicit"] for r in rows)}
    Path(outp).write_text(json.dumps({"label": "post-freeze cross-check of g5x.py against the explicit cipher "
                                               "(synthetic only)", "seed": SEED, "all_ok": allok, "summary": summ,
                                      "rows": rows}, indent=1, default=str) + "\n")
    print(json.dumps(summ), "ALL OK" if allok else "SOME FAILED")


if __name__ == "__main__":
    main()
