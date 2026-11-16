# T6 item 1 plan (fixed before any K4 run): independent replay of R83a's EXACT step (L172)

Written 16 Nov 2026, before `replay_exact.py` touches K4 or any shuffle. Tests (`r83/audit/tests/test_replay_exact.py`) pass:
- brute force over every key on toy sizes;
- 33 max-parameter plants;
- agreement with exact83 on random ciphertexts (slots in full, LX on 1,083,000 settings).

| Family | Replay | Ciphertexts | Compared with |
|---|---|---|---|
| WPX, PFX | Full (T1's `exact_drop.py`, already committed in `EXACT_DROP.json`) | K4 + NULL_000–NULL_019 | `r83/k4/run/R83A.json` EXACT: tested and feasible by checks, feasible list |
| SLX, SLX-A, SSX | Full | K4 + NULL_000–NULL_019 | The same |
| LX | **Full**, all 96,112,640 settings | K4 | Tallies by checks; feasible list, which is complete since 1 < 300 |
| LX | Boundary cells in full (m 2 or 20, or w 2, 48 or 97: 550 of 3,610 cells) + a random 5% of the other settings (seed 830616) + every archived feasible setting. This is a **sampled replay** | NULL_000–NULL_004 | Feasible list, complete for every shuffle (≤ 16 < 300) |

- **Pass:** zero disagreements of feasibility on any replayed setting, and equal tallies where the replay is full.
- **Stop and report:** any disagreement.
- **Budget:** `T6_BUDGET.json`, 2 h and 4 GB per job.
- **Not replayed:** DROP and SHIFT for SLX, SLX-A, SSX and LX (separate questions); LX on NULL_005–NULL_019.
