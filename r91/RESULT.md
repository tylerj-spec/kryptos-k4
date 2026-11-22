# R91 result: both archived bounded solver attempts lack required power

**Terminal outcome: `SOLVER_NO_POWER` for both arms, and NO-GO for advancement of these broad bounded solver attempts.** Neither arm satisfies the preregistered necessary recovery screen. No K4 experiment was run or authorized, and both cipher families remain OPEN.

This is a completed fresh synthetic experiment, not an unfinished build or a renamed pending item. All 600 candidate records were produced, frozen and checked before truth was opened. Every returned message/key pair reproduces its ciphertext; recovery against the true message/key is the separate criterion below.

## Fixed decision and aggregate result

The gate required at least **18/20 exact 97-letter messages with the true or proved-equivalent key in every declared stratum**. True structural settings were supplied while messages and keys were hidden. The algorithms, scoring, seeds, effort and one-key-per-branch retention were fixed before holdout generation.

| Arm | Exact message + key | Passing strata | Required | Decision |
|---|---:|---:|---|---|
| R82 linked tableaux | 250/360 | 8/18 | Every stratum ≥18/20 | `SOLVER_NO_POWER` |
| R68 plaintext autokey | 32/240 | 0/12 | Every stratum ≥18/20 | `SOLVER_NO_POWER` |

The ≥95-letter diagnostic equals exact recovery in every stratum. There were no cases rescued only by the relaxed letter diagnostic and no nonidentical equivalent keys that changed a decision. These diagnostics did not replace the fixed criterion.

## R82 linked-tableau results

The unchanged archived factor-graph solver used its fixed unigram objective, 12 restarts, 100 stochastic coordinate updates per restart and at most seven greedy sweeps. It was supplied the correct key length and width for AZ→KRY followed by AZ→AZ.

| Key length m | Width w | Exact message + key | ≥95 letters | Stratum |
|---:|---:|---:|---:|---|
| 3 | 3 | 20/20 | 20/20 | PASS |
| 3 | 5 | 20/20 | 20/20 | PASS |
| 3 | 31 | 20/20 | 20/20 | PASS |
| 4 | 4 | 20/20 | 20/20 | PASS |
| 4 | 6 | 20/20 | 20/20 | PASS |
| 4 | 31 | 20/20 | 20/20 | PASS |
| 5 | 5 | 17/20 | 17/20 | FAIL |
| 5 | 7 | 19/20 | 19/20 | PASS |
| 5 | 31 | 20/20 | 20/20 | PASS |
| 7 | 7 | 13/20 | 13/20 | FAIL |
| 7 | 9 | 14/20 | 14/20 | FAIL |
| 7 | 31 | 17/20 | 17/20 | FAIL |
| 9 | 9 | 10/20 | 10/20 | FAIL |
| 9 | 11 | 9/20 | 9/20 | FAIL |
| 9 | 31 | 8/20 | 8/20 | FAIL |
| 12 | 12 | 1/20 | 1/20 | FAIL |
| 12 | 14 | 1/20 | 1/20 | FAIL |
| 12 | 31 | 1/20 | 1/20 | FAIL |

The six m=3 and m=4 cells recovered all 120 cases. Recovery then fell to 56/60 at m=5, 44/60 at m=7, 27/60 at m=9 and 3/60 at m=12. Ten of the 18 declared cells failed. The broad baseline attempt therefore cannot advance. The successful small-key cells are useful development evidence for a future narrower proposal; they are now spent and do not establish unknown-family recognition.

## Archived PTAK results

The original R68 primer optimization was preserved: 20 restarts, at most 20 coordinate sweeps, the original convention indexing and seed formula, and the order-four score reconstructed from the pinned R59 corpus/builder. The correct path, M1/M2 model, alphabet convention and lag were supplied.

| Primer lag | Exact message + primer | ≥95 letters | Stratum |
|---:|---:|---:|---|
| 13 | 11/20 | 11/20 | FAIL |
| 14 | 10/20 | 10/20 | FAIL |
| 15 | 6/20 | 6/20 | FAIL |
| 16 | 1/20 | 1/20 | FAIL |
| 17 | 3/20 | 3/20 | FAIL |
| 18 | 1/20 | 1/20 | FAIL |
| 19 | 0/20 | 0/20 | FAIL |
| 20 | 0/20 | 0/20 | FAIL |
| 21 | 0/20 | 0/20 | FAIL |
| 22 | 0/20 | 0/20 | FAIL |
| 23 | 0/20 | 0/20 | FAIL |
| 24 | 0/20 | 0/20 | FAIL |

Every lag cell failed. Lags 13–15 recovered 27/60 cases; lags 16–18 recovered 5/60; lags 19–24 recovered 0/120. These results close this archived long-lag solver attempt at its declared effort. They do not exclude plaintext autokey as a cipher family or show that a stronger optimizer would fail.

## Why this closes the bounded attempts

The proposed advancement rule requires each true structural branch, using the same fixed seeds, objective, effort and single retained key, to satisfy this positive-recovery screen. A later reranker cannot retrieve a key already discarded by that branch. Both attempts fail that prerequisite even when true structure is supplied, so the corresponding full-method gate is terminally **not eligible** for these bounded attempts.

This reasoning does not establish that every unknown-structure classifier must fail: another equivalent branch might return the right text, and a different optimizer, beam, seed schedule or effort defines different work. No wrong-family false-positive rate is estimated because the preliminary positive-recovery stage failed before an unknown-family/negative-control gate became eligible. There is no statistical or exact K4 exclusion here.

## Execution and chronology

| Published stage | Commit |
|---|---|
| Preregistration | `61affb205c85509d713951bfe58fc4a6ee85ef84` |
| Bound source, model, protocol and QA | `e9ee84906a4680cdf1b5a43dcd40a03fc46e9b22` |
| Public inputs and truth commitment | `552022dbe551181da96a525d8afbbedb38c79a94` |
| Complete output freeze, before truth opening | `600747049a1537378e7843d93b356ddbe8d4390a` |

The coordinator confirmed each stage was committed and pushed before authorizing the next stage. The output-freeze tree contained all 60 pinned artifacts and no truth or result. The evaluator verified the complete freeze and truth commitment before reading truth. Its fixed structural, resource and witness assertions all passed.

The fresh data used 200 nonoverlapping 97-letter windows from each of the three preregistered books. The generator rejected exact 97-letter overlaps with the reconstructed R59 training corpus and duplicate messages. The controls do not certify power on other languages, masking, corruption, other chart settings or other parameter ranges.

| Formal operation | Status | Wall seconds | Aggregate CPU seconds | Peak sampled aggregate RSS, MiB |
|---|---|---:|---:|---:|
| Generation | COMPLETE | 4.770 | 4.542 | 40.5 |
| R82 kernel | COMPLETE | 10.774 | 11.565 | 24.8 |
| PTAK kernel | COMPLETE | 7.523 | 7.342 | 3.7 |
| Forward witnesses | COMPLETE | 0.252 | 0.069 | 0.1 |
| Truth evaluation | COMPLETE | 0.255 | 0.132 | 0.1 |

Each operation had a cap of 1,800 seconds wall, 1,800 seconds aggregate CPU and 2,048 MiB RAM. Memory and CPU monitoring were sampled over the process group; the wrapper also imposed a per-process address-space limit. Short-lived memory peaks can fall between samples. Each candidate arm ran once, with zero retries.

The candidate kernels enforced their file/network isolation probes before searching. The scalar public-input verifier reproduced all 600 ciphertexts before truth opening. Compiled-binary hashes, compiler commands and runtime versions are recorded in `holdout/run/BUILD_RECEIPT.json`; no untracked binary path is asserted as a committed freeze entry.

The lower-order model equality follows from the unchanged builder and identical pinned corpus: orders 1–4 depend on raw counts through order 5 and lower-order recursion. No byte comparison with the unavailable historical full order-six binary was performed, and the full historical unknown-family classifier was not replayed.

## Audit status and artifacts

One ChatGPT execution team performed this round. The separate internal source review is documented in `INTERNAL_SOURCE_REVIEW.md`; it is same-model review, not independent-model execution review. Independent-model execution review remains **NONE**. Any further separately coded recomputation should be recorded as an additional verification artifact without changing the frozen source, QA or outputs.

Core evidence: `PREREGISTRATION.md`, `PROTOCOL.sha256`, `holdout/INPUTS.sha256`, `holdout/FROZEN.sha256`, both complete output JSONL files, `holdout/run/WITNESSES.json`, `holdout/TRUTH.json`, `RESULT.json` and the resource logs. The revealed truth matches SHA-256 `2ece5a84dfdaa644a43ab5829e4f300e773ebb26d294f1e7cb9ee16d530cb5b7`.

`QA_MANIFEST.json` remains at its frozen pre-reveal state, with `gate_verdict: PENDING_TRUTH_REVEAL`; the post-reveal decisions are in `RESULT.json` and this report. That immutable state is deliberate.

## Terminal backlog recommendation

- Close the **R82 broad linked-key baseline gate attempt** as `SOLVER_NO_POWER`; do not describe generic fractionation catalogs as having tested this linked-key mechanism.
- Close the **archived R68 long-lag PTAK solver gate attempt** as `SOLVER_NO_POWER`.
- Keep both cipher families and materially different algorithms OPEN. Do not add a K4 exclusion or promote an independent-verification label from this round.
- Treat any narrower small-key linked-tableau classifier, stronger PTAK optimizer, altered seed schedule or larger retained candidate set as a new preregistered proposal requiring new untouched controls. R91 controls are now spent.
