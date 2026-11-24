# R99 result (Claude Code, 24 Nov 2026): K1/K2's keyed tableau with a plaintext autokey is EXCLUDED at every decidable lag

## In plain words
**A plaintext autokey on K1/K2's keyed tableau is ruled out for K4 at every lag where the published letters can
decide it.**
- **The cipher:** K1 and K2 use a Vigenère tableau built on one keyword alphabet (KRYPTOS). This round asked whether
  K4 uses the same tableau with a self-keying key: each letter is keyed by the plaintext letter L places earlier.
  ACA Condi is this with L = 1.
- **What varies:**
  - the alphabet: any of the 77,229 keyword alphabets of R76's tier;
  - the direction: all four sign combinations (Vigenère, Variant, Beaufort and the reversed form);
  - any constant offset;
  - any starting key.

**Result.**
- No setting fits K4's 24 published letters at any lag from 1 to 23 or from 34 to 47.
- Allowing one wrong letter, or one wrong ciphertext letter anywhere on a decoding chain, still none fits at lags
  1–23 and 36–45.
- At the lags where the letters give only a few checks, there are feasible settings. They occur at the same rate as
  in shuffled copies of K4, so they are chance, not candidates.
- Lags 27–29 and 53–96 cannot be decided this way: no two published letters share a chain.

## Gate (`holdout/CHECKER_GATE.json`, seed 990901): **GO**
| Check | Result |
|---|---|
| V1 reference round trip | 400/400 |
| V2 brute-force oracle (reference decryptor, every c) | 30 inputs × every linked lag × 4 signs × 120 alphabets: **0** mismatches for the fast path, **0** for the simple path. All 30 inputs have EXACT > 0 |
| V3 full-tier plants | 32/32 counted in EXACT; 32/32 in DROP with one wrong published letter; 32/32 in DROP with one wrong ciphertext letter on a link |
| V4 ACA Condi (coded separately) | 16/16 found at L = 1, (+, +) |
| V5 throughput | simple path agrees at 3 lags; planted full scan found; forecast 485 s CPU (limit 960) |

**Run:** COMPLETE, 70.7 s wall, 70.1 s CPU, peak 163 MB (cap 300 / 240 / 1,024). Gate freeze f8082d0 was pushed
before any K4 input was read.

## Target (`k4/AGGREGATES.json`, frozen in 9b5f717): **EXCLUDED**
Each lag has 308,916 settings: 77,229 alphabets × 4 sign pairs.

| Lags | Links | K4 EXACT | K4 DROP | Shuffles |
|---|---|---|---|---|
| 1–15, 19–22 (DROP-decided) | 9–23 | **0** | **0** | all 0 / 0 |
| 16–18, 23 | 7–8 | **0** | **0** | EXACT all 0; DROP up to 2 |
| 35–47 (EXACT-decided) | 6–11 | **0** | 0 at 36–45; 9, 1, 9 at 35, 46, 47 | EXACT ≤ 2; DROP ≥ K4's in 17, 26 and 14 shuffles |
| 34 | 5 | **0** | 71 | EXACT ≤ 8 |
| 24–26, 30–33, 48–52 (weak) | 1–5 | 1 to 308,916 | — | K4 within the shuffle range at every lag |
| 27–29, 53–96 | 0 | — | — | no information (OPEN) |

**Family decision** (`k4/EVALUATION.json`): **EXCLUDED**.
- **K4:** EXACT 0 over the 36 EXACT-decided lags, and DROP 0 over the 26 DROP-decided lags.
- **Shuffles, EXACT-decided lags:** 10/200 have some EXACT setting there, with a maximum of 2. This matches the
  expected chance rate at 6–7 links.
- **Shuffles, DROP-decided lags:** none has a DROP setting.

**Run:** COMPLETE, 248 s wall, 246 s CPU, peak 100 MB (cap 1,800 / 1,200 / 1,024), zero retries. The freeze was
pushed, and the remote blobs were checked before evaluation.

## Post-freeze cross-check (`k4/CROSSCHECK.json`)
`crosscheck99.py` recomputes K4's per-lag counts from the frozen inputs with the second checker path, which brute
forces over c with step-by-step propagation and uses no masks or closed-form sums.
- It agrees on every lag.
- It ran through the wrapper: 108 s, 148 MB.

## Agreement with earlier rows
- **L172 (R83a PFX, m = 1):** excluded A ∈ {AZ, KRYPTOS, PALIMPSEST, ABSCISSA} at lags 1–10. R99 gives 0 at those
  lags for every alphabet, so it replicates that result.
- **L157 (R68 PTAK):** AZ/KRYPTOS, no constant. R99 extends it with the constant and to all tier alphabets.

## What this excludes, and what it does not
**Excluded exactly** (crib-assisted: the published letters in place and in the carved order):
- **Cipher:** y_i = s1·x_i + s2·x_{i−L} + c, with ranks in one alphabet A from the tier, any c and any primer,
  either sign pair.
- **Lags without errors:** 1–23 and 34–47.
- **Lags with one error allowed:** 1–23 and 36–45. The error can be one wrong published letter, or one wrong
  ciphertext letter anywhere on a link.

**Not excluded:**
- lags 24–33 and 48–96. The weak lags have chance-level feasible settings, and lags 27–29 and 53–96 carry no
  information;
- separate plaintext, ciphertext and feedback alphabets, beyond L27/L58/L172;
- alphabets outside the tier;
- a keyword combined with the autokey (m > 1);
- ciphertext autokey (see L17 and L157);
- a transposition layer;
- insertion or deletion;
- two errors.

Nothing from R99 enters any blind search.

## Review
**Independent review: NONE.** One model (Claude Code) registered, built and ran R99. ChatGPT is the named
reviewer. The natural independent checks are:
- re-deriving the chain criterion (`PREREGISTRATION.md` §2);
- a separately written checker of the same criterion on the frozen inputs.
