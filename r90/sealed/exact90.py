#!/usr/bin/env python3
"""R90 POST-FREEZE exact check against the published letters: CRIB-ASSISTED, EXCLUSION-ONLY. Run only after the
blind K4 evaluation (evaluate90.py) is committed and pushed. Decodes only the 24 published positions; changes no blind
output. Written from r90/PREREGISTRATION.md G0; the alphabet list comes from witness90.py (standard library).
Every one of the 104,340 F26 / F26C settings is decoded at the published positions and the matches counted, on K4
and the 200 shuffles identically.
  EXACT    a setting with 24/24 (all published letters right);
  DROP-PT  a setting with >= 23/24 (one published plaintext letter wrong);
  DROP-CT  a setting with >= 22/24: the NECESSARY screen for one wrong ciphertext letter, which can change two
           decoded letters (ChatGPT's R89 review, correction C). A setting below 22 cannot be rescued by one
           ciphertext substitution; one at or above 22 would need checking (none is expected).
Decision (r90/PREREGISTRATION.md G5): EXCLUDED if K4 has no setting at >= 22 (so all three are excluded); otherwise
  LEAD if no shuffle has one, else CHANCE. Reported: K4's maximum against every shuffle's maximum.
Usage: exact90.py TARGET.tsv OUT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import witness90 as W  # noqa: E402  (standard-library definitions)


def settings():
    pairs = lambda b: [(u, v) for u in range(1, b) for v in range(1, b) if u != v]  # noqa: E731
    outers = [None] + [(k, sg, ph) for k in W.OUTER_KEYS for sg in (1, -1) for ph in range(len(W.OUTER_KEYS[k]))]
    return [(a, b, u, v, o) for o in outers for a in W.WORDS for b in (5, 7, 9, 11) for (u, v) in pairs(b)]


def hits(ct, pos, letters, sts):
    n, inner, out = len(ct), {}, []
    for a, b, u, v, o in sts:
        if o not in inner:
            U = None if o is None else W.OUTER_KEYS[o[0]]
            inner[o] = ct if o is None else "".join(
                W.KRY[(W.KRY.index(ch) - o[1] * W.KRY.index(U[(i + o[2]) % len(U)])) % 26] for i, ch in enumerate(ct))
        m, A, h = inner[o], W.ALPH[a], 0
        for k, want in zip(pos, letters):
            off = (k // b) * b
            t = min(b, n - off)
            j = k - off
            h += A[13 * (A.index(m[off + (j - u) % t]) // 13) + A.index(m[off + (j - v) % t]) % 13] == want
        out.append(h)
    return out


def main():
    tsv, out = Path(sys.argv[1]), Path(sys.argv[2])
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # the published letters; this step runs only after the blind evaluation
    pos = [o + i for o, t in CLUES for i in range(len(t))]
    letters = [c for _, t in CLUES for c in t]
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    ids = ["K4"] + sorted(i for i in cts if i != "K4")
    sts = settings()
    per = {}
    for rid in ids:
        h = hits(cts[rid], pos, letters, sts)
        mx = max(h)
        per[rid] = {"max_hits": mx, "n_24": h.count(24), "n_ge_23": sum(x >= 23 for x in h),
                    "n_ge_22": sum(x >= 22 for x in h), "best_settings": [sts[k] for k, x in enumerate(h) if x == mx][:10]}
    k4, nulls = per["K4"], [per[i] for i in ids[1:]]

    def verdict(key):
        if k4[key] == 0:
            return "EXCLUDED"
        return "LEAD" if all(r[key] == 0 for r in nulls) else "CHANCE"

    rep = {"settings": len(sts), "positions": len(pos), "k4": k4,
           "verdict_exact": verdict("n_24"), "verdict_drop_pt": verdict("n_ge_23"), "verdict_drop_ct": verdict("n_ge_22"),
           "shuffle_max_hits": sorted((r["max_hits"] for r in nulls), reverse=True),
           "p_max_hits": (1 + sum(r["max_hits"] >= k4["max_hits"] for r in nulls)) / (1 + len(nulls)),
           "shuffles": {i: {k: per[i][k] for k in ("max_hits", "n_ge_22")} for i in ids[1:]}}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print("EXACT", rep["verdict_exact"], "| DROP-PT", rep["verdict_drop_pt"], "| DROP-CT", rep["verdict_drop_ct"],
          "| K4 max", k4["max_hits"], "| shuffles max", rep["shuffle_max_hits"][0], "| p_max_hits %.3f" % rep["p_max_hits"])


if __name__ == "__main__":
    main()
