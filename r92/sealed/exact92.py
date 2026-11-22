#!/usr/bin/env python3
"""R92 POST-FREEZE exact check of the RXP family against the published letters: CRIB-ASSISTED, EXCLUSION-ONLY.
Run only after the blind K4 evaluation (evaluate92.py) is committed and pushed. It decrypts nothing and changes no
blind output. Written from the definition (r92/PREREGISTRATION.md G0), not from r92/rotor92.py (tests compare the two).
For a setting (E_in, E_out, n, r, d) every published position i with plaintext letter p and ciphertext letter c gives
x = (E_in-place(p) + s_i) mod 26 and y = (E_out-place(c) + s_i) mod 26, s_i = d * floor((i + r) / n); some wiring W with
W[x] = y at every position exists iff the pairs form a partial bijection. checks = positions - distinct x.
Scope: the 192 labels (16 alphabet pairs x n 2-4, r 1..n-1, d +-1), on K4 and the
200 shuffles of r92/k4/TARGET.tsv identically. The offsets depend on the position only, so one wrong letter of EITHER kind
at a published position changes exactly one pair: DROP covers one wrong published plaintext letter and one wrong
ciphertext letter at a published position (an error elsewhere does not enter the check).
  EXACT  all 24 published letters assumed right;   DROP  each one set aside in turn (one wrong letter).
Decision (r92/PREREGISTRATION.md G5): EXCLUDED if K4 has no feasible setting; LEAD if K4 has a feasible setting with
>= 3 checks and no shuffle reaches K4's maximum; otherwise CHANCE (reported with the shuffle comparison).
Usage: exact92.py TARGET.tsv OUT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(word):
    out = []
    for ch in word + AZ:
        if ch not in out:
            out.append(ch)
    return "".join(out)


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
SETTINGS = [(a, b, n, r, d) for a in ALPH for b in ALPH for n in (2, 3, 4) for r in range(1, n) for d in (1, -1)]


def feasible(ct, pos, letters, st):
    """(ok, checks) for one setting; pairs compared directly (no dictionaries shared with rotor87)."""
    ein, eout, n, r, d = ALPH[st[0]], ALPH[st[1]], st[2], st[3], st[4]
    xs, ys = [], []
    for i, p in zip(pos, letters):
        s = d * ((i + r) // n)
        xs.append((ein.index(p) + s) % 26)
        ys.append((eout.index(ct[i]) + s) % 26)
    for a in range(len(xs)):
        for b in range(a + 1, len(xs)):
            if (xs[a] == xs[b]) != (ys[a] == ys[b]):
                return False, None
    return True, len(xs) - len(set(xs))


def scan(ct, pos, letters):
    best, found = -1, []
    for st in SETTINGS:
        ok, c = feasible(ct, pos, letters, st)
        if ok:
            found.append({"setting": st, "checks": c})
            best = max(best, c)
    return {"feasible": len(found), "max_checks": best, "settings": found[:50]}


def decide(k4, nulls):
    if k4["feasible"] == 0:
        return "EXCLUDED"
    reach = sum(r["max_checks"] >= k4["max_checks"] for r in nulls)
    return "LEAD" if k4["max_checks"] >= 3 and reach == 0 else "CHANCE"


def main():
    tsv, out = Path(sys.argv[1]), Path(sys.argv[2])
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # the published letters; this step runs only after the blind evaluation
    pos = [o + i for o, t in CLUES for i in range(len(t))]
    letters = [c for _, t in CLUES for c in t]
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    ids = ["K4"] + sorted(i for i in cts if i != "K4")
    rep = {"settings": len(SETTINGS), "positions": len(pos), "exact": {}, "drop": {}}
    for rid in ids:
        rep["exact"][rid] = scan(cts[rid], pos, letters)
        per = []
        for j in range(len(pos)):
            r = scan(cts[rid], pos[:j] + pos[j + 1:], letters[:j] + letters[j + 1:])
            per.append({"dropped_position": pos[j], "feasible": r["feasible"], "max_checks": r["max_checks"],
                        "settings": r["settings"][:10]})
        rep["drop"][rid] = {"feasible": sum(p["feasible"] for p in per),
                            "max_checks": max(p["max_checks"] for p in per),
                            "by_dropped_position": per if rid == "K4" else
                            [p for p in per if p["feasible"]][:5]}
    nulls_e = [rep["exact"][i] for i in ids[1:]]
    nulls_d = [rep["drop"][i] for i in ids[1:]]
    rep["verdict_exact"] = decide(rep["exact"]["K4"], nulls_e)
    rep["verdict_drop"] = decide(rep["drop"]["K4"], nulls_d)
    rep["shuffles_with_feasible_exact"] = sum(r["feasible"] > 0 for r in nulls_e)
    rep["shuffles_with_feasible_drop"] = sum(r["feasible"] > 0 for r in nulls_d)
    rep["shuffles_drop_max_checks"] = sorted((r["max_checks"] for r in nulls_d), reverse=True)[:10]
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print("EXACT", rep["verdict_exact"], "| K4 feasible", rep["exact"]["K4"]["feasible"], "| shuffles with any",
          rep["shuffles_with_feasible_exact"], "| DROP", rep["verdict_drop"], "| K4 feasible", rep["drop"]["K4"]["feasible"],
          "max checks", rep["drop"]["K4"]["max_checks"], "| shuffles with any", rep["shuffles_with_feasible_drop"])


if __name__ == "__main__":
    main()
