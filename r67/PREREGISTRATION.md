# R67 immutable preregistration — structured-cipher controls for the R65 SNAKE_L anomaly

**Protocol state: PRE-REGISTERED FOR REVIEW; no R67 control generation, blind scorer run, K4 candidate generation, K4/K5 experiment or external checker has been performed under this protocol.**
**Owner approval for a production run remains a separate step.** The experiment may start only after this file and `r67/PROTOCOL.sha256` are committed and reviewed. Results are a calibration of a statistic selected after looking at K4, never a new confirmatory discovery.

## Premise and tested question

The R64 German-running-key model's stage-1 ten-route score gives K4 a `SNAKE_L` first-place gap of 28.4979 over the next route. R65 replicated that anomaly against 300 frequency-preserving shuffled K4 strings (0 exceedances, +1 Monte Carlo fraction 1/301). K4 has non-random order, and *many* genuine ciphers can create dependency patterns lost when shuffled. Shuffles do not tell us whether a particular route or method is correct.

R65b is a **high-power statistical rejection**, not a mathematical exclusion, of German running keys on `SNAKE_L` under the six AZ/KRY conventions and ordinary English plaintext. The R65b implied-fragment p=0.040 missed its preregistered 0.01 positive-evidence threshold; the independent 2,000 + 2,000 real German fragment power samples (modern Europarl and 1912 literary German) all scored above K4's implied fragments. R64's 2/6 literary German *blind reconstruction* sensitivity is distinct from this high-power *implied-key check*. R65 main correction (PR #51, main aff9109) is authoritative. No exact rule-out is implied.

R66's six surviving columnar homophonic orders were selected using the published K4 letters. They are **never** candidate-generation inputs and are irrelevant to R67.

R67 asks: **Do other genuine, independently encrypted, length-97 ciphertexts with similar low index of coincidence and alphabet coverage also produce large route-score gaps?** If so, R65's shuffle-only anomaly loses explanatory specificity.

## Fixed primary statistic and no solver changes

- Compare with the **already frozen** R65 K4 stage-1 result `G = 28.4979`, top route `SNAKE_L`.
- For each control `CT`, run the *unchanged* `r65/blind/run.py` / `r64/blind/run.py` / `r63/blind/rk2_solve.cpp` German model: all **10** unmodified `r61/routes.txt` permutations, 6 conventions, stage-1 beam `15000`, TOPN `2000`, LAMBDA `1`, `POLISH_M=0`, `WORDS=20000`. Do not run stage 2 or optimize settings.
- `G = best route total - second-best route total` (tie break by original fixed route index). Preserve all 10 totals and all full 97-letter raw witnesses.
- Source code, registry and model digests are fixed by `r67/REFERENCE_SHA256`, transcribed from R65's frozen `r65/k4/run/FROZEN.sha256`; exactly ten dependencies are required, including binary hash **f171dbe52d7abf405b37844314e9c19ceacc5d374164675f762c94f590435e25** and English/German model hashes. Do not recompile/retrain or substitute different binaries.
- R65 frozen stage-1 source model is modern German. Its score cannot be interpreted as German-key *evidence* after the high-power R65b rejection.

## Pinned corpora, source split and encoding — fix #2

Construct exactly the two normalized `hold_pt.txt` and `de_hold.txt` files with `r67/sealed/build_sources.py`. It accepts only original archive bytes whose SHA-256 matches:

| Source, role | Original file or archive | Pinned SHA-256 |
|---|---|---|
| Jack London, *The Call of the Wild*, English held-out plaintext | GITenberg `215-0.txt` | `7b3e855dbc4e9833b0281a0bc1d527379d85c14f8dfb389ef916022d6e4d888c` |
| A. Conan Doyle, *The Hound of the Baskervilles*, English held-out plaintext | GITenberg `2852-0.txt` | `c8a61868388cafca2c76d1d82ee610d24b2bb09913ba6da936c4aca94eb1d1e4` |
| Europarl German, held-out keys | NLTK `europarl_raw.zip` | `ad553e177baac263840c10980e6f3e76d5d15f7f7a078bd98520b36edb69b27c` |

English: remove Project Gutenberg header/footer between START/END markers, uppercase, retain A–Z only; concatenate the books in the order above. These books were R64's new holdout sources, not the 14 R59 letter-model training books or its NLTK training corpora. German: sort 10 `europarl_raw/german/` archive entries as in `r63/corpus/build_keys.py`, select **entry index 9**, while entries 0–7 trained the model and entry 8 was development. Normalize UTF-8 Europarl using R63 G-DE1: `Ä→AE, Ö→OE, Ü→UE, ß→SS`, then A–Z only. The source tool emits UTF-8-compatible **ASCII letter-only** streams. Never pass Gutenberg Latin-1 `-8.txt` files to `letterstream()`.

The `SOURCE_MANIFEST.json` stores verified original hashes, selected member and normalized-file hashes. The generator checks source filenames, original archive provenance, normalized hashes, and source-builder digest; it refuses substituted development sources. Do not silently replace a failed source. Corpus disjointness is by specified edition/held-out file and training split, not a claim that every sentence is unique.

## Control generation and statistical design — fixed owner decisions

R67 uses the deterministic `r67/sealed/make_controls.py`, seed **670001**. Synthetic ciphertexts have **97 A–Z characters**. Sample plain 97-letter English windows and independently selected random cipher keys; never construct any message around a published K4 phrase. Six nuisance families with 32 retained ciphertexts each (192 total):

1. `OTP`: independent uniform 97-letter A–Z key, used once per plant.
2. `PERIODIC_VIG`: Vigenere key with sampled period 5–18.
3. `QUAG_III`: KRYPTOS-alphabet Quagmire III with period 5–18.
4. `PLAINTEXT_AUTOKEY`: alphabetic plaintext-autokey lag 5–24.
5. `QUAG_III_ROUTE`: Quagmire III followed by one randomly chosen R61 route.
6. `HOMOPHONIC_ROUTE`: position-independent homophonic table with at most four cipher symbols per plaintext letter, followed by one R61 route.

Accept a nuisance ciphertext only if its index of coincidence is within **0.004** of unaltered K4's **0.03608247422680412**, with **at least 25 distinct** ciphertext letters. No exact histogram, published plaintext clue, scoring outcome or K4 key structure may influence acceptance. Up to **40,000 generation attempts per family**; if any family yields fewer than 32, abort and record INCONCLUSIVE without viewing scores. Output accepted/attempt counts, distributions of accepted periodic key lengths, autokey lags, number/max of homophones.

24 additional positive controls use independently sampled **German holdout running-key** 97-letter windows with ordinary English plaintext, six alphabet/convention variations, and a transposition. Exactly **12** use SNAKE_L, while the other 12 use other randomly selected R61 routes. Positive controls are **not IC/coverage-filtered** and are kept separate from the nuisance calibration. Their true route/key/plaintext stays concealed until full freeze. R64's prior Europarl modern-German controls had correct route 6/6 but G >= 28.4979 only 4/6; literary German controls 0/6. Do not automatically label small positive-G fractions as cipher identification.

**Owner choices fixed before scores:** Use only these 216 controls. **No unmatched companion run** (would double compute), but disclose strong IC selection bias; homophonic retained controls were ~4.4% of candidates in the pre-registration development dry run, and sampled periods shift longer. No additional 97-letter carved-order solve (would add compute); only already available 10-route contrasts are evaluated. No expanding families, no score-based retuning, no changing the gap threshold.

## Strict blind isolation and minimal filesystem — fix #1

Preparation may access the unchanged original K4 ciphertext **only to compute the target IC and letter coverage**, verified with its SHA256. This is NOT K4 candidate generation.

Only after this protocol and sidecar are committed, create a fresh `CONTROL_DIR`: `BLIND.tsv` with 216 anonymized control ciphertexts; `SEALED_TRUTH.json` with separate secret synthetic answers; `MANIFEST.json` containing hashes and source provenance. Keep the sealed-truth file outside the blind execution environment. No clue masks, letters, K4 plaintext positions or witness history enter the solver.

Prepare isolated stage **outside the Git checkout** via:

`python3 r67/sealed/stage_blind.py CONTROL_DIR STAGE_DIR ENGLISH_LM MODEL_DIR R63_SOLVER`

This stages only 13 allowlisted files with digest checks:
- `BLIND.tsv`;
- `r65/blind/run.py` and its import `r64/blind/run.py`;
- `r63/blind/rk2_solve.cpp` (source hash in frozen manifest) and executable `solver/rk2_solve`;
- `r61/routes.txt`;
- `r59/blind/LM_SHA256`, `r63/blind/MODELS.sha256`;
- `k4kit/data/word_model_orth.tsv`;
- `models/lm6.v2.bin`, `models/lm6_de.bin`, `models/de_words.tsv`;
- `r65/PREREGISTRATION.md` (the legacy R65 protocol the unchanged runner hashes).

No full repository, `SEALED_TRUTH.json`, any `r6*/sealed/reveal_k4.py`, `r65/sealed/implied_key_check.py`, `r66/sealed/hom_feas.cpp`, K4 clues, R67 evaluator or R66 feasible-order file is mounted. Mount the stage tree **read-only**, a separate initially empty output directory writable, and nothing else from the host; use a **network-disabled, nonroot, read-only-root-filesystem** container. The host `stage_blind.py` only stages files; run the unchanged solver manually from inside this isolated container. Example when Docker is available:

```bash
mkdir -p R67_RUN_OUT
chmod 777 R67_RUN_OUT
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user 65534:65534 --tmpfs /tmp:rw,noexec,nosuid,nodev \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$PWD/R67_STAGED:/safe:ro" -v "$PWD/R67_RUN_OUT:/out:rw" \
  python:3.11-slim python3 -I /safe/r65/blind/run.py /safe/BLIND.tsv \
  /out /safe/models/lm6.v2.bin /safe/models /safe/solver/rk2_solve 4
```

Use actual absolute STAGE/OUTPUT paths outside the repository when running; the shell sample assumes they are under `$PWD` for illustration only. Do not mount the repository or sealed truth as part of the container. Stage and output writable permission configuration must be reviewed on the operator host.

## Freeze, verification and reveal — fix #3

A. Freeze `r67/PREREGISTRATION.md` SHA-256 in immutable `r67/PROTOCOL.sha256` and commit/push **before generating any production controls**. Code, corpus builder and all dependencies are fixed by the preregistration commit and output manifests. Do not modify production code or protocol after this.

B. Stage, generate and blind-score control messages. Runner creates `RESULTS.jsonl`, `WORK.sha256`, `FROZEN.sha256`, and all full raw witness files. The R65 runner labels **its old `r65/PREREGISTRATION.md`** as `protocol` in the frozen manifest; R67's **own** separately pinned protocol SHA is captured in `CONTROL_DIR/MANIFEST.json`, and both must verify.

C. Hash and **push** all unedited solver output, cipher-only inputs, control manifest, model source versions and an attempt ledger into a review branch. Never expose synthetic truth before the push/freeze. Perform `r67/verify_controls.py BLIND.tsv RUN_DIR STAGED_DIR VERIFY.json` before synthetic truth. It compares SHA-256 of **all ten** reference dependency entries including the R63 binary, English model, German model and word tables, runner sources, legacy protocol, routes, complete frozen input/output hashes, and every `WORK.sha256` file. It independently forward-encrypts **every** 97-character plaintext/key witness through its stated convention and route; anything invalid yields `INVALID`. Do not proceed to reveal unless `VERIFY.json` says `PASSED` and its hash is recorded/pushed.

D. ONLY THEN call `r67/analyze_controls.py CONTROL_DIR RUN_DIR/RESULTS.jsonl VERIFY.json REPORT.json`. Its first step verifies the frozen results hash, verification report hash references and R67 protocol digest. Only this post-freeze stage opens `SEALED_TRUTH.json` to learn synthetic family labels, routes and planted keys. Commit/hash the descriptive report; no external checker and no merge.

## Predeclared descriptive measurements

- **Primary**: `q_pool = (1 + # of 192 nuisance ciphertexts with G >= 28.4979) / 193`, plus each family `(1 + ge) / 33`. Values are ***not*** fresh independent K4 p-values; the K4 statistic was selected after inspection.
- **Component decomposition** without extra model solves: report best-route total and second-best total separately, counts of controls ≥ K4 on each, and **SNAKE_L − SNAKE_R** route-score contrast. K4's first/second route totals are ~-320.9 and ~-349.4; SNAKE_R ~-360.5. Also report best=SNAKE_L and the joint best=SNAKE_L + G ≥ K4; the latter is explicitly post-selected.
- **Positive sensitivity**: correct-route count, count G ≥ 28.4979, both jointly, and by 12 SNAKE_L versus 12 other routes. Full distribution/per-family results remain archived, not just threshold outcomes.
- **Selection bias**: attempted/accepted controls by family, accepted period/lag/homophone distributions. Explicitly disclose that IC matching selects atypical tails and that no unmatched sample was run.
- Interpret q_pool ≥ .05 as "not unusual among the specified controls", q_pool < .05 as "unusual within only the specified six families, conditional on the matching and sensitivity". Weak positive sensitivity means INCONCLUSIVE, even with small q_pool.
- No R67 decode can be a K4 candidate; no claim of cipher identification follows from an anomalous score.

## Integrity and authorizations

`r53/BLIND_RULES.md` remains controlling. No known published K4 plaintext letters or offsets in generator, stage, solver or tuning. Do not use formerly clue-conditioned R66 orders or R65b implied key fragments as search inputs. No external checker. No K4/K5 issue #35 activation unless an independently verified complete authentic encrypted K5 ciphertext is released. Do not assume K4/K5 use the same key. No merging PR #50 or any R67 output without Tyler's explicit review.
