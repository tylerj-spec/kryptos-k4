# R83a T1: exact one-wrong-plaintext-letter check for PFX and WPX (15 Nov 2026)

**Label: POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY AUDIT.** Nothing was decrypted, no key was completed, nothing was
ranked, and the trial plaintext letter is never written out. No original R83 file was changed. Work order:
`audit/NEXT_STEPS.md`, task T1.

## What it means, in plain words
R83a had claimed that the walking key stepped by the plaintext (WPX) is ruled out for K4 even if one of the 24
published letters is wrong. That claim was withdrawn because the old test was unsound. The exact re-check says:

- **WPX with one wrong published letter is not ruled out, but what survives is at chance level.** Exactly 2 of
  12,800 settings survive, and they are one setting written two ways. Random shuffles of K4 produce as many
  survivors, as strong or stronger, 12 times out of 20.
- **PFX (keyword + plaintext autokey) with one wrong letter: 22 settings survive**, fewer than on any shuffle
  (12–39). Chance level. 22 is now a complete count under R83a's semantics. The old 17 was not.
- With all 24 letters taken as right, both families stay excluded (0 survivors), as R83a found.

Nothing here is a lead. It does not point at a key or a plaintext.

## Method (`r83/audit/exact_drop.py`, standard library only, no imports from R83's engine)
- **Semantics, the same as R83a's EXACT step and its brute-force test:** a setting is feasible if some key letters
  (and a start pointer per published run for WPX, a primer for PFX) send every published letter to the ciphertext
  letter at its position. Unpublished plaintext is unconstrained.
  - **The gap between the runs (WPX):** the pointer advance over the 29 unpublished letters is unknown, so the second
    run's pointer offset is free and all m values are tried.
  - This relaxes the real cipher, where decryption fixes the unpublished letters. So an exclusion here is sound,
    but a survivor does not mean a full decryption exists.
- **One wrong letter:** at published position b, the true letter is an unknown x. Each of the 25 other letters is
  substituted and the **whole** check is run again. So the equation at b, PFX's feedback equation at b + L, and
  every WPX pointer step after b in b's run are all recomputed.
- **Statistic and verdict:** R83a's rule is unchanged (`r83/verdict83.py`). The count is settings infeasible as they
  stand but feasible with some x different from the published letter, with checks counted on all 24 letters. LEAD
  means a K4 setting at eff ≥ 3 that no shuffle reaches.

## Validation (`r83/audit/tests/test_exact_drop.py`, all pass)
| Test | Result |
|---|---|
| 1. Exhaustive search over every key on toy sizes (WP m 2–3, PF m 1–3, lags 1–7), every position, every x, using `r83/models83.py`'s per-letter encryptor | Agrees on 29 settings × every position (17 exact-feasible, 12 not; 80 drop-feasible, 97 not) |
| 2. True-model soundness: full decryption of toy ciphertexts over every key and start state | All 162 truly feasible cases are feasible in the checker |
| 3. Planted 97-letter messages at K4's positions: WP m 26 (and 13), PF m 26 with lag 12 and 1, m 13 and 26 with lag 4. One **plaintext** letter wrong at 1-based 22, 34, 64, 74, 28 and 67; ciphertext from the true text | True setting survives in 42/42. 17 of the 42 are infeasible as they stand, so the error mattered |
| 4. The two counterexamples of `r83/audit/plaintext_drop.py --synthetic`, and its extra positions | All survive. Both are infeasible as they stand at the corrupted position |
| 5. The x = published case against R83a's original `exact83.pfx` / `exact83.wpx` on 3 random ciphertexts; every exact drop survivor against the conservative checker | Identical feasible sets. All 2,153,278 exact survivors lie inside the conservative bound |

Calibration on 20 random ciphertexts with random letters (`EXACT_DROP_RANDOM.json`): exact feasible at ≥ 3 checks is
WPX 0 / 20 and PFX 0 on 18 (1 and 4 on the other two). Drop-one: WPX 0–6 (median 0), PFX 9–46.

## K4 and the 20 shuffles (`EXACT_DROP.json`; `r83/k4/TARGET.tsv`, the shuffles R83a used)
Positions are 0-based in the JSON; 1-based in brackets.

| Family | Settings ≥ 3 checks | EXACT K4 | DROP K4 | DROP shuffles | K4 best eff | Shuffles reaching it | Verdict |
|---|---|---|---|---|---|---|---|
| WPX | 12,800 | 0 | 2 | 0–14 (12/20 have any) | 4 | 12/20 (two reach 5) | **CHANCE** |
| PFX | 39,424 | 0 | 22 | 12–39 | 4 | 6/20 | **CHANCE** |

- **WPX survivors:** convention ABS → KRY additive, step alphabet PAL, e = 1, m = 26, d = +1 and d = −1. They are
  freed by 0-based position 25 or 28 (1-based 26 or 29). At m = 26, d = −1 is d = +1 with the key read backwards, so
  this is one setting.
- **PFX at eff 4:**
  - AZ → ABS reverse, β AZ, f −1, L 1, m 24;
  - PAL → KRY reverse, β ABS, f +1, L 3, m 23 (also in R83a's 17);
  - PAL → KRY additive, β AZ, f −1, L 4, m 15 (also in R83a's 17).
  The full list is in the JSON.

## Pass condition (`t1_passcheck.py`, `T1_PASSCHECK.json`): PASS
- The conservative checker was re-run in full and reproduces the 260 WPX settings.
- Both exact survivors are among the 260, and so is each (setting, position) pair.

## Resources
Both jobs ran through `audit/run_bounded.py` (budget `T1_BUDGET.json`: 1,800 s, 2 GB), status COMPLETE:
- K4: 40 s, 32 MB (`T1_K4_RESOURCE_LOG.json`);
- random: 35 s, 31 MB (`T1_RANDOM_RESOURCE_LOG.json`).

## Not covered
- The real-cipher coupling of the runs through decryption of the gap. Here it is relaxed, so a survivor is an upper
  bound.
- Two or more wrong letters.
- Ciphertext errors.
- Everything listed under R83a's own "Not covered".

**Independent review: NONE.** One model wrote and checked this work.
