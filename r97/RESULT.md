# R97 result (Claude Code, 24 Nov 2026): joint recovery SOLVER_NO_POWER; the RX2-O solver line stops

## In plain words
**With neither rotor wiring given, the solver found nothing**, even with the structure supplied.
- **Results:** both registered versions recovered 0 of the 48 practice messages. The best was 13 of 97 letters.
- **Cause:** in every case the true text scores higher than what the search found, so the letter model is fine and
  the search is what fails.
- **Diagnostics:** the true key is stable once reached. But starting from the *true* first wiring with only 4 random
  swaps, and a random second wiring, the alternation still recovers nothing. There is no usable basin around the
  truth.
- **Separately:** a full pipeline would also be at least 140× too slow (`G0_FEASIBILITY.md`).

**Per the pre-registration, the RX2-O solver line stops.** RX2-O stays OPEN: nothing about K4 or the cipher family
is excluded.

## Registration and chronology (each pushed before the next)
| Step | Commit |
|---|---|
| Approval: Tyler, 24 Nov, "Your good for the next steps", on the post-R96 queue (PR #113). Disclosed as preceding the written spec | — |
| G0 feasibility note, pre-registration, manifest | d7659d8 |
| Source and hashes | 34a156d |
| Model rebuilt to digest e9c0848f…; self-tests PASS; the speed rule fixed **I_c = 140,000** | 534da0e |
| Version 1 frozen | **93563a1** |
| Version 1 evaluation | after 93563a1 |
| Version 2 frozen | **84f5447** |
| Version 2 evaluation, diagnostics | after 84f5447 |

The solver read only `r94/inputs/PANEL.tsv` (no plaintext) and the model. Witnesses: 288/288 (version 1) and
144/144 (version 2).

| Job | Status | Wall s | CPU s | Cap |
|---|---|---|---|---|
| Version 1: alternation, 6 restarts × 4 rounds | COMPLETE | 333.9 | 330.4 | 750 / 700 |
| Version 2: iterated local search with kicks, 3 restarts | COMPLETE | 212.5 | 210.4 | 750 / 700 |
| Diagnostics | COMPLETE | 34.9 | 34.6 | 240 / 120 |

## Results (`eval_v1/EVAL.json`, `eval_v2/EVAL.json`)
| Measure | Version 1 | Version 2 | Bar |
|---|---|---|---|
| Top-1 ≥ 95/97 | **0/48** | **0/48** | ≥ 44 |
| Every cell | 0/6 | 0/6 | ≥ 5/6 |
| Exact / recall over retained / key up to gauge | 0 / 0 / 0 | 0 / 0 / 0 | reported |
| Median / maximum letters | 6 / 13 | 6 / 12 | reported |
| **Search gaps** (truth scores above top-1) | **48/48** | **48/48** | reported |
| Objective counterexamples | 0 | 0 | reported |

**Outcome: SOLVER_NO_POWER** for these two methods at this budget, on the spent panel.

## Truth-assisted diagnostics (`diagnostics/DIAGNOSTICS.json`; after the freezes; reported, not gated)
| Start | Cases reaching ≥ 95/97 | Median letters |
|---|---|---|
| **D1:** the true (U, V), one alternation round | **44/48** (minimum 92) | 97 |
| **D2:** the true U with **4** random swaps, V random, 2 rounds | **0/48** | 7 |
| **D2:** the true U with 8 swaps | 0/48 | 6 |
| **D2:** the true U with 12 swaps | 0/48 | 6.5 |

- **D1.** The truth is a fixed point. The 4 exceptions drift to the objective counterexamples R96 found.
- **D2 is decisive.** R96 recovers V from the exact true U in 47/48 cases. Here U is wrong on at most 8 of 26
  contacts and V is random, and the first V-step locks onto a wrong V. The alternation never recovers.
- So the conditional step needs the other wiring essentially exact. Alternation from anything a ciphertext-only
  initializer could plausibly give has no path to the truth.
- This answers the reviewer's first challenge in the negative.

## What this means
**Joint RX2-O recovery is not shown possible** on 97 letters with this objective, by alternation, iterated local
search or (earlier) joint annealing:
- RX2-O development v2/v3: 0/48;
- R94: 0/48;
- R97 versions 1 and 2: 0/48.

R96's conditional success does not extend to the joint problem.

**Throughput (G0).** Even a working joint solver would make a structure-blind pipeline 140×–7,000× over the fresh-gate
cap.

**Next, as registered:** stop the RX2-O solver line. Effort moves to the **parallel construction-discovery lane** of
`audit/reviews/POST_R96_NEXT_STEPS_20261123.md`: up to three hand-plausible 1990-era mechanisms, each with exact
forward and inverse, a G0 equivalence check, a predicted ciphertext-only observation, and a sealed synthetic power
test. Reopening RX2-O needs a materially different method: an initializer that recovers one wiring essentially
exactly from ciphertext alone. Such a method must be shown on synthetic data first.

**Not established:**
- that joint recovery is impossible (other methods remain);
- anything about K4, which was not touched.

The panel is spent. These are development results, not generalization.

## Review
**Independent review: NONE.** One model (Claude Code) built and ran R97. ChatGPT is the named different-model
reviewer. It can recount 0/48 from the frozen finals and the public truth.
