# R99 development records (DEVELOPMENT_ONLY; no K4 file or published letter was read)

**Development gate.** `DEV_GATE_seed4343.json` and its log ran the gate code with development seed 4343, not the
gate seed 990901.
- Every check passed (DEVELOPMENT_ONLY_GO).
- 68 s CPU; aggregate peak 102 MB.

**Synthetic rehearsal of the target.** `smoke_target99.py` built a throwaway tree:
- the "ciphertext" is a plaintext-autokey encryption on a random tier alphabet (L 40, signs (+1, −1), c 17);
- the "clues" are that random text's letters at positions 21–33 and 63–73;
- the source constants were re-pointed at those synthetic files.

It then ran `run_target99.py` and `evaluate99.py` there (`SMOKE_TARGET_EVAL.json`, `SMOKE_TARGET_LOG.json`).
- **Planted lag:** EXACT 1 and DROP 2; every shuffle had 0 at that lag.
- **Decision:** LEAD, on the DROP total over the DROP-decided lags (2 against a shuffle maximum of 0).
- **EXACT total over the EXACT-decided lags:** 1; 9/200 shuffles had at least 1 there (maximum 2). That is the
  chance rate at 6–7 links, as `PREREGISTRATION.md` §2 expects.
- **Run:** 244 s wall, 242 s CPU, peak 151 MB, inside the target's 1,800 / 1,200 s caps.
