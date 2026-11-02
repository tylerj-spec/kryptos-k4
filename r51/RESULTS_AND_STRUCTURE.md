# R51 completed — K3-before-substitution with ciphertext-autokey, no Gromark

**30 October 2026. Exact result `EXCL` for a narrowly preregistered model. NO K4 plaintext found.**

## Raw reproducible test
- [Preregistration](PREREGISTRATION.md) SHA256 `a05b6dbe2c3e7e3932484146cd8b416438b668c1ad4ce92e72355d039ce3b65a`; sealed solver [`cipherfeedback_exact.py`](sealed/cipherfeedback_exact.py). Committed BEFORE K4 computation.
- GitHub Actions [run 41159977489](https://github.com/tylerj-spec/kryptos-k4/actions/runs/41159977489) **SUCCESS**. Full [frozen JSON](R51_EXACT_RESULT.json) and [hashes](R51_RESULT.sha256) committed after execution.
- Tested exact four K3 24×8 **T_then_S** routes, ciphertext-autokey lags **1..24**, key numbering by **AZ or KRYPTOS** and ± operation. The first L shifts were completely free, so anchors inside the seed region were appropriately excluded rather than assigned guessed digits.
- Keyword PA/free CA and free PA/keyword CA, all **4,749** standard R44b keyword alphas plus **12** deduplicated themed keywords. Full 26-letter injectivity/bijection feasibility, first three graph-feasible parameters per route/ciphertext independently checked by all-keyword brute force.
- **20/20 synthetic forward/inverse plants** passed (10 each alphabet orientation, sign, and two numbering bases), including original full plaintext recovery when the true initial seed and alphabets were supplied. These are algebra controls, NOT 20 new blind recoveries.
- **Two** shuffled-letter null ciphertexts (seeds 51100 and 51101) completed. No keyword-compatible null settings, no calibrated p-value.

## Original K4 result

| K3 T_then_S route | Two unrestricted alphabets: feasible lag/basis pairs out of 48 | One of 4,761 keywords + other unrestricted |
|---|---:|---:|
| R24x8/CW/fwd | **2** | **0** |
| R24x8/CW/inv | **8** | **0** |
| R24x8/CCW/fwd | **6** | **0** |
| R24x8/CCW/inv | **21** | **0** |
| **Total** | **37 of 192** | **0** |

**Independent implementation check:** Separate C++ code uses its own modular weighted-graph union and full 26×26 two-alphabet component packing, with independent K3 route generation. Source SHA256 `fe5e8a9bf0f5bcee216ab9fbd4b9357525df5e0cb67096ea7108e58ca203e04f`; full CLI output SHA256 `1391791d771a9054dddfc2541fb4874c3c690625ae877efa63b5b49617cc4f98`. The C++ counts are **exactly 2 / 8 / 6 / 21**, agreeing with Github Actions.

### Additional structural lesson

Every K4 two-free-alphabet compatible setting among these **37** had **ZERO independent graph cycles**, even when **24 of the original anchor letters** were outside the unknown-seed region. The inverse K3 permutation maps the two fixed plaintext runs onto ciphertext characters that form essentially a constraint *forest*: different full alphabet assignments can satisfy all edges, so a raw two-free feasibility result is weak evidence. This cycle count is independent of key signs, dictionary and frequency optimization; the independent C++ graph calculation also agrees.

This is why earlier 24/24 crib-compatible *two arbitrary alphabet* results must not be mistaken for recovered text. Even a complete forward-encryption witness can be one of many arbitrary completions. A convincing candidate requires novel independently recovered plaintext under a specified method, not a graph SAT witness.

## Scientifically valid scope

`EXCL` only the four K3 **T_then_S** routes × *ciphertext feedback* lags1..24 with AZ/KRYPTOS rank map × +/- × one of **4,761** fixed keyword alphabets and one unrestricted bijective alphabet. This does **not** exclude plaintext autokey, any longer lag, other permuted routes, mixed alphabets, unknown extra masking or two entirely arbitrary alphabets. It also does not establish the Berlin World Clock as a key. Zero verifier submissions; `main` untouched.

**Research redirection:** R45–R51 are increasing the *number of ruled-out narrow families*, not yielding new deciphered K4 letters. Stop treating that as solved-mystery progress. Put effort into (i) independently grounded mechanism data beyond the already audited historical clock chart and (ii) a true *unknown-key, unknown-plaintext* solver verified on fresh, genuinely unseen plant messages before K4.
