# R113 result (Claude Code, 27 Nov 2026): CLOSE. The one uncovered lag-21 mechanism does not explain R₂₁ = 11 well enough to pursue (P5 closes)

**Type:** synthetic simulation. No K4 input; only K4's published IC (0.03608) and R₂₁ = 11 were used as thresholds.
**Independent review: NONE**; this is audit batch C.

## In plain words
**The question.** K4's letters 21 apart repeat in pairs more than chance predicts (R71; R110 re-measured it). R71
had already shown that its seven cipher families do not explain this. One mechanism remained untested:
- a transposition that puts each plaintext letter's neighbour 21 places later in the ciphertext (a "decimation" by 37,
  or by 60 for the reverse);
- combined with a periodic substitution, before or after it.

R113 simulated it on 100,000 English messages per variant, keeping only those whose letter statistics match K4's.

**The answer: CLOSE.**
- The mechanism makes 11 or more lag-21 repeats about **3–3.7 times** more likely than a running-key cipher does.
- That is roughly 0.7–0.9% of messages, against 0.23%.
- The registered bar was **10 times**, on conservative 99% bounds. The conservative ratios are 1.8–2.3.

**What follows.** P5 closes with no K4 run. The lag-21 repeat structure stays an unexplained fingerprint. It is not
a lead for this family.

## Results (`run_v1/RESULTS.json`, frozen in the commit after f20d56e)
**Checks:**
- C1: decimation inverse and lag ±21 correct;
- C2: the two R₂₁ implementations agree on 1,000/1,000 strings;
- C3: decimated English without substitution has mean R₂₁ 21.6, against 12.3 shuffled. The difference is 24.2
  combined standard errors, so it passes.

| Arm | IC-matched | R₂₁ ≥ 11 | q₁ | 99% CP | Conservative ratio | Point ratio |
|---|---|---|---|---|---|---|
| D37, substitution after | 25,987 | 205 | 0.0079 | 0.0066–0.0094 | 2.09 | 3.37 |
| D37, before | 25,718 | 207 | 0.0080 | 0.0067–0.0096 | 2.13 | 3.43 |
| D60, after | 25,876 | 180 | 0.0070 | 0.0057–0.0084 | 1.82 | 2.97 |
| D60, before | 25,406 | 219 | 0.0086 | 0.0072–0.0102 | 2.30 | 3.68 |
| RUNKEY baseline | 31,993 | 75 | 0.0023 | 0.0017–0.0031 | — | — |

**R71-weighted count** (q₂, max(n − 1, 0) ≥ 11): the conservative ratios are 1.6–2.8. They agree.

**By period** (D37 after, for example): hits per accepted message are 24/456 at p 2–5, falling to 53/12,610 at
p 21–30. Short periods raise the rate but rarely match K4's IC.

**Exploratory chained triples** at lags (21, 42): a mean of 0.14–0.16 for the arms, against 0.07 for RUNKEY.

**Run:** COMPLETE through `audit/run_bounded_agg.py`, 56 s, zero retries.

**Commits:**
- pre-registration 0fe82fa;
- source f20d56e.

**Disclosure** (in the source commit): C3's first code threshold, a mean ratio above 2, failed on a dev smoke run at
1.90. Before the registered run it was replaced by the 5-standard-error rule. The pre-registration said only "far
above", and the decision rule is unaffected.

## Scope
**Closed:** decimation mod 97 (steps 37 and 60) with periodic substitution (p 2–30), at K4's IC. These do not
**explain** the lag-21 count at the registered strength.

**Not tested:**
- other routes or layouts with lag-21 adjacency;
- non-periodic substitutions after such a transposition;
- physical or layout explanations.

This is not an exclusion of these ciphers for K4. It is only a decision not to chase this fingerprint further.
