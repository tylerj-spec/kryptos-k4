# R93 independent-model review (Claude Code): L182's finite exact exclusion is reproduced

**Verdict: PASS.**
- Within its registered scope, **no setting of the 145,728 is compatible with K4's 24 published letters**, either all
  of them (EXACT) or with any one set aside (DROP).
- **The same holds for every one of the 200 frozen shuffles.**
- Every per-input count in R93's `r93/k4/AGGREGATES.json` is reproduced exactly by a separately derived and separately
  coded checker.
- L182's finite exact exclusion qualifies for promotion to INDEPENDENTLY VERIFIED. Nothing else does.

Reviewer: Claude Code, a different model from R93's builder (ChatGPT). Same-model subtasks are one review.

## What was reviewed
**L182** (`r93/PREREGISTRATION.md`):
- one rotor with any wiring of 26 contacts;
- AZ/KRYPTOS/PALIMPSEST/ABSCISSA contacts on each side (16 pairs);
- s_i = d·⌊(i + r)/n⌋ for n 5–96, r 1..n−1, d ±1, in place: 145,728 labels;
- the frozen 201 inputs (`r93/k4/INPUTS.tsv`) and the 24 published observations.

## How (`PLAN.md`, published before any review code)
**Own derivation.** A wiring exists iff the observed (input contact, output contact) pairs form a partial bijection.
Any partial bijection extends to a permutation by pairing the unused contacts. The offsets depend only on position,
so:
- one wrong published plaintext letter changes exactly one pair;
- so does one ciphertext substitution at a published position;
- a substitution elsewhere changes none.

DROP-infeasibility therefore excludes each single-error model separately.

**Different formulation and code.**
- `check93r.c` re-checks **each of the 24 omissions from scratch**: 25 forward/backward-table checks per label and
  input. R93 instead intersects the endpoints of a pairwise conflict graph.
- It computes offsets by **counting step events** rather than by the floor formula.
- The review imports nothing from R87, R92 or R93. R93's checker sources were not read before this review's source
  was published.

**Synthetic gate** (`SYNTHETIC.json`): **GO** on all seven checks, in 9.3 s wall, 9.2 s CPU and 35 MB, against caps
of 180 / 120 / 512.
| Check | Result |
|---|---|
| T1 complete-key toy oracle (q 2–5, every pair list of the stated lengths: 33,483) | 0 disagreements with brute force over all q! wirings, EXACT and every omission |
| T2 schedules and scope | step-event offsets equal the floor formula on all 9,108 clocks; **every R93 scope count reproduced**: 145,728 labels, 4,690 distinct clock sequences, 75,040 clock/contact labels, 94 sequences (1,504 clock/contact, 36,096 raw labels) shared with R87's zero-phase clocks, 73,536 outside, 0 shared with R92 |
| T3 plants at **every** label (145,728; R93 planted 3 phases per period) | every true setting accepted; 9,108 full round trips |
| T4 error plants (9,108 × 3) | a changed observed plaintext letter or an observed ciphertext substitution leaves that omission feasible; an off-mask substitution leaves EXACT feasible |
| T5 second implementation (pure-Python dictionary checker) | 24,000 flag vectors equal the C checker's |
| T6 sensitivity and throughput | a planted input is reported feasible by the full scan (16 EXACT labels, 56 DROP labels); random inputs 0; forecast 37.6 s against the 1,440 s / 960 s limits |
| T7 the registered q = 5 worked example | reproduced and inverted |

**Target replay** (`REVIEW_RESULTS.json`): one run, COMPLETE, 13.3 s wall, 13.2 s CPU, 30 MB, against caps of
1,800 / 1,200 / 512, with zero retries.
- **Provenance:** the input file, K4 and observation-file hashes match. The 24 observations were parsed as a literal,
  not imported: unique and in range. The 200 shuffles are distinct, frequency-preserving and not K4, and were
  regenerated **byte for byte** from seed 930400 in 200 draws.
- **Counts:** 29,291,328 setting/input calls, each with an EXACT decision and 24 omission decisions (702,991,872
  omissions; 732,283,200 decisions in all, R93's figure).

| Input | EXACT-feasible labels | Labels with a feasible omission | Label/omission pairs |
|---|---|---|---|
| K4 | **0** | **0** | **0** |
| Each of the 200 shuffles | 0 | 0 | 0 |

All 201 per-input records equal R93's.

## Chronology (each commit pushed and checked on the remote before the next step)
| Step | Commit |
|---|---|
| Plan and budgets | 44dfb52 |
| Review source and hashes (`SOURCE.sha256`) | b33e248 |
| Synthetic gate GO (`GATE_FROZEN.sha256`) | 529e90f |
| Target replay frozen (`REVIEW_FROZEN.sha256`) | 5771533 |
| This review | the commit adding this file |

## Limits
- **Finite scope only.** Not reviewed:
  - other contact alphabets, step sizes or n ≥ 97;
  - multiple rotors, irregular or letter-driven stepping;
  - transposition, changed alignment, insertion or deletion;
  - simultaneous errors at two observed positions;
  - lost state updates.
- **R87.** The remaining R87 labels (L176 beyond n ≤ 4) are not reviewed here. Of the combined R87/R92/R93 figure
  of 148,992 labels, independent review now covers:
  - the 145,920 nonzero-phase labels (R92's 192 by ChatGPT, R93's 145,728 here);
  - the 128 zero-phase labels with n ≤ 4 (ChatGPT's R92 review).

  It does not cover R87's 2,944 zero-phase labels with n 5–96.
- **Labels are not functions.** The 145,728 labels include finite-clock duplicates (4,690 distinct sequences). They
  are not independent trials, and distinct schedules need not be distinct cipher functions.
- **Input assumptions.** The exclusion is exact and language-independent, but it assumes the published letters are
  in place, in the carved order, and right up to the one registered relaxation.
- **Plan correction (additive).** `PLAN.md` §4 says "732,283,200 omission decisions plus 29,291,328 EXACT decisions".
  The correct split is 702,991,872 omission decisions plus 29,291,328 EXACT decisions, 732,283,200 in all.
- **Outputs.** No plaintext, wiring, feasible-label list, ranking or score was produced. Nothing here enters RX2, R95
  or any blind search.

**Signed: Claude Code, 23 November 2026, independent-model reviewer of ChatGPT's R93.**
