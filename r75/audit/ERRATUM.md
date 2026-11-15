# R75 F1X — integer overflow and unsafe decode branch (additive erratum)

**Date:** 2026-11-15. **Classification:** CONFIRMED NUMERIC/RESOURCE DEFECT.
**Scope:** R75's crib-assisted F1X checker, subsequently reused by R83a.

## What went wrong

The original immutable `r75/sealed/exact.py` computes the number of
consistent root assignments using a NumPy **signed int64** product,
`nsol *= ok.sum(axis=1)`. A sufficiently underconstrained graph
can have 26 to the power of 14 or more root assignments. That product
overflows 64 bits, sometimes wrapping to a small or negative value.

The original checker then compares that wrapped value to a small
decode limit. In the worst case it enters a loop enumerating an
astronomical number of root combinations. This is **not** a K4
cryptographic contradiction and can cause runaway CPU/RAM usage.
The R83a F1X DROP run hit the issue on shuffled ciphertext
NULL_010 and NULL_011; those jobs required a separate low-memory
feasibility-only rerun.

## What the defect does and does not invalidate

- **Invalid / not trusted without recheck:** solution counts for
  any overflow-prone F1X setting, and any conclusion derived
  from a completed enumeration presumed to be small because an
  int64 counter wrapped. A killed or timed-out worker is
  INCOMPLETE, never an exclusion.
- **Not automatically invalidated:** a graph feasibility check
  completed before multiplying the solution counts; the R75
  blind K4 NO_SIGNAL result; unrelated R75 F2X/F3X/F4X
  families. Their validity requires separate audits, not a
  blanket certification from this note.
- The legacy R75 source and all original frozen K4 artifacts,
  preregistration and SHA manifests are preserved unchanged.

## Safe replacement for future audits

`r75/audit/f1x_safe.py` is a **separately written, standard-library
graph-consistency checker**, not a mutation of the frozen R75
algorithm. For a FIXED convention and two declared periods it:
1. Constructs the permutation relating the two stage key slots
   for each known-position plaintext/ciphertext pair.
2. Finds all bipartite connected components independently.
3. Tests precisely the 26 possible root values in each
   component, counting consistent roots.
4. Multiplies counts as **arbitrary-precision Python integers**.
5. Reports exact feasibility, active-root-assignment count,
   unobserved slots, and all-full-key assignment count, with
   no candidate plaintext, key-completion or decoder branch.

The checker is **post-freeze, crib-assisted only** if passed K4's
published known-plaintext characters. It must not supply a K4
candidate generator, ranking model or language model.

## Independent synthetic checks

`r75/audit/tests/test_f1x_safe.py` uses a separate explicit
encryptor and toy brute-force oracle. It verifies:
- Agreement with exhaustive full-key enumeration for 1+1,
  1+2 and 2+1 keyword slots.
- Valid planted messages across four alphabets, both signs,
  and periods up to 26.
- Contradictory graph cycles are rejected.
- A graph with 17 independent components has EXACTLY
  **26^17 active solutions** (greater than 2^63) and
  **26^19 complete key assignments**, without overflow
  or enumerating a single completed key.
- Bad inputs and implicit unbounded period scans are rejected.

GitHub Actions verified the synthetic tests and source-import
guard: https://github.com/tylerj-spec/kryptos-k4/actions/runs/43734956416

## Still required before a historical exclusion is promoted

A separate follow-up must run the new checker on a bounded and
preregistered set of original R75 F1X known-position conditions
and compare feasibility **setting by setting** with the archived
outputs, including overflow-prone periods 15–18 and the
problematic R83a shuffled controls. The test must record all
disagreements rather than retroactively rewriting R75's result.
It needs an independent reviewer, with results in an additive
audit file rather than the old sealed directory.

This PR is a software-safety and count-correctness repair, not
a new full K4 reanalysis or K4 candidate discovery.
