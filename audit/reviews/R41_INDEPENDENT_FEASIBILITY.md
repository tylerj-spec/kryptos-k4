# R41: complete independent feasibility replay

Affected ledger IDs: L135
Promotes: L135
Validation: Independently derived equality-index proof; exhaustive small-alphabet oracle; separately generated routes and keystreams; compiled-versus-scalar synthetic checks; complete feasible-setting counts for both parts of all nine archived inputs; independent forward encryption and true-setting checks for all six plants. All 18 archived part counts agree.
Independent review: YES ChatGPT, reviewing the original Claude Code implementation. Same-model ChatGPT subtasks are one review, not several independent models.

## Conclusion

The exact zero-feasibility exclusion in L135 is independently verified within its declared scope. **K4 has zero feasible settings in both parts**, covering **10,912,725,152 labeled settings** with any plaintext alphabet. Both archived nulls also have zero. All six plants retain their true configurations, and their complete feasible-setting counts match the original.

The audit covers all nine inputs, a Cartesian domain of **98,214,526,368 labeled settings**. An exact algebraic index avoids visiting every incompatible pair individually. This is complete feasibility, not a sample. The original full violation histogram and minimum positive violation statistic were not recalculated or promoted.

| Input | Part A feasible | Part B feasible |
|---|---:|---:|
| K4 | 0 | 0 |
| NULL_00 | 0 | 0 |
| NULL_01 | 0 | 0 |
| PLANT_00 | 1 | 0 |
| PLANT_01 | 1 | 0 |
| PLANT_02 | 1 | 0 |
| PLANT_03 | 2 | 2 |
| PLANT_04 | 0 | 1 |
| PLANT_05 | 0 | 1 |

Part A contains 3,630,205,152 settings; Part B contains 7,282,520,000. Evidence: `r41/audit/backlog_closeout/REPLAY.json`.

## Why the accelerated check is complete

For a fixed route, cipher alphabet and key, write `x_i = CA^-1(C[q_i])`, where `q` is the inverse route. An arbitrary plaintext alphabet exists exactly when the known plaintext letters and numeric values `y_i = x_i - k_i` (VIG/BEAU class) or `y_i = x_i + k_i` (VARB class) form a partial bijection. Equal letters must have equal values; different letters must have different values. A consistent partial bijection always extends to a complete 26-symbol permutation.

For each repeated plaintext letter, select its first observed occurrence as representative `a`. In the minus case, equality requires `k_i-k_a = x_i-x_a` modulo 26; in the plus case it requires `k_i-k_a = x_a-x_i`. The new implementation indexes **every declared fixed keystream** by this difference vector and queries it for every route, cipher alphabet and operation. Every key returned by the index is then checked against **all** equal-letter and different-letter constraints.

No feasible setting can be lost: its required difference vector is identical and therefore enters the same index bucket. Hash collisions can only add keys to the bucket, and the full relational check rejects any incompatible ones. No arbitrary plaintext alphabet is completed, no K4 plaintext is decoded, and no new candidate is emitted.

The VIG/BEAU collapse is valid for existence of an arbitrary plaintext alphabet: negating all its numeric positions is another allowed alphabet. Both signs represented in the original two-operation scope are retained.

## Scope and checks

The audit independently reconstructed all 116 Part A routes and all 5,000 Part B routes. It preserves route multiplicity. Part A includes every C10b5/C10b6 primer and every CARTER/K1K3 window in both directions and both numberings. Part B includes C10b5 and K1K3. All seven fixed cipher alphabets and both operation classes are included.

The independent kernel and Python reference agree on synthetic setting grids; 78,732 exhaustive small-alphabet checks compare relational feasibility with enumeration of every possible free alphabet. Boundary controls include the first and last 5/6-digit primers and first/last running-key windows. Every archived plant is also re-encrypted independently and its true configuration verified under the published observation mask.

The result is conditional on the unchanged ciphertext and the published positions and letters being correct. It excludes only the stated routes, cipher alphabets and fixed keystream domains with substitution before transposition and one free plaintext alphabet. It is separate from the historical blind gate and makes no additional language-model or error-tolerance claim.

## Provenance and limits

- Plan, independent kernel, helper, budgets and synthetic outcome committed and pushed before the target: `dea5bb84ec983b3d7fc978e11efeebe7f0fd72df`.
- Final driver committed and pushed before the target: `b23e1bcc12119707fb699d81ae6d71c63ce0c376`.
- The driver verifies the published source bytes, key-source hashes and canonical ciphertext hash, and rebuilds the pinned kernel before execution.
- `audit/run_bounded_agg.py`: **COMPLETE**, 15.288 seconds wall, 8.784 seconds aggregate CPU, 146.0 MB sampled aggregate peak RSS, against limits of 2,400 seconds wall, 1,800 CPU seconds and 2,048 MB.
- No target retry, parameter change, count disagreement or K4 survivor occurred.
- Full violation histograms and positive minimum-V values remain outside this replay. Their absence does not limit the independently proved zero-feasibility exclusion.

Result SHA-256: `e421c421f69fd7694dd0cedaf9ae549eec411f0589752daf7843daa07620c39a`.
