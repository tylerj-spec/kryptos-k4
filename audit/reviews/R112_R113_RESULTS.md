# R112–R113: L200–L201, general same-column Slidefair check and the lag-21 step-1 simulation (synthetic)

Affected ledger IDs: L200, L201

Validation:
- **Order of commits.** Both rounds pushed their pre-registration alone, then their source, then their frozen
  outputs, then the result note:
  - R112: bb84541, 111c0d1, 3708a6c;
  - R113: 0fe82fa, f20d56e, then its freeze commit.
- **Resources.** Both are COMPLETE under `audit/run_bounded_agg.py`: R112 405 s, R113 56 s, zero retries.
- **No K4 input.**
- **CI.** `r112-r113-synthetic.yml` re-runs both and compares every result except timings.
- **Guardrail check:** PASS.

Independent review: NONE. One model (Claude Code) built and ran both. They join audit batch C.

## Summary
- **R112 (L200).** X112 handles Slidefair's same-column rule exactly, for any number of crib pairs, with one bad pair
  optional.
  - It is sound on 400 plants with up to 9 same-column crib pairs.
  - It agrees with a brute-force reference on 1,960 cells.
  - Its chance exclusion with any key is 0.58, close to R107's conditional 0.59.
  - It is ROBUST at p 1–8 with one bad pair.
  - The K4 run is proposed as P6.
- **R113 (L201).** CLOSE. The lag-21-adjacency decimations make R₂₁ ≥ 11 only about 3–3.7 times likelier than R71's
  running-key baseline. Their conservative ratios of 1.8–2.3 fall short of the registered 10×. P5 is closed.

## Points for the auditor
1. **R112's sign error.** The source commit records a Beaufort same-column sign error in the dev prototype, caught by
   T1 before the source was committed. The pre-registration's development figures came from that prototype.
2. **R113's C3 threshold.** It was re-operationalized before the registered run, after a dev smoke run failed the
   code's first choice (a ratio above 2). The pre-registration's wording was "far above". This is disclosed in the
   source commit.
3. **The shared equation table.** R112's reference shares the per-pair equation table with X112. T1 checks that
   table directly against R98's reference cipher.
