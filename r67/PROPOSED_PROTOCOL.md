# R67 proposal (review only): calibrate the R65 SNAKE_L route gap against real cipher ciphertexts

**State: PROPOSED, NOT PREREGISTERED, NOT RUN ON K4, NOT A SOLUTION.**
This branch is for review. Nothing here changes `main` or the R53 freeze, and no clue-conditioned candidate generation or external checker is authorized. Do not start production until the owner reviews the design, commits an immutable pre-registration and records its SHA-256. Do not change the statistical rule after looking at the control scores.

## What is known and why R67

- R64's German running-key stage-1 score placed SNAKE_L first by **28.4979** points. This was noticed after the original K4 reveal and hence originally exploratory.
- R65 reproduced the fixed gap on 300 additional frequency-preserving K4 shuffles: 0/300 met or exceeded it, descriptive Monte Carlo p = 1/301. A shuffle destroys the local dependencies of almost *any* structured ciphertext, not just the correct one. R65 therefore did **not** establish the SNAKE_L route or the German-key method.
- R65b's best implied German-key-fragment score had a **one-sided shuffle p = 0.040**. That missed its preregistered 0.01 **positive-signal** threshold, but a missed positive-signal threshold is **not a mathematical exclusion of German keys**. R64's pre-1996/literary German controls were also low-power (2/6). Do not call the key hypothesis proved or categorically impossible.
- R66's primary blind homophonic solver was at null (57/100 controls >= K4). Its six columnar orders in Part B were found using *published* letters and must remain labelled **crib-conditioned mathematical feasibility only**; do not use them to choose a blind K4 candidate or algorithm.

**Question:** Is a large 10-route stage-1 gap ordinary for *real*, independently enciphered 97-letter strings that resemble K4's ciphertext statistics? Or is it unusual across those alternative methods, too?

The statistic is selected using K4, and this follow-up cannot retroactively become an independent K4 hypothesis test. Results are a *calibration of a known anomaly* and must be presented as descriptive, not a new proof of route identification.

## Frozen target statistic and comparator

- Target: R65's frozen **G(K4) = 28.4979**, top route **SNAKE_L**. Read the existing `r65/k4/EVALUATION.json`; do not rerank or retune using K4.
- On each synthetic control ciphertext, use the **unchanged** `r65/blind/run.py` (R64 German stage 1, beam 15,000, TOPN 2,000, six conventions, 10 frozen R61 routes, no polish), the same binary and sha256-pinned models as R65. Keep the full unedited stage-1 route scores and witnesses.
- Define **G = best total - second-best total** after the standard ten-route search; ties follow the frozen route order. Record the top route and all ten scores. No plaintext scoring, clue masks, key fits or R66 feasible-order lists are allowed in the blind run.
- Ciphertext-only matching: target IC **0.03608247422680412**, all **26** distinct letters. Accept nuisance controls with |IC - target| <= **0.004** and at least **25** distinct symbols; do not match or screen by plaintext clues or solver score. Predeclared sampler: seed 670001, maximum 40,000 attempts per family. Insufficient matches abort the experiment, with the failure logged, *before seeing control scores*.

## Nuisance controls: 192 genuinely encrypted, not shuffled, ciphertexts

Create **32 independent 97-character ciphertexts in each of six families** from out-of-sample English passages, using random keys and parameters independent of K4. The generator is `r67/sealed/make_controls.py`.

| Control family | Forward encryption | Purpose |
|---|---|---|
| OTP | A-Z Vigenere with 97 independent uniform key letters | Flat, nonrepeating baseline; an arbitrary OTP is **not identifiable** from K4 alone |
| PERIODIC_VIG | A-Z Vigenere, random period 5–18 | Key periodicity and dependencies |
| QUAG_III | Same KRYPTOS keyed alphabet for input/output, period 5–18 | Analog of K1/K2's cipher family |
| PLAINTEXT_AUTOKEY | A-Z plaintext autokey, initial lag 5–24 | Self-keying feedback dependencies |
| QUAG_III_ROUTE | Quagmire III then one of the 10 R61 routes | Layered substitute-then-transpose alternatives |
| HOMOPHONIC_ROUTE | Fixed homophonic table, maximum four homophones per plaintext letter, then an R61 route | Frequency masking with layered transposition |

**Important:** these nuisance models are *not* all cryptographically equivalent. Report each family separately, and report the equal-weighted pooled collection. A low hit rate within this finite set **cannot** exclude other structured ciphers or prove SNAKE_L. Conditional selection on IC/coverage may select atypical tails of a cipher family; print accepted/attempted counts and discuss this selection.

### Positive controls: 24 known German-key plants (not part of the nuisance p)

- Make 24 English-plaintext / German-running-key / transposition ciphertexts matching the R64 hypothesis: one of its six alphabet-operation conventions, then one of the frozen ten routes. **12 use SNAKE_L**, **12 use other R61 routes**.
- Use genuinely held-out, *modern German* text where the R63 German key model has measured power. Pin corpus bytes by SHA-256, document source/edition and disjointness from prior development windows before the production freeze. If disjoint sources cannot be established, label dependence. Old-spelling literary German is explicitly a future *separate* low-power test, not a reason to move the threshold.
- Success is measured only after freeze against sealed **synthetic** truth: top route correct; G >= 28.4979; both true together. Positives check whether G can detect what it purports to detect. They do not validate any K4 plaintext.

## Execution and freeze order

1. Choose and hash at least one eligible English corpus and modern German corpus. The public-domain English source and German key corpus are generic and unrelated to K4 published clue text; *do not seed passages with known K4 letters*. Review and hash the generator, evaluator, unchanged runner, all models, routes, source books and protocol. Commit the final **R67/PREREGISTRATION.md** and hash before producing targets.
2. Run `python3 r67/sealed/make_controls.py ENGLISH_LETTERS GERMAN_LETTERS R67_CONTROL_DIR` offline. It verifies original K4 ciphertext SHA256 **2797de14...**, reads it **only to measure ciphertext IC**, and emits 216 anonymized `CTRL_*` ciphertexts, a private synthetic-truth file and a manifest. Verify 192 nuisance/24 positives, 32 per nuisance family, ciphertext-only matching and all fixed permutations. **Do not mount, send, or commit synthetic truth into the blind-solver environment.**
3. Pass only the `BLIND.tsv` file, the exact model binaries, reviewed `r65/blind/run.py` code, routes and an output directory to the no-network unprivileged R53 isolation. Run `r65/blind/run.py BLIND.tsv OUTDIR ENGLISH_LM KEYDIR SOLVER [PROCS]`. No repository, R65b implied fragments, published letters, known offsets, R66 feasible orders, truth file or evaluator is mounted.
4. Verify all raw ten-route outputs and independently re-encrypt every recovered plaintext/key witness through its convention and route; record verifier hashes. Freeze and **push** raw `RESULTS.jsonl`, `WORK.sha256`, `FROZEN.sha256`, the generator/source/model/route hashes, unchanged control ciphertexts and the complete attempt ledger in a separate review branch. Only afterward may a separate post-freeze evaluator read synthetic-truth labels. If raw witnesses or hashes are incomplete, report INVALID.
5. Run `r67/analyze_controls.py R67_CONTROL_DIR R67_RUN_RESULTS.jsonl R67_REPORT.json` **only after freeze**. Cross-check frozen R65 target without any known K4 letter. Hash and commit the descriptive evaluation. Do not merge without Tyler's review.

## Predeclared evaluation (not a K4 candidate gate)

- Main descriptive quantity: **q_pool = (1 + number of 192 nuisance controls with G >= 28.4979) / 193**. Report same quantity for each family using n=32, full G distributions and unmatched attempt counts. Pooled q is not a formal newly-discovered K4 p-value.
- Report fraction of controls whose **best route is SNAKE_L** and separately the joint event best route SNAKE_L AND G >= K4. This route was selected by inspecting K4; report it only as *post-selection descriptive*.
- Report synthetic positive detection, correct-route identification and joint rate (overall and SNAKE_L stratum). A small `q_pool` without adequate positive sensitivity is *INCONCLUSIVE*; a large `q_pool` means R65's shuffle p is not unique to the hypothesized method.
- Interpret `q_pool >= 0.05` as **not unusual among these selected structured controls**; `q_pool < 0.05` as **still unusual within the tested control families only**, conditional on their coverage and power. Neither outcome is proof of method or decipherment. No new K4 plaintext candidate is generated by this experiment.

## Explicit exclusions / authorization boundaries

- Never feed **published K4 plaintext, offsets, crib masks, R65b implied key fragments, R66's six crib-selected columnar orders**, or other post-reveal fits to any blind candidate generator or solver. R67 itself performs *no K4 candidate generation*.
- Do not activate issue **#35**, which is reserved for K4/K5 paired ciphertext and remains dormant unless authentic full K5 ciphertext is released and separately validated.
- Do not assume K4 and K5 share a key. Do not access or submit to any external checker. Do not merge.
- Review/QA of this proposal and synthetic-only code is permitted now. **Production control generation, blind scoring and publication of a numerical R67 result must await a frozen approved protocol.**