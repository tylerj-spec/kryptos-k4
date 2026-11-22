# R94: structured RX2-O development diagnostic

Status at registration: prospective source and work order; no R94 execution.
Scope: the **existing, spent 48-message RX2-O development panel only**, with its
true structural setting supplied. No new messages, fresh holdout, K4 input,
known K4 plaintext, target comparison, or unknown-structure catalog search.
The two inverse wirings are unknown in the candidate phase. Truth-assisted
diagnostics run separately after both candidate output sets have been written.
This is an engineering experiment, not a statistical gate or cipher exclusion.

## Why this work order exists

The archived v1 job is INCOMPLETE: it ran candidate search but failed before
saving candidates. It cannot be scored as zero recoveries. Archived v2/v3 saved
no final restart state with at least 95 matching plaintext letters. They did not
save every visited annealing state, so this does not establish that no visited
state ever recovered a message. The original v3 order 5 objective scores the
true text above every retained final state on 47/48 plants; this demonstrates
missed feasible scores on those plants, not global identifiability or an
adequate objective. One wrong retained state already outscores its true text.

Both inverse wirings currently change by independent two-entry swaps. Here a
whole conditional wiring can be updated exactly for an additive letter score.
The higher-order follow-up uses assignment proposals and legal cycle moves,
then checks their actual order 4 score. It is a structural change, not more
random restarts of the archived joint-swap annealer.

## Exact algebra and its limits

Let q=26, U=W1 inverse and V=W2 inverse. For the supplied setting define
a_i=(C_i+s2_i) modq and delta_i=(s2_i-s1_i) modq. Decryption in contact indices is

    P_i = U[(V[a_i]-delta_i) modq] - s1_i modq.

Given V, each position belongs to b_i=(V[a_i]-delta_i) modq. For a fixed public
letter-frequency score f, the exact conditional cost matrix is

    A[b,x] = sum over i with b_i=b of log10 f(Ein[(x-s1_i) modq]).

Maximizing sum_b A[b,U[b]] over a permutation U is a 26 by 26 linear assignment.
Given U, the other matrix is

    B[a,v] = sum over i with a_i=a of
             log10 f(Ein[(U[(v-delta_i) modq]-s1_i) modq]).

Its assignment optimum is the exact conditional V optimum. Alternation is
only a block-coordinate method: neither a joint global optimum nor recovery
is guaranteed. Costs use floating-point arithmetic with the stated tolerance.

For an additional structural check, after normalization the block maps are
G_delta=W2 T_delta W1=H^delta F, where F=W2 W1 and
H=W2 T_1 W2 inverse is one 26-cycle. Thus normalized maps share a conjugate
cycle; they are not independent substitutions. This removes the global
interface-rotation gauge in the representation. It does not make either
wiring identifiable from a 97-letter observation, nor turn order 4 optimization
into a linear assignment. No cycle-based solver is silently added here.

## Inputs and scorer

- Exact copies of the existing 48-row `PANEL.tsv` and public spent truth from
  `audit/backlog/multirotor/solver/dev/panel/` at main
  `9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1`. Six rows in each of eight turnover
  cells. No source-text acquisition or new control generation.
- The generic letter-frequency vector is copied verbatim from
  `r91/vendor/r82/pairwise_pilot.py`, normalized and logged base10. It is not
  fitted to this panel.
- Order 4 is the committed `r91/R59_LOWER4_FROM_K5.bin`, SHA256
  `85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41`.
  It uses order 1 at the first letter, order 2 at the second, order 3 at the third,
  and order 4 conditional probabilities thereafter. Scores are sums of log10
  probabilities; division by 97 is presentation only.
- R91 reconstructed orders1–4 from pinned corpus and source. Their equality
  to the archived K6 construction follows from the continuation-count
  dependency proof. No byte comparison to the unavailable original full K6
  binary has been performed. The available K5 model's top order 5 is different
  from the original v3 order 5 and is **not** used here.
- NumPy 2.3.5 and SciPy 1.17.0, one numerical-library thread. Python's Random
  generator uses the recorded seed rule. Package versions and all input hashes
  are checked at execution and recorded. Any mismatch blocks execution.

## Version A: exact conditional unigram assignments

For each of the 48 supplied structures use 8 starts, with independently shuffled
U and V. The seed is the first 16 hexadecimal digits of SHA256 of
`940101|id|ciphertext|comma-separated-label`. For each start, make at most 16
U-then-V sweeps. Each block proposes its full conditional assignment optimum.
Accept only an improvement greater than 1e-9; retain the old key on an equal
score. Stop after a sweep with no accepted update. Assert that every proposed
assignment's actual additive score equals its matrix score within 1e-7 and
cannot lower the previous score by more than 1e-7.

Save all 8 final restart states per row, including keys, plaintext, score and
assignment counts. Rank final states by decreasing frozen order 4 score, then
decreasing unigram score, then plaintext and the two wiring vectors. Deduplicate
plaintexts and retain at most 8. All final states remain in the raw output.
This retention rule does not retain every intermediate higher-order score.

## Version B: fixed higher-order refinement

Run B only if the mathematical self-checks pass, A completes all 48 rows within
its cap, and every A output has a scalar forward-encryption witness. The trigger
uses no plaintext recovery, truth, or tuned score cutoff. B is predefined even
if A recovers nothing: its purpose is to measure the effect of the stronger
objective and structured proposals. There is no third version in this order.

Start from each of the same 8 final A states, with no additional random starts.
For a block (U, then V), construct the 26 by 26 matrix of order 4 score changes
when just one entry is assigned each possible value. These counterfactual maps
can contain duplicate values and are **not cipher candidates**. The exact
assignment solution maximizes the sum of those one-entry changes, a surrogate.
Its full permutation and each of its nontrivial disjoint permutation cycles
are legal candidate moves. Evaluate each under the actual order 4 objective.
If none improves by more than 1e-9, evaluate all 325 legal two-entry swaps for
that block. Accept the best actual improvement, with fixed enumeration order
breaking ties. Repeat at most 24 U-then-V sweeps; stop at no improvement.

Save all 8 final B states and retain/deduplicate with A's rule. The actual order 4
score must increase on every accepted move. This is a finite heuristic for
order 4, not an exact conditional order 4 optimizer. Counterfactual score calls
and legal candidates have separate semantics in the receipts.

## Diagnostics after the unknown-wiring output files are written

Open the spent truth only after both candidate phases have completed, and
record the hashes of the unknown-wiring output files before opening it.
The process has ordinary filesystem access; this read-order restriction is
an auditable development convention, not an operating-system blind sandbox.

For every row, independently verify forward witnesses and calculate top1 and
any-retained matching-letter counts, exact recovery, and at least 95 matches.
Report each of the eight cells, raw final states and retention losses. Also
report exact 97-position whole-operator equivalence and global interface-gauge
equivalence to the planted keys. Raw full-key equality is not required for a
plaintext-recovery statistic. Unused contacts may prevent unique wiring
recovery. No post hoc subset becomes a new validated lead.

Two separate truth-assisted conditions supply V=true or U=true. In each, solve
the other wiring by its exact unigram assignment, then apply the same B routine
to the unknown block only, at most 24 sweeps. The frozen true block must remain
unchanged. These 96 conditional cases do not count as unknown-wiring recoveries.
They are diagnostics, not an easier gate whose pass authorizes a target run.

At the true pair, also evaluate all 650 individual legal transpositions across
the two blocks, once. Count distinct wrong plaintexts that score above the true
plaintext, and record the best witness. This is a finite local check, not a
uniqueness proof. A wrong feasible text above truth is a score counterexample;
truth above a found feasible text establishes a remaining optimization gap to
a known point. Neither outcome proves an information-theoretic limit. Strong
conditional recovery combined with poor two-unknown recovery identifies
coupled search as a practical obstacle, without proving it is the only one.

The same job independently rechecks the saved v2/v3 forward witnesses and
matching-letter counts. It does not rerun those optimizers or claim to replay
their unavailable original order 5/6 scores. Recount all 17 committed resource
logs, including failed jobs, and retain the narrow v1 INCOMPLETE designation.

## Finite budgets and terminal outcomes

One invocation of `audit/run_bounded_agg.py` wraps the entire work order:
**1,800 wall seconds, 1,800 aggregate CPU seconds, 2,048 MiB aggregate sampled
resident memory and per-process address-space limit, zero retries**. There is
one numerical worker. Every test, candidate phase, diagnostic and report in
this invocation counts. No allowance resets between scripts or versions.

Additional phase ceilings, each in both wall and CPU seconds: mathematical
self-checks 60; A 300; B 900; truth-assisted diagnostics plus archival replay 300.
The global wrapper covers imports, report writing and the remainder. Internal
checks run at finite loop boundaries; the global wrapper is the hard cap.
Any exception, mismatch, exhausted phase/global cap or killed job is INCOMPLETE.
Partial output can document what ran but cannot be promoted to a complete result.

Candidate bounds: at most 384 final unknown-wiring states per version; 96
conditional states per diagnostic version; at most 48 best-neighbor witnesses.
Thus at most 1,008 newly saved states, with an explicit maximum of 1,100. Matrix
counterfactuals and local move evaluations are finite internal computations,
not saved candidates. A uses at most 12,288 assignment calls; B uses at most
18,432 block updates. Each B update scores at most 1,015 strings: 676 one-entry
counterfactuals, at most 14 assignment/cycle moves, and 325 swaps on fallback.
Known-block diagnostics add at most 96 unigram assignments and 2,304 B updates;
true-key neighbor diagnostics add 31,200 legal scores. Mathematical checks are
explicitly finite in source. All outputs disclose actual counts.

This order ends with COMPLETE_DIAGNOSTIC, INCOMPLETE, or BLOCKED_INPUT_MISMATCH.
If both complete versions have zero at-least 95 recovery, label this bounded
attempt SOLVER_NO_POWER on the spent panel. Any successes remain development
observations; they authorize neither a fresh gate nor K4. Generalization beyond the 48 spent development cases and all 16,640 unknown
structural labels remains unestablished. False-positive control, masked inputs,
corpus generalization and a new sealed gate remain separate prerequisites.
No confidence threshold or false-positive rate is estimated from positive-only,
spent data. No cipher-family exclusion or independent execution promotion is
made by this work order.

## Publication and command

Root first publishes this preregistration, then the exact source, model/input
hashes and QA binding in a following commit. Execute only after root confirms
both have been pushed. Do not modify any pinned source after execution begins.
Use a single command from the repository root:

    python3 -I audit/run_bounded_agg.py --manifest r94/QA_MANIFEST.json \
      --log r94/RESOURCE_LOG.json -- python3 -I r94/run_all.py

The runner refuses a nonempty results directory. A failure consumes this work
order's attempt; diagnose it additively, without an undisclosed second run.
