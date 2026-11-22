# R91: close the archived R82 and PTAK solver-power backlog

**Synthetic controls only. No K4 run is authorized by this round.**

This is a fresh, preregistered **necessary-condition power screen**. The true
cipher family and structural settings are deliberately supplied; the complete
97-letter message and secret key are concealed. Passing is not unknown-family
recognition. Failing a required stratum rejects this bounded solver attempt
for the broad proposed method-identification gate; it does not reject the cipher.

## Provenance and exact question

R82 draft PR77 at `1550736de568abdf442686e4a15b8889c585f2f3`, especially
`r82/council/BUILD_GATE.md`, deferred a linked-key method gate. Its only
implemented key solver was a unigram factor-graph annealer with 12 restarts,
100 stochastic coordinate updates and at most seven greedy sweeps. Long-key
developer controls had poor power. R91 tests that actual solver on fresh books.
The earlier generic 2x13 construction and R89/R90 finite fractionation
catalogs are separate; R91 is not another fractionation search.

R68's plaintext-autokey solver was weak at lags13–24 in the historical power
review. R91 tests the actual archived primer optimizer at those lags, using
its original order-four language score and 20 restarts/20 sweeps. It does not
replace that score with a deliberately weaker model.

The necessary-screen argument applies to a proposed unknown-structure
pipeline that uses the **same one returned key per structural branch, seeds,
effort and scoring**, and requires recovery in every declared stratum. Later
reranking cannot recover the correct key from its true branch if that branch
discarded it. This is not a theorem about a different optimizer, larger
beam, other seed schedule, or an equivalent branch returning the text.

## Arm L: shared-key linked tableaux

AZ is the ordinary alphabet; KRY is the keyed KRYPTOS alphabet. The fixed
charts are AZ→KRY followed by AZ→AZ, with positive shifts at both stages.
For key K of primitive length m and width w, the two key indices are
`r=i mod m` and `s=(i+floor(i/w)) mod m`.

`mid_i = KRY[(AZ_index(P_i)+AZ_index(K_r)) mod26]`

`C_i = AZ[(AZ_index(mid_i)+AZ_index(K_s)) mod26]`.

The inverse undoes the second shift, takes the KRY index, then subtracts
the first shift. `reference.py` implements independent scalar directions.

**Bounds:** m∈{3,4,5,7,9,12}; w∈{m,m+2,31}:18 strata. Each gets20 messages,
giving360 positive controls. The solver receives m and w. It does not search
other chart/sign configurations, and a pass cannot establish power there.

**Frozen solver:** the archived `vendor/r82/pairwise_pilot.py` unchanged.
It maximizes the supplied unigram log score through 12 starts,100 stochastic
updates/start and≤7 greedy sweeps. Only its best complete key is retained.
Per-input RNG seed is the first15 hex digits of SHA256 of
`R91_R82_12x100|` followed by canonical JSON of ciphertext,m,w (sorted keys,
compact separators). IDs do not affect this arm's seed. The ciphertext and
structural metadata are the only input-dependent seed material.

## Arm P: archived R68 plaintext autokey

Use the original21 route/model rows: ID once and ten R61 routes under M1/M2.
For route permutation π, the path ciphertext Y obeys `CT[j]=Y[π(j)]`.
M1 has plaintext in path order; M2 has `P[j]=Q[π(j)]`.
Ap,Ac∈{AZ,KRY}; op∈{VIG,BEAU,VARB}. Set x=Ap_index(Q_t), y=Ac_index(Y_t).
The encryption is respectively `y=x+k`, `y=k−x`, or `y=x−k` modulo26.
For t<L, k is the corresponding secret primer shift; thereafter
`k_t=Ap_index(Q_(t−L))`. The inverse reconstructs Q sequentially.

**Bounds:** L=13,14,…,24:12 strata,20 controls each,240 total. Each control
gets a uniformly selected R61 path, permitted model and one of12 conventions.
Its true structural settings are supplied to the optimizer. The primer is
uniform over AZ shifts, rejecting a nonprimitive full primer string.

**Faithful preserved optimization:** `derive_ptak_screen.py` makes eight
checked replacements in the archived `vendor/r68/keyed_solve.cpp`. These
select the supplied convention/lag, remove unrelated families, adapt public
row metadata, remove later order-six/word reranking, rename the resulting
score field, and install input isolation. The complete PTAK primer optimizer,
order-four score, loops,20 restarts,≤20 sweeps and mt19937_64 remain unchanged.
The ordinary periodic branch is disabled with PMAX=0.

The original seed formula is retained: seed68, FNV hash of row ID
`<public-id>__<R61-path-index>__<M1-or-M2>`, lag, family index1 and convention
index. Candidate key choice occurs before the deleted downstream rescoring.
The screen cannot certify the old complete unknown-path/family classifier.

**Exact model restoration:** all14 original training novels and all5 NLTK
ZIP digests match the archived corpus builder, plus the original Carter file.
Training text has23,373,368 letters. Building with K=5 gives the same
continuation-count tables for orders1–4 as K=6; the differing top order is
discarded. `MODEL_RECEIPT.json` records the source and corpus hashes. The
1,901,024-byte extracted model is SHA256
`85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41`.
The full order-six model was not rebuilt and is not claimed to have been replayed.
The equality claim follows from the pinned builder and identical training
corpus: orders below five use continuation counts from the next order and
recursively use only lower-order tables. No direct byte comparison with the
unavailable historical order-six binary has been performed.

## Fresh sources and generation

The three books and exact raw hashes/URLs are fixed in `SOURCES.json`:
The Red House Mystery (narrative), Common Sense (political essay), and
The Analysis of Mind (analytic nonfiction). No use of these titles was found
in main's named corpus/preregistration references. They are outside the
named R59 training books. Generator checks further reject any complete
97-letter window appearing in the reconstructed training corpus.

Generator seed912211; Python `random.Random`. Strip Gutenberg header/footer,
uppercase, retain A–Z. Each stratum cycles across the three sources (6 or7
per source); windows are97 letters, nonoverlapping within each source across
both arms, and unique across the whole600 controls. Sampling excludes500
letters at either end of each stripped book. Each draw gets≤100,000 attempts;
exhaustion is an infrastructure failure, never a cryptographic negative.
The complete600 cases are generated once; no replacements or resampling.
Ordinary English only: no masking, other-language or corruption claims here.

## Decisions fixed before holdout generation

For every stratum, require **≥18/20 exact97-letter messages AND the true key
or a proved equivalent key**. For R82, key equivalence is checked over all26
plaintext symbols at every position in one full m×w slot-schedule period.
For PTAK, the first L plaintext symbols determine the primer uniquely, so
key equality is required. Report≥95 letters, exact message and exact key
separately as diagnostics; none replaces the main criterion.

- If any stratum in an arm fails, that broad bounded solver attempt is
  **SOLVER_NO_POWER / NO-GO**. It cannot advance to the proposed full-method
  gate. The cipher family and untested methods remain OPEN.
- If every stratum passes, the result is **SCREEN_PASS_ONLY**. It still
  needs a separately registered hidden-structure/unknown-family gate with
  the originally proposed wrong-family controls. It does not authorize K4.
- Missing records, a failed forward witness, failed input-isolation probes,
  changed hashes, or exhausted resources yield **INCOMPLETE**, never NO-GO.

Wrong-family negatives are unnecessary to reject an arm that cannot pass this
mandatory easier recovery stage. Therefore no200-negative method-recognition
experiment is claimed here. The deferred classification gate terminates as
not eligible if this necessary stage fails; a more capable solver is new work.

## Freeze and isolation sequence

1. Commit and push this preregistration, all code/model/provenance hashes and
   the fixed resource limits. No fresh window or secret key exists yet.
2. In a later commit, bind the exact preregistration commit/hash in
   `QA_MANIFEST.json`. Generate the600 public ciphertext/structural records
   and only the private truth's SHA256. Keep truth outside the repository.
   Commit and push public inputs and truth commitment.
3. Compile the pinned kernels, run both arms once, and independently verify
   all forward encryptions without reading truth. Save complete97-letter
   outputs and keys, model/code/binary hashes and aggregate resource logs.
   Commit and push the complete output freeze.
4. Only then open truth, evaluate fixed criteria and publish the truth,
   result and narrow closure statement. Do not alter frozen inputs/outputs.

This host disallows mount/network namespaces and has no Landlock syscall.
Candidate kernels instead preload approved inputs/model/code, open the output
stream, then install a **thread-synchronized seccomp** filter that denies all
new filesystem opens, sockets, exec, process-memory access and io_uring.
They probe that a new file open and network socket each fail with EPERM;
failure aborts before solving. R82 closes unrelated descriptors first. The
PTAK executable only has its declared model/input/output descriptors. No
private truth, raw source book, repository clue file or network input is
loaded into candidate kernels. OS probes are recorded in development evidence.

## Finite resource bounds

Per formal arm: wall≤1800s, aggregate CPU≤1800s, aggregate sampled RSS≤2048MiB,
one candidate kernel, zero retries. Resource wrapper:
`audit/run_bounded_agg.py`; its sampling caveat remains explicit. Dataset
generation and evaluation each get the same conservative cap. Maximum saved
candidate records:360 for R82,240 for PTAK,600 total. No adaptive restarts.

PTAK has at most20×20×24×26 candidate coordinate evaluations per message,
plus initial evaluations. R82 has exactly12 starts with the finite update
bounds above. No unconstrained branch enumeration or integer products occur.

Spent development evidence:1,200 random round trips per reference family,
six cases/arm from already revealed R59 development plaintexts, no tuning.
R82 recovered4/6 exact; PTAK4/6 exact. Candidate-kernel seccomp probes passed.
These are implementation/runtime checks, not the fresh gate.

## Review status

One ChatGPT execution team. Internal subtasks are not independent models.
Independent review of this new gate execution: NONE. Original frozen
experiments stay intact. No new K4 candidate, K4 score or ledger exclusion.
