# R92: independent exact review and saved-evidence audit

Affected ledger IDs: L181
Promotes: L181
Validation: Independently derived conflict-graph feasibility proof; exhaustive
toy permutation oracle; 320 full-size planted controls and both substitution
error tests; complete exact/single-deletion replay on all 201 frozen inputs;
2,015 independent candidate forward witnesses; saved gate/evaluation arithmetic;
101 hash-manifest entries and historical freeze/commit checks.
Independent review: YES ChatGPT, reviewing Claude Code's R92 implementation.
Same-model ChatGPT subtasks are one review, not additional independent models.

## Decision

**The R92 finite exact exclusion is independently verified. Promote L181 only
at that exact scope.** No R92 setting admits any wiring consistent with all 24
published observations, or with any one observation removed. The independently
implemented replay agrees with every retained original exact/drop aggregate.

The explicitly registered additional R87 subset also passes: its 128
zero-phase labels with n=1..4 have no feasible wiring under either screen.
Together the two audited subsets cover **all 320 phase/contact/direction labels
for n<=4**. This is an independent exact statement, not a blind solution.

This review does **not** promote the whole R87/L176 row. Its 2,944 zero-phase
labels for n=5..96, its original null panel, and its two-error diagnostic were
not replayed here. Original frozen files and original blind results are intact.

## Exact domain and result

For every setting, the wiring is an arbitrary permutation of 26 contacts.
Input and output alphabets independently range over AZ, KRYPTOS, PALIMPSEST
and ABSCISSA. Directions are +1 and -1. The schedule is
`s_i=d*floor((i+r)/n)`, with i counted from zero.

| Audited subset | Timing domain | Labels | K4 feasible, all 24 | K4 feasible, any single deletion | Shuffles with any feasibility |
| --- | --- | ---: | ---: | ---: | ---: |
| R92 RXP | n=2..4, r=1..n-1 | 192 | 0 | 0 at every observed position | 0/200 for both screens |
| Registered R87 subset | n=1..4, r=0 | 128 | 0 | 0 at every observed position | 0/200 for both screens |
| Combined audited domain | n=1..4, r=0..n-1 | 320 | 0 | 0 | 0/200 for both screens |

The complete audit represents **64,320 base decisions and 1,543,680
single-deletion decisions: 1,608,000 logical feasibility decisions**. The
implementation determines the deletion results together, rather than repeating
the same computation 24 times. Every input and setting is included; this is
not a sampled replay.

The report retains all 24 deletion counts for every input. It distinguishes
the number of settings admitting some deletion from the sum of
setting/deletion combinations. Both are zero here, so the original aggregate
counting convention does not affect the conclusion.

No target plaintext, feasible-setting list, wiring assignment or key completion
was generated or emitted. With all shuffles also infeasible, these exact results
do not rank K4 as unusually compatible with the model.

## Why the independent check is exact

For a known observation `(i,p,c)`, the cipher requires

`W[x_i]=y_i`,

where `x_i=(E_in.index(p)+s_i) mod26` and
`y_i=(E_out.index(c)+s_i) mod26`.

The independent checker builds a conflict graph on observations. An edge joins
i and j if equality of their x contacts differs from equality of their y
contacts. With no edges, every repeated input has one output and different
inputs have different outputs. This is precisely a partial bijection. Pairing
unused inputs with unused outputs proves that it extends to a full wiring;
the audit never constructs that extension for target data.

Removing observation j succeeds exactly when every conflict edge touches j.
Intersecting the endpoint bits of all edges computes all permissible deletions.
This derivation differs from the original implementations' direct pair scan
and forward/backward dictionaries. The checker imports neither original cipher
code nor any original gate, witness or evaluation implementation.

The schedule depends only on position. A substituted plaintext or ciphertext
symbol changes one observed pair, so the deletion test covers an unknown
single substitution at an observed position. An error elsewhere leaves the
observed constraints unchanged. This does not cover insertion/deletion, a
lost state update, changed observation positions, or two errors at different
observed positions. The exact conclusion is independent of the language of the
unobserved text.

## Synthetic validation

The forward oracle advances a counter and rotor angle explicitly, independently
of the checker's floor-expression coordinate calculation.

| Check | Result |
| --- | ---: |
| Every four-symbol plaintext/ciphertext pair, every wiring, q=2,3,4 and four phased schedules | 289,412 comparisons; all exact and deletion outcomes agree |
| Full-size plants across all registered labels | 320/320 pass and round-trip |
| Single plaintext substitutions, altered text re-encrypted | 31,040/31,040 pass the propagation/deletion check |
| Single ciphertext substitutions | 31,040/31,040 pass the propagation/deletion check |
| Identity-second-rotor embeddings | 1,280/1,280 agree |
| Translation-wiring overlap examples | 320/320 agree |

The 24-position synthetic mask was independently sampled, with endpoint
coverage; it was not the published K4 mask. Composite modulus 4 is included
in the exhaustive oracle. No division or primality assumption is used.

An initial successful synthetic record is preserved as
`SYNTHETIC_PRE_HISTORY_CLARIFICATION.json`. Before any target execution, a
history assertion was corrected to reflect that the original exact and
cross-check results were published together. The mathematical kernel did not
change. The final source was synthetically revalidated, then published before
the sole target run. This was not a target retry.

## Saved blind evidence: what was and was not independently checked

All **1,010 gate candidate witnesses and 1,005 target/null candidate witnesses**
independently re-encrypt to their recorded 97-letter input using an advancing
counter implementation. IDs, wiring permutations, structural domains,
best/top consistency and saved-score ordering also agree. All 52 positive and
extra truth cases pass their appropriate independent forward check, including
the two explicitly corrupted-ciphertext cases.

The saved gate arithmetic reproduces:

| Measure | Independently recounted result |
| --- | ---: |
| Confident recovery at >=95/97 letters | 47/48 |
| Confident exact 97/97 recovery | 44/48 |
| Six clock cells | 8, 8, 8, 8, 8, 7 of 8 |
| Three genres | 15, 16, 16 of 16 |
| Masked controls | 11/12 |
| Structural setting equal to the builder's label | 48/48 |
| Wiring agrees on every true used contact | 44/48 |
| Confident negatives | 0/150 |
| Reported extras | 4/4 recovered; plaintext-error cases exact, ciphertext-error cases 96/97 |

The frozen GO follows from the registered thresholds. These are results on
the recorded sampled controls, not universal recovery of every wiring or
perfect discrimination between mathematically overlapping families.

The saved target arithmetic also reproduces: **50/200** shuffle maxima are
at least K4's retained score, so the add-one value is **51/201 = 0.2537313433**.
The recorded best has 0/24 observed-letter matches; the retained top five reach
at most 2/24; there are zero contenders. The unchanged blind outcome is
**NO_SIGNAL**. All 200 previously frozen shuffles were reconstructed byte for
byte from seed 920400.

The pipeline first anneals all 192 labels using quadgrams, retains 48 for its
second anneal and LM rescoring, then LM-polishes five candidates. Therefore
its reported maximum is a **retained-pipeline maximum**, not the LM optimum
over all 192 labels or all wirings. The identical-pipeline null comparison is
the appropriate interpretation of the saved p-value. The source's statistic
named `null_best_lm_median` is its upper-middle order statistic for 200 nulls;
that diagnostic does not enter the outcome rule.

**No original optimizer, LM rescoring or runtime isolation was rerun.** The
untracked full LM binary is unavailable to this audit; its two runner hash
commitments agree with the pinned expected hash, but the actual binary bytes
were not rehashed. Raw book freshness and training overlap were not independently
certified. There are three plaintext books and one running-key book, rather
than four plaintext sources. All such limits are separate from the exact proof.

## Frozen evidence, chronology and resources

The audit verifies **101 manifest entries** across the protocol, both stage
freezes and both runner manifests, including original source/data bytes at
the baseline and relevant historical freeze commits. The truth commitment
matches; truth is absent from the gate-freeze tree, and evaluation is absent
from the target-freeze tree. Recorded sandbox allowlists and input hashes
agree with the frozen artifacts.

| Original stage | First public commit |
| --- | --- |
| Preregistration | `14494aa03b6809f125a2b0f3048965f180201b6a` |
| Hidden-control inputs/commitment | `78142bc83bf70ab1369daf5a13411e4493ea2641` |
| Gate outputs frozen | `92ba8ed3ec4b1e3cec6ceafa676d40ace5685d02` |
| Gate truth/verdict | `d07938476dfc9ee30c22b628f7e2c49ba503d722` |
| Target inputs | `f77cad6db229369433501199ddea3b3173cc67e1` |
| Target outputs frozen | `25026ff942d78e70ecc7fa8c351234d163bd487c` |
| Target evaluation | `456d401998500cafe1680d62114a182cc62cddec` |
| Exact and original cross-check results together | `1fc9bb3dae69a5ba20273a6351eb5c180e1d4632` |

Git verifies these commit relations; it cannot independently establish the
instant of a historical push or the first local read of clue material.

The recorded formal gate and target runs are COMPLETE within their registered
7,200-second wall / 28,800-second aggregate CPU / 4,096-MiB limits. Their
recorded wall/CPU times are 966.490/1,906.165 and 1,021.598/2,012.818 seconds,
respectively, with sampled aggregate peaks of 2,563.6 and 2,563.0 MiB.

The original development run exceeded the earlier synthetic-work budget,
as disclosed in the preregistration. That remains a deviation; this review
does not retroactively certify it as compliant. The QA candidate ceiling of
1,005 describes the target panel; the explicitly declared 202-input gate has
1,010 retained candidates.

This audit's plan was committed and pushed at
`76d9a013c3dd3c2aff9c0144c8a9ebf22ba6d361`; its checker and final synthetic PASS
were committed and pushed at `567f418961cc18847207008468679115074f4c93` before
the target job. The checker verifies its own published source and plan before
accessing target evidence.

| Audit job | Status | Wall seconds | Aggregate CPU seconds | Sampled aggregate RSS, MiB |
| --- | --- | ---: | ---: | ---: |
| Final synthetic controls | COMPLETE | 3.756 | 3.571 | 13.7 |
| Single target/saved-evidence audit | COMPLETE | 1.754 | 1.628 | 34.8 |

The target job used the registered 300-second wall / 180-second CPU /
1,024-MiB cap and had **zero retries**. Summed RSS can count shared mappings
more than once and miss peaks shorter than the 0.25-second sampling interval;
the wrapper also applies its per-process address-space bound.

## Required additive corrections and remaining scope

`SCOPE_CORRECTIONS.md` records the source-level corrections in detail:

- RX2-O with identity second wiring embeds the phased RXP subfamily too.
- Distinct clock schedules do not imply disjoint function families.
- Remaining nonzero phases for n=5..96 number **145,728**, not 145,920.
- The blind statistic concerns the fixed pruned pipeline; exact contradiction
  does not depend on an English-language assumption.

Those wording defects do not invalidate the independently reproduced exact
contradiction. Arbitrary two-rotor models, different contact alphabets,
different stepping, transposition, and errors outside the declared model remain
untested by this review. No R92 survivor, score, key or ranking may feed RX2
candidate generation.

## Evidence hashes

| Artifact | SHA-256 |
| --- | --- |
| `review92.py` | `f5e84c7514fe3744e5b03fb527e2a67a73710f8c48b4cd43792c83294f78123c` |
| `SYNTHETIC.json` | `a5afdfe3d9c34be0cfa97ff37c7b058faf52fdecd0500d8d90a30d57795a73f8` |
| `REVIEW_RESULTS.json` | `dcc0f936262fff82e749acbc8a7a04f200cc806e1f7ef5d46fac68ee21d9bec4` |
| `REVIEW_RESOURCE_LOG.json` | `e56a6cf8d452b6e2c682f7b2d1e471b87458a56f70e0ca5f60edcb42526da7d5` |

**Signed: ChatGPT — independent mathematical and code-path review of Claude
Code's R92, with complete aggregate replay at the stated finite scope.**
