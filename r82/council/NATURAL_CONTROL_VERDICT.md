# R82 adversarial readout after natural-English old-family challenge

**Status:** reproducible development results, not a sealed holdout,
not an independent AgentCouncil multi-model verdict, not a K4 run.
No published K4 plaintext or positions entered any implementation.

## Source, test, controls, provenance

Code: r82/linked_key.py, r82/pairwise_pilot.py,
r82/natural_pairwise_pilot.py,
r82/tests/test_linked_key.py and
r82/tests/test_mask_absorption.py.

Continuous integration run:
https://github.com/tylerj-spec/kryptos-k4/actions/runs/43552260883

The natural-language plaintexts are 80 **previously revealed**
positive synthetic controls in r81a/holdout/sealed_truth.json,
originally drawn from Silas Marner and Main Street. No messages
from the real K4 input/known plaintext were read. The test
intentionally reused sources across eight experimental cells.
Those cells share training material, so the 16 outcomes per cell
are not eight independent experiments. This is development only.

Known method in each cell:
 AZ plaintext -> KRY output in tableau 1 -> AZ input -> AZ output
 in tableau 2; Vigenere sign +1 at both stages; common unknown
 random keyword K, stage2 index (i+floor(i/w)) mod m.
 The solver KNOWS m, w, and the two alphabets. It does NOT know
 K or plaintext. This severely narrows the task.

Baseline null: ordinary repeating-key AZ->KRY Vigenere on
the SAME source and SAME keyword, processed by the FULL same
linked-key solver search for the fixed cell (m,w). This checks
one already-studied confounder, NOT all possible wrong families.

## Observed natural-prose performance (16 cases per cell)

| m,w | Exact hidden key | Mean linked pseudo-LL/letter | Mean ordinary-VIG pseudo-LL/letter | Linked cases below strongest 16 wrong-family scores |
|---|---:|---:|---:|---:|
| 4,4 | 16/16 | -2.923 | -3.249 | 0/16 |
| 5,5 | 15/16 | -2.930 | -3.208 | 0/16 |
| 7,7 | 14/16 | -2.903 | -3.113 | 1/16 |
| 9,9 | 8/16 | -2.915 | -3.025 | 6/16 |
| 9,11 | 9/16 | -2.927 | -3.028 | 5/16 |
| 9,31 | 4/16 | -2.927 | -3.014 | 4/16 |
| 5,31 | 15/16 | -2.902 | -3.179 | 1/16 |
| 12,31 | 0/16 | -2.902 | -2.932 | 12/16 |

Full plaintext exact recovery equals exact key recovery in these
chosen cells. No ordinary-VIG wrong-family case accidentally
reproduced its full true plaintext (0/16 in each cell). But that
last observation does not by itself rule out a false
HIGH-CONFIDENCE English-looking wrong-family decode, and the
low negative-sample count prevents a meaningful rare-event
false-positive estimate. There is NO fixed family-wide confidence
cut yet and no 100-way global method scan.

Scores are from a simplistic iid English unigram model. This
is a *pseudo*-likelihood development tool, not the already
calibrated R59 natural-English model. The 0/16 vs 16/16
separation at short m is encouraging but not a verified
K4 mechanism discriminator.

## Role-based adversarial conclusions

**Constructor:** A single shared-key two-tableau process is a
legitimate fully invertible hand-executable construction, and
the unusual row-dependent second-stage index creates a
longer pair-of-slot schedule without a second independent key.
This is an explicit cipher, not a guessed plaintext.

**Breaker:** The equality-collision invariant does not
identify it: older period-m Vigenere satisfies the same
equality relations. Long pair-index period does not imply a
detectable cipher period, and a key-discovery algorithm that
knows m,w and tableaux has not established blind
method-identification. Repeated keywords, width>=97, sign
and alphabet symmetries require canonicalization.

**Experimentalist:** m<=5 appears recoverable under this
simple baseline; m=7 partially; m=9 and m=12 fail a
method-conditional test far too often for a meaningful K4
negative claim. The likely next step is using pairwise
factor graph inference as initialization and R59 ngram
language rescoring. Test wrong families at full search
scale, not just the 16 old-VIG negative examples.

### Verdict table

| Mechanism | Provisional verdict | Condition to change |
|---|---|---|
| Linked key m<=5, named charts | SURVIVED AS A BUILDABLE SOLVER, not as identified K4 method | Fresh natural-language masked/wrong-family method-identification gate, calibrated full-search maximum |
| Linked key m=7 | MODIFIED/OPEN | Show >=95/97 and exact recovery on independent hidden plants and distinguish old G4 |
| Linked key m>=9 | NO-POWER | New inference substantially improves hidden-key recovery before any K4 run |
| Generic ciphertext same-slot collisions | OVERTURNED as family identifier | Impossible to rehabilitate without a statistic that separates ordinary periodic substitution |
| Pure 2x13 fractionation fixed named chart | LOWER PRIORITY/STAT | Independent information-power gate, distinguish from old transposition and other fractionation |
| One-to-one per-letter spelling mask | OVERTURNED as separate cryptographic stage | Is a renaming of first-stage alphabet |
| Context-dependent pre-mask / transcription slip | OPEN, NOT TESTED | Explicit reversible state transducer and controlled error propagation tests |

## Actionable next experiment, before any K4 ciphertext

1. Implement exact/elimination or max-product belief propagation
   for the 26-state shared-key factor graph. At m=7/9,
   compare the **true key likelihood** (diagnostic only) with
   the algorithm's best likelihood to separate solver errors
   from information limitations.
2. Use a frozen R59 letter model to rescore full
   97-letter blinded decodes, and compare with the naive
   unigram factor model; language must be trained on material
   disjoint from the concealed plaintext.
3. Hide m,w, charts and cipher FAMILY from the model.
   Include R79 ordinary periodic, R81a G4 rotation,
   R75 fixed two-tableau, simple text transposition,
   changed orthography, and random/letter-frequency matched
   nulls. Calibrate the full-search maximum per target.
4. Prespecify a meaningful exact/95-letter success cut
   per parameter cell; choose only eligible cells for any
   later real K4 test. Do not relabel m9 failures
   as cryptographic contradictions.

This report is a reproducible, developer-level stage
leading to a future preregistration, NOT a formal conclusion
about K4 or Ed Scheidt's actual cipher.
