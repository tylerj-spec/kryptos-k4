# R101 development records (DEVELOPMENT_ONLY; no K4 file or published letter was read)

**Development gate.** `DEV_GATE_seed4545.json` and its log ran the gate code with development seed 4545, not the
gate seed 1010901.
- Every check passed (DEVELOPMENT_ONLY_GO).
- 108 s CPU; peak 406 MB.
- V2 decided 50/60 and V3 28/32. These motivated Amendment 1's bars.

**V2 rate.** `V2_RATE.txt`: decided 46–53 of 60 over five more development seeds, with 0 misses.

**Synthetic rehearsal of the target.** `smoke_target101.py` built a throwaway tree:
- the "ciphertext" is a plaintext autokey on a uniformly random alphabet (L 2, signs (+1, −1));
- the "clues" are that random text's letters at positions 21–33 and 63–73.

It then ran `run_target101.py` and `evaluate101.py` (`SMOKE_TARGET_EVAL.json`, `SMOKE_TARGET_LOG.json`).
- **Planted cell:** (L 2, +1, −1) was FEASIBLE (22 links, mod-13 dimension 5), so the plant was found.
- **Decision:** CHANCE, not LEAD. One of the 20 shuffles also had one chance-feasible cell, which ties the totals at
  1 under the strict registered rule. This is the same conservative behaviour as R100's rule.
- **Chance:** 1 feasible cell of 400 shuffle cells, and 2 undecided.
- **Run:** 137 s wall, 135 s CPU, peak 407 MB, inside the target's 1,800 / 1,200 s caps.
