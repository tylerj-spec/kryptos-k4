# R91 internal source and mathematical review

Reviewer: ChatGPT, a second internal task within the same execution team. This is **same-model internal review**, not independent-model review and not a second council vote. No fresh holdout truth was generated or inspected for this review. No K4 input was read.

## Finding

The proposed screen is a reasonable preregistered eligibility test of the two pinned solver attempts. The cipher equations, supplied-structure interfaces, key-equivalence rule and preserved PTAK optimization are consistent. Neither a pass nor a failure is a K4 result. The distinction between per-branch recovery and complete unknown-structure recognition must remain explicit in the eventual result.

## Necessary-screen qualification

Fix a structural branch, its input-dependent seed, effort, objective and one returned key. If that branch discards the correct key, reranking that single retained result cannot recover the discarded key. Supplying the correct branch is therefore an appropriate screen for the declared **per-true-branch recovery requirement**.

This does not prove that every broader classifier must fail on the same input: another equivalent structural branch might return the true text, or a different optimizer, beam, seed schedule or effort could recover it. The preregistration expressly excludes those claims. A failure should be reported as the bounded solver attempt failing this mandatory eligibility rule, not as a theorem that its cipher or all unknown-structure classifiers are unrecoverable.

Passing all strata gives only `SCREEN_PASS_ONLY`; hidden-structure recognition, wrong-family rejection and K4 authorization do not follow. The absence of wrong-family negatives in this preliminary stage is compatible with rejecting a solver that fails the mandatory positive-recovery condition. It cannot establish false-positive calibration if the stage passes.

## PTAK adaptation preserves its key choice

I compared `vendor/r68/keyed_solve.cpp` with `ptak_r68_screen.cpp` and the eight checked replacements in `derive_ptak_screen.py`.

- The 1,274-byte body beginning with the CTAK/PTAK candidate initialization and ending before `finish(b)` is byte-identical. SHA-256 of that body: `abdfed2adf356e960abf4d3fab04b9c1f7b4fa4753702ba1757d659955ded328`.
- The primer reconstruction, coordinate loops, strict-improvement rule, 20-sweep limit, best-key retention and `mt19937_64` are unchanged.
- The complete convention vector remains intact, so filtering to the supplied convention does not change the convention index used in the RNG seed. The family index remains1 for PTAK. The supplied lag enters the same seed formula.
- Periodic and Gromark work is disabled. Those branches do not share the PTAK generator; removing them does not change its random sequence.
- The order-six and word scoring occurs in the old `finish(b)` **after** the branch's single key has been chosen. Replacing that final score with order four changes downstream ranking fields, but cannot change the within-branch key being tested. This is not a replay of the full historical classifier.
- The public-row conversion correctly maps the ciphertext back into path order and uses identity layout for M1 and the supplied permutation for M2. The scalar forward and inverse PTAK equations use plaintext-alphabet indices for feedback and AZ numeric shifts for the primer.

Reviewed original solver SHA-256: `de7144fb870f6800671be8fff2a222e3bcae944991e926ee415e575523daf26b`.

Reviewed adapted solver SHA-256: `672974ca59a9fd071e8e22b16614b3d8c61647ab02cb6ad914a8d1c96d1c5d77`.

## Lower-order model reconstruction

The archived R59 builder computes, for each order k below its maximum K, continuation counts from **raw counts at order k+1**. Its order-one probabilities depend on bigram continuation counts; each later probability table depends on that order's continuation counts and the previous probability table.

Consequently, orders1–4 depend only on raw counts through order5. With identical training bytes and the unchanged builder, choosing K=5 or K=6 gives the same mathematical tables for orders1–4. Building K=4 instead would be wrong because order4 would then use top-order raw counts. The implementation correctly builds K=5 and extracts only orders1–4.

The extracted 1,901,024-byte model matches the recorded SHA-256 `85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41`. This review checked the dependency argument, source and receipt; it did not rebuild the full historical order-six binary or claim its complete byte-for-byte reproduction.

## Linked-tableau mechanism and equivalence

The factor-graph decoder and scalar reference agree algebraically: undo the second AZ shift, take the KRY alphabet index, and undo the first AZ shift. Each position depends only on key slots `i mod m` and `(i+floor(i/w)) mod m`.

The schedule repeats after m×w positions: adding m×w leaves the first slot unchanged and adds a multiple of m to the second. Therefore testing every plaintext symbol at every position of this full period is sufficient to establish equality of these positionwise cipher maps for two same-length keys. The evaluator's same-length linked-key equivalence check is sound. It intentionally does not classify alternative lengths or structural branches.

The PTAK primer is uniquely determined by the first L **path-order** plaintext/ciphertext pairs for the supplied convention and path. Requiring exact primer equality when the full plaintext is recovered is appropriate here.

## Input and execution safeguards

The public-input witness checker validates complete output IDs, lengths, returned family/convention/lag and full forward encryption before opening truth. It uses scalar encryption separate from either optimizer's internal decryption.

The candidate kernels preload their approved material, then install a thread-synchronized seccomp filter that denies new opens and network access and probes those denials. This is the stated host-specific isolation mechanism, not a claim that mount namespaces or Landlock were available. The same-team source review is not a general security audit.

I recommended two inexpensive safeguards before the source freeze: a finite cap for primitive-key rejection sampling, and explicit assertions of all18 linked strata/all12 PTAK strata and public/truth structural agreement in evaluation. Both safeguards have been added before execution. These recommendations do not involve inspecting or tuning on fresh data.

## Reviewed status

The review supports proceeding with the **fresh synthetic screen under its stated narrow decision rules**, subject to the normal prospective commits, input commitment, bounded execution, output freeze and later truth opening. It does not certify an execution that has not yet occurred, change any gate threshold, authorize a K4 run, or independently promote a ledger exclusion.
