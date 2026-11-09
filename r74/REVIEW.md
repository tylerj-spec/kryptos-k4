# R74 review (Claude Code, 9 Nov 2026): K1 → K3 → K2 "sandwich" from PR #65 — audit and synthetic pilot

**No K4 data was used.** Everything below ran on the KRYPTOS tableau, the R61 route file, K1/K2 test vectors and
development books.

## Verdict: GO, with the changes listed at the end
- **ChatGPT's numbers all reproduce:**
  - 14 directed routes, 20,160 raw settings, 15,680 distinct ciphers;
  - no repeating key with a period of 48 or less;
  - K1 and K2 decrypt on the KRYPTOS tableau.
- **96.4% of the ciphers are new to this project.** The other 3.6% reduce to a form the L47 search already checked.
- **The solver can't miss within the family.** The pilot recovered 12/12 hidden messages exactly.
- **The weakness is the prior, not the method.** K4 would need exactly these two keywords, this tableau, this stage
  order and one of our 14 proxy routes. I expect NO_SIGNAL.
- **It is cheap:** about 15–40 minutes of computing in total, including 1,000 K4 shuffles.
- **The outcome will be clean.** Every cipher gives one fixed K4 decrypt, so a post-freeze published-letter check
  settles each of the 15,680 exactly.

## A. Reference checks (`r74/audit.py` → `r74/results/AUDIT.json`; tests `r74/tests/test_r74.py`)
**Historical vectors:**
- K1 decrypts exactly (63/63) with PALIMPSEST, VIG, on the KRYPTOS tableau.
- K2 matches with ABSCISSA for its first 361 letters. The last 8 read IDBYROWS: that is the documented carving
  anomaly (Sanborn's intended XLAYERTWO), not a tableau error.

**Routes:** 10 frozen R61 routes plus their inverses give **14 distinct directed routes**.
- The four R24x8 routes are already two inverse pairs.
- SNAKE_L and SNAKE_R are their own inverses.

**Composite:** for output position j,
`C[j] = σ·P[r[j]] + v[j]`, where `σ = s_a·s_b` and `v[j] = s_b·t_a·Ka[(r[j]+a) mod |Ka|] + t_b·Kb[(j+b) mod |Kb|]`
(mod 26).
- For all 20,160 settings it equals the explicit three-stage encryption on two random plaintexts.
- `decrypt()` inverts it in every case.

**Why 15,680:** with (s, t) = VIG (1, 1), BEAU (−1, 1), VARB (1, −1), the transform depends on the operations only
through (σ, s_b·t_a, t_b).
- The nine operation pairs give 7 distinct triples: BEAU/BEAU = VARB/VIG, and BEAU/VIG = VARB/BEAU.
- So there are 2 × 80 × 7 × 14 = **15,680** transforms. No other coincidences occur (at most 2 labels per transform),
  which gives 1,120 per route.

**Periods:** the composite shift repeats no sooner than **every 80 letters**, in either ciphertext or plaintext order.
So it is never a simple period of 48 or less.

## Novelty matrix
| Earlier test | What it covered | Overlap with R74 |
|---|---|---|
| L36 | Sums of periodic keys **in place** (no transposition) | None: no route is the identity |
| L47 / L48 | One transposition + summed periodic keys in **one** text order (crib-assisted exact checks); substitute-first pairs ≤ 48, transpose-first period sets totalling ≤ 24 | **560 transforms (3.6%), possibly.** See the note below |
| R58 | V / T / VT / TV: **one** substitution stage, six engraving routes | None |
| R61, R64 | Running key from English text, then a route | None: one stage, English key |
| R66 | Homophonic substitution + route | None |
| R68 M1/M2 | **One** periodic key (exact to p ≤ 48), Gromark or autokey, along a route | None: the composite period is ≥ 80 |
| R73 / R73b | Word-state keys | None |

**The L47 overlap:**
- **Covered case:** on route R24x8/CCW/fwd with PALIMPSEST first and ABSCISSA second, the ABSCISSA term read in
  plaintext order repeats every 16 letters. The composite is then a period-10 plus period-16 key in plaintext order:
  L47's substitute-first pair form.
  - That holds only if L47's 24×8 quarter-turn is the same permutation as R61's. L47's `two_step.py` is not in the
    repo, so this cannot be checked.
- **Mirror case, not covered:** R24x8/CCW/fwd⁻¹ with ABSCISSA first is period 16 + 10 in ciphertext order. That
  totals 26, above L47's transpose-first limit of 24.
- **Net:** at least **15,120 of 15,680 transforms (96.4%)** have not been run in this project. Outside work is not
  covered: PR #65 notes that others have sampled three-layer constructions, often with clue-chosen settings.

## B. Synthetic pilot (`r74/pilot.py` → `r74/results/PILOT.json`; development books only)
**Setup:**
- **Positives:** 12 passages (6 from *The Secret Agent*, 6 from *The Riddle of the Sands*), each enciphered under a
  hidden setting drawn from all 20,160.
- **Controls:** 33: 21 from R71's seven wrong-family generators and 12 letter shuffles of the positives.
- **Scan:** every ciphertext was decrypted under all 15,680 transforms. Each decrypt was scored with the R59 order-6
  letter model and, as a second independent scorer, the R59 word model.

| | Exact plaintext and true transform | Letter model, per letter | Word model, per letter |
|---|---|---|---|
| 12 positives | **12/12** | −0.56 to −0.93 | −0.49 to −1.16 |
| 33 controls | — | best −1.80 | best −3.58 |

- **Margins:** the winning decode beat the next different text by 0.18–1.22 per letter. The two smallest (0.18,
  0.21) are partial lookalikes that share most of the true shifts, and they were still clear.
- **Cost:** 2.3 s per ciphertext from a cold model file; faster once it is cached.
  - A sealed gate of 420 ciphertexts plus K4 and 1,000 shuffles fits in well under an hour on 4 cores.

## Changes I propose to PR #65's design
1. **Confidence cut fixed on development data before the holdout,** by the R73b rule: the midpoint of the lowest
   positive and the highest control, rounded down to 0.05.
   - The pilot alone gives −1.40 per letter. A larger development run fixes it.
   - **PROSPECT** also requires the word model to clear its own development cut.
2. **The gate as ChatGPT proposed:**
   - 120 positives from two never-used books outside the letter model's training text, and 300 controls from the seven
     R71 generators plus shuffles;
   - pass at ≥ 108/120 exact (plaintext and transform class) and 0/300 confident;
   - plus forward re-encryption of every stored decode.
   - It will almost certainly pass, because the family is closed. It is still the control that proves the pipeline.
3. **Nulls: 1,000 K4 shuffles** through the identical full scan, comparing K4's maximum over the 15,680 transforms with
   each null's maximum.
4. **R74X, pre-registered as a crib-assisted check (after the freeze and verify; never part of the blind outcome):**
   - For every one of the 15,680 K4 decrypts, count the published letters in place.
   - The chance that a wrong transform matches all 24 is about 15,680 × 26⁻²⁴ ≈ 10⁻³⁰. So the family is either in or
     **EXCLUDED**, with nothing in between.
5. **Top-25 packet as ChatGPT proposed:**
   - frozen before the reveal;
   - route and keyword order spread out first;
   - labelled **LOW-CONFIDENCE RAW OUTPUTS** if all are below the cut.

## Not proposed now
**R74b (unknown keywords at both stages, any lengths) on the same routes:**
- It is a far wider family, and the blind search would need a key hill-climber.
- Worth considering only if R74 is negative and we want to widen it.
