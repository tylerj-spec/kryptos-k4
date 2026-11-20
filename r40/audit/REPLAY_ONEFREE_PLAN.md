# T6 item 3 plan (fixed before any K4 run): independent replay of R40 (L134), R42 (L136); R41 (L135) next

Written 19 Nov 2026, before `r40/audit/onefree.c` touches K4 or any shuffle.

**Checker:** `r40/audit/onefree.c`, written from the pre-registrations, not from the originals' `whole_family.cpp`.
- One free alphabet. R40: the plaintext alphabet is free under 7 fixed cipher alphabets × 2 operations. R42: the cipher
  alphabet is free under 7 fixed plaintext alphabets × 2 operations.
- Keys: chain addition from every primer (R40: base 10 with b 5, 6, 7 and base 26 with b 5; R42: base 10 only), and
  the CARTER and K1–K3 running keys (forward or reversed, AZ or KRY, every offset).
- V = the bijection-violating pairs, from letter and value tallies. With `ONEFREE_SELFCHECK`, every 997th setting is
  re-counted by brute force over all pairs, and any mismatch aborts.

**Tests that pass before this commit** (`r40/audit/tests/test_onefree.py`):
1. A pure-Python reference (V by brute force over pairs, plus a constructive bijection test) agrees with itself.
2. Fresh plants in both modes and all key types, from an independent encryptor, have their true setting at V = 0.
3. Every setting the kernel lists at its minimum is re-computed to the same V by the reference.

A smoke run on R40's PLANT_00 reproduced the archive: 337,634,136 settings, 1 consistent, the true setting, and
338,651 brute-force self-checks.

**Replay** (`replay_onefree.py`): every ciphertext the originals' whole-family step checked.

| Round | Ciphertexts | Comparison |
|---|---|---|
| R40 | K4, NULL_00–03, PLANT_00–05 (in place) | settings, consistent, min V, the complete min-V list |
| R42 | K4, NULL_00–01, PLANT_00–05 | the same |

All archived min-V lists are complete: at most 19 entries, under the cap of 50.
- **Pass:** all 20 jobs equal.
- **Stop and report:** any disagreement.
- **Budget:** `T6_BUDGET.json`, 2 h and 4 GB. A full replay of 3.4 × 10⁸ and 1.7 × 10⁸ settings per ciphertext.

**R41 (L135; 1.09 × 10¹⁰ settings per ciphertext) is not in this run.** It needs the 116 routes and 5,000 double
rotations re-derived independently. It gets its own plan and a **sampled** replay, reported as sampled, in a
following PR.
