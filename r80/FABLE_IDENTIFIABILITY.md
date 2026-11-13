# R80 design study: can a two-stage cipher be identified, and what is left to test after R79 (Claude Code, Fable, 13 Nov 2026)

**Status.** Proofs, one synthetic study (`r80/ident.py`, `r80/results/IDENT.json`; no K4, no published letters), and
a ranked list of hypotheses with test specifications. Nothing was run on K4. No published K4 letter is used.

**No mechanism is identified.** Part 2 says what is still worth testing and why.

## Findings in brief
| # | Finding | Kind |
|---|---|---|
| 1 | Two keyword stages on different tableaux have **no equivalent keys**: all 676 pairs of key letters give different substitutions, for all 12 ordered pairs of the four alphabets. The keys are identifiable in principle | Proof + computed |
| 2 | They have strong **near-equivalent keys**. Moving one unit of key from stage one to stage two leaves 54% of letters unchanged for A–Z with KRYPTOS, and 77% for A–Z with ABSCISSA. The cipher is a sum-key Vigenère with a small offset that depends on the intermediate letter | Proof + computed |
| 3 | **Blind hill-climbing over both keys fails**: 0 of 48 planted messages recovered from random starts, with or without moves along the near-equivalence, even at key lengths 5 and 6. From a start with six key letters wrong it recovers 12 of 12. Each letter needs both of its key letters right, so there is nothing to climb | Synthetic run |
| 4 | With **either key fixed, the other separates slot by slot** and is exactly the R79 solver's problem. So the honest blind scope of R80 is "one keyword from a list or very short, the other free", not "both unknown" | Proof |
| 5 | This corrects `r78/FABLE_MASKING.md` §B7, where I expected plain coordinate ascent to work up to a total of about 14 key letters | Correction |
| 6 | After R79, an in-place cipher on the standard alphabets with a keyword of up to 12 letters and a key position computed from the position or the ciphertext is excluded. What remains is listed in Part 2, with six testable hypotheses | Analysis |

---

## Part 1. Identifiability of two keyword stages

### 1.1 Model
Stage one: `u = s₁·IDX[PA₁][p] + a`, intermediate letter `CA₁[u]`. Stage two: `y = IDX[CA₂][c] = s₂·τ(u) + b`.
- `a = k₁[i mod m₁]`, `b = k₂[i mod m₂]` are the two key values at position i.
- `τ = IDX[PA₂] ∘ LET[CA₁]` carries a place in stage one's output alphabet to a place in stage two's input alphabet.
- If the two alphabets are the same, τ is the identity and the keys simply add (closed, L36).

### 1.2 No exact equivalent keys
**Theorem I1.** Key pairs (a, b) and (a + d, b − s₂·e) give the same substitution iff `τ(z + d) = τ(z) + e` for all z.
Such (d, e) form a subgroup of Z26 × Z26. It is trivial unless τ has a translation symmetry.

*Proof.* Equate `s₂·τ(z) + b` and `s₂·τ(z + d) + b′` for all z = s₁x + a. ∎

**Difference table.** Let `N(d, e) = #{z : τ(z + d) − τ(z) = e}`. An exact equivalence needs an entry equal to 26
other than N(0, 0).

| Stage-one output → stage-two input | Largest entry | Where | N(d, d) for d = 1, 2, 3, 4 | Distinct substitutions |
|---|---|---|---|---|
| A–Z ↔ KRYPTOS | 14 | (1, 1) | 14, 11, 9, 6 | 676 of 676 |
| A–Z ↔ PALIMPSEST | 12 | (1, 1) | 12, 6, 3, 2 | 676 |
| A–Z ↔ ABSCISSA | 20 | (1, 1) | 20, 17, 14, 11 | 676 |
| KRYPTOS ↔ PALIMPSEST | 7 | (1, 1) | 7, 4, 1, 1 | 676 |
| KRYPTOS ↔ ABSCISSA | 10 | (1, 1) | 10, 6, 4, 4 | 676 |
| PALIMPSEST ↔ ABSCISSA | 11 | (1, 1) | 11, 7, 5, 3 | 676 |

(Each row holds for both directions.) No entry reaches 26, so **every key pair is a different cipher**. For fixed
alphabets, signs and periods, with every slot in use, the pair (k₁, k₂) is unique.

### 1.3 Near-equivalent keys, and what the cipher really is
- Keyword alphabets agree with A–Z in order over long stretches: A to J, L to N and U to X in the KRYPTOS alphabet.
  On such a stretch τ is a translation, `τ(z) = z + c`.
- So **`y = s₂·(s₁x + a + c(u)) + b`**: an ordinary Vigenère under the sum of the two keys, plus an offset c(u) that
  depends only on which stretch the intermediate letter u falls in.
  - For A–Z with KRYPTOS, c = 7 on 10 of 26 letters, 6 on 3, 1 on 4, and scattered values on the other 9.
- Shifting all of k₁ by d and all of k₂ by −s₂·d (a "gauge move") leaves a letter unchanged whenever u and u + d
  lie on one stretch: N(d, d)/26 of the time. That is 54% for d = 1 with KRYPTOS and 77% with ABSCISSA.
- **Consequences.**
  - Around the true key there are 25 "shadow" keys whose decodes are a third to three quarters right. A solver
    can stop on one; adding gauge moves to its move set lets it step off.
  - A–Z with ABSCISSA is nearly the additive case: it will be the easiest to find and the hardest to tell from a
    sum key.
  - KRYPTOS with PALIMPSEST is the most "mixing" pair, with the faintest shadows.

### 1.4 Why blind search over both keys fails
Synthetic study: planted English messages, random keys, quadgram coordinate ascent, 12 random restarts each.

| Alphabets (stage one → stage two) | Key lengths | Recovered, plain ascent | Recovered, with gauge moves |
|---|---|---|---|
| A–Z → KRYPTOS | 7 and 10 | 0/12 | 0/12 |
| KRYPTOS → A–Z | 7 and 8 | 0/12 | 0/12 |
| A–Z → KRYPTOS | 5 and 6 | 0/12 | 0/12 |
| A–Z → KRYPTOS | 9 and 11 | 0/12 | 0/12 |

Sanity checks on the same code:
- the true key decodes exactly, 12/12;
- a start with three letters wrong in each key is repaired, 12/12.

**Reason.** A letter decodes correctly only when both of its key letters are right, or both are wrong by one gauge
move. From a random start about 1 letter in 26 is right, scattered, and changing one key letter moves 10–14
letters at once with nothing to reward it. The surface is flat with one narrow hole. This is a property of the
cipher, not of the solver's tuning. The run is small (12 restarts); a much longer annealing run might do better,
and that is a question for R80a.

### 1.5 What does work: fix one key
**Theorem I2 (separability).** If k₂ is known, `u = τ⁻¹(s₂·(y − b))` is known at every position, and k₁ is an
ordinary repeating key on u. If k₁ is known, each letter depends on its own k₂ letter only. In both cases the
unknown key separates by slot, and the problem is SLOTSOLVE (`r79/slotsolve.c`) with per-position output tables.

*Proof.* Substitute the known key into §1.1; what is left has one unknown shift per slot. ∎

So a two-stage cipher is blind-solvable exactly when one of its keys can be enumerated:

| Mode | One key | The other key | Cost per ciphertext (8,000 solver calls per second per core, from R79) |
|---|---|---|---|
| L | a word from a list, at phase 0 | free, 1–12 letters | 25,743 words × 2 directions × 32 conventions × 12 lengths ≈ 2 × 10⁷ calls ≈ 40 core-minutes |
| L+ | the same, at every phase | free | about 8 times that |
| X | every key of 1–3 letters | free | 18,278 keys: about the same as L |
| A | free | free | open research: long annealing runs; no claim until a gate shows it works |

Theorem K (R78) for mode L with a 10-letter free key: about 10²¹ settings, cut λ ≥ −1.13.

### 1.6 Reductions that shrink the search
- **Signs.** With a free key, variant Beaufort equals Vigenère (k ↦ −k). Two signs per stage, not three. The key's
  numbering alphabet is irrelevant for a free key.
- **Conventions.** PA₁, CA₁, PA₂, CA₂ from four alphabets with CA₁ ≠ PA₂, two signs each: 768. With A–Z and KRYPTOS
  only: 32. Start with 32.
- **Periods.** L89 (ciphertext only) says K4 shows no repeating structure up to period 48. A two-stage cipher repeats
  with period lcm(m₁, m₂). So the pairs that fit K4 have **lcm ≥ 49**: (7, 8), (7, 9), (7, 10), (7, 11), (8, 9),
  (8, 11), (9, 10), (5, 11) and so on. Pairs such as (8, 10) or (6, 9) are disfavoured. Run all, report by lcm.
- **Recovery criterion.** A shadow decode is half right and half wrong. Keep "recovered" at 95 of 97 letters; do not
  credit shadows.

### 1.7 Handoff: R80a (synthetic only), then R80
1. **R80a.** Build modes L and X on the R79 solver, both directions (list key in stage one or stage two).
   - Gate by (list-key length, free-key length), with plants whose list key is a real word.
   - Measure the speed of a letter-frequency-only first pass.
   - Separately, give mode A a fixed budget (for example 10 core-hours of annealing on 20 plants at lengths 7 and
     10) and report the hit rate. If it is near zero, say so and drop it.
2. **R80.** Pre-register from R80a's numbers. Blind K4 and shuffles; freeze; validator.
3. **Scope statement to carry into the result:** "two stages, one keyword on the list" is what is tested. "Two
   unknown non-words" is not, unless mode A passes a gate.

---

## Part 2. What is left after R79, and six hypotheses to test

### 2.1 Where the evidence now stands
- **R79 excluded, exactly** (given the published letters, in-place working and a correct carving): one stage on the
  A–Z and KRYPTOS alphabets, a keyword of 1–12 letters, the key position computed from the position or the earlier
  ciphertext by any of 982 rules, with or without ciphertext feedback or the K1–K3 text as a second stream.
- **Theorem M1** (R78b): any in-place mask is a key process. So, if the three assumptions hold, K4 must differ from
  the excluded class in at least one of five ways:

| Way out | Hypothesis below |
|---|---|
| A second stage that does not commute with the first | G1 |
| A key position that depends on the plaintext | G2 |
| A key that changes by a rule from pass to pass | G3 |
| A position rule not in the library | G4 |
| Other alphabets on the main sides | G5 |
| One of the three assumptions is false | G6 |

- **Ciphertext-only evidence is thin.**
  - L89 (no repetition to period 48) and the even letter counts (R78b §B2) favour keys that do not repeat within
    48 letters and use many key values.
  - The width-7 doubled letters are a tail event under every mechanism I can construct. The best case, a running
    total with E as the special letter, still gives 5 of 14 only 3% of the time. I treat them as chance.

### 2.2 The hypotheses
| # | Hypothesis | Odds | Blind test | Validator decides? | Cost |
|---|---|---|---|---|---|
| G1 | Two keyword stages on different tableaux, one keyword a real word | 0.5–1% | Modes L and X (§1.5) | Yes, where 5+ checks | R80a then R80 |
| G2 | The key position or a second stream depends on the plaintext | 0.5% | Sequential search | Yes: inside each published run the plaintext is known | R81 |
| G3 | The keyword re-enciphers itself each pass (per-slot progression) | 0.3% | Slot-wise fit, then ascent | Yes, to 9 keyword letters | hours |
| G4 | Position rules not yet in the library | 0.3% | SLOTSOLVE | Yes | minutes |
| G5 | R79's families with PALIMPSEST or ABSCISSA, or an unknown keyword alphabet, on the main sides | 0.5% | SLOTSOLVE for the two named alphabets; too large for an unknown one | Yes | minutes / days |
| G6 | An assumption fails: one published or carved letter is wrong | 0.3% | — | Drop-one re-check | minutes |

Together about 2.5–3%. These are judgments, not calculations.

**G1. Two stages (§1).** The literal "mask, then encipher"; K2's corrected ending reads LAYER TWO.
- *Distinguishes it:* R75 ran 80 words on both stages. R80 would run every list word against a free key.
- *1990 plausibility:* K1/K2's own method used twice, with two charts.
- *Success:* a decode above the Theorem K cut whose free key also spells a word.

**G2. Plaintext-driven keys.**
- *Members:*
  - keyword plus plaintext feedback: `K = U[i mod m] + IDX[ka][p[i−L]]`, L 1–12;
  - the walking key stepped by the plaintext letter (r78 §4.2, WK-P).
- *Distinguishes it:* R79 covered only states computable from the ciphertext. L27, L58 and L59 cover plaintext
  feedback without a keyword.
- *1990 plausibility:* the plaintext autokey with a keyword is the textbook strengthening of Vigenère, and it
  decrypts by look-up.
- *Blind solver:* decoding is sequential.
  - Exhaust keywords of 1–4 letters.
  - For 5–8 letters, a left-to-right beam over the key letters in order of first use, scored by the letter model on
    the decoded prefix, beam 2,000.
  - Run the word list at every length.
- *Gate:* recovery by keyword length; expect it to fade above about 8.

**G3. The self-progressing keyword.**
- *Statement:* after each pass the key is enciphered by the keyword again, so slot r advances by its own letter:
  `K[i] = A[r] + j·B[r]`, r = i mod m, j = i div m. Special cases: A = B (the keyword re-enciphers itself) and B
  constant (the progressive key, L13).
- *Distinguishes it:* L13 has one step for all slots; L36 adds repeating keys; R75's grid key is A[column] + B[row].
  A per-slot step is in none of them.
- *1990 plausibility:* one keyword, the tableau, and "encipher the key with itself to get the next line". No
  repetition for 26 passes, and every key value is used, which fits §2.1.
- *Blind solver:* for each slot the pair (A, B) has 676 values and slots are independent for letter frequencies;
  fit each slot, then quadgram ascent. m 2–12, 32 conventions.
- *Theorem K:* 26^(2m) settings, so certifiable to about m = 8.

**G4. More position rules** (all computed from the position alone; added to the R79 library):
- the keyword rotated by d places after each pass: slot = (i + d·⌊i/m⌋) mod m;
- two or three keywords taken in turn, letter by letter or pass by pass;
- two parts with two keywords and a cut at any position.

**G5. Other alphabets.**
- PALIMPSEST and ABSCISSA as plaintext or ciphertext alphabets multiply R79's settings by 4: one more run.
- An unknown keyword alphabet (25,743 words, three constructions) is about 10⁵ times R79, too large to run blind on
  100 shuffles.
- **A decision for Tyler:** a check of that family against the published letters alone would be fast and exact, but
  it has no blind run before it. It could only ever exclude, never discover. It should be run only if Tyler
  accepts that departure from freeze-first.

**G6. Robustness.**
- Repeat R79's validator with each of the 24 published letters dropped in turn, and with the key index of the
  second published run shifted by ±1 (K2's carving precedent).
- If some setting then passes with 5 or more checks on K4 and on no shuffle, it is a lead for a new blind round.

### 2.3 Order
1. R80a (synthetic) now; it decides R80's size.
2. G4, G6 and the named-alphabet half of G5: one short pre-registered round on the R79 code (R81a).
3. R80 (G1).
4. G2 and G3, which need new solvers (R81b).

### 2.4 What would change the picture
- A decode above the Theorem K cut that the validator then confirms.
- A G6 lead: one dropped letter that makes an otherwise excluded simple family feasible on K4 only.
- Documentary evidence about the method, from the Deep Research report or an archive.
