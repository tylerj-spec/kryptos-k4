# R82 adversarial research council: challenge packet and verdicts

**Purpose:** create attackable, buildable methods and eliminate false hypotheses
BEFORE any additional K4 cipher search. This is a single-assistant
adversarial review, NOT an independently run three-model AgentCouncil.

**Integrity:** No public-known K4 plaintext or positions are present in
this packet; candidate generators, key search, model training and
preference tuning MUST NOT load them. All future K4 candidates start
with original ciphertext alone, are frozen as full 97-letter plaintext,
method, key and forward witness, pushed to Git, and only afterwards
checked against known letters by an independent validator.

## 0. What the real AgentCouncil provides, and what we can do here

The MIT project https://github.com/Sentry01/AgentCouncil is a GitHub
Copilot CLI plugin with parallel seats from different model families,
anonymous drafts, adversarial attacks and a final orchestrator verdict
SURVIVED / MODIFIED / OVERTURNED. It requires GitHub Copilot CLI with
per-subagent model selection. That executor is not available in this
ChatGPT conversation. Therefore we have NOT run independent Anthropic,
Google, and OpenAI agents in this turn; the role-based criticisms below
are explicitly single-assistant analytical work. This document is
ready for a real multi-model review when the owner invokes the plugin.

## 1. Neutral context brief for all outside reviewers

Repository: tylerj-spec/kryptos-k4. Read LEDGER.md through L170,
r75/METHOD_MATRIX.md, r80/FABLE_IDENTIFIABILITY.md,
r82/METHOD_FINGERPRINT_ROADMAP.md, r82/HISTORICAL_AND_MATH_AUDIT.md,
r82/LINKED_KEY_LAYER.md, r82/linked_key.py,
r82/tests/test_linked_key.py, and r82/pairwise_pilot.py.

Already tested: sums of additive periods (L36); 40,000+ sheet routes
with ordinary substitution (L47/L48); 25-symbol Bifid, arbitrary-cube
Trifid and Hill+route (L12/L61/L88/L91); fixed sculpture-key sandwich
(R74); fixed-key two-tableau families (R75); ciphertext-driven/
position-driven keyword families (R79/R81a). The exclusions are exact
to named configurations, not statements about all hand ciphers.

Candidate A, linked two-tableau: one shared keyword K, primitive
length m; first tableau slot i mod m; second slot
(i + floor(i/w)) mod m, row width w, fixed different intermediate
alphabets CA1 != PA2. Both stages are ordinary reversible shifts in
their respective charts. Full ordered key-index pair schedule
generically repeats after m*w for m>=2; it is not by itself a
cryptanalytic signature. See linked_key.py for reference inverse.

Candidate B: R80a, one enumerated dictionary keyword, a second
arbitrary short keyword and two different intermediate tableaux;
do not confuse with R75 fixed-key scans. Conditional key inference
is per-slot (Fable R80), but fully random two-key hill climbing
failed 0/48 planted tests in its small experimental budget.

Candidate C: R81b causal plaintext feedback plus independent
keyword, and B2 per-slot key progression K_i=A_r+j*B_r,
i=r+j*m; unlike R79 ciphertext feedback or uniform progression.
Exact second differences cancel A_r and B_r; this is necessary but
weak on 97 letters.

Candidate D: a special reversible 26-symbol 2x13 coordinate
fractionation with distinct row/column position routes. E1 has
2!*13! redundant chart relabelings; E2 relative component route
plus whole-letter transposition; E3 conserved marginals. Ordinary
Bifid and Trifid already tested. The pure fixed-chart model is
statistically disfavored by a NON-preregistered K4-only marginal
screen, not algebraically eliminated; keep a low priority.

Candidate E: finite Stage-0 English preprocessing and bounded
one-event worksheet error. Distinguish reversible spelling rules,
lossy vowel deletion, semantic codebooks, and actual German/Dutch
prose. Published plaintext anchors are not generator inputs.

## 2. Three read-only seats for an actual independent council

Seat A: BUILDER / HISTORIAN
- Define one complete 1990 pencil-and-paper instruction sheet per
  family, both directions, and count independent secret symbols.
- Prove it does not collapse to L36/R74/R75/R79/R81a; find a concrete
  counterexample to single-stage equivalence where claimed.
- Classify every claim as PROVED, SYNTHETICALLY TESTED, DOCUMENTED
  HISTORY, or CONJECTURE. Do not infer the actual K4 method from an
  example or a suggestive phrase.

Seat B: ALGEBRAIC BREAKER
- Search for exact equivalent charts, primitive-period duplicates,
  signs and key symmetries, identical intermediate tableaux,
  route trivializations and width>=97 degeneracies.
- Prove or disprove each claimed ciphertext-only invariant. Test an
  OLD METHOD as an explicit false-attribution counterexample.
- Distinguish unique substitution tables for all 26 plaintext
  letters from identifiable keys for 97 ciphertext symbols.
- Do not accept an apparent coincidence peak without multiple
  search correction.

Seat C: EXPERIMENTALIST / SOURCE AUDITOR
- Specify fresh blind N=97 plants with natural English, systematic
  phonetic English, other-language prose, wrong-family ciphers,
  random and fixed-letter-frequency controls.
- Demand separate rates for (i) family recognition, (ii) correct
  parameters/key, (iii) >=95/97 plaintext recovery, and
  (iv) exact 97/97 recovery, plus perfect re-encryption.
- Freeze all class/candidate thresholds and overall max-over-search
  null calibration BEFORE heldout/K4 evaluation.
- Attack power mismatches: does failure implicate method, parameter,
  language model, optimizer, or limited ciphertext length?

Orchestrator: anonymize drafts, select the strongest claim, have
other two seats attack it, and mark each claim exactly SURVIVED,
MODIFIED, OVERTURNED, or OPEN/NO-POWER. Deliver small executable
specs with budgets, genuine confounder controls and stop conditions.

## 3. Current single-assistant adversarial verdicts

| Proposed claim | Mathematical/experimental counterargument | Verdict |
|---|---|---|
| Ordinary repeated-key substitution twice is new | Additive streams collapse into one (L36) | OVERTURNED |
| Pair schedule with m=9,w=11 is 99 and hence detectable | Pair schedule period is 99, but the 97-letter observation contains just 16 same-pair comparisons | MODIFIED |
| Pairwise equality collisions identify linked two-stage method | Period-m simple Vigenere also satisfies them identically. Added an explicit wrong-family regression | OVERTURNED as a METHOD detector |
| Same-pair collisions can reject m=9,w=11 if absent | Simulated IID English power ~8.6% at nominal 5% FPR, versus 35.3% for m9,w31 and 52.2% for m5,w31, one configuration at a time | OPEN/NO-POWER |
| Linked-key unknown keyword is computationally hopeless | A one-key, 26-value/slot PAIRWISE factor graph exists. See new synthetic-only inference pilot, below | MODIFIED |
| Two free independent keys are easy to hill climb | Fable R80 found 0/48 planted recoveries from random starts | OVERTURNED as blanket solver assertion |
| Pure 2x13 fractional scrambling is a novel top candidate | E1/E2 canonicalization and conserved marginals; named-chart exploratory K4 marginals unlike 40 heldout English samples | MODIFIED, LOWER PRIORITY |
| Vowel deletion is an ordinary invertible cipher | Unmarked deletion is many-to-one and cannot reveal unique original plaintext | OVERTURNED |
| One bad known plaintext letter exhausts transcription possibilities | A one-time key-state slip can change an entire suffix and was not covered by R81a G6 | OVERTURNED |

## 4. New pairwise key-factor solver, with a real synthetic pilot

For linked two-tableau, each ciphertext position i depends on just
the plaintext character P_i, unknown key values K_(i mod m) and
K_((i+floor(i/w)) mod m). If a simplified source model treats
plaintext letters as IID with known frequency F(p), the exact
key-conditional likelihood factorizes:

  log L(K) = sum_i log F(Decode(C_i, K_r(i), K_s(i))).

Thus the key can be solved as a pairwise graphical model with
m discrete variables, 26 states per variable. This is NOT R79
one-free-key SLOTSOLVE and does not rely on knowing a second key.
It suggests variable elimination, max-product, belief propagation
or annealed coordinate ascent as real implementation avenues.

R82 code: r82/pairwise_pilot.py (seed 8223, 16 synthetic IID-english
ciphertexts per (m,w), 97 letters, random unknown key, known chart,
known m and w, 12 starts, 100 anneal moves). NO K4 DATA.

| m, w | Exact hidden keyword /16 | Full plaintext mean |
|---|---:|---:|
| 4,4 | 16 | 97.0/97 |
| 5,5 | 16 | 97.0/97 |
| 7,7 | 13 | 80.1/97 |
| 9,9 | 4 | 46.8/97 |
| 9,11 | 6 | 43.4/97 |
| 9,31 | 7 | 68.6/97 |
| 5,31 | 16 | 97.0/97 |
| 12,31 | 1 | 36.8/97 |

These are **development** numbers for a *known-method, known-width,
known-alphabet, IID-letter source* and do not imply power on natural
English or blind method discovery. Where the true key's own unigram
score is >= the solver's score but not recovered, optimization is
a limiting factor; where even the true key is worse, the finite
97-letter sample/source model is not sufficient to reliably identify
it by unigram maximum likelihood.

An immediate adversarial falsifier is to measure the same score and
recovered key confidence on **ordinary Vigenere** and R81a G4
controls, with the linked solver allowed its complete identical
search. Without this, exact linked-key recovery of plants does
NOT establish linked-family classification.

## 5. Build order with explicit stop conditions

L0: Source/historical labels and overlap matrix. Confirm no obvious
algebraic collapse; existing exact negative ledger rows bound scope.
L1: Re-encryption, synthetic round trips, primitive key period, equality
counterexample and deliberate single-letter corruption. CI DONE.
L2: For linked model, compare (a) dictionary enumeration, (b) pairwise
graph/loopy BP plus ngram rescoring, and (c) baseline annealing.
Run fresh natural prose at m4,5,7,9,12 and w=m,m+2,31. Test
correct-family and old wrong-family samples. Predeclare a fixed
budget and report power for each cell, not only the overall mean.
L3: Calibrate family-wide maximum across all alphabets, m,w,
key candidates, restarts, and language scorers on independent nulls.
If m9 cannot recover easy synthetic messages, no K4 negative may
exclude m9. If a lower-m subset passes, preregister only that subset.
L4: Train and test orthographic masking WITHOUT looking at K4,
including lossy cases with explicit restorability limits. Measure
whether prior English language models reject a true cryptographic
inversion.
L5: Only after the preceding gates and a sealed protocol may the
selected method be run on ORIGINAL K4 ciphertext. Push full
candidate, forward witnesses, code hashes BEFORE the independent
post-freeze public-letter validation.

Do not optimize against K4 or published plaintext while constructing
any of the procedures above.

## 6. Ready-to-run actual multi-model AgentCouncil handoff

Requires GitHub Copilot CLI and the AgentCouncil plugin from
https://github.com/Sentry01/AgentCouncil. Run in the repo working
tree; the per-seat tool will be READ-ONLY:

  verbose adversarial council: Read
  r82/council/ADVERSARIAL_SPEC.md,
  r80/FABLE_IDENTIFIABILITY.md, r75/METHOD_MATRIX.md,
  r82/LINKED_KEY_LAYER.md, r82/linked_key.py,
  r82/tests/test_linked_key.py, r82/pairwise_pilot.py,
  r82/HISTORICAL_AND_MATH_AUDIT.md and LEDGER.md through L170.
  Work READ-ONLY. Derive formal counterexamples and quantify
  97-letter holdout method-identification power; do not use
  public-known K4 plaintext words or positions. Return
  SURVIVED/MODIFIED/OVERTURNED/NO-POWER for each mechanism,
  two independent test specifications for each survivor,
  and a final preregistration outline. Do not run K4.

The multi-model outcome is PENDING; the results above are from
mathematical analysis and *synthetic* local/CI checks in this session.
