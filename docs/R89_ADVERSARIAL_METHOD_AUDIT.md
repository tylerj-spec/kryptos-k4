# Kryptos K4: independent-mechanism audit of R89 proposals

Date: 2026-11-20. Status: SYNTHETIC DEVELOPMENT AND DESIGN REVIEW ONLY.
Builder and reviewer: GPT-6 performing a builder / breaker / auditor workflow. These are NOT three independent reviewers. Independent-model review: NONE. No new K4 decryptions, no published K4 plaintext in a candidate generator. All numerical results here are from previously exposed R85/R86 control messages or from random synthetic inputs.

## Scope, significance and limitations

The previous taxonomy of 118 entries is a research index, not 118 independent cipher hypotheses. R89 should not search everything. Original text length is 97; fitting a short English-looking message with a free or nearly free one-time key is uninformative. We seek a small, pre-specified, reversible structural family that simultaneously (1) yields a K4-like frequency profile under representative English source texts, (2) can be identified blind among competing families on NEW held-out ciphertexts, and (3) can be searched with the same exhaustive or appropriately calibrated heuristic effort on target ciphertext and nulls.

Prior source overlap matters. R77 H8 proposed letter-dependent stepping in general. R78 gave the in-place mask / state-machine reduction; R79 tested some earlier-ciphertext-driven slot rules, not every possible update function. R68 tested selected carved-path key-advancement and route/composite orders; R72 verified that mod-97 decimations and proposed 98-cell sheet maps are not new conceptual discoveries. R87 excluded one *regularly* stepped, arbitrarily wired rotor with 16 fixed contact-alphabet pairs. R88 excluded constant-step one-free-alphabet progressive Quagmire under fixed other side. Both are narrower than state-dependent rotor or fractionation plus tableau. R87/R88 were later partly re-derived independently in the previous inventory PR, but no generalized family exclusion follows.

## A. M1: ciphertext-driven rotor with constrained residue stepping

Definition: A free 26-permutation W, initial state s0=0, and (d,m,q) in {-1,+1} x {2,3,4,5} x {0,...,m-1} produce 28 structural settings. For each i, c_i = (W[(p_i+s_i) mod26]-s_i) mod26, then s_(i+1)=(s_i+d*[1+((c_i+q) mod m==0)]) mod26. The decrypter knows prior ciphertext, so computes the identical state before looking up W-inverse. This is reversible for every free W. It is distinct from R87's regular s_i=d floor(i/n), but is an explicit SUBFAMILY of R77's broader H8 concept, not a newly invented family of cryptography.

Synthetic results: 3000/3000 97-character reference roundtrips; one ciphertext-symbol alteration propagated beyond that symbol in 1299/3000 random trials (this MUST be included in error controls); 8/8 correct structural (m,q,d) search recognitions, but only 4/8 exact plaintext recoveries at 16 starts x 6000 proposals and 7/8 exact at 80 starts x 16000 proposals (one 92/97). Both use spent, one-genre plaintexts, an old general English ngram model, and no unknown-family contest. Rerun with more starts is *development*, not a sealed-gate repair. Frequency simulation (500 controls): median IC ~0.03898; 16.4% at IC <=0.0361; 46.2% use all 26 symbols. These descriptive statistics are not an independent K4 signal, nor a posterior probability of any specific cipher.

Adversarial findings:
- One early synthetic reference had a Python operator-precedence error in the step expression. The corrected reference uses 1+int(((c+q)%m)==0), independently round-trips with the solver. Original pre-fix data are NOT evidence. This failure illustrates the value of redundant oracles.
- The previous R77 H8 and R79 slot library must be compared by actual transition-table equality, not by names. Any overlapping parameter schedule will be flagged as previously tested; nothing here supersedes an archived exact result.
- The unknown wiring has 26! nominal choices, but at 97 letters only contacted entries and language-score optima constrain it. Solver recovery on known-family movie reviews does not prove unknown-family identifiability.
- The hypothesis' exact event [(c+q) mod m==0] is mechanically possible but entirely speculative; no historical evidence connects it to the Kryptos design.

Verdict: CONDITIONAL PROSPECT for a fresh synthetic unknown-family gate, secondary to M3b. Not a K4 candidate and not a cryptographic exclusion. Larger irregular rules, multiple wheels and alternate alphabets remain outside its scope.

## B. M2: transposition before an in-place tableau

Reference model: q_i=p_{pi(i)}, c_i=E(q_i,k_i), with a fully specified permutation pi and shift stream k_i. Let j=pi(i), q_i=p_j. Then the same composite can be represented as substitution of p_j by k_(pi_inverse(j)) followed by the corresponding inverse route. In a fully unrestricted key stream, stage order is merely a reparameterization. The equivalence does NOT generally hold if both original and permuted key streams must be *short periodic with the same phase*, so key-schedule restrictions can make stage order genuinely different.

Synthetic checks: 2000/2000 reversible, 2000/2000 equivalent when reordering the unrestricted shift stream. Only 1/2000 of the examples also used the identical unpermuted short key; only 6/2000 permitted a permuted key with any period <=12. These were random modular routes, not new K4 data.

Adversarial finding: modular decimations mod97 were already documented in L47/R72 and selected route/key searches in R68/R41; the earlier R89 M2 proposal mislabeled generic modular routes as novel. R72's 26 directed 98-cell candidates lacked authenticated photographic proof; their absence from archived *run artifacts* alone is not evidence that they were never considered. Testing them requires a separate geometry-driven source gate and a genuinely new cipher/key composition.

Verdict: REJECT from next K4 round. Reopen only after an authenticated or independently motivated route is pinned and proven non-equivalent to earlier executed index maps and key advancement semantics. A fake 'new route' is not progress.

## C. M3: keyed 2 by 13 coordinate fractionation alone

Keyed alphabet A is one 26-letter permutation derived from a predeclared list of twenty generic words/alphabets, which defines row r in {0,1} and column h in {0,...,12} for each letter. In each block of length t=min(b,97-offset), with b in {5,7,9,11}, choose u,v in {1,...,b-1}, u!=v. The ciphertext at in-block position j has row r_(j+u mod t) and column h_(j+v mod t), mapped back through A. Decrypt with row from (j-u) mod t and column from (j-v) mod t. Final partial block uses its actual t, and all 97 characters are retained. The limit u!=v is by the nominal block length b; in a short final block some u/v residues can coincide, causing harmless degeneracy. If u==v for a full block the cipher becomes pure block transposition. No source evidences 2x13 on Kryptos; this is a synthetic research hypothesis.

Exhaustive small test space: 20 alphabets x [12+30+56+90] shift-pairs = exactly 3760 settings. 2000/2000 random 97-letter roundtrips, 2000/2000 individual-block conservation of row and column histograms, and one-character ciphertext corruption changed no more than two plaintext letters. In spent movie-review development controls, 40/40 best full 97-letter plaintexts recovered exactly with both parameters hidden, with wrong-family score separation. THESE 40 were two reused groups of 20, not a sealed holdout.

But the invariants retain conspicuous English statistical structure. In 1000 synthetic encryptions the standalone ciphertext index of coincidence NEVER reached the real K4 value ~0.0361; only 2% contained all 26 ciphertext symbols. Median standalone IC ~0.05326-0.05412. A mechanism can be easily solved and still have weak reason to resemble K4.

Historical counter-evidence: the 1943 Army Advanced Military Cryptography manual, para. 36, called a 2x13 letter rectangle impractical in conventional digraphic substitution. The present block-coordinate mix is not that same historic cipher, so this is contextual skepticism, not proof of impossibility. See https://www.nsa.gov/Portals/75/documents/news-features/declassified-documents/friedman-documents/publications/FOLDER_235/41760779079990.pdf (printed pp. 58-59).

Verdict: REJECT as a standalone K4 search family. Keep as a negative/competing synthetic family and an essential reversible inner component of M3b.

## D. M3b: M3 plus a fixed, K1/K2-style letter tableau

First produce M_i = F26_A,b,u,v(P)_i. Then let E be the keyed alphabet KRYPTOSABCDEFGHIJLMNQUVWXZ and U be either PALIMPSEST or ABSCISSA. The final ciphertext is C_i=E[(index_E(M_i)+sign*index_E(U[(i+phase)%len(U)])) mod26], sign in {-1,+1}, phase in 0..len(U)-1. The inverse subtracts the same shift before the 2x13 inverse. The tableau stage separately reproduced the known K1 and K2 opening encryption examples: BETWEENSUB->EMUFPHZLRF and ITWASTOTAL->VFPJUDEEHZ; the F26 stage is entirely our invented variant, NOT authenticated Kryptos process.

Parameter space: 3760 F26 keys x (10+8)*2=36 outer key/phase/sign options = 135360 layered variants. Include the 3760 standalone F26 settings as controls: 139120 total nominal transformations per ciphertext. Search trick: independently undo each of the 36 tableau options from ciphertext and rank by inner unigram IC, retain top 8, then test all 3760 F26 keys per retained option and bare F26. This is only ciphertext-derived selection, no released plaintext/positions. Exactly 9*3760=33840 scored F26 decryptions/ciphertext, plus 36 IC rankings. This shortlist may miss the truth and MUST be measured on fresh holdouts across genres and on every null.

Reference 3000/3000 random length97 roundtrips. Representative English-source simulations: median composite IC ~0.04102; 6.13% IC<=0.0361; 36.5% use all26 letters; 5.03% simultaneously low IC + all26. This is statistically more compatible than standalone F26 but still not independent evidence of mechanism. Development: 8/8 exact and correct outer method with phase fixed at0; another 16/16 exact recovered with phase unknown across 36 options and the same inner key search; known true outer phase ranked top8 for all16. A separate diagnostic found it ranked first 33/40 and in top8 40/40 previously spent development controls. Sixteen negative rotor/shuffle controls had lower scores but were **forcibly classified**; there was no abstention threshold then. An initial misleading field name 'false_F26_confidence' was corrected to 'forced_family_assignments_on_negatives' in the local development pilot; it must not be reported as zero false positives or a confidence rate.

A subsequent adversarial run on heavily but length-preservingly changed Germanic-looking spelling recovered its first 8/8 held-out-looking BUT SPENT developer positives exactly, even with phase hidden. The same longer process exceeded its time limit after 8 M1 + 6 regular rotor negative cases. The run is **INCOMPLETE**: no claim about later negatives or a completed all-family calibration. The 14 completed negatives scored far below those positive cases, but no threshold is established. The observed slower runtime reverses the optimistic initial speed estimate. All files remain available in the companion pilot archive.

Adversarial issues:
- Both inner alphabet and outer key list were selected using general source/known K1/K2 cryptographic context. This is allowed as external evidence independent of public K4 plaintext, but it makes the family highly specific and can fail simply because the actual key is elsewhere.
- The histogram-based phase shortlist is not guaranteed to keep the correct phase on different genres or longer/masked plaintext; a fresh *full unknown-family* sealed gate is mandatory. If true stage is missed, do not relax cutoff post-hoc.
- KRYPTOS-style tableau is established for K1/K2, NOT for K4. F26's specific 2x13 shape is engineered to preserve A-Z, not a historical attribution.
- The same generic English model scores all output texts. We need literary/technical/modern genres and orthographically altered plaintext, and must not mistake English-like snippets on nulls for success. Maximum across both methods requires familywise calibration.
- Reencryption witnesses are required but trivial to manufacture with a fitted key. The key must be independently searched from ciphertext only and must recover the full unknown message with the stated finite method parameters.

Verdict: PRIMARY CANDIDATE **FOR A NEW SYNTHETIC GATE**, not a K4 prospect or K4 run authorization. Further performance engineering if required must happen on already spent data, with all changes committed before an unseen gate.

## E. M4: both alphabets arbitrary with a nonperiodic key

Previous R43/R44b and L138 showed that a known key and one free alphabet can be recovered, while a fully unknown pair of alphabets/unknown key is severely underidentified in 97 characters. An arbitrary 97-position shift stream is an OTP and can fit any chosen plaintext. A dictionary search that merely selects words is susceptible to enormous multiple-testing bias. The earlier R89 design did not define a compact prior over key and alphabets, so neither the computational search space nor the familywise significance test was executable.

Verdict: DEVELOPMENT-ONLY RESEARCH TRACK. Must first find a compact generative state grammar and demonstrate unknown-method+unknown-key recovery on 97 letters. Do not include in next K4 trial.

## Engineering and scientific audit conclusions

1. Candidate generator was not run on K4 in this round; published clue letters/positions never entered source, model, or selection. K4's publicly known IC was used only to compare synthetic frequency distribution *after* method definitions, never to fit a key, phase or word.
2. The full experimental record contains repeated use of exposed R85/R86 source plaintext. Those 40+16 synthetic recoveries are genuine tests of implemented algorithms but **NOT independent statistical validation**. No power estimate can be promoted without a pre-committed fresh holdout.
3. Every fake family must get *the same combined search* as real K4 ciphertext and matched nulls, including phase screens, key grids, random restarts, word model and postprocess. Overall p-values require correction for trying both primary and secondary mechanism families.
4. Resource log and memory use must come from the repository's bounded runner, not extrapolated from one local performance snapshot. Current observed local runtime differs materially between sessions; a low estimate is not a firm budget.
5. The review was done by one model building and critiquing its own pilots; this is NOT an independent-model council. R89 formal preregistration requires separate reviewer signoff, reimplementation and postmortem of each past bug.

Net decision: **GO only to a fresh, preregistered, unknown-family SYNTHETIC gate of M3b and (after power verification) M1**. No-go for M2 and standalone M3, and no K4 attempt from these pilots. See `R89_EXECUTABLE_BOUNDS_V2.md` for actionable limits.
