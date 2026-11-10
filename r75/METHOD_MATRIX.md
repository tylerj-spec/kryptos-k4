# K4 method matrix (Claude Code, 10 Nov 2026)

Built from all 164 ledger rows on `main` (through R74) and ChatGPT's request in PR #67 for a method-selection matrix.
No K4 computation was done for it.

**How to read it:**
- **Evidence** is support that does not come from K4's ciphertext or published letters.
- **Seen in the key?** says whether the family would show up in the key that the published letters imply. The rates
  come from the synthetic calibration in `r75/results/KEYCLASS_CALIBRATION.json`, where the family was hidden from
  the classifier.
- **Solvable blind?** means from the 97 ciphertext letters alone.

| # | Method class | Evidence | Covered so far | Seen in the key? | Solvable blind? | R75 |
|---|---|---|---|---|---|---|
| 1 | One stage, repeating key (as K1/K2) | K1, K2 | **EXCL** periods 1–26 and 30–52 (L03, L04); 27–29 and 53–97 leave no repeat to check | Period 30–52: 60% | Yes | F0X control only |
| 2 | One stage, key from a rule: progressive, linear recurrence, chain addition, autokey | Hand methods of the period; nothing specific to K4 | **EXCL** L13, L14, L17, L49, R68 | Progressive 83%, autokey 99.8%, digits 70% | Yes | Step 1b would flag a miss |
| 3 | One stage, key = a text (running key) | K3 quotes a book | Named texts **EXCL** (L16, L90, L106, R70); unknown English text: no signal (R59, R61) | **No**: 444/500 look like a random key | Partly (R59 detected 16/20) | — |
| 4 | One stage, irregular key: held, interrupted, or few values used unevenly | "Interrupted key" is a documented manual technique; R73 tested word restarts only | **Not tested** before R75 | Held 100%, few values 89% | Regular forms yes; irregular forms no (too many free choices) | **F2, F3** blind, then **F2X, F3X** for all keys |
| 5 | Two stages in place on different tableaux | K2 ends "LAYER TWO" (weak); nothing documents a tableau switch (PR #67 note) | **Not tested**; PR #67 prototype (2,880 settings) | **No**: 452/500 look random | Keyword pairs yes | **F1** blind (6.2M settings), then **F1X** for all keys, periods ≤ 26 |
| 6 | Substitution plus transposition, either order | K3 is a transposition | 1.7 billion settings at chance (L47, L48); R58, R61, R66, R68, R74 negative | No: the key is not aligned with the letters | Listed routes only | — (the route is the unknown) |
| 7 | Two unknown alphabets with an unknown key; one-time pad | Scheidt's "masking" (vague) | Feasible everywhere, readable nowhere (L22, L27, L72); not identifiable (L138) | Looks random | **No** | — |
| 8 | Fractionating or digraphic: Playfair, Bifid, Trifid, Hill | "HILL" on the tableau; Scheidt's matrix codes | **EXCL** L11, L12, L61, L88, L91; R57 | — | — | — |
| 9 | A masking step before encryption: nulls, homophones, re-spelling | Scheidt: English was "masked" | Homophonic + routes: no signal (R66); nulls: no result (L81–L83) | — | No | Open; no testable form yet |

**What the matrix says:**
- **Row 4 is the only class that is untested, cheap to settle, and visible in the key.** If K4's key is held or
  drawn from few values, step 1b names it with 89–100% reliability.
- **Row 5 is untested and cheap, but invisible in the key.** Only the exact check (F1X) can decide it. That is why
  R75 runs the exact check and does not rely on recovery rates.
- **Rows 3, 6, 7 and 9 cannot be settled from the ciphertext and 24 letters by any test we know.** If rows 4 and 5
  come back empty and the key shows no structure, the honest position is that the method is one of these, and the
  next lead has to come from outside information.

**What "identifying the method" can mean here.** Step 1b reports one of three things:
1. **A named key class** (held, few values, autokey, progressive, digits, periodic). That narrows the next round to
   one row.
2. **No visible structure.** That rules out the visible half of the table, rows 2 and 4, and leaves rows 3, 5, 6, 7.
3. **Mixed.** Structure that matches no class; the raw numbers go back for review.
