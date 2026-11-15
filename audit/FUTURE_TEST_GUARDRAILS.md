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

## What CI enforces (`audit/check_guardrails.py`, schema `k4-qa-v2`)

The checker runs on every pull request to `main` and on every push to `main`. CI runs the copy of the checker that is already on `main` as well as the copy in the pull request, so a pull request cannot pass by weakening the checker.

| # | Rule | Why |
|---|---|---|
| 1 | **Frozen evidence cannot be modified or deleted.** Covers, inside any round directory: any file named like a preregistration, protocol, freeze, reveal or sealed truth; any `.sha256` file; everything under `k4*/`, `holdout/`, `frozen/`, `runs/`; and **any file whose current content is pinned by a committed SHA-256 manifest**, anywhere in the repository. Corrections go in `rNN/audit/`. | Stops silent rewrites of old results, including solver code that a protocol hash covers. |
| 2 | **Experiments live in `rNN/` directories.** A new top-level directory that is not a round is rejected. | An experiment cannot avoid the checks by living elsewhere. |
| 3 | **A new round that adds anything other than Markdown, and any round that adds K4 files, needs `rNN/QA_MANIFEST.json`.** It must name the mode (blind or crib-assisted), the hypothesis, what the test **cannot** rule out (`not_excluded`), the preregistration with its commit and SHA-256, and a positive resource budget. | No unregistered or unscoped experiments, whatever folder layout is used. |
| 4 | **Order is checked in Git history:** preregistration, then the sealed synthetic gate, then any K4 file, each in a separate earlier commit. `gate_verdict` must be `GO`. | A failed or missing gate means K4 is not run and no exclusion is recorded. |
| 5 | **`FROZEN.sha256` is verified line by line**, and every K4 output must either be listed in it or be committed in a later commit (reveal, verdict). | Freeze before reveal is checked, not just declared. |
| 6 | **K4 outputs need resource logs from `audit/run_bounded.py`** with status `COMPLETE` and within the preregistered wall-clock and memory budget. | A killed, stalled or over-budget job is INCOMPLETE, never a negative result. |
| 7 | **Blind inputs:** every file in `solver_inputs` is rejected if its name suggests clue material or its content contains a published K4 plaintext word. | Tripwire against crib leakage. Not a proof of isolation. |
| 8 | **Search hold:** while `audit/SEARCH_HOLD.md` exists, no round may add K4 files. | New K4 searches stay suspended until the owner lifts the hold. |
| 9 | **A change to `LEDGER.md`, or to the guardrail files themselves, needs a new `audit/reviews/*.md` note** with `Affected ledger IDs:`, `Validation:` and `Independent review:` lines. Every ledger row that changed must be named in the note. | No unaudited ledger claims; the note must say who, if anyone, checked the work independently. |

`audit/run_bounded.py` starts a job under the manifest's limits, kills the whole process group when a limit is reached, and writes the resource log. Start every job that reads the K4 ciphertext through it.

## What CI cannot enforce (reviewer responsibility)

- Whether a test measures its claimed hypothesis, and whether its controls are adequate (G0, G2).
- Whether positive controls corrupt a **plaintext** symbol where plaintext drives later state (the R83a defect).
- Whether counts use arbitrary-precision integers (the R75 defect). Counts of solutions must be Python `int`, never a fixed-width NumPy product.
- True isolation of a blind solver. Rule 7 is a tripwire only; use the R53 container pattern for real separation.
- That reviewers are independent. `Independent review:` is a statement, and "NONE" is an acceptable honest answer that keeps the claim unverified.
- Direct pushes to `main` are detected after the fact (CI turns red), not prevented. Turn on branch protection for `main` and make "K4 research evidence guardrails" a required check.

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
