# Rolling work queue

Procedure: `audit/OPERATING_PROCEDURE_ROLLING.md`. This file is edited in place as items move, and older states are
kept in git history.

## Audit batches
| Batch | Rounds | Auditor | Status |
|---|---|---|---|
| A | R98, R99, R100, R101 (L187–L190) | ChatGPT | **assigned 25 Nov 2026; in progress** |
| B | R102, R103, R104, R105 (L191–L194) | ChatGPT | **ready for audit (26 Nov 2026)**; R106 waits on it |
| C | R107, R108, R109, R110, R111 (L195–L199) | ChatGPT | **ready for audit (27 Nov 2026)**, after batch B |

## Current batch: `audit/reviews/BATCH_WORK_ORDER_R102_R107.md`
| Item | Depends on | Dependency verified? | Status |
|---|---|---|---|
| R102 S3b algebra | — | — | **done: VERIFIED (L191).** C5 refuted the 'no exact crib check' claim |
| R103 S3b identifiability | R102's code (re-verified in R103's own gate) | not needed | **done: IDENTIFIABLE (L192)** |
| R104 feedback-chain decomposition and architecture | — | — | **done (L193).** R105 entry gate met for B known, F = A (19/24); the A-known mode is closed (0/24) |
| R105 conditional synthetic solver | R103 IDENTIFIABLE and R104's feasibility gate | entry met (R103, R104); both unaudited, batch B | **done: GO (L194)** for B known, F = A: 42/50 plants |
| R106 joint synthetic solver | R105 GO | **must be independently verified**; not yet (batch B) | **blocked until ChatGPT verifies R105** |
| R107 structured-key Slidefair feasibility | — | — | **done (L195): TESTABLE at p 1–8, 10, 11** by the exact check X107; WEAK at 9, 12, 16, 24, 36 and any key |

## Proposals P1–P4: done (Tyler, 27 Nov 2026: "Do the 4 proposals then we'll do the audit")
| Item | Round | Result |
|---|---|---|
| P1 exact S3b crib check on K4 | **R109 (L197)** | 34 of 420 checkable cells excluded (6 with one error allowed); mostly open |
| P2 ciphertext-only lag-1 test | **R110 (L198)** | no lag-1 signal (p = 0.071); exploratory lag 21 p = 0.0013 (Bonferroni 0.032) |
| P3 blind S105 on K4, B ∈ {AZ, KRY} | **R111 (L199)** | NO_SIGNAL (provisional on the batch-B audit of R105) |
| P4 exact free-alphabet periodic Slidefair | **R108 (L196)** | all 768 cells excluded at the exact level, any key included; 372 with one bad pair |

## Proposed new items (need approval)
| Item | Why | Depends on |
|---|---|---|
| **P5. Lag-21 follow-up (ciphertext only).** List the constructions that predict an R_21 excess, give each its own synthetic power, and test each in a registered blind round | R110's exploratory lag-21 excess (p = 0.0013; Bonferroni 0.032 over 24 lags) | none; must stay blind |

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
