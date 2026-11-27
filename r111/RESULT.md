# R111 result (Claude Code, 27 Nov 2026): NO_SIGNAL. R105's solver finds no English plaintext in K4 under the two-free-alphabet autokey with B = AZ or KRYPTOS, lags 1–5

**Type:** BLIND. The solver's only input was the K4 ciphertext. The clue check ran only after the freeze and the
evaluation were pushed. **Independent review: NONE**; this is audit batch C.

**Provisional:** R111 relies on R105's solver GO (L194), which is still unaudited (batch B). It ran ahead of that
audit on Tyler's instruction of 27 Nov 2026.

## In plain words
**The setting.** R105 built a solver that recovers a plaintext autokey with a secret plaintext alphabet, once the
cipher alphabet is supplied. It recovered 42 of 50 synthetic messages. R111 ran it blind on K4, with the cipher
alphabet set to:
- the straight alphabet; or
- the KRYPTOS alphabet of K1–K3.

It tried every lag from 1 to 5 and both sign classes: 20 settings in all.

**Gate.** Before K4 was touched, the same 20-setting search was run on 8 synthetic messages. It found the right
setting and the plaintext for 7 of them. Every recovery scored −420 or better, and every decoy −456 or worse.

**K4.**
- The best of the 20 settings scored **−459.3**. That is a decoy-level score.
- **9 of the 15 shuffled copies of K4 scored higher.** The best shuffle reached −451.3.
- The registered bar for a candidate was −440, and the score had to beat every shuffle.
- **NO_SIGNAL.**

**Clue check after the freeze.** The best K4 output matched **1** of the 24 published letters. The best match in any
setting was 5, against about 1 expected by chance.

**What this means.** Within this family, K4 does not decrypt to English, as far as this solver can tell. The family is
not excluded: the solver misses about 1 message in 6. R109's exact check covers the same algebra with both alphabets
free.

## Gate (`holdout/GATE.json`, seeds 1110901 / 1110902): **GO**
| Plant (B, L, σ) | Top-cell T | Top cell right? | Letters right |
|---|---|---|---|
| AZ, 1, +1 | −381.2 | yes | 97 |
| KRY, 2, +1 | −391.7 | yes | 97 |
| AZ, 3, −1 | −375.4 | yes | 96 |
| KRY, 4, −1 | −373.1 | yes | 97 |
| AZ, 5, +1 | −378.8 | yes | 96 |
| KRY, 1, +1 | −382.0 | yes | 95 |
| AZ, 2, −1 | −420.2 | yes | 93 |
| KRY, 3, −1 | −447.2 | **no** | 0 |

**Decoys** (full 20-cell search): shuffles of plants 0–2 scored −456.9, −456.5 and −459.5; Quagmire III on KRY with
periods 7 and 8 scored −456.5 and −466.2.

**Checks passed:**
- recovered 7/8 (≥ 6 required);
- every recovery above every decoy;
- every output re-encrypts.

COMPLETE: 1,473 s. The gate freeze edb25f3 was pushed before K4 was read.

## Target (`k4/CANDIDATES.json`, `k4/NULLS.json`, frozen in 9a4d909)
| | Value |
|---|---|
| **T(K4)** (best cell: KRY, L 5, σ −1) | **−459.26** |
| Next best K4 cells | KRY L5 σ+1 −465.9; AZ L5 σ+1 −466.9; AZ L4 σ−1 −467.8 |
| Null T (15 shuffles) | −467.9 to **−451.3**; 9 of 15 at or above T(K4) |
| Every output re-encrypts | yes |
| **Decision** (`k4/EVALUATION.json`) | **NO_SIGNAL** |
| Clue check (`k4/CLUE_CHECK.json`) | top cell 1/24; best of any cell 5/24 (AZ L3 σ+1, score −471.4); chance about 0.9 per cell |

**Run:** COMPLETE through `audit/run_bounded_agg.py`: 1,816 s wall, 1,808 s CPU, 368 MB (cap 3,600 / 3,600 /
2,048), zero retries.

**Commits:**
- pre-registration 4ccce07;
- source 7842666;
- gate freeze edb25f3;
- target freeze 9a4d909;
- evaluation 2bf5e6c;
- clue check 11f17ad.

## Scope
**What NO_SIGNAL means.** At these 20 settings, S105 finds no English-scoring plaintext for K4. Its synthetic
recovery rate is 84–88%, so this is **not an exclusion**.

**Not covered:**
- other cipher alphabets;
- lags above 5;
- feedback in the cipher alphabet or the straight alphabet;
- any additional layer.

Nothing from R111 enters another blind search.
