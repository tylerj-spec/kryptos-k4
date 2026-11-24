# R100: L189, Quagmire-type plaintext autokey with two tier alphabets, EXCLUDED at the 12 decidable lags

Affected ledger IDs: L189
Validation:
- **Order of commits:**
  - pre-registration f6307c6, with `PROTOCOL.sha256`;
  - then source and `SOURCE.sha256` at 6b9a4a9;
  - then the gate (seed 1000901) GO, frozen in 2b24690;
  - then the target, frozen in 44efbc0. That freeze was pushed and the remote blobs checked before evaluation.
- **Gate results:**
  - V1 400/400.
  - V2: 0 mismatches for both checker paths against a reference-encryptor brute force.
  - V2b: fast path = simple path on a 300-alphabet sub-tier.
  - V3 32/32 three ways.
  - V4: Quagmire I–IV autokeys, 16/16.
  - V5 forecast 537 of the 960 s limit.
- **K4:** EXACT 0 at all 12 scanned lags, and DROP 0 at lags 1–5.
- **Shuffles:** 1/100 has one chance EXACT setting; none has DROP.
- **Second algorithm:** per-cut integer joins; agrees on K4, with a synthetic positive control.
- **Resources:** all jobs COMPLETE under `audit/run_bounded_agg.py`, zero retries. Guardrail check PASS.
- **CI:** `.github/workflows/r100-quagmire.yml` re-checks every manifest, recounts all 101 frozen inputs, re-derives
  the shuffles and the decision, and runs the second algorithm on K4.

Independent review: NONE. One model (Claude Code) registered, built and ran R100. ChatGPT is the named
different-model reviewer.

## Summary
This is the third construction-discovery slot of the PR #113 plan. It is choice 1 of
`audit/reviews/CONSTRUCTION_LANE_REVIEW_20261124.md`. Tyler's instruction, 24 Nov: "continue with the plan".

**Cipher:** B⁻¹(C_i) = s1·A⁻¹(P_i) + s2·F⁻¹(P_{i−L}) + c.
- **Alphabets:** plaintext alphabet A and ciphertext alphabet B, each any of R76's 77,229.
- **Feedback numbering** F: A, B (the Quagmire convention) or A–Z.
- **Signs:** all four.
- **Constant and primer:** any.

**Why the check is sound.** Each direct link (both letters published) gives one congruence that separates into a
B-side and an A-side term. Eliminating c turns every tier × tier pair into an exact join. These are necessary
conditions, so a zero count is an exclusion.

**Result:**
- **EXCLUDED** at lags 1–7 and 39–43.
- With one error allowed: **EXCLUDED** at lags 1–5.
- Other lags have fewer than 10 direct links and stay open.

## Where the plan stands
The construction lane's three slots are used: R98 (Slidefair), R99 (one-alphabet autokey) and R100 (two-alphabet
autokey). All are EXCLUDED, with no lead.

The plan's remaining items:
- a different-model review of R98–R100;
- S3 (free alphabets), which needs a type C solver gated on fresh synthetic controls first. That needs its own work
  order and Tyler's approval;
- the fresh rotor gate, which stays blocked (R97).
