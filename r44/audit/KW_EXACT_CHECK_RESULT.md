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
