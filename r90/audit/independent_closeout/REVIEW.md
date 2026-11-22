# Independent R90 closeout review

Affected ledger IDs: L179

Promotes: L179

Independent review: YES ChatGPT, a different model from the Claude Code builder. This is one ChatGPT review; same-model audit roles are not counted as separate independent models.

Source revision: `bef9e7d7bcbecc1ca870fa46f0dd78d8a0805d77` (merged PR #101; result head `040abbd9775d51c8a48ca27a6598e1c9cf904c74`).

Validation: independently derived forward-coordinate constraints, an independent all-setting/all-input aggregate-only exact checker, exhaustive toy controls, independent saved gate/evaluation arithmetic and forward witnesses, all 80 protocol/freeze hash entries, commit-order review, and the committed R90 synthetic test suite. Both audit jobs completed under `audit/run_bounded_agg.py`.

## Promotion decision

**Promote the narrow R90 `EXACT_SCOPE_EXCL` result to independently verified.** No setting in the preregistered 104,340-setting catalog satisfies the published plaintext constraints, including the necessary screens for one wrong published plaintext letter or one wrong ciphertext substitution. This conclusion follows from full finite enumeration and the coordinate error bound. It does not depend on the language model, the blind ranking heuristic, or the successful synthetic gate.

The independently checked gate arithmetic supports its recorded **GO**, and the saved blind outputs support **STAT_NO_SIGNAL** for the specified quadgram-to-top-256-to-letter-model pipeline. This review does **not** claim to have rebuilt or rerun the original language-model scoring pipeline. Keep that distinction in the ledger.

## Exact scope and independent derivation

The alphabet is keyword first, then the unused letters of A–Z. The 15 keywords are ORCHARD, MYSTERY, TRAVEL, MECHANIC, RIVER, PHILOSOPHY, HORIZON, GARDEN, SECRET, TEMPLE, MARKET, TUNNEL, LIBRARY, MIRROR, CIPHER. All 15 form distinct F26 equivalence classes, and none equals any of R89's 20 classes. Their union with R89 has 35 classes and includes all 20 from the original ChatGPT development kit.

For each alphabet, the block sizes are 5, 7, 9, and 11. The offsets satisfy `1 <= u,v < b` and `u != v`: 188 combinations per alphabet. The outer stage has 36 PALIMPSEST/ABSCISSA key/sign/phase combinations, plus no outer stage. Thus the exact scope is `15 * 188 * 37 = 104,340` fully determined decryptions. Zero offsets, other alphabets, other block sizes, and other outer keys are outside this result.

For each candidate setting and each known plaintext position, the independent checker follows that input letter's row and column to their respective output positions. After reversing the optional pointwise outer substitution, both coordinate requirements must agree. This checks the forward equations at the known positions without constructing or emitting a complete candidate plaintext. The checker imports no R90 cipher, witness, solver, or exact-check implementation.

The last block uses its actual length, including cases where the two offsets coincide modulo that short length. Such cases remain invertible. The outer substitution is pointwise and bijective.

One ciphertext substitution can alter only one row-bearing middle coordinate and one column-bearing middle coordinate. Therefore it changes at most two decoded plaintext positions. A setting compatible with one ciphertext substitution must match at least 22 of the 24 published positions on the unchanged ciphertext. The `>=22` screen is necessary, not sufficient; absence of a survivor is decisive. R90 implements this corrected criterion properly.

| Exact audit | Independent result |
| --- | --- |
| Saved inputs checked | K4 and all 200 shuffles |
| Settings checked per input | 104,340 |
| K4 maximum known-letter matches | 6/24, attained by 11 settings |
| K4 settings at 24, at least 23, at least 22 | 0, 0, 0 |
| Highest shuffle maximum | 9/24 |
| Shuffles reaching K4's maximum | 200/200 |
| Disagreement with recorded per-input exact counts | None |
| Upper bound after any one ciphertext-symbol correction | 8/24 |

The three excluded error models are no error, one wrong published plaintext letter, or one wrong fixed-length ciphertext symbol. Insertions, deletions, changed alignment, and other cipher models are outside the scope. The exact constraints do not depend on the language of the unknown plaintext; “non-English” is a limitation of blind language scoring, not an escape from these exact constraints within the same catalog and known-letter assumptions.

## Synthetic controls and gate arithmetic

The independently written toy oracle exhausts every 2×3-coordinate plaintext up to five symbols for its stated block/offset cases: **121,800 plaintext/parameter combinations across 90 parameter cases**, including 28 short-block cases with coincident offset residues. It encrypts by coordinate gathering and inverts by independently scattering coordinates back to their source positions. Every map is bijective and every inverse agrees.

An additional 60 synthetic plants in the actual 26-letter catalog verify that the independent complete-family constraint enumeration recognizes the planted setting. Separate plaintext and ciphertext mutation checks pass for all 60 plants. These controls contain no K4 plaintext or ciphertext.

The committed R90 suite also passes all ten test groups, including 3,000 round trips, every final-block length for all 188 offset settings, reference/witness agreement, catalog equivalence, optimized solver maps, exact hit counts, ciphertext-error propagation, witness rejection tests, holdout construction, gate bars, and sandbox input rejection.

The independent audit recalculates the saved gate using its actual right-key requirement, full plaintext comparison, confidence cuts, and retention list. The truth hash matches its prior commitment. All IDs and ciphertexts agree across input, truth and output.

| Gate measure | Independently checked result |
| --- | --- |
| Correct key, at least 95/97 letters, confident | 48/48 |
| Exact 97/97 with correct key and confidence | 48/48 |
| True setting retained | 48/48; recorded rank 1 throughout |
| Each block stratum | 12/12 |
| Each genre | 16/16 |
| Masked controls | 12/12 |
| Shared negative controls confident | 0/150 |
| Diagnostic extras | 4/4 |
| Independent forward-witness checks | 1,259 checks across 202 inputs |

The negative counts are nine generators with 13 cases each, 25 English anagrams, and 8 random cases. The gate has 48 distinct positive plaintexts. Zero confident negatives is an observed result for this control distribution, not a claim of zero general false-positive probability.

The source implements the preregistered retention rule: quadgram scores for every setting; a deterministic top 256 with setting-order tie breaks; letter-model scores on those 256; the maximum of those retained settings is “best.” It does not claim an exhaustive letter-model maximum over all 104,340 settings. The saved tags are valid and unique; all saved best/top/sub-family outputs belong to the retained list.

## Blind result and provenance

From the saved outputs, the independent audit reproduces **150/200** shuffles at or above K4's best score and `p = 151/201 = 0.7512437810945274`. The best saved output scores −1.9066235494 per letter and −4.7567605620 on the word score, below the fixed confidence cuts. It matches one published letter; the maximum over saved K4 outputs is two. There are no contenders. The outcome remains **NO_SIGNAL**.

All **1,302** saved K4/shuffle forward-witness checks pass independently. The target contains the unchanged K4 ciphertext and 200 unique frequency-preserving shuffles, reproduced exactly from seed 900400.

All **80** entries across the protocol, gate-freeze, and K4-freeze manifests match the repository bytes. The prerequisite source, artifact, and reveal commits were also cross-checked against GitHub PR #101's commit list. The sequence is:

| Stage | First commit |
| --- | --- |
| Preregistration | `cd411e9b7d1dae53286179b7eeb2b640331f01f4` |
| Sealed input and truth hash | `2d9f43c819d8376d6431fa9601f41524d485bc55` |
| Operational amendment | `903340cd494208ef51cdc3cc49c2230d9e018a84` |
| Gate output freeze | `167afe649148a802cb9986cc9a742990eff1ad91` |
| Truth and gate verdict | `f6eb8795561cad4b403628672b9bef08fdcffc73` |
| K4 and null inputs | `247ee88f269c2b8085d107adc954148b4a34df16` |
| K4 output freeze | `ab3447b2149cc8d59790b2643e373e3b1d2717d0` |
| Post-freeze evaluation | `d6fd7f14a1742be805f178be481a32d8a9b7dbbe` |
| Post-freeze exact check | `7e8ee9ce351bfe61de8fa3af222cfd6af2df7cd9` |

The source uses an allowlist, a fresh sandbox, an isolated network and mount namespace, and a pinned language-model digest. The saved sandbox reports are consistent with that allowlist. The four named holdout books are absent from the checked R59 training-book list. The raw holdout books and original letter-model binary were not supplied to this audit, so byte-level corpus reconstruction and full language-model rescoring are not claimed. Repository commit order cannot by itself prove historical first-read or push wall-clock timing; the original execution attests those steps.

## Resource and retry qualification

The first four-worker gate launch was correctly labeled **INCOMPLETE** and retained: it exceeded the sampled aggregate RSS limit at 4,184.3 MB after 3.531 seconds. Amendment 1 was committed before the successful output freeze, reduced workers to two, and preserved all numerical budgets and cipher/scoring rules. The runner writes its output file only after the job finishes, so the recorded failure did not publish a partial results file. The original preregistration's “No retries” and `max_retries=0` were therefore **not literally satisfied**: this was a disclosed operational relaunch. It must not be described as unamended compliance. Nothing in the saved evidence shows outcome-based tuning, and the finite mathematical exclusion does not depend on this relaunch.

The aggregate wrapper examines all processes in the job's process group, sums resident memory, includes CPU from reaped children, and kills the process group when the sampled budget is exceeded. For this runner, workers inherit the group and do not deliberately escape it. Sampling occurs every 0.25 seconds and can miss shorter memory spikes, as the wrapper states. Summed RSS also counts shared mappings in each process; it is not a measurement of unique physical RAM. These are limitations of the stated measurement, not a defect in the exact result.

The completed gate and K4 runs report approximately 2,568 MB aggregate RSS, below the 4,096 MB budget. The independent audit completed in **6.516 seconds wall / 7.213 seconds CPU / 54.6 MB sampled aggregate RSS**. The committed synthetic test suite completed in **3.506 seconds wall / 4.287 seconds CPU / 43.6 MB**. Both review logs were produced by the aggregate wrapper. No frozen experiment artifact was modified.

## Reproduction and evidence

From the repository root, choose a fresh output directory and run:

```bash
python3 -I audit/run_bounded_agg.py --manifest r90/QA_MANIFEST.json \
  --log /tmp/r90-independent-resource.json -- \
  python3 -I r90/audit/independent_closeout/review_r90.py . /tmp/r90-independent-results
```

The saved evidence is `REVIEW_RESULTS.json`, `REVIEW_RESOURCE_LOG.json`, and `UNIT_RESOURCE_LOG.json` beside this note. `review_r90.py` is the complete independent verifier. Original experiment records remain unchanged.

**Signed: ChatGPT.** Promotion applies to L179's finite exact exclusion and its stated error models. Saved statistical arithmetic and gate results are verified as described; full original blind scoring execution is not independently rerun.
