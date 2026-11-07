# Kryptos K4 — interdisciplinary research dossier

<small>Research reviewed November 3, 2026 · Read-only research PR · Not a cipher solve or an implemented experiment</small>

**Aim:** establish a historically sourced, cryptographically meaningful research base **before** another computational K4 attempt. This package adds human-research documentation only. It does **not** alter `main`, modify any solver, generate or score candidates, run a checker, or merge a pull request. Read the authoritative repo ledger and the dated sources; correct disputes rather than overfitting K4.

## Start here — findings that materially change next steps

1. **K4 remains cryptanalytically unsolved within the results examined.** In 2025 the full plaintext was found in Smithsonian documents and confirmed by Sanborn; this was **archival recovery, not method/key derivation**. Paradigm announced stewardship and a private full-answer verifier in June 2026. A checker can confirm a complete answer string, not prove an independently discovered cipher method.
2. **Scheidt said K4's plaintext was English and he deliberately disguised normal English statistics.** He did not verify a German/Dutch phonetic algorithm. This supports testing **nonstandard masking**, but not declaring any language hypothesis true.
3. **German and Dutch are distinct possible roles**: a foreign-language **key**, English made to look/sound Germanic in an **intermediate masking stream**, or actual foreign-language **final plaintext**. R63's negative German result tests the first role with a *modern-Europarl-trained key model*, not the other two.
4. **The Berlin Urania World Clock's 1989 inscription has not been reconstructed with enough confidence** to claim a historically exact literal key. Specialist/municipal history reports **80 original cities**, while an Erich John interview caption reports **97**. Modern sources disagree on **146/148**. Later renovations altered city names; R63's **107-name synthetic vocabulary** was a fair broad test, **not** proof against the actual 1989 sequence.
5. **R59, R61, R62 and R63 narrow well-defined cipher families; they do not exclude every running key, OTP, phonetic mask, free alphabet or mechanical cipher.** A high number of checked parameters is not automatically high evidential relevance. R62C's `COL_LT` anomaly is interesting but post-selected.
6. **The next useful computer experiment is bounded:** R63's clock/German keys followed by one of R61's ten fixed transposition routes (existing **draft PR #45**). Preregister it fully, prove power on unseen, unbiased controls, freeze raw full outputs to remote Git, and only then check the released letters. In parallel, historic clock-source acquisition and a carefully controlled **masking-method** program may be higher-yield than brute forcing more keys.

## Dossier index

| Document | Use it for | Safe with a candidate generator? |
|---|---|---|
| [SOURCES.md](SOURCES.md) | 36 initial numbered external/internal source leads, evidence grades (P1/P2/P3/I), chronology, contradictions and cross-checks | **Research only**: may contain public clue discussion |
| [HISTORY_AND_CLUES_VALIDATION_ONLY.md](HISTORY_AND_CLUES_VALIDATION_ONLY.md) | Original installation, K1–K3, K4 source, public clue dates and literal text/offsets, 2025 revelations, K5 context | **NO — sealed postfreeze validation use only** |
| [WORLD_CLOCK_SOURCE_AUDIT.md](WORLD_CLOCK_SOURCE_AUDIT.md) | Physical 24-face clock, rotating hour ring, city-name count conflict, archival transcription requirements | Source-grounding/research only; no verified original cipher key |
| [GERMAN_DUTCH_LANGUAGE.md](GERMAN_DUTCH_LANGUAGE.md) | Germanic orthography, historical 1989 corpora, period/genre mismatches, German-as-key vs Germanic-English-as-mask | Hypothesis development only, not K4-dependent scoring |
| [CRYPTOGRAPHY_AND_TEST_DESIGN.md](CRYPTOGRAPHY_AND_TEST_DESIGN.md) | Method classes, reversible layer order, homophony, wheels, codebooks, OTP information limit and matched-null calibration | Design review only |
| [REPOSITORY_COVERAGE_AND_NEXT_STEPS.md](REPOSITORY_COVERAGE_AND_NEXT_STEPS.md) | R59/R61/R62/R63 bounded exclusions, reproducibility caveats and falsifiable R64 priorities | Historical results only |
| [EXTERNAL_CLAIMS_AND_OPEN_GAPS.md](EXTERNAL_CLAIMS_AND_OPEN_GAPS.md) | Online "solves" vs fitted keys, paid answer verification, Navajo code-talker analogy, evidence gaps | Research only; no output seeding |

## Canonical local records (do not duplicate as a fresh result)

- [Original ciphertext and hash](https://github.com/tylerj-spec/kryptos-k4/blob/main/r39/ic_gate/k4_ciphertext.txt)
- [Cipher family catalogue](https://github.com/tylerj-spec/kryptos-k4/blob/main/docs/CIPHER_TYPES_TESTED.md)
- [Historical cryptography reference](https://github.com/tylerj-spec/kryptos-k4/blob/main/docs/CRYPTOGRAPHY_REFERENCE.md)
- [Cryptanalysis methods](https://github.com/tylerj-spec/kryptos-k4/blob/main/docs/CRYPTANALYSIS_METHODS.md)
- [Immutable blind research rules](https://github.com/tylerj-spec/kryptos-k4/blob/main/r53/BLIND_RULES.md)
- [Original R61 result](https://github.com/tylerj-spec/kryptos-k4/blob/main/r61/RESULT.md)
- [Original R63 result](https://github.com/tylerj-spec/kryptos-k4/blob/main/r63/RESULT.md)
- [R64 proposed follow-up — review-only draft PR #45](https://github.com/tylerj-spec/kryptos-k4/pull/45)

## Source reliability and unresolved questions

**Evidence grades:** P1 originating institution or direct participant; P2 expert/reporting secondary; P3 independent/unverified hypothesis; I local frozen result within explicit scope. Direct statements of intent do not prove that an imagined implementation is the correct one. All dates and competing facts should be sourced.

| Issue | Current assessment | Needed evidence |
|---|---|---|
| World Clock name counts | **Conflicted**, original 80 vs captioned 97; present 146/148 | Original 1969 production drawings, pre-1990 full-face photos, 1997 restoration log |
| English vs German/Dutch | English final plaintext is best-supported creator statement; foreign-looking intermediate remains **untested fully** | Independent hidden-planted phonetic-transducer benchmark |
| German corpus | R63 trained on post-1996 Europarl; authentic 1989–1990 texts have different orthography and genre | Dated DeReKo Wendekorpus or equivalent period-pinned independent source |
| Masking process | Frequency disguise **stated by Scheidt**, exact operator unknown | A concrete reversible generative process that recovers hidden plaintext with a derived key |
| R62C physical layout anomaly | Post-selected statistic retested on 300 fresh nulls; not an identified cipher route | Authenticated physical construction or a fresh preregistered layer hypothesis with successful controls |
| OTP | Information-theoretically underdetermined from ciphertext alone if key truly random and unknown | Independent physical/documentary key material |
| Public full plaintext | Recovered archivally in 2025, **not part of this package** | Not necessary; do not import as generator truth |
| Internet "solves" | Some reconstruct/back-solve lookup values from a desired plaintext | Independent source-backed key and blind recovery audit |

## What can happen after research review

**Phase 0: finalize research.** Resolve broken/weak sources, corroborate historical clock counts and spellings, acquire legitimately usable source corpora; pin source bytes/rights if imported later.

**Phase 1: method-discovery controls.** Select *one* finite, historically motivated transform class, define end-to-end encryption and inverse, create fresh hidden 97-letter English source messages that never use known K4 clue phrases, freeze model source, seed, scoring and null-family rules before the holdout.

**Phase 2: conditional K4 run.** Only if the holdout demonstrates detection and substantial recovery on unseen truth: produce 97-letter candidate outputs from original ciphertext **alone** (plus independently justified frozen source/method). Record raw alternatives and hashes; confirm a successful remote Git commit before published-letter comparison.

**Phase 3: separate validation.** Postfreeze evaluator checks source hashes, full forward encryption, published letters and genuine new natural-language recovery. Don't refine the same generator from released clue matches, checker response or manually guessed message.

**Stop condition:** If available evidence doesn't constrain the hypothesized key/transform, label the hypothesis **underdetermined**, not “solved” through a fitted one-time pad or 97 free offsets.

## Citation/commit policy

All external sources appear as hyperlinks in the relevant file, with originating evidence separated from interpretation. No copyrighted full documents, hidden K4 solution, paid external checker output, historical image reproduction or source-corpus dumps were added. This work is a **review-only historical and cryptographic evidence dossier**, not a claim that every relevant document has been located.

**Owner instruction preserved:** Published K4 clues may motivate a source class (e.g., study Berlin clocks), but their actual plaintext bytes and positions must never reach a candidate generator; comparison is only after a remotely frozen blind output.
