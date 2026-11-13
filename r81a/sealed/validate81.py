#!/usr/bin/env python3
"""R81a post-freeze validator (run ONLY after the K4 results are frozen, pushed, verified and revealed). It CHECKS frozen
blind work against the published letters and never fits anything to them: no key letter is completed from the
published letters, nothing is re-ranked. Labelled crib-assisted as in R70 Erratum 1.
For K4 and the first 10 shuffles, over every setting of the four R81a families and of R79's four keyword families:
  exact     the published letters pin each slot's shift; FEASIBLE when the pinned shifts agree within every slot
            (every setting has >= 12 such checks: at most 12 slots hold 24 letters);
  drop-one  (G6) FEASIBLE once one published letter is set aside: all disagreements involve that one letter.
For every setting flagged on K4, the report gives the frozen pass-1 blind score (OUT/scores/K4.npz) and replays that
same deterministic blind solver call (same seed and index, ciphertext only) to show the blind decode; the replayed
score must equal the frozen one.
Usage: validate81.py LM TARGET.tsv RUN_DIR REVEAL.json OUT.json"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r81a"))
sys.path.insert(0, str(ROOT / "r73" / "sealed"))
import core  # noqa: E402
import families as F79  # noqa: E402
import families81 as F  # noqa: E402
import solver as SV  # noqa: E402
from reveal_k4 import CLUES  # noqa: E402

POS = np.array([o + i for o, t in CLUES for i in range(len(t))])
WANT = np.array([ord(c) - 65 for _, t in CLUES for c in t])
PAIRS = [(a, b) for a in range(len(POS)) for b in range(a + 1, len(POS))]
SEED = 810001
CUT_LM, CUT_WORD = -1.30, -2.50
FAMSETS = [("R81a", F, F.FAMS), ("R79", F79, ("H7CT", "H7TXT", "LIB", "PROG"))]


def check_family(mod, fam, ct, want_list):
    inv = np.argsort(mod.bank()[0], axis=2).astype(np.uint8)
    n, exact, drop = 0, 0, np.zeros(len(POS), dtype=np.int64)
    flagged = []
    for Z, R, M, OI, info in mod.chunks(fam, ct):
        V = inv[OI[:, None], POS[None, :], WANT[None, :]].astype(np.int16)
        D = (V - Z[:, POS].astype(np.int16)) % 26
        RP = R[:, POS]
        C = np.zeros(len(Z), dtype=np.int16)
        Ca = np.zeros((len(Z), len(POS)), dtype=np.int16)
        for a, b in PAIRS:
            conf = (RP[:, a] == RP[:, b]) & (D[:, a] != D[:, b])
            C += conf
            Ca[:, a] += conf
            Ca[:, b] += conf
        ok0 = C == 0
        ok1 = (C > 0)[:, None] & (Ca == C[:, None])
        exact += int(ok0.sum())
        drop += ok1.sum(axis=0)
        if want_list:
            for j in np.flatnonzero(ok0 | ok1.any(axis=1)):
                flagged.append({"global_index": n + int(j), "chunk_info": info, "row": int(j),
                                "dropped": [int(POS[a]) for a in np.flatnonzero(ok1[j])] if not ok0[j] else [],
                                "z": Z[j], "r": R[j], "m": int(M[j]), "oi": int(OI[j])})
        n += len(Z)
    return n, exact, drop, flagged


def replay(mod, ct, fam, f, frozen, scorer):
    sc, de = SV.slot_batch(f["z"][None], f["r"][None], np.array([f["m"]]), np.array([f["oi"]]), mod.bank()[0], 1, SEED,
                           f["global_index"])
    st = mod.setting(f["chunk_info"], f["row"], de[0])
    t = mod.decrypt(ct, st)
    lm = float(scorer.lm_score(core.codes(t)[None])[0])
    return {"family": fam, "setting": st, "dropped_positions": f["dropped"], "frozen_pass1_quad": float(frozen),
            "replayed_quad": float(sc[0]), "replay_matches_frozen": abs(float(sc[0]) - float(frozen)) < 0.01,
            "blind_decode": t, "lm_per_letter": lm, "word_per_letter": scorer.word_score(t),
            "published_letters_matched": int(sum(t[p] == chr(65 + w) for p, w in zip(POS, WANT)))}


def main():
    lm, tsv, run, reveal, outp = sys.argv[1:6]
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    ids = ["K4"] + [i for i in cts if i != "K4"][:10]
    frozen = np.load(Path(run) / "scores" / "K4.npz")
    scorer = core.Scorer(lm)
    out = {"label": "CRIB-ASSISTED CHECK of frozen blind work (post-freeze; nothing fitted to the published letters)",
           "reveal_outcome": json.loads(Path(reveal).read_text())["outcome"], "rows": {}, "k4_flagged": []}
    for rid in ids:
        row = {}
        for tag, mod, fams in FAMSETS:
            for fam in fams:
                n, ex, drop, flagged = check_family(mod, fam, cts[rid], rid == "K4")
                row[f"{tag}:{fam}"] = {"settings": n, "exact_feasible": ex, "drop_one_feasible": int(drop.sum()),
                                       "drop_one_by_position": {int(POS[a]): int(drop[a]) for a in range(len(POS))
                                                                if drop[a]}}
                if rid == "K4":
                    key = f"K4__{fam}" if tag == "R81a" else f"K4__R79_{fam}"
                    assert len(frozen[key]) == n, (key, len(frozen[key]), n)
                    for f in flagged:
                        out["k4_flagged"].append(replay(mod, cts[rid], f"{tag}:{fam}", f, frozen[key][f["global_index"]],
                                                        scorer))
        out["rows"][rid] = row
        print(rid, {k: (v["exact_feasible"], v["drop_one_feasible"]) for k, v in row.items()}, flush=True)
    for e in out["k4_flagged"]:
        e["clears_cuts"] = e["lm_per_letter"] >= CUT_LM and e["word_per_letter"] >= CUT_WORD
    print("K4 flagged settings:", len(out["k4_flagged"]),
          [(e["family"], e["dropped_positions"], round(e["lm_per_letter"], 3), e["replay_matches_frozen"])
           for e in out["k4_flagged"]])
    Path(outp).write_text(json.dumps(out, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
                          + "\n")


if __name__ == "__main__":
    main()
