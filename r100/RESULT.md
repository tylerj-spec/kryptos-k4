# R100 result (Claude Code, 24 Nov 2026): Quagmire-type plaintext autokey with two tier alphabets is EXCLUDED at the 12 decidable lags

## In plain words
**A two-alphabet plaintext autokey on a Quagmire tableau is ruled out for K4 at every lag where the published
letters give at least 10 direct checks.**
- **The cipher:** R99 tested K1/K2's tableau with a self-keying key when one alphabet does every job. This round
  separates the jobs:
  - the plaintext is read in one keyword alphabet and the ciphertext written in another, as in the Quagmire I, II and
    IV tableaux;
  - the key letter, which is the plaintext letter L places earlier, is numbered in the plaintext alphabet, in the
    ciphertext alphabet, or in plain A–Z.
- **What varies:**
  - both alphabets: any of the 77,229 tier alphabets each;
  - the directions: all four sign pairs;
  - any constant offset;
  - any starting key.

**Result.**
- No setting fits the published letters at lags 1–7 or 39–43.
- Allowing one wrong letter, or one wrong ciphertext letter at a published position, still none fits at lags 1–5.
- Other lags have too few direct checks for two free alphabets and were not scanned; they stay open.

## Gate (`holdout/CHECKER_GATE.json`, seed 1000901): **GO**
| Check | Result |
|---|---|
| V1 reference round trip | 400/400 |
| V2 brute-force oracle (reference encryptor, every c) | 16 inputs × 256 (A, B) pairs × 12 sign/feedback cases: **0** mismatches for the fast path, **0** for the simple path; all 16 inputs have EXACT > 0 |
| V2b simple-path agreement | 8 inputs × 300-alphabet sub-tier (90,000 pairs) at registered lag sizes: 0 disagreements |
| V3 full-tier plants | 32/32 in EXACT; for the 16 at DROP lags, 16/16 with a wrong published letter and 16/16 with a wrong ciphertext letter |
| V4 Quagmire I, II, III, IV autokeys (F = B) | 16/16 found |
| V5 throughput | planted full scan found; forecast 537 s CPU (limit 960) |

**Run:** COMPLETE, 104 s wall, 104 s CPU, peak 147 MB (cap 300 / 240 / 1,024). Gate freeze 2b24690 was pushed
before any K4 input was read.

## Target (`k4/AGGREGATES.json`, frozen in 44efbc0): **EXCLUDED**
Each lag has 7.157 × 10¹⁰ settings: 77,229² alphabet pairs × 4 sign pairs × 3 feedback conventions.

| Lags | Direct links | K4 EXACT | K4 DROP | 100 shuffles |
|---|---|---|---|---|
| 1–5 | 22, 20, 18, 16, 14 | **0** | **0** | all 0 / 0 |
| 6, 7 | 12, 10 | **0** | not computed | EXACT 0, except one shuffle with 1 at lag 7 |
| 39–43 | 10, 11, 11, 11, 10 | **0** | not computed | all 0 |

**Decision** (`k4/EVALUATION.json`): **EXCLUDED**. K4 has EXACT 0 over all 12 scanned lags and DROP 0 over lags 1–5.

**Run:** COMPLETE, 279 s wall, 277 s CPU, peak 157 MB (cap 1,800 / 1,200 / 1,024), zero retries. The freeze was
pushed, and the remote blobs were checked before evaluation.

## Post-freeze cross-check (`k4/CROSSCHECK.json`)
`crosscheck100.py` recomputes K4's counts from the frozen inputs with a second algorithm:
- one integer-key join over **all** direct links;
- for DROP, a separate join for every published-position cut;
- no two-group candidates and no float codes.

It agrees on every lag (94 s, 87 MB).

**Positive control** (`dev/CROSSCHECK_CONTROL.json`, synthetic). On two full-tier plants at 14-link lags, one with a
corrupted published letter, it matches the fast path in all 24 sign/feedback cases and finds both plants. The plant
with the corrupted letter is found by DROP.

## Agreement with earlier rows
- **L188 (R99):** its A = B, F = A cases are a subset, and they give 0 here as well.
- **L172 (R83a PFX):** its named-alphabet cases give 0 here as well.
- **L27 / L58:** R100 decides the tier sub-case of their AZ/KRYPTOS-rank families exactly, by necessary conditions.

## What this excludes, and what it does not
**Excluded exactly** (crib-assisted: the published letters in place and in the carved order):
- **Cipher:** B⁻¹(C_i) = s1·A⁻¹(P_i) + s2·F⁻¹(P_{i−L}) + c, any c and any primer, for any two tier alphabets A and B,
  any F ∈ {A, B, AZ} and any sign pair.
- **Lags without errors:** 1–7 and 39–43.
- **Lags with one error allowed:** 1–5. The error can be one wrong published letter, or one wrong ciphertext letter at
  a published position.

**Not excluded:**
- lags with fewer than 10 direct links (8–38 and 44–96 for this family);
- the extra information in chains through unpublished positions (not used);
- alphabets outside the tier;
- a keyword combined with the autokey;
- ciphertext autokey;
- a transposition layer;
- insertion or deletion;
- two errors.

**Alias note (from the controls).** Near a true plant, related tier alphabets also fit; 5–9 extra EXACT settings
appeared at a 14-link lag. So a non-zero count at a decided lag would mark a family of related settings, not one
key. K4 has none.

## Review
**Independent review: NONE.** One model (Claude Code) registered, built and ran R100. ChatGPT is the named reviewer.
