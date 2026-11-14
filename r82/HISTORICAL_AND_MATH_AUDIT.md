# R82 deeper independent research audit: method vs keys (13 Nov 2026)

**Research memo, not a K4 cipher test.** No K4 ciphertext was processed in this audit. Public known K4 plaintext clues or positions were neither read nor supplied to model inference. Any future candidate must be generated blind, frozen with full 97-letter plaintext and forward witness, and pushed BEFORE the separate clue check. This memo corrects the scope and priorities of the original R82 roadmap; it makes no cipher exclusion.

## 1. New primary-source findings and evidential limits

1. Ed Scheidt, interview by Kim Zetter, WIRED, 21 Jan 2005:
   https://www.wired.com/2005/01/inside-info-on-kryptos-codes/
   - Four processes; two similar, other two different. He says all four sections are English and that he obscured English-language patterns in K4, making method discovery the first challenge. He does NOT disclose a specific encryption step or imply that K4 literally reuses K1/K2/K3 in order.
   - He says Sanborn could have modified the intended process, and could have altered the carved message; do not assume a single public account uniquely defines the final implementation.
   - His illustration of different meanings after linguistic decryption is about semantic codebooks, not proof that K4 uses one. R60 already separated semantic ambiguity from encrypted-letter recovery.

2. Jim Sanborn, Smithsonian Archives of American Art oral history, 14-16 July 2009:
   https://www.aaa.si.edu/collections/interviews/oral-history-interview-jim-sanborn-15700
   - He describes receiving a primer on old and modern cryptographic/matrix methods, including methods not demanding advanced mathematics, and adapting these himself.
   - His account of cutting English text into separate *sentence strips* refers to showing an intelligible but reordered story to CIA reviewers, NOT necessarily the algorithm used to encrypt K4. Do not confuse disclosure handling with a cryptographic transposition.

3. NOVA scienceNOW, PBS broadcast transcript, 24 July 2007:
   https://www.pbs.org/wgbh/nova/transcripts/3411_sciencen.html
   - Scheidt describes substitution and transposition; Sanborn demonstrates a graph-paper method for the solved sections. The program specifically raises *possible* pre-encipherment concealment (vowel deletion and phonetic spelling). This is an interviewer/explanatory hypothesis, not a confirmed disclosure of K4.
   - Primary educational presentation makes physically manageable grids, lettering and preprocessing worth testing, but does not give the hidden K4 technique.

4. CIA official sculpture description (background, with potentially stale solve-status text):
   https://www.cia.gov/legacy/headquarters/kryptos-sculpture/
   - Notes that the tableau is mounted so it reads from the back and that the first three texts used tableau/matrix systems. The physical display does not prove a route or chart is used for K4.

5. Associated Press, 2025 report:
   https://www.ap.org/news-highlights/spotlights/2025/kryptos-final-code-remains-unsolved-the-cia-sculptures-creator-is-auctioning-the-solution/
   - Archival recovery of an original plaintext is distinct from independent recovery of the encryption method/key. The project's objective remains a reproducible ciphertext-origin derivation, not reading leaked archive answers.

6. NSA historical Friedman publications catalog:
   https://www.nsa.gov/Helpful-Links/NSA-FOIA/Declassification-Transparency-Initiatives/Historical-Releases/Friedman-Documents/Publications/
   - Parts III/IV catalog period hand-processes, transposition, fractionation, and cryptanalysis. Historical existence establishes plausibility, NOT that Sanborn chose a particular method.

**Likelihood implication (qualitative, not numerical):** prioritize a concise human-executable instruction sheet, a substantive masking or position rule, and potential implementation errors. Do not treat a classical named-cipher combination as a strong prior merely because it uses a technique appearing in K1-K3.

## 2. Mathematical equivalences in R82 2x13 fractionation

The R82 model maps plaintext letter p to coordinates (r,c) in
{0,1} x {0,...,12} via a fixed alphabet A, applies separate
*position permutations* pi_r and pi_c in each block, then recombines:
cipher_i = A[13*r_(pi_r(i)) + c_(pi_c(i))].

**Theorem E1 — independent coordinate relabeling.**
Let sigma be any permutation of the two row-coordinate symbols and tau
any permutation of the 13 column-coordinate symbols. Make a new
alphabet A' by moving letter A[13*r+c] to coordinate
( sigma(r), tau(c) ). Encrypting any plaintext with A' and the same
position routes produces EXACTLY the same actual ciphertext as A.
Proof: the relabeled coordinates are sigma(r_i), tau(c_i);
the position permutations commute with symbol relabeling; recombination
through inverse A' cancels sigma and tau. No K4 facts needed.
There are 2! * 13! = 12,454,041,600 redundant labelings per arbitrary
2x13 alphabet representation (not necessarily distinct restricted
dictionary alphabets).

**Theorem E2 — only a relative component route matters up to a
post-transposition.** In a block define y_i=(r_(pi_r(i)), c_(pi_c(i))).
Reorder the complete output letters by q = inverse(pi_r). The result
at position i is (r_i, c_(pi_c(inverse(pi_r)(i)))).
Thus the compound of two coordinate permutations is equivalent
to a single relative coordinate route plus an ordinary whole-letter
transposition. In particular pi_r==pi_c is *exactly* simple
transposition (an already covered family). This equivalence is
confirmed by new synthetic tests, and must be applied in any future
family-size or false-positive calculation.

**Theorem E3 — conserved coordinate marginals.**
For each block, the distribution of binary row symbols and 13 column
symbols is unchanged by *any* two independent component position
routes. Consequence: a ciphertext-only detector based only on these
marginal counts cannot be calibrated using letter-preserving SHUFFLES
of that very ciphertext, because those shuffles preserve the same
marginals exactly. Use independently drawn English, wrong-family,
and independent random ciphertext controls, with all alphabet choices
included in the maximum statistic. The same caveat applies to
any proposed letter-count-only invariant elsewhere in the ledger.

**Practical implication:** the 2x13 model is currently a *lower*
priority than R80a and robust Stage-0 controls. A novel visual cipher
must be both reversible AND distinguishable at 97 characters. No
method-identification power has yet been demonstrated for this model.
Do not expand arbitrary alphabet/route ranges without canonicalizing.

## 3. Important new stress-test category: Stage-0 English masking

Prior R79/R81a positive controls successfully tolerated a few changed
letters, nonstandard spelling, and adjacent-rule confusion. They did
NOT prove high power for **systematic text preprocessing**.

Separate explicit mechanisms:
- M0 untouched ordinary English.
- M1 deterministic length-PRESERVING changes, e.g. fixed-position
  phonetic-looking one-letter swaps or a bijective visual relabeling.
  These can be modeled as an invertible pre-encipherment stage.
- M2 length-changing but reversible encodings, only when explicit
  punctuation/escape or extra indicators make the transformation
  one-to-one. They may change 97-symbol alignment and must define
  where the encoder stops and how length is determined.
- M3 lossy changes (e.g. delete vowels with no side information).
  These do NOT have a unique general inverse; a recovered
  intermediate is not an exact original plaintext. Use explicit
  language reconstruction and score it as interpretive, not proof
  of unique decryption.
- M4 true Dutch/German prose (not English) and semantic codebook
  English. Distinct from English that merely *looks* Dutch/German,
  and from German used as a RUNNING KEY (tested in R63/R64).

Generate masking transformations from independently declared rules
on unseen natural texts, NOT inferred from K4 or the published clue
words. Include mild, medium and severe alteration. Fix language
scorers and model-level rejection thresholds before synthetic
holdouts. Test the same fixed cipher family on M0-M4 to estimate how
often a real solution is wrongly dismissed for not looking like
conventional English. Inspect both recognition and full recovery.

**Critical caveat:** known clue positions are reserved for the
post-freeze check. Do not tune any masking rule to leave those
positions or words unchanged, or build prompts from known decoded
phrases. A method that changes length cannot claim ordinary 97-place
anchor alignment without an explicit, frozen mapping.

## 4. Error-channel models: one error may affect a whole suffix

R81a's G6 drop-one tested exactly one potentially wrong *published
plaintext* letter. It did NOT cover:
- a carved ciphertext letter mistyped or substituted;
- one omitted/copied character in an intermediate worksheet;
- a key-state advance skipped once (changes many later symbols);
- a wrong tableau row/column continued until the next reset;
- one block transcribed in reverse or with its end cells swapped.

These are mechanism-specific, and should first be introduced into
fresh synthetic plants **without using K4**. Make at most one
predeclared error event per synthetic message, reserve explicit
no-error controls, and record how much each error alters the next
97 letters. A search that is allowed to "repair" multiple arbitrary
K4 errors can manufacture almost anything, so do not fit arbitrary
fixes to maximize readability or published-letter agreement.

## 5. Two-keyword algorithmic identifiability vs solver failure

Fable's R80 proof that 676 fixed-alphabet key-letter PAIRS make
distinct per-character substitutions is valid in its exact scope,
but it does NOT prove arbitrary *period labels* are unique (e.g. a
two-character word repeated to length 4 or 6 is the same stream),
nor does it imply an English plaintext can be recovered from
N=97 ciphertext. Canonicalize primitive periods and equivalent
stage signs, and deduplicate full 97-character transformations.

The 0/48 random-start simultaneous-ascent recovery is an
ALGORITHM failure on that synthetic budget, not information-
theoretic impossibility or evidence that a two-free-key method is
absent from K4. R80a should test conditional one-known/one-free
SLOTSOLVE first. A separate capped synthetic-only pilot can test
a factor-graph or beam method to recover two unknown keys without
quietly assuming the fixed list key is a good prior.

## 6. Revised work order and explicit stop conditions

**First:** strengthen synthetic M0-M4 masking and error-channel
power evaluation on the existing R80a and R81b methods. Otherwise
an orthodox-English scorer can reject a correct cipher family.

**Second:** R80a (one enumerated/short keyword + one free stage)
and R81b (plaintext-dependent feedback and per-slot progression)
may proceed as distinct preregistered rounds after their own
method-specific synthetic gates. Require >=95/97 and exact
recovery, not solely English-like detection.

**Third:** R82's 2x13 fractionation must (a) pass the mathematical
E1/E2 equivalence and E3 marginals, (b) show method-identification
and full-length recovery on held-out 97-character masked/unmasked
texts, (c) beat wrong-family and match-marginal controls using the
**global scan maximum**. If it cannot, do not run it on K4.

**Fourth:** only compose two stages when a specific new component
has passed, and compare with existing L47/L48, R58/R61/R66/R74
and R75 equivalences before calling it "untested."

Any final solution still requires ciphertext-origin discovery,
full 97-character readable decode (or a separately justified
invertible restoration), exact re-encryption, independently derived
key and method, and an independent post-freeze check of all
published letters. No K4 execution is authorized by this memo.
