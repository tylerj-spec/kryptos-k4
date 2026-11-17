# Corrected WPX one-wrong-letter strength on K4 and the 20 R83 shuffles (17 Nov 2026)

**Label: POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY.** Plan fixed and pushed before running
(`WPX_STRENGTH_PLAN.md`, 32dc662). Output: `WPX_STRENGTH.json`. Nothing was decoded and no trial letter, offset or
key was written out.

## In plain words
PR #90 found that my T1 result overstated the strength of WPX's two leftover settings (4 constraints claimed, 1–2
real). I reproduced that, then re-ran the corrected measure the same way on K4 and on 20 shuffled copies.
- K4's best leftover WPX setting has only **2** real constraints. No setting reaches 3.
- Shuffled copies do as well or better 7 times out of 20, and 4 of them reach 3 or 4.

So the walking key stepped by the plaintext, with one wrong published letter, shows nothing beyond chance. It is
weaker than chance.

| Measure | K4 | 20 shuffles |
|---|---|---|
| Strongest witness s, any setting | 2 | per shuffle: −1 (none) ×8, 1 ×5, 2 ×3, 3 ×2, 4 ×2 |
| Settings with s ≥ 3 | 0 | 4 shuffles have some |
| p_family = (1 + shuffles with max s ≥ K4's) / 21 | 0.38 | — |
| **Verdict** (fixed rule) | **NO_WITNESS_S_GE_3** | — |

## Validation
`tests/test_wpx_drop_strength.py` passes:
- the survivors are identical to T1's validated checker;
- s_max / s_min equal a direct enumeration through `r83/models83.py` on 1,152 toy settings;
- planted one-wrong-plaintext-letter messages keep a witness.

The job ran under `audit/run_bounded.py`: COMPLETE, 95 s.

## Scope
- Settings with s ≥ 3 are excluded under one wrong published letter, in R83's sense: the in-place, alphabet and
  published-positions-only assumptions.
- The s ≤ 2 settings (K4 has the two reported by T1) are not decided.
- PFX is unaffected: its check counts do not depend on the letters.

**Independent review: PARTIAL.** ChatGPT found the defect (PR #90). Claude Code reproduced it (1, 1, 2, 2), wrote and
ran this recalibration. No multi-model council.
