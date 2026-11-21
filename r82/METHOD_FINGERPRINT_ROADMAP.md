# R82: construction-first method fingerprints

**Status (13 Nov 2026): synthetic-only research and reference implementation.**
Not a preregistered K4 search, no K4 cipher or published plaintext
supplied to any reference model, and no new exclusions claimed.

## Goal and strict blind contract

Determine which reversible, hand-executable construction families are
statistically recognizable from only 97 ciphertext letters, and which
are not. A successful encryption/decryption round trip is necessary but
NOT enough to claim a method can be discovered from ciphertext.

For any future K4 test: first prove mathematical distinctness and
calibrate on spent development inputs, then preregister fixed methods,
training/holdout separation, key/route budgets, seeds, family-wide cuts,
and ABSTAIN logic. Independently generate *new* held-out synthetic
controls (plain, orthographically modified, wrong-family, masked,
random and shuffled). Only passing methods get the original published
97-letter ciphertext. Freeze the full 97-letter decoded candidate,
method, keys, software hashes and re-encryption witnesses and **push
them BEFORE consulting public-known K4 plaintext**. Published clues
are a separately labelled after-freeze validator only. No key fitting,
completion, selection, ranking, prompt construction or retraining using
those clues. Never send tentative plaintext externally.

## Coverage check against the project ledger through L170

| Old result | Tested scope | Implication |
|---|---|---|
| L03/L04/L36/L89 | Periodic in-place substitutions and sums of periodic keys; letter repeats | Multiple ordinary Vigenere stages on identical alphabets collapse into earlier families. Low period evidence is not an absolute exclusion. |
| L06-L09, L38/L41, L47/L48/L56, L114/L115/L118/L121/L127, L166 | Huge sets of transpositions with periodic keys, Gromark, text streams, and K3 routes in both orders | A generic substitution-plus-transposition is not new. Any future route must differ materially and have a bounded, preregistered description. |
| L61 | Hill plus transposition, both orders | Hill-plus-grid already covered in its defined scope. |
| L12/L88/L91/L95 | Fixed and arbitrary 27-symbol Trifid, 25-symbol Bifid/Playfair/Polybius families | Fractionation itself is not new. The specific 26-symbol 2x13 split below is narrower and not known to be covered; check for equivalence before K4. |
| L145/L168 | Chaocipher wheel and recency alphabet updates | Generic alphabet evolution is not novel. |
| L147/R58, L150/R61, L153/R64, L155/R66, L164/R74 | Bounded V/T/VT/TV, running-key + route, homophonic+route and fixed K1 to K3 to K2 layers | New layered tests need a genuinely different stage, key class or solver capability. |
| L165/R75 | Millions of *fixed-key* two-tableau settings and exact checks | The open question is a two-stage cipher with one keyword unknown, not another fixed sculpture-key scan. |
| R80 FABLE_IDENTIFIABILITY | Nontrivial different-tableau key-pair substitutions; strong near-equivalences, unconstrained hill climb 0/48 synthetic | Enumerate one keyword, solve the other conditionally; do not assert both arbitrary unknown keys are recoverable. |
| L169/R79 and L170/R81a | In-place ciphertext-driven and position-driven keyword rules; 8 families and many alphabet variants, exact post-freeze exclusions | Do not rescan H7CT, H7TXT, LIB, PROG, or G4 with new labels. Plaintext feedback and self-progression still differ. |
| L148/R60, L64/R63 | Semantic masking and German/Dutch or other-language models | German-like English plaintext is a separate robustness population; do not mistake it for a German *key*. |

All previous EXCL results are conditional on enumerated families and
assumptions. Blind NO_SIGNAL is statistical, not mathematical proof.

## A. Distinct-alphabet two-keyword layers — R80a first

Define i in 0..96, x=IDX(PA1,p[i]), u=s1*x+k1[i mod m1],
t=IDX(PA2,LET(CA1,u)), and
IDX(CA2,c[i])=s2*t+k2[i mod m2], all modulo 26.
Require CA1 != PA2, or the two shifts combine into a single
repeated-key substitution already addressed by L36 etc.

**New recovery capability:** enumerate a predeclared dictionary
keyword or exhaustive 1-3-letter key for one stage. With that stage
fixed, the other stage is solvable by per-slot output tables and
R79 SLOTSOLVE. Run both stage orders and alphabet signs. R75 used
fixed keys and does not close the entire one-key-free family.
Avoid the previous failed two-unknown-key simultaneous ascent as
the primary solver.

**Detection:** score complete ciphertext-only recovered plaintext
under a held-out English model. Measure exact and >=95-letter
recovery by m1, m2, gcd and lcm, alphabet pair and key class, and
against wrong-family plants. Do not hard reject lcm <=48 by L89;
instead report its actual statistical detection power. Family-wide
maximum of scores across all stage settings and restarts must be
calibrated on equal-budget random/shuffled controls.

## B. Plaintext-driven / self-progressing schedules — R81b

**B1 plaintext feedback:** k_i=A_(i mod m)+f(IDX(PFB,p_(i-d)))
with d>=1. An alternative B1-WALK uses a state rho_(i+1)
=(rho_i+g(IDX(PWALK,p_i))) mod m and k_i=A_(rho_i).
These require left-to-right decryption. Plaintext-only autokey
without a separate keyword was already explored in L58/L59/R68.
R79's ciphertext-driven walking key is distinct and does not
exclude B1-WALK.

**B2 per-slot progression:** with i=r+jm,
k_i=A_r+j*B_r (mod26).
A separate increment B_r for each slot is distinct from a single
global progressive increment. A useful exact cancellation is
D2_m(C)_i = s*D2_m(P)_i for alphabet indices,
where D2_m(X)_i=X_i-2X_(i+m)+X_(i+2m) mod26.
This cancels both unknown A_r and B_r, but it cannot in general
reveal English at N=97. An earlier exploratory conversational
test had low power, so treat a failure as OPEN, not an exclusion.

**Detection:** tiny keys exhaustive; fix left-to-right beam width
for longer keywords before holdout; compare lag/period-specific
recovery with ordinary autokey and other wrong-family controls.
For B2, fit each slot's 26x26 (A,B) grid then assemble candidates,
and separately test D2 language-likelihood power. Calibrate the
joint maximum across 4 alphabets, 12 periods, and both signs.

## C. Narrow new 26-symbol coordinate fractionation — R82 pilot

Earlier 5x5 (25-symbol) Bifid and 3x3x3 Trifid tests do not
necessarily subsume a bijective 2x13 coordinate system. It uses
ALL 26 letters, and the last partial block is handled without
padding. This is a plausible *manual construction*, not documentary
evidence that Sanborn employed it.

For a keyed alphabet A, encode p_i to (r_i,c_i) using
divmod(IDX(A,p_i),13). For each block of length n<=b, choose
independent fixed permutations pi_r, pi_c. Output
A[13*r_(pi_r(i))+c_(pi_c(i))]. Invert by separately undoing
both permutations. If pi_r==pi_c, this is precisely the old
transposition class; include it as a negative/degenerate control.

**Necessary exact invariant:** for every block, the count of
row 0/1 coordinates and the histogram of all 13 column coordinates
are unchanged by any independent component permutations. By
themselves they do NOT reveal original plaintext; unknown
alphabet choices and 97-letter sampling greatly weaken detection.

**Possible ciphertext-only fingerprints:**
(1) rank learned English row/column marginal likelihood after
accounting for the number of alphabet/width choices, against matched
IC controls;
(2) enumerate only a small, fixed set of hand-executable component
permutations, independently invert, and score English using a
model trained on different source texts;
(3) assess the maximum such score across *all* tried alphabet/route
pairs on the same complete null replicates.

**Hard limitation:** arbitrary 97-element row/column permutations
would be vastly underconstrained. Do not optimize a secret 97-step
route from K4. Also compare with Bifid/Trifid normal forms and
existing Polybius tests before any K4 experiment. If equivalent,
close the proposal without spending a new search.

**Layer extension only if pure model passes a fresh blind gate:**
a single *enumerated* outer tableau stage before searching
unknown combined keys. Do not add a free long keyword before
showing recovery is possible.

## D. Route + tableaus: only after a genuinely novel stage passes

The physical K3 sheet operations were reconstructed in R72/L161.
Many columnar, spiral, fold and snake routes were enumerated in
L47/L48 and related rounds. An informal 737 route-period test
from the previous conversation yielded no multiple-testing-safe
K4 signal. Stop using isolated peaks or one favorable route.
Only explore a *small* archive-grounded route coupled to A/B/C
after those families recover truly blinded synthetic controls.

## E. Other axes and decision criteria

**Hand reproducibility:** A plausible 1990 construction has
short written instructions, small alphabet tables, inverse
instructions, and a key someone could communicate; 97 independent
random instructions are not a credible shortcut. Explicitly
document encrypt/decrypt step counts.

**Spelling masking:** separate normal English, deterministic
German/Dutch-like phonetic English (W/V, CK/K, PH/F, etc.), and
actual Dutch/German source prose. R79/R81a already tested several
nonstandard-spelling perturbations; further tests should add
independent transformations and withhold unseen texts. Nonstandard
English is a robustness dimension, not evidence for a cipher class.

**Physical/transcription issues:** R81a's drop-one check addressed
a possibly wrong published *plaintext letter*, not a ciphertext
transcription mistake, shifted clue location or new carving order.
Treat those as separate preregistered sensitivity rounds.

**False confidence:** always benchmark against cross-family
controls, equal-letter-frequency/IC nulls, and the maximum-over-
entire-search distribution. Only count candidates readable
across all 97 letters with exact re-encryption and reproducible
key/method derivation. A published-letter-compatible candidate
obtained by known-letter fitting is never a blind discovery.

## Proposed experiment sequence (no runs on K4 yet)

1. R80a: test one fixed/list key + one unknown stage, by lengths,
   gcd/lcm and alphabet, using 97-letter fresh hidden plants.
2. R81b: test sequential plaintext-driven key rules and B2
   progression with predeclared beam/slot solver and power curves.
3. R82: first verify invertibility, marginal invariants, 676
   distinct per-letter two-tableau key pairs, and D2 cancellation
   (these are reference sanity checks, NOT detection). Then
   derive a feature-power gate from spent texts; freeze model
   family and cuts before fresh synthetic holdout.
4. Only for models that passed step 3, try a limited new
   physical route or *enumerated* outer key as a layer.
5. Only passing families may see K4 after protocol freeze.
   Freeze and push full candidates BEFORE public clue check.

**No K4 solve, no K4 result, no new ledger exclusion in this PR.**

## Files in this branch

- r82/models.py — independent reference encryptors/decryptors for
  26-symbol coordinate fractionation, distinct two-tableau
  substitution, per-slot evolving keyword, and old route controls.
- r82/tests/test_models.py — synthetic-only 97-character seeded
  round-trip, invariant, identical-route degeneracy and 676-key-
  pair permutation comparisons.
- .github/workflows/r82-synthetic-models.yml — CI runs tests,
  and rejects accidental K4/clue imports in reference code.
