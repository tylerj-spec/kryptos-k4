# R96 result (Claude Code, 23 Nov 2026): conditional recovery PASSES (GO_FOR_JOINT_DEVELOPMENT)

## In plain words
**With one of the two rotor wirings supplied, the solver now recovers the text.**
- It used the same 48 practice messages that R94's solvers failed on (0/48).
- With R95's order-5 letter model and plain annealing, it recovered at least 95 of 97 letters in 45/48 cases when
  the second wiring was given, and 47/48 when the first was.
- It met the bar in every one of the eight turnover groups.
- It never failed for lack of search. Every miss is a case where a slightly wrong text scores higher than the true
  one.

This is the second rung of the development ladder (objective → **conditional** → joint → fresh gate). The next rung,
with both wirings unknown, is where every earlier attempt failed. No K4 run is authorized, and nothing is excluded.

## Registration and chronology (each pushed before the next)
| Step | Commit |
|---|---|
| Approval (Tyler, 23 Nov: "I approve") and registration | 06fc6b5 |
| Source, inputs, hashes | 5a352c5 |
| Model rebuilt to digest e9c0848f…; self-tests PASS; the speed rule fixed **I = 230,000** | b8f4e1f |
| Version 1 outputs frozen (before the truth was opened) | **1b7ee5e** |
| Amendment 1: the freeze manifest renamed `OUTPUTS.sha256` for the guardrail's name rule; the evaluator reads it; outputs and freeze unchanged | 29f3a89 |
| Version 1 evaluation | the commit after 29f3a89 |

**Version 1:** 96 conditions × 16 seeded starts × 230,000 proposals, then greedy polish.
- COMPLETE in 266 s wall and 264 s CPU, against caps of 450 / 450.
- The forward witness passes for all 1,536 saved states.

The solver read only `r96/inputs/CONDITIONS.tsv`, which holds no plaintext, and the model.

## Result (`r96/eval_v1/EVAL.json`)
| Measure | true-V (U searched) | true-U (V searched) | Bar |
|---|---|---|---|
| **Top-1 ≥ 95/97** | **45/48** | **47/48** | ≥ 44 |
| By cell (n1t3, n1t4, n2t1, n2t2, n3t1, n3t2, n4t0, n4t1) | 6, 5, 6, 6, 6, 5, 6, 5 | 6, 6, 6, 5, 6, 6, 6, 6 | ≥ 5 each |
| Exact 97/97 | 43 | 44 | reported |
| Any of the 8 retained ≥ 95 | 47 | 48 | reported |
| Wiring right on every used contact | 43 | 44 | reported |
| Starts (of 16) reaching ≥ 95, median / minimum | 10 / 0 | 11 / 3 | reported |
| **Search gaps** (truth scores above top-1) | **0** | **0** | reported |
| Objective counterexamples (a wrong text above truth) | 5 | 4 | reported |

**Version 1 passes both conditions, so version 2 is not run.** Outcome: **GO_FOR_JOINT_DEVELOPMENT**.

**The nine objective counterexamples:**
| Case | Condition | Letters | Score above truth | Source |
|---|---|---|---|---|
| D_007 | true-U | 96 | +2.822 | R95's one-swap witness |
| D_009 | true-V | 96 | +0.722 | R95's one-swap witness |
| D_011 | true-V | **94** | +0.413 | R95's one-swap witness |
| D_019 | true-U | 96 | +0.214 | R95's one-swap witness |
| D_033 | true-V | 96 | +0.622 | R95's one-swap witness |
| D_002 | true-U | 95 | +1.647 | farther away |
| D_018 | true-U | **92** | +0.895 | farther away |
| D_032 | true-V | **93** | +3.077 | farther away |
| D_042 | true-V | **94** | +0.098 | farther away |

- Five of them are exactly R95's one-swap witnesses, at the same margins. The other four are wrong optima beyond one
  swap.
- The four in bold are the misses.
- So the order-5 objective, not the search, now limits recovery, at about 4% of conditional cases.

## What this does and does not establish
**Established, on spent, truth-assisted development data:**
- with the structure and one true wiring supplied, R95's objective and this annealer recover the other wiring;
- this holds across all eight turnover regimes.

**Not established:**
- recovery with **both** wirings unknown (the next rung);
- unknown structure, or throughput for a full search;
- fresh texts, masking, misspelling or false-positive rates;
- anything about K4.

RX2-O stays **OPEN**. No exclusion follows from any development result.

**Next** (charter §6.3): the joint stage needs its own work order. That is both wirings unknown with the structure
supplied, on the same 48 cases, with ≥ 44/48 top-ranked ≥ 95/97 and ≥ 5/6 per cell. Earlier joint attempts (RX2-O
v1–v3, R94) found 0/48. A working conditional solver suggests an alternating design: anneal one wiring with the other
held, and swap roles. That design is not yet specified.

## Review
**Independent review: NONE.** One model (Claude Code) built and ran R96. ChatGPT is the named different-model
reviewer. It can re-derive the counts from `r96/run_v1/RESULTS.jsonl` and the public truth in minutes.
