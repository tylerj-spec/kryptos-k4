# R74 research proposal — K1 -> K3 -> K2 superencipherment (strict blind)
**Date: 9 November 2026. Status: review-only proposal; no K4 computation, candidate, or merge.**
**Goal:** a bounded new cipher mechanism that, if right, can yield legitimate, independently generated 97-character prospects for owner review. We cannot promise any K4 plaintext or a positive outcome.

## Decision in one paragraph

Test a **substitution -> transposition -> substitution** ("cipher sandwich") built from the THREE documented technique classes already used in K1, K2 and K3. Encrypt an English message with a KRYPTOS-alphabet tableau and the K1 keyword PALIMPSEST; apply one of the existing frozen K3-like/physical transcription permutations; then apply a second KRYPTOS-alphabet tableau with K2 keyword ABSCISSA. Enumerate both keyword orders, all independent starting phases and the three ordinary tableau sign conventions. Do **not** put any K4 published plaintext letters/positions, crib-derived settings, or result feedback into method/key/candidate selection. This is a historically motivated **guess**, NOT documentary evidence that Sanborn applied those three steps to K4.

Our expectation should be modest. The principal benefit is a **small, exact, falsifiable and novel (subject to proof) family** that can produce complete plaintext candidates with uniquely specified stage keys and round-trip certificates. If it is negative, retire this defined mechanism; do not automatically broaden it.

## Independent historical support, and its limits

1. K1 and K2 used the keyed alphabet KRYPTOSABCDEFGHIJLMNQUVWXZ with the words PALIMPSEST and ABSCISSA, respectively. K3 was a transposition. Source: [Scientific American history (2025)](https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/) and this project's K1/K2/K3 confirmed positive controls.
2. **Multi-stage encipherment is historically documented well before 1990**, but it is *not evidence Sanborn used this sequence*: [US Army 1950 Basic Cryptography TM32-220, chapter 10, sections 128–134, NSA declassified copy](https://www.nsa.gov/portals/75/documents/news-features/DECLASsified-documents/friedman-documents/publications/FOLDER_238/41748889078809.pdf). It distinguishes repeated periodic substitution (which can collapse to a single longer period) from combinations including transposition. Our proposed intervening route matters precisely because two same-alphabet Vigenere additions with no permutation are a trivial summed key.
3. K4 has low ciphertext IC; a layered process with two noncommuting stages can mask plaintext statistics. **The IC does not prove this method** and does not tell us that any intermediate transposition exists.
4. R72 verified the real 336-character K3 construction; **it did NOT prove a K4 encryption worksheet**. We use already frozen 97-symbol permutations as *proxies*. Do not assert the sculpture's 4+31+31+31 shape was a cryptographic route.
5. Other public research has sampled three-layer constructions, often choosing settings through the public K4 clues; see [nitsuah's research gap notes](https://github.com/nitsuah/kryptos/blob/main/docs/analysis/K4_KEYSTREAM_ANALYSIS.md). **Do not import crib-conditioned survivors or claim this is unique globally.** Exact repetition within our own repo must be checked before touching K4.

## Novelty and exclusion audit (mandatory before preregistration)

Read: [docs/CIPHER_TYPES_TESTED.md](../docs/CIPHER_TYPES_TESTED.md), [LEDGER.md](../LEDGER.md) (especially L36, L47–L48, L147, L150, L155, L157, L160–L163), [r58/PREREGISTRATION.md](../r58/PREREGISTRATION.md), [r61/routes.txt](../r61/routes.txt), [r68/PREREGISTRATION.md](../r68/PREREGISTRATION.md), [r73/R73B_RESULT.md](../r73/R73B_RESULT.md).

- **L36** tested sums of periodic keys *in place*. Without intervening T, two Vigenere layers collapse to a single periodic key of period LCM(10,8)=40; that is **not the new hypothesis**.
- **R58** tested V/T/VT/TV, and **R68** tested one periodic/Gromark/autokey family with a transposition or key path. Neither, as documented, establishes coverage of a fixed first tableau key **before** T AND a distinct tableau key **after** T.
- **R61/R66** tested single substitutions plus paths, not the requested S -> T -> S at distinct independent key phases. R69 retired SNAKE_L as a privileged path; it must NOT receive extra search weight.
- **R73/R73b** found NO SIGNAL for two word-state methods; do not recycle either.
- **Exact-equivalence gate:** derive canonical output-position affine keystreams for ALL proposed (route, stage-key order, phase1, phase2, op1, op2) tuples, then compare the *mathematical transforms*, independent of K4 contents, to all previously tested transforms. If this is only a reparameterization of a previously tested closed family, **STOP R74 and report duplication**. Don't use previous K4 clue-conditioned exclusions to prune a newly proposed candidate family.
- A first-pass arithmetic check using ONLY r61/routes.txt and the KRYPTOS tableau (no K4 text) found **14 distinct directed route permutations** after including inverse orientations of the 10 frozen routes; **20,160 raw parameter settings**; **15,680 distinct (route, affine sign, 97-element effective shift vector) transforms** after algebraic deduplication. **No effective shift vector is a simple period <=48 in final ciphertext order.** These figures are provisional independent checks: Claude must reproduce and audit them in committed code before freezing R74. An effective shift need not be a simple in-place periodic stream to be equivalent to another preexisting routed-key family, so the full transform comparison still matters.

## Exact proposed operator (100% reversible at 97 letters; no padding)

Let A = KRYPTOSABCDEFGHIJLMNQUVWXZ (26 distinct letters), and let idx_A return a character's 0-based position in A. Operate on A–Z letters, no punctuation.

For stages E(x,k;op), with letter values x,k modulo 26:
- VIG: y = x+k mod 26, inverse x = y-k
- BEAU: y = k-x mod 26, inverse x = k-y
- VARB: y = x-k mod 26, inverse x = y+k

Every stage maps y back to A[y]. Do not confuse normal A–Z key ranks with keyed-alphabet ranks. Before the first synthetic plant, independently reproduce the published K1/K2 full single-stage known-cipher controls, with any documented text-carving anomalies noted rather than silently corrected.

Define K_a and K_b as (PALIMPSEST, ABSCISSA) **or** (ABSCISSA, PALIMPSEST), never keyword pairs chosen from K4. Initial phase a is 0..len(K_a)-1 and b is 0..len(K_b)-1, independently. For plaintext P of exactly 97 letters:

1. X[i] = A[E(idx_A(P[i]), idx_A(K_a[(i+a) mod len(K_a)]); op_a)].
2. Choose one 97-position permutation r from the **14 exact distinct directed routes** formed by the 10 frozen r61/routes.txt maps and their inverses. Convention: Y[j] = X[r[j]]. Do not interchange source-index/output-index conventions.
3. C[j] = A[E(idx_A(Y[j]), idx_A(K_b[(j+b) mod len(K_b)]); op_b)].

Decrypt in exact reverse order: inverse op_b in ciphertext order, apply inverse route to restore X[i], then inverse op_a in plaintext order. **Intermediate outputs X and Y are evidence, not data to optimize against K4 known text.**

**Size:** 2 keyword orders × 10×8 phase pairs × 3×3 operations × 14 unique directed permutations = 20,160 configurations. Canonicalizing algebraic equivalences should leave 15,680 unique invertible transformations (preliminary; verify). No additional candidate keywords, alphabets, masks, routes, word-boundary guesses, extra cells, German/Dutch rewrites or phase resets are authorized inside R74. Identity/no-transposition case is a **synthetic equivalence control only**, not a novel K4 candidate.

For the keyed alphabet and signs s,t (VIG: +,+; BEAU: -,+; VARB: +,-), the two-stage composite satisfies for output index j:

    idx_A(C[j]) = (s_b*s_a)*idx_A(P[r[j]])
                 + s_b*t_a*idx_A(K_a[(r[j]+a) mod len(K_a)])
                 + t_b*idx_A(K_b[(j+b) mod len(K_b)]) mod 26

Canonicalize by (r, coefficient on plaintext [+1/-1], full 97-element shift vector). Two distinct parameter labels can encode exactly the same transform; return **equivalence classes**, not fabricated independently identified keys. The equality test applies to all 26 input letters at all 97 positions, not to K4's particular characters.

## Why this differs from the earlier failures

A single periodic cipher after T has a key schedule that repeats in the final text order. Here the first key is indexed by **r[j]** while the second by **j**. Combining them creates an irregular-looking, position-dependent shift even when each original keyword is periodic. This is exactly the extra degree of structure provided by **interleaving the transposition between two substitution stages**. It is not the same as extending the earlier K1/K2 keys, or as merely adding two periodic keys without T.

This property is a **testable reason** the model might evade ordinary single-periodic checks—not proof that it matches K4.

## What produces *legitimate prospects* rather than wishful English

**Primary output is not a guessed sentence or crib fit.** It is a ranked set of COMPLETE 97-letter plaintexts calculated deterministically from each frozen method/key/route, plus a full forward-reencryption certificate.

Before any original K4 trial, select **two independent generic English scorers** (e.g., the existing R59 order-6 model and a separately trained word/bigram model). Fix all corpora, hashes, interpolation weights, spelling tolerance (prefer NONE first), and tie-breaking **using synthetic development only**. Score all 15,680 algebraically unique transforms, do not seed or rescore using known K4 fragments or semantically inferred content. Calibrate the **MAXIMUM score across all transformations** for every null message to handle the multiple comparisons. No posthoc reranking by published letters.

An actual **PROSPECT** label requires:
- A calibrated high-confidence, independently fluent 97-letter output (thresholds fixed from held-out positive/wrong-family controls, not K4);
- Its exact reversible transform and both keywords/phases are identifiable at least up to mathematically proved equivalence;
- Verified original 97-letter ciphertext recovered by independent forward encryption;
- The entire candidate set frozen **before any** separate public-clue validator has access to the candidate output.

**For the owner manual-review packet:** freeze the top 25 unique full plaintexts even when all are below confidence (clearly label them **LOW-CONFIDENCE RAW OUTPUTS, not prospects**); include the canonical stage parameters, score, unique-route id, X/Y intermediates (if helpful), full ciphertext roundtrip hash, percentile against null maxima, and a separate sealed postfreeze validator status. Diverse selection must be fixed **before** target (e.g., no two outputs from the same route+keyword-order among first-pass candidates until each is represented, then fill by global score). If no candidate passes blind confidence and no postfreeze anchor check, report **NO SIGNAL**; never call nonsense a candidate or make up text around public clues.

Postfreeze clue agreement is **necessary but not sufficient** for a genuine candidate. A 24/24 match arising from previously fitted known letters is disqualified. The human may discuss ambiguities ONLY after frozen candidate generation and the sealed independent check; a new algorithm proposed after seeing human comments is a separately preregistered experiment, never a retroactive success.

## Synthetic-only feasibility and closed-world recovery gate (separate PR)

1. **A: Reference verification.** Write an independent, tiny encryptor and inverse; check all 26 symbols, every 97-index route, all operations. Assert K1/K2 single-stage historical test vectors. Assert 20,160 raw → 15,680 unique transforms (or correct the count with a documented proof). Show the new transforms are not all covered by L36/R58/R68 already. No original K4 input at this step.
2. **B: Pilot, NO K4.** Use 12 fresh 97-letter English passages with hidden key order, phases, signs and route, plus at least 20 false-family controls; time the *full* scorer/search including all canonical candidates, and report core-hours and memory. Establish a **hard upper compute budget** before any wider test.
3. **C: Preregistered sealed holdout, NO K4.** Suggested: 120 unknown-key+route+method family positives from at least 2 never-before-used books and 300 wrong-family/null controls from at least 7 different generators and independently shuffled texts; opaque randomized IDs; holdout sources not in scoring corpora. Include held-out controls with deliberately archaic spelling, names and Sanborn-like occasional misspellings, independently specified *before* target exposure. If this adjustment materially hurts recovery, report both clean and misspelled power separately.
4. **Gate proposed for Claude's review:** >= 108/120 full 97/97 plaintext EXACT, correct route and canonical effective key transform (or equivalent) on family positives; **zero confident** among 300 wrong-family controls; independent forward encryption checks 100%; confidence score threshold fixed entirely on synthetic development and heldout false-positive calibration. Report the lower 95% bounds for power and the upper 95% bound on false confidence, not only point estimates. If this gate fails, **DO NOT RUN K4**. If the scorer is unstable across independent language models, report LOW_POWER / ABSTAIN rather than search the target.
5. **Target only on separate explicit owner approval:** unchanged original K4 ciphertext, identical reviewed solver, and at least 300 **new** count-preserving K4 shuffles run through the **same full-search max-score** procedure, plus structured wrong-family controls where appropriate. Prefer 1,000 shuffles if a synthetic pilot shows the cost fits the fixed budget; lock that number before accessing the K4 target. Do not stop, tune, choose keys or change route coverage based on target results.
6. **Freeze first:** full 97-letter raw output(s), all candidate parameters, all searched parameter hashes, 2-language-model scores, score ranks, distinct candidate identities, code/model/route/ciphertext hashes, and complete attempted-output ledger, committed to remote Git before the separate reveal evaluator. If the output list is too large, freeze **one complete compressed deterministic full-scan file** plus a raw top-25 packet and checksums. Do not send only hand-picked English-looking fragments.
7. **Independent reveal:** a separate evaluator verifies all frozen candidate hashes and forward encryption, then compares complete known K4 plaintext anchors only as validation/rejection. No anchor-conditioned new search or reranking. Any candidate matching all public anchors plus fluent novel text becomes a **manual-review prospect**, not an established solve.

**Stop rule:** If no high-confidence candidate or K4 has null-like maximum score, report a model-specific negative and STOP. Do not turn partial anchor coincidences into the next key or route. If the historical K1/K2 equations cannot be reproduced exactly, fix the controls before ever testing K4.

## Why NOT the other tempting methods (for this round)

- **The 98-cell R72 routes:** no documented K4-sized encryption worksheet. R73 physical route close-out is still exploratory.
- **Width 7 / 21 anomalies:** R71 showed no candidate family reproduces their joint signature. Secondary diagnostics, never candidate filters.
- **More interrupted keys or R26 minus variant:** both word-state lead families had clean no-signal on K4. A change of sign alone has no independent K4 justification.
- **Two arbitrary alphabets and long unknown key:** at 97 characters the current solver failed blind identification even with partial oracle information. No credible prospects without an entirely new synthetic-only inference capability.
- **OTP or unexplained semantic masking:** may be unidentifiable from 97 letters. A fitted keystream that happens to encrypt attractive English is not a legitimate recovery.

## Implementation handoff to Claude — review before execution

Read THIS research document, then audit main's L36, L47/L48, R58, R61, R68, R73/R73b and any other scripts that implement more than one key stream separated by a transposition. Confirm the authentic K1/K2 tableau equations with independent K1/K2 data and count/equivalence classes of the 97-position routes. Do **not** trust the preliminary 15,680 count without reproducing it. Decide whether the S1 -> T -> S2 family is genuinely new in the exact defined scope; if not, report STOP and propose a different, nonduplicate method.

If new, respond with:
1. Exact effective-shift equivalence proof + novelty matrix against all recorded experiments;
2. A minimal reference encrypt/decrypt implementation and its *synthetic-only* algebraic/unit tests;
3. A frozen development-corpus/dual-scorer plan, expected number of true unique settings and actual profiling cost;
4. A proposed **R74 preregistration** including 120 positive/300 negative gate, global-max null correction, false-confidence threshold and full candidate packet schema;
5. A **GO / REVISE / STOP** recommendation with the anticipated sensitivity (from synthetic examples, not K4).

**This PR does not authorize a K4 test, a merge, an external checker, confidential-plaintext retrieval, a K5 watch or unrelated key hunting.** The user wants a fresh, independently reproducible route to real K4 plaintext candidates; negative evidence is acceptable, but invented plaintext is not.
