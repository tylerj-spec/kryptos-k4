#!/usr/bin/env python3
"""R81a post-freeze POWER CONTROL for g5x.py (synthetic only; no K4 ciphertext is used). Committed version of the
one-off plant test that preceded the pre-registration, extended to both modes and all three families.
Each plant encrypts 97 letters of the K1-K3 plaintext with one of R79's H7CT / H7TXT / LIB settings in which one
keyword alphabet (plaintext side for PA-free, ciphertext side for CA-free) is a random ordering from R76's large tier;
the "published letters" are the plant's own letters at the 24 published positions. Pass rules:
  plant     the true setting (family, rule, stream, ka, op, fixed alphabet, free alphabet) is among those found;
  wrong     with the published letters taken from a different stretch of text, the true setting is not found.
Nothing here changes the frozen K4 outcome or any pre-registered rule.
Usage: control_g5x.py OUT.json"""
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g5x as G  # noqa: E402

SEED = 810600
PLANTS = [  # (family, mode, fixed alphabet, ka, op, stream choice)
    ("H7CT", "PA-free", "KRY", "AZ", "BEAU", "lag"),
    ("H7CT", "CA-free", "AZ", "KRY", "VIG", "lag"),
    ("H7TXT", "PA-free", "AZ", "KRY", "VARB", "text"),
    ("H7TXT", "CA-free", "KRY", "AZ", "BEAU", "text"),
    ("LIB", "PA-free", "AZ", "KRY", "VIG", "lag"),
    ("LIB", "CA-free", "AZ", "AZ", "BEAU", "none"),
]


def build(rng, names, TI, spec):
    fam, mode, fixed, ka, op, sk = spec
    k = rng.randrange(len(names))
    A = "".join(G.core.AZ[v] for v in np.argsort(TI[k]))
    assert all(A.index(ch) == TI[k][G.core.AZ.index(ch)] for ch in G.core.AZ)
    G.core.ALPH["X1"] = A
    m = rng.randint(2, 12)
    if fam == "LIB":
        st = G.F79.random_setting(rng, "LIB", 2, 12)
        st["L"] = 0 if sk == "none" else rng.randint(1, 7)
        m = st["m"]
    else:
        st = {"fam": fam, "m": m}
        if fam == "H7CT":
            st["L"] = rng.randint(1, 48)
        else:
            tn, d, o = rng.choice(G.F79.streams()[0])
            st.update({"text": tn, "d": d, "o": o})
    st.update({"pa": "X1" if mode == "PA-free" else fixed, "ca": "X1" if mode == "CA-free" else fixed, "ka": ka,
               "op": op, "key": "".join(rng.choice(G.core.AZ) for _ in range(m))})
    off = rng.randrange(0, 600)
    pt = G.F79.texts()["K13PT"][off:off + 97]
    ct = G.F79.encrypt(pt, st)
    assert G.F79.decrypt(ct, st) == pt
    wrong_off = (off + 211) % 600
    wrong = G.F79.texts()["K13PT"][wrong_off:wrong_off + 97]
    if fam == "LIB":
        rule = [st["rule"], list(st["rp"]), st["m"]]
        stream = ["L", st["L"]]
    else:
        rule = ["REP", [], m]
        stream = ["L", st["L"]] if fam == "H7CT" else ["T", st["text"], st["d"], st["o"]]
    want = {"family": fam, "rule": rule, "stream": stream, "ka": ka, "op": op,
            ("ca" if mode == "PA-free" else "pa"): fixed, ("pa" if mode == "PA-free" else "ca"): names[k]}
    return {"spec": list(spec), "alphabet": names[k], "setting": {x: y for x, y in st.items() if x != "key"},
            "ct": ct, "pt": pt, "wrong": wrong, "want": want, "mode": mode}


_T = None


def _work(job):
    global _T
    if _T is None:
        _T = G.tier()
    names, TI = _T
    item, which = job
    text = item["pt"] if which == "plant" else item["wrong"]
    G.WANT = np.array([ord(text[p]) - 65 for p in G.POS])
    counts, found = G.run_ct(item["ct"], names, TI)
    w = item["want"]
    hit = any(all(f.get(x) == y for x, y in w.items()) for f in found[item["mode"]])
    return {"found_PA_free": len(found["PA-free"]), "found_CA_free": len(found["CA-free"]), "true_found": hit}


def main():
    from multiprocessing import Pool
    outp = sys.argv[1]
    rng = random.Random(SEED)
    names, TI = G.tier()
    items = [build(rng, names, TI, sp) for sp in PLANTS]
    jobs = [(it, w) for it in items for w in ("plant", "wrong")]
    with Pool(4) as pool:
        res = pool.map(_work, jobs, chunksize=1)
    rows, allok = [], True
    for (it, w), r in zip(jobs, res):
        ok = r["true_found"] if w == "plant" else not r["true_found"]
        allok &= ok
        rows.append({"which": w, "spec": it["spec"], "alphabet": it["alphabet"], "setting": it["setting"], **r,
                     "ok": ok})
        print(w, it["spec"][:2], it["alphabet"], r, "OK" if ok else "FAIL", flush=True)
    Path(outp).write_text(json.dumps({"label": "post-freeze power control for g5x (synthetic only)", "seed": SEED,
                                      "all_ok": allok, "rows": rows}, indent=1, default=str) + "\n")
    print("ALL OK" if allok else "SOME FAILED")


if __name__ == "__main__":
    main()
