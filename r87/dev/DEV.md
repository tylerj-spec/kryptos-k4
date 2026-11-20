# R87 development record (spent books only; NOT gate evidence)

**Texts.** Every development run used only spent text:
- Tom Sawyer (`r59` dev_pt) for plaintext;
- Dorian Gray (dev_key) for running keys.

No fresh book, no K4 ciphertext and no published letter was used.

## Design pilot (`pilot85.py`, `PILOT.json`; cited by `r85/DESIGN.md` §4)
- **Exact check on random data:** random ciphertexts with random letters at K4's 24 positions pass **0 of 153,600**
  setting trials.
- **True settings on English-frequency plants** have a median of 10 checks (range 4–14).

## Development history
1. **First solver** (pass 1: 2 restarts × 6,000 iterations at T0 2.0, top 24; pass 2: 8 × 30,000), development set
   seed 850300 (R85 naming).
   - Positives: **20/24**.
   - Three misses were scorer limits. In H_027 (n 3) the true setting was dropped in pass 1.
2. **Larger pass 1** (3 × 10,000, top 32) **and a letter-model polish of the best 5** (pass 3). Same set: 24/24.
3. **The round renamed R87** (ChatGPT's PR #95 uses r85/ and r86/). The seed now enters every annealing seed. Fresh
   development set, seed 870300, with the one-ciphertext-letter-wrong kind added.
   - Positives: **20/24** (S4 4/6).
   - Diagnosis at the true settings (scratch script `diag87.py`): **all five misses were search failures**.
     - In 3 the true setting ranked 63, 94 and 617 in pass 1. In 2, pass 2 at the true setting failed.
     - A long anneal (24 × 60,000) at the true setting reached 90–97/97 in every case.
4. **Schedule measured** (per-restart success at the true setting, 24 positives × 20 restarts each; success = within 3
   log-points of the true text's quadgram score):

   | Iterations / T0 | 10k/1 | 10k/2 | 10k/4 | 10k/6 | 20k/2 | **20k/4** | 20k/6 | 40k/2 | 40k/6 |
   |---|---|---|---|---|---|---|---|---|---|
   | successes of 480 | 56 | 116 | 232 | 202 | 184 | **334** | 321 | 241 | 386 |

   T0 = 4 is about optimal. Final parameters (`solve87.PARAMS`):
   - pass 1: 3 × 20,000 at T0 4.0, keep the top **48**;
   - pass 2: 12 × 40,000, and a better pass-1 wiring is never discarded.
5. **Final code on both development sets** (`DEV1_SUMMARY.json`, `DEV2_SUMMARY.json`):

| Set (seed) | Positives recovered and confident | S1 / S2 / S3 / S4 | CTERR | Negatives confident | Negatives max lm / word | Recovered min lm / word |
|---|---|---|---|---|---|---|
| 1 (870300) | 22/24 (22 exact) | 6/6 / 6/6 / 5/6 / 5/6 | 8/8 | 0/27 | −1.392 / −1.954 | −0.977 / −1.630 |
| 2 (870301) | 22/24 (21 exact) | 6/6 / 6/6 / 5/6 / 5/6 | 8/8 | 0/27 | −1.349 / −1.973 | −1.075 / −2.054 |

- The four misses are **confident decodes at 91, 93, 94 and 88 of 97 letters**. At the true setting the scorer
  prefers them to the true text, so they are scorer limits.
- The cuts (−1.30 / −2.50) were not changed.

## Files
| File | sha256 |
|---|---|
| Development set 1 input | b36f652f2c80523ae3466cea450cb7dde6b3a13c7305d2966c447ffecf78c2fa |
| Development set 1 results | 9e3e6843f84271f2b21d62e2c9c5e05e0f189d6cc08952b83050ae87d7593bc9 |
| Development set 2 input | 14b7e8a839eee016dbd292c5098e46888ee91dcf341c6a7d86b2262d53259e53 |
| Development set 2 results | 6b6cdb022aa9691097ad6e4c72144dca600c70cb7482fd8235666d2965990a98 |

The development sets regenerate byte for byte from `make87.py` with the seeds above.

**Cost:** 59 items in 329 s on 4 cores.
