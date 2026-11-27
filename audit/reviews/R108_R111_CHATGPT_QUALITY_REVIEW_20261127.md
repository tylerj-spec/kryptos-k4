# R105 and R108–R111: ChatGPT quality review, 27 November 2026

The experiments provide useful conditional exclusions, a weak statistical screen and a limited blind solver result.
Several summaries need narrower claims, and the lag-21 follow-up needs reconciliation with R71.
This is a partial independent review; it does not close batches A, B or C or release R106.

Affected ledger IDs: L194, L196, L197, L198, L199. Historical comparison: L160.

Validation: static mathematical and source review; inspection of registrations, saved gate summaries, result notes,
resource records and Git history; independent arithmetic on the published R105 recovery table. No experiment or
target computation was executed, no K4 candidate plaintext was inspected, and no full manifest/optimizer replay
was performed for this review. Documentation changes pass the repository guardrail check and whitespace check.

Independent review: PARTIAL — ChatGPT, with same-model assisting reviewers (one reviewing model). Reviewed source
base: a9764846779d5fed8728af5130aa7fa7c6bf8bab, the merge of PR #125. No ledger promotion is made.

## 1. Overall assessment

The inspected work shows substantial care: specified equations and decision rules, controls before target work,
explicit abstention on exhausted exact searches, frozen outputs, bounded jobs, and reproducible CI recounts.
The detailed results also disclose failures, scope limits and the provisional R105 dependency of R111.
Git history places each R108–R111 registration before its source/gate, each gate before its target freeze, and each
evaluation after the freeze. The R109 amendment/approval records precede its gate. Git ordering alone is not an
independent attestation of execution isolation or the time each intermediate commit was pushed.

I found no demonstrated mathematical soundness error within the conditional exclusion scopes inspected, and no
apparent counting or permutation-test bug in R110. That is not a complete correctness certificate. Shared code,
holdout provenance, full witnesses and claim wording remain material audit work.

The batch does not establish a promising K4 construction. R108 and R109 principally eliminate or delimit cases;
R110's primary result and R111 are negative; the exploratory lag-21 result revisits a previously studied structure.

## 2. R108: retain the exclusion, attach its actual assumptions

All 768 labelled settings are excluded only under the assumption that the 22 published letters in the 11 complete
crib pairs are correct and **none of those pairs invokes the same-column rule**. The 372 DROP settings remain
excluded allowing **at most one** erroneous or same-column pair. Two or more such pairs are outside this guarantee.
These are counts of overlapping labelled settings, not 768 independent pieces of evidence.

The distinction matters even for valid ordinary Slidefair messages. The frozen synthetic gate records:

| Same-column crib pairs in a true plant | OPEN | EXCLUDED_EXACT | EXCLUDED_DROP |
| --- | ---: | ---: | ---: |
| None | 264 | 0 | 0 |
| Exactly one | 86 | 23 | 0 |
| Two or more | 18 | 6 | 3 |

The exclusions outside the label's assumptions are expected, not a failed soundness gate: the gate checks the
promised conditional claim. They show why “Slidefair with any alphabets and any key is ruled out” is too broad.
The saved panel had 136/400 messages with at least one same-column crib pair; the result note's approximate 38%
should not be presented as the observed fraction on that panel.

The normal-pair equations and forced-collision tests inspected are valid necessary conditions. Trying every
single-pair omission supports the stated one-event exclusion. The rank reference independently implements the
collision calculation, but it runs inside the same X.check pipeline: pair extraction, equation construction,
identity checks and DROP bookkeeping are shared. Audit those common parts explicitly.

Sources: [registration](../../r108/PREREGISTRATION.md), [result](../../r108/RESULT.md),
[saved gate](../../r108/holdout/GATE.json), [gate source](../../r108/gate108.py),
[cross-check](../../r108/crosscheck108.py), [X107](../../r107/x107.py), [rank reference](../../r107/ref107.py).

## 3. R109: distinguish necessary consistency, full feasibility and checker independence

The 34 exclusions can follow from a violated necessary condition. Passing that condition has a weaker meaning.
The solver constructs an equation only where both P_i and P_(i-L) are known. Its own documentation says the test
is necessary only unless the plaintext hypothesis is closed under the lag. It does not establish propagation
through every intervening ciphertext position with a single primer and both alphabets.

Therefore the safe reading is:

- 34 settings fail the tested necessary equations; 6 also fail every one-position omission.
- 322 satisfy the tested necessary equations; this is not a full-chain feasibility proof for all 24 known letters.
- 64 are computationally undecided.
- 732 have no equations in this direct-pair screen; this does not establish that no stronger check could exist.

The result's “322 are possible; some pair of alphabets fits the 24 letters” should carry that qualification.

The primary solver finds 12 exclusions. For primary-UNDECIDED cases the target falls back to DFS, then uses the
same DFS again as its cross-check. Thus 22 of the 34 decisions are DFS-only, followed by a repeat of that method.
“DFS confirmed all 34” is accurate; “two independent solvers proved all 34” would not be. Both solvers also use
the same equation builder. A separate derivation of that mapping and of DFS exhaustion is a priority for promotion.

The positive-control gate reports 150 plants, but 67 have no equations: 83 exercise nonempty systems. The result
table discloses this. Future gates should require nonvacuous cases in the relevant parameter strata.

### The amendments

Amendment 1 reduces the enumeration cap from 7 to 5. Returning UNDECIDED when the cap is reached is conservative
for exclusions. Amendment 2 changes the cross-check coverage requirement from at least 50% of 200 cases to at
least 40 of 600. That is a relaxed gate criterion, even though the zero-disagreement rule is unchanged.

The actual 142/600 both-decided cases exceed the old minimum absolute count of 100 but do not meet its 50% share.
Both amendments were documented before the gate and their records state owner approval. Treat them as disclosed
prospective changes, not an unchanged preregistration. “Both are conservative” should distinguish conservative
verdict handling from a weaker coverage requirement. No false exclusion follows merely from this amendment.

Sources: [equation builder](../../r102/s3b102.py), [DFS](../../r102/dfs102.py),
[per-cell checks](../../r109/check109.py), [target source](../../r109/run_target109.py),
[result](../../r109/RESULT.md), [gate](../../r109/holdout/GATE.json),
[amendment 1](../../r109/AMENDMENT_1.md), [amendment 2](../../r109/AMENDMENT_2.md).

## 4. R110: a valid weak screen; lag 21 is not a new independent clue

The inspected statistic, one-sided permutation tail including ties, add-one calculation and 24-lag Bonferroni
adjustment implement the registration coherently. Lag 1 was the primary test; **the exploratory scan of lags
2–24 was also registered**, so calling that scan an unplanned extra is inaccurate.

The frozen report gives p = 0.071 at lag 1, correctly labelled NO_SIGNAL. Detection of 122/300 synthetic positives
is 40.7% power for the registered lag-1 mixture: a null result cannot exclude that model. The lag-21 raw p of
0.00132 and adjusted p of 0.03168 describe the stated frequency-preserving shuffle null and the 24-lag scan.
They are not a project-wide correction for all previous feature and mechanism choices or a probability that a
particular construction is true.

R71 already registered and reported the width-21 repeated-pair phenomenon, including a count of 11. The statistics
are related, not identical:

| | R71 | R110 |
| --- | --- | --- |
| Pair objects | Letters separated by width/lag | Same |
| Contribution of a pair occurring n times | max(n − 1, 0) | n(n − 1)/2 |
| Reported K4 value at 21 | 11 | 11 |
| Analysis | Widths 2–48; standardized maximum; joint fingerprint | Lags 1–24; permutation tails; primary lag 1 |

R71's substantial family simulations produced NO_FAMILY for its joint doubled-letter/repeated-pair fingerprint.
That does not rule out every new lag-21 mechanism. It does require P5 to explain what is new before repeating a
family sweep. Fresh shuffles, another weighting or another seed on the same 97 letters do not provide independent
confirmation. A second observable on the same previously inspected text also remains exploratory unless its
selection and calibration justify a stronger interpretation.

A useful P5 begins with a finite novelty review, then synthetic comparison of concrete mechanisms against realistic
alternative families. It needs a distinguishing prediction or a path to actual blind recovery, an explicit gate
and a stop rule. If no materially different mechanism or test emerges, close the follow-up without another K4 run.

Sources: [R110 registration](../../r110/PREREGISTRATION.md), [statistic](../../r110/lagpair110.py),
[target procedure](../../r110/run_target110.py), [result](../../r110/RESULT.md),
[R71 registration](../../r71/PREREGISTRATION.md), [R71 features](../../r71/features.py),
[R71 result](../../r71/RESULT.md), [charter, section 7](../RESEARCH_CHARTER.md).

## 5. R105/R111: useful solver progress with limited demonstrated reliability

The R105 rank recurrence, gauge shift and sign reflection are mathematically consistent in the inspected code.
The fast histogram formula correctly computes the intended sum of squared counts. Synthetic truth passed through
the trace argument is read only after winner selection for diagnostics; it does not steer the inspected search.
R111 runs all 20 registered cells on every plant, decoy, target and target shuffle, and does not use R109's
crib-assisted survivors to skip settings. These are substantive strengths.

Independent arithmetic on the 50 entries in the published R105 result table gives:

| Endpoint | Count |
| --- | ---: |
| At least 90/97, the registered recovery endpoint | 42/50 |
| At least 95/97 | 31/50 |
| Exactly 97/97 | 17/50 |

The registered development GO was met; preserve that endpoint. It is not an 84% exact-solving rate. Five documented
failures are scorer counterexamples with 47–88 correct letters; other failures arise from search and pruning.
“High scores separated the tested true hypotheses from the tested decoys” is warranted. “A high score shows the
hypothesis is right” is too strong for 30 decoys and does not certify an arbitrary future result.

The synthetic pipeline also needs stronger generalization evidence before a broader search:

- Development and holdout generation use the same Carter OCR source. Fresh seeds do not establish disjoint text
  windows or held-out books. No enforced disjoint partition was evident in the inspected generators.
- Quadgram training-text provenance and its overlap with those windows remain unverified. This is an evidence
  gap, not a finding of actual leakage.
- R111's eight true plants represent eight of the 20 parameter cells, including only one lag-5 plant. Its observed
  7/8 recovery is a useful small gate, not a precise reliability estimate across every cell or plaintext style.
- Both rounds check re-encryption only from position L onward. With an arbitrary primer the initial letters can
  be fitted algebraically: k_i = B^-1(C_i) − s1 A^-1(P_i) mod 26 for i < L. That makes the tail check meaningful,
  but the next validation version should emit the primer and independently forward-encrypt all 97 letters.
- R111's evaluator reports re-encryption flags without making failure invalidate its score-based decision.
  Current reports say all flags passed; this is a future fail-closed repair, not a demonstrated invalid run.
  Add it in a new registered/additive version, preserving frozen source.

R111's reported NO_SIGNAL is appropriately limited: its best output loses to 9/15 shuffle maxima, and the family
is not excluded. Improve S105 using synthetic failure modes and fresh independent text, not by tuning to R111's
best K4 setting or to its post-freeze clue counts. R106 remains blocked on the substantive batch-B audit.

Sources: [R105 registration](../../r105/PREREGISTRATION.md), [solver](../../r105/solve105.py),
[run source](../../r105/run105.py), [result](../../r105/RESULT.md),
[R111 registration](../../r111/PREREGISTRATION.md), [cell search](../../r111/cells111.py),
[gate source](../../r111/gate111.py), [evaluator](../../r111/evaluate111.py),
[result](../../r111/RESULT.md), [reference encryptor](../../r100/autokey100.py).

## 6. Work between audits

Keep the adopted 4–6-experiment audit cadence and dependency rule. The current queue has 13 rounds across three
unclosed audit batches; this partial review closes none. Prioritize batch B's R102–R105 foundations to resolve the
R106/R111 dependency, while preserving the outstanding batch-A and batch-C obligations.

Claude can continue independent approved work while those audits proceed. The productive preparation is:

1. A lag-21 novelty/mechanism comparison against R71, with a finite synthetic work order if a new question survives.
2. A solver validation plan with disjoint text, balanced true cells, exact and near-recovery endpoints, full
   witnesses and failure classification. Execution stays within the applicable dependency/work-order gates.
3. An exact derivation of ordinary Slidefair same-column case handling on synthetic examples before proposing
   any broader target exclusion.
4. The already approved fallback catalogues F1–F3, each with concrete reversible equations, overlap checks and
   a decision that a future experiment could change.

These items are directions for finite work orders, not permission to change acceptance thresholds, repeat a spent
holdout, use crib-assisted survivors in a blind generator or launch an unregistered K4 computation. Quality comes
from informative tests and defensible decisions; experiment count alone is not progress.

The reported blocked ad hoc command was not independently investigated here. Its reported refusal is not proof
of every input boundary. Full isolation remains part of the execution audit.
