# R89 research-design proposal: unknown-family mechanism discrimination, before another K4 scan

**Status: DESIGN ONLY; NOT preregistered, NO synthetic or K4 run, NO K4 candidates.** 20 November 2026, GPT-6; independent-model reviewer: **NONE**. This file intentionally lives under \`docs/\` because a real new \`r89/\` must be preregistered, checked and committed before generating its holdout or K4 outputs. Reference inventory: \`docs/K4_CIPHER_FAMILY_MATRIX_2026-11-20.md\` (116 classified variants). Base repository through R88 (L177).

## Executive decision

**Do not run 116 independent key brute-forces on K4.** They are overlapping, many are mathematically unconstrained, and 97 letters seldom identifies a complicated custom process. R89 should first prove it can distinguish **several related, genuinely different reversible mechanisms when both method and key are unknown**, on *fresh* hidden 97-letter text. Only gated methods earn one tightly bounded K4 comparison. This reduces repeated optimizer-artifact headlines and preserves the user's hard blind rules.

### Initial method pool (no published K4 letters, positions, or clue-derived sources)

**M1 — ciphertext-controlled irregular stepping single rotor ("RX-CT").**
- Frame letters as integers 0..25, W an unknown arbitrary permutation; initial state s_0=0, absorbing any phase in W.
- Encryption at i: \`c_i = (W[(p_i+s_i)%26]-s_i)%26\`. Then \`s_(i+1)=(s_i+d*delta(c_i;m,q))%26\` with d∈{-1,+1}, m∈{2,3,4,5}, q∈{0,...,m-1}, \`delta(c;m,q)=1+[(c+q)%m == 0]\`.
- Inverse: \`p_i = (Winv[(c_i+s_i)%26]-s_i)%26\` followed by exactly the same update from the **ciphertext already seen**. This is deterministic, ciphertext-only state, reversible and allows self-encipherment. Distinct from R87's \`floor(i/n)\` constant-step state; require symbolic equivalence proof/known-plant differential first. No plain-text clue positions affect state.
- Key space: 28 (d,m,q) schedules × 26! W; search heuristically over W for each schedule; do **not** report exact exclusions. The 28 is 2×(2+3+4+5), with s0 absorbed.
- Dedicated oracle: Python standard-library encipherer separate from optimized solver; all 97 indices, every update point and one altered ciphertext symbol must round-trip. Disruption of a ciphertext symbol may alter every later state and must be tested.

**M2 — transposition BEFORE a keyword tableau / free alphabet ("T→S").**
- \`q_i = p_(pi(i))\` for a genuine permutation pi of 0..96; then \`c_i = CA[(PAinv(q_i)+k_(i mod L))%26]\`. Inverse first undoes tableau at all i, then inverse-pi. Require consistent definition of each alphabet/keystream and phase.
- Start with two **preselected independent of K4 plaintext** route groups: (a) nontrivial modular decimations over 97 positions (a invertible mod 97, b fixed or from a small declared set), and (b) one rigorously defined K3-derived grid operation. Key lengths L∈{3,...,10}, a keyword pool frozen from general English and *independent* of K4 clues, PA/CA one fixed (AZ/KRY) and the other keyword or free.
- **Before** sampling controls, compute equivalence/dedup against L47/L48/L134–L136/R41/R68/R74/R76. A route with a different name but the same index map/advance order is NOT a new mechanism.
- Strongest target: a stage-order comparison of T→S versus S→T under otherwise identical source data. S→T becomes a negative-control family if the target is T→S.

**M3 — separately permuted 2×13 coordinates ("F26"), an explicit 26-symbol fractionating candidate.**
- A key gives a bijection \`A: A..Z → {0,1}×{0..12}\`, e.g. keyword order in a 2×13 rectangle. For a block of length b (including final short block), map plaintext letters to coordinates \`(r_j,h_j)\`.
- For declared shifts \`u,v\`, output coordinates \`(r_(j+u mod b),h_(j+v mod b))\`, then use \`A^(-1)\` to get **one A–Z ciphertext letter per input letter**. Decrypt by the inverse shifts on each coordinate sequence.
- Predefine b∈{3,...,12}, u,v∈{1,...,b-1}, u≠v, and a finite keyword-derived A family before any holdout. Do not invoke a normal 6×6 Bifid encoder with silent rejection of digit outputs. F26 avoids the 25-symbol Playfair/Bifid issue, yet is a new **constructed analogue**, not evidence that Sanborn used this specific fractionation.
- Gate must show that plaintext AND A/key can be inferred at 97 letters. If not, label SOLVER_NO_POWER and stop.

**M4 — two-free-alphabet nonrepeating tableau ("2FA"), DEVELOPMENT TRACK ONLY initially.**
- \`c_i=CA[(PAinv(p_i)+k_i)%26]\`; PA and CA are independent unknown permutations, and k is an explicitly constrained nonperiodic process from a small rule grammar. A pure arbitrary 97-letter key is banned as unidentifiable.
- Build a **constraint-propagating word-segment search**: propose ordinary generic dictionary words at unknown positions, propagate bijection constraints for both alphabets and the state machine, reject inconsistent assignments. This is a *generic* word-level move, NEVER inserting a released K4 phrase/position. Prior R43 dev showed the word objective was more discriminating than quadgrams but hard to optimize (L138); rebuild baseline on controls.
- M4 cannot enter the K4 phase until its independent unknown-family recovery exceeds the **same gate** as M1–M3. Otherwise it remains exploratory development.

### Essential confounders and reason for choosing these mechanisms
- R87 standard regular rotor, R88 progressive Quagmire, R73/R79 word-driven keys, a standard single-tableau Vigenere, 97-character plaintext-preserving transposition, and long-key random streams are *negative/unknown-family controls* rather than newly searched K4 families.
- Every chosen family uses **shared structure**, not 97 independently fitted letters: one W plus a small ciphertext-state rule; one pi + one keyword/tableau; or a keyed 2×13 coordinate map with short within-block shifts.
- M1 and M2 are mechanically/hand-operably motivated; M3 is a falsifiable fractionating alternative. Their historical plausibility is a hypothesis, not an attribution to Sanborn or Scheidt.

## Milestone 0 — independent audit of the latest negative claims (not a K4 generator)

Before declaring R87/R88 universally ruled out, invite a **different model or human** to rederive:
1. R87: equations of unknown free rotor W (all AZ/KRY/PAL/ABS ordered contact pairs, n1–96, d±1), full and drop-one published constraints, exact pairwise bijection consistency, positive synthetic oracles, and count 0/3072. Check whether s0 really folds into W under differing in/out contacts. Inspect code and seeds.
2. R88: one free alphabet with fixed other, d 1–25, n1–96, 19,200 settings; independent code that does NOT import the archived checker; verify no one-error propagation bug and distinguish full from relaxed counts. Check which settings are algebraically equivalent.
3. Sign the review or report disagreement via additive \`audit/reviews/\` note. This is **crib-assisted audit-only**, not a candidate generator. Never use any structural survivors or K4 clue result to seed R89's blind search.

R87 and R88 were single-model internally cross-checked and should remain \`EXACT_SCOPE_EXCL, independently unpromoted\` until this passes.

## Milestone 1 — exact definitions, implementations and reversibility

- Code M1/M2/M3 separately in optimized solver and independent stdlib encipher/decipher; no shared encryption implementation imported by checker.
- **Algebraic equivalence screen**: compare all toy keys on alphabets of size 3/4/5 and small 5–11 letter lengths, plus 97-letter boundary controls, for distinct state families. For M1 use only toy alphabet sizes with the same c-dependent increment; any check referencing modulus 26 is adapted exactly for toy alphabet size.
- Randomly sample thousands of 97-letter tuples across n, key alphabet, route/padding, and one or two altered **plaintext** and **ciphertext** symbols. Re-encrypt and check all positions, downstream updates, last block, modulo signs and wrap.
- Freeze canonical source code, models, and a corpus manifest. Use \`audit/run_bounded.py\`, not an ad hoc resource logger. Full source/test hashes included.

**Stop if** any inverse mismatches, any alias to already-closed parameter region is unrecognized, or the inverse is not unambiguous for all 97 symbols.

## Milestone 2 — method unknown, plaintext/key hidden synthetic evidence

- Use independent data sources at least three genres: 20th-century narrative/diaries, formal prose, and contemporary general English; no shared documents in training/test. Add deliberately misspelled or alternate-English orthography positives as a separate predeclared stratum and German/Dutch *intermediate key source* cases if applicable; do not use published K4 clue phrases as planted strings.
- For each M1/M2/M3 family produce **at least 20 fresh held-out positives** with both key and plaintext hidden. M4 separately if developed. Key parameters stratified by difficulty (small/large block length, early/late step trigger, route order, alphabet choice) **before** truth exposure. No using development cases as sealed holdout.
- Include at least 100 wrong-family ciphertexts from five or more confounders and at least 100 ciphertext-only nulls not fabricated from one new family. Record false confident family assignments, false positive English scores and abstentions.
- The runner receives **only ciphertext, frozen generic language model and frozen source**; does not see family, key, plaintext or any published released K4 characters/positions.
- Pre-register the score and thresholds on **development** data, then freeze. Proposed minimum GO: **>=16/20 at >=95/97 letters with correct family and structurally equivalent key** for each proposed family, **>=3/5 per disclosed difficulty stratum**, and **<=1/100 confident false positives** on the full unknown-family contest. Report exact recovery as additional metric, not hide it behind the 95/97 cut. Preserve model, seed, all decodes and truth/evaluation SHA freeze order.
- **IMPORTANT:** 20/20 correct method with wrong plaintext is not a pass. A true method's arbitrary fitted key is not a pass. A specialized solver that works with the true family supplied is not a pass for the integrated unknown-family contest.
- If one family fails, **do not** run it on K4 or pretend its null outcome excludes the mechanism. It can undergo a newly preregistered *synthetic-only* redesign with another untouched holdout; old gate results stay archived.

## Milestone 3 — preregister and run a combined strictly blind K4 test (conditional only)

At this point create the actual \`r89/PREREGISTRATION.md\`, \`QA_MANIFEST.json\`, \`PROTOCOL.sha256\` and fresh sealed gate in proper **separate committed historical order**. The construction and key search must not read any known released plaintext/positions.

On GO, input is only the published original K4 **ciphertext**, hash with newline:
\`2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3\`.
Plus **at least 200 frequency-preserving K4 ciphertext shuffles**, same across families and deterministic by preregistered seed; include a *separate stratum* of 100 heldout cipher confounders. Do not pool different null distributions into a single p-value.

- All eligible M1/M2/M3/M4 methods are searched on K4 and on every shuffle by exactly the same branch-and-bound or annealing procedure and budget. Record each family's maximum plus overall **maximum across all tried families/parameter settings** for K4 and each shuffle.
- Define \`p_family=(1 + #shuffles whose overall maximum score >= K4's overall maximum score)/(1 + #shuffles)\`. Do NOT compute an uncorrected per-family minimum p and call it a global signal. Also report wrong-family-control false positives separately.
- Prespecify an objective readability/word-boundary screen on development controls; a numeric anomaly that lacks coherent English is only \`SCORE_ANOMALY\`. Full independent reencryption must reproduce each of the 97 ciphertext letters, using the recorded key and route, not a fitted one-time pad.
- Store complete **unedited** 97-letter outputs, all chosen key/state rules, per-family and familywide scores, all null outputs, oracle witnesses, source hashes, resource logs. Produce and **PUSH** \`FROZEN.sha256\` before any source/module containing released plaintext is opened.
- Only a separate postfreeze verifier can check the 24 released letters at their exact offsets; a candidate with any contradiction is rejected. Never use those results to reorder, extend, restart or correct the plaintext. No external answer-verifier submission without the user's explicit authorization.

**GOAL:** one independently reproducible fully blind 97-character English message, derived key/method and exact forward encryption, then postfreeze 24/24. Anything else stays an explicitly scoped failed or tentative hypothesis.

## Three adversarial critiques worth resolving BEFORE writing R89 code

1. **M1 may secretly reduce to an ordinary shifted monoalphabetic substitution.** For each structural schedule, its position shifts can be computed from *ciphertext alone*. This makes the W search potentially easy, but also makes the model highly flexible and prone to arbitrary English fragments. Require AIC/MDL penalty, null max-score calibration, and a formal equality check against R87/R88 fixed-step settings; don't celebrate partial phrases.
2. **M2 may have already been tested under a different algebraic convention.** Compare actual permutations and where the key advances, not labels. A \`T→S\` on a permutation pi can equal \`S→T\` with a transformed key when the key is unconstrained; if so, the apparent novelty disappears. G0 audit can reduce the search dramatically.
3. **M3 may be under-identifiable at 97.** Two coordinate streams under a mostly free 26-cell alphabet can overfit as badly as the two-free-alphabet tableau. Use a restricted keyed alphabet and compare whether 97 letters can recover it, before committing computational effort. Strong controls make a weak family safe to stop.

## Resource-envelope proposal (to be locked at actual preregistration)

- Development cost limit: <=2 CPU-hours per family to demonstrate a promising basic solver; any repeated redesign is separately labeled and uses *new* holdout cases.
- Formal sealed gate: <=2 wall-hours total with resource log COMPLETE and <=4 GB RAM; tune number of CPU workers/iterations only during development, then never alter in sealed test.
- K4+200 shuffles: propose <=4 wall-hours, <=4 GB and <=5 retained candidates per eligible family per target (subject to a pilot-based feasibility estimate documented *before* formal pre-registration). If too expensive, lower the **number of family hypotheses** rather than skip decoys or drop randomness controls. No overruns silently counted as negative evidence.
- Seeds, sample source hashes, sample distribution, scoring, stop criteria, branch ranges, compile flags and max candidate count are immutable from first sealed gate commit onward.
- Split roles BUILDER/BREAKER/AUDITOR; repeated personas of the same model are not independent-model verification. Request a separate reviewer and link signed artifact.

## Decision tree

1. Independent review finds error in R87/R88? → Repair **that** historical row and issue erratum before spending new compute.
2. G0 finds M2 equivalent to old tested finite model? → Remove or change it before any holdout.
3. M1/M2/M3 unknown-family controls fail? → NO K4, report SOLVER_NO_POWER, do not inflate language scoring to make gate pass.
4. Controls pass but K4 scores like shuffles? → STAT_NO_SIGNAL, no exclusion unless a separately valid scoped exact proof exists.
5. K4 unique high score but plaintext gibberish or postfreeze clues disagree? → SCORE_ANOMALY/REJECT, do not backfit.
6. Full English + derived reversible key + postfreeze exact 24/24? → Independent repro and source/key provenance, then request authorization before outside checking.

## Provenance and scope constraints

Primary project files: \`audit/FUTURE_TEST_GUARDRAILS.md\`, \`r53/BLIND_RULES.md\`, \`r85/DESIGN.md\`, \`r87/RESULT.md\`, \`r88/RESULT.md\`, \`LEDGER.md\`. External historical crosswalk: American Cryptogram Association cipher catalog (https://www.cryptogram.org/resource-area/cipher-types/) and CrypTool NCID list (https://legacy.cryptool.org/en/cto/ncid.html). Context from Scheidt WIRED 2005 (https://www.wired.com/2005/01/inside-info-on-kryptos-codes/) and Sanborn Scientific American November 2025 (https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/).

**No experiments were run for this design. Unknown/missing facts remain unknown. The released K4 words are never part of a generator input.**
