# Kryptos K4 — method-first COA addressing Claude's objections
**Date:** 2026-11-08. **Status:** hypothesis/design only; not a frozen preregistration or authorization to run on K4. **No K4 candidate.**  
**Priority:** identify whether a *word-boundary-dependent* encryption state is recoverable after the spaces are stripped from ciphertext.

## Executive decision

Do not wait for a release, leaked plaintext, or additional inaccessible images. Do **not** run another unstructured K4 key/route/family sweep either. The most useful narrowly specified guess to test is an **interrupted-key cipher whose key resets at each plaintext word boundary**, followed by removal of the spaces. A secondary comparand is a **26-letter Ragbaby-style progressive alphabet** with its word divisions likewise removed.

These are *historically feasible hand ciphers*, NOT evidenced Sanborn/Scheidt K4 methods. The unusual change from older work is that the solver must infer the **missing segmentation** while recovering plaintext and key; previously tested models advanced mostly by ciphertext-character index, not by *unknown plaintext word boundaries*. The published 7/21 features are **secondary observations**, never constraints.

The key technical objection is **identifiability** at 97 letters. No full K4 run is justified until an independently developed, class-and-key-hidden solver passes a demanding out-of-distribution synthetic benchmark and wrong-family abstention test. Correctly re-encrypting *one fitted* text by itself is meaningless.

### Claim-to-evidence hierarchy
- **First-party historical cipher type:** [ACA Interrupted Key instructions](https://www.cryptogram.org/downloads/aca.info/ciphers/InterruptedKey.pdf): keyword may restart at **plaintext word divisions**, or at other interruptions, rather than repeat uninterrupted. [CryptoCrack explanation](https://sites.google.com/site/cryptocrackprogram/user-guide/cipher-types/substitution/interrupted-key) dates publication to 1935 and explicitly describes restarts at word divisions. **Removing the divisions in our proposed encryption is an ADDITIONAL hypothesis.**
- **Historical word-progressive cipher:** [Ragbaby 24-symbol explanation](https://youngtyros.com/2023/02/28/ragbaby-tutorial/), [GC Wizard history](https://blog.gcwizard.net/manual/en/ragbaby-cipher/ragbaby-2/). It encodes by word number + position within word; traditional I/J and W/X merges cannot output an unconstrained 26-letter ciphertext. A 26-symbol alphabet variant has been described, but our exact variant below is a *proposed*, explicit implementation, not proof of Sanborn's practice.
- **Our repo:** [r53/BLIND_RULES.md](../r53/BLIND_RULES.md); [docs/CIPHER_TYPES_TESTED.md](../docs/CIPHER_TYPES_TESTED.md) §17 explicitly marks interrupted keys and word-dependent/progressive schemes as gaps. The R56, R59–R72 tests do not globally eliminate such mechanisms.

## Claude concern matrix — answered directly

| Claude's concern | Decision and testable answer |
| --- | --- |
| **No K4 candidate; evidence hasn't given a method.** | Correct. This is a search-direction proposal, **not** a candidate or claim of convergence. No expectation of a solve is asserted. |
| **Photos inaccessible / ambiguous; no 98-cell source.** | R73/98-cell image hypothesis is not a prerequisite. This test needs only independent classical cipher definitions and synthetic data. No requirement to fetch PBS/worksheet sites, guess which layer bears “TOP #4,” or transcribe K4 images. |
| **R59–R72 negatives already cover many algorithms.** | Novel dimension: word-boundary-triggered key reset / word-number stepping with **boundaries deleted prior to transmission**. Do an exact code/ledger overlap audit first; do not repeat fixed-period keys, normal running keys, Gromark, existing Chaocipher, or SNAKE_L. |
| **Too many combinations / two free alphabets and an unknown method.** | Freeze two *small* fully defined models with at most two known tableau alphabets and three independent K1/K2-derived keywords. **No arbitrary alphabets, free codebooks, extra transpositions, German/Dutch spelling rules, random-null placement, or new keys chosen after K4.** If this bounded model fails controls, stop. |
| **Cannot decipher 97-letter K4 blindly.** | Make **unknown method, unknown key and unknown plaintext word boundaries** hidden variables on *independent 97-letter synthetic controls*. Measure exact full-message recovery, method/key identification, false positives, full forward re-encryption, and score calibration. If unidentifiable, return ABSTAIN. |
| **What if K4 uses a truly random one-time pad?** | Ciphertext alone then generally cannot identify the unique message without independent key information. State this as an unsolved/possibly information-theoretically impossible case; don't invent a key fitted to a guessed plaintext. |
| **Why another experiment instead of pausing?** | This tests a historical, hand-executable, reversible method dimension with a tractable synthetic-only go/no-go gate. The diagnostic can fail before any K4 processing or extensive compute. It is *not* yet evidence K4 uses it. |
| **Width-7 doubled letters / width-21 repeated pairs?** | Both **descriptive diagnostics only**, not generator/scorer/selection criteria, not necessary conditions for the correct method. R71's family diagnostics gave NO_FAMILY, not a universal exclusion of all new models. |
| **Previously published-letter checks contaminate blind selection.** | Strict R53: NEVER feed any public K4 plaintext, positions, held-out message, prior fitted key, or clue-conditioned survivor into any generator, source selection, scorer, parameter tuning, prompt or stop rule. A separate evaluator may inspect public letters **only after full raw-output freeze**. |

## Candidate families: exact encipherment specifications

All new messages are *natural English with independent authentic word divisions*, A–Z-normalized; strip punctuation and spaces **after encipherment** to obtain a 97-letter ciphertext. Synthetic messages and source corpora must be independent of prior R59–R72 synthetic material, test files and K4 itself. A 97-letter plaintext is taken across full natural word boundaries; do not split or truncate a word midstream unless such behavior is explicitly modeled and predeclared.

**Family I — word-restarted Interrupted Key (lead, highest priority).** Select a keyword from \`KRYPTOS\`, \`PALIMPSEST\`, \`ABSCISSA\` (known K1/K2 independently of K4). Use PA=CA=AZ, or PA=CA=KRYPTOS-keyed, operation VIG, BEAU or VARB. For each **separate plaintext word**, restart keyword phase at zero; at word-local zero-based letter position t, key K[t % m] is the keyword's alphabet index. VIG: \`C = CA[(PA^-1(P) + K[t % m]) % 26]\`; BEAU and VARB follow the existing repo tableau definitions. Delete all spaces afterward. This differs from standard periodic ciphers because the key's phase is set by unobserved boundaries. The exact-key, exact-operation, exact-alphabet recovery is the intended test.

**Family R26 — 26-letter Ragbaby-like word-progressive substitution (secondary test only if Family I pilot succeeds).** Choose full keyed alphabet A from AZ or KRYPTOS-keyed; zero-based t in word number w (1-based), phase b from 0..25. \`C = A[(A^-1(P) + w + t + b) % 26]\`. After enciphering, strip word divisions. This is a full-26 analogue of a documented word-number/word-local-position scheme, **not canonical 24-letter Ragbaby**. Distinct words have different starting shifts; character-local position increases within each word. At exactly 97 letters the original w is unknown and must be inferred. **Be explicit that some key/phase choices may be observationally equivalent; count identification modulo mathematically provable equivalence only.**

**No optional K4 modifications.** No transpose stage, guessed word-boundary list, extra pad or null, language substitution, irregular random key restart, or selection of arbitrary alphabets in this first pilot. Those would be additional theories requiring independent evidence and separate sealed controls.

## Solver: full decryption without a K4 crib

For Family I, a candidate segment C[i:j] can be deterministically decrypted *as a complete word* for a specified method/key/alphabet, since key phase resets at its start. Precompute candidate words up to a **fixed pre-registered maximum length** (e.g. 18), and run dynamic programming / beam search over ciphertext offsets with dictionary, word frequency, and word-bigram probabilities. Preserve out-of-vocabulary paths with a fixed penalty; never force a K4 clue word. For R26, include inferred word number in the DP state. A full candidate contains plaintext, exact segmentation, algorithm, key/phase, score and complete encryption proof. Calibrate lexical scores on disjoint English texts; penalize a proliferation of one-letter words and implausible segmentation *in the pre-K4 synthetic stage*.

**Identifiability stress test:** Constrain output to complete, independently generated 97-letter messages. Evaluate whether alternate word segmentations with a different key/family routinely give equally plausible English. If yes, report ambiguity and ABSTAIN: it is not acceptable to select an appealing English candidate based on coincidence. Check equivalence of parameter settings across all possible inputs, not only one 97-letter ciphertext.

## Pre-registration/power gates BEFORE exposing the model to K4

**Phase A — synthetic-only feasibility pilot.** Build encipher/decrypt forward checks, unit tests, a sealed generator and decoder with no K4 input. Run e.g. 12 messages per family plus 30 wrong-family controls (numbers adjustable based on compute *before K4*), profile actual throughput and failure modes. Report core-hours, peak memory, solver correctness and ambiguity. If the class-and-key-hidden recovery is very poor, STOP.

**Phase B — newly generated, sealed, disjoint holdout.** Suggested minimum **100 true positive messages per tested family** with different hidden key/operator/tableau settings, and **300 independent negative/wrong-family ciphertexts** from conventional periodic, running-key, autokey, homophonic and random-like controls. Fix heldout source corpora, keys, RNG seeds, source hashes and evaluation code before running solver on them. Benchmark three increasingly difficult tasks:
1. Method/key/segmentation GIVEN: oracle parser consistency and word-model correctness.
2. Method GIVEN, key + segmentation UNKNOWN: actual method-specific cryptanalysis.
3. Method, key, segmentation ALL UNKNOWN: true method identification and decryption.

**Go/no-go:** Require at least 90/100 exact full plaintext + equivalent actual key + method + segmentation (when needed) for **each family** on task (3), report a one-sided 95% confidence bound, and **zero false-confident K4-like outputs among 300 negative controls**. Zero of 300 gives a one-sided 95% binomial upper bound just under 1% (unlike zero of 100, which does NOT support a 1% bound). If uncertainty/scores overlap, gate fails and the solver ABSTAINS. Recover **same-family hidden keys**, not merely find *some* parameters reproducing the ciphertext; require exact forward encryption of all recovered control cases.

**Compute budget:** Benchmark 12-per-family pilot, then lock total cores, wall-clock cap, candidate beam width, dictionary/model hash and max attempts **using synthetic-only data**. No unbounded brute-force pass and no retroactive K4-dependent change to scores/thresholds. A negative K4 finding **only** limits these frozen model families, not all layered/masked ciphers.

**First K4 run (only after owner's separate approval and synthetic gate):** pass the unchanged original 97-character ciphertext, source-justified frozen families, generic English lexicon and model into an R53-isolated solver. Do **not** mount the research report, published K4 clues/indices, previous clue-feedback, or archival plaintext. Freeze **all** complete raw 97-letter outputs, their inferred boundaries and method/parameters, exact log scores, code/corpus/model/input SHA256, deterministic seeds and attempted settings, **before** an independent evaluator sees public known-letter checks. A postfreeze disagreement **rejects** that candidate, not a license to rerank or tune.

## What we are NOT claiming

This is a **reasonable next method hypothesis**, not a historically proven Sanborn choice or proof that K4 even has meaningful English plaintext directly beneath the cipher. R69–R72's negative results are still valid **within their tested scopes**; they do not justify a universal impossibility claim. Even a candidate with an internally consistent key and readable English could be a false positive, especially with short ciphertext and hidden segmentation; blinded false-positive calibration and postfreeze independent validation are mandatory.

A random OTP cannot be broken by ingenious language models without independent key evidence. A semantic codebook or other unknown masking language might also be unidentifiable with the available 97 characters.

## Claude action checklist (review first; NO K4 run authorization here)

1. Cross-check this document against repo's entire LEDGER / cipher-type code to ensure the *deleted-boundary interrupted-key* mechanism and the *specified R26* were not already attempted.
2. Correct any algebra, parameter ambiguity, overlap or statistical-gate errors **on synthetic samples only**. Verify the ACA references independently. If an older ACA source describes a different interruption rule, label our word-reset choice as a **specific variant**, not the historically mandated technique.
3. Implement two-stage synthetic-only driver: **pilot** → new sealed 100-per-family / 300-negative holdout; locked corpora, scorer and stop rules. Include correct-family and wrong-family controls, exact full-message+key+boundaries verification, error analysis and confidence intervals.
4. Bring back a proposed **R73 alternative** preregistration and actual pilot estimates. Ask owner before running K4, pushing a solver PR or merging anything. If hidden-method retrieval or segmentation is not identifiable, recommend STOP instead of using K4 to tune.
5. Do not search for unreleased K4 plaintext/method, leak-related material or a release announcement. The owner wants our own best method hypothesis and a rigorous independent solve.

**Recommendation:** Test **Family I** first. Only expand to R26 if the synthetic feasibility pilot shows recoverable, meaningful signals. This keeps the next experiment explainable and sharply bounded, avoids the blocked archival-photo issue, and honors all Claude concerns.
