# Kryptos K4: comprehensive mechanism and cipher-family inventory (20 November 2026)

**Design-study document, not a K4 experiment and not a cryptographic proof.** Base repository: main merge `bc09794bc0319fb4f1d3ee71df23efb67030ea15`, through R88 / ledger L177. Prepared by GPT-6, independent reviewer **NONE**. Do not use this document as a key/route list selected by released K4 plaintext. Proposals below are for **fresh synthetic tests** until an immutable, separate blind protocol exists.

## Purpose and reading rules

A cipher is *viable* here only if it remains logically possible under some specified reversible mechanism and the **current project's tested scope**. Viable does not mean likely, and nearly arbitrary keyed transformations are unfalsifiable from 97 letters. This is a broad finite **research taxonomy** of 116 named mechanism/variant entries, not an exhaustive enumeration of all mathematically possible algorithms.

**Status tags:** `O` OPEN plausible specific mechanism, no decisive exclusion; `P` PARTLY TESTED / earlier null or exact ruling covers a subspace only; `C` COMPOSITE ONLY (direct form structurally incompatible with observed cipher facts; an explicit extra stage is needed); `S` SCOPED NEGATIVE (many direct versions examined; only altered parameters, layers or distributions worth revisiting); `X` EXACT-IN-SCOPE reported exclusion, pending independent-model promotion where noted; `U` UNDERDETERMINED absent a constrained key source; `N` NOT INVERTIBLE as a standalone decrypting algorithm. Count by tag: C=14, S=5, X=2, O=58, P=28, U=8, N=1. This is not an evidence-grade likelihood ranking.

**Facts and provenance:** K4 original length 97, all 26 ciphertext letters present, IC ~0.03608, 24 released plaintext letters for checking **after freeze only** (`docs/KRYPTOS_FACTS.md`). Pure transposition directly fails the multiset invariant (L01); fixed monoalphabetic substitution in place directly fails repetition-to-distinct-plaintext (L02). A direct alphabet of only 25 symbols cannot emit all 26 ciphertext letters without an added representation stage. These statements do not reject compositions whose final positions/alphabets differ. K4 layout and boundary conditions matter: 97 is prime, but padding is possible; do **not** infer a 97-wide grid key by itself. Sanborn/Scheidt's statements are context, not proof of the algorithm.

**Current essential updates:** R87 (L176, merged PR #96) reports 0 of 3,072 single free-wiring constant ±1 stepping-rotor structural settings, and a blinded no-signal result. R88 (L177, merged PR #97) reports 0 of 19,200 constant-step one-free-alphabet Quagmire structural settings, and blind no-signal. Both use known letters in a **separate post-freeze exact exclusion only** and both declare `Independent review: NONE`; independent-model replay is needed before promotion. R85/R86 on draft PR #95 is narrower and does not negate R87.

## Scope boundaries and priority

Do not rerun unchanged (a) a standard single rotor with fixed ±1 advance, (b) an in-place one-free-alphabet Quagmire with constant progress, (c) bare Vigenere/Caesar/columnar, or (d) the same named book offsets, as if these were genuinely new. Focus on **unknown-family identification**, **state dependence**, **multiple free alphabets**, **reversible masking**, **stage ordering**, and **bounded polygraphic fractionation**. A broad space can remain open because it has too many degrees of freedom to derive from 97 symbols; treat that as a limitation, not positive evidence.

### Source keys for entries
- `Lnnn`: `LEDGER.md`, status advisory until audited.
- `Rnn`: `rnn/RESULT.md` or `rnn/PREREGISTRATION.md`.
- `O` does not assert this particular type has not been touched anywhere; it means the **specified remainder** has not been decisively eliminated.
- ACA and CrypTool are completeness checks for named classical types, not evidence the sculpture used them.


## A. Fixed-tableau, running-key and generated-key families

| ID | Cipher/mechanism | Tag | Specific K4 evidence or constraint | Useful differentiating test |
|---|---|---|---|---|
| A01 | Caesar / affine / Atbash, single alphabet | **C** | In-place mapping contradicted (L02); consider only before a permutation or other layer. | Stage-order synthesis; not solo. |
| A02 | Vigenere / Beaufort / variant Beaufort | **S** | Many in-place periodic lengths/tableaux exactly checked (L03–L05, L88). | Only long/irregular keys or distinct layer order. |
| A03 | Quagmire I / II / III / IV, keyword alphabets | **S** | Broad in-place periodic/keyword searches (L03–L04, L76/166). | Changed alphabet construction + nonperiodic stream. |
| A04 | Porta / Gronsfeld / numeric repeating keys | **S** | Direct standard cases checked (L14, L88, R75). | Avoid unless preceded by nontrivial masking. |
| A05 | One fully free alphabet + a regular progressive key | **X** | R88 L177: 0/19,200 in its exact in-place scope (one fixed AZ/KRY/PAL/ABS alphabet). | Independent replay; avoid re-running identical model. |
| A06 | Two fully free alphabets + unknown irregular key | **O** | Central unidentifiable/unsolved space (L21, L138); distinct from R88 one-free case. | Word-constraint solver; rank on fresh controls. |
| A07 | Two free alphabets + structured nonrepeating key | **O** | Limited Gromark/linear schedules tested; much broader. | Independent state equations and recovery pilot. |
| A08 | Unknown running key from arbitrary English text | **P** | R59/61 blind no-signal for specific tableaux, alignments and routes. | New source classes/transposition order; avoid recycling the same 5 books. |
| A09 | Running key from non-English text | **P** | German/World-Clock R63/64 negative within measured corpora; literary German gate weak. | Period-correct German/Dutch corpora and genre-separated power. |
| A10 | Running key from nonlexical symbol/text stream | **O** | Dates, limited numeric sequences, named text lists were scoped checks (L16, R63, R70). | Prespecified source generator; exact edition/hash. |
| A11 | Two independent running keys or text + alphabet mask | **O** | Single streams and two keyword stages tested, not arbitrary independent streams. | Controls with hidden both key sources; joint identifiability. |
| A12 | Plaintext autokey, especially long lag / free alphabet | **P** | L27, L52, R68, R83 have incomplete long-lag/low-power ranges. | State-safe oracle; unknown initial seed; word-level search. |
| A13 | Ciphertext autokey, lag 73–96 or reordered path | **P** | L17/R68 exclude many direct shorter lags, not all long lags or orders. | Toy exhaustion + control gate in uncovered range. |
| A14 | Mixed plaintext/ciphertext feedback | **O** | Not equivalent to one-lag autokey; R77/R79 touch only narrow rules. | Bounded two-tap state; corruption propagation oracle. |
| A15 | Interrupted / held / reset keyword key | **P** | R73/R79/R83 cover named reset rules only. | Unmarked reset grammar and unknown word boundaries. |
| A16 | Keyword + nonlinear PRNG / NLFSR / mixed recurrence | **O** | R75/F1X cover linear and periodic subspaces, not arbitrary nonlinear state. | Explicit finite state/key sizes; power test. |
| A17 | Key schedules varying with row/block/time | **P** | Piecewise/physical clocks tested narrowly (L75/L76; R69). | Finite change points independent of clue positions. |
| A18 | Two-stage tableau substitution (both keys free) | **P** | R80a/R84 one-listed-one-free returned no signal; fully free largely unidentified. | Unknown-family sealed gate before real K4. |
| A19 | Arbitrary per-slot substitutions, m=26 or long period | **U** | L21/L53 leave many periods open; unconstrained alphabets can fit almost anything. | Only testable with shared wiring/state constraint. |
| A20 | Finite-state, non-linear reversible letter transducer | **O** | Unbounded bespoke space; must make transition grammar finite. | Enumerate compact update rules and synthesize controls. |
| A21 | Progressive word-number/Ragbaby variants | **P** | R73b/R79/R81a covered fixed rules only. | Different word segmentation/change rule; avoid same R26. |
| A22 | Two different keyword alphabets with transposed key advancement | **P** | R68/L157 test 10 carved routes and selected tableau conventions. | New route family from independent geometry, then key order. |

## B. Evolving alphabets, rotors, and polyalphabetic mechanisms

| ID | Cipher/mechanism | Tag | Specific K4 evidence or constraint | Useful differentiating test |
|---|---|---|---|---|
| B01 | Single freely wired rotor, step ±1 every n characters | **X** | R87 L176: 0/3,072 settings for n=1–96 and four alphabet families, in place. | Audit R87 independently, do not repeat unchanged. |
| B02 | Single rotor with irregular fixed stepping schedule | **O** | R87 explicitly leaves irregular stepping open. | Finite change schedule, 2–8 step intervals; fresh gate. |
| B03 | Single rotor stepping on ciphertext symbol class | **O** | Mechanically explainable, self-synchronizing; absent from R87 scope. | Define advance-before/after; exhaustive toy transitions. |
| B04 | Single rotor stepping on recovered plaintext symbol class | **O** | Distinct future-state dependence; vulnerable to R83 error-propagation bug. | Sequential inverse + one-plaintext-error controls. |
| B05 | Single rotor with variable step sizes (not ±1) | **O** | R87 checked only d=±1, though may be symmetry-equivalent for some alphabets; prove uniqueness first. | Deduplicate invertible step conjugacies. |
| B06 | Two-rotor odometer stepping | **O** | Natural next extension and R87 negative family control, not searched on K4. | Fast shared-wiring solver; synthetic identifiability first. |
| B07 | Two rotors, coupled/irregular stepping | **O** | Much larger family; do not equate to odometer. | Restrict state rule to a small, motivated grammar. |
| B08 | Three- or more-wheel rotor / pinwheel-machine family | **U** | Likely too underdetermined with 97 characters unless external key/structure. | Prove identifiable on 97-letter controls first. |
| B09 | Reflecting fixed-point-free rotor (direct Enigma-type) | **C** | Direct in-place no-self-map structure conflicts with published K4 aligned letters (L01–L04 facts); layers undo inference. | Only composite with transposition/recoding. |
| B10 | Hebern-like rotor with alternate contact alphabets | **P** | R87 checks only AZ/KRY/PAL/ABS contact numberings. | Require independently justified different alphabet source. |
| B11 | Chaocipher with both wheels fully free | **O** | R56 tested one word-keyed and one standard wheel; not two unknown arbitrary wheels. | Hidden-wheels plant recovery and identifiability check. |
| B12 | Chaocipher with alternate wheel update rule | **O** | Standard R56 update only; custom variant must be precisely reversible. | Toy oracle comparing whole state trajectory. |
| B13 | Alberti disk, unmarked irregular turns | **O** | Period/phase must be learned without location hints. | Finite turn schedule, generic letter score controls. |
| B14 | Phillips dynamic squares / Phillips-RC | **C** | Standard 5x5 direct output cannot show all 26 letters; 26/36-symbol variants possible. | Explicit alphabet and 97-length convention. |
| B15 | Move-to-front / move-to-back alphabet rotation | **P** | R78b L168 tested key-free recency model only. | Keyed/stateful variant, controls, independent oracle. |
| B16 | CONDI and related successive alphabet rotations | **O** | Keyed progressive monoalphabetic updates; distinguish from R88 constant-step model. | Test state update after ciphertext not just index. |
| B17 | Alternating hidden lookup tables / cyclic code alphabets | **O** | Not necessarily a single free alphabet; per-slot matching only if period small. | Sparse shared-table state + compression/MDL. |
| B18 | Keyed 26-letter permutation evolving by swaps | **O** | Bespoke but hand-operable, masks counts; many swap schedules. | Small reversible swap grammar; severe decoy calibration. |

## C. Transpositions, stage order, geometry and reading paths

| ID | Cipher/mechanism | Tag | Specific K4 evidence or constraint | Useful differentiating test |
|---|---|---|---|---|
| C01 | Pure columnar, railfence, route, grille, fold, etc. | **C** | Pure permutation preserves letter histogram; impossible for aligned K4 clues (L01). | Only use as a stage coupled to substitution. |
| C02 | Substitution then complete/incomplete columnar | **P** | R41/R68 plus L06–L09 cover bounded routes/keys. | Uncovered parameters with one free alphabet. |
| C03 | Columnar transposition before substitution | **P** | Order matters; earlier suites cover only selected combinations. | Distinct T→S operator tested against S→T. |
| C04 | Double columnar (same/different keyword) + substitution | **O** | Not every key pair, uneven column-length convention or order was enumerated. | New structural routes, not renamed old ones. |
| C05 | Myszkowski / shared-rank columnar + substitution | **P** | L48 covers explicit routes, not arbitrary superencipherment. | Unique handling of duplicate keyword letters. |
| C06 | AMSCO variable cell lengths + substitution | **O** | Pure AMSCO ruled out; mixed cells may matter under additional substitution. | Forward/inverse for final incomplete cell. |
| C07 | K3-style double quarter-turn + fresh layer | **P** | L47–L48, R41, R68; tested routes not all compositions. | Avoid previously enumerated width/order grids. |
| C08 | Modular decimation of 97 indexed cells + substitution | **O** | 97 is prime; nonzero multipliers give permutations, but no special meaning by themselves. | Enumerate nonduplicate modular strides and offset. |
| C09 | 98-cell sheet with one pad/null + encryption | **O** | R72 discussed 98-cell idea; specific full mechanism not settled. | Pad location and deletion stage fixed a priori. |
| C10 | Variable-length or nonrectangular rail/spiral routes | **O** | Bounded prior routes; enormous broader geometrical space. | Require generative geometric grammar/MDL penalty. |
| C11 | Turning grille / Cardan cutout + substitution | **O** | Pure grille excluded; compounded writable holes are not. | Finite holes, orientations, no crib-shaped mask. |
| C12 | Nihilist / route transposition + substitution | **O** | Pure routes ruled out, composite uncertain. | Differential route signatures after decryption. |
| C13 | Cadenus transposition + letter substitution | **O** | Strong length/layout constraints; 97 often needs explicit padding. | Predefine last-block policy. |
| C14 | Swagman / diagonal Latin-square route + substitution | **O** | Needs reversible coordinates; underexplored. | Nonoverlapping routes and two-stage controls. |
| C15 | Sequence transposition + evolving substitution | **O** | Distinct state if key advances in written vs read order. | Compare path-key ordering with identical controls. |
| C16 | Redefence / keyed railfence + substitution | **P** | Historical enumerations cover a subset (L48). | New non-overlapping key class only. |
| C17 | SNAKE / alternating carved-row direction + new cipher | **P** | R69 ruled earlier reading artifact, not every composite. | Do not select because of R69 K4 scores; fresh controls. |
| C18 | Interleaved streams with distinct keys (odd/even/rows) | **O** | Implicit two-stream state can flatten statistics and hide periodicity. | Typed interleave schedule and test identifiability. |
| C19 | Transposition applied to key stream, not message | **P** | R68 tested selected carved paths; general key-path mechanism survives. | Compare original-order/key-order state in oracle. |
| C20 | Arbitrary 97-place permutation + free pad | **U** | Can fit any text and lacks falsifiability without key-source limits. | Do not spend brute force unless source constrains permutation. |

## D. Polygraphic, fractionation and mixed-radix encodings

| ID | Cipher/mechanism | Tag | Specific K4 evidence or constraint | Useful differentiating test |
|---|---|---|---|---|
| D01 | Playfair / two-square / four-square (standard 5x5) | **C** | 25-symbol output cannot directly represent K4's 26 distinct symbols. | Only 6x6 or explicit recoding/layer. |
| D02 | Tri-square / seriated Playfair (standard 5x5) | **C** | Same direct 25-symbol problem; digraph/padding conventions matter. | 6x6 or recoded output only. |
| D03 | Playfair / four-square / two-square 6x6 | **O** | Output includes 36 symbols; observing 26 letters is possible but not generic. | Predefine 36→26 restriction or alphabet output conditioning. |
| D04 | Hill matrix 2x2–5x5 direct | **S** | L11, L35, L61, R57 checked specific block/pad/alphabet conventions. | Only new reversible block layout + independently powered solver. |
| D05 | General non-linear digraph/polygraph substitutions | **O** | Arbitrary map on 26² pairs; not the same as Playfair. | Restrict to algebraic/keyed maps for identifiability. |
| D06 | Bifid 5x5 direct | **C** | Direct 25-letter cipher alphabet incompatible with 26 ciphertext symbols. | Explicit expansion or second-stage relettering. |
| D07 | Bifid 6x6, selected 26-letter outputs | **O** | Fractionation can flatten frequency; 6x6 variant historically documented. | Fix period, handling of digits, final block. |
| D08 | Conjugated-matrix Bifid, 6x6 | **O** | Mixed squares/matrix; 5x5 form has output-alphabet issue. | Separate 6x6 and 26-relettered hypotheses. |
| D09 | Trifid 3x3x3, one stage | **S** | L12/L91/L95 report exact negative in particular cube/phase setting families. | Independently audit 'any cube' scope before universal claims. |
| D10 | Digrafid / pairwise coordinate fractionation | **O** | Accepts paired symbols and 3D layouts, but odd 97 requires a rule. | Synthetic oracle with odd final char. |
| D11 | Bifid-derived custom 26-contact fractionation | **O** | Artist-designed coordinate mapping with exactly 26 output letters. | Specify bijective per-block encoding. |
| D12 | Bazeries cipher (digit key, reversal, mixed alphabet) | **O** | Reversals make it unlike simple progression; not equivalent to Gromark. | Bound digit key and explicit grouping. |
| D13 | Portax paired-letter tableau | **O** | Alphabet remains 26, paired-letter mechanism differs from single tableau. | Odd-97 final symbol policy and keyword gate. |
| D14 | Slidefair paired-letter polyalphabetic | **O** | Letter aligned in groups, not pure repeating Vig. | Odd-length handling; unknown-key controls. |
| D15 | Fractionated Morse encoded back into A–Z | **O** | ACA standard output can be alphabetic with keyed trigram alphabet. | Punctuation/spacing assumptions controlled. |
| D16 | Morbit / Pollux with final alpha rendering | **C** | Raw output digits, not 26-letter K4; explicit reversible rendering needed. | Length expansion + base conversion restrictions. |
| D17 | ADFGX / ADFGVX plus second alphabetic layer | **C** | Raw output only 5/6 symbols; standalone impossible. | Add fully defined invertible relettering step. |
| D18 | Nihilist substitution (digits) then base-26 symbols | **C** | Raw numeric output; composite may be possible. | Reject implementations without reversible 97-length mapping. |
| D19 | Straddling checkerboard / VIC-style superencipherment | **O** | Digit fractionation plus transposition + alpha rendering may hide statistics. | Independent checkerboard and relettering; complex but well specified. |
| D20 | Monome–dinome / Tridigital / numbered-key | **C** | Raw digit/limited-alphabet outputs; viable only with additional coding stage. | Account exact expansion/contraction. |
| D21 | Grandpré / checkerboard homophones (numeric) | **C** | Needs explicit mapping to 26 glyphs or more. | No silent symbol dropping. |
| D22 | 26-letter substitution layered with Polybius/fract. | **O** | Direct simple mono impossible, but inner/outer relettering changes constraints. | Use exact composition equivalence checks. |

## E. Homophones, language, codes and deliberate masking

| ID | Cipher/mechanism | Tag | Specific K4 evidence or constraint | Useful differentiating test |
|---|---|---|---|---|
| E01 | Fixed one-to-many homophonic substitution in place | **C** | One ciphertext symbol decoding consistently cannot yield both different known letters (L02). | Position-varying tables or transposition only. |
| E02 | Homophonic substitution then unknown transposition | **P** | R66 L155 ruled out selected routes; other routes/tables remain. | R66 gate was only 14/20; improve controls. |
| E03 | Stateful homophonic tables cycling over time | **O** | Flat frequencies and repeated-cipher-letter ambiguity plausible. | Finite number of tables; sealed controls. |
| E04 | Polyalphabetic homophones with marker/escape symbols | **O** | Bound number of alternatives and escape cadence. | Track length and invertibility exactly. |
| E05 | Nomenclator: token/codeword dictionary | **U** | Long plaintext may be recovered semantically, but arbitrary dictionary fits anything. | Only test with independently available codebook. |
| E06 | Syllabary / word-code then alphabetic rendering | **O** | ACA syllabary codes often need 2-symbol groups; K4 odd length complicates. | Fixed odd-length convention, published-independent codebook. |
| E07 | Condi / Compressocrat / word-frequency recoding | **O** | Hand-solvable but requires precise contextual rule. | Synthetic exact example, distinct from Quagmire. |
| E08 | Phonetic English with German/Dutch-like orthography | **P** | Past language/misspelling searches found no candidate (L62–L69, R60). | Only via a reversible mapping with known error distribution. |
| E09 | Code-talker-like English coverwords for secret meaning | **U** | The covertext can be valid English yet semantic code can be independently arbitrary. | Look for deciphered *surface* English before semantics. |
| E10 | German/Dutch source language as intermediate key/mask | **O** | English final message is compatible with a foreign-language *key* or intermediate code. | Separate key-language and plaintext-language controls. |
| E11 | Intentional spelling changes, nulls, separators | **P** | K1–K3 contain misspellings; null/orthographic scans done only narrowly. | Fixed emission grammar; do not fit after clue checking. |
| E12 | Null insertion/deletion/skip masks | **P** | L81–L83 checked periodic/marked subsets; general masks open. | Limit entropy and reconstruct original length. |
| E13 | Reordering or hiding words before letter encryption | **O** | English word frequencies disappear after deliberate word shuffle. | Score order-free candidate then recover independent route. |
| E14 | Plaintext word-boundary keyed updates | **O** | Word boundaries are not visible in K4 ciphertext. | Latent segmentation + state-update decoding. |
| E15 | Semantic/narrative shift after ordinary decoding | **U** | An English solution may contain second-layer meaning independent of cipher. | Do not confuse meaning with cryptographic evidence. |
| E16 | Acrostic/telestich/letter selection before encryption | **O** | Can create 97-letter stream after longer source text. | Exact selection grammar and external source. |
| E17 | Morse, punctuation and typography as intermediate code | **O** | Physical panels and dots/dashes may give an independent stream; earlier K0 tests narrow. | Pre-register reading order from artifact, not K4 clues. |
| E18 | Custom 26-symbol keyed substitution schedule | **O** | Scheidt called the masking technique potentially unfamiliar. | Small reproducible human-operable state grammar. |
| E19 | Unusual word-order punctuation (X/Q, spacing) | **P** | R43/R60/R84 and earlier work scored such forms, not an unlimited language class. | Holdout variants without target-driven adjustments. |

## F. External keys, physical mechanisms and cryptographic limits

| ID | Cipher/mechanism | Tag | Specific K4 evidence or constraint | Useful differentiating test |
|---|---|---|---|---|
| F01 | One-time pad with 97 independent letters | **U** | Always invertible for any intended text; no ciphertext-only discrimination. | Requires independently sourced pad/key; otherwise no useful brute force. |
| F02 | Published or handmade finite pad generator | **O** | If generative seed/edition is externally known, a constrained OTP-like family is testable. | Small key domain, no padding fit from clues. |
| F03 | Pseudorandom stream cipher / nonlinear combining | **O** | Circa-1990 or earlier designs possible; keyspace typically enormous. | Identify physical/technical evidence and finite seeds first. |
| F04 | Physical strips/wheels (Jefferson, M-94, M-138) direct | **C** | Nonzero per-strip offset yields no same-letter mapping in place, conflicting with aligned published self-matches. | Composite/position permutation could reopen. |
| F05 | Multiple rotating disks with time-dependent offset | **O** | R87's single regularly stepped rotor does not cover arbitrary wheel trains. | Mechanism-driven controls, not broad blind guessing. |
| F06 | Sculpture KRYPTOS tableau sampled along a path | **P** | L20/L50 narrow paths and arithmetic stepping checked. | Use only independently documented geometry. |
| F07 | Carved row, reverse side, literal letter layout | **P** | R68/R69/R72 and K3 analogues; historical signs/paths not fully known. | Independent transcript comparison before modeling. |
| F08 | 24-face clock, timestamp and city-index machine | **P** | Clock-derived running keys and fixed paths checked; reconstruction uncertain (L25/R49). | Only independent physical reconstruction; clue-derived selection barred. |
| F09 | World maps, compass or bearings as key schedule | **P** | Geography tests limited; K4 plaintext clues cannot choose geometry in blind run. | Independent artifact-based paths. |
| F10 | Paper spreadsheet, ruler, turntable or hand slide | **O** | Hand construction could conceal an unusual reversible alphabet permutation. | Document exact physical operations as code. |
| F11 | Book/location/code page number map | **U** | Unbounded until independently identified edition, offsets, and transform. | Prehash source; do not pick a passage because of published clues. |
| F12 | DES/block encryption then letters/base-26 | **O** | Not formally impossible, but needs explicit binary framing and 97-character transport. | Low prior without era/art evidence; avoid open-ended search. |
| F13 | Hash-only / one-way transform | **N** | Cannot recover a unique plaintext without extra structure; not a usable decryption method alone. | No key-recovery experiment; demand reversible composition. |
| F14 | Artist-specific multi-layer recipe (2–4 stages) | **O** | Sanborn/Scheidt descriptions leave possibility of nonstandard masking; avoid unrestricted combinations. | Grammar with bounded description length + unknown-family gate. |
| F15 | Carving/transcription error or layout offset | **P** | R83/R87/R88 test selected one-/two-letter clue errors; other errors cannot be assumed. | Independent visual provenance, no post-hoc fixes. |

## What the inventory means

### Strongest new mechanism research clusters (not a ranking of true likelihood)
1. **Coupled/nonlinearly evolving substitution**: B03–B07, B11–B13, B16–B18, A06–A07, A14, A20. Shared, compact state is what makes an otherwise free alphabet hypothesis testable.
2. **Transposition order and physical stage**: C03–C11, C15–C19, E13. Must be controlled for exact non-equivalence to existing L47/R68/R76 scans.
3. **Word/orthographic mask before encryption**: E08, E10–E14, E18–E19; avoid presuming foreign *final* plaintext when Scheidt said the material was English.
4. **Compact polygraphic/fractionating cipher that outputs 26 letter symbols**: D05, D07–D08, D10–D15, D19. Avoid smuggling arbitrary codebook mappings into a search.
5. **Unrestricted OTP, arbitrary per-slot alphabets, free permutation/key**: A19, C20, E05, F01, F11. These can fit any target; **not useful K4 cipher searches** absent independently supplied construction constraints.

### Coverage matrix for classical ACA named families
The ACA cipher catalog includes roughly 60 entries, some educational variants or paired-message 'Twin' problems. The table above separately covers their core transformations: AMSCO C06; autokey A12–A14; Bazeries D12; Beaufort A02; Bifid D06–D08; Cadenus C13; checkerboard D21; columnar C01–C04; Compressocrat E07; CONDI B16/E07; CM Bifid D08; Digrafid D10; Four-square D01/D03; fractionated Morse D15; Grandpré D21; grilles C11; Gromark A16/A07; Gronsfeld A04; Headlines/book codes E05/F11; homophonic E01–E04; interrupted keys A15; key phrase A01/E07; monome-dinome D20; Morbit/Pollux D16; Myszkowski C05; Nicodemus C03/C15; Nihilist substitution D18 and transposition C12; nulls E12; numbered key D20; periodic Gromark A16; Phillips B14; Playfair D01/D03; Porta A04; Portax D13; progressive A05/A17; Quagmire A03/A05/A06; Ragbaby A21; railfence/Redefence C01/C16; route C01/C07–C10; running key A08–A11; sequence C15; seriated Playfair D02; Slidefair D14; Swagman C14; syllabary E06; Tridigital D20; Trifid D09; Tri-square D02; two-square D01/D03; variant A02; Vigenere A02. Twin Bifid/Trifid are paired-cipher conditions, **not** a standalone one-message K4 algorithm; a future K5 ciphertext could make paired-message methods genuinely relevant.

### Caveats that prevent false exclusions
- **Exact setting** is an exact conclusion only if its equation, source, word positions and scope are correct and the independent reviewer signs. R87/R88 still need independent-model replay. Do not call an entire general rotor or Quagmire family eliminated.
- **Family-wise null comparison** is required when scanning many methods. A p=0.04 chosen after searching 40 families is not persuasive; compare the maximum of all families for K4 to the maximum from every decoy.
- **Positive controls** must hide family, key and plaintext simultaneously. A known-key free-alphabet solver is not an unknown-family K4 recovery system.
- **English mask hypothesis** must specify a bijection, grammar or reversible mapping. Arbitrary post-hoc 'sounds Dutch' transformations are untestable.
- **Any 97-character candidate can be encrypted to K4 with an arbitrarily fitted pad**; forward encryption alone is not evidence. A derived key, reproducible complete text, and postfreeze validation are essential.
- **Physical keys derived from the released phrases are not allowed in blind generator selection.** A context study may discuss historical artifacts, but no clue-specific route, city, bearing, source keyword or positional mask may enter candidate search, training, selection, null calibration or scoring.
- **Clue-conditioned post-freeze mathematical exclusions** may be kept as an evidence class separate from blind discovery. Never recycle survivors/failed keys from those checks into the next blind search.

## Primary references and next design
- Repository: [LEDGER.md](https://github.com/tylerj-spec/kryptos-k4/blob/main/LEDGER.md), [R87](https://github.com/tylerj-spec/kryptos-k4/blob/main/r87/RESULT.md), [R88](https://github.com/tylerj-spec/kryptos-k4/blob/main/r88/RESULT.md), [guardrails](https://github.com/tylerj-spec/kryptos-k4/blob/main/audit/FUTURE_TEST_GUARDRAILS.md), [R53 blind rules](https://github.com/tylerj-spec/kryptos-k4/blob/main/r53/BLIND_RULES.md).
- [American Cryptogram Association: cipher types](https://www.cryptogram.org/resource-area/cipher-types/) — historical hand-cipher coverage.
- [CrypTool NCID: comparison of 51/56 classical identification classes](https://legacy.cryptool.org/en/cto/ncid.html) — method-classification controls.
- [WIRED 2005 Scheidt interview](https://www.wired.com/2005/01/inside-info-on-kryptos-codes/) — English hidden by masking, mechanism may be unfamiliar.
- [Scientific American 2025 Sanborn interview](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/) — creative interpretation; 'not necessarily math' is not a cipher proof.
- [Associated Press 2025](https://www.ap.org/news-highlights/spotlights/2025/kryptos-final-code-remains-unsolved-the-cia-sculptures-creator-is-auctioning-the-solution/) — plaintext discovery does not establish method/key.
- Proposed focused experimental design: [R89 multi-family identifiability study](./R89_MULTI_FAMILY_EXPERIMENT_DESIGN.md).

**Independent review: NONE. This is a hypothesis catalog. No K4 decryption was performed to create it.**
