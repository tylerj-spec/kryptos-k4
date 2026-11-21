# R75 scientific-value review — downgrade to exploratory (9 Nov 2026)

**Decision: HOLD progression to a costly sealed R75 gate and do NOT try K4 on this rationale alone.** This review is an epistemic correction to the earlier enthusiastic PR description, not a negative R75 result, not a clue-assisted search, and not a constraint on any future owner-authorized experiment.

## 1. What R75 establishes versus what it does not

- The constructed cipher is a **small, implementable family**: two successive Quagmire-style substitutions with AZ/KRY tableaux, known PALIMPSEST/ABSCISSA keywords, independent phases/signs, no transposition. An algebraic enumeration gives 2,880 distinct 40-position substitution-map sequences under these definitions. These are **model properties**, not evidence that K4 uses this construction.
- K1 and K2 historically used the **same KRYPTOS tableau**, not different tableaux. The cross-tableau switch is an **invented modeling assumption**. The existence of an untested finite family does not increase its independent probability of being the actual K4 method.
- The repository's `SMOKE_LOCAL.json` records **60/60 synthetic recoveries and 0/120 controls** under a technical-prose development setup. This review did **not** independently reproduce the exact reported run; no raw per-example candidate log, execution-environment hash, CI job or full error audit accompanies those aggregate numbers. Treat the result as a **reported, unsealed smoke outcome pending independent reproducibility**, **not** a sealed pass and not evidence K4 uses this cipher.
- Even a fully reproduced 60/60 would only show the solver inverts a **known, deliberately narrow** family when one of its 2,880 settings generated the synthetic messages. It does not identify the method from arbitrary unknown-family ciphertexts. No K4 blind candidate has been produced.

## 2. Is there a distinctive ciphertext-only prediction?

R75 is a **fixed per-position bijection with period 40**. It therefore preserves equalities among plaintext letters separated by multiples of 40. At length 97 there are 17 phase columns with 3 occurrences and 23 with 2; exactly

    17*C(3,2) + 23*C(2,2) = 74

within-phase pairs. Under a simplistic independent English plaintext model, expected matches are ~74 * 0.066 = 4.88; under uniform random letters, ~74/26 = 2.85, a gap of only ~1.23 null standard deviations. This rough calculation shows why period-40 repetition alone is **weak method evidence at 97 letters**. It is **not** a calibrated K4 statistic and should not be interpreted as one. L89 reports compatibility with period 40, not exclusivity or a strong likelihood ratio. Also, flat IC and all-26-letter coverage are common across many unrelated ciphers.

R75 currently has **no demonstrated discriminative K4 ciphertext feature**, other than being not mathematically ruled out by its current narrow historical coverage. In particular, do **not** elevate the public-letter-derived 22-pair sum observation into a key-generation or model-choice cue: R53 forbids that.

## 3. Minimum work before Claude should advance or merge R75

**A. Provenance/reproduction:** Re-run `r75/tests/test_reference.py`, `r75/audit.py`, and `r75/smoke.py` in a pinned Python/numpy environment and commit exact code/input hashes, stdout, and raw per-example outputs including both successful and failed attempts. Resolve any discrepancy against `AUDIT_LOCAL.json`/`SMOKE_LOCAL.json` openly; these JSON files are *reported preliminary summaries*, not a cryptographic test attestation.

**B. Independent evidence check before consuming a sealed 120/300 gate:** Name a concrete **K4-independent historical observation** pointing to a change of tableau between stages, **or** a preregistered **ciphertext-only diagnostic** in which R75 distinguishes its own fresh 97-letter controls from a realistic wrong-family matched baseline with calibrated power, selection correction and effect size. No known-plaintext clues, offsets or postfreeze feedback. If neither exists, assign R75 **LOW PRIORITY (coverage close-out only)**, not 'promising K4 method'. An uncorrected retrospective period-40 match or IC similarity is not sufficient.

**C. True method-identification difficulty:** If synthetic further work is justified, test *hidden FAMILY as well as hidden keys* against competing double-tableau constructions not in R75, same-period non-equivalent per-slot substitution models, conventional periodic families, and other matched ciphertext generators. Fix acceptance/abstention on separate development data. If classification specificity fails, do not deploy a K4 candidate-labeling pipeline. A 97-letter known-family decrypter is easier than an unknown-method solver.

**D. Only if A–C warrant a real K4 test:** Full locked preregistration and fresh independent literary texts, exact 97-letter recovery with actual method/key, a hard compute budget, calibrated full-search nulls, immutable remote freeze of all candidates, and separate public-clue validation as required by `r53/BLIND_RULES.md`. Any raw top-25 set not passing confidence must be labeled *low-confidence raw outputs*, never 'prospects'.

## 4. Higher-value project choice

Before adding another guessed construction, prepare a **method-selection/coverage matrix** with columns: independently documented support; exact invertible operator; prior tested equivalences; distinctive ciphertext-only prediction; synthetic unknown-method identifiability; expected K4-signal power; parameter/compute cost; and stop decision. Rank by *new independent evidence or falsifiable discriminating predictions*, **not** by the number of blind decryptions or synthetic known-family recoveries. Reuse R71's negative result to avoid repetitive width-7/21 hypothesis fitting.

If all rows lack an independent positive likelihood signal, stop claiming an improved chance of solving K4. A method inventory or cheap coverage close-out may still be reasonable, but it is **not a solution lead**. The owner seeks independently generated, coherent full-length candidates, not another sequence of impeccable negative tests.

**Status: Review-only caution. No K4 ciphertext, clue letters, or known offsets were used to prepare this note. No K4 experiment or merge authorized.**
