# R78b: reversible masking mechanisms, and what the previous work does and does not cover (Claude Code, Fable, 12 Nov 2026)

**Assignment** (Tyler, relaying ChatGPT's R78 review): identify a reversible masking or preprocessing mechanism that
could hide English statistics and still let a person decrypt K4 with a constructed key or a physical aid; do it
independently of R79; analyse the previous work as well.

**Status.**
- Reasoning and proofs, one pre-registered ciphertext-only test (T-REC: `r78/PREREG_TREC.md`, commit 21bb5f4, run
  after it), and one synthetic table of predicted letter evenness.
- No decode was run. No published K4 letter is used in any script, test or argument here.
- Connectors used: Wolfram (exact values for `r78/FABLE_ANALYSIS.md` §1.6) and alphaXiv (one literature search and
  one paper; §B9).

**No mechanism is identified.** This file narrows the question and says what to build. Part C gives the ranking.

## Findings in brief

| # | Finding | Kind |
|---|---|---|
| 1 | Every mask that leaves letters in place is a key process: mask plus cipher is one polyalphabetic cipher (Theorem M1). "Masking" is then not a separate object to find; the open question is which state rule | Proof |
| 2 | Hiding letter frequencies completely on one tableau needs key letters that are evenly spread over all 26 values (Lemma M2). A single short keyword cannot do it, however its letters are ordered; feedback and two layers can | Proof + synthetic table |
| 3 | A whole non-additive class is now tested without any key: alphabets re-ordered by recency (the used letter moves to the front or the back). The recency ranks of the ciphertext are then a simple substitution of the plaintext. K4 scores below all 2,000 planted messages: **disfavoured** (ledger L168) | Proof + run |
| 4 | Every mask whose state comes from the position and the earlier ciphertext reduces to one solver with a computable slot map (Theorem M3). The search over such masks is a search over simple state rules; a library is specified | Proof + design |
| 5 | The most literal reading of "mask, then encipher" is two keyword stages on different tableaux with unknown keywords. The repo has never run a blind solver for it, only word lists and a crib check. A solver is specified (§B7) | Gap + design |
| 6 | Previous work: 167 ledger rows cover the standard alphabets against almost every textbook key process, one process at a time. The gaps are combinations (keyword with feedback), text-driven key movement, unknown keyword pairs, and unknown alphabets with a non-repeating process (Part A) | Analysis |

---

## Part A. Analysis of the previous work (ledger L01–L167)

### A1. What kind of result each row is
| Kind | Rows (examples) | What it rests on |
|---|---|---|
| Exact exclusion from the published letters | L02–L09, L13–L17, L21, L36, L49, L88, L91, L134–L136, L141, the R75/R76 exact checks | The 24 published letters at their positions; the stated order of operations; the transcription |
| Exact exclusion from the ciphertext alone | L01 (letter counts), L167 (sum invariant) | The model only |
| Strict-blind fixed-method scans, frozen before any comparison | L111, L114, L115, L118, L121, L122, L124, L126, L127, L129–L131, L165, L166 | The listed methods only: "excluded for these fixed conventions" |
| Blind solvers with a sealed gate, no signal | L149 (unknown English running key), L150, L152, L153, L155, L157, L159, L163, L164 | The gate's recovery rate; a statistical statement, not an exclusion |
| Ciphertext-only statistics | L32, L89, L137, L160; R78's T-RK; T-REC (L168) | A stated text population |
| Feasible but unreadable | L22, L27, L58, L59, L72, L76, R75 F1X, R76 H1X | Shows the model cannot be decided at 97 letters, not that it is wrong |

### A2. Coverage by key process and alphabet
"Std" = the four alphabets A–Z, KRYPTOS, PALIMPSEST, ABSCISSA. "One free" = one side arbitrary, the other from a
short list. Message in place unless stated.

| Key process | Std alphabets | Wider alphabets | Rows |
|---|---|---|---|
| Repeating key | Closed, periods 1–26 and 30–52 | Any per-slot alphabets at 19 periods; 77,229 keyword alphabets, periods 2–52 (weak above about 20) | L03, L04, L21, L53, L89, L166 |
| Progressive; linear recurrence; chain addition | Closed | Chain addition with keyword alphabets; two free alphabets feasible, unreadable | L13–L15, L49, L102, L111, L129–L131, L141, L143, L22, L72 |
| Autokey (ciphertext or plaintext) | Ciphertext: closed to lag 67. Plaintext: about a third of the settings excluded, the rest feasible and unreadable | One free alphabet | L17, L18, L27, L52, L58, L59, L144 |
| Running key, named texts | Closed or no candidate for K1–K3, Carter, five named books, the World Clock | Both alphabets free for a given key | L16, L19, L37, L90, L93, L106, L159 |
| Running key, unknown text | No signal (blind solver, gate passed) | Not solvable | L31, L149, L152 |
| Sums of repeating keys | Closed where 3 or more checks | — | L36 |
| Two keyword stages on different tableaux | Word lists blind; any keys by crib check, feasible and unreadable | — | L165 |
| Irregular use of one keyword (trigger letter, held, word ends, grid, route-scrambled) | Closed or no signal | Grid and route forms: std only | L162, L163, L165, L166 |
| The message as its own key | Sum invariant closes two thirds of the same-alphabet forms | Mixed forms open | L167 |
| Key read off a physical object | Closed within the reconstructions | — | L25, L39, L40, L50, L75–L79, L96, L97 |
| **Keyword plus feedback** | **Not tested** | — | — |
| **Key moved by the text, every letter its own step** | **Not tested** | — | — |

| Other structures | Status | Rows |
|---|---|---|
| Transposition with a substitution (routes, K3-style rotations, columnar; both orders) | Large enumerated families closed or at chance | L06–L10, L38, L41, L47, L48, L54, L56, L94, L114–L127, L135, L150, L153, L164 |
| Fractionation (Trifid, any 27-symbol cube, every period) | Closed | L12, L91, L95 |
| Pair and matrix ciphers (Playfair family, Hill) | Closed within tested forms | L11, L61, L88, L146 |
| Homophones; nulls | Homophones with a route: no signal; nulls: nothing coherent | L81–L83, L155 |
| Changing alphabets (Chaocipher-type) | One narrow form, no signal | L145 |
| Other languages and spellings | Scoring tests only | L33, L62–L64, L66–L69, L108 |
| "Masking / pre-encoding layer" as such | **Listed OPEN since L26** | L26 |

### A3. What the record establishes
1. **K4 is not any single textbook key process on the standard alphabets with the message in place.** This is the
   solid core: many independent exact checks, several re-derived by a second party (L57, L85, L95, L98, L113, L117,
   L119, L133, L142).
2. **Adding one enumerated transposition does not rescue those processes.** Billions of fixed settings, all at
   chance.
3. **Unknown alphabets on both sides cannot be decided at 97 letters** (L116, L123, L138): a wrong pair of
   alphabets can score as well as the right one. This is a limit of information, not of effort.
4. **Apparent anomalies have not survived retesting** (L128; L154, retired by L158; L160 found no family for the
   width-7 feature).

### A4. What it assumes
- **Three assumptions sit under almost every exclusion:** the published letters are at final plaintext positions;
  the last step leaves letters in place (or the stated order holds); the carving is right. L35 tests the third for
  repeating keys only.
- **One process at a time.** Each row varies one mechanism against fixed alphabets. Combinations of two simple
  processes were tested in two cases only (sums of repeating keys; two tableaux).
- **Exclusion by word list.** The strict-blind scans close "these keywords", not "any keyword".

### A5. The gaps, in order of how natural they are
| Gap | Why it matters | Where addressed |
|---|---|---|
| Keyword plus feedback | The standard way to hide a keyword's period and flatten letter counts; decrypts by look-up | `r78/FABLE_ANALYSIS.md` Part 3 (H7); R79 |
| Two keyword stages on different tableaux, unknown keywords, solved blind | The literal "mask, then encipher"; only word lists so far | §B7 |
| Key moved by the text | Generalises the trigger-letter method | `FABLE_ANALYSIS.md` §4.2; §B4 |
| Unknown keyword alphabet with a non-repeating process | Only chain addition has been crossed with keyword alphabets | §B4 note; large but certifiable |
| Alphabets that change by a rule | One narrow form tested | §B5 (recency forms now tested) |

---

## Part B. Masking mechanisms

### B1. An in-place mask is a key process
**Definition.** A mask is *in place* if output letter i depends on plaintext letter i and on a state, and nothing
else of the plaintext letter itself. It is *reversible by look-up* if the state at i is known to the reader before
letter i is decoded: from the key, the position, and the letters already decoded.

**Theorem M1.** Any in-place mask that is reversible by look-up, followed or preceded by any in-place cipher, is a
polyalphabetic substitution `c[i] = π_{s[i]}(p[i])`, where each `π_s` is a permutation of the alphabet and
`s[i] = σ(key, i, c[0..i−1], p[0..i−1])`.

*Proof.* Fix the key and the earlier letters. The reader can recover p[i] from c[i], so the map p[i] → c[i] is
one-to-one on 26 letters: a permutation, indexed by everything else the reader knows. Composing two such maps
gives another. ∎

**Consequences.**
- "Mask + cipher" in place is one cipher. It is described by a family of alphabets {π_s} and a state rule σ.
  Nothing else is free.
- The state can come from only three places:

  | Source | Examples | Decided how |
  |---|---|---|
  | S0: the position | repeating, held, progressive, generated, read from a text | slot map known → SLOTSOLVE |
  | S1: earlier ciphertext | ciphertext feedback, walking key | slot map or stream computed from the ciphertext → SLOTSOLVE |
  | S2: earlier plaintext | plaintext autokey | sequential search |

- A state taken from plaintext that is *not* earlier (H11) is not reversible by look-up; the reader must solve
  cycles (`FABLE_ANALYSIS.md` §1.5).
- So an in-place mask can be "broader than a Vigenère variant" in only two ways: the alphabets {π_s} are not the
  shifts of one tableau (§B5, §B6, §B7), or the state rule is one nobody has listed (§B4).

### B2. What hiding the letter frequencies requires
**Lemma M2.** On one tableau the ciphertext letter number is `x + k`, with x the plaintext number (distribution q)
and k the key number (distribution κ over the whole message). For large texts the ciphertext distribution is the
convolution q ∗ κ, and its index of coincidence is `(1/26)·(1 + Σ_{j≠0} |q̂_j|²·|κ̂_j|²)`, with q̂, κ̂ the discrete
Fourier transforms. It equals 1/26 exactly when `κ̂_j = 0` wherever `q̂_j ≠ 0`; for English that means κ uniform.

*Proof.* The transform of a convolution is the product of the transforms; Parseval gives the sum of squares. ∎

**What it says.** How flat the ciphertext is depends only on *which* key letters are used and how often, not on
their order. Re-ordering one keyword's letters (trigger rules, holding, walking, a route) changes nothing here.

**Predicted evenness** (synthetic; standard English frequencies; A–Z numbering; 40,000 samples of 97 letters):

| Key letters come from | Index of coincidence, long text | At 97 letters: mean ± sd | Share of samples at or below 0.0361 |
|---|---|---|---|
| Uniform (feedback, generated key, running total) | 0.0385 | 0.0385 ± 0.0028 | 21% |
| Two keywords added (KRYPTOS + PALIMPSEST) | 0.0388 | 0.0388 ± 0.0029 | 19% |
| English text | 0.0397 | 0.0397 ± 0.0032 | 12% |
| One keyword, KRYPTOS | 0.0409 | 0.0409 ± 0.0034 | 7% |
| One keyword, PALIMPSEST or ABSCISSA | 0.0429 | 0.0429 ± 0.0039 | 2% |

- 0.0361 is K4's value (ledger, R54). The last column was computed after seeing it and extends R78's T-RK to more
  models; treat it as a first look.
- **Reading.** K4 is as even as a successful mask should be. That mildly favours masks whose key letters are spread
  over the whole alphabet (feedback, two stages) over any scheme that only re-orders one keyword, by a factor of
  about 3 for KRYPTOS and about 10 for the longer keywords. It is weak evidence, and it is the only evidence in
  this file that discriminates among the candidates.
- It lowers my odds for the walking key (`FABLE_ANALYSIS.md` §4.2) to about 0.3–0.5% when the ring is one keyword.

### B3. The solvability principle
- From Theorem K (`FABLE_ANALYSIS.md` §2.1, as corrected): with 97 letters a blind decode can be certified only if
  the settings number at most about 10³⁰, which is roughly 20 free key letters on top of the method choices.
- The designers meant K4 to be solvable. A design whose secret exceeds that budget (a long random key; two unknown
  mixed alphabets with a long key) could not have been meant to be solved from the sculpture, and no result on it
  could be certified anyway.
- So the working assumption is: **public material, one or two short secrets, and a rule.** The search is over rules.
  More key material is not what is missing.

### B4. Masks whose state comes from the ciphertext: one theorem, one library
**Theorem M3.** Let the cipher be `y[i] = s·x[i] + U[r(i)] + S(i)`, where the slot `r(i) ∈ {0..m−1}` and the
stream S(i) are computable from i and c[0..i−1] without the key, and U is an unknown table of m letters. Then the
set of decryptions is exactly `{ x[i] = s·(y[i] − S(i)) − s·U[r(i)] }` over the 26^m tables U: a shift cipher with
known slots.

*Proof.* Substitute; r and S are known functions of the ciphertext. ∎

So every such mask costs one SLOTSOLVE call per candidate (r, S), and the search for the mask is a search over
**state rules**. The library below is the masking search space I recommend. ChatGPT confirmed from Friedman's
*Military Cryptanalysis*, Part III, that restarting the key, omitting key elements, reversing its direction,
autokeys and transposed key sequences are documented; the walking and counting rules are new here.

| # | Rule for the place in the keyword (ring of length m) | Source | Ledger |
|---|---|---|---|
| R1 | Next letter each time | textbook | closed (control) |
| R2 | Each letter held h times | textbook | closed, std alphabets (control) |
| R3 | Restart, stall or skip at one trigger letter | Friedman | closed, std alphabets (control) |
| R4 | **Reverse direction** at a trigger letter (cipher letter in a chosen set: one letter; the letters of a sculpture word) | Friedman | new |
| R5 | **Omit** elements: each pass drops the next key letter in turn; or pass n omits element n | Friedman | new |
| R6 | **Walk**: advance by the number of the cipher letter just written (`FABLE_ANALYSIS.md` §4.2) | new | new |
| R7 | Interrupt by a numeric key (the ranking of a word) | Friedman-type | new |
| R8 | **Count**: use key letter number n for the n-th occurrence of a cipher letter | new | new |
| R9 | **Class of the previous cipher letter**: halves or thirds of an alphabet; in a sculpture word or not; vowel or consonant | new | new |
| R10 | Products of two rules with m₁·m₂ ≤ 16 (for example R1 × R9) | new | new |

Streams S(i) to combine with any rule: none; the previous cipher letter at lag 1–48 (feedback); the sculpture
text at an offset; a progressive `a·i + b` on a second alphabet.

- **Size.** A few thousand slot maps × about 3,000 streams × 32 conventions is about 10⁸·⁵ SLOTSOLVE calls if run in
  full. Start with streams "none" and "feedback, lag 1–7": about 10⁶ calls, minutes.
- **Cut.** Count every slot map, stream, convention and 26^m keys in the Theorem K cut. At 10⁸·⁵ fixed settings and
  m = 7 the cut is λ ≥ −1.16; at m = 12, −1.09.
- **Controls.** R1–R3 must reproduce the ledger (nothing). Plants of every rule must be recovered, by m.
- **Unknown keyword alphabet.** The same library with the plaintext alphabet drawn from the 77,229 keyword
  alphabets is certifiable (about 10⁵ more settings) but 10⁵ times the work. Hold it until the standard alphabets
  are done.

### B5. Alphabets that change by a rule: a key-free test
A mask outside every tableau: the cipher alphabet is a list, and the letter just used is moved. Repeated
plaintext letters then get different cipher letters each time, which hides frequencies without any key stream.
A strip of movable letter tiles is the physical aid.

**Theorem M4 (recency transform).** Let the cipher list be re-ordered after each letter by moving the letter just
used to the front (MTF) or to the back (MTB). Let the plaintext alphabet P be fixed. Let ρ(i) be the number of
distinct letters occurring in the ciphertext strictly between position i and the previous occurrence of c[i].
Then at every position whose letter has occurred before, the plaintext index in P is ρ(i) for MTF and 25 − ρ(i)
for MTB, whatever the starting list.

*Proof.* MTF: by induction the list is always the used letters, most recent first, followed by the unused letters
in their starting order. A letter used before, with ρ distinct letters used since, is at place ρ. MTB: the list is
the unused letters, then the used ones, oldest first; with U letters used, such a letter is at place
(26 − U) + (U − 1 − ρ) = 25 − ρ. ∎

So ρ, computed from the ciphertext alone, is a **simple substitution of the plaintext** at 71 of K4's 97
positions, for all 26! starting lists and all 26! plaintext alphabets at once. If the plaintext list is the one
re-ordered instead, the ciphertext is a fixed relabelling of the plaintext's own recency ranks, which is far from
even.

**T-REC result** (pre-registered; plants are 97-letter windows of the K1–K3 plaintext):

| Statistic | K4 | 2,000 plants: minimum / 1st percentile / median | 10,000 shuffles of K4 | Verdict |
|---|---|---|---|---|
| A: index of coincidence of ρ (cipher list re-ordered) | 0.0439 | 0.0491 / 0.0540 / 0.0712 | mean 0.0409; K4 at the 79th percentile | **Disfavoured** |
| B: index of coincidence of the ciphertext (plaintext list re-ordered) | 0.0361 | 0.0365 / 0.0391 / 0.0477 | — | **Disfavoured** |

- The theorem held in all 2,000 plants.
- K4 is below every plant on both statistics and looks like its own shuffles. Both recency classes are recorded as
  STAT, not EXCL (ledger L168). Limitation: the plants come from 768 letters of one text.
- **Not covered:** rules that swap neighbouring letters or follow a Chaocipher-type pattern have no such
  transform. They can only be run as fixed methods (keyword starting lists × a few rules), at low odds.
- **The general tool.** A key-free transform that turns a class into a simple or repeating-key cipher decides the
  class at once. Three are now known: differences of neighbouring cipher letters (running total), feedback
  removal, recency rank. Any new mask idea should first be asked: is there such a transform?

### B6. Other families of alphabets
- A tableau in which every row is the same re-arrangement of the row above is a group table. There are exactly two
  groups with 26 elements: the cyclic one (every Vigenère, Beaufort and Quagmire form, with any alphabets) and the
  dihedral one (a disk that can be turned *and* flipped; Porta uses its 13 flips).
- A dihedral tableau with a repeating key is a per-slot alphabet cipher, inside L21 and L89. With feedback or a
  second stage it is untested. I do not propose it: nothing on the sculpture suggests a flipped alphabet.
- An arbitrary chart of 26 unrelated rows cannot be certified at 97 letters (§B3).

### B7. Two keyword stages on different tableaux, solved blind
**Statement.** Stage one enciphers the message with one keyword on one tableau; stage two enciphers the result
with another keyword on a different tableau. Neither keyword need be a sculpture word.

**Why it is the literal mask.**
- Stage one flattens the letters that stage two sees, so the usual attack on stage two fails. With keyword lengths
  7 and 10 the pattern repeats only after 70 letters.
- If the stage-one output alphabet and the stage-two input alphabet are the same, the keys just add (closed, L36).
  With different alphabets they do not.
- It decrypts by two look-ups. It needs only K1/K2's method, used twice with two charts.

**Ledger.** R75 ran sculpture keywords and 80 words blind (nothing), and an any-key crib check that found
thousands of feasible settings and no readable one. No blind solver for unknown keywords has been run.

**Definition.** `w[i] = CA₁[s₁·IDX[PA₁][p[i]] + k₁[i mod m₁]]`, `c[i] = CA₂[s₂·IDX[PA₂][w[i]] + k₂[i mod m₂]]`,
alphabets from the four, CA₁ ≠ PA₂, m₁ and m₂ in 2..12, both orders of the two tableaux.

**Solver (LAYERSOLVE).**
1. Decode: `w = PA₂[s₂·(IDX[CA₂][c] − k₂)]`, `p = PA₁[s₁·(IDX[CA₁][w] − k₁)]`.
2. Coordinate ascent on the letter model over the m₁ + m₂ key letters, 26 values each, until nothing changes; 200
   random restarts.
3. Exact shortcut when one keyword is on a list: undo that stage for each list word and phase, then SLOTSOLVE the
   other stage with a free key. Run the 77,229-word list on the outer stage first.

**Certifiable range.** About 10⁵ conventions and period pairs × 26^(m₁+m₂):

| m₁ + m₂ | Theorem K cut |
|---|---|
| 14 | λ ≥ −1.10 |
| 17 | λ ≥ −1.05 |
| 20 | λ ≥ −1.01 |

**Gate and rejection.** Plants with random keywords, recovery reported by (m₁, m₂). I expect good recovery to a
total of about 14 and little above 18. Closed in scope when the gate passes for a pair of lengths and no K4 decode
clears the cut; lengths the gate does not reach stay open and are reported as such.

**Odds.** 0.5–1%. The evenness table (§B2) is neutral to favourable; the crib check's thousands of feasible
settings say only that it is undecided.

### B8. Masks that do not leave letters in place
| Mask | Reversible by hand | Hides frequencies | Ledger | Comment |
|---|---|---|---|---|
| Transposition after the substitution | yes | no (digraphs only) | large families at chance | The ledger takes the published letters as final positions; a last-step transposition contradicts that |
| Fractionation (Trifid, Bifid) | yes | yes | Trifid closed for any cube and period (L91, L95); 25-letter squares impossible (L88) | — |
| Pair ciphers on a 26-letter matrix | yes | partly | Playfair family closed; Slidefair on keyword alphabets untested (r77 H10) | Low odds |
| Nulls at agreed places | yes | only with chosen nulls | nothing coherent (L81–L83) | Changes the length between published positions |
| Homophones | yes | yes | in place impossible; with a route, no signal (L155) | — |

I add nothing new here. These are either closed or conflict with the ledger's position assumption.

### B9. Sources consulted
- **Wolfram:** exact averages for `FABLE_ANALYSIS.md` §1.6 (4.827 × 10⁻⁴, 1.2935%, 13.07%); 97·log₁₀26 = 137.2524.
- **alphaXiv:** one search on hand ciphers that hide letter frequencies. The archive is thin on classical systems.
  One relevant paper: F. Ruiz, "Can a Tabula Recta provide security in the XXI century?" (2023,
  https://www.alphaxiv.org/abs/2312.02869). It describes pencil-and-paper schemes on the plain tableau: several
  texts added in one pass, a lagged-Fibonacci key stream, and mixed alphabets written on the tableau's headers. It
  notes that adding ciphertext to the key adds no secrecy, and that transposition does not change letter counts.
  It is a modern design paper, not evidence about 1989, and it supports nothing specific here.
- **ChatGPT's check of Friedman, Part III** (relayed by Tyler): supports irregular key movement in general.

---

## Part C. Ranking and handoff

### C1. Where a reversible mask can still be
| Rank | Mechanism | In place | Hides frequencies (§B2) | Blind solver | Odds | Build |
|---|---|---|---|---|---|---|
| 1 | Keyword plus ciphertext feedback, including the running total | yes | fully | SLOTSOLVE | 1–1.5% | R79 (already planned) |
| 2 | Two keyword stages on different tableaux, unknown keywords | yes | nearly | LAYERSOLVE (§B7) | 0.5–1% | new, after R79 |
| 3 | State-rule library R4–R10 with streams (§B4) | yes | only with a stream or two stages | SLOTSOLVE | 0.5–1% together | rider to R79 |
| 4 | Walking key on one keyword | yes | partly | SLOTSOLVE | 0.3–0.5% | in R79 |
| 5 | Recency-ordered alphabets | yes | fully | key-free transform | closed at STAT (L168) | done |
| 6 | Swap-type or Chaocipher-type alphabets | yes | fully | fixed methods only | 0.2% | optional |

Together about 3%. **The evidence does not identify a mechanism**, and the only discriminating evidence in this
file is the weak evenness comparison of §B2.

### C2. What I would tell the cheaper model
1. R79 stands as ChatGPT wrote it. Add the state-rule library (§B4) as slot-map generators; they cost nothing once
   SLOTSOLVE exists.
2. After R79, build LAYERSOLVE (§B7) with its own gate. It is the one large untested reading of "mask, then
   encipher".
3. Use the corrected Theorem K rules: count every free quantity; use shuffles and wrong-family plants as well.
4. Before building any new mask idea, look for a key-free transform (§B5). If one exists, the idea is decided in
   seconds.

### C3. What would be worth Fable's time next
- A result from R79 or LAYERSOLVE that is feasible but unreadable in a structured way.
- A documented statement about the method, from an archive or an interview.
- A proof that some class in §B4 has a key-free invariant like L167's, so that it can be closed without a search.
