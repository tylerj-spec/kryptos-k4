# R82 council BUILD / ABSTAIN plan (draft; synthetic-only)

The external multi-model AgentCouncil has not yet run in this ChatGPT
turn. This document is the **implementable outcome of single-model
adversarial review and executable synthetic tests**, to be attacked by
the separate model-family seats using ADRVERSARIAL_SPEC.md.

## Ticket L — one shared keyword across two different tableaux

Reference: r82/linked_key.py, r82/tests/test_linked_key.py.
Unknown keyword K, primitive period m. First stage uses K[i % m].
Second uses K[(i + floor(i / row_width)) % m]. Two different
intermediate alphabet charts; independent tableau signs.

**Eliminate dead branches before solver development:**
- Same intermediate alphabet: additive collapse, broad L36 coverage.
- Equal coordinate routes or pure row permutations: old transposition.
- m=1, row_width>=97, and width=1: their full 97-position
  substitutions often reduce to ordinary repeated-slot patterns.
- Equivalent keyword periods and chart relabelings: deduplicate full
  transformations, not merely display labels.
- Key-index collision fingerprints are not family-specific.
  Ordinary period-m Vigenere satisfies all such equalities.
- L89's period absence is statistical, not an absolute veto.

**Build:**
1. Canonicalize full transformation table for each (m,w,alph,sign)
   and prove a distinct example outside R75 fixed-key and R81a G4.
2. Implement three blind keyword solvers: (a) enumerated fixed
   dictionary; (b) pairwise-factor model with max-product or
   variable elimination; (c) current annealing baseline plus
   full-text ngram rescoring. No true key used as initial guess.
3. Development strata: m=3,4,5,7,9,12; w=m,m+2,31;
   AZ/KRY/PAL/ABS intermediate pairs; both stage signs.
4. Use natural English, systematic context-dependent orthography
   and true Dutch/German prose as *distinct* controls. Include
   single Vigenere, R81a G4, R75 F1 and random ciphertext as
   wrong families. Entire model search must be repeated on each
   negative.
5. Report exact keyword, >=95/97 plaintext, 97/97 plaintext,
   and true-method selection, by stratum. Also record likelihood
   of true key vs algorithm's maximum to diagnose optimizer vs
   information shortage.

**Observed pilot scope (NOT fresh holdout):**
- IID-English-letter pilot: m4/w4=16/16, m5/w5=16/16,
  m7/w7=13/16, m9/w11=6/16, m12/w31=1/16 exact keywords;
- Previously revealed natural-English developer controls:
  m4/w4=16/16, m5/w5=15/16, m7/w7=14/16,
  m9/w11=9/16, m12/w31=0/16 exact;
- The method family, alphabets, m,w were all supplied; only K
  and P were hidden. These results show a promising solver
  for SMALL m, and LOW POWER for large m. No K4 test was made.
- Natural pilot also checks ordinary Vigenere wrong-family
  controls; those false-attribution results must be reviewed
  before any method-identification claim.

**Gate:** Freeze the fixed solver/cut/null statistic first; then
>=20 *fresh unseen* plants per preselected stratum. Initial target:
>=18/20 exact message+method recoveries in every stratum claimed
recoverable, and no high-confidence false classifications in 200
wrong-family controls (but 0/200 is NOT enough by itself to prove
a 10^-6 false-alarm rate for a huge search). Calibrate the maximum
over ALL keywords, alphabets, routes, signs and scorers on matched
nulls. Any stratum with poor power is OPEN/NO-POWER, not EXCL.

## Ticket T — two independently keyed tableaux (R80a)

R75's fixed-key F1 does not exclude R80a's one-known/one-free
configuration, but ordinary additive same-alphabet layers are OLD.
Implement known-word/short-enumerated first stage followed by
R79 SLOTSOLVE for second unknown stage. Try both layer orders,
stratify by two key lengths and gcd/lcm. Compete directly with
Ticket L and single-stage negative controls. Do not assert
simultaneous two-unrestricted-key solving when Fable's R80
small synthetic test recovered 0/48 from random starts.

## Ticket P — causal plaintext feedback and per-slot progression

Plaintext feedback plus repeating keyword: left-to-right
decryption, stated lag and initial-state rules, avoid revisiting
L58/L59's plaintext-only autokey and R79 ciphertext feedback.
Progressive per-slot K_(r+jm)=A_r+jB_r: use exact second
differences as necessary tests, but previous exploratory
97-letter detection power was poor. Build full keyword solver
and calibrate on fresh natural 97-letter controls. Failure
of an underpowered statistic cannot exclude the method.

## Ticket F — fractional coordinate recombination

R82's 2x13 model is mathematically reversible, but E1 coordinate
label symmetries, E2 relative-route equivalence, and E3
conserved row/column marginals make arbitrary searches
redundant. Existing arbitrary-cube Trifid/25-symbol Bifid and
many routes are already tested. An exploratory K4-only
marginal check disfavors pure named-chart fractionation,
not unknown charts or fractionation with another cipher.
No large K4 scan until method detection and full synthetic
recovery pass independently.

## Ticket M — preprocessing and error channel

A globally bijective letter-for-letter pre-mask is precisely a
change in the first tableau alphabet; theorem and regression
in r82/tests/test_mask_absorption.py. A many-to-one replacement
is not uniquely invertible. Actual new cases require finite
context-dependent orthographic rules, reversible variable-length
encodings with explicit framing, or a separately labelled lossy
reconstruction. Test one predeclared worksheet state slip in
synthetic messages; do not edit K4 to fit published plaintext.

## Frozen integrity and decision protocol

Every independent experimentalist receives the same *neutral*
specification but separate heldout plaintexts/keys. Reviewers
operate read-only until the orchestrator delivers a verdict.
A true K4 run is allowed only for a method with measured
blind recovery power and properly calibrated false alarms.
Candidate generation must ingest only original ciphertext,
never published known plaintext. Push full 97-character
candidates, method/key parameters, full forward witnesses,
code/model hashes and immutable holdout results BEFORE
the independent published-letter check.

Status words: PROVED mathematical invariant; CONTROL PASS;
CIPHERTEXT-ONLY SIGNAL; STAT/NO_SIGNAL; OPEN/NO-POWER;
EXCL limited family after postfreeze consistency; VERIFIED
independent ciphertext-origin solution. Never mix them.
