# R93 result: wider nonzero-phase single-rotor scope excluded

Date: 22 November 2026, America/Chicago.

**Outcome: EXACT_SCOPE_EXCL for the registered all-correct and one-observation
error conditions.** K4 admits no wiring for any of the 145,728 registered
labels, both with all 24 observations and with any single observation omitted.
All 200 registered shuffles also have zero compatible labels under both checks.

Mode: **CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY**.
Gate type: **EXACT_CHECKER_CORRECTNESS**.
Blind recovery certified: **false**.
Independent review: **NONE**. This is a new ChatGPT execution with same-model
internal review and a separately implemented synthetic oracle, not an
independent-model promotion.

No plaintext was decoded, no wiring was completed, no surviving setting was
published, and no candidate or strength ranking was generated. No R93 output
was supplied to RX2 engineering or another blind candidate process.

## 1. Exact executed scope

The reversible model is the preregistered position-only stepping rotor:

`s_i = d * floor((i+r)/n)`, with positions i starting at zero,

`c_i = E_out[(W[(E_in.index(p_i)+s_i) mod26]-s_i) mod26]`.

W is any permutation of the 26 contacts. The input and output contact alphabets
independently range over AZ, KRYPTOS, PALIMPSEST and ABSCISSA, each constructed
keyword first followed by unused A–Z letters. The finite domain is
**n=5..96, r=1..n-1 and d in {-1,+1}**, giving 16 contact pairs and

`16 * 2 * sum(n-1 for n in 5..96) = 145,728` labels.

Every registered label was evaluated. There was no result-conditioned pruning,
fallback sampling, wiring search cutoff or budget extension.

The 9,108 clock labels induce 4,690 distinct 97-position clock sequences.
Including the contact-pair factor gives 75,040 clock/contact labels; 1,504 of
these are also represented by R87 zero-phase clocks, corresponding to 36,096
raw R93 labels. There are 73,536 distinct clock/contact labels outside that
schedule overlap. All overlaps and multiplicities were retained in the scan.
These are parameter and schedule counts, not independent statistical trials or
proofs that the corresponding sets of cipher functions are disjoint.

The earlier figure 145,920 counts nonzero phases for n=2..96 and includes
R92's 192 labels. R93 tests the 145,728-label remainder only. Combining the
recorded scopes of R87, R92 and R93 accounts for all 148,992 phase/contact/
direction labels with n=1..96 under the same model. This coverage accounting
does not independently review R87's remaining original results or strengthen
the review status of R93.

## 2. Frozen target counts

| Frozen input group | Labels per input | EXACT-compatible labels | Labels compatible after some one-observation omission | Label/omission pairs |
| --- | ---: | ---: | ---: | ---: |
| Original K4 | 145,728 | 0 | 0 | 0 |
| Each of the 200 shuffles | 145,728 | 0 | 0 | 0 |

Across all 201 inputs, the scanner evaluated **29,291,328 setting/input calls**.
The combined exact-and-deletion masks represent **732,283,200 logical
feasibility decisions**. The implementation evaluates all omissions jointly;
it does not repeat a separate wiring search for each omission.

The ordered input file contains the unchanged canonical ciphertext and 200
distinct frequency-preserving shuffles from seed **930400**. Exactly 200 draws
were needed. Input IDs, full setting counts and all aggregate inequalities
agree with the frozen protocol. Accumulated counts use Python integers; the
compiled kernel emits only bounded feasibility bitfields, not counts of
complete wirings. Those per-setting bitfields were not persisted.

The shuffle counts are descriptive compatibility controls. They supply no
p-value, language score, unusual-strength claim or plaintext lead. The
exclusion follows from the exact constraints within the declared model.

## 3. Why the exact and one-error conclusions follow

For observation (i,p,c), a setting requires `W[x_i]=y_i`, where

`x_i=(E_in.index(p)+s_i) mod26`,

`y_i=(E_out.index(c)+s_i) mod26`.

A complete wiring exists exactly when these assignments form a partial
bijection. Equivalently, there must be no pair of observations for which input
equality and output equality disagree. If no such conflict exists, unused
inputs can be matched with unused outputs to extend the partial map. The
target code does not construct that extension.

Deleting observation j makes the assignments feasible exactly when every
conflict edge touches j. Intersecting all conflict-edge endpoint sets therefore
computes all allowable one-observation omissions. The frozen zero counts mean
that neither the full observation list nor any individual omission admits a
wiring at any registered label.

Because the clock depends only on position, one wrong reported plaintext
symbol alters one observed pair. One fixed-length ciphertext substitution
alters one pair if it falls at an observed position, and no pair otherwise.
Thus the DROP exclusion covers each of those single-error models separately.
It does not establish a conclusion for simultaneous errors at different
positions, insertions/deletions, shifted observations or a lost state update.
The synthetic lost-update example changed 90 positions and was explicitly
outside the model.

The exact contradiction does not assume English or a language model. It
requires that the supplied observations describe the actual enciphered
symbols, subject only to the registered single-observation relaxation.

## 4. Formal correctness gate

The complete gate was run once after source publication and passed every
registered requirement. Its GO means correctness of the specified finite
compatibility test under the proof and test suite; it does not mean blind
plaintext recovery, family recognition or confidence calibration.

| Requirement | Completed evidence |
| --- | --- |
| Complete-key toy oracle | 141,793 ordered pair-list cases; q=2 lengths 1..6, q=3 lengths 1..5, q=4 lengths 1..4; zero false exclusions, false feasibilities or omission-mask disagreements |
| Full-size parameter plants | 8,832 plants over every period n=5..96, the three registered phases {1,floor(n/2),n-1}, both directions and all 16 contact pairs |
| Plant/error setting checks | 44,160 checks; 17,664 exact forward/inverse round trips; 8,832 checks of each specified substitution condition |
| Full-catalog code path | First and last labels, indices 0 and 145,727, both accept their independently constructed plants |
| Adversarial cases | One conflict, disjoint conflicts, high omission bits, negative offsets, repeated contacts and the separate lost-update counterexample pass |
| Scope and worked example | All declared counts and the q=5 event-clock example reproduced |
| Throughput gate | Three full-catalog synthetic scans; conservative target forecasts 20.255 seconds wall and 22.044 CPU, below the registered 80% thresholds |

The reference uses a countdown clock, explicit contact rotation and exhaustive
complete wiring permutations in the toy domain. The production kernel uses
the conflict/intersection criterion. The reference is an independent code
path, not a second model or a fresh hidden-English recovery gate. The full-size
plants test the three specified phases per period, while the target scan
enumerates every registered nonzero phase.

## 5. Resources and prospective publication sequence

| Job | Status | Wall seconds | Aggregate CPU seconds | Sampled aggregate RSS, MiB | Registered caps |
| --- | --- | ---: | ---: | ---: | --- |
| Formal correctness gate | COMPLETE / GO | 6.011 | 5.943 | 92.6 | 180 s wall / 120 CPU / 512 MiB |
| Single target audit | COMPLETE | 6.273 | 7.972 | 94.5 | 1,800 s wall / 1,200 CPU / 512 MiB |

Both jobs used `audit/run_bounded_agg.py`, with no retry or source change.
Its memory metric samples the sum of process-group RSS every 0.25 seconds and
can double-count shared mappings or miss shorter peaks; the per-process
address-space cap also applies. CPU is aggregate over the job's process group.

| Prospective stage | Published commit |
| --- | --- |
| Registration and explicit mode clarification | `567f418961cc18847207008468679115074f4c93` |
| Reviewed source/protocol and QA | `3e781d57994a617610db943ea57438759dc6b4ce` |
| Completed correctness gate and gate freeze | `2621a5e0d64fe787c498cc765f7ee14dd78af1ee` |
| Complete target input/output/resource freeze | `542165b77806917d17dd4f3f8314685fd2d1e55a` |
| Interpretation | This later result note |

The coordinator confirmed each publication and fetched commit before the next
authorized stage. The target driver verified the source and gate provenance
before opening the canonical ciphertext and parsing the observation literal.
Interpretation waited until the complete target freeze was published. Both
freeze manifests were then checked against their committed and local bytes:
15 gate entries and 21 target entries.

The legacy QA schema requires a positive `max_candidates` value. Its unused
ceiling is 1, while the stricter declared limits `max_decoded_candidates=0`
and `max_surviving_setting_outputs=0` remain binding. The actual count is zero.
Aggregate records have their separate cap of 201 and were not renamed
candidates. No guardrail code was changed.

## 6. Evidence and limits

| Artifact | SHA-256 |
| --- | --- |
| `r93/PROTOCOL.sha256` | `bffbf215b3366da3cc95d969c21c1b9352030179c7ab6f0c153a95544a3cf234` |
| `r93/holdout/GATE_FROZEN.sha256` | `f6171d1dc9c49fa0f85e1488a1befe684d2a90551a26b1417f2dbce1c0479d98` |
| `r93/k4/INPUTS.tsv` | `fbc28710cfba45278f9c34fada0c212e622d17df766b8e82029ec1b6fdad9610` |
| `r93/k4/AGGREGATES.json` | `8022f709941ff2d37771bf2363d12d11f48ea69420dddbe7039a9f213b8e0ee0` |
| `r93/TARGET_RESOURCE_LOG.json` | `74516856e0984ffa8866d5159b19a2521058516b4f5f9d0c96684e518d47b817` |
| `r93/k4/FROZEN.sha256` | `090a511691ed4166c4a438b4cf6ecbff4cd660bfa99c02af650976cd3fc55477` |

Uncovered domains include other contact alphabets, step sizes other than +/-1,
multiple rotors, irregular or letter-triggered clocks, transposition, changed
alignment, insertions/deletions, simultaneous error models and n>=97. No wider
finite-schedule equivalence is inferred here without its own proved accounting.
No candidate, readable plaintext, key, English-recovery result or independent-
model review is claimed. R94 remains a separately registered development task;
this exclusion supplies no input or authorization for it.

**Signed: ChatGPT — completed registered exact-only execution and same-model
scope/result review.**
