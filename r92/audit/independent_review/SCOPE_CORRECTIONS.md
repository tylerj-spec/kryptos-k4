# Additive R92 source and scope corrections

Reviewed baseline: `9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1`.
Reviewer: ChatGPT. These findings come from equations and source inspection,
not a new target search. Original frozen files remain unchanged. The separate
review report records whether the exact numerical replay succeeds.

## RX2-O contains the phased single rotor

The R92 preregistration's statement that RX2-O with identity second wiring
embeds RX0 but not RXP is false. Its first rotor already uses
`s1_i=d1*floor((i+r)/n)`. With `W2=identity`,

`W2(M_i+s2_i)-s2_i = M_i`

for every slow schedule, including every turnover phase and either direction.
Thus RX2-O contains R92's phased n<=4 single-rotor functions. Excluding that
subfamily does not exclude arbitrary nonidentity second wirings. R92 evidence
must not seed or filter a blind RX2 solver.

## Distinct schedules do not imply disjoint cipher families

R92's twelve clock arrays are not equal to the R87 zero-phase arrays up to a
constant, but the stronger statement that the function families do not overlap
does not follow. For `W(x)=x+t`, encryption becomes
`E_out.index(c)=E_in.index(p)+t`, independently of the schedule. These wirings
belong to both families. The nonconstant timing difference remains a valid
reason to test the additional labels; it is not a disjointness proof.

## Timing counts

Each `(n,r)` has 16 contact pairs and two directions, hence 32 labels.

| Domain | Labeled settings |
| --- | ---: |
| All phases, n=1..4 | 320 |
| Zero phase, n=1..4 | 128 |
| Nonzero phase, n=2..4 (R92) | 192 |
| All phases, n=1..96 | 148,992 |
| Zero phase, n=1..96 (R87) | 3,072 |
| Nonzero phase, n=2..96 | 145,920 |
| Remaining nonzero phase, n=5..96 | 145,728 |

R92's result calls the last domain 145,920; that includes the already-tested
192. The preregistration also uses "every r" for the nonzero-phase total.
These are count/scope wording errors, not a change in the executed 192 labels.

The independent audit plan adds only R87's n<=4 zero-phase subset. It does not
independently certify the remaining original R87 n=5..96 zero-phase results.

## The actual blind score is a pruned-pipeline maximum

`r92/blind/solve92.py` applies its first quadgram anneal to 192 settings,
keeps 48, and applies the second quadgram anneal to those retained settings.
`r92/blind/run92.py` then computes LM scores for those 48 and greedily polishes
the five best LM candidates before keeping five outputs.

Consequently "letter-model maximum over all 192 settings" is not literal.
It is the maximum retained by that fixed pipeline. Whole-pipeline shuffle
calibration can still be valid when every input follows the identical pipeline.
The audit recomputes saved-score arithmetic and forward witnesses, not the
original optimizer or unavailable full LM binary.

## Exact scope, language and errors

The partial-bijection contradiction is independent of the language of the
unobserved plaintext. It excludes every text satisfying the registered symbol
constraints within this cipher model, including non-English text. A language
limitation applies to the English solver's demonstrated recovery power, not
to the exact mathematical predicate.

DROP covers at most one erroneous observed pair: a plaintext substitution or
a ciphertext substitution at one published position. This is not a claim
about one error of each kind at two different positions, insertions/deletions,
or lost stepping updates. A substitution outside the observed positions does
not affect the exact constraints. General masking that changes the prescribed
observed letters lies outside these no-error/one-error assumptions.

## Execution and reporting qualifications

- The development run exceeded the earlier synthetic-job budget. This was
  disclosed in the original preregistration. A later exact audit cannot make
  that earlier run compliant retroactively.
- The gate contains 202 inputs and 1,010 retained witnesses; the target stage
  contains 201 inputs and 1,005 witnesses. The QA `max_candidates=1005` value is
  the explicitly described target bound, not the count of gate candidates.
- Three books supply the plaintext genres; the fourth book supplies running
  keys for negatives. The audit does not certify unavailable raw-source
  freshness or training nonoverlap from file names alone.
- Original exact and cross-check results were published together in commit
  `1fc9bb3`; the essential blind-output, clue-evaluation and exact-result
  publications are separate. Git establishes those public commit relations,
  not the instant of a historical push or the first local read of a clue.

These corrections restrict interpretation. They do not, by themselves, prove
or refute the executed finite exact exclusion.
