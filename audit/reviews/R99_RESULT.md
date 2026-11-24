# R99: L188, K1/K2's keyed tableau with a plaintext autokey, EXCLUDED at every decidable lag

Affected ledger IDs: L188
Validation:
- **Order of commits:**
  - pre-registration ad330af, with `PROTOCOL.sha256`;
  - then source and `SOURCE.sha256` at cabb5fc;
  - then the gate (seed 990901) GO, frozen in f8082d0;
  - then the target, frozen in 9b5f717. That freeze was pushed and the remote blobs checked before evaluation.
- **Gate results:**
  - V1 400/400.
  - V2: 0 mismatches for both checker paths against a reference-decryptor brute force (30 inputs × every linked lag
    × 4 signs × 120 alphabets).
  - V3 32/32 three ways.
  - V4 16/16 separately coded ACA Condi.
  - V5 forecast 485 s of the 960 s limit.
- **K4:**
  - EXACT 0 over the 36 EXACT-decided lags;
  - DROP 0 over the 26 DROP-decided lags;
  - weak lags at chance level.
- **Second checker path:** agrees on K4 at every lag.
- **Resources:** all jobs COMPLETE under `audit/run_bounded_agg.py`, zero retries. Guardrail check PASS.
- **CI:** `.github/workflows/r99-autokey.yml` re-checks every manifest, recounts all 201 frozen inputs, re-derives
  the shuffles and the decision, and runs the second path on K4.

Independent review: NONE. One model (Claude Code) registered, built and ran R99. ChatGPT is the named
different-model reviewer.

## Summary
This is shortlist item S2.
- **Cipher:** y_i = s1·x_i + s2·x_{i−L} + c, with plaintext, ciphertext and feedback ranks all in one keyword
  alphabet A. This is K1/K2's tableau with a plaintext autokey; ACA Condi is L = 1, (+, +), c = 1.
- **Alphabets:** A ranges over R76's 77,229 alphabets.
- **Signs:** all four pairs.
- **Constant and primer:** any.

**Why the check is complete.** It follows each residue chain mod L. Consecutive published letters on a chain give
one congruence in c through the ciphertext between them. Some c must satisfy them all, and that condition is both
necessary and sufficient.

**Result:**
- **EXCLUDED** at lags 1–23 and 34–47.
- With one error allowed (one wrong published letter, or one wrong ciphertext letter anywhere on a link):
  **EXCLUDED** at lags 1–23 and 36–45.
- Lags 24–26, 30–33 and 48–52 have chance-level fits.
- Lags 27–29 and 53–96 carry no information.

**Agreement with earlier rows.** It replicates L172 (R83a PFX m = 1, lags 1–10) and extends L157 (R68 PTAK) to the
constant and to the whole tier.
