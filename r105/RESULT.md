# R105 result (Claude Code, 26 Nov 2026): GO. With the cipher alphabet supplied, the two-free-alphabet autokey is solved from 97 letters

**Type:** C development (solver), synthetic only. No K4 input. **Independent review: NONE**; this is audit batch B.
**R106 may not start until ChatGPT has verified this GO independently.**

## In plain words
**The setting.** The cipher is a plaintext autokey with two secret mixed alphabets: the plaintext alphabet A and the
cipher alphabet B. This round assumes B is known, along with the lag and the signs, and that the key letters are
numbered in A (F = A). The solver must find A, a constant and the starting letters.

**The solver.** R104 showed this case is a simple substitution of a sequence we can compute, once a constant and one
offset per autokey chain are known. R105's solver S105 works in four stages:
1. It tries **every** (constant, offsets) setting, ranking them with an exact letter-frequency statistic.
2. It re-ranks the best 4,000 with repeated-bigram and repeated-trigram counts.
3. It runs a quick substitution solve on the best 200.
4. It runs a full solve on the best 10.

**The test.** It was applied to 50 fresh synthetic messages at lags 1–5, and to 30 decoys. The decoys were:
- random letters;
- the right message with a wrong B;
- the right message with a wrong lag.

**The result.**
- **42 of 50 messages recovered** (≥ 90 of 97 letters right), and at least 7 of 10 at every lag. 45 of 50 had at
  least 80 letters right.
- Every recovery scored far above every decoy: recoveries −424 or better, decoys −459 or worse.

**The caveat.** A high score shows that the hypothesis (B, lag, signs) is right. It does not show that every letter
is. 7 of the 8 failures also scored above every decoy. In 5 of them, the scorer preferred a wrong plaintext over the
true one: 47–88 letters right, with the true text scoring lower.

**When σ is unknown.** Solving both σ cells and keeping the higher score picked the right cell in **10 of 10** cases.

## Verdict: **GO** (pre-registered bars met)
| Bar | Required | Result |
|---|---|---|
| Gates G1a, G1b, G2, G3 | all pass | **all pass** |
| M1 recovered (≥ 90/97 letters) | ≥ 35/50, ≥ 5/10 per lag | **42/50**; lags 1–5: 9, 8, 9, 9, 7 |
| Recoveries above the null maximum M | ≥ 90% | **42/42 (100%)** |

## Results (`run_v1/RESULTS.json`, frozen in f4b8b88)
| Step | Result |
|---|---|
| **G1a gauge** | 100 plants, L 1–8, all four sign pairs: 0 failures. The true key in the gauge (o_0 = 0; c′ = c + 2·s1·o_0 when σ = −1) reproduces A⁻¹(P) − o_0 exactly |
| **G1b reflection** | 100 plants: 0 failures. (s1, s2, A) and (−s1, −s2, reflected A) give the same ciphertext at every position ≥ L |
| **G2 stage-1 reference** | 1,020 grid points (20 plants): the table value equals Σ n_v² counted directly, with 0 mismatches |
| **G3 re-encryption** | All **100** solver outputs (M1, M2, E1) re-encrypt exactly to their input at positions L…96 under `r100/autokey100.py` |
| **M1 plants** | **42/50** at ≥ 90 letters; 45/50 at ≥ 80 |
| **M2 nulls** (best score per kind) | random ciphertext −468.8; wrong B −458.9; wrong L −465.4. **M = −458.88**. Recoveries scored −423.6 to −352.3 |
| E1 σ unknown | 10 plants × 2 cells: the higher-scoring σ was the true σ in **10/10**; that output was recovered in 8/10 (81 and 46 letters in the other two) |

**Letters right per plant** (5 plants per cell):

| Lag | σ = +1 | σ = −1 |
|---|---|---|
| 1 | 97, 91, 93, 96, 96 | 47, 92, 97, 97, 96 |
| 2 | 97, 97, 86, 96, 88 | 96, 97, 93, 92, 97 |
| 3 | 97, 97, 80, 95, 94 | 94, 95, 97, 96, 97 |
| 4 | 95, 97, 96, 96, 95 | 94, 10, 92, 96, 97 |
| 5 | 97, 40, 95, 79, 93 | 97, 5, 97, 92, 97 |

**Where the 8 failures were lost:**

| Cause | Count | Plants (letters right) |
|---|---|---|
| Scorer counterexample: the truth was selected, but the true plaintext scores below the output | 5 | 47, 86, 88, 80, 79 |
| Annealer gap: the truth was selected, and the true plaintext scores above the output | 1 | 40 |
| Lost at stage 3: the truth was 29th after the quick solve (cut at 10) | 1 | 10 |
| Lost at stage 1: the truth was not in the top 4,000 of the exact grid (L 5, σ = −1) | 1 | 5 |

In all 42 recoveries the solver selected the true (c′, offsets). The truth ranked at most 289th at stage 1, 28th at
stage 2 and 5th at stage 3.

**Run:** COMPLETE through `audit/run_bounded_agg.py`: 720 s wall, 715 s CPU, peak 458 MB (cap 1,800 / 1,800 /
2,048), zero retries. The E1 time guard was not reached.

**Commits:**
- pre-registration 4576cb0, pushed alone;
- source 310c4de, pushed before the run;
- outputs frozen in f4b8b88.

## What this establishes, and what it does not
**Established (synthetic, within the stated model):** a fixed solver recovers the plaintext autokey with two free
alphabets, given B, the lag (1–5), the signs, F = A and 97 letters, at 84% (42/50). Its score separates right
hypotheses from wrong-B, wrong-lag and random-text decoys with a wide margin.

**Not established:**
- **No K4 claim.** Nothing touched K4.
- **B unknown (R106):** not attempted here, and still conditional on independent verification of this GO.
- **Other modes:**
  - F = B or F = AZ: not covered.
  - A known: closed by R104.
  - Lags above 5: untested.
  - Other plaintext languages or styles: untested.
- **Correctness from the score alone.** It is not available: scorer counterexamples reach decoy-beating scores with
  only 47–88 letters right. Under a right hypothesis a high score means "nearly or fully solved", and finishing still
  needs a reader or a word model.

**What a K4 use would need:** a separately registered round with its own gate and Tyler's approval. For example, the
cipher alphabet B could be taken from a short list registered in advance (KRYPTOS-keyed, straight), with the lags
and both σ cells scanned.

Nothing from R105 enters a blind search.
