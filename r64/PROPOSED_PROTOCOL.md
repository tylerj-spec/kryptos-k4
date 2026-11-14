# R64 proposal — non-English running key followed by a physical transposition

**Status: REVIEW-ONLY DESIGN PROPOSAL. Not a frozen preregistration, not a K4 run, and not a solve.**
Before launching any holdout or K4 run, implementation, fixtures, score definitions, thresholds, source hashes, and random seeds must be finalized and committed to a *new*, unaltered preregistration. This proposal changes no R59/R61/R63 findings and no active workflow.

## Motivation and bounded hypothesis

R63 (L152) found NO SIGNAL for the in-place World Clock-city-name model (81/100 frequency-preserving nulls >= K4) and German-prose model (27/100 >= K4), after passing 10/10 controls for each model. R61 (L150) found NO SIGNAL for **English** running-key output then transposed through 10 historically specified routes (5/100 nulls >= K4). These do **not** cover their composition.

**R64-A hypothesis:** plaintext is ordinary English, key is a CLOCK or GERMAN stream of the exact frozen R63 model type; encrypt letterwise with AZ or KRYPTOS numbering and Vigenere/Beaufort/variant-Beaufort; **then** transpose through exactly one of the ten fixed routes in `r61/routes.txt`. No extra routes, free alphabets, unknown padding, reverse layer order, numeric-key source, or source-informed semantic filtering are included.

The R61/R62C COL_LT stage-one gap is an interesting *post-selected* ciphertext-only observation (fresh nulls 2/300 >= historical gap; plus-one tail 3/301), **not** a validated route. R64 must search/calibrate all ten frozen routes symmetrically; do not tune the route shortlist from K4, and do not treat the original gap as an independent prior or a fresh p-value.

## Implementation proposal

1. Read `r61/routes.txt` unmodified; check each is a length-97 permutation. For route `p`, use `CT[j] = X[p[j]]`, where `X[i]` is the pre-transposition ciphertext. Undo each route *before* calling the unchanged R63 two-language solver (`r63/blind/rk2_solve.cpp`).
2. Per route and model, use a lower-budget **ciphertext-only** stage-one pass (no polish) to rank all 10 routes. Then run the unchanged full R63 parameters on the best two *per model*. Route retention on held-out plants must be a separately reported power measure. Fix the stage-one budget and all tie rules after development **before** pre-registration; do not choose it from K4.
3. Keep both CLOCK and GERMAN analyses separate. Stage-two score is the R63 joint plaintext/key model total, not any known-K4-letter match, guessed plaintext, hand interpretation, or external answer checker.
4. Record **all ten stage-one raw 97-letter plaintext/key witnesses, stage-two raw alternatives, model/convention/route/score, input ciphertext, exact route mapping and model/binary/source hashes**, for every plant, control and K4 case. Do not silently prune raw evidence, and reject a stale cache unless the ciphertext, source hash, model hashes, route hashes, and parameter digest all match.
5. Independent postfreeze verifier must reconstruct the forward encryption, including the final permutation, for *every* saved 97-letter witness; validate raw-file hashes and remote Git tree contents. The postfreeze evaluator must be separate from the candidate generator.

## Control design: power before K4

**First complete development work on fresh, non-K4 sources**, then commit a final preregistration and source hash **before** generating unseen holdout plants. The preregistration must fix counts, seed, model/route budgets, score definitions and pass/fail bars; it is not legitimate to set these from K4. 

- Use fresh 97-letter **ordinary English messages with no K4 clue phrases or known original K4 plaintext**. Hide exact message/key/route/convention truth from the solver. Do not author synthetic messages around published clues, unlike the four numeric-key R63 fixtures (those were sealed controls, not K4 inputs, but their wording reduces independence).
- For CLOCK, include both randomly ordered city-name keys drawn from the frozen 107-name R63 vocabulary and an out-of-distribution *deterministic walk* through a photo-derived ring, with caveats that the true historical inscription sequence is not verified. For GERMAN, include an unseen-genre German source (independently pinned and hashed); avoid training/test overlap with Europarl. These out-of-distribution controls test whether R63's good in-model gate generalizes to real physical/text sequences.
- Use fresh frequency-preserving shuffled ciphertext controls from the same construction. Independently reencrypt each hidden control to verify it was correctly generated.
- Report model detection (heldout model score > max null under same search), route correctly retained top two, correctly identified convention, true plaintext letter recovery out of 97, and whole-chain encryption witnesses. If power is inadequate, report **INCONCLUSIVE** and **do not run K4**. Do not relabel such a failure as exclusion.

## Conditional K4 sequence

Only after passing the finalized hidden holdout gate:

1. Make an unchanged-copy input of the original 97-letter K4 ciphertext, assert its byte SHA256 (including newline) equals `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`; include at least 100 previously unseen frequency-preserving permutations created with the predeclared seed.
2. Run each target/null identically. Freeze complete raw 97-letter output and every source hash and **push a successful remote Git commit** before revealing *any* published clue letters or accessing any external checker.
3. Independently verify all complete forward witnesses from the frozen inputs and frozen source. Preserve all failures, nondeterminism and cache problems.
4. **Only then** run the separate published-letter evaluator on the frozen target outputs. The primary decision rule must already be fixed in the preregistration and must use a statistic calibrated against the same per-case route+model search on nulls (including the look-elsewhere cost).
5. Never fit guessed plaintext, a key, route, score, model, or hyperparameters to the revealed letters. A partial match is not a solution. To claim genuine K4 recovery require substantial coherent *new* English, an independently derived key and physical method, complete forward encryption and independent confirmation.

## What a negative result would and would not mean

A well-powered negative would argue against this **ten-route, substitution-then-transposition, ordinary-English plaintext, two fixed non-English key-model** family. It would **not** exclude transposition-first-then-substitution, hour/UTC-offset key encodings, different clock inscriptions, irregular/interrupted keystreams, two free alphabets, non-English or deliberately altered plaintext, a general masking layer, a true one-time pad, or arbitrary mechanical transformation.

If this restricted combination also fails with demonstrably high holdout power, prioritize a separately preregistered **masking-method identification** program rather than incrementally enlarging key dictionaries without a falsifiable construction.

## Sources and independence cautions

- `r63/RESULT.md`, `r63/PREREGISTRATION.md`, `r63/k4/INDEPENDENT_AUDIT.json`, R63 remote freeze `2d043af`.
- `r61/PREREGISTRATION.md`, `r61/RESULT.md`; `r62c/PREREGISTRATION.md` (PR #43).
- `r53/BLIND_RULES.md`: known K4 plaintext is validation data, never generator input.
- R63 numeric postfreeze `WHOLE_FAMILY.json` checks 92.9 million *fixed family settings* against published letters, but **only the top 100 outputs per key stream** were saved as raw full-length candidates. Describe that finding as an exact bounded family check, **not** as 92.9 million independently frozen full-text candidate outputs.
- R63's postfreeze audit JSON has `verified_remote_git_freeze: false`, indicating that the audit program itself does not attest Git provenance. The separate remote commit and parent/commit chronology must be checked, as done for R63. Do not convert this flag into an audit failure or silently treat it as verification.

**No published K4 clue text or offsets occur in this proposed generator spec. No K4 candidate is produced by this document.**
