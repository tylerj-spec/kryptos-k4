# Audit readiness index, R98–R113 (Claude Code, 27 Nov 2026)

Affected ledger IDs: none. This is an index for the substantive review; it changes no row.

Validation: compiled from `LEDGER.md` (L187–L201), the round result notes and errata,
`audit/reviews/R108_R111_CHATGPT_QUALITY_REVIEW_20261127.md` (partial) and `audit/ROLLING_QUEUE.md`. Every listed
round is merged on `main`. Each has a pre-registration, a sealed gate or registered run, a bounded job and a CI
re-run or recount.

Independent review: NONE (one model). Everything below awaits the different-model audit.

## What is ready, by batch
| Batch | Round | Ledger | Claim (in its stated scope) | Check first |
|---|---|---|---|---|
| A | R98 | L187 | Slidefair, **tier** keyword alphabets, any key: EXCL (one pair may be set aside) | Same-column rule coverage; the derivation of the cancelled-key criterion |
| A | R99 | L188 | Condi-type autokey, one tier alphabet: EXCL at the lags listed in the row | The chain-link algebra |
| A | R100 | L189 | Quagmire-type autokey, two tier alphabets: EXCL at the lags listed in the row | Direct-link joins; float64 code capping |
| A | R101 | L190 | Autokey on one arbitrary alphabet, lags 1–5: EXCL, 20/20 cells | The CRT enumeration and the DFS agreement |
| B | R102 | L191 | S3b algebra (Latin square, gauges, a necessary consistency test) | The equation builder `r102/s3b102.py rows`, which R109 also relies on |
| B | R103 | L192 | S3b identifiable at 97 letters (0/3,000) | Whether unrelated passages are an adequate null |
| B | R104 | L193 | B known with F = A reduces to a substitution; the A-known mode is closed | The reductions (E2) |
| B | R105 | L194 | Solver S105 GO: 42/50 at ≥ 90/97 letters (31 at ≥ 95, 17 exact) | The gauge (G1a), the stage-1 table, the dev history; **R106 and R111 depend on this** |
| C | R107 | L195 | Free-alphabet Slidefair is testable with a periodic key (chance power) | X107's collision rule |
| C | R108 | L196 | K4: **conditional** EXCL of 768 cells (no same-column crib pair); 372 with one bad pair | The shared `X.check` pipeline; the conditional wording |
| C | R109 | L197 | K4: 34/420 cells fail necessary direct-pair equations (6 with one error); 322 pass the screen only | 22 of the 34 exclusions are DFS-only; Amendment 2 relaxed a gate criterion |
| C | R110 | L198 | K4: no lag-1 signal; the lag-21 excess re-measures R71 | That the permutation test is right |
| C | R111 | L199 | K4 blind S105: NO_SIGNAL, provisional on batch B | Witnesses run from position L only; 8 gate plants |
| C | R112 | L200 | Exact Slidefair check with general same-column handling: sound, keeps power | The Beaufort sign fix (caught by T1); the shared equation table |
| C | R113 | L201 | P5 step 1: CLOSE (conservative ratios 1.8–2.3 < 10) | C3's threshold change before the run; the IC window |

## Independence gaps already known (from the partial review and the errata)
- **Shared code between solvers:**
  - R109's two solvers share the equation builder.
  - R108's rank reference runs inside the same pair and DROP pipeline.
  - R112's reference shares the per-pair equation table.
- **R105/R111 synthetic data:** a single source text with no enforced split; unknown quadgram provenance;
  re-encryption checked from position L only. These are addressed by the validation plan (P7).

## Waiting on the review
| Item | Waits for |
|---|---|
| **R106** (both alphabets free) | substantive verification of R105 (batch B) |
| R111's status (provisional) | batch B |
| **P6:** K4 run of X112 (removes R108's no-same-column assumption) | approval, after the review |
| **P7:** the S105 validation round (`audit/reviews/SOLVER_VALIDATION_PLAN_20261127.md`) | agreement on its bars |
| Fallback catalogues F1–F3 | available; not started |

## Closed in this period
- **P5 (lag 21):** closed by R113 with no K4 run.
- **Proposals P1–P4:** run as R109, R110, R111 and R108.
