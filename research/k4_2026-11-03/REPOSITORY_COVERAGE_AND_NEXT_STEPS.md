# Kryptos K4 — source-to-experiment gap audit (November 3, 2026)

**Research synthesis, not a decryption claim.** Read together with [the source register](SOURCES.md), [historical/clue register — VALIDATION ONLY](HISTORY_AND_CLUES_VALIDATION_ONLY.md), [World Clock historical audit](WORLD_CLOCK_SOURCE_AUDIT.md), [German/Dutch language](GERMAN_DUTCH_LANGUAGE.md) and [cryptographic mechanism atlas](CRYPTOGRAPHY_AND_TEST_DESIGN.md). The repository's canonical ground-truth ledger remains `LEDGER.md`; do not silently replace existing bounded exclusions.

## 1. What the latest actually shows

| Round / ledger | Exact bounded hypothesis | Control capability | K4 observation | Correct reading |
|---|---|---|---|---|
| R59 / L149 | Ordinary English plaintext and **English text running key**, in-place | Original benchmark 16/20 detected; R62B later tested additional modern-style messages 20/20 | No signal, word salad | Evidence against the **tested** ordinary-English running-key source/model/conventions; no exclusion of all nonrepeating keys |
| R61 / L150 | English plaintext + unknown English running key, then one of ten K3/engraving-site routes, substitution before transposition | 18/20 holdout detections; route recovered 15/20, strict K4 rule 13/20 control power | K4 5/100 shuffled nulls >= target, only chance-level validation matches | **NO SIGNAL** for this ten-route family; not an exact impossibility proof |
| R62B / proposed L151 (review-only PR #41) | Fresh modern/Sanborn English running-key detection calibration; **not a K4 run** | Modern 20/20 vs original 16/20; Sanborn 18/20 cohort threshold, 17/20 pooled; frozen reports on PR | Not applicable: no original K4 test | Establishes detection power **in-place** and warns K1/K3 training overlaps; don't extrapolate it to German phonetic masking |
| R62C / PR #43 | Fixed R61 **COL_LT stage-one best-minus-second gap**, with 300 fresh shuffled nulls and 20 alternate-route families | 41,730 full 97-letter forward witnesses; 300 nulls, 20 correlated alternate route families | 2/300 fresh nulls >= historical gap; plus-one 3/301; 0/20 alternate families >= original | Localized **structural anomaly**, not an all-search-adjusted significance claim or proof that COL_LT is an encoding route |
| R63 / L152 | English plaintext + **World Clock city-name key** (R63's 107-name synthetic model) or **modern German prose key**; in place; plus bounded numeric streams | CLOCK 10/10 detected, median 97/97 plaintext; GERMAN 10/10, median 85/97; independent K4 audit 202 + 3,030 complete witnesses | CLOCK 81/100 nulls >= K4, 2/24 validation; GERMAN 27/100, 0/24; numeric exact families 0/92.9 million all-24 matches | Strong evidence **against these in-place, fixed key models**; **not** the German/clock + transposition combination; numeric searches are exact only within their enumerated operators |

References: [R61 preregistration](https://github.com/tylerj-spec/kryptos-k4/blob/main/r61/PREREGISTRATION.md), [R61 result](https://github.com/tylerj-spec/kryptos-k4/blob/main/r61/RESULT.md), [R63 preregistration](https://github.com/tylerj-spec/kryptos-k4/blob/main/r63/PREREGISTRATION.md), [R63 result](https://github.com/tylerj-spec/kryptos-k4/blob/main/r63/RESULT.md), [R62B PR](https://github.com/tylerj-spec/kryptos-k4/pull/41), [R62C PR](https://github.com/tylerj-spec/kryptos-k4/pull/43), [canonical cipher catalog](https://github.com/tylerj-spec/kryptos-k4/blob/main/docs/CIPHER_TYPES_TESTED.md).

### R63 chain of custody

- Original research preregistration remote commit [95ad2e8](https://github.com/tylerj-spec/kryptos-k4/commit/95ad2e8e6490d1dc97c2afd190741da4c80d5b69).
- Complete primary and raw alternatives remote freeze [2d043af](https://github.com/tylerj-spec/kryptos-k4/commit/2d043af9d3c7427b0bc450e4b5158c92c27a5934) before the reveal.
- Independent audit and reveal commit [b469983](https://github.com/tylerj-spec/kryptos-k4/commit/b46998354a893f197a6c47249ac4c32bf42ddfbd).
- The audit JSON says `verified_remote_git_freeze:false`: its *program* checks local hashes, not remote push chronology. Separate GitHub evidence supports a real frozen remote commit; do not silently convert the flag to true or treat it as a failed cipher witness.
- R63 numeric family counted **92.9 million precisely parameterized cases for afterfreeze bounded feasibility checking**; it did **not** store a raw 97-letter output for each of 92.9 million cases. The scanner preserved top ranked outputs by key family. Also, four numeric development/control messages used public K4 phrases in synthetic plaintext. They were not provided to K4 candidate generation, but new unbiased controls should avoid them.

## 2. Open case taxonomy

### A. Near-term and bounded (cheap to specify, conditional computation)

- **A1: R64 non-English running key + transposition**: join R63 CLOCK/GERMAN key models to R61's 10 frozen routes, order **substitute → transpose**. PR [#45](https://github.com/tylerj-spec/kryptos-k4/pull/45) holds a **review-only proposal**, not a completed preregistration or K4 test. Require source hashes, independent natural-language controls, 97-letter raw alternatives, explicit postfreeze verifier and whole-route null calibration. A failed control gate = **INCONCLUSIVE**, not K4 exclusion.
- **A2: Reverse operator order (transpose → substitute)**: R61's solver cannot directly use ordinary English plaintext statistics on the scrambled intermediate text. New decoding/scoring and hidden-planted power tests are required; merely reversing route names is not equivalent.
- **A3: Clock hour values/UTC offsets**: first obtain authentic old face/hour-ring mapping and a time/date convention **independent of K4 ciphertext**. A 24-index stream or hour rolling register is not the same as R63's city names.

### B. Plausible but needs a new solver with real controls

- **B1: German-/Dutch-looking *English* intermediate plaintext**: phonetic/orthographic transformation distinct from using German text as a key. Evidence that Scheidt deliberately concealed statistics supports researching masking generically; it does not prove an actual Germanic cipher. Need fixed transducer and a reversible length/phase rule. Pre-1996 German and pre-1990 Dutch source controls matter.
- **B2: Homophonic encoding, nulls, letter suppression/insertion**: these can conceal unigram statistics but must explain how exactly **97 ciphertext characters** arise and how English is reconstructed. Earlier periodic/bounded-null failures do not exclude arbitrary systems.
- **B3: Two fully free alphabets + independently unknown key**, unlike R44b's 20/20 controls with **known key**. At 97 letters this is heavily underdetermined; need model restrictions that genuinely predict held-out truth.
- **B4: Irregular/interrupted keystreams, wheel stepping and mixed alphabets**: current bounded Chaocipher/short-period outcomes do not exhaust these families.
- **B5: Book/source key with authenticated pre-1990 edition**: a public novel, 1989 political speech or guidebook edition is stronger evidence than a model that can manufacture arbitrary key text; require source provenance and key-start rule before scanning.

### C. Hypotheses requiring *external physical evidence* first

- The exact **1988–1990** face-by-face original World Clock city inscriptions and orientation: current sources conflict on 80 vs 97 original cities and 146 vs 148 modern counts. See [clock audit](WORLD_CLOCK_SOURCE_AUDIT.md).
- The physical orientation, panel construction, missing/corrected characters and material affordances of Kryptos itself: the creator's method may involve interpretation of **the sculpture as an object**, not only 97 ciphertext letters. This is an investigation priority, *not* a license to change the canonical ciphertext.
- 1968–1969 clock designs/restoration records and Sanborn studio-era material accessible lawfully; neither privately purchased archive contents nor Smithsonian unpublished 97-character answer has been imported or guessed.

### D. Non-falsifiable without a new independent constraint

- **A perfect true OTP:** by Shannon's perfect-secrecy argument, ciphertext alone does not determine its plaintext. Don't brute force a free 97-letter pad and call the resulting readable answer a solve.
- **Unrestricted 97-position key + two arbitrary alphabets + arbitrary route:** virtually any 97-letter target message can be fitted with enough degrees of freedom. A forward-encryption witness then certifies mathematics, not source discovery.
- **Arbitrary phonetic substitutions changed until a ciphertext fits:** absence of a frozen rule prevents evidence from accumulating.

## 3. Source-evidence acquisition vs algorithm execution: priority matrix

| Priority | Work product | Why higher value | Stop/go rule |
|---|---|---|---|
| **1** | Full annotated historical source dossier (this package) + evidence conflict log | Stops repeated false leads and quantifies what is genuinely unknown | Research sources dated and traceable; uncertain claims expressly marked |
| **2** | 1988–90 World Clock original 24-face list, 1997 replacement differences and hour-band mechanics | Can constrain a physical, historically credible key **more strongly than brute force** | No claim of literal clock key without clear old-era evidence |
| **3** | R64 implementation and hidden-message holdout, if user authorizes new experiment | Clean nearest untested R61×R63 composition | Preregister, hide truth, pass hard recovery + null gates before K4 |
| **4** | Independent Germanic/phonetic masking **method discovery**, not just dictionary swaps | Different mechanism; tests Scheidt-style statistical disguise | Demonstrate recoverable unseen English **without identity of transform** being handed to solver |
| **5** | Alternate operator order or historically grounded source-key family | Adds a real new hypothesis class, not one more keyword | No K4 run if planted truth cannot be recovered |
| **6** | Broader high-dimensional free-alphabet/rotor/OTP explorations | Potentially relevant but enormous false-positive risk | Only after independent evidence sharply restricts search |

## 4. Guardrails for implementation

1. The original unmodified 97-character ciphertext is the **only K4 payload into generation**. Do not supply clue text/offsets, a mask, validation feedback, presumed plaintext, or derived target key corrections.
2. Historical human hypotheses **can be motivated by public clues** (the owner explicitly clarified this), but each computational construction is fixed **before** seeing K4 validation.
3. Freeze **full** raw 97-letter plaintext/key candidates (including alternatives and route identifiers), source hashes, build arguments, binary hashes, source corpora and preprocessing. Verify successful **remote Git** push before a separate checker runs.
4. Validate exact encryption witnesses and each source independently. If an external checker is ever used, it must receive only a **previously independently produced, frozen 97-letter candidate**, never be used as an iterative score oracle to tune a generator.
5. Keep **EXCL** (bounded mathematical impossibility), **STAT** (no signal under a well-powered test), **WEAK** (insufficient power), **FEAS** (fits arithmetic but meaningless text), and **OPEN** distinct.
6. Maintain an exact record of unchanged physical text and transcriptions; a missing or extra letter can yield a plausible but wrong result, as the K2 2006 correction demonstrated.

## 5. Recommendation

After this research audit, **do not assume another general-running-key search will solve K4**. R64 is a reasonable next *bounded, controlled* computational experiment because it closes a specifically untested composition. In parallel, prioritize source work that can uniquely constrain a masking/physical mechanism. A genuine result will explain why the **specific** algorithm and key are correct — not just reproduce the published validation fragments.

**No solver code, no hidden-K4 key, and no K4 test is generated by this document.**
