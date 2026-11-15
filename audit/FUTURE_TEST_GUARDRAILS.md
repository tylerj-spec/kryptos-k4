# K4 Future-Test Guardrails — mandatory from adoption

**Purpose:** stop false exclusions, invalid scientific claims, crib leakage, and wasted compute. This is prospective policy. Historical rows are **not automatically certified**; audit them separately. Never overwrite original frozen experiments; publish additive errata with an affected-row analysis.

## G0. Method and scope review — before an experiment exists

- Specify complete reversible encryption and inverse equations, state transitions, key domains, alphabets, position/layout rules, and handling of short/final blocks. Include a worked synthetic example.
- Search the ledger and implementation code for equivalent old models. A new name, route convention, or alphabet labeling does not establish a new hypothesis.
- Describe the exact family being tested and what it **cannot** rule out. A statistical failure, underpowered solver, and mathematical contradiction have different meanings.
- Label the round BLIND or CRIB_ASSISTED. The two modes require separate execution. A crib-assisted feasibility screen can exclude only under its exact assumptions, and can never produce a blind solution.

## G1. Immutable preregistration — before holdout or K4

- Commit a preregistration listing methods, every scanned parameter, corpora and hash, random seeds, scores, stop rules, acceptance and abstention cuts, total search space, multiple-testing correction, null controls, and maximum computational resource budget.
- Record positive-control recovery by **stratum**, wrong-family negatives, independent-text holdouts, expected failure modes, and an explicit GO/NO-GO threshold.
- Set hard limits on CPU duration, memory/RAM, candidate count, retries, and expensive branch enumeration. Check integer bounds; never use silent fixed-width overflow for counts of solutions. A stalled or exhausted job is FAIL/INCOMPLETE, not a negative cryptographic result.
- For any new round that produces K4 outputs, add an experiment QA manifest with the preregistration commit SHA and SHA-256 of the preregistration; commit the manifest before running K4.
- Specify a clear fail-fast rule: if the sealed synthetic gate cannot recover its own hidden truth at the required rate, **do not run K4** and do not mark that family excluded.

## G2. Adversarial positive and negative checks — before K4

- Independent reference encryptor/decryptor and a separately implemented checker; verify all 97 characters round-trip and exact forward witness.
- Exhaustively compare optimized code against brute-force toy settings. Challenge **maximum** key length, lag, graph size, alphabet conventions, nonunit residues modulo 26, wraparound, equal slots, boundary effects and negative indices.
- Test corruption of one PLAINTEXT symbol and one CIPHERTEXT symbol separately. If plaintext drives future state, relax/recalculate **every affected downstream constraint**, not merely the equation at the corrupted index. Test a one-time lost state update and verify the error propagation.
- Require blind recovery of method, key and full plaintext from *unknown-family* fresh synthetic ciphertexts. Report family recognition, parameter success, >=95/97 letters, exact 97/97, false confident classifications and abstentions for each stratum.
- Use challenging old-family confounders and random/null messages; run the **full identical search** on every null and calibrate the maximum over all alternatives. Zero confident negatives in a tiny sample is not a tiny p-value.
- Include ordinary English, systematically masked English and genuinely different-language prose where relevant. Training text and held-out text must not overlap.
- A control invented by the same algorithm is not independent verification. Require a differently implemented oracle or manual worked calculation.

## G3. Blindness and immutable freeze

- Candidate generators get only the original 97-letter ciphertext (hash checked) and prespecified models. No published known plaintext letters, positions, phrases, masks, or crib-derived features enter key search, scoring, training, dictionaries selected for K4, or prompts.
- Separate candidate generation from an independent post-freeze validator, ideally through a restricted input allowlist. Source-code string searches are tripwires, NOT guarantees of isolation.
- Commit and PUSH the complete 97-letter candidate(s), every actual selected method/key, independent forward-reencryption witness, code/model/corpus hashes, random seeds, null and positive outcomes, and resource logs BEFORE checking any known letters.
- Freeze order must be verifiable by distinct Git commits: preregistration, frozen ciphertext-only outputs, and any subsequent known-letter check. A late bug fix is a separately named rerun/erratum, not an overwrite.
- Crib-assisted experiments must not emit decoded plaintexts or complete missing key letters by combining published clues and candidate-generation methods.

## G4. Independent council, audit and ledger promotion

- A BUILDER proposes and implements; an independent BREAKER tries counterexamples and equivalences; an AUDITOR verifies source, tests, allowed inputs, resource bounds and claims. Three roles run by one model **do not count** as independent-model review. Record names, commits and disagreements.
- Published-letter assisted exclusions require an independent code path or mathematical proof backed by exhaustive toy controls.
- A ledger change requires an additive audit/review note identifying affected IDs, current vs prior conclusions, source hashes and verification status.
- Classification vocabulary: EXACT_SCOPE_EXCL; POSTFREEZE_CONDITIONAL_EXCL; STAT_NO_SIGNAL; SOLVER_NO_POWER; OPEN; SUPERSEDED; VERIFIED_BLIND_CANDIDATE. Never silently promote NO_SIGNAL to EXCL. Legacy EXCL is still unaudited until reviewed.
- An invalidated test gets an erratum and restricted conclusion; original data is retained. Never delete, rewrite or pretend the old run never happened.
- Any claim to have solved K4 requires independently reproduced complete 97-letter text, exact reversible forward encryption, reproducible key derivation, and *then* independent validation using the published letters.

## Enforcement by accompanying GitHub Actions

The audit checker is designed to:
1. Reject modification of existing preregistration, protocol hash, or frozen output artifacts.
2. Require QA_MANIFEST.json when a newly created experiment round adds a K4 result.
3. Validate manifest fields, pinned source hashes, and (when present) prereg/freeze/validation Git commit ancestry.
4. Require an additive review note for edits to the ledger.

CI is **structural**, not a mathematical proof. A separate reviewer must approve whether a test actually measures its claimed hypothesis. Existing rounds remain available for additive corrections in a new file.

## Mandatory reviewer checklist

- [ ] Method truly distinct from a previously tested, explicitly scoped method?
- [ ] Complete equations, keys, exact encryption and inverse defined?
- [ ] Preregistration committed before new controls or real K4 results?
- [ ] Independent encryptor vs decoder and exhaustive toy comparisons pass?
- [ ] Max-parameter, state propagation, plaintext/ciphertext corruption and overflow tested?
- [ ] Hidden keys, unseen corpora, and genuine old-family negative controls?
- [ ] Per-stratum synthetic GO/NO-GO gate met?
- [ ] Family-wise max-score false-positive calibration across the whole scan?
- [ ] K4 candidate process isolated from published letters and positions?
- [ ] CPU/RAM/time budget enforced, and failed jobs labeled INCOMPLETE?
- [ ] Frozen outputs PUSHED before an independent post-freeze clue check?
- [ ] Builder, breaker and auditor separately signed the actual conclusion?
- [ ] Ledger entry narrowly scoped, reproducibly cited and independently checked?

**Any unchecked critical item => STOP, repair and run a FRESH sealed holdout.** Do not reinterpret a revealed holdout to make the experiment pass.
