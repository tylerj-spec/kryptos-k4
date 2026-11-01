# Independent methodology audit after Claude's reference library and R55–R57
**Reviewed 1 Nov 2026 — no verified K4 solution.** This note is research evidence and test design, not a candidate plaintext or a cipher chosen using K4's public clue letters.

## 1. What has actually been established

| Round | Reversible model & fixed key search | 20 fresh, hidden plaintext + hidden key, exact top-1 | K4 frozen rank-1 agreement (out of 24, **postfreeze only**) | Best of 12 frozen | Nulls with better English score |
|---|---|---:|---:|---:|---:|
| R55 | 29,952 affine feedback settings, lag 1–8, plaintext or ciphertext feedback | 20/20 | 1/24 | 2/24 | 2/12 |
| R56 | 51,324 Chaocipher-style evolving-wheel initial states with one generic-keyword wheel | 20/20 | 0/24 | 3/24 | 4/12 |
| R57 | 97,344 invertible Hill 2×2 matrices with explicit nonstandard pad-X + truncated final ciphertext output | 20/20 | 0/24 | 2/24 | 6/12 |

**Verification:** R55 [PR #27](https://github.com/tylerj-spec/kryptos-k4/pull/27), R56 [PR #28](https://github.com/tylerj-spec/kryptos-k4/pull/28), and R57 [PR #29](https://github.com/tylerj-spec/kryptos-k4/pull/29), all merged. The raw, full-length, ranked candidate outputs were remotely Git-frozen before the separate public-letter evaluator ran. For every round, **240/240** synthetic-control and **156/156** K4/null independent forward encryptions passed. Original ciphertext `OBKRU...UEKCAR` was used intact. None produced coherent recovered English or a 24/24 letter agreement.

**Statistical scope:** twelve shuffled nulls provide only coarse comparisons; the resulting nominal empirical upper-tail values are 3/13 (R55), 5/13 (R56), 7/13 (R57), **not** proof-grade p-values. All three K4 language scores look ordinary relative to shuffled text. The nulls preserve exact K4 letter counts, but they do not represent every plausible *wrong cipher-family* distribution. Multiple rounds add additional multiple-testing risk.

**Meaning of 20/20:** The same parameter family generates the synthetic ciphertext and is exhaustively searched to recover the hidden key. Thus this demonstrates strong *within-family inverse-recovery* and code correctness; it cannot discriminate the correct **family** of the original K4 cipher, nor predict what happens if the true model is not in the predeclared finite key set. Avoid presenting it as an algorithm-identification success.

## 2. Critical corrections to research claims

1. **Pure transposition:** impossible for K4 *alone*, because confirmed K4 plaintext already contains three E's while K4 ciphertext has only two. An unmodified permutation preserves counts and cannot create letters. This is a genuinely general exclusion of a pure, single transposition layer.
2. **Direct single monoalphabetic substitution:** impossible *in place*, because adjacent ciphertext `QQ` at confirmed positions corresponds to two different plaintext letters. A fixed substitution maps any one symbol to a unique other symbol.
3. **Substitution combined with an unknown transposition is NOT excluded by either argument.** A following permutation changes positions; a preceding fixed substitution relabels letter frequencies. For a generic illustration `ABCA` -> substitution `QRSQ` -> transpose `QQRS`: adjacent `QQ` need not correspond to adjacent equal plaintext. This corrects the prior overbroad §2 wording in Claude's cipher-type summary.
4. The K4 **IC ≈ 0.03608** and all 26 alphabet letters fit several mechanisms; they **do not identify** Vigenere, Hill, Gromark, evolving alphabets, transposition-plus-substitution, or deliberate masking by themselves. Likewise lag-7 is **not significant after correcting for looking at all lags** (R54 familywise p around 0.15).
5. **R57** has an explicit odd-length ciphertext handling rule not established to have been used by the sculptor; its negative result does not eliminate every Hill construction. Earlier Hill exclusions (L11, L61) apply to their own conventions.
6. **R56** uses a legitimate evolving-wheel example, but only one keyed wheel and one standard wheel. Both wheels arbitrary, alternate updates, unknown free alphabets and composite encipherment remain unsolved.
7. **Claude's R44b** passed 20/20 controls **with the true Gromark keystream provided**; it therefore validates *known-key* alphabet recovery, not the actual unknown-key K4 task. **Claude's R52** chose a surviving parameter hypothesis with the 24 public K4 letters first, making its overall pipeline **crib-conditioned** even though a later stage omitted those words. It remains archival and separate from owner-compliant blind K4 candidate generation; PR #12 should not be wholesale merged.
8. The phrase "**EXCL**" must always be followed by its family, model parameter bounds, operation order, and any assumption about plaintext spelling or character alignment. Heuristic gibberish is **negative evidence for an output**, never proof that every key in an open family is impossible.

## 3. Primary sources and new status learned

- **Ed Scheidt**, interviewed [by WIRED on 21 Jan 2005](https://www.wired.com/2005/01/inside-info-on-kryptos-codes/), said K4's process deliberately disguises familiar English statistics and the **masking technique may not be publicly known**. He also said the challenge was to determine the technique before deciphering. This supports studying *mechanisms* rather than blindly assembling long key lists. It does **not** say exactly how the masking was implemented.
- **Jim Sanborn**, [Scientific American, 12 Nov 2025](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/), described the World Clock, Egypt 1986, the Berlin Wall 1989, and conveying a message. When asked about the mathematics, he questioned the assumption of a purely mathematical solution. These are **interpretive source constraints**, not permission to fit public plaintext into search.
- **Paradigm**, [June 12 2026](https://www.paradigm.xyz/writing/kryptos), identified itself as the K4 archive steward and described an automated answer-checking mechanism. Its architecture and privacy properties are company statements rather than independently verified facts. The existing owner instruction forbids submissions without explicit approval. An answer accepted by an automated checker still does not independently demonstrate the encryption *method*.
- **Modern 2026 independent research and Paradigm CTF write-ups** include deliberately layered Quagmire, transposition and Hill examples ([example independent account](https://asynchronous.win/post/solving-pk1-pk7-at-paradigms-ctf/)). These are **useful external exercises for testing solver generalization**. They are NOT proof of Sanborn's 1988–90 method or keys; no words/solutions from those puzzles should become K4 plaintext clues or keys.

## 4. What a stronger R58 should measure

The limiting uncertainty is **which transformation to invert**, not just how to search parameters when the right model is already selected. Do **not** run a fourth unrelated K4 brute-force family until the following independent method-discovery evaluation is established.

**Proposed R58: blinded multi-family inverse benchmark, initial research proposal only (NOT yet preregistered or run).**

1. Define 3–5 *mutually distinguishable and historically defensible* candidate mechanisms and composition orders, for example:
   - Quagmire III + a transposition (and the reverse order);
   - two Quagmire stages with mathematically nonequivalent alphabets or key schedules;
   - a polygraphic or fractionating layer plus an independently justified masking layer;
   - one evolving-alphabet control and *out-of-family* ciphertext not generated by any enumerated model.
   Beware algebraic aliasing: two additions over the same periodic alphabet can collapse into one periodic stage; independent composition does not automatically add complexity.
2. Generate at least **20 never-before-seen 97-character English messages per family**, hide both the family label and the full true key from the solver, and **separate test-generation code/data from the solver environment**. Use a held-out, fresh text source rather than simply recycling the authored R55–R57 sentences. Include different writing styles and genuine mistakes/nulls where predeclared.
3. Solve all families using a **single shared ciphertext-only classification-and-key-recovery runner**, not a solver told which family created each message. Record exact family accuracy, entire 97/97 plaintext recovery, key recovery, failure-to-identify/rejection rate and compute budget. The model should select the family *before* seeing the truth. Good performance on one labelled family does not satisfy the task.
4. Preregister a meaningful go/no-go rule (for example >=16/20 full recovery in **each** in-family group, >=16/20 correct family labels per group, and <=1/20 confidently false recoveries on out-of-family controls). This is a **design proposal**, not a retroactive threshold for R55–R57.
5. Run at least 100 shuffled and wrong-family nulls if tractable, and report familywise false discovery across *all* family/parameter hypotheses. Maintain a real baseline (chance key recovery) and prohibit selecting family/order from a failed K4 known-letter score.
6. If the new method identifier passes, use only original canonical K4 ciphertext and generic language priors in the blind environment; freeze all full output, complete derived keys, code/model/input SHA256 to Git *before* a separate evaluator checks the public 24 letters and independent forward encryption. **Do not tune or re-run the algorithm because of the K4 known-letter outcome.**
7. A candidate is promoted only for independently coherent new 97-letter plaintext, reproducible ciphertext-to-plaintext key derivation, exact forward re-encryption, and 24/24 public-letter agreement after freeze. A checker submission remains forbidden without explicit owner authorization.

**Alternative scientific path if R58 classifier cannot meet its gates:** stop escalating blind brute force. Work from *new independent primary evidence* about the sculpture's physical plaintext/masking construction, handwriting, instrument geometry, inscriptions and date/edition hashes, while ensuring no postfreeze clue scores ever select the mechanism. Request more historical evidence only when a specific unresolved dependency could actually change a model.

## 5. Handoff and review boundary

- `main`: merged R49, R53–R57 and the reviewed R43/R44b known-key archive. No K4 solve.
- Claude's **reference-library PR #26**: corrected here for layered-cipher exclusions and updated through R57.
- Claude's **historical PR #12**: do not merge wholesale; its R52 data are explicitly crib-conditioned.
- GitHub [issue #30](https://github.com/tylerj-spec/kryptos-k4/issues/30) is a prepared request for an *independent Claude Code audit*; it does not mean Claude was actually invoked from this conversation.

This note makes no fresh K4 decryption attempt and contains no new candidate; it records what we know well enough to inform the next genuinely discriminating experiment.
