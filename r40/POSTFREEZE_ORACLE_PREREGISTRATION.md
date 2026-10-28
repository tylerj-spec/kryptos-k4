# R40 B — postfreeze intersection of blind IC ranks and the pre-existing exact 24-letter feasibility oracle

This check is **postfreeze by design**. R39 full 100,000-primer K4 score vector was committed before its reveal (commit `00baaa94868103f5450f40f778bc866a0dc0da0d`, see `r39/ic_gate/FROZEN.sha256`). The R40 independent IC null audit was registered before computing its 1,000 shuffled maxima (`r40/PREREGISTRATION.md`).

## Question and method, declared before calculating intersection

For the **identity-route, two-arbitrary-alphabet**, five-decimal-digit chain-addition hypothesis only:
1. Reconstruct all 100,000 five-digit primer conditional-IC scores **without** clues, exactly as the frozen R39 ranker defined them.
2. From a wholly separate, postfreeze checker, apply the already-public 24 known plaintext letters at positions 22–34 and 64–74 to the fixed 97-letter K4 ciphertext to test graph consistency under `c = CA[(PA^-1(p)+k) mod 26]`. Both alphabets are unknown bijections, so this is an **existence** test, never plaintext recovery.
3. Verify the number feasible equals the prior independent result, 39/100000 (`k4kit/tools/key_oracle.py`), then compute rank of each feasible primer in the **already-frozen score order**, counting exact ties by ascending primer.
4. Report all 39 feasible primers, their blind IC ranks, best feasible primer and rank, and whether any is in R39's frozen top 100/1000/5000.
5. If an overlap is found, it is a **hypothesis shortlist only**, not decryption: the 24 letters have been used to filter! Do not retrofit a plaintext, never claim 24/24 as independent validation, and require genuinely blind English recovery and an independently checkable method before any claimed solve.
6. If zero in the top 5000, this is weak evidence against the direct Gromark two-free-alphabet hypothesis **relative to the IC ranker** but cannot exclude it. An unsampled or differently transposed method remains open.
7. Caveat: IC ranking and feasibility are both functions of the same K4 ciphertext; do **not** treat their overlap as statistically independent or attach a naive p-value.

No external verifiers. Commit exact source and tabular results for audit.
