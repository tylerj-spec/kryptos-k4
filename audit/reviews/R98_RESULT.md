# R98: L187, Slidefair with keyword alphabets, any key, EXCLUDED (EXACT and DROP)

Affected ledger IDs: L187
Validation:
- **Order of commits:**
  - pre-registration b455147, with `PROTOCOL.sha256`;
  - then source, Amendment 1 and `SOURCE.sha256` at ae2de10;
  - then the gate (seed 980901) GO, frozen in 960607c;
  - then the target, frozen in 3afd9f6. That freeze was pushed and the remote blobs checked before evaluation.
- **Gate results:**
  - V1 400/400.
  - V2: 0 per-convention mismatches against a forward-encryptor brute force (30 inputs × 16 conventions × 120²
    alphabets), for both counting paths.
  - V3 32/32 plus 32/32 corrupted; V4 16/16.
  - V5 forecast 604 s of the 960 s limit.
- **K4:** 0 EXACT and 0 DROP. The 200 shuffles are all 0.
- **Second implementation:** the pure-Python checker agrees on K4 and 5 shuffles, with a synthetic positive control.
- **Resources:** all jobs COMPLETE under `audit/run_bounded_agg.py`, zero retries. Guardrail check PASS.
- **CI:** `.github/workflows/r98-slidefair.yml` re-checks every manifest, recounts all 201 frozen inputs,
  re-derives the shuffles and the decision, and runs the second implementation on K4.

Independent review: NONE. One model (Claude Code) registered, built and ran R98. ChatGPT is the named
different-model reviewer.

## Summary
This is the first item (S1) of the construction-discovery shortlist (`audit/reviews/CONSTRUCTION_SHORTLIST_20261124.md`).
- **Cipher:** ACA Slidefair, the two-letter rectangle rule on a sliding Vigenère/Variant or Beaufort chart.
- **Alphabets:** PA and CA are any two of R76's 77,229 keyword alphabets.
- **Key:** any key per pair.
- **Conventions:** all 16 (tableau × role order × output order × pair parity).

**Why every key is covered.** The key cancels from each pair's constraint. A setting fits a pair iff
(F = G ≠ 0) or (F, G) = (1, 25), where F is measured in PA and G in CA. So the whole key space is decided per
(convention, PA, CA).

**Result:**
- No setting of 95,429,095,056 fits K4's 24 published letters, which form 11 pairs per parity.
- None fits with any one pair set aside.
- The family is closed in scope, so the shortlist's stopping rule applies: stop S1.

**Not excluded:**
- free alphabets (S3);
- alphabets outside the tier;
- a different same-column rule at two or more pairs;
- other digraphic rules;
- transposition;
- insertion or deletion;
- two-pair errors.

**Erratum (additive).** The pre-registration's setting count, 95,428,212,656, was an arithmetic slip. The correct
count, 95,429,095,056, is recorded in the result and in the aggregates.

## Next in the lane
S2 is a Condi-type keyed plaintext autokey (R99). Its G0 overlap check against L27, L58 and L169 comes first, as
the shortlist requires.
