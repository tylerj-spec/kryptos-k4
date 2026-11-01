# Claude Code review request — R43 modular word-constraint solver

**Owner action:** Open draft [PR #11](https://github.com/tylerj-spec/kryptos-k4/pull/11) on a new review branch and review against the current `main`. Do NOT merge the experimental solver, call external K4 verifier, or read any unreleased K4 plaintext.

## Objective

Find a **genuine blind-recovery algorithm** for 97-letter English ciphertext encrypted under **two independently randomized alphabet permutations** and a supplied true 97-digit base-10 Gromark stream. A method that only returns a reversible but incorrect plaintext is NOT successful.

This is the prerequisite to wider key searches; the current R43 beam fails its planted recovery gate and has **never been run on the original K4 ciphertext**.

## Exact review inputs

1. `r43/PREREGISTRATION.md`: research protocol and explicitly separate fresh holdout gate.
2. `r43/blind/word_constraint_beam.cpp`: 52-vertex modular weighted disjoint sets, shift consistency, exact component-side injectivity, complete 26-by-26 alphabet reconstruction, English word-priority beam, optional cycle bonus, duplicate plain-prefix dominance and global shift feasibility.
3. `r43/blind/test_graph.cpp`: ten independent forward/randomized 97-letter graph positive controls, already pass.
4. `r43/sealed/make_d0.py`, `evaluate.py`, `coverage.py`, `trace_report.py`: 20 fresh D0 development controls, withheld from blind code, independent forward verifier and post-run diagnostic.
5. `r43/D0_FINDINGS.md`: immutable facts and GitHub Actions run links for four development CI comparisons. In final experiment, true plaintext vanished from blind beam at **character 10 (D0_00; rank 277)** and **character 2 (D0_01; rank 18)**. Exact recovery remains **0/2**, despite >300 million candidate placements in the larger variants. One wrong full 97-letter witness was **91/97 letters incorrect** but re-encrypted exactly.

## Independent audit requests

- Verify orientation/sign of `CA_index(cipher)-PA_index(plain)=k mod26` and every graph union, cycle check, collision mask, and completed alphabet mapping **against a separately written encryptor**.
- Inspect `word_constraint_beam.cpp` for soundness, memory safety, false-negative pruning, and search state dominance; test cases that exercise global component packing where a locally consistent assignment **cannot** complete to two 26-letter permutations.
- Explain with trace and lexical coverage **why** the true prefix is lost by letter 2/10. Specifically audit whether the true next word was in the capped dictionary and whether its hypothesized graph would be feasible if evaluated without pruning.
- Develop a substantially different word-aware search architecture, ideally **nonsequential word placement / word-domain CSP with modular constraint propagation and lookahead** or another approach that actually solves unseen controls. Do not simply widen beams or use K4 crib-fitting.
- Keep experiments reproducible and the D0 development results honest, including failures; rerun `bash strictblind/tests/run_all.sh` and historical `bash verify_all.sh`.

## Required success gates

1. On D0 development examples: demonstrate full 97-letter blind recovery with the true keystream supplied, with every returned two-alphabet candidate re-encrypting exactly. Tune only here and document every change.
2. **Before any K4 run:** preregister new tests, freeze source/parameters, and demonstrate **>=16/20 exactly recovered original 97-letter messages on an entirely NEW, never-seen 20-message holdout** generated independently, plus zero invalid forward-encryption witnesses. *Do not count a close word score, feasible graph, forced published word, or 24/24 crib fit as a success.*
3. Only if the fresh holdout passes, create a separately preregistered **K4 original-ciphertext-only** search; freeze/commit the entire blind output before consulting published EASTNORTHEAST or BERLINCLOCK. Verify any candidate independently with its disclosed algorithm, complete raw 97 characters and exact re-encryption. All raw evidence should go to GitHub review branch; no external checker submission.

## Decision requested

Please post a focused review of PR #11 stating whether the solver architecture is salvageable or should be replaced. If a new architecture passes the D0 development bar, implement it as a separate PR with a truly unseen holdout. If it fails, record a negative result and recommend the next bounded hypothesis. Do not merge into `main` on development metrics alone.
