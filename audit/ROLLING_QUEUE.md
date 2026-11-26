# Rolling work queue

Procedure: `audit/OPERATING_PROCEDURE_ROLLING.md`. This file is edited in place as items move, and older states are
kept in git history.

## Audit batches
| Batch | Rounds | Auditor | Status |
|---|---|---|---|
| A | R98, R99, R100, R101 (L187–L190) | ChatGPT | **assigned 25 Nov 2026; in progress** |
| B | R102 onward (4–6 rounds) | ChatGPT | not started |

## Current batch: `audit/reviews/BATCH_WORK_ORDER_R102_R107.md`
| Item | Depends on | Dependency verified? | Status |
|---|---|---|---|
| R102 S3b algebra | — | — | **done: VERIFIED (L191).** C5 refuted the 'no exact crib check' claim |
| R103 S3b identifiability | R102's code (re-verified in R103's own gate) | not needed | queued |
| R104 feedback-chain decomposition and architecture | — | — | queued |
| R105 conditional synthetic solver | R103 IDENTIFIABLE and R104's feasibility gate | — | conditional |
| R106 joint synthetic solver | R105 GO | **must be independently verified** | conditional |
| R107 structured-key Slidefair feasibility | — | — | queued (independent branch) |

## Proposed new items (outside the approved batch; need approval)
| Item | Why | Depends on |
|---|---|---|
| **P1. Exact S3b crib check on K4.** Direct-pair necessary conditions for every pair of free alphabets, every (lag, signs, F); a type B round with its own gate (oracle, plants, two solvers) | R102 C5: about 42% of cells are excluded by chance alone, so the check has real power | none (its own gate re-verifies the solvers) |
| **P2. Ciphertext-only lag-1 repeated-pair test on K4.** A blind round with shuffle nulls, no clues | R102 C6: power 0.41 at L = 1 | none |

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
