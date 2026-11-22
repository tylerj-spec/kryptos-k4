# RX2 mathematical challenge: internal review

Reviewer: ChatGPT, same model as the design builder. This is an internal mathematical check, **not** an independent-model council vote or a ledger promotion. No K4 text, published-letter positions, or language scores were read or used.

## Verdict

The two-rotor equations, modular constraint reduction, and bounded SAT/UNSAT/UNKNOWN kernel are correct for the declared integer-contact, position-dependent schedules. The important scope correction was the treatment of collapsed rows with a step-boundary phase; that correction is now included in `DESIGN.md`.

The review supports a synthetic development kernel. It does not establish blind recovery power for two unknown wirings and does not exclude any K4 hypothesis.

## Derivation checked

With `R_s(W)=T_-s W T_s`, the composition imposes

`b_i = W2(x_a_i + delta_i)`, where `a_i=P_i+s1_i`, `b_i=C_i+s2_i`, `delta_i=s2_i-s1_i`, and `x_a=W1(a)`.

Thus distinct observed first-rotor contacts must have distinct x values, while equal second-rotor outputs require equal second-rotor inputs and different outputs require different inputs. Equal-output constraints give `x_j-x_i=delta_i-delta_j` modulo 26. Graph potentials correctly detect inconsistent cycles. Remaining inequalities correctly forbid differences between component offsets. The implementation's two adjacency signs match those equations.

There is no division or inversion of arbitrary residues, so composite modulus 26 poses no field-arithmetic assumption. Difference 13 modulo 26 is handled correctly in explicit synthetic cases.

The global interface gauge is valid: replace `W1(x)` by `W1(x)+t`, and replace `W2(y)` by `W2(y-t)`. The complete cascade is unchanged at every position. Therefore fixing one component offset to zero is safe; fixing further components without another proved symmetry would not be justified.

If the constraints are satisfiable, both observed wiring relations are injections, each extendible independently to a full permutation. Those extensions provide a complete reversible cipher and preserve every observed pair. This sufficiency depends on the schedules being independent of the unknown plaintext and ciphertext. The checker correctly returns UNKNOWN on branching exhaustion instead of converting an incomplete search into UNSAT.

## Collapse and phase correction

A constant relative angle gives

`R_(s+d)(W2) R_s(W1) = R_s(T_-d W2 T_d W1)`.

However, collapsing to a single rotor does not prove coverage by a previously tested single-rotor schedule. R87's actual implementation uses `s_i=d*floor(i/n)` and does not enumerate step-boundary phase r.

The RX2-D domain has 400 distinct raw clock rows. Exactly 20 have constant relative angle: equal n, r, and direction on both stages. Removing them leaves **380 rows × 16 contact pairs = 6,080 labeled settings**. Of the removed rows:

- Eight have r=0: **128 labels** fall within R87's tested schedule domain.
- Twelve have r>0: **192 labels** collapse to phase-shifted single rotors that remain **OPEN**.

A concrete synthetic counterexample shows why r cannot be absorbed as a starting orientation. Take q=26, n=2, r=1, and a wiring swapping contacts 0 and 1. Its full time-dependent maps satisfy `F0 != F1 == F2`. A zero-phase rotor with n>=2 necessarily has `F0==F1`; a zero-phase n=1 rotor with `F1==F2` must be stationary at every time. No fixed input/output alphabet relabeling changes these equality relations between full maps. This phased family is therefore not merely a renamed R87 family.

Additive initial angular offsets **are** absorbable by conjugating each free wiring. The turnover phase h and step-boundary phase r change when transitions occur and cannot generally be removed that way.

## Stationary second rotor and label duplication

A stationary second rotor is an arbitrary output substitution after the moving first rotor. It generally does not collapse into R87's four fixed output alphabets. For example, identity W1 and a stationary W2 swapping A/B give a fixed A/B substitution. That substitution lies outside all stationary maps expressible by R87's 16 fixed contact pairs and cyclic translations. The internal checks explicitly verify this example.

The odometer count **16,640 labeled settings** is correct. It is not a count of distinct literal schedule arrays. At n=4 and h=0 or 1 the slow rotor never moves during 97 positions; its direction is then immaterial. There are 32 such clock labels (512 contact-pair labels). Across all O labels there are **1,016 distinct full schedule arrays**, or **16,256 arrays/contact pairs**. Keeping all 16,640 labels is safe and matches the stated bound; any later deduplication should use complete schedules and be fixed before a target run.

## Additional executed controls

`internal_review_checks.py` performs a separate synthetic challenge:

| Control | Result |
| --- | --- |
| q=4, length 4; all plaintext/ciphertext pairs for two irregular schedules, checked against every wiring pair | 131,072 comparisons; all agree |
| q=6 random instances checked by enumerating every first wiring and directly testing the second partial map | 200/200 agree: 72 SAT, 128 UNSAT |
| Reordering and duplicating those observations | 200/200 unchanged |
| Modulo-26 nonunit-difference cases | 2/2 correct |
| Global interface gauge transformations | 360/360 identical outputs |
| Additive initial-angle absorption | 30/30 identical outputs |
| Structural counts and phased/static counterexamples | Pass |

These controls ran through `audit/run_bounded_agg.py` with the design's synthetic budget: COMPLETE in **1.259 seconds wall, 1.244 seconds CPU, 9.3 MB sampled aggregate RSS**. Evidence is in `INTERNAL_REVIEW_RESULTS.json` and `INTERNAL_REVIEW_RESOURCE.json`.

**Signed: ChatGPT.** No further mathematical blocker was found within this defined model. A future experiment must still freeze its complete scope, key-equivalence test, resources and scoring policy, pass a fresh power gate, preserve all UNKNOWN outcomes, and keep the 192 phase-shifted single-rotor labels explicitly open unless separately tested.
