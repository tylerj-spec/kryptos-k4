# R69 result (Claude Code, 7 Nov 2026): SNAKE_L's edge is not exceptional once all row directions are allowed (ARTIFACT); what remains is a row-4 effect

**No K4 solution, and none was possible: R69 never decrypts K4 into a candidate and never uses the published
letters.** It is a pre-registered attribution of the SNAKE_L structure found in R64, R65 and R67.

## Plain words
- **The question:** SNAKE_L differs from carved order only in reading carved rows 2 and 4 right-to-left. R69 asked which
  rows carry the effect, and whether it survives a fair comparison once every row-direction reading is allowed.
  - It scored all 16 combinations of K4's four carved rows read forward or backward.
  - It also scored 62 back-and-forth readings, one per possible start column.
  - It used the same German-key stage 1 that found the effect.
- **Pre-registered outcome: ARTIFACT.**
  - K4's best reading is still SNAKE_L (−320.86).
  - When each control may also choose the best of the 16 readings, 7 of the 492 controls (300 shuffles of K4 + 192
    real structured ciphers) do as well or better: p = 0.016, above the 0.01 bar.
  - By the rule fixed in advance, the SNAKE_L lead is retired from future designs.
- **What the attribution shows:**
  - The effect sits in carved row 4 (the last 31 letters, positions 67–97 counted from 1). Reading row 4 right-to-left
    raises K4's average score by +17.6. That is more than any of the 492 controls (p = 0.0020, beyond its own bar of
    0.0025).
  - K4's four best readings all reverse row 4.
  - Row 2, the other row SNAKE_L reverses, adds nothing beyond chance (+5.1, p = 0.50); nor do rows 1 and 3.
  - So SNAKE_L stood out among R61's 10 routes because it was the only one that read row 4 backwards. It is not
    evidence for an alternating-row (boustrophedon) layout.
- **The start-column scan:**
  - The best of the 62 back-and-forth readings is the sculpture's own layout (column 27, i.e. SNAKE_L).
  - It is not exceptional against 100 shuffles (p = 0.099).
  - No other start column comes close: column 3 scores −327.8, column 22 −331.6.

## Steps
| Step | Commit | Result |
|---|---|---|
| Pre-registration (`r69/PREREGISTRATION.md`) | 671257c | — |
| Holdout plants (seed 690001; truth sha256 1f828240… withheld) | fe02c20 | 40 plants |
| Holdout freeze | 9913d85 | — |
| `verify.py` + gate (truth hash matched) | 22c2d5a | **PASSED**: rows 2–4 right in 27/32 (bar 24); B start column 7/8; 7,840 witnesses |
| Target (K4 + 300 shuffles, seed 690070, + 192 R67 controls) | ca21b45 | — |
| K4 freeze (resumed three times after machine restarts; digest-checked reuse) | a7afbf3 | 493 results, 1,972 work files |
| `verify.py` | 4ce550c | **PASSED**: 97,636 raw decompositions re-encrypt |
| `attribute.py k4` | this commit | **ARTIFACT** |

## Pre-registered statistics (`r69/k4/ATTRIBUTION.json`)
| Row (carved, 1-based) | Letters | Main effect E (reversed − forward) | Nulls with \|E\| ≥ K4's (of 492) | p (pooled) | p (shuffles / structured) | Significant (p ≤ 0.0025)? |
|---|---|---|---|---|---|---|
| 1 | 4 | −5.22 | 157 | 0.321 | 0.312 / 0.337 | no |
| 2 | 31 | +5.08 | 245 | 0.499 | 0.525 / 0.461 | no |
| 3 | 31 | −7.67 | 137 | 0.280 | 0.272 / 0.295 | no |
| 4 | 31 | **+17.57** | **0** | **0.0020** | 0.0033 / 0.0052 | **yes** |

- **S_max** (best of the 16 F readings): K4 −320.86 at F_0101 (SNAKE_L). 7/492 nulls are ≥ K4, p_S = 0.0162 > 0.01.
  The outcome is therefore **ARTIFACT**, which the rule applies before the row tests.
- **The 7 nulls at or above K4:**
  - 4 shuffles: SHUF_061, SHUF_008, SHUF_062, SHUF_161;
  - 3 structured controls: R67_CTRL_205, R67_CTRL_135, R67_CTRL_064.
  - The best was −315.3.
- **The row-2 × row-4 interaction:** +2.40, p = 0.56 (descriptive).
- **K4's 16 F totals, best first:**

  ```
  F_0101 −320.9   F_1101 −326.3   F_1001 −330.6   F_0001 −334.8   F_0111 −339.8   F_0010 −344.2
  F_1111 −345.3   F_0011 −346.7   F_0100 −348.7   F_1011 −350.2   F_0110 −351.6   F_1100 −354.7
  F_1110 −357.1   F_0000 −357.3   F_1010 −360.5   F_1000 −360.9
  ```

- **Secondary (descriptive):**
  - B_max is −320.86 at B_c27_q0 (= SNAKE_L), D = 0.
  - p(B_max) vs 100 shuffles = 0.099; p(D) = 1.0.
  - The next start columns are c03 (−327.8), c22 (−331.6) and c07 (−338.5).
- **Post-hoc power:** in the 32 F plants, 53 of 96 true row effects (rows 2–4) exceeded every null's \|E\|. A per-row
  test at this bar therefore detects a real planted German-key row about 55% of the time.

## What this means
- **Retired (pre-registered rule):** SNAKE_L as a privileged reading of K4. Its edge in R64, R65 and R67 came from
  being the only one of R61's 10 routes that reverses row 4. Once all row directions are allowed, its score is
  matched by 7 of 492 controls.
- **Reported, not acted on:** reading row 4 (carved letters 67–97, `VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR`) right-to-left
  fits the English/German two-model scorer better than forward, by more than any control.
  - Under the ARTIFACT rule this does not justify restricting the next search.
  - It is one 31-letter stretch under one scorer, found by asking which rows matter. Any follow-up would need its own
    pre-registration and fresh controls.
- **Not shown:** R69 identifies no cipher, key or plaintext. Nothing here bears on the published letters.
