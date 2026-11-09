#!/usr/bin/env python3
"""R73b SEALED K4 reveal (run ONLY after the K4 + nulls results are frozen, pushed and verified). R26 only.
The published letters come from r73/sealed/reveal_k4.py (0-based plaintext positions 21-33 and 63-73; R26 enciphers
in place, so the decoded letters are in carved order). Rules fixed in r73/R73B_PREREGISTRATION.md:
  CONFIDENT     K4's best R26 score >= CUT per letter AND above every null's best;
  SIGNAL        CONFIDENT and the decode matches >= 10/24; SCORE_ANOMALY: CONFIDENT without it; else NO_SIGNAL.
  Contenders    any of K4's 52 R26 decodes matching >= 12/24, with the nulls' maximum.
  R26X          (crib-assisted, post-freeze; not part of the blind outcome) for each tableau alphabet, whether ANY
                phase, word numbering and word division (words of 1-18 letters, unknown plaintext between the two
                published blocks) makes R26 encipher the 24 published letters to K4's letters; the consistent word
                divisions inside each block are listed, and the same check is reported for the 100 nulls.
Usage: reveal_k4_r73b.py TARGET.tsv RUN_DIR REPORT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r73"))
sys.path.insert(0, str(ROOT / "r73" / "sealed"))
import wordkey as W  # noqa: E402
from reveal_k4 import CLUES, hits, sha  # noqa: E402

CUT = -1.4
MAXLEN = W.MAXLEN


def block_divisions(ct, alph, off, text):
    """All word divisions of one published block consistent with R26: y = x + s + t, s = word phase (+1 per word),
    t = position in word (0..17). The block's first word may start up to 17 letters before it (t0 <= off) and its last
    word may continue after it. Returns the list of divisions (block text with spaces at word starts)."""
    A = W.ALPH[alph]
    d = [(A.index(ct[off + i]) - A.index(text[i])) % 26 for i in range(len(text))]
    out = []

    def go(i, t, cuts):
        if i == len(text) - 1:
            out.append(cuts)
            return
        if t + 1 < MAXLEN and d[i + 1] == (d[i] + 1) % 26:
            go(i + 1, t + 1, cuts)
        if d[i + 1] == (d[i] - t + 1) % 26:
            go(i + 1, 0, cuts + [i + 1])

    for t0 in range(min(MAXLEN - 1, off) + 1):
        go(0, t0, [0] if t0 == 0 else [])
    seen, res = set(), []
    for cuts in out:
        s = "".join((" " if (i in cuts and i > 0) else "") + c for i, c in enumerate(text))
        s = ("|" if 0 in cuts else "…") + s
        if s not in seen:
            seen.add(s)
            res.append(s)
    return res


def joint_feasible(ct, alph):
    """Whether one R26 path (phase s, position t) runs from position 21 to 73 matching every published letter, with
    free plaintext at positions 34-62."""
    A = W.ALPH[alph]
    fixed = {o + i: (A.index(ct[o + i]) - A.index(c)) % 26 for o, t in CLUES for i, c in enumerate(t)}
    lo, hi = CLUES[0][0], CLUES[-1][0] + len(CLUES[-1][1]) - 1
    states = {(s, t) for s in range(26) for t in range(min(MAXLEN - 1, lo) + 1) if (s + t) % 26 == fixed[lo]}
    for i in range(lo + 1, hi + 1):
        nxt = set()
        for s, t in states:
            for s2, t2 in ((s, t + 1), ((s + 1) % 26, 0)):
                if t2 < MAXLEN and (i not in fixed or (s2 + t2) % 26 == fixed[i]):
                    nxt.add((s2, t2))
        states = nxt
        if not states:
            return False
    return True


def r26x(ct):
    return {a: {"feasible": joint_feasible(ct, a),
                "blocks": {t: block_divisions(ct, a, o, t) for o, t in CLUES}} for a in W.ALPH}


def main():
    tsv, run, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    for line in (run / "FROZEN.sha256").read_text().splitlines():
        h, lab, _ = line.split("  ")
        if lab in ("input", "results"):
            assert sha(tsv if lab == "input" else run / "RESULTS.jsonl") == h, f"freeze mismatch {lab}"
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    fam = {}
    for rid in cts:
        w = json.loads((run / "work" / f"{rid}.json").read_text())
        fam[rid] = sorted([s for s in w["settings"] if s["family"] == "R26"], key=lambda s: -s["score"])
        assert len(fam[rid]) == 52
    nulls = [i for i in cts if i != "K4"]
    k4 = fam["K4"][0]
    k4_pl = k4["score"] / 97
    null_best = sorted(fam[i][0]["score"] / 97 for i in nulls)
    confident = k4_pl >= CUT and k4_pl > null_best[-1]
    h = hits("".join(k4["words"]))
    outcome = ("SIGNAL" if h >= 10 else "SCORE_ANOMALY") if confident else "NO_SIGNAL"
    k4max = max(hits("".join(s["words"])) for s in fam["K4"])
    null_max = sorted(max(hits("".join(s["words"])) for s in fam[i]) for i in nulls)
    contenders = [s for s in fam["K4"] if hits("".join(s["words"])) >= 12]
    x_k4 = r26x(cts["K4"])
    x_nulls = {i: r26x(cts[i]) for i in nulls}
    out = {"outcome": outcome, "cut_per_letter": CUT, "k4_best": k4, "k4_best_per_letter": k4_pl, "k4_best_hits": h,
           "nulls_best_per_letter_sorted": null_best, "nulls_at_or_above": sum(v >= k4_pl for v in null_best),
           "contender_screen": {"k4_max_hits_52_settings": k4max, "null_max_hits_sorted": null_max,
                                "contenders_ge_12": contenders},
           "r26x_crib_assisted": {"k4": x_k4,
                                  "nulls_feasible": {a: sum(x_nulls[i][a]["feasible"] for i in nulls) for a in W.ALPH},
                                  "n_nulls": len(nulls)}}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(outcome, "| K4 best R26 %.3f/letter (cut %.2f)" % (k4_pl, CUT), k4["setting"], "| nulls >= K4:",
          out["nulls_at_or_above"], "of", len(nulls), "| null best max %.3f" % null_best[-1], "| hits", h)
    print("raw decode:", " ".join(k4["words"]))
    print("contender screen: K4 max hits over 52 settings", k4max, "| nulls median/max", null_max[len(null_max) // 2],
          null_max[-1], "| contenders >= 12:", len(contenders))
    for a in W.ALPH:
        print(f"R26X (crib-assisted) {a}: K4 feasible {x_k4[a]['feasible']}; block divisions",
              {t: len(v) for t, v in x_k4[a]["blocks"].items()}, "| nulls feasible",
              out["r26x_crib_assisted"]["nulls_feasible"][a], "of", len(nulls))


if __name__ == "__main__":
    main()
