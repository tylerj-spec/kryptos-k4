# R95 internal breaker notes

Date: 22 November 2026 (America/Chicago).

Status: completed pre-execution source review. Existing assets, preregistration,
work order, both implementations, metadata checks, budget/QA/model specifications,
model-rebuild source, execution handoff, and CI workflow were reviewed.
No R95 score comparison, optimizer, fresh
control generation, or K4 computation was executed by this reviewer.

Reviewer: ChatGPT subagent, same model/team as the builder and root. This is
internal adversarial review, not independent-model certification.

## Verified existing assets

- Candidate K=5: `/workspace/scratch/4f425b909cf8/backlog_gate_dev/r59_rebuild/lm5.bin`,
  49,426,528 bytes, SHA256
  `e9c0848f5e256814387968c09006a44804e90a72aeb79034d0b12abfcce31abd`.
  Header is `R59LM`, byte 5, two zero pad bytes; length equals eight header bytes
  plus four bytes per entry in the five dense 26-ary tables.
- Baseline K=4: repository `r91/R59_LOWER4_FROM_K5.bin`, 1,901,024 bytes,
  SHA256 `85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41`.
  All baseline table bytes exactly equal the corresponding candidate prefix.
- Normalized training file:
  `/workspace/scratch/4f425b909cf8/backlog_gate_dev/r59_rebuild/corpus/train.txt`,
  23,373,369 bytes, SHA256
  `871627e5fd2f84b4afa976516303098f437b5c339b7297db238fcd1ecb0e0434`.
  This matches the archived build receipt.
- `r59/blind/lm_build.cpp` SHA256 is
  `87b521d7654c07ead5b3bdbaa1da24c5ff60f10ae95b8f9aa8cf83673e2fc915`,
  matching the archived build receipt.
- R94 panel TSV SHA256 is
  `9b3ed6b49d437d4289f2a1126dd79b61ed7158b0e35b408bb39b1409aab8786c`;
  public synthetic truth SHA256 is
  `27aecaf0aa2050e12d0d05e6c2ccc84b0598acd170e3e47f8667718732cf6ebf`.

These are local existence/hash/format checks. They do not independently
rebuild the language model or score any panel message.

## Model semantics that must remain explicit

The candidate's top order five uses raw five-gram counts. The unavailable old
K=6 model's order five used continuation counts from order six. The rebuilt
K=5 binary is therefore a **new candidate score**, not a historical v3 score
replay. Its orders one through four do match the baseline by bytes. The
archived `BUILD_RECEIPT.json` model digest describes the lower4 output, not
the full 49 MB K=5 file; R95 must pin the latter's separate digest.

The builder stores float32 log10 probabilities in oldest-letter-first base26
index order. Scoring should accumulate in float64: order one at position 0,
order two at position 1, etc.; thereafter the maximum selected order. Use sum
log10 scores consistently when applying the fixed 1e-9 tolerance. No division
by 97 on only one code path.

## Scientific scope and failure traps

1. The primary endpoint is **ANY** wrong plaintext below 95 matches whose score
   is greater than truth+1e-9. The earlier25 cases with a below 95 *best saved*
   neighbor are not necessarily the complete count for this endpoint.
2. Keep all 650 legal swap labels per case, including observational aliases.
   Also count distinct plaintexts. Neither the 31,200 labels nor the distinct
   texts constitute independent statistical trials.
3. A candidate with 97 matching letters is the same observed plaintext even if
   its rotor key differs. It is not a wrong-text score error. Calling it a
   globally equivalent cipher is also unwarranted: a nontrivial transposition
   in exactly one wiring changes the full per-position bijection, though the
   observed97 inputs may not visit affected contacts.
4. Report strict wins, ties within 1e-9, and losses separately for below 95,
   95–96, and 97-match groups. Exact-text and >=95 criteria answer different
   questions; do not silently substitute one for the other.
5. A <=2/48 result is an engineering continuation bar only. It establishes
   neither global score adequacy, conditional optimization success, blind
   recovery, unknown-method identification, nor false-positive control.
6. The neighborhood is all single transpositions of the *true* two wirings.
   It is a fixed local challenge, not the full keyspace or an independently
   found candidate set. Truth-assisted construction must be disclosed.
7. All 48 truths and earlier outcomes were publicly available and repeatedly
   used. This remains spent-data development whatever the result.
8. The panel's recorded source titles are Rebecca of Sunnybrook Farm, The
   Prince and the Pauper, The Railway Children, and Anne of Green Gables.
   They do not appear among R59's 14 named training novels, but R59 also uses
   NLTK bundles and Carter/Mace. Title comparison alone is not an empirical
   non-overlap certification. An exact normalized 97-letter substring check
   can be registered as provenance, with its narrow interpretation.

## Implementation checks required before execution

- Hash and shape-check both models, exact lower4-prefix equality, all required
  input/protocol/source files, expected package versions, and finite tables.
- Validate all 48 input/truth IDs and supplied labels, six per turnover cell,
  two 26-element permutations, 97-letter strings, and forward/inverse witnesses.
- Enumerate each rotor then each ordered index pair i<j exactly once; retain
  swap metadata permitting independent reconstruction of all 31,200 records.
- Exclusive-create output directory/files; a refused repeat must not overwrite
  evidence from the first attempt, including failure logs.
- Use one bounded invocation for integrity checks, scoring, witness checks,
  summaries and output writing. Freeze explicit limits and zero automatic
  retries. An exception, mismatch or exceeded bound is INCOMPLETE.
- No source edits, alternate score weights, extra model versions, filtered
  subsets, or score-dependent reruns after execution starts.

## Recommended independent code-path audit

A standard-library checker should read little-endian float32 values with
`struct`, recompute every score by a scalar rolling base26 index, reconstruct
both swapped wirings, and independently encrypt/decrypt every saved text.
It should recompute every per-case/per-cell/global count and deterministic
best witness from the complete records, verify the 650-label catalog, and
check complete artifact manifests and aggregate resource logs. It must not
import the builder's score, encryption, classification, or aggregation helpers.

This yields a second implementation within one model; independent-model
review remains NONE. No K4 exclusion or solution can follow from R95.

## Prospective preregistration and work-order review

The initial `r95/PREREGISTRATION.md` and `WORK_ORDER.md` were read before
publication. Their finite cipher equations and manually checked three-contact
worked example are correct. The supplied sample, new-candidate identity,
ANY-below 95 endpoint, epsilon comparison, no-adaptation rule, provenance
diagnostic, public output freeze, and limited continuation interpretation
address the principal scientific risks above.

The primary 300-wall/240-CPU/1,024-MiB and verifier 300-wall/240-CPU/512-MiB
limits sum to 600 wall / 480 CPU across one invocation each. This is an explicit
engineering resource allowance unrelated to the user's 25-meter phrase. No
fresh holdout, K4 evaluation, or conditional optimizer is silently authorized.

One prospective clarification was requested: define selected-witness tie
breaking as the exact numerical maximum with first enumeration index for
equal scores, and reserve the 1e-9 tolerance for comparison to truth. This
avoids ambiguity from non-transitive approximate ties. Also ensure both
implementations enumerate inverse-wiring swaps U then V, as registered;
forward swaps cover the same neighboring permutations but have different
labels and order. These are pre-execution specification clarifications,
not result-driven changes.

## Completed primary implementation review

Read `r95/score_challenge.py` without executing or importing it. The source
matches the registered inverse-U-then-V catalog, signed clock conventions,
input/output alphabet definitions, forward/inverse equations, and all 650
legal swaps per case. It verifies true-key recovery and complete forward
witnesses for the true text and every neighbor. Its batched base26 model
indices and float64 score sums handle prefix orders correctly.

The primary ANY-below95 endpoint, exact-text aliases, near-wrong and below95
groups, epsilon comparisons, raw-score witness maximum and first-label tie
break are implemented consistently. All labels are retained. Per-category
`wins`, `ties`, and `losses` are **label counts**. `distinct_plaintexts` counts
all unique texts in that category, not unique winning texts; narrative must
not compare labeled wins to the earlier R94 count of distinct winning texts.
The primary case-level endpoint does not depend on duplicate multiplicity.

Input/model/protocol digests, model format/finite values, lower-table byte
equality, expected 48-case coverage, six-per-cell balance, legal permutations,
and fixed 97-letter length are checked. The training substring diagnostic
cannot remove a case or alter the decision. Outputs use exclusive creation;
a refused repeated directory cannot overwrite first-attempt evidence.
Per-case shard and aggregate byte caps prevent unbounded retention. The
summary remains provisional pending the separately bounded verifier.

Runtime versions are recorded rather than restricted to one NumPy release.
This portability choice is accepted: scientific inputs are fixed float32
table bytes, accumulation is float64, and a separate standard-library
implementation must agree on scores, witnesses, counts and decision.

## Completed manifest and reconstruction review

Read `QA_MANIFEST.json`, `MODEL_SPEC.json`, `REVIEW_BUDGET.json`,
`CI_REBUILD_BUDGET.json`, and `rebuild_model.py`. Independently checked that
all five MODEL_SPEC paths/digests for builder, corpus builder, acquisition,
Carter, and lower4 match current bytes. QA's preregistration digest also
matches. The synthetic-truth mode is explicitly distinguished from K4 crib
use; the QA record authorizes no K4 run or fresh gate.

The 600-wall/480-CPU primary-plus-review resource total agrees across the
specifications. The CI dependency reconstruction is separately bounded and
cannot renew the primary run allowance. It imports only the pinned corpus
builder, reads no panel, and reconstructs the same pre-existing model. All 19
acquisition entries have relative non-parent paths and approved public raw
source URLs. Their recorded largest source is 4,251,829 bytes, below the
20-MiB single-download cap. Reconstructed training/model digests and the
baseline table prefix must match exactly, otherwise reconstruction fails.
Compiler/platform differences are not permission to substitute another
candidate model or relax a digest after observing performance.

## Verifier mathematical review and final metadata check

Read `verify_score_challenge.py`. It imports neither the primary implementation
nor the earlier cipher/scorer. It independently reconstructs each inverse
swap as a forward-output-value transposition; inversion finds the unique
preimage in the forward wiring. Its scalar rolling suffix indices implement
the stated score. It reconstructs every true and neighboring plaintext,
checks complete forward witnesses, both scores and margins, and re-derives
all cases, categories, cells, summaries and deterministic best witnesses.
No mathematical blocker was found.

Before source freeze, the verifier was amended and reread. Its numeric
verification tolerance now matches the registered 1e-8, while the scientific
comparison remains 1e-9. It checks recorded score against independently
computed truth, against the reported truth score, and via the recorded margin;
any classification disagreement fails the review. SUMMARY status, mode,
case/score counts, score order, epsilon, continuation bar and provisional
decision metadata are checked. RECEIPT source/protocol/input/model/training
pins and inventories, model sizes, requested thread count, zero optimization/
restart/retry fields, retention metadata, and runtime-field types are checked.
The canonical protocol path and registered reviewer source pin are required.
The earlier metadata gap is resolved prospectively.

Resource logs and publication ancestry are separate root-level checks; the
scalar scientific verifier does not purport to reconstruct historical process
isolation or independently measure peak RAM. Internal review remains one
model throughout.

## Handoff, CI, and final source decision

The handoff commands invoke the primary and verifier under their respective
registered aggregate wrappers, with fixed external input digests and fresh
output directories. The CI workflow reconstructs the exact model/training
dependency and executes the saved-evidence scalar review. It does not invoke
the primary producer, optimizer, or a new K4 computation. The verifier's
machine report deliberately omits environment-specific timings and paths
so the CI comparison can be byte-for-byte. Resource logs remain separate.

The following source digests identify the final implementations read here:

| File | SHA256 |
| --- | --- |
| `r95/PREREGISTRATION.md` | `b91449d0e1131ddbdd0434aaf1e261efcce1b86a9a69b86438a7446477778c7d` |
| `r95/score_challenge.py` | `4f3c83810da0320f3044fe23612301b7488c100b5eb57d98e0bc72ade4ecf3a7` |
| `r95/verify_score_challenge.py` | `8bde21759f97af3812d0df766acc4d593c75e1ffc08f645d578d1608edafa658` |
| `r95/rebuild_model.py` | `efe2af5b7c55043decb9913e4338d9e7bcfd63a4c2808d075dfba15339102ca7` |

**Decision: no remaining pre-execution scientific or source-review blocker
found for this narrowly defined development diagnostic.** This decision is
conditional on publication of these reviewed sources and complete protocol
pins before the primary invocation. It is not an empirical test result,
independent-model promotion, global objective certificate, or permission
to advance directly to K4. The actual run and separate saved-evidence review
must both complete under their fixed limits before a development verdict
is accepted.

Signed: ChatGPT internal breaker — read-only review; no experiment execution.
