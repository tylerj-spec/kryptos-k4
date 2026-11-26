# R103: L192, the two-free-alphabet autokey is IDENTIFIABLE at 97 letters (synthetic)

Affected ledger IDs: L192
Validation:
- **Order of commits:** pre-registration b03793f; source 6b01776 (pushed together with the pre-registration;
  disclosed); run v1 frozen in 0bb4817.
- **Gate:** G1 100/100; G2 0 disagreements on 36.
- **Primary (M2):** 0 hits in 3,000 trials.
- **Time guard:** truncated M1 and M3, as registered.
- **Resources:** COMPLETE under `audit/run_bounded_agg.py`, 1,790 s wall against a 1,800 s cap, zero retries.
  Guardrail check PASS.
- **CI:** `.github/workflows/r103-identifiability.yml` re-runs G1, G2 and M2 (the guard set to 0, so the
  exploratory sections are skipped) and compares them with the frozen results.

Independent review: NONE. One model (Claude Code) built and ran R103. It is part of audit batch B (ChatGPT).

## Summary
Unrelated English never passes R102's exact consistency test against a planted 97-letter ciphertext: 0 of 3,000,
over all 12 sign/feedback cells at the true lag. So the family is identifiable at K4's length, and R105 (the
conditional solver) is not cancelled by the batch's stop rule.

Short prefixes are not identifying: at 30 letters, 74 of 214 unrelated passages fit, mostly at long lags.
