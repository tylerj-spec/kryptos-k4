#!/usr/bin/env python3
"""R89 POST-FREEZE exact checks against the published letters: CRIB-ASSISTED, EXCLUSION-ONLY. Run only after the
blind K4 evaluation (evaluate89.py) is committed and pushed, and only for the arms that passed the gate. Decrypts
only at the 24 published positions; changes no blind output. Written from the definitions (r89/PREREGISTRATION.md
G0); the alphabet list comes from witness89.py (standard library, independent of r89/f26l.py; tests compare them).
F26 / F26L (finite family, NO free key): every one of the 139,120 settings is decoded at the published positions and
  the matches counted. EXACT: a setting with 24/24; DROP: a setting with >= 23/24 (one published letter wrong or one
  wrong ciphertext letter feeding a published position). Reported: K4's maximum vs every shuffle's maximum.
RCT (free wiring): for each of the 448 settings the offsets come from the ciphertext; some wiring fits iff the 24
  (input contact, output contact) pairs form a partial bijection. EXACT all 24; DROP each one set aside (one wrong
  published PLAINTEXT letter; a wrong ciphertext letter would also change later offsets and is not covered).
Decision per arm (r89/PREREGISTRATION.md G5): EXCLUDED if K4 has no feasible setting (F26: none at 24/24, or at
  >= 23/24 for DROP); LEAD if K4 has one and no shuffle does (RCT: at >= 3 checks); otherwise CHANCE.
Usage: exact89.py TARGET.tsv ARMS OUT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import witness89 as W  # noqa: E402  (standard-library definitions)

AZ = W.AZ


def f26_settings():
    pairs = lambda b: [(u, v) for u in range(1, b) for v in range(1, b) if u != v]  # noqa: E731
    outers = [None] + [(k, sg, ph) for k in W.OUTER_KEYS for sg in (1, -1) for ph in range(len(W.OUTER_KEYS[k]))]
    return [(a, b, u, v, o) for o in outers for a in W.F26_ALPH for b in (5, 7, 9, 11) for (u, v) in pairs(b)]


def f26_hits(ct, pos, letters, settings):
    """Matches at the published positions for every setting (decoding those positions only)."""
    n = len(ct)
    inner = {}
    out = []
    for a, b, u, v, o in settings:
        if o not in inner:
            if o is None:
                inner[o] = ct
            else:
                U = W.OUTER_KEYS[o[0]]
                inner[o] = "".join(W.KRY[(W.KRY.index(ch) - o[1] * W.KRY.index(U[(i + o[2]) % len(U)])) % 26]
                                   for i, ch in enumerate(ct))
        m = inner[o]
        A = W.F26_ALPH[a]
        h = 0
        for k, want in zip(pos, letters):
            off = (k // b) * b
            t = min(b, n - off)
            j = k - off
            r = A.index(m[off + (j - u) % t]) // 13
            c = A.index(m[off + (j - v) % t]) % 13
            h += A[13 * r + c] == want
        out.append(h)
    return out


def rct_feasible(ct, pos, letters, st):
    ei, eo, d, m, q = st
    Ei, Eo = W.CONTACTS[ei], W.CONTACTS[eo]
    s, offs = 0, []
    for c in ct:
        offs.append(s)
        s += d * (2 if (AZ.index(c) + q) % m == 0 else 1)
    xs = [(Ei.index(p) + offs[i]) % 26 for i, p in zip(pos, letters)]
    ys = [(Eo.index(ct[i]) + offs[i]) % 26 for i in pos]
    for a in range(len(xs)):
        for b in range(a + 1, len(xs)):
            if (xs[a] == xs[b]) != (ys[a] == ys[b]):
                return False, None
    return True, len(xs) - len(set(xs))


def rct_settings():
    return [(ei, eo, d, m, q) for ei in W.CONTACTS for eo in W.CONTACTS for d in (1, -1) for m in (2, 3, 4, 5)
            for q in range(m)]


def main():
    tsv, arms, out = Path(sys.argv[1]), sys.argv[2].split(","), Path(sys.argv[3])
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # the published letters; this step runs only after the blind evaluation
    pos = [o + i for o, t in CLUES for i in range(len(t))]
    letters = [c for _, t in CLUES for c in t]
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    ids = ["K4"] + sorted(i for i in cts if i != "K4")
    rep = {"arms": arms, "positions": len(pos)}
    if "F26L" in arms:
        sts = f26_settings()
        per = {}
        for rid in ids:
            h = f26_hits(cts[rid], pos, letters, sts)
            mx = max(h)
            per[rid] = {"max_hits": mx, "n_at_max": h.count(mx), "n_ge_23": sum(x >= 23 for x in h),
                        "n_24": h.count(24), "best_settings": [sts[k] for k, x in enumerate(h) if x == mx][:10]}
        k4 = per["K4"]
        nulls = [per[i]["max_hits"] for i in ids[1:]]
        rep["F26"] = {"settings": len(sts), "k4": k4, "shuffle_max_hits": sorted(nulls, reverse=True),
                      "p_max_hits": (1 + sum(x >= k4["max_hits"] for x in nulls)) / (1 + len(nulls)),
                      "verdict_exact": "EXCLUDED" if k4["n_24"] == 0 else
                      ("LEAD" if all(per[i]["n_24"] == 0 for i in ids[1:]) else "CHANCE"),
                      "verdict_drop": "EXCLUDED" if k4["n_ge_23"] == 0 else
                      ("LEAD" if all(per[i]["n_ge_23"] == 0 for i in ids[1:]) else "CHANCE"),
                      "shuffles": {i: {k: per[i][k] for k in ("max_hits", "n_ge_23", "n_24")} for i in ids[1:]}}
    if "RCT" in arms:
        sts = rct_settings()
        res = {}
        for rid in ids:
            ex = [(st, *rct_feasible(cts[rid], pos, letters, st)) for st in sts]
            fe = [(st, c) for st, ok, c in ex if ok]
            dr = []
            for j in range(len(pos)):
                P, L = pos[:j] + pos[j + 1:], letters[:j] + letters[j + 1:]
                dr += [(pos[j], st, c) for st in sts for ok, c in [rct_feasible(cts[rid], P, L, st)] if ok]
            res[rid] = {"exact_feasible": len(fe), "exact_max_checks": max((c for _, c in fe), default=-1),
                        "drop_feasible": len(dr), "drop_max_checks": max((c for *_, c in dr), default=-1),
                        "exact_settings": fe[:20], "drop_settings": dr[:20]}

        def decide(key_n, key_c):
            k4 = res["K4"]
            if k4[key_n] == 0:
                return "EXCLUDED"
            reach = sum(res[i][key_c] >= k4[key_c] for i in ids[1:])
            return "LEAD" if k4[key_c] >= 3 and reach == 0 else "CHANCE"

        rep["RCT"] = {"settings": len(sts), "k4": res["K4"],
                      "verdict_exact": decide("exact_feasible", "exact_max_checks"),
                      "verdict_drop": decide("drop_feasible", "drop_max_checks"),
                      "shuffles_with_feasible_exact": sum(res[i]["exact_feasible"] > 0 for i in ids[1:]),
                      "shuffles_with_feasible_drop": sum(res[i]["drop_feasible"] > 0 for i in ids[1:])}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    for a in ("F26", "RCT"):
        if a in rep:
            r = rep[a]
            print(a, "EXACT", r["verdict_exact"], "DROP", r["verdict_drop"],
                  {k: r[k] for k in r if k not in ("k4", "shuffles", "shuffle_max_hits")}, "| K4",
                  {k: v for k, v in r["k4"].items() if "settings" not in k})


if __name__ == "__main__":
    main()
