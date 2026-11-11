#!/usr/bin/env python3
"""R76 post-hoc follow-up (CRIB-ASSISTED, after the freeze; not pre-registered, reported as such): the one H1X setting
feasible for K4 (period 37, plaintext alphabet PLAITING/asc, ciphertext alphabet MANDATORIES/aca, additive), and for
comparison the same completion on the 11 settings feasible for shuffle NULL_003. Each setting's 21-29 unpinned key
letters are completed blind by coordinate ascent from RESTARTS random starting keys; the best letter-model score is
reported. A real solution would score near the holdout's -0.6 to -1.0 per letter.
Usage: h1_followup.py LM TARGET.tsv OUT.json"""
import importlib.util
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r76" / "sealed"))
import exact76 as X  # noqa: E402
import core  # noqa: E402

RESTARTS = 60
_s = importlib.util.spec_from_file_location("r73_reveal", ROOT / "r73/sealed/reveal_k4.py")
_m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_m)
CLUES = _m.CLUES


def best_completion(c, pos, pk, setting, tiers, scorer, rng):
    names, IDXT, LETT = tiers[setting["tier"]]
    pi, ci, s, m = names.index(setting["pa"]), names.index(setting["ca"]), setting["s"], setting["m"]
    slots = pos % m
    key = np.zeros(m, dtype=np.int64)
    for e in range(len(pos)):
        key[slots[e]] = (int(IDXT[ci][c[pos[e]]]) - s * int(IDXT[pi][pk[e]])) % 26
    free = [u for u in range(m) if u not in set(slots.tolist())]
    best = None
    for _ in range(RESTARTS):
        k0 = key.copy()
        for u in free:
            k0[u] = rng.randrange(26)
        P, k = X.complete_periodic(c, LETT[pi], IDXT[ci], s, m, k0, free, scorer)
        lm = float(scorer.lm_score(P[None, :])[0])
        if best is None or lm > best[0]:
            best = (lm, core.text(P))
    return {"setting": setting, "free_slots": len(free), "best_lm": best[0], "word": scorer.word_score(best[1]),
            "decode": best[1]}


def main():
    lm, tsv, out = sys.argv[1:4]
    known = {o + i: ch for o, t in CLUES for i, ch in enumerate(t)}
    rows = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    scorer = core.Scorer(lm)
    tiers, r2, r2b = X.load_all()
    pos = np.array(sorted(known))
    pk = np.array([ord(known[int(p)]) - 65 for p in pos], dtype=np.int16)
    rng = random.Random(760600)
    rep = {}
    for rid in ("K4", "NULL_003"):
        c = core.codes(rows[rid])
        r = X.run_all(rows[rid], known, None, tiers, r2, r2b, ("H1X",))["H1X"]
        settings = [f for f in r["feasible"] if f["shift"] == 0]
        rep[rid] = [best_completion(c, pos, pk, s, tiers, scorer, rng) for s in settings]
        for x in rep[rid]:
            print(rid, x["setting"]["m"], x["setting"]["pa"], x["setting"]["ca"], "free", x["free_slots"],
                  "best lm %.3f word %.2f" % (x["best_lm"], x["word"]), x["decode"], flush=True)
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")


if __name__ == "__main__":
    main()
