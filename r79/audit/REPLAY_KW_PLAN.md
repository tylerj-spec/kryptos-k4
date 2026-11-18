# T6 item 2 plan (fixed before any K4 run): independent replay of R79 (L169) and R81a (L170) keyword exclusions

Written 18 Nov 2026, before `r79/audit/replay_kw.py` touches K4 or any shuffle.

**Checker:** `r79/audit/replay_kw.py` uses the standard library only and imports nothing from `r79/` or `r81a/`. It
re-derives all 982 + 2,560 slot rules, the K1–K3 streams and the setting lists from the definitions.

**Tests that pass before this commit** (`r79/audit/tests/test_replay_kw.py`):
1. Every slot rule equals the originals' encryption-side state machine (11,703 rule–ciphertext pairs). That is a
   different path from the vectorised `slot_map` the original checks used.
2. The streams equal R79's. The setting counts equal the pre-registered totals for all 8 families: 13,824; 774,720;
   170,816; 374,400; 41,472; 512,448; 168,000; 1,123,200.
3. Feasibility equals exhaustive keyword search through the originals' `decrypt()` on toy lengths, all 8 families.
4. Plants at keyword length 12 are feasible. One-wrong-PLAINTEXT-letter plants are flagged at that position (24/24).

| Replay | Ciphertexts | Compared with |
|---|---|---|
| All 8 families (R79's four and R81a's four), exact and drop-one | `r81a/k4/TARGET.tsv`: K4 + NULL_000–NULL_009 (R81a's validator set) | `r81a/k4/VALIDATE.json`: settings, exact_feasible, drop_one_feasible, drop_one_by_position |
| R79's four families, exact | `r79/k4/TARGET.tsv`: K4 + NULL_000–NULL_009 (R79's validator set) | `r79/k4/VALIDATE.json`: feasible_by_checks |

Both replays are full: every setting.
- **Also reported:** the minimum checks of any setting, testing the claim "every setting ≥ 12 checks".
- **Pass:** identical counts everywhere, and minimum checks ≥ 12.
- **Stop and report:** any disagreement.
- **Budget:** `T6_BUDGET.json`, 2 h and 4 GB.
- **Not covered:** R79's H11 routes; R81a's G5X (one unknown keyword alphabet). These are separate checks, to be
  replayed later.
