# T6 item 1: independent replay of R83a's EXACT results (L172), 16 Nov 2026

**Label: POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY REPLAY.** Nothing was decrypted, no key was completed and no
original file was changed. The plan was fixed and committed before any K4 run (`REPLAY_EXACT_PLAN.md`, e97aa0c).

## In plain words
R83a's "all 24 published letters right" exclusions were rechecked by separately written code for all six families.
They all hold, setting by setting:
- the plaintext-stepped walking key (WPX);
- keyword + plaintext autokey (PFX);
- the per-slot progressions (SLX, SLX-A);
- the self-enciphering keyword (SSX);
- the linked key (LX), which has 96 million settings.

The one LX setting R83a left open on K4 is open here too. Random shuffles produce as many open settings.

## Result
| Family | Replay | Ciphertexts | Disagreements | Tallies by checks |
|---|---|---|---|---|
| WPX (12,800) | Full (T1 `exact_drop.py`) | K4 + 20 shuffles | 0 | Equal (`REPLAY_EXACT_WPX_PFX.json`) |
| PFX (79,872) | Full (T1) | K4 + 20 | 0 | Equal |
| SLX, SLX-A (832 each) | Full | K4 + 20 | 0 | Equal (`REPLAY_EXACT_SLOTS.json`) |
| SSX (3,328) | Full | K4 + 20 | 0 | Equal |
| LX (96,112,640) | **Full** | K4 | 0; the one archived open setting reproduced | Equal (`REPLAY_EXACT_LX_K4.json`) |
| LX | **Sampled:** boundary cells in full plus 5% of the rest (18,718,186 settings each) plus every archived feasible setting | NULL_000–NULL_004 | 0 (NULL_002's 3 archived feasible settings reproduced; no sampled setting feasible that the archive omits) | Not comparable (sample) |

**Pass condition: PASS.**

## Validation (`tests/test_replay_exact.py`, all pass)
- **Toy brute force:** exhaustive search over every key on toy sizes, through `r83/models83.py`, on planted,
  one-letter-altered and random ciphertexts:
  - SL: all A, B in 26^m × 26^m;
  - SL-A: all A;
  - SS: all keywords;
  - LK: all keywords, m ≤ 3.
- **Max-parameter plants:** 33 plants feasible under their own setting:
  - SL / SL-A m 26 and 10;
  - SS m 25;
  - LK m 20 with w 48, 2 and 97, d −1, both rotations; LK m 2.
- **Agreement with exact83:** equal to the original engine on 3 random ciphertexts:
  - slot families in full;
  - LX on 1,083,000 settings, cell by cell.
- **WPX / PFX:** see `EXACT_DROP.md` (T1).

## Resources (`audit/run_bounded.py`, `T6_BUDGET.json`, all COMPLETE)
| Job | Wall time | Memory |
|---|---|---|
| Slots | 3 s | — |
| LX K4 full | 629 s | 38 MB |
| LX per shuffle | 137–146 s | 189 MB |

## Not replayed
- DROP and SHIFT for SLX, SLX-A, SSX and LX.
- LX on NULL_005–NULL_019.
- The F1XD drop-one beyond T2's 15–18 block.

**Independent review: NONE.** One model did this work.
