# R110 pre-registration (Claude Code, 27 Nov 2026): ciphertext-only lag-pair repetition test on K4

**Mode: BLIND.** The only K4 input is the 97-letter ciphertext (hash-checked). No published letter, position or mask
is read at any stage.

**Approval:** Tyler, 27 Nov 2026: "Do the 4 proposals then we'll do the audit". This is proposal P2 of
`audit/ROLLING_QUEUE.md`.

**Independent review: NONE** (one model). R110 belongs to audit batch C.

## 1. The statistic and the prediction
**The statistic.** For a text C of 97 letters and a lag L:

    R_L(C) = Σ over distinct pairs (x, y) of n(n − 1)/2,   n = #{i : C_i = x, C_{i+L} = y}

**The prediction (R102, L191).** In the two-free-alphabet plaintext autokey with lag L, a ciphertext lag pair
(C_i, C_{i+L}) is a fixed function of the plaintext triple (P_{i−L}, P_i, P_{i+L}). Repeated plaintext triples
therefore repeat ciphertext lag pairs, and R_L exceeds the value expected from the letter frequencies alone.
- **R102 C6 (synthetic):** power 0.41 at L = 1, 0.11 at L = 2 and 0.09 at L = 3, against shuffles at the 5% level.

**What this test is.** It is a **weak, non-specific** test. Any cipher that preserves plaintext repetition at lag L
also raises R_L.
- A significant result means only "lag-L repetition above the letter-frequency level".
- A null result does not exclude the autokey: power is 0.41 at best.

## 2. Sealed synthetic gate (`r110/gate110.py`; reads no K4 file)
**Seed:** 1100901. The plaintexts are Carter OCR windows that contain no published K4 word.

| Check | What | Pass |
|---|---|---|
| G1 two implementations | R_L by a Counter of pairs, and by sorting the pair codes, on 500 random strings × L 1–24 | 0 disagreements |
| G2 power | 300 fresh plants, as R102 C6: two free alphabets, F ∈ {A, B, AZ}, random signs, c and primer, L = 1. One-sided p against 1,000 letter-shuffles of the same ciphertext | share with p < 0.05 **≥ 0.25** |
| G3 size | 300 uniform random 97-letter strings, with the same p-value computation | share with p < 0.05 **≤ 0.08** |

**GO** if G1–G3 all pass. Otherwise **NO-GO**: K4 is not run.

**Budget:** `audit/run_bounded_agg.py`, 600 s / 600 s / 1,024 MiB.

## 3. Target (`r110/run_target110.py`; only after the gate's GO and its freeze are pushed)
**The computation:**
- R_L(K4) for every L in 1–24;
- **100,000** letter-shuffles of K4 (seed 1100400), with R_L computed for each;
- one-sided p_L = (1 + #{shuffles with R_L ≥ R_L(K4)}) / 100,001.

**Primary test (registered): L = 1 at α = 0.05.**
- **SIGNAL_L1** if p_1 < 0.05;
- **NO_SIGNAL** otherwise.

**Exploratory:** L = 2–24, reported with the Bonferroni-adjusted minimum, min p_L × 24.

**Budget:** 1,800 s / 1,800 s / 1,024 MiB, zero retries.

**What follows from each result:**
- **SIGNAL_L1** is not a K4 claim. It would be reported, and would raise the priority of lag-1 autokey work.
- **NO_SIGNAL** is STAT_NO_SIGNAL and excludes nothing.

## 4. Order
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`, pushed alone.
2. Source and `SOURCE.sha256`.
3. The gate, then `holdout/GATE_FROZEN.sha256` and the manifest's GO, pushed.
4. The target, then `k4/FROZEN.sha256`, pushed.
5. The evaluation and the result note.
