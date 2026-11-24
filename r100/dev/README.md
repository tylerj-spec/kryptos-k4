# R100 development records (DEVELOPMENT_ONLY; no K4 file or published letter was read)

**Development gate.** `DEV_GATE_seed4444.json` and its log ran the gate code with development seed 4444, not the
gate seed 1000901.
- Every check passed (DEVELOPMENT_ONLY_GO).
- 98 s CPU; aggregate peak 146 MB; forecast 658 s CPU against the 960 s limit.

**Synthetic rehearsal of the target.** `smoke_target100.py` built a throwaway tree:
- the "ciphertext" is a two-alphabet plaintext-autokey encryption: random tier alphabets A and B, F = B, L 41,
  signs (−1, +1);
- the "clues" are that random text's letters at positions 21–33 and 63–73;
- the source constants were re-pointed at those synthetic files.

It then ran `run_target100.py` and `evaluate100.py` (`SMOKE_TARGET_EVAL.json`, `SMOKE_TARGET_LOG.json`).
- **Planted lag:** EXACT 1, and every shuffle had 0 at that lag, so the pipeline found the plant.
- **Decision:** CHANCE, not LEAD. One shuffle had one chance EXACT setting at another lag, so K4's total (1) was not
  above every shuffle's (max 1).

  This is the registered rule working as written. The total-based LEAD rule is conservative: a single planted
  setting at an 11-link lag can tie with one chance hit elsewhere. Per-lag counts are reported alongside the
  decision.
- **Run:** 284 s wall, 282 s CPU, peak 207 MB, inside the target's 1,800 / 1,200 s caps.
