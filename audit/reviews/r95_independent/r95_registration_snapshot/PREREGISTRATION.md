# R95: fixed five-letter score challenge

Date: 22 November 2026 (America/Chicago).
Mode: DEVELOPMENT / SYNTHETIC-TRUTH-ASSISTED. No K4 computation.
Independent-model review: NONE. Builder, breaker and verifier are ChatGPT
roles within one internal review process.

## Question and authority

Does one already-built, fixed order-five objective pass the first development
selection bar in `audit/reviews/NEXT_STEPS_AFTER_R94.md` on the spent 48-case
RX2-O panel and its complete legal one-swap neighborhood?

The user clarified that "25m" means a 25-meter immediate-priority target,
not a 25-minute deadline, and directed focus now. This work executes the
previously proposed single-score challenge. The scientific budgets below
are independent of that corrected terminology. It neither extends R94 nor
starts a K4 search. Existing authorization for the project repository covers
publishing this specification, source, public synthetic derived evidence,
internal review, and the resulting PR through the established workflow.

Baseline repository: `3a48dec3414560c0d26de6b1558e3dbf05ab772c` (PR #105).
The preregistration is published before source execution. Complete source,
hash manifest and separate checker are published before the sole primary
run. Complete outputs are published before narrative interpretation.

## Fixed inputs and one candidate

- Exactly the 48 public, previously used R94 records in
  `r94/inputs/PANEL.tsv` and `r94/inputs/PANEL_TRUTH.json`, in their original
  ID order. All eight turnover cells contain six records each. No new texts,
  keys, labels, samples, or exclusions may be chosen after scoring.
- Baseline: `r91/R59_LOWER4_FROM_K5.bin`, SHA-256
  `85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41`.
- Sole candidate: the existing R59-builder K=5 artifact, 49,426,528 bytes,
  SHA-256 `e9c0848f5e256814387968c09006a44804e90a72aeb79034d0b12abfcce31abd`.
  Its orders one through four must equal the baseline table bytes exactly.
- Existing normalized training file, 23,373,369 bytes, SHA-256
  `871627e5fd2f84b4afa976516303098f437b5c339b7297db238fcd1ecb0e0434`.
  Its hash is already recorded in `r91/model_build/BUILD_RECEIPT.json`.
- Builder: `r59/blind/lm_build.cpp`, SHA-256
  `87b521d7654c07ead5b3bdbaa1da24c5ff60f10ae95b8f9aa8cf83673e2fc915`.
  Corpus source and acquisition pins are the existing R59/R91 records.

This K=5 artifact is a new candidate objective for this comparison. Its top
order uses raw five-gram counts. The unavailable historical K=6 model used
continuation counts at order five. Consequently this experiment is NOT a
replay of the original RX2-O version-three scoring model. No model is trained,
tuned, interpolated differently, or selected from additional alternatives.

The model and training file already exist locally and are bound by digest.
Repository source and public-source reconstruction instructions are retained;
the 49 MB model need not be embedded in a text commit. Any later reconstruction
must match its registered digest before it can verify this result.

## Cipher and neighborhood, completely finite

The cipher is the frozen RX2-O model from R94, unchanged. On zero-based
position i with alphabet indices in Z/26Z:

    tau_i = floor((i+r)/n)
    s1_i = d1*tau_i
    s2_i = d2*floor((tau_i+h)/26)
    m_i = W1(P_i+s1_i)-s1_i
    C_i = W2(m_i+s2_i)-s2_i

All contact operations are modulo 26. Plaintext/ciphertext are converted
using each record's supplied input/output alphabet, selected from the frozen
AZ/KRYPTOS/PALIMPSEST/ABSCISSA definitions. W1 and W2 are permutations.
Their inverse arrays U and V give the exact inverse:

    m_i = V(C_i+s2_i)-s2_i
    P_i = U(m_i+s1_i)-s1_i

There is no padding, insertion, deletion, transposition, unknown layout,
clock search, or final-block convention. Each record has exactly 97 letters.
The supplied labels and true synthetic keys define this diagnostic's inputs;
they are not recovered or claimed secret.

A worked three-contact analogue uses W1=[1,0,2], W2=[2,0,1], n=2, r=1,
h=1, d1=d2=1, and identity contact numbering. At positions 0,1,2 the fast
shifts are 0,1,1 and slow shifts 0,0,0. Plaintext [0,1,2] encrypts to
[0,0,2]; the two inverse permutations with those same shifts recover [0,1,2].

For each true key, enumerate every pair 0<=x<y<26, first swapping entries
U[x],U[y], then swapping V[x],V[y]. This is the same deterministic ordering
as R94's neighborhood: 325+325=650 labels per case, 31,200 total.
It equals all one-transposition neighbors in either forward wiring; swapping
inverse entries corresponds to swapping the named forward output values.
Every swap leaves both wirings bijective. Unchanged plaintexts from unused
contacts are retained and counted separately. Same plaintext on this input
does not establish full cipher-function or key equivalence.

## Scores and endpoints

For maximum order K in {4,5}, score a 97-letter plaintext by summing the
stored float32 log10 conditional probabilities, accumulated in float64:
at position i use order min(i+1,K), indexing the ending substring in base26
with its oldest character most significant. There is no word model,
normalization-dependent cutoff, plaintext feedback, or fitting.

All comparisons use epsilon=1e-9 on the full summed score:

- above truth: score(neighbor)-score(truth)>epsilon;
- tied with truth: absolute difference<=epsilon;
- below truth: difference<-epsilon.

Letter agreement is exact positionwise agreement out of 97. For each score,
the PRIMARY endpoint is the number of cases with ANY neighbor that has fewer
than 95 matches and scores above truth. It is not the number whose best wrong
neighbor is below 95. The previously reported 25/48 saved-best figure is only
a lower bound for this endpoint and is not assumed to be its baseline value.

The single candidate passes the proposed development selection bar if and
only if the run and verification are complete and that primary count is
at most 2/48. Outcome: GO_FOR_CONDITIONAL_DEVELOPMENT. More than two gives
SCORE_NO_GO. Report the identical baseline endpoint for comparison, but do
not use baseline performance to change the candidate's threshold.

Secondary descriptive outputs, separately for each score, case, and turnover
cell: all 650 score margins and matches; any wrong-text neighbor above truth;
any 95/96-match neighbor above truth; all ties including same-plaintext aliases;
counts by match class; the deterministic best wrong-text and best below-95
witness (exact numerical maximum of the stored score, with the first
enumeration label used only for exactly equal scores; epsilon is used only
for comparisons with truth). Retain full neighbor
plaintexts and swap metadata so the legal keys can be reconstructed, plus
true-record scores and the selected witnesses' complete synthetic keys.

Record whether each complete 97-letter true plaintext occurs verbatim in the
normalized training file. This is a fixed provenance diagnostic, not a row
filter or alternative pass rule. Zero such occurrences does not establish
absence of shared phrases, books, style, or development exposure. All 48 rows
remain spent development data regardless of this diagnostic.

## Verification, resources, and stops

One primary invocation and one separately coded verification invocation:

| Job | Wall ceiling | Aggregate CPU ceiling | Sampled aggregate RSS / per-process address space | Workers | Retries |
| --- | ---: | ---: | ---: | ---: | ---: |
| Primary complete comparison |300 s|240 s|1,024 MiB|1|0|
| Independent-code saved-evidence verification |300 s|240 s|512 MiB|1|0|

Both use the frozen `audit/run_bounded_agg.py`. The total experiment allowance
is at most 600 wall seconds and 480 aggregate CPU seconds across these two
jobs, not a resettable retry allowance. Imports, self-checks, model/input hash
validation, all comparisons and output writing count. Native thread counts
are fixed to one. Memory is sampled process-group RSS; brief spikes can be
missed and shared mappings may be counted twice. The same per-job memory
number is also an RLIMIT_AS ceiling.

Primary computation: two scores on 48*(650+1)=31,248 strings, each97letters;
31,200 neighbor records and48truth records maximum. Selected witnesses are
references to these strings, not extra searches. No optimizer, random seeds,
candidate generation beyond the fixed swaps, new restart or adaptive branch
exists. Byte caps and exact row counts are checked by the source.

The verifier imports neither the primary scorer nor its cipher implementation.
It independently parses the model, generates all labeled legal neighbors,
decrypts and forward-encrypts all retained plaintexts, evaluates scalar scores,
and recomputes every decision and summary. Numerical tolerance for checking
reported scores is1e-8; score comparisons themselves retain the1e-9 rule.
Any threshold-disposition disagreement is a verification failure, not a
rounding-based permission to choose an outcome. Both code paths must agree.

Any hash, dimension, witness, count, score, threshold, resource or exceptional
failure is INCOMPLETE, preserving partial files and resource logs. An existing
output directory is refused without overwriting it. No retry or amendment
after results is authorized by this work order. Prospective source corrections
before execution may be published and reviewed while preserving this scope.

## What this cannot establish

This is a synthetic-truth-assisted diagnostic, not blind recovery or a fresh
gate. It does not establish that the global optimum is correct, that a search
can reach it, that arbitrary wrong keys score lower, that altered spelling or
masked plaintext is handled, or that K4 uses any rotor. It estimates no false
positive rate and makes no K4 exclusion or solution claim. A pass permits only
separately specified conditional-solver development; a failure rejects this
one objective under this finite selection rule, not a cipher family.

R93's different-model review remains outstanding and is not replaced by this
internal review. Earlier frozen R94 files are not modified.
