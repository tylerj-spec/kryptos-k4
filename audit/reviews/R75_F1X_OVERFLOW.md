# Independent R75 F1X numeric audit — evidence review

Affected ledger IDs: L165, L172
Validation: CI run 43734956416 passed synthetic independent brute-force oracle, max-period planted controls, a contradictory-cycle test, and 26^17 arbitrary-precision regression.

## Scope

The older R75 F1X code can overflow the int64 product of
connected-component root counts. A wrapped count may
incorrectly enter an unbounded plaintext-enumeration loop.
R83a's two shuffled cases demonstrated the operational risk.

The independent replacement checker under r75/audit/f1x_safe.py
does not decode and uses unbounded Python integers. It is not
the frozen R75 program and does not alter any original K4
result. Its algorithm is checked independently using a toy
full-key enumeration and a 26^17 boundary counterexample.

## Disposition

- Preserve original R75 K4 NO_SIGNAL, exact feasibility records,
  original hashes, and R83a low-memory rerun provenance.
- Mark historical F1X solution counts above the signed-int64
  boundary as UNTRUSTED pending independent re-enumeration.
- Do not extrapolate one numeric bug into a false blanket
  elimination of R75 F2X/F3X/F4X or R83a EXACT constraints.
- Never use the old f1x() for a new feasibility-only run.
- Require the post-freeze setting-by-setting replay plus
  independent review before new F1X exclusion labels.

References: r75/audit/ERRATUM.md;
https://github.com/tylerj-spec/kryptos-k4/actions/runs/43734956416
