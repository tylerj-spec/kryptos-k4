# R104 result (Claude Code, 26 Nov 2026): one conditional mode of the two-free-alphabet autokey is solvable; R105 may proceed for it

**Type:** synthetic measurement and prototype study. No K4 input.

## In plain words
**The setting.** The autokey feeds each plaintext letter back into the key, so one wrong entry in an alphabet could
spoil everything after it. R104 measured that, and tested two ways round it, each with one of the two alphabets
supplied.

**Errors stay local in one place only.** If the key letters are numbered in the *plaintext* alphabet (F = A), a few
wrong entries in that alphabet only relabel letters. 93% of letters survive one wrong pair, and 87% survive two.
Every other error spreads along the chain: only 15–46% of letters survive.

**Mode 1: cipher alphabet known, F = A. This works.** The cipher becomes a simple substitution of a sequence we can
compute, once a constant and one offset per chain are found. A cheap statistic (the index of coincidence) picks
those, and a standard annealer then solves the substitution. **19 of 24** fresh synthetic messages were recovered
(≥ 90/97 letters).

**Mode 2: plaintext alphabet known, F = A, lag 1. This does not work yet.** The cipher becomes a substitution of a
"code" sequence, and that reduction is exact. But the code statistics computed from English quadgrams are too weak:
a wrong code map scored above the truth in 17 of 24 cases. **0 of 24** were recovered.

**Consequence.** R105, the conditional solver, may proceed **for mode 1 only**, as R104's pre-registered gate allows.
Mode 2 is closed for this batch until a stronger objective exists.

## Results (`run_v1/RESULTS.json`, frozen in 913bd86)
| Step | Result |
|---|---|
| **E1 landscape** (mean fraction of letters right; prediction **holds**) | F = A: A-swaps ×1 **0.926**, ×2 **0.874**; B-swaps ×1 0.442, ×2 0.260. F = AZ: A ×1 0.458, ×2 0.294; B ×1 0.378, ×2 0.184. F = B: A ×1 0.461, ×2 0.243; B ×1 0.213, ×2 0.146 |
| **E2 reductions** | (a) B known, F = A: 0/100 failures. (b) A known, F = A: 0/100. (b) A known, F = AZ: 0/100 |
| **E3 prototype P1** (B known, F = A, L 1–3) | **19/24 recovered.** Letters per plant: 96, 97, 97, 92, 97, 16, 97, 97, 95, 97, 97, 97, 97, 92, 8, 41, 97, 23, 94, 95, 97, 97, 94, 84. **Gate for R105: met** |
| **E4 prototype P2** (A known, F = A, L 1) | **0/24 recovered.** 17 objective counterexamples, 7 search gaps. **Gate: not met** |

**Run:** COMPLETE, 69 s wall, 69 s CPU, peak 36 MB (cap 1,800 / 1,800 / 2,048), zero retries.
- The pre-registration (2709df3) was pushed alone, before the source (b27e4d1).
- The run was frozen in 913bd86.

## What R105 is (entry conditions met for mode 1)
**The question for R105:** a conditional solver, with the cipher alphabet B supplied and F = A, recovering the
plaintext alphabet A, the constant and the primer.
- It runs on fresh synthetic controls, at lags 1–5 and both σ.
- It uses an improved P1: a fuller offset search for L ≥ 3 and more candidates.
- It is registered with its own bar before any run.

**Why it matters for K4.** "B supplied" becomes practical by enumerating B over a keyword-alphabet tier, which gives a
blind solver for "keyword cipher alphabet × free plaintext alphabet" autokeys. That is the mirror of R44b's
keyword-PA × free-CA solver.

## Review
**Independent review: NONE.** One model (Claude Code) built and ran R104. It is part of audit batch B (ChatGPT).
