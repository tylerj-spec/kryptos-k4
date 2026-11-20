# R88 development record (spent books only; NOT gate evidence)

**Texts.** Tom Sawyer (`r59` dev_pt) for plaintext and Dorian Gray (dev_key) for running keys. No fresh book, no K4
ciphertext and no published letter was used.

**Parameters.** R87's solver parameters (`r87/dev/DEV.md`), unchanged: pass 1 at 3 × 20,000 iterations and T0 4,
the top 48 settings, pass 2 at 12 × 40,000. **Nothing was tuned for R88.**

## Final code on two development sets (`DEV1_SUMMARY.json`, `DEV2_SUMMARY.json`)
| Set (seed) | Positives recovered and confident | S1 / S2 / S3 / S4 | Exact | CTERR | Negatives confident | Negatives max lm / word | Recovered min lm / word |
|---|---|---|---|---|---|---|---|
| 1 (880300) | 21/24 | 5/6 / 6/6 / 5/6 / 5/6 | 16 | 7/8 | 0/30 | −1.392 / −2.046 | −0.961 / −1.510 |
| 2 (880301) | 22/24 | 6/6 / 6/6 / 5/6 / 5/6 | 19 | 7/8 | 0/30 | −1.382 / −1.928 | −0.958 / −1.417 |

## Misses
**Confident partial decodes:** 93, 93, 94, 94 and 71 of 97 letters.

**Not confident:** two items at 13 of 97 letters.

**Diagnosis at the true setting** (scratch script `diag88.py`; spent truth only). All three hard cases are scorer
limits, not search failures:

| Item | True setting's pass-1 rank | Long anneal (24 × 60,000) at the true setting | Truth's quadgram score |
|---|---|---|---|
| H_040 (set 1) | 1 | wrong text, 10/97, quad −438.7 | −465.5 |
| H_053 (set 1) | 1 | 67/97, quad −432.9 | −436.1 |
| H_039 (set 2) | 2 | 43/97, quad −448.8 | −451.8 |

In each case the quadgram scorer prefers a wrong text to the true one. With a free alphabet on one side, the PA side
in particular is a monoalphabetic substitution in the rotor frame, so on unusual plaintext it has more room to fit
English-looking text. **Partial recoveries are therefore more common than in R87** (35 exact of 43 recovered here,
against 43 of 44 in R87).

## Files
| File | sha256 |
|---|---|
| Development set 1 input | 8df2429b4b78679e9a5a9c6bdad242490ae5c10b2ee71a9add40fb13d336d70d |
| Development set 1 results | 4c448ab69da3e099348829b34082744ae800ce99ed91f2639ec8f719a322f30e |
| Development set 2 input | 04fad0a66abffbbfea0e4335359ad27386295bb915e4248875c300e79be792d2 |
| Development set 2 results | 3f2feb238c5cd006e87dcfd29e91bb804ccd0c66c758ab117d557fc4055210c9 |

**Cost:** 62 items in 287 s and 253 s on 4 cores.
