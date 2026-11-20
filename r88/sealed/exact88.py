#!/usr/bin/env python3
"""R88 POST-FREEZE exact check of the RQ family against the published letters: CRIB-ASSISTED, EXCLUSION-ONLY.
Run only after the blind K4 evaluation (evaluate88.py) is committed and pushed. It decrypts nothing and changes no
blind output. Written from the definition (r88/PREREGISTRATION.md G0), not from r88/rq88.py (tests compare the two).
For a setting (side, A, n, delta), s_i = delta * floor(i / n), every published position i with plaintext letter p and
ciphertext letter c gives one pair that a free alphabet must map bijectively:
  side PA:  p  <->  (A-place(c) - s_i) mod 26          side CA:  (A-place(p) + s_i) mod 26  <->  c
Some free alphabet fits iff the pairs form a partial bijection. checks = positions - distinct left-hand values.
Scope: 2 sides x 4 alphabets x delta 1-25 x n 1-96 = 19,200 settings (delta 25 is the blind step's d = -1; n >= 97 is
one alphabet, excluded by L02), on K4 and the 100 shuffles of r88/k4/TARGET.tsv identically.
  EXACT  all 24 published letters assumed right;   DROP  each one set aside in turn (one wrong letter).
Decision (r88/PREREGISTRATION.md G5): EXCLUDED if K4 has no feasible setting; LEAD if K4 has a feasible setting with
>= 3 checks and no shuffle reaches K4's maximum; otherwise CHANCE (reported with the shuffle comparison).
Usage: exact88.py TARGET.tsv OUT.json"""
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
SETTINGS = [(side, a, n, dl) for side in ("PA", "CA") for a in ALPH for dl in range(1, 26) for n in range(1, 97)]


def feasible(ct, pos, letters, st):
    """(ok, checks) for one setting; pairs compared directly (no dictionaries shared with rq88)."""
    side, A, n, dl = st[0], ALPH[st[1]], st[2], st[3]
    ls, rs = [], []
    for i, p in zip(pos, letters):
        s = dl * (i // n)
        if side == "PA":
            ls.append(ord(p) - 65)
            rs.append((A.index(ct[i]) - s) % 26)
        else:
            ls.append((A.index(p) + s) % 26)
            rs.append(ord(ct[i]) - 65)
    for a in range(len(ls)):
        for b in range(a + 1, len(ls)):
            if (ls[a] == ls[b]) != (rs[a] == rs[b]):
                return False, None
    return True, len(ls) - len(set(ls))


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
