# R92 independent exact and saved-evidence audit plan

Reviewer: ChatGPT, a different model from R92's Claude Code builder.
Baseline: `9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1` (merged PR #104).
Mode: **POST-FREEZE, CRIB-ASSISTED, AGGREGATE-ONLY EXCLUSION AUDIT**.

This plan must be committed and pushed before its target computation. The
independent checker and synthetic evidence must also be committed and pushed
before the target computation. No frozen experiment file is changed. This is
not a new blind search, a candidate generator, or a rerun of the original
language-model optimizer. No target result will enter RX2 engineering.

## 1. Exact finite scope

Re-derive R92 independently: one arbitrary permutation wiring, input/output
contact alphabets AZ, KRYPTOS, PALIMPSEST and ABSCISSA, direction +1 or -1,
and `s_i = d * floor((i+r)/n)` for `(n,r)` in
`(2,1),(3,1),(3,2),(4,1),(4,2),(4,3)`. There are 192 labeled settings.

Replay all 201 unchanged inputs already frozen in `r92/k4/TARGET.tsv`:
38,592 all-observation decisions and 926,208 single-deletion decisions,
964,800 decisions in total. Compare every retained exact/drop count and
maximum-check statistic in R92's archive; report any disagreement and stop
promotion. The 24 individual deletion counts are retained by this audit for
every input, even where the original archive retains only their aggregate.
Report distinct settings admitting any deletion separately from the sum of
setting/deletion pairs. No feasible setting, wiring assignment, key completion
or decoded text is emitted.

Also audit the already-tested R87 zero-phase subset **n=1..4 only**: 128
labels, on the same 201 frozen R92 inputs. This adds 25,728 base and 617,472
single-deletion decisions. Together these domains are 320 labels, every
boundary phase for n<=4, and **1,608,000 total logical decisions**.
The R87 original K4 aggregate must be compatible with the subset result.
This does not replay R87's full n<=96 scope, its historical null panel, its
two-error diagnostic or its blind optimizer, and cannot promote full L176.

## 2. Independent mathematics and code path

For each observed `(i,p,c)`, form
`x_i=(E_in.index(p)+s_i) mod26` and
`y_i=(E_out.index(c)+s_i) mod26`.
Make a conflict graph on observation indices: connect i,j exactly when
`(x_i==x_j) != (y_i==y_j)`. A permutation exists exactly when this graph has
no edge: the required partial relation is then a bijection and extends to a
permutation by pairing unused contacts.

Deleting observation j leaves a feasible relation exactly when every conflict
edge is incident on j. Intersecting each edge's two endpoint bits therefore
computes all single-deletion results together. This checker imports no R92,
R87 or other original cipher/evaluation implementation. It never constructs
the unspecified portion of a target wiring.

Because the schedule depends only on position, a substituted plaintext symbol
or ciphertext symbol affects one observed pair. The deletion test covers an
unknown single substitution at a published position; a substitution elsewhere
does not affect these constraints. It does not cover insertion, deletion,
lost/extra state updates, changed positions, or simultaneous errors at distinct
positions. Exact feasibility is independent of the language of the unobserved
text; the blind English solver's power is a separate question.

## 3. Synthetic checks before target access

Use an independently written forward cipher with an advancing position counter,
rather than the floor formula, and enumerate every toy wiring. Exhaustively
compare all four-symbol plaintext/ciphertext pairs for q=2,3,4 and four fixed
phased schedules, including both directions and composite modulus 4. Compare
both exact feasibility and all four deletion outcomes to that permutation
oracle (289,412 labeled plaintext/ciphertext/schedule cases).

Use seed 921105 for 97-symbol planted tests at all 320 registered real labels,
with an independent 24-observation synthetic mask containing the endpoints.
Check inverse round trips, every single-position plaintext substitution
(re-encrypted from the altered plaintext), and every ciphertext substitution.
Test position-local propagation and the appropriate surviving deletion, with
unobserved substitutions leaving feasibility intact. No K4 mask is used in
these synthetic checks.

Verify the algebraic corrections with synthetic examples: translation wirings
overlap zero-phase and phased schedules; setting the second RX2-O wiring to
identity embeds every first-rotor phase in scope. Recount the 192-label and
145,728-label n=5..96 timing domains without reading target observations.

## 4. Saved evidence and provenance

Independently forward-encrypt every stored gate candidate (202*5=1,010) and
every stored target/null candidate (201*5=1,005), check structural domains,
permutation validity, record IDs, best/top consistency and saved-score order.
Recompute gate recovery, exactness, used-contact key agreement, cell/genre/mask
counts, extras and negative-panel arithmetic from frozen records. Verify
positive/extra truth encryptions; for ciphertext-error extras verify the one
changed symbol against the clean ciphertext. Negative generator labels and
source code are reviewed; this plan does not regenerate unpublished raw books.

Recompute target evaluation arithmetic from the saved candidate records and
saved scores, including hits, all 200 null comparisons, add-one p, score cuts
and contender counts. Regenerate the already-frozen shuffle sequence with
seed 920400 and verify byte equality. No new plaintext is decrypted or fitted.

Check all accessible protocol/freeze/runner manifests, the truth commitment,
source bytes at the baseline and historical freeze commits, recorded resource
logs, sandbox allowlists and Git ordering. Report missing paths or untracked
model bytes explicitly. A Git ancestry check establishes commit ordering, not
the historical instant of a push or first local read. Raw source-book novelty,
training overlap and unavailable model bytes are not independently certified.

The saved pipeline uses quadgram pruning to 48 of 192 labels and then LM
rescoring/polishing; its retained maximum is not the LM optimum over all
wirings or all 192 labels. No original optimizer or LM rescoring is rerun.
Resource overruns disclosed for development remain deviations; an exact
replay does not retroactively certify them as compliant.

## 5. Bounds, publication and verdict

Run through `audit/run_bounded_agg.py`. Synthetic checks use
`SYNTHETIC_BUDGET.json` (180 seconds wall, 120 seconds aggregate CPU,
512 MiB). The one target/saved-evidence job uses `BUDGET.json`
(300 seconds wall, 180 seconds aggregate CPU, 1,024 MiB). Zero target retries.
All counts use Python integers. Save aggregate JSON, source/input hashes,
resource logs and a signed review under this additive directory.

Any failed oracle, changed frozen evidence, contradiction, missing required
record or exhausted resource budget blocks promotion and is reported as
INCOMPLETE or a concrete disagreement. A completed exact exclusion can support
a named narrow L181 promotion if independently reproduced. Scope corrections
are additive; neither a survivor nor a statistical NO_SIGNAL is a new solve.
