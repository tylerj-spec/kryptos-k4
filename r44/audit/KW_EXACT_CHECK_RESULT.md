# Independent replication of PR #13's exact exclusion (Claude Code, 29 Oct 2026)

This is a sealed, after-freeze check that uses the 24 published letters. It is crib-assisted: it can exclude a
family, never confirm a plaintext.

`r44/audit/kw_exact_check.cpp` was written independently of PR #13. It covers:
- all 100,000 five-digit base-10 Gromark primers;
- both operation forms;
- all 4,749 R44 keyword alphabets, built by the same rule as `kwpa_solve.cpp`;
- in place, in both orientations.

Feasibility is exact: an equality-pattern test against the ciphertext (keyword plaintext alphabet) or against the
24 letters (keyword cipher alphabet).

| Input | (a) keyword PA × free CA | (b) keyword CA × free PA |
|---|---|---|
| Control HB_00 (own 24 letters) | 1 feasible = its true setting (33511, REMOTABC…, +) | 0 |
| Control HB_07 (own 24 letters) | 1 feasible = its true setting (29740, RELIGONAB…, +) | 0 |
| **K4 (published 24 letters)** | **0** | **0** |

This agrees with PR #13: in-place decimal-Gromark H-KW is EXCL in both orientations. A K4 run of the R44b solver on
this family, or on R39's IC shortlist, cannot produce the published letters.

## Replication of R47 (ChatGPT PR #15): running keys × keyword alphabet

`r44/audit/rk_exact_check.cpp` covers:
- **Keys:** the Carter vol. I and K1–K3 running keys, forward and reversed, AZ and KRY numbering, every window
  (1,135,348 windows), both signs, in place.
- **Two free alphabets:** checked with R43's audited `EdgeGraph`.
- **Keyword alphabet on either side:** the exact equality-pattern test.

| Input | Free/free feasible | Keyword-feasible |
|---|---|---|
| **K4** | 1,170 window-signs = **585 windows** × 2 signs (with both alphabets free the sign is a relabelling) | **0** |
| Control HB_03 (keyword PA; planted CARTER/rev/KRY/off202893, sign −) | 3,938 | 1 = the planted setting |
| Control HB_11 (keyword CA; planted CARTER/rev/KRY/off241142, sign −) | 1,474 | 1 = the planted setting |

This agrees with R47: 585 free/free windows and 0 with a keyword alphabet. R46 (routes after substitution) was not
replicated here; it needs PR #14's exact route definitions.
