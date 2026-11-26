# Rolling work queue

Procedure: `audit/OPERATING_PROCEDURE_ROLLING.md`. This file is edited in place as items move, and older states are
kept in git history.

## Audit batches
| Batch | Rounds | Auditor | Status |
|---|---|---|---|
| A | R98, R99, R100, R101 (L187–L190) | ChatGPT | **assigned 25 Nov 2026; in progress** |
| B | R102, R103, R104, R105 (L191–L194) | ChatGPT | **ready for audit (26 Nov 2026)**; R106 waits on it |
| C | R107 onward (L195–) | ChatGPT | open |

## Current batch: `audit/reviews/BATCH_WORK_ORDER_R102_R107.md`
| Item | Depends on | Dependency verified? | Status |
|---|---|---|---|
| R102 S3b algebra | — | — | **done: VERIFIED (L191).** C5 refuted the 'no exact crib check' claim |
| R103 S3b identifiability | R102's code (re-verified in R103's own gate) | not needed | **done: IDENTIFIABLE (L192)** |
| R104 feedback-chain decomposition and architecture | — | — | **done (L193).** R105 entry gate met for B known, F = A (19/24); the A-known mode is closed (0/24) |
| R105 conditional synthetic solver | R103 IDENTIFIABLE and R104's feasibility gate | entry met (R103, R104); both unaudited, batch B | **done: GO (L194)** for B known, F = A: 42/50 plants |
| R106 joint synthetic solver | R105 GO | **must be independently verified**; not yet (batch B) | **blocked until ChatGPT verifies R105** |
| R107 structured-key Slidefair feasibility | — | — | **done (L195): TESTABLE at p 1–8, 10, 11** by the exact check X107; WEAK at 9, 12, 16, 24, 36 and any key |

## Proposed new items (outside the approved batch; need approval)
| Item | Why | Depends on |
|---|---|---|
| **P1. Exact S3b crib check on K4.** Direct-pair necessary conditions for every pair of free alphabets, every (lag, signs, F); a type B round with its own gate (oracle, plants, two solvers) | R102 C5: about 42% of cells are excluded by chance alone, so the check has real power | none (its own gate re-verifies the solvers) |
| **P2. Ciphertext-only lag-1 repeated-pair test on K4.** A blind round with shuffle nulls, no clues | R102 C6: power 0.41 at L = 1 | none |
| **P3. Blind K4 run of R105's solver S105 with B from a short list registered in advance** (for example straight and KRYPTOS-keyed), lags 1–5, both σ, with decoy nulls on shuffled K4. Exploratory; the score detects hypotheses, not letter-perfect decryptions | R105 GO (L194): 42/50 synthetic, all recoveries above all decoys | **R105 independently verified** (batch B) |
| **P4. Exact periodic-key free-alphabet Slidefair crib check on K4** (X107): 16 conventions × p 1–48 and any key, EXACT and DROP levels, with 200 shuffle controls and the rank reference as post-freeze cross-check; crib-assisted, exclusion-only | R107 (L195): chance exclusion ≥ 0.50 at p 1–8, 10, 11 with one pair dropped | none (its own gate re-runs R107's soundness and two-implementation checks) |

## Fallback tasks (independent of everything above)
| Item | Status |
|---|---|
| F1 reversible language masking, as concrete mechanisms with predictions | available |
| F2 layered simple constructions, as a G0 catalogue | available |
| F3 non-repeating deterministic key generation | available |

## Standing parallel research priorities
| Area | Priority |
|---|---|
| Construction discovery | very high |
| Reversible language masking | high |
| Layered encryption | high |
| Historical cryptographic methods | high |
| Non-repeating key generation | medium |
| Rotor solver | low (only with a materially different strategy) |
| Unrestricted free-alphabet Slidefair | deferred (insufficient identifiability) |
