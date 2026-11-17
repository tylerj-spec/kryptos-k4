# Plan (fixed before running): corrected WPX one-wrong-letter strength on K4 and the 20 R83 shuffles

Written 17 Nov 2026, before `r83/audit/wpx_drop_strength.py` touches K4 or any shuffle. This is the follow-up that
PR #90 (`r83/audit/WPX_STRENGTH_ERRATUM.md`) calls for.

**Defect being corrected.** T1 labelled each one-error WPX survivor with the check count of the *original* published
letters (R83a's label). For a plaintext-stepped walk, the substituted letter moves later pointer residues, so the
label was stale. PR #90 showed that the two K4 survivors' real witnesses have 1–2 constraints, not 4. I reproduced
that independently: 1, 1, 2, 2.

**Statistic, fixed now.**
- A *witness* is a published position b, a replacement letter x ≠ the published letter, and a second-run pointer
  offset o, such that the setting is feasible.
- Its strength is c = 24 − (distinct pointer residues under the altered letters and o): the number of key equalities
  it actually satisfies.
- Per setting: s = max c over its feasible witnesses; s_min is reported too.
- Only settings infeasible with all 24 letters count.
- Scope: all 12,800 WPX settings, on K4 and NULL_000–NULL_019 of `r83/k4/TARGET.tsv`, with the identical scan.

**Verdict, fixed now.**
| Verdict | Condition |
|---|---|
| NO_WITNESS_S_GE_3 | No K4 setting has s ≥ 3 |
| LEAD | K4's maximum s ≥ 3 and above every shuffle's maximum |
| CHANCE | Otherwise |

- p_family = (1 + shuffles whose maximum s ≥ K4's) / 21.
- A LEAD is a stop-and-report event, never a candidate.

**Validation (passes before this commit):** `r83/audit/tests/test_wpx_drop_strength.py`.
- Survivors are identical to T1's validated checker.
- s_max / s_min equal a direct enumeration through the reference encryptor on 1,152 toy settings.
- Planted one-wrong-plaintext-letter messages keep a witness.

**PFX is not affected.** PFX's check count depends only on which published positions pair up at lag L, never on the
letters. So T1's PFX labels are already correct, and no rerun is needed.
