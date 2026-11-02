# R58 completed: reconstruct the PROCESS, unknown family and key — strong controls; no K4 solve

**Result date:** 1 Nov 2026 UTC. **Status:** research experiment complete, negative on authentic K4. **No K4 key, novel plaintext or cipher construction established.** The experiment deliberately did not fit or use the 24 published plaintext letters/positions during candidate generation.

## Motivation and source-grounded hypothesis

Ed Scheidt's 2005 interview described concealing K4's ordinary English letter statistics and the importance of identifying the technique. The original engraving places the 97 K4 letters on a 4-cell row tail plus three complete 31-cell rows (4/31/31/31); the sculpture has a reversed tableau. Those facts justified testing a limited, reproducible physical **route permutation**, an independent position-dependent keyed-alphabet **tableau proxy**, and both orders of the two operations. The physical layout does **not prove** these particular routes were used.

R58 was designed to address the genuine prior limitation: the R55–R57 solvers knew the cipher **family** on their synthetic controls, even though the keys were unknown. R58 did **not know either the operation family or the key**, and it had to abstain on ciphertext outside its supported models.

Four families:
- **V:** position-dependent keyed-alphabet addition.
- **T:** pure rearrangement over *only the engraved 97 sites*, six fixed geometry-derived routes, no guessed blank/null cells.
- **VT:** tableau/mask then route, reversing route before decryption.
- **TV:** route then tableau/mask, reversing mask before route.

Keys were exactly KRYPTOS, PALIMPSEST, ABSCISSA (pre-existing K1/K2/sulpture evidence), plus 64 predetermined high-priority generic English words, de-duplicated. All settings were explored under exactly the same shared blind scorer: **877 total configurations per ciphertext** (67 keyword choices × 13 positions/orders + 6 route-only options). All candidate ranking used the full 97-character **final** plaintext; gibberish intermediates were retained, not pruned. The only public-letter comparison was in the independent after-freeze evaluator.

## Preregistration, corpus and construction controls

- Protocol and target protocol committed before the respective experiments; the pre-control corpus amendment replaced self-authored prose with two immutable public-domain literary sources and recorded book commit IDs, Git blob SHA-1, and sampling procedure **before any control creation**.
- 120 raw blind ciphertext controls from nonoverlapping fixed-size passages of pinned *Alice's Adventures in Wonderland* and *Pride and Prejudice*, with a **different, sealed generator**. Opaque, interleaved IDs hid classes/keys/messages.
- 20 each of V, T, VT, TV, 20 out-of-family Hill digraphic controls, and 20 shuffled-English nulls.
- Separate no-network, read-only, non-root Docker solver saw **only** two-field ciphertext TSV, compiled/reviewed blind code and existing generic word/quad models, not the corpus, truth, generator, K4 clue files, repository or source notes.
- Predeclared confidence gate: top final plaintext quadgram score >= -525.0 **and** advantage of >=10.0 log10 units over the next distinct full plaintext, with no aliased class. Else **ABSTAIN**.
- Raw 120×8 complete candidate outputs and full parameters were committed to **remote Git before** the sealed evaluator reconstructed and opened plaintexts/families/keys; after that separate evaluation, all 960 forward witnesses were checked independently.
- Controls output SHA-256: `bac0d282256df71aefb71f69ddcae61e0a0526d60c1dc4bdb1e7be476220994a`.

### R58A blind unknown-family and unknown-key controls — PASS

| True generating family | Exact 97-letter recovery AND correct detected family | Exact recovered settings and text | Abstentions |
|---|---:|---:|---:|
| V, keyed tableau proxy | **20/20** | 20/20 | 0 |
| T, physical route | **18/20** | 18/20 | 2 |
| VT, tableau then route | **20/20** | 20/20 | 0 |
| TV, route then tableau | **17/20** | 17/20 | 3 |
| Unsupported Hill controls | 0/20 confident false discoveries | N/A | 20 |
| Unsupported shuffled-English controls | 0/20 confident false discoveries | N/A | 20 |

**75/80** in-family cases recovered correct full plaintext, operation sequence and key/route; **0/40** confidently false detections on declared out-of-family controls. **960/960** complete 97-letter forward-encryption witnesses verified. All predeclared per-family and abstention gates passed; controls are a restricted known-construction synthetic benchmark and **not evidence about the actual K4 method**.

R58A completed green: [GitHub Actions run 41267344107](https://github.com/tylerj-spec/kryptos-k4/actions/runs/41267344107). An unintended secondary control workflow run was triggered by narrowing its workflow paths after the first freeze. Its existing-output write-once protections caused that duplicate to fail; it **is not a fresh control attempt** and contributes no new evidence.

## R58B: authentic unchanged K4 (after synthetic gates passed)

- Original 97-letter ciphertext SHA-256 with newline: `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3` (no edits).
- Same frozen blind solver and **877** operation/key configurations, plus **100** independent frequency-preserving K4 shuffles with RNG seed 580070. K4 known words/letter positions never entered the solver, key search, ranking, or experiment selection.
- Original and null **101×8 full 97-letter plaintexts**, exact keys/route/order, intermediates and code/model/input hashes were REMOTELY Git-frozen **before** a separate evaluator was allowed to access the published K4 known letters.
- K4 raw-output SHA-256: `706c87a7d77b990bca0b8823d349b070e10015eed9c0f5c52f0eb7f70a4aa82c`.
- Full-source independent forward audit: **808/808** raw K4/null candidate witnesses re-encrypt to the exact original submitted ciphertexts. All intermediate values were independently checked.
- Blind classifier declared **ABSTAIN**. Its best final plaintext score was **−677.07906103** with margin **4.618**, both below preregistered acceptance (−525 and margin 10). The highest-scoring raw text (unmodified) was:

```text
VPOBLVNDQDFFGGRBDLITHAVBMEIBBITUEGRUMCRYAIEGALQTTPUEOXLRDFTEDAGKXQLCEHJABANTOOSQUEHLETUKULXJJAOXV
```

- **7/100** shuffled null ciphertexts scored as well as or better than the original K4; descriptive empirical upper-tail rank `(7+1)/(100+1)=8/101≈0.0792`. **0/100** nulls also passed the stringent confidence threshold. The rank is NOT a precise formal p-value identifying a cipher family.
- **Only after remote freeze and independent forward checks**, published-letter comparison found frozen blind rank-1 **1/24**, best among the 8 frozen **1/24**, **0/8** matching all 24. No complete readable English message, and no reproducible novel K4 plaintext.

R58B completed green: [GitHub Actions 41267495107](https://github.com/tylerj-spec/kryptos-k4/actions/runs/41267495107). Negative K4 output is an expected research result, **not a CI failure**.

## What was learned and what remains unknown

1. **A single common solver CAN identify the operation family, order and hidden key on its closed-world 97-letter test population** without a pretrained class label and can abstain appropriately on two deliberately unsupported groups. That is stronger than R55–R57's within-family proof-of-concept recoveries.
2. **A visually grounded, composite cipher's intermediate need not resemble English**. Ranking only after complete inversion avoids the methodological risk of prematurely eliminating the correct process through gibberish intermediates.
3. **This exact simple KRYPTOS-keyed-tableau proxy + six 4/31/31/31 routes did not yield a credible K4 candidate**. The visual arrangement itself, true Sanborn/Scheidt masking technique, more complex transpositions, multi-key/multi-stage algorithms, irregular shifts, and physical artwork-specific steps are still untested. Do not mistake our proxy Quagmire operation for a historically proven K1/K2 equation.
4. Pure substitution and pure transposition do not explain a radical unigram/IC change in ordinary English; K4's flat IC should be investigated with transforms that alter the frequency distribution (e.g. position-varying tableau, running key, or a meaningful masking process). But **flat IC alone identifies nothing**.
5. Controls from two novels and one fixed key library are a **closed-world generalization test**. Their excellent results do not establish performance on arbitrary texts or K4 with unmodeled encryption. We need a new, historically sourced mechanism or physical construction rule, not an undisclosed tuning of the current model based on its K4 postfreeze mismatch.

**Research follow-up:** prioritize a documented, independently source-justified physical/masking mechanism; benchmark it with new hidden-family controls (including truly unseen key material) and abstention calibration **before** any fresh K4 test. No external K4 checker used. No claim of a solution; `main` unchanged by this PR.
