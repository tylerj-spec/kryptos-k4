# R78: mathematical analysis of H11 and H7, and what to build next (Claude Code, Fable, 11 Nov 2026)

**Status.** Reasoning, proofs, a handoff, and one synthetic check of the formulas (§1.6). Two small ciphertext-only tests were pre-registered
(`r78/PREREG_INVARIANTS.md`, commit b5d18fa) and then run (`r78/invariants.py`, `r78/results/INVARIANTS.json`).
Nothing else was run. No published K4 letter is used in any script, test or argument in this file. The one place
where an earlier, crib-derived note in the repo bears on a point is marked (§3.4).

**No plaintext is claimed.** The evidence does not identify K4's method (Part 6).

## 0. Findings in brief

| # | Finding | Kind |
|---|---|---|
| 1 | H11 (a rearranged copy of the message is its own key) is solved as a mathematical problem. Each cycle of the rearrangement gives one closed-form condition on the ciphertext and a small, exactly known set of decryptions (Part 1) | Proof |
| 2 | **A new invariant decides half of H11 for every possible rearrangement at once.** If the plaintext and key use the same alphabet, the ciphertext letter numbers must sum to 0 mod 26 (Beaufort, variant) or to an even number (Vigenère). K4 gives 7, 12, 7, 14 in the four alphabets. So Beaufort and variant are **excluded for all 97! rearrangements**; Vigenère is excluded when the ciphertext alphabet is A–Z or PALIMPSEST and survives for KRYPTOS and ABSCISSA (§1.4) | Proof + one number per alphabet |
| 3 | H11 can never be decrypted uniquely, whatever alphabets are used (§1.5). The intended reader would have to guess a letter per cycle and test it. A professional designer is unlikely to have chosen that | Proof |
| 4 | Given the route, 97 letters are enough: the true message is always among the candidates, and wrong routes give only gibberish. A counting theorem (§2.1) turns this into an acceptance rule with a proven false-alarm rate | Proof |
| 5 | The same theorem explains R76's caveat. With 45 free key letters no decode can be certified from 97 letters, however readable it looks | Proof |
| 6 | r77 said K4's letter counts are too flat for an English-keyed cipher. That is wrong. The expected index of coincidence is 0.0397, not 0.043, and K4's 0.0361 is at the 12th–15th percentile. Letter counts cannot separate "English key" from "random key" at 97 letters (§2.3) | Run, first look |
| 7 | H7 (keyword plus feedback) reduces exactly to a repeating-key cipher on a transformed ciphertext. It is the best next build (Part 3) | Proof + judgment |
| 8 | A new mechanism, the **walking key**: the place in the keyword moves by the value of the letter just written. It is in the standard textbook family of "ways to hide the period", it is not in the ledger, and it has a real blind solver (Part 4) | New hypothesis |
| 9 | H11, H7 and the walking key all reduce to one solver, `SLOTSOLVE` (§2.2). Build it once | Design |

## 1. H11: the message keyed by a rearranged copy of itself

### 1.1 Model and notation
- Positions `i` = 0..96. π is a permutation of the positions. `LET[a]` and `IDX[a]` are an alphabet and its inverse.
- One tableau stage: `y[i] = s·a(p[i]) + t·k(p[π(i)]) (mod 26)`, where `y[i] = IDX[ca][c[i]]`, `a = IDX[pa]`,
  `k = IDX[ka]`. Vigenère (s, t) = (1, 1); Beaufort (−1, 1); variant (1, −1).
- `x[i] = a(p[i])` is the plaintext as numbers. `σ = a ∘ LET[ka]` turns a key number into a plaintext number;
  σ is the identity exactly when pa = ka. I call pa = ka the **same-alphabet** case and pa ≠ ka the **mixed** case.
- Solving for the key letter gives the **step map** `x[π(i)] = T_{y[i]}(x[i])`, with `T_y(x) = σ(t·(y − s·x))`.
  Each `T_y` is a permutation of Z26.

### 1.2 Cycle theorem (all cases)
Let C = (i₀ → i₁ → … → i_{L−1} → i₀) be a cycle of π and `Φ_C = T_{y[i_{L−1}]} ∘ … ∘ T_{y[i₀]}`.

**Theorem 1.** The plaintexts that encrypt to c under (π, convention) are exactly the choices of one fixed point of
`Φ_C` for every cycle C. Their number is `∏_C |Fix(Φ_C)|`.

*Proof.* A plaintext is a solution iff `x[π(i)] = T_{y[i]}(x[i])` for all i. On a cycle, x[i₀] determines every
other letter by walking, and the walk must return to its start: `Φ_C(x[i₀]) = x[i₀]`. Cycles share no position, so
the choices are independent. ∎

The same holds when the key position is any map q (not a permutation): each connected piece of the graph i → q(i)
has one cycle, one letter fixes the whole piece, and the cycle gives the condition. An autokey with a primer is the
case with no cycle at all: the pieces are chains that start at the primer.

### 1.3 Same-alphabet case: closed forms
Here `T_y` is a translation or a reflection of Z26, so `Φ_C` is one too.

| Operation | Cycle length L | Condition on the ciphertext | Decryptions of the cycle | How they differ |
|---|---|---|---|---|
| Beaufort, variant | any | `Σ_C y ≡ 0 (mod 26)` | 26 | every letter of the cycle shifted by the same δ |
| Vigenère | even | `Σ_j (−1)^j y[i_j] ≡ 0 (mod 26)` | 26 | letters shifted by +δ, −δ, +δ, … along the cycle |
| Vigenère | odd | `Σ_C y` is even | 2 | every letter of the cycle shifted by 13 |

*Proof.*
- Beaufort: `x[i_{j+1}] = x[i_j] + y[i_j]`. Variant: `x[i_{j+1}] = x[i_j] − y[i_j]`. Going round adds `±Σ_C y`, which
  must be 0; then any start works.
- Vigenère: `x[i_{j+1}] = y[i_j] − x[i_j]`. After L steps, `x_L = A + (−1)^L x₀` with `A = Σ_j (−1)^{L−1−j} y[i_j]`.
  - L even: `x_L = x₀ + A`, so A ≡ 0 and any start works.
  - L odd: `2x₀ ≡ A`, so A must be even (A and `Σ_C y` have the same parity) and `x₀ = A/2` or `A/2 + 13`. ∎

**Corollary (structure).** In the same-alphabet case encryption is linear over Z26. For m cycles, of which m_e are
even and m_o odd, every reachable ciphertext has exactly `26^m` decryptions (Beaufort, variant) or
`26^{m_e}·2^{m_o}` (Vigenère). They form one coset: a base text plus one free shift per cycle.

**Special cases worth knowing.**
- A fixed point of π: Beaufort needs `y = 0` there and says nothing about the letter. Vigenère needs y even.
- A 2-cycle (i, j): Vigenère needs `c[i] = c[j]`; Beaufort needs `y[i] + y[j] ≡ 0`.
- The mirror i → 96 − i (same alphabet): Vigenère would make the ciphertext a palindrome. K4 is not one.

### 1.4 Two invariants that hold for every rearrangement
**Theorem 2.** In the same-alphabet case, for every permutation π and every alphabet A = pa = ka:
`S(ca) := Σ_i IDX[ca][c[i]] ≡ (s + t)·Σ_i x[i] (mod 26)`.
So `S(ca) = 0` for Beaufort and variant, and `S(ca)` is even for Vigenère.

*Proof.* `Σ_i y[i] = s·Σ_i x[i] + t·Σ_i x[π(i)]`, and the second sum runs over all positions once. ∎

The invariant needs no route and no key, and it does not care which alphabet numbers the plaintext. It is
ciphertext-only.

**Result on K4** (pre-registered rule; controls: 0 of 2,000 planted messages violate it; random ciphertexts give
S = 0 at rate 0.039 and even S at rate 0.50):

| Ciphertext alphabet | S | Beaufort / variant | Vigenère |
|---|---|---|---|
| A–Z | 7 | **excluded** | **excluded** |
| KRYPTOS | 12 | **excluded** | open |
| PALIMPSEST | 7 | **excluded** | **excluded** |
| ABSCISSA | 14 | **excluded** | open |

- **Scope of the exclusion:** every one of the 97! rearrangements, every plaintext alphabet, as long as plaintext and
  key letters are numbered by the same alphabet.
- **What stays open in H11:** same-alphabet Vigenère with the KRYPTOS or ABSCISSA ciphertext alphabet (this includes
  the K1/K2 tableau itself), and every mixed case. Theorem 2 has no mixed version: there the sum depends on the
  plaintext's letter counts.

### 1.5 The cipher can never be decrypted uniquely
**Theorem 3.** For every permutation π, every pair of alphabets pa, ka (equal or not), every ca and all three
operations, the map plaintext → ciphertext is not one-to-one.

*Proof.* Take one cycle of length L and the map E on Z26^L, `y_j = f(x_j) + g(x_{j+1})`, where `f = s·a` and `g = t·k`
are bijections from letters to Z26. E commutes with rotating the cycle. If E were a bijection it would map the
rotation-fixed vectors, the constant ones, onto themselves, so `h = f + g` would be a bijection of Z26. But
`Σ h = Σ f + Σ g ≡ 13 + 13 ≡ 0 (mod 26)`, while a bijection of Z26 sums to 325 ≡ 13. Contradiction. (This is the
classical fact that a cyclic group of even order has no complete mapping.) ∎

Consequences:
- Some ciphertexts have several decryptions and, by counting, some have none.
- **The legitimate reader cannot decrypt mechanically.** With the route in hand they must still try up to 26 start
  letters per cycle and see which walks close and read as English.
- K1–K3 all decrypt mechanically. A professional who "designed the system" for Sanborn would not normally hand him
  one that does not. I put H11 at **0.2% or less**, lower than r77's 0.5–1%.

### 1.6 Number of candidates, and accidental survivors
**Lemma (average count).** For any map E on Z26^97, a uniformly random ciphertext has on average exactly one
preimage. So over a random ciphertext the expected number of candidate plaintexts, summed over N settings, is N.
Only the spread differs between cases.

Chance that one setting passes the cycle conditions on a random ciphertext, for a route with m cycles:

| Case | Passes with probability | Candidates when it passes | Average over uniformly random routes of 97 |
|---|---|---|---|
| Beaufort / variant, same alphabet | `26^{−m}` | `26^m` | 4.9 × 10⁻⁴ (all-or-nothing through S; **0 for K4**) |
| Vigenère, same alphabet | `26^{−m_e}·2^{−m_o}` | `26^{m_e}·2^{m_o}` | 1.3% (2.6% given S even) |
| Mixed | about `0.63^m` (heuristic) | about `1.6^m` | about 13%, with about 8 candidates each |

- The averages use the cycle-count generating functions `(1−z)^{−1/26}`, `(1+z)^{3/13}(1−z)^{−7/26}` and
  `(1−z)^{−0.632}`. Real route sets are not uniform. The builder should compute the exact figure for the R77 routes
  from their cycle types; it is a sum of the middle column.
- Mixed case, why "about": for a random ciphertext each start letter closes its walk with probability exactly 1/26,
  so the mean number of fixed points is exactly 1. The count is close to Poisson(1) for longer cycles only.
- **Checked on synthetic data** (no K4; a short script, not kept):
  - same alphabet: 0 of 3,000 random cases depart from the table of §1.3, and the true text is always a candidate;
  - mixed, AZ against KRY: mean fixed points 0.97–1.03 at every length; a cycle has none 36–39% of the time at
    length 5–30, 42% at length 3, and 51–53% at length 1–2;
  - 200,000 random routes: the three averages are 4.95 × 10⁻⁴, 1.30% and 13.1%; mean 5.16 cycles.
- **Unrelated cipher families.** The figures above hold for any ciphertext whose letters are close to uniform and
  independent, which covers every polyalphabetic cipher with a non-repeating key. They do not hold for a ciphertext
  that is itself a near miss of H11, such as an ordinary plaintext autokey of lag L: that is H11 with the cyclic
  shift except at L wrap positions, and it would decode as stretches of text each off by a constant shift.

### 1.7 Is 97 letters enough?
Yes, when the route comes from a list that is not astronomically large. Two separate questions:

1. **False alarms.** By Theorem K (§2.1), with N settings, the expected number of wrong candidates scoring at least
   λ per letter on the letter model is at most `N·10^{−97(λ + 1.415)}`. For N = 2 × 10⁶ and a 10⁻⁶ false-alarm
   budget the cut is **λ ≥ −1.29**. English scores −0.6 to −0.9. So a decode that reads as English under a listed
   route cannot be chance. This holds however the candidates were searched.
2. **Finding the true text among the candidates of the true route.**
   - Mixed case and Vigenère with odd cycles only: a handful to a few thousand candidates. Enumerate all of them.
     Recovery is certain except for single letters on cycles of length 1–2, which context must settle.
   - Cosets with d free shifts (one per cycle): this is a shift cipher with d scattered key slots. Information
     suffices up to about d = 35–40 (`26^d·10^{−97·0.6} ≪ 1`). Hill-climbing is reliable to about d = 15–20; the
     gate must measure it by number of cycles.
   - A fully free permutation would **not** be decidable. With no route list, a text is a solution whenever its
     implied key is an anagram of it, and by a rough count 10¹² or more English-like texts satisfy that for any
     given ciphertext. The route list is what makes the problem well posed.

### 1.8 Algorithm (ciphertext only)
```
H11_SOLVE(c, routes, conventions):
  for conv = (pa, ka, ca, s, t) in conventions:
    y = IDX[ca][c]
    if pa == ka:                                   # route-free gate, Theorem 2
      S = sum(y) mod 26
      if (s + t == 0 and S != 0) or (s == t and S odd): skip this convention for ALL routes
    for π in routes:                               # cycles(π) precomputed once per route
      if pa == ka:
        for cycle C = [i0, i1, ...] of length L:
          if s + t == 0:  ok = (sum(y[C]) mod 26 == 0);            free[C] = "same shift, 26 values"
          elif L even:    ok = (sum((-1)^j * y[C[j]]) mod 26 == 0); free[C] = "alternating shift, 26 values"
          else:           A = sum((-1)^j * y[C[j]]) mod 26; ok = (A even); free[C] = "shift 0 or 13"
          if not ok: reject (π, conv)
          base: x[i0] = 0 (odd Vigenère: A/2 mod 13); x[C[j+1]] = t*(y[C[j]] - s*x[C[j]]) mod 26
        text = SLOTSOLVE(base, slot = cycle id, sign pattern, allowed shifts)        # §2.2
      else:
        for cycle C: F[C] = [x0 in 0..25 : walk(x0) returns x0], walk step x -> IDX[pa][LET[ka][t*(y - s*x) mod 26]]
        if some F[C] is empty: reject
        candidates = product of F[C]; enumerate if <= 20,000, else coordinate ascent over cycles on the letter model
      keep the best letter-model score with its setting
  accept a decode only if its score clears the Theorem K cut for the number of settings actually run
```
- Cost: about 100 table look-ups per setting in the same-alphabet case, 2,600 in the mixed case. The whole R77 list
  (74,093 routes × 24 conventions) is seconds to a minute in numpy, not CPU-hours.
- Because it is this cheap, the route list can grow a thousand-fold before the Theorem K cut moves by more than
  0.03 per letter.

### 1.9 Test requirements
| Test | Requirement |
|---|---|
| Algebra | For 10,000 random (π, convention, plaintext): the plaintext is among the returned candidates; every returned candidate re-encrypts to the ciphertext; the candidate count equals the formula of §1.3 |
| Theorem 2 | Planted: holds in all. Random: rates 1/26 and 1/2. (Done in `r78/invariants.py`.) |
| Theorem 3 | For L = 1, 2, 3 and all conventions: brute-force all 26^L inputs, confirm the map is not one-to-one |
| Survivor rates | Random ciphertexts: observed pass rates match §1.6 for the actual route list, per case |
| Positives | Sealed plants from fresh books, random route from the list, random convention: recovered exactly, except letters on cycles of length ≤ 2, which are reported as ambiguous. Report recovery by number of cycles |
| Negatives | Random ciphertexts, shuffles of plants, and plants of other families (repeating key, running key, lag autokey): none clears the Theorem K cut |
| Near miss | A lag-L plaintext autokey decoded with the cyclic-shift route: record what the output looks like, so it is recognised if it occurs |

### 1.10 Verdict on H11
- It **can** recover a message when the route is on the list. The solver is exact, fast, and its false-alarm rate is
  proven.
- It is **unlikely to be K4's method**: no unique decryption (Theorem 3), and two thirds of the natural conventions
  are already excluded for every route (Theorem 2).
- Run the rest once, because it costs a minute and closes the idea properly. Do not expand it into a larger search.

## 2. Three tools that apply beyond H11

### 2.1 Theorem K: a proven false-alarm bound
**Theorem K.** Let Θ be any finite set of settings, each a map `E_θ` on Z26^n (one-to-one or not). Let M be any
probability distribution on n-letter strings. For a uniformly random ciphertext, the expected number of pairs
(θ, x) with `E_θ(x)` = the ciphertext and `M(x) ≥ 10^{−B}` is at most `|Θ|·10^B / 26^n`.

*Proof.* The expectation is `Σ_θ #{x : M(x) ≥ 10^{−B}} / 26^n`, and at most `10^B` strings can each have
probability `10^{−B}` or more. ∎

For n = 97, `26^97 = 10^{137.25}`. With λ the letter-model score per letter (log10), B = −97λ.

| log10 of settings (keys included) | Cut for 10⁻⁶ expected false alarms |
|---|---|
| 6 (H11 as listed) | λ ≥ −1.29 |
| 15 (period-7 key over 10⁵ fixed settings) | λ ≥ −1.20 |
| 20 (period 10) | λ ≥ −1.15 |
| 34 (period 20) | λ ≥ −1.00 |
| 42 (period 26) | λ ≥ −0.92 |
| 73 (R76 H1X at period 45: 26⁴⁵ keys × 77,229² alphabet pairs) | λ ≥ −0.60 |

- The bound counts settings, not search effort, so it holds for hill-climbing and restarts.
- It needs M to be a true probability model. The order-6 letter model is one. The word model is not, so keep it as
  a second, empirical check.
- **Against shuffles of K4** the denominator is the number of arrangements of K4's letters, `10^{116.9}` instead of
  `10^{137.25}`. Every cut becomes stricter by 0.21: for 10⁶ settings it is λ ≥ −1.08 instead of −1.29.
- **Other spellings or languages.** Score with a fixed mixture of j models (English; English with K1–K3-style
  misspellings; German). The theorem holds with B raised by log10 j. This is the clean way to allow nonstandard
  orthography without fitting anything to K4.
- **Reading of R76.** At period 45 the cut is −0.60, which ordinary English does not reach. No decode with that many
  free key letters can be certified from 97 letters. That is a limit of information, not of the solver.
- The repo's cut of −1.45 is looser than uniform (−1.415) and is justified only by the shuffles. Keep the shuffles,
  and add the Theorem K cut as the bar for a claim.

### 2.2 SLOTSOLVE: one solver for three hypotheses
**Problem.** Given a base text `z[0..96]` in Z26, a slot map `r: positions → {0..m−1}`, signs `ε[i] = ±1` and an
allowed shift set per slot (Z26, or {0, 13}), find shifts δ that maximise the letter-model score of
`x[i] = z[i] + ε[i]·δ[r(i)]`.

| Hypothesis | Base text z | Slot map r |
|---|---|---|
| Repeating key, period m | `s·y[i]` | `i mod m` |
| H7 with ciphertext feedback | `s·(y[i] − t·α(c[i−L]))` | `i mod m` |
| Walking key (Part 4) | `s·y[i]` | pointer value, computed from the ciphertext |
| H11 same-alphabet | base text of §1.8 | cycle of π (signs alternate on even Vigenère cycles) |

**Method.**
1. Slots with 12 or more letters: pick the shift by letter frequencies alone.
2. Coordinate ascent on the letter model over all slots until nothing changes; 20 random restarts.
3. Three or fewer free slots: exhaustive.
4. Return the best text, its score, and which slots moved between restarts (those letters are "uncertain").

**Gate.** Recovery rate as a function of m and of the smallest slot size, on sealed plants. I expect near 100% for
m ≤ 10, falling above m = 15.

### 2.3 Letter counts cannot tell an English key from a random key (correction to r77)
- **Test T-RK** (pre-registered first look, independent letters, standard English frequencies): the log-likelihood
  ratio of K4's letter counts, "English ± English" against uniform, for 24 conventions.
- **Result.**
  - The model's mean index of coincidence is 0.0393–0.0398. K4's 0.0361 sits at its 12th–15th percentile.
  - K4's ratio is below the model's 2.5th percentile in 5 of 24 conventions (3 distinct, after two equivalent
    pairs): AZ plaintext with KRY key, variant, AZ ciphertext (0.3%); the two mixed Vigenère forms with KRY
    ciphertext (1.8%); and all-KRYPTOS Vigenère (1.1%).
  - In 5 other conventions K4 looks slightly *more* like the model than like uniform (95th–96th percentile under
    uniform; not significant across 24).
- **Reading.** The two hypotheses' mean ratios differ by only 2–3.4 units, which I estimate at 1.5–2 standard
  deviations at 97 letters. Nothing is decided.
  r77's sentence that K4's flat counts "weigh on every running-key idea" should be struck.
- The all-KRYPTOS Vigenère form that Theorem 2 leaves open is one of the mildly disfavoured ones (1.1%).

## 3. H7: keyword plus a second stream

### 3.1 Exact reduction
`y[i] = s·x[i] + U[i mod m] + S[i]`. If S is known, `u[i] = y[i] − S[i]` is an ordinary repeating-key cipher on the
same plaintext. So:

| Stream | Known from | Problem left |
|---|---|---|
| Ciphertext feedback `S[i] = t·α(c[i−L])` | ciphertext alone | SLOTSOLVE with slots `i mod m` |
| Sculpture text at an offset | ciphertext + the carved text | the same |
| Progressive `S[i] = a·i + b` on another alphabet (§4.3) | nothing | the same |
| Plaintext feedback `S[i] = t·α(p[i−L])` | not known in advance | sequential decode; see §3.3 |

For the first three, **H7 is exactly as solvable as a repeating key of period m**, once per stream. Nothing about
the feedback makes it harder.

### 3.2 What 97 letters allow
- Certifiable (Theorem K, 10⁵·⁵ fixed settings): period 7 needs λ ≥ −1.19, period 12 needs −1.12, period 20 needs
  −1.00. English clears these. Beyond about period 20 a blind claim cannot be certified.
- Solvable in practice: m ≤ 10 reliably, 11–15 often. The gate must report recovery by m.
- The first L positions carry no feedback. If the designer used starting letters there instead, those L letters
  are free. Leave them unscored for L ≤ 3 and say so.
- A key-free detector exists (index of coincidence of the columns of u). At 97 letters it reaches about 3.8
  standard deviations for m = 7 against a search maximum near 4.2, so it cannot stand alone. Use SLOTSOLVE.

### 3.3 Plaintext feedback
- With no primer, decoding is deterministic given U, but one wrong key letter corrupts every later position in its
  chain. Coordinate ascent is unreliable.
- Use exhaustive search for m ≤ 4, a left-to-right beam over the key letters in order of first use for m ≤ 8, and
  the keyword list beyond that.
- It is the lower-priority half of H7.

### 3.4 One member predicts where doubled letters fall
- Take lag 1, with the previous cipher letter added on the same alphabet as the ciphertext (t = +1, α = IDX[ca]).
  Then `y[i] = y[i−1] + s·x[i] + U[i mod m]`: the ciphertext is the **running total** of an ordinary repeating-key
  cipher, and the differences of neighbouring cipher letters are that cipher.
- A doubled cipher letter then means `s·x[i] + U[i mod m] = 0`. So **in each key slot, doubled letters occur at one
  fixed plaintext letter**, and a slot whose letter is E or T collects many doubles while other slots collect none.
- This is ciphertext-only and specific. R71 (L160) found that K4's doubled letters crowd into one column at width 7
  (0.67% of shuffles) and that none of its seven families does this. R71's ciphertext autokey had no keyword, so it
  does not cover this member.
- Two cautions. The feature was known before this prediction was written, so it is not a test. And
  `r77/HYPOTHESES.md` Fact E, which was derived in that round from the published letters, lists the plaintext under
  three of those doubles; in this member they would have to be one and the same letter. I have not used that here.
  It is the validator's first check after the freeze, and nobody should raise H7's odds on the doubled letters
  until it is made.

### 3.5 Assessment
- **New relative to the ledger.** Feedback alone (L17, L27, L58, L59), repeating keys alone (L03, L04), sums of
  repeating keys (L36) and text streams alone (L16, L90) are closed. Their sum was never run.
- **1990 plausibility.** Adding the last cipher letter to the keyword is the hand version of cipher feedback, a mode
  every government cryptographer of the 1980s knew. It hides letter frequencies completely, which matches Scheidt's
  description of masking the English, and it decrypts mechanically.
- **Odds.** 1–1.5% (r77's figure stands). Ciphertext feedback first, and within it the running-total member of §3.4.

## 4. New mechanisms

### 4.1 Where the gaps are
The standard textbook list of ways to hide the period of a keyword cipher (from memory of the US Army texts of
the 1930s–40s that this generation trained on; ChatGPT should confirm the list against a printed source):

| Method | Ledger |
|---|---|
| Key restarts at word ends | R73, R73b (L162, L163) |
| Key restarts, stalls or skips at one trigger letter | R75 F2X (L165) |
| Each key letter held several times | R75 F3X (L165) |
| Progressive key | L13 |
| Autokey, plaintext or ciphertext | L17, L27, L58, L59 |
| Running key | L16, L90, L149, L150, L152, L153, L159 |
| Two keys of different length combined | L36, R75 F1X |
| **Autokey combined with a keyword** | **not tested → H7** |
| **Key advanced irregularly, by a number taken from the text or from a numeric key** | **not tested → walking key (§4.2)** |

### 4.2 WK: the walking key
**Statement.** The keyword is written on a ring. A pointer marks the current key letter. After each letter is
enciphered the pointer moves forward by the number of the letter just written, not by one.

**Definition.**
- Ring `U[0..m−1]`, m in 2..26. Key at position i: `K[i] = U[ptr[i]]`. One tableau stage as in §1.1.
- `ptr[0] = 0`; `ptr[i+1] = (ptr[i] + d·(IDX[α][z[i]] + e)) mod m`, with z = c (WK-C) or z = p (WK-P),
  α in AZ / KRY / PAL / ABS, e in {0, 1}, d = ±1.
- Rider **IK-N** (numeric interruption): the pointer runs 0, 1, …, n₁−1, restarts, runs 0..n₂−1, and so on, where
  n₁, n₂, … repeat the alphabetical ranking of a word (KRYPTOS → 1 4 7 3 6 2 5), each capped at m.

**What distinguishes it.**
- F2X moves the pointer irregularly at one trigger letter only. Here every letter has its own step.
- r77's H8a accumulates the *key value*. Here the *place in a keyword* accumulates, so the key takes only the
  keyword's letters.
- With a step of 1 it is K1/K2's cipher. With the ring equal to the whole alphabet it is H8a.

**Why a 1990 cryptographer could have built it.** It is the trigger-letter method with the trigger replaced by a
count. It needs only the tableau and a finger on the keyword. It decrypts mechanically. It hides the period and
flattens the letter counts.

**Blind solver (WK-C and IK-N).** The pointer sequence is computed from the ciphertext alone. The cipher is then a
shift cipher with known slots: SLOTSOLVE with `r(i) = ptr[i]`. There is no keyword list and no route list.
- Size: 16 step rules × 25 ring lengths = 400 slot maps (plus about 4,000 for IK-N over the 80 sculpture words),
  × the 32 conventions of `r75/sealed/exact.py: CONV`. About 1.4 × 10⁵ SLOTSOLVE calls per ciphertext: minutes.
- WK-P needs the plaintext to move the pointer. Run it as a fixed-method family (the 102 key rows of r77's H7 ×
  16 rules × 24 conventions = 39,168 methods) and exhaustively for m ≤ 4.

**Success looks like.** One (rule, m, convention) whose SLOTSOLVE text clears the Theorem K cut for
`10^5 · 26^m` settings (m = 7: λ ≥ −1.20), whose ring letters spell a word, and which re-encrypts to the
ciphertext. Then, after the freeze, the validator's comparison with the published letters.

**Controls and rejection.**
- Step 1 for every letter must reproduce the repeating-key result (L03, L04: nothing).
- A step rule that is 1 except at one letter must reproduce F2X.
- Random ciphertexts and shuffles: nothing above the cut.
- Plants: recovered, with the rate reported by m.
- **Reject WK** if the gate passes and no K4 decode clears the cut for m ≤ 12, and the validator's exact check
  (pointer known from the ciphertext, so `group_check(ptr, kall)` as in R76's H2X) finds no feasible setting with
  5 or more checks for m ≤ 24.

**Odds.** 0.5–1%. It is new, natural and cheap; nothing in the ciphertext points to it specifically.

### 4.3 PROG: a progressive mask on a different alphabet (rider)
- **Statement.** First shift the plaintext by its position, `a·i + b`, on one alphabet (Trithemius). Then encipher
  with a keyword on a different tableau.
- **Why new.** On one tableau this is the progressive key (L13). On two tableaux it is R75's F1 with the fixed
  stage-one key ABC…Z, which was not in the word list.
- **Build.** A fourth stream type in H7b: 25 steps × 26 starts × 4 alphabets × both orders. The stream is known, so
  the rest is SLOTSOLVE. Odds 0.3%.

### 4.4 Considered and not proposed
| Idea | Why not |
|---|---|
| A larger H11 (more routes, key added) | Theorem 3: not mechanically decryptable. With a keyword added it is also beyond certification |
| Unknown mixed alphabets with a long key | Theorem K: too many settings for 97 letters. No blind claim could be certified |
| Transposition after the substitution | Not addressed here; R61–R67 cover the tested forms |
| Hypotheses read off the published letters | Not done in this round, by instruction |

## 5. Handoff: what the cheaper model should build

**Order.**
1. **SLOTSOLVE and the Theorem K cut** (§2.1, §2.2), with their own unit tests. Everything else calls them.
2. **H11 close-out** (§1.8, §1.9): the R77 route list, 24 conventions. One minute of compute. Expected: nothing.
3. **H7** (r77's definition, with §3 here): ciphertext feedback first, then the sculpture text streams and PROG,
   then plaintext feedback.
4. **WK-C and IK-N** (§4.2), then WK-P.

**For each of 2–4, in this order, as in R75/R76.**
1. Pre-register: family, counts, seeds, books, the Theorem K cut for the exact number of settings, the shuffle cut.
2. Self-tests of §1.9 or the controls of §4.2. No K4.
3. Sealed gate on fresh books: at least 54 of 60 plants recovered and above the cut; 0 of 100 negatives above it.
   Include plants with K1–K3-style misspellings and score with the mixture model of §2.1.
4. Blind run on K4 and 100 shuffles. Freeze and push. Verify by re-encryption.
5. Only then the separate validator: the published letters against the frozen decodes, and the exact checks of r77
   (H7X, H11X) and §4.2, labelled crib-assisted.

**What to hand back.** For each family: gate numbers by key length or cycle count; K4's best score against the
Theorem K cut and against the shuffles; the number of settings; the validator's result. Any decode above the cut:
stop, do not tune, report it raw.

**Rejection criteria.** A family is closed in its stated scope when its gate passes, no K4 decode clears the
Theorem K cut, and the validator finds no feasible setting. A failed gate closes nothing.

**For ChatGPT to review independently.**
- Theorems 1–3 and K, and the three generating functions of §1.6.
- The claim that no complete mapping exists on Z26 as used in Theorem 3.
- The textbook list of §4.1 against a printed source.
- Whether "keyword plus autokey" or a letter-counted key advance appears in any account of what Scheidt taught.
  No K4 plaintext sources.

## 6. What the evidence supports
- **Proven this round:** the H11 results of Part 1, including the exclusion of its Beaufort and variant forms for
  every rearrangement; the false-alarm bound; the reduction of H7.
- **Not shown:** that any of H7, WK, PROG or the rest of H11 is K4's method. My odds are H7 1–1.5%, WK 0.5–1%,
  PROG 0.3%, H11 remainder at most 0.2%. Together about 2–3%.
- **Evidence is insufficient to identify the mechanism.** After 166 exclusions the ciphertext shows no feature that
  singles out one family; the letter counts in particular carry almost no information (§2.3).
- **What would change this:** a decode above the Theorem K cut that then matches the published letters in the
  validator; or a documented statement of the method.

## 7. Corrections to r77/HYPOTHESES.md
| Where | Correction |
|---|---|
| H11 "Against": IC near 0.043, K4 low by 1.5–2 SD | Expected 0.0397; K4 at the 12th–15th percentile. Not evidence (§2.3) |
| H11 cost: 2–6 CPU-hours | About a minute (§1.8) |
| H11 conventions | Skip Beaufort and variant with pa = ka entirely, and Vigenère with pa = ka when ca is AZ (Theorem 2) |
| H11 odds 0.5–1% | 0.2% or less (Theorem 3) |
| Acceptance by the −1.45 cut and shuffles only | Add the Theorem K cut as the bar for any claim (§2.1) |
