# R93 preregistration: the wider nonzero-phase single-rotor scope

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY.**

This is a new finite mathematical compatibility audit, not a blind decoding
round or a rerun of R92. `MODE_CLARIFICATION.md` records the user's authorization
and the explicit exact-checker correctness gate. No target ciphertext is read
until this registration, the complete source package and a successful gate
result have been committed and pushed in that order.

## 1. Reversible model and exact domain

Positions are zero-based and the message length is 97. Contact alphabets are
AZ, KRYPTOS, PALIMPSEST and ABSCISSA, each keyword first followed by unused A–Z
letters. The input and output choices are independent, giving 16 pairs. The
wiring W is any permutation of 0…25, with no language restriction.

For period n, boundary phase r and direction d, define

`s_i = d * floor((i+r)/n)`.

Encryption and its inverse are

`c_i = E_out[(W[(E_in.index(p_i)+s_i) mod 26]-s_i) mod 26]`,

`p_i = E_in[(W_inverse[(E_out.index(c_i)+s_i) mod 26]-s_i) mod 26]`.

The exact registered domain is **n=5…96, r=1…n−1, d∈{−1,+1}**, all 16
contact pairs and any W. Initial angular orientation is absorbed into W; the
boundary phase changes transition positions and is explicitly enumerated.
There is no transposition, feedback from letters, reset, missing update, null
insertion or alignment change.

Worked q=5 example: with identity contact labels, W=(2,4,1,0,3), n=5, r=4,
d=−1 and plaintext indices (0,1,2,3,4,0,1,2,3), the offsets are
(0,−1,−1,−1,−1,−1,−2,−2,−2), and ciphertext indices are
(2,3,0,2,1,4,0,4,1). The independent event-clock reference must reproduce and
invert this example.

## 2. Labeled counts, equivalences and previous coverage

`16 * 2 * sum(n-1 for n in 5..96) = 145,728` labeled settings.

The earlier figure **145,920** includes all nonzero phases for n=2…96;
R92 accounts for its n=2…4 contribution of **192**. It is incorrect to use
145,920 as the n=5…96 remainder.

Over 97 positions, the 9,108 clock labels in this registration induce 4,690
distinct offset sequences modulo 26. With contact pairs this gives 75,040
distinct clock/contact labels. There are 94 clock sequences also represented
by R87's zero-phase n=1…96 clocks: 1,504 clock/contact labels, corresponding
to 36,096 labels in the full R93 enumeration. The remaining distinct
clock/contact labels number 73,536. No R93 clock equals an R92 n=2…4 clock.

Why duplicates arise: a clock with two transitions determines both its first
boundary and period; a clock with only one transition records only that
boundary. The latter has multiple (n,r) representations. Adding a constant
offset is absorbed by conjugating W. All listed phases start at offset zero,
so normalized equality reduces to equality of the finite sequences. These
counts are reproduced by an independent synthetic scope script before the gate.

The audit retains **all 145,728 labels**, including overlaps and multiplicities.
No parameter is dropped based on an earlier K4 result. Distinct schedules do
not prove disjoint sets of ciphertext functions: special wirings can make
different schedules agree. Neither labeled settings nor distinct clocks are
independent statistical trials.

Prior exposure is disclosed: R87 and R92 outcomes and their stated scopes were
known before this work. The wider domain was already specified algebraically in
the work order; no surviving K4 setting or published-letter score selected it.
No R93 output may be transferred to RX2 research or any blind candidate process.

## 3. Exact compatibility and single-observation deletion

For each supplied observation (i,p_i) and ciphertext symbol c_i, a setting
implies the contact pair

`x_i = (E_in.index(p_i)+s_i) mod 26`,

`y_i = (E_out.index(c_i)+s_i) mod 26`.

A complete wiring exists **iff** these pairs form a partial bijection. Every
such partial bijection extends to a permutation by matching unused inputs and
outputs, but the target program must not construct that completion.

Equivalently, create an inconsistency edge between observations a,b when
`(x_a == x_b) != (y_a == y_b)`. EXACT is feasible iff there are no edges.
Deleting observation j is feasible iff every inconsistency edge touches j.
The admissible deletions are therefore the intersection of the endpoint sets
of every inconsistency edge; with no edges all 24 deletions are admissible.
This evaluates all deletions exactly, with no wiring search or branch cutoff.

Record only three integer counts per input:

- `exact_feasible_labels`: settings satisfying all 24 observations;
- `drop_feasible_labels`: settings satisfying at least one of the 24
  single-observation omissions;
- `drop_feasible_label_observation_pairs`: the sum over the 24 omissions.

DROP is an **at-most-one** observation relaxation, including exact settings.
The schedule is position-only. One erroneous published plaintext symbol
changes only its pair. One fixed-length ciphertext substitution changes only
its position's pair; if it lies outside the observed positions it changes no
pair. Thus absence of any DROP-feasible label excludes either error model
separately within scope. This does not cover simultaneous plaintext and
ciphertext errors, insertions/deletions, shifted positions, or a lost state
update. Such errors can affect more than one constraint.

The target only evaluates compatibility. It emits no decoded text, partial
wiring, completed key, surviving setting list, ranking or strength statistic.

## 4. Independent correctness gate: all requirements must pass

Gate type is **EXACT_CHECKER_CORRECTNESS**, explicitly not blind recovery.
The separately implemented reference uses an event-countdown clock and tries
complete wiring permutations in its toy oracle. It imports no R87/R92 checker.
The production kernel uses the pairwise conflict/intersection theorem above.

1. Exhaust all ordered contact-pair lists of lengths 1…6 for q=2, 1…5 for
   q=3, and 1…4 for q=4: **141,793 cases**. Compare EXACT and every possible
   omitted observation with enumeration of all q! complete wirings. Require
   zero false exclusions, zero false feasibilities and zero deletion-mask
   disagreements.
2. Independently encrypt and decrypt 97-symbol plants for every n=5…96,
   phases {1,floor(n/2),n−1}, both directions and all 16 contact pairs:
   **8,832 parameter plants**. Seed **930101**. Cycle random symbols,
   repeated-pattern symbols and cyclic alphabet symbols; use fresh generated
   permutations. Observation sets have 24 positions, include message and step
   boundaries, and are generated without the K4 observation mask. Every true
   setting must be accepted and every full round trip must match all 97 symbols.
3. For every plant, test a changed plaintext symbol with re-encryption, a wrong
   reported plaintext observation, a ciphertext substitution at an observed
   position, and a substitution outside the observations. Require the stated
   one-pair propagation and the true setting's acceptance under the matching
   EXACT or DROP model. A separately constructed lost-update example must show
   multiple-position propagation and is explicitly outside the exclusion.
4. Challenge a one-edge conflict (either endpoint deletion is valid) and two
   disjoint conflicts (no one-observation deletion is valid). Require exact
   agreement with the independent toy oracle. Random/wrong-family synthetic
   inputs have oracle-defined feasibility, not an assumed negative label.
5. Reproduce the schedule counts in §2, the worked example, all four alphabet
   permutations, the compiled kernel's complete labeled count, and successful
   handling of short observation lists, repeated contacts and negative offsets.
6. Run the full registered scan on three deterministic synthetic random
   97-symbol ciphertexts with 24 unrelated observations, seed **930102**.
   Verify aggregate accounting and forecast the 201-input target job using
   **twice** the measured 3-input scan CPU and wall time, scaled by 201/3,
   plus 10 seconds for compilation/startup. Both forecasts must be below 80%
   of their respective target caps. No K4 data are used in this benchmark.

All cases and expectations are deterministic public correctness tests. They
are not hidden English recovery controls; no language model, training corpus,
confidence cut, method-recognition rate or false-positive classifier claim is
part of R93. The kernel receives only numeric pairs or ciphertext/observation
data, never an expected verdict or true wiring.

A completed mathematical check with a mismatch, or a completed benchmark with
a failed resource forecast, means **NO-GO**. An invalid source hash,
infrastructure failure, cap exhaustion or otherwise incomplete validation is
**INCOMPLETE**, not a scientific NO-GO. Both outcomes block the target. Preserve
the evidence and report the failure. A later repair requires an explicitly
named amendment and new gate, not an overwrite or automatic retry.

## 5. Target inputs and nulls, only after published GO

Use the unchanged 97-letter ciphertext from
`r39/ic_gate/k4_ciphertext.txt`. Verify the source file bytes, including its
trailing newline, against canonical SHA-256
`2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.
Then strip surrounding whitespace and require exactly 97 A–Z letters.
Read the fixed published observation list from the pinned `CLUES` literal in
`r73/sealed/reveal_k4.py`, using literal parsing rather than importing its
executable code. Its complete file hash is pinned in the source manifest
before the gate. Require 24 unique, in-range positions and valid A–Z symbols.

Generate 200 distinct frequency-preserving ciphertext shuffles with Python's
`random.Random(930400)`, rejecting a duplicate or the original, with a hard
10,000-draw cap. Preserve the ordered target/null input file. Every input gets
the identical full labeled scan and the same observation list.

There are **29,291,328 base setting/input calls**, corresponding to
**732,283,200 logical EXACT-or-single-deletion tests**. The shared conflict
criterion evaluates these without separately repeating the 24 deletions.
Report per-input aggregate counts and how many of the 200 nulls admit any
EXACT or DROP setting. These nulls are descriptive compatibility controls.
There is no p-value, strength ranking, LEAD label or candidate selection.

## 6. Resources, integers and stopping

Formal synthetic gate: <=180 seconds wall, <=120 aggregate CPU seconds,
<=512 MiB sampled aggregate RSS. Target audit: <=1,800 seconds wall,
<=1,200 aggregate CPU seconds, <=512 MiB sampled aggregate RSS. All jobs use
`audit/run_bounded_agg.py`; one deterministic kernel, no worker pool, zero
target retries and zero candidate outputs. The wrapper also imposes a
per-process address-space cap; its sampled memory semantics are retained.

All accumulated counts and domain products are Python integers. The compiled
kernel emits only a bounded per-setting feasibility bitfield for aggregation
through a pipe; it does not multiply or accumulate a number of wiring
completions. At most 24 omission bits and one exact flag are needed.

There is no expensive branch enumeration and no heuristic UNSAT decision.
An interrupted process, malformed input, wrong record count, hash mismatch or
any resource breach produces **INCOMPLETE / UNKNOWN**, never an exclusion.
No fallback sampling or automatic budget extension is allowed. Nonzero
feasibility is a completed compatibility result, not an instruction to inspect
a key or extend the scan.

## 7. Publication and decision stages

1. Commit and push this preregistration and `MODE_CLARIFICATION.md`.
2. Commit and push the complete source files, source hashes, the bounded
   validation plan and QA manifest naming the exact preregistration commit.
3. Run the formal correctness gate. Commit and push its result, complete source
   receipt and wrapper log. Set `gate_type: EXACT_CHECKER_CORRECTNESS`,
   `gate_verdict: GO` only on full success, and
   `blind_recovery_certified: false`. A source change restarts this stage under
   an additive amendment.
4. After the coordinator confirms publication, run the target once. Write and
   freeze the complete target/null inputs, aggregate counts, source receipts,
   QA manifest and resource log with SHA-256 entries. Commit and push before
   writing the interpretive verdict or updating the ledger. This is a
   crib-assisted output freeze, not a claim of pre-clue blind generation.
5. Publish a separate result note and scope review. EXACT with zero feasible
   labels supports `EXACT_SCOPE_EXCL` under all-correct observations. DROP with
   zero feasible labels supports the stated one-error extensions. A positive
   count means `COMPATIBLE / OPEN` for that check. INCOMPLETE keeps the entire
   affected claim OPEN. No result is fed to RX2 or a candidate generator.

**Independent review: NONE** for a new ChatGPT build reviewed by same-model
agents. The independent oracle is an independent code path, not another model.
No `INDEPENDENTLY VERIFIED` ledger promotion is requested by this round.

## 8. Explicit limits

The exact constraints do not depend on English, masking or another language
provided the supplied observations correctly describe the actual enciphered
symbols. The audit cannot adjudicate changes to those observations beyond the
registered one-symbol relaxation. It does not cover new contact alphabets,
other step sizes, multiple rotors, irregular or letter-triggered updates,
transposition, insertion/deletion, alignment changes, simultaneous error
models, or n>=97. Some omitted finite schedules overlap earlier scopes; no
broader claim is inferred without its own proved accounting. There is no
English-recovery result or K4 plaintext candidate in R93.
