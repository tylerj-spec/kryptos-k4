# Kryptos K4 — Master Technical Handoff for a Coding/Research Agent
**State as of 2026-10-26, after 28 collaboration rounds between ChatGPT and Claude.**

## 0. Your job and operating rules

Continue an evidence-driven effort to decrypt the 97-character Kryptos K4 section. The user's objective is an independently justified, complete, **readable** plaintext and a reversible cipher procedure—not a plausible sentence produced by fitting arbitrary substitutions. **No solution has been established or submitted.**

The user explicitly welcomes (a) readable English written with intentional Dutch-, German-, Frisian- or other Germanic-looking phonetic spellings; (b) mixed-language vocabulary; and (c) a historically motivated extra masking or null-letter layer. Do not throw out partial candidate text merely because an English language scorer rejects it. **Show the user all promising raw 97-character strings, unchanged**, alongside optional proposed segmentation, translations, spelling interpretations and uncertainty. Interpretations must never replace the raw ciphertext-derived letters. The user particularly wants to inspect clue-compatible outputs with recognizable fragments. Never submit a candidate to the external/paid Paradigm verifier without explicit permission.

**Rigor:** pre-register the mechanism, exact search space, constraints and selection thresholds before running a large search; use planted positive controls, matched negative controls and independent forward re-encryption. Count independent crib equations/cycles and forced *non-clue* letters, not merely the number of compatible free-alphabet parameter settings. Report exact mathematical exclusions separately from statistical disfavor and mere feasibility. Track multiple testing and post-hoc discoveries. Deduplicate sign-equivalent variants when both alphabets are unrestricted. Cache source text with provenance, edition, date, normalization and SHA256. Preserve all earlier work in the cumulative research ledger; do not blindly rerun exhausted families.

## 1. Immutable K4 input

**Ciphertext — exactly 97 uppercase A–Z characters:**

```text
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

**Published plaintext clues — EXACT final plaintext positions, not guessed cribs:**

| 1-based positions | 0-based inclusive | Ciphertext slice | Required plaintext |
|---|---|---|---|
| 22–34 | 21–33 | `FLRVQQPRNGKSS` | `EASTNORTHEAST` (13 letters) |
| 64–74 | 63–73 | `NYPVTTMZFPK` | `BERLINCLOCK` (11 letters) |

`NYPVTT` at positions 64–69 decrypts to `BERLIN`. The two clues fix 24 letters; 73 plaintext positions remain unknown. Use them as **output-position constraints regardless of language**. There are only 13 distinct letters among the 24 plaintext clue positions, leaving much of a free plaintext alphabet unconstrained. K4's ciphertext uses all **26** letters. It contains only two `E` characters, while the required plaintext clues alone use three `E` characters. Preserve the originally transcribed ciphertext unless explicitly investigating a bounded typo/correction hypothesis.

**Verification gate for any serious candidate:** show the complete unmodified plaintext P of length 97; show a compact, reproducible cipher recipe and key **determined without constructing them backward from P**; demonstrate that encrypting P yields the exact 97 ciphertext letters; preserve all 24 anchors; and compare the candidate against matched decoys from the exact same search procedure. A cipher with completely free alphabets can often be constructed to fit gibberish. Such a fit is not cryptanalysis.

## 2. High-confidence exclusions and invariants (read the model scope)

- **Pure transposition/permutation of K4 alone:** exactly excluded by ciphertext's 2 E letters versus at least 3 E in the known plaintext (L01). A *transposition combined with substitution* remains possible; an exact gibberish witness moves 96/97 positions and satisfies the final anchors (L55).
- **Single in-place monoalphabetic substitution:** excluded by ciphertext double `QQ` at 1-based 26–27 while plaintext requires `NO` (L02).
- **Conventional in-place short-period Vigenère/Beaufort/Quagmire/related variants:** many specific periods, alphabet pairings and operation orders exactly contradicted (L03–L05, L21, L35–L36). In an in-place fixed-bijection-per-column cipher, same-letter pairs separated by period *m* have the same equality relationship before and after encryption. K4 has unusually few such equalities relative to conventional English for numerous *m*: at period 8, `T8(K4)=14` versus ~34 for the reference English set. This **statistically disfavors** many short repeated-key models; it does not rule out every period, artificial spelling, or a transposition/masking layer (L89).
- **Columnar/route/fold families plus bounded periodic substitutions:** extensive exact negative tests, e.g. all complete columnar widths 2–10 (L06); circular, padded grid, fold and back routes (L07–L10); many double/folded/rail-fence/Myszkowski routes in two-stage sweeps (L47–L48). Results apply only to the specified permutations, keys and algebraic constraints, not all transpositions.
- **Direct Hill ciphers 2×2 to 5×5 under the tested alphabets/alignments:** excluded (L11). Selected Hill+rearrangement bounded tests mostly excluded, with only chance-level 1–3-check fits (L61).
- **Trifid with arbitrary 27-symbol cube, all 97 periods and all starting phases:** excluded by an exact duplicate-coordinate contradiction in all 4,752 nontrivial phase-period settings; independently audited (L91/L95). Standard 5×5 Playfair/Bifid/Polybius-style outputs cannot directly produce K4's full 26-letter alphabet without an added convention or second layer; Porta fails its defined half-alphabet constraints (L88). Do not overstate this as an exclusion of any modified 5×5 system.
- **Direct legacy affine-linear keystream recurrence of order 1–6 modulo 26, within specified in-place schemes:** excluded (L49). Similarly constrained Fibonacci, progressive, tableau paths and multi-clock sums of periodic keys are excluded when sufficiently checked (L13, L15, L20, L36, L50).
- **Running keys from K1–K3 plaintext, specific dated/coordinated number streams, self-key variants and carved K1–K3 ciphertext with tested alignments:** no feasible or useful matches within stated schemes (L16, L19, L90, L93). This does not exclude a different passage, the full Carter volume, an untested orientation, or a transformed source.
- **Gromark with AZ/KRY fixed plaintext alphabet and arbitrary ciphertext alphabet:** any decimal digit stream is mathematically excluded by a clue-pair rank-difference contradiction (L14). With **both** substitution alphabets unrestricted, 39 five-digit Gromark primers are clue-compatible, but English and phonetic-English recovery tests have produced no credible K4 message (L22, L69–L73). These 39 are feasibility witnesses, not a solved method.
- **Plaintext-feedback autoclave:** same plaintext/feedback alphabet AZ or KRY, two signs and lags 1–96: 127/384 exact contradictions, 257 complete feasible witnesses; different plaintext/feedback alphabet: **115/384 exact contradictions, 269 feasible witnesses**. In the mixed case, 188/269 feasible cases have zero repeated-anchor chain checks. Long lags often allow arbitrary pseudo-English fits; short lag 12–22 searches did not recover meaningful K4 plaintext (L27/L52/L58). The model family beyond these assumptions remains open.

## 3. Statistically interesting leads that did NOT hold up

- **GF(13) after-transposition high-check anomaly:** huge L47/L54 search produced 63 five-check and 11 six-check matches (`T=74`). A preregistered 200-shuffle follow-up had **13/200 shuffled K4 ciphertexts score at least as high**, one-sided Monte Carlo `(13+1)/(200+1)=0.06965`; not significant under its registered primary criterion. This was independently sampled/audited; do not revive an earlier 24-shuffle p≈0.04 without acknowledging the later null (L56/L57).
- **K3-style rearrangement + non-repeating five-digit Gromark:** 20 routes × 2 operation orders × 100,000 primers = **4,000,000 settings**, 65,968 compatible under two free alphabets. However independent clue cycles are mostly 0–2. On a frozen 100k-setting subsample K4 had 1,604 compatibility hits; 20 letter-count-preserving K4 shuffles averaged 1,571.3, empirical p≈0.524. **No discriminating signal**; does not exclude a different transposition or key source (L94).
- **Clock/compass 48-state two-free-alphabet models:** 484/19,200 labeled assignments compatible, but no more unusual than 64 letter-preserving ciphertext controls (empirical p≈0.569). Many fits arise from unconstrained alphabets. The 484 completions are speculative and not independently legible plaintexts (L75/L76).
- **Lag-22 negative-feedback autoclave with AZ:** the 24 clue letters *conditionally force* an `X` immediately after `BERLINCLOCK` at plaintext position 75. Independent algebra checks this. Across 150,000 letter-preserving shuffled K4 nulls, 18 also forced this X, and across 150,000 iid ciphertexts, 33 did. **The setting was selected post hoc after many trials**; this is a conditional structural curiosity, not corrected statistical proof of the cipher. No readable K4 at lag 22 (L63/L65).

## 4. Non-English/plaintext-masking work: the user's main interpretive interest

**Working hypothesis:** final P might be English in normal English order with intentionally nonstandard Dutch-, German-, Frisian- or similar *orthography*; perhaps some genuine German words and a deliberate deletion/null or X/Q punctuation layer. A sentence entirely in Dutch/German is less favored by the 2005 Ed Scheidt interview, where he said all four sections used English and K4's English statistical signatures were deliberately masked; Sanborn might still have altered spelling or text. The two fixed clues are English letter sequences in every hypothesis.

- Multilingual text screens (Dutch, West Frisian, Low German/Saxon, Swedish and German) over earlier search results, autoclave and running-key models returned **no K4 candidate**. Early models were based on only ~5k characters of authored text per language. Later rescoring used publicly sourced Nescio Dutch prose, Frisian/Dutch code-mixed material, Low Saxon, Swedish and German corpora; no convincing result. All language scores are population-dependent, never mathematical exclusions (L62–L64).
- **Spelling-aware English model:** 25 distinct synthetic 97-letter modified-English examples preserving both anchors: baseline English word gate accepted 5/25 whereas a small prespecified spelling-tolerant model accepted 25/25. This establishes that traditional word scorers can miss readable unconventional English, **not** that any synthetic sentence is K4 plaintext (L66).
- **Blind test on newly encrypted examples, known five-digit primer:** enhanced spelling-aware solver got 3/16 exact vs baseline 0/16; but its mean accuracy on the 73 unknown letters fell from 60.70% to 56.51%, and 652/2,560 wrong-output scores increased (L69). Independent audit and fresh larger S2 blind tests narrowed the claim: readable results were 14/20 for ordinary English, 10/14 for dictionary-known modifications, and **7/20 when spelling modifications were held out/unknown**. Search and score overfitting remain a serious issue (L70/L71).
- **Apply S2 to actual K4:** 39 feasible Gromark primers searched, none reached readable score; K4 best `W=-141.82` vs strongest calibrated readable/wrong-key bar around `-114.93` (specific scorer/protocol; scores from other models are not interchangeable). This is negative evidence against *that model plus readable English*; not a universal failure bound for unknown phonetic rules (L72/L73).
- **Salt/null theory:** bounded arbitrary deletion of up to eight letters outside the 24 anchors, periodic deletion, Gromark primer-digit null markers, and spelling-aware deletion attempted on G4/G7. G4 covered 21 of 73 unknown-position characters in 4+-letter dictionary words; **157/1,200** verified known-wrong outputs did at least as well. Orthographic extension: **190/1,200** wrong outputs ≥ G4. G7 got 17/73, and 330/1,200 wrong outputs ≥ G7. These are exploratory correlated controls. No independent historical rule yet selects the supposed nulls (L81–L87).
- Null deletion alone cannot make `VIFTZ` into `IFITS` or `WEIT` into `WENT`. German `GAB` is legitimately “gave”; German `WEIT` is “far/wide,” not “went.” Interpretation, translation, edits and deletion are different operations and must be separately costed.
- K2/K3-style `X`/`Q` punctuation masking was proposed with a preregistered plan (L87), but **not executed** as a substantive recovery experiment. It remains a useful bounded next test.

## 5. Trial strings that the user wants to see, not authenticate

These are 97-character Gromark **optimizer completions** consistent with the 24 clues under *fitted* free alphabets. Raw letters must be retained exactly.

**G4, five-digit primer `98850`:**

```text
VIFTZJAMESWEITGABALLNEASTNORTHEASTRIJAATIOGLEAKCITYANOHUEPROWARBERLINCLOCKABUVYIFITOHUMDOESDUKSLB
```

**G7, primer `60319`:**

```text
SANJESBUDBEORMUNICHAFEASTNORTHEASTQUHEANDSLIPRDXVASHAESFRAJOFIPBERLINCLOCKJURYXPEGGRADNLBDIJARDIX
```

G4 highlights: JAMES, WEIT, GAB, LEAK, CITY, PROWAR, IFIT, DOES. G7: MUNICH, AND, SLIP, JURY. These are actual substrings, but optimizers explicitly favor word-like results. Under G4's exact primer, **34/97** letters are mathematically forced by the 24 clues—only 10 extra letters. Under G7 **29/97**—only 5 extra. G4 `JAMES` has just **1/5** forced; `WEIT` 1/4; `GAB` 1/3; `CITY` and `DOES` 0. G7 `MUNICH` and `JURY` are **0** forced. A separate completed assignment under the same primer can change LEAK→LMAP; another can change JURY→BHRJ. Further solver restarts did not reproduce JAMES or MUNICH in 512 runs each (L85/L86). Thus **neither is verified plaintext**, though the user should be able to inspect and annotate them.

An earlier source-key trial (not a solution) was:

```text
LUINMMWWWOLDIISGRVUELEASTNORTHEASTAPPIFCIKUZATCYHMHETHANHOYTYOHBERLINCLOCKLKINUTRFIVPWHALLIESRENO
```

For review outputs, show candidate ID, exact P, method, external key/primer, 24/24 anchor pass, 97/97 re-encryption pass, independent extra forced letters, independent clue cycles, true-text score, null rank/p-value, and a separate human-readable annotation. Distinguish the 39 Gromark winners from the 484 clock completions in Round 23 (523 displayed labels overall).

## 6. Historical research and physical-key data (preserve uncertainty)

**Berlin World Clock:** the `BERLINCLOCK` clue has been linked in reporting to the Urania World Clock at Berlin's Alexanderplatz, designed by **Erich John**, opened **30 September 1969**, not the separate mathematical light-display Berlin Clock by Dieter Binninger. John worked in German-speaking East Germany; this motivates looking at German spelling/engraving but does not establish German plaintext. It has **24 time-zone faces** with engraved city names and (historically) a compass-rose pavement. Earlier user+Claude work reconstructed a **360° face map** from dated photographs, with upper and lower city lists and confidence labels for each uncertain inscription.

Estimated original orientation: Berlin's +1 face roughly **177°** (south), the **+8 face near ENE** (~72°, vs compass ENE 67.5°). The exact orientation, some 1988–1990 inscriptions, time-ring phase and whether Sanborn intended this relationship remain **unproven**. The drum's hour markings move with time of day, so no fixed hour-number key can be assumed without the clock's depicted time. The 1969–72, ~1980–90, and post-1997 city panels differ; **do not silently use modern names**. Example pre-1997 +1 upper row: `AMSTERDAM BERLIN BRÜSSEL BUDAPEST MADRID PARIS PRAG STOCKHOLM WARSCHAU`; +8 upper `IRKUTSK ULAN BATOR`, lower `PEKING SHANGHAI MANILA`. The earlier 1988–1990 map is partially composite and flags sources. See `sources/world_clock_360.md`, `sources/2026-10-22_world_clock_and_sources.md` in Round 23.

Extensive bounded physical-key tests already performed, without a signal: city lists as running key (56M+ settings in a previous sweep, best 8/24 anchors); face-specific keyword alphabets; face-hour letter picks; 24-column drum readouts; compass 48-state patterns; keyword columnars; estimated ENE vs Berlin starting faces; 42-character distance between the two anchor starts divided by seven face offsets = **six characters per face**, 0/25,760 specified settings; speculative 97=4×24+1 structure, 0/13,056 sufficiently sourced settings (L25, L37–L42, L75–L79). Historical clock mechanism is **still open outside those precise tested rules**.

**Exploratory geography, NOT a confirmed cipher clue:** A due WSW (247.5°) ray from the World Clock passes close to Bebelplatz (book burning) and the former Führerbunker site; the WSW-line direction could be relevant if K4 describes a place ENE/WSW of the clock. A Mercator/rhumb-line bearing between Langley and the Yasenevo intelligence complex crosses close to the clock, but a great-circle route does not, and the map projection/endpoints were tried after the fact. Matched word/landmark tests showed no reliable signal (L43–L46, including L44b). **Do not promote these alignments to an encryption key absent independent evidence.**

**Carter book source:** K3 draws on Howard Carter's Tutankhamun account. The correct candidate is **Howard Carter and A. C. Mace, *The Tomb of Tut-Ankh-Amen*, Volume I, Cassell 1923**. A scan is catalogued at:
- `https://openlibrary.org/books/OL6661682M/The_tomb_of_Tut.ankh.Amen`
- `https://archive.org/details/tomboftutankhame01cart`
- `https://en.wikisource.org/wiki/Index:The_tomb_of_Tut%27Ankh%27Amen_(London).djvu`

A reliably normalized **complete book text has NOT been retrieved or tested**. Only authenticated **excerpts** (Carter's 1923 account, 1922 diary and later lecture) were run as source-key windows in R27: 4, 2, 3 compatible unique settings respectively; none exceeds 80 matched shuffled-text controls (empirical p≈0.136, 0.333, 0.148). The 1923 book *Tutankhamen and the Discovery of His Tomb* by **G. Elliot Smith** is not the Carter/Mace volume; do not substitute it.

**Kryptos Morse/K0:** a 1999-photo-backed text transcription is at `https://rumkin.com/reference/kryptos/k0/`. It includes standalone `E` marks that earlier cleaned transcriptions can lose. R28 reconstructed 106 plaintext Morse letters, tested **three provisional concatenation orders** (true geographic reading order not verified), reversed keys, AZ/KRY numberings, 97-letter windows and five fixed route variants in two operation orders. One fixed alphabet: 0/8,640 source-key settings; both alphabets free: 24/1,080 mathematically compatible but **zero independent crib cycles** and no shuffled-source excess. Dot/dash stream (238 marks, regenerated from decoded letters, not raw plate transcription): 0/122,688 one-fixed-alphabet and 0/15,336 both-free settings with tested simple encodings. All planted controls passed. No K4 candidate. Physical Morse spacing/isolated marks, alternative reading order and more elaborate transformations remain open (L96/L97).

**Scheidt/Sanborn source caution:** a 2005 WIRED interview attributes to Ed Scheidt that all four plaintext passages were in English but K4 deliberately masked English characteristics with a special technique. Oral accounts favor a direct letter relationship between ciphertext/known plaintext, but final-position anchors alone cannot prove no transposition. Treat historical quotations and the reported physical clues as priors, not algorithm specifications. No unverified public “97/97” plaintext claim should be trusted merely because a key is derived backward from its chosen plaintext.

## 7. Reusable tools, data, and provenance

The master cumulative research inventory is **`LEDGER.md`**, entries **L01–L97 plus L44b**, updated through Round 28. Status legend: `EXCL` exact contradiction within a named model; `FEAS` a complete model witness (may be gibberish); `SCORE` dependent on trained text; `STAT` statistically unfavorable/indistinguishable; `WEAK` too few independent constraints; `OPEN` unresolved. Whenever possible link a new experiment to existing rows rather than overwrite scopes.

**Useful existing files by archive** (all were created during this conversation, though an agent needs copies mounted/uploaded to execute them):
- **R26 Claude ZIP**: `claude/r26/key_oracle.py` exact two-free-alphabet known-keystream feasibility; `solver_s2k.cpp` cipher-aware English/spelling search; `period_repeats.py`; `trifid_any.py`.
- **R27 ChatGPT ZIP**: `r27_audit.py`, `r27_route_chunks.py`, source-key tests and nulls, `CANDIDATE_REVIEW.md`, `verify_packet.py`, audited R26 handoff.
- **R28 ChatGPT ZIP**: `r28_morse_experiment.py`, `r28_morse_pulses.py`, `R28_RESULTS_FOR_REVIEW.txt`, 98-entry cumulative ledger (L01–L97 plus L44b) and reproducible JSON results.
- **R23 ChatGPT ZIP**: city-name/photo map, `clock_position.py`, `clock_six.py`, `clock_4x24.py`, `two_free_clock.py`, `REVIEW_OFFLINE.html`, `ALL_REVIEW_STRINGS.csv`.
- **R21 Claude ZIP / R20 ChatGPT ZIP**: phonetic/spelling-aware benchmark fixtures, S2 trained word model, `word_model_orth.tsv`, `quad_log10.f32`, R20 recovery protocol, true-primer and wrong-primer controls.
- **R24 ChatGPT ZIP**: `r24_null_probe.py`, G4/G7 raw-and-interpretations and matched negative controls. **G4/G7 forced-letter audit ZIP** separately preserves primers, assignments, alternate readings and validator.
- **R13–R16 archives**: L47/L48 route catalogs, L54–L57 GF13 high-check data/nulls, L58 mixed-autoclave exact feasibility and witnesses, `two_step.py`, `l56_null.py`.

Many of these are large (up to millions of outputs). Do not use a file name as proof of a run: check executable/version, seeds, SHA, control results and exact tested scope; independent replay before treating a result as authoritative. Treat saved optimized text as *generated* candidate data, not independent evidence.

## 8. Proposed next coding-agent work: actionable priorities

### Priority A — Set up a clean, auditable search framework
1. Load ciphertext and exact anchor mask. Unit tests: length 97; 24 fixed letters; full 26-character ciphertext inventory; `c[63:69] == NYPVTT`; test G4/G7 raw strings exactly when supplied with their fitted alphabets. Separate `source_text`, `ciphertext`, `key`, `cipher_model`, `alphabet_mapping`, `transposition_route`, `raw_plaintext` and `human_interpretation` in every result.
2. Implement a **unified keystream feasibility oracle** for `c_i=CA[(PA^-1(p_i)+k_i) mod 26]` and Beaufort variants, fixed or arbitrary PA/CA. With both PA and CA completely free, **+/- sign versions are isomorphic** by reversing both alphabet coordinate numberings (L92), so deduplicate. Provide graph/cycle rank, contradiction certificates, minimum forced positions and full validated witnesses.
3. Implement a *blind* decoder benchmark: hidden corpus plaintext, fixed pre-registered spelling rules, source-key/primer held secret unless testing known-key, multiple seeds and matched wrong keys. Score raw strings independently under multiple language models; train/test split by document; calibrate **the maximum after searching** on controls run through the identical pipeline.
4. Export a human-review HTML/CSV view of exact 97-letter P, with anchors highlighted, optional speculative word splits/phonetic translations/null deletions, and explicit edit costs. Keep raw bytes immutable; never auto-correct the candidate. Record interpretation votes and provenance separately.

### Priority B — Acquire and test **complete, edition-verifiable** source texts
5. Obtain the actual **Carter/Mace 1923 Volume I** OCR/transcription and verify against page scans for the passage K3 quotes. Document edition and exact punctuation, retained/dropped X/Q, and normalized text plus SHA. Do not use a different author/book. Use all source windows and reversed windows; preselected reading variants; one-fixed vs two-free alphabets; 80+ source-inventory-preserving shuffles; positive controls. On feasible windows, run `solver_s2k` with matched random **feasible** wrong keys, and report how many *independent clue equations* each key yields.
6. Obtain photographed plate-level **Morse inscription ordering**, including E separators and dot/dash spacing. Correct historical physical arrangement first, then precommit alternate defensible readings. R28 only used three provisional orders and reconstructed pulse marks; do not claim the entire Morse method was eliminated.
7. Freeze a **single 1988–1990 World Clock** upper/lower city-list reconstruction with confidence labels from dated photographs (do not mix later plates unmarked). Propose and preregister ONE physically constrained mapping from clock bearing/face sequence/engraved spelling to key stream, including time-ring phase. Demand at least **three independent non-clue relations** before language optimization. Try German-name orthography and English phonetic readings as separately labeled transformations.

### Priority C — Model a real disguising operation
8. Execute the **unrun L87 X/Q separator and optional limited-null rule** on hidden positive messages first. Use historically documented placement logic (e.g. a time-zone face/interval, a true key digit, or K2/K3 punctuation), never arbitrary post-hoc deletion to form words. Run the same search on G4/G7 and known-wrong controls. Count substitutions, translations, insertions, deletions and boundary changes explicitly; test learned/held-out phonetic rules and reject methods that merely overfit wrong decodes.
9. Try a **two-stage cipher** only when its source key and route are both specified independently of desired plaintext: e.g. K3-documented transposition with an independently sourced nonrepeating book key. The R27 4M 5-digit Gromark two-stage sweep was not a signal. Require enough independent clue cycles and at least one newly *predicted* plaintext letter, not a free-alphabet completion.
10. Treat carving errors as a sensitivity branch, not a default escape. Preserve original ciphertext and disclose every changed letter/position; previously tested one-/two-clue error tolerances already show many short-period exclusions survive (L35).

### Acceptance / stopping rules
- **REJECT within scope** if necessary algebraic constraints fail (with reproducible certificate). Do not mark a broad cipher family excluded just because one alphabet or route fails.
- **HOLD for human inspection** if a complete 97-letter candidate re-encrypts, preserves both anchors, and shows independent non-clue structure; supply exact raw text and separate interpretation, even if spelling is strange.
- **PRIORITIZE** only if a prospect has *pre-specified* historical/physical key provenance, multiple genuinely independent clue relations, convincing context/grammar or systematic phonetic English, recovery on blind held-out tests, and a favorable matched-search null result. A simple word or many fitted alphabet assignments is insufficient.
- **CLAIM SOLVED** only when the method and authentic full plaintext are independently verified and explain all 97 letters, not just the clues or hand-picked fragments. **Never submit to a paid/public validator without user authorization.**

**Immediate first task to execute:** inspect the latest `LEDGER.md` and the R26–R28 oracles; acquire the genuine complete Carter/Mace 1923 Volume I before any book-cipher claims; in parallel implement the unrun X/Q+limited-null blind test and a human-review candidate table. Return an evidence table with exact tested scope, positives/nulls, forced extra plaintext, raw 97-character candidate strings if any, and a clean updated ledger. Avoid another unconstrained sweep with fewer than three independent crib constraints.
