# R95 independent-model verification (Claude Code): the score check is GO (1/48), on independent evidence

**Answer to R95's registered question: GO_FOR_CONDITIONAL_DEVELOPMENT.**
- R95 asks whether the fixed order-5 letter model (R59 builder, K = 5, sha256 e9c0848f…) passes the first development
  bar.
- That bar is that at most 2 of the 48 spent RX2-O cases have **any** one-swap neighbor below 95/97 letters that
  scores above the true plaintext.
- In this different-model replication **1/48** do. The lower-order baseline gives **32/48**.

**This is not R95's own primary evidence.**
- R95's primary outputs were lost with ChatGPT's workspace (47 of 48 shards). Its registered verifier never ran.
- This review neither reruns nor replaces them. It is a separately published, separately coded computation of the
  same fully determined quantity.
- It agrees exactly with the one primary shard that survived.

Reviewer: Claude Code, a different model from R95's builder (ChatGPT). Tyler: "Can you verify R95".

## Chronology (each pushed and checked on the remote before the next)
| Step | Commit |
|---|---|
| Plan (`PLAN.md`) | a09f16b |
| Source (`verify95.py`, written from `r95/PREREGISTRATION.md` without reading R95's scorer, verifier or rebuild script) | 5d9fae2 |
| Amendment 1 (model reconstruction; see below), before any endpoint computation | 7b27d64 |
| Outputs frozen (`FROZEN.sha256`) | 03ef90f |
| This review | the commit adding this file |

## Model reconstruction (`BUILD.json`, `BUILD_CR.json`, `AMENDMENT_1.md`)
- **Pinned build fails here.** The pinned builder compiled here gives 09a1966f…, not the registered e9c0848f….
- **Cause.** glibc 2.39's `log10f` is not correctly rounded; R95's Debian toolchain ships glibc ≥ 2.41, which is.
- **Fix.** With that one line made correctly rounded, the build reproduces **e9c0848f… exactly**, and its orders 1–4
  equal R95's baseline `r91/R59_LOWER4_FROM_K5.bin` byte for byte.
- **Side finding.** That baseline differs from the canonical R59 model `lm6.v2.bin` by ≤ 1 float32 ulp in about 5% of
  order-4 entries (≤ 4.8e-7 log10 each). R91's "exact lower-order tables" description is therefore true only up to
  `log10f` rounding. This changes no decision.

## Checks (`RESULT.json`): all pass
- **Chronology.** Registration c02b7a9 precedes executed source b347130, which precedes the interruption record
  8f59313. All 22 entries of R95's `PROTOCOL.sha256` match the branch files.
- **Input pins.** Panel, truth, baseline and builder all match R95's registered sha256 digests.
- **Worked example.** The registered three-contact example is reproduced and inverted.
- **Witnesses.** All 48 true keys encipher their plaintexts to the published ciphertexts and decrypt back. All 31,200
  neighbors (325 U swaps then 325 V swaps per case, in the registered order) decrypt and forward-encrypt back to the
  ciphertext.
- **Recovered primary shard** (`r95/development/neighbors/D_000.jsonl`, blob 78221aaf…): **650/650 records equal**
  this computation. That covers label and order, text, matches, alias flag, both sums and both deltas within 1e-8, and
  the witness flag.
- **Verbatim provenance.** No true plaintext occurs verbatim in the training file (0/48).

## Results (ε = 1e-9 on the full float64 sum of float32 table values)
| Measure | Order-5 candidate | Order-4 baseline |
|---|---|---|
| **Primary: cases with a below-95 neighbor above truth** | **1/48** (D_011, cell n1t4: one 94/97 neighbor, +0.413 log10) | **32/48** |
| By cell (n1t3, n1t4, n2t1, n2t2, n3t1, n3t2, n4t0, n4t1) | 0, 1, 0, 0, 0, 0, 0, 0 | 4, 4, 6, 3, 4, 2, 6, 3 |
| Cases with any wrong-text neighbor above truth | 5/48 (four of them at 96/97) | **39/48** (equals R94's published 39/48) |
| Cases with a 95–96-letter neighbor above truth | 4 | 28 |
| Below-95 neighbors above truth, in all | 1 | 73 |
| Ties with truth | 15, all same-plaintext aliases (unused contacts) | — |

The five K = 5 wrong-text winners are D_007 (+2.82, 96/97), D_009 (+0.72, 96), D_011 (+0.41, 94), D_019 (+0.21, 96)
and D_033 (+0.62, 96). The per-case witnesses are in `CASES.json`, and every neighbor's delta is in `NEIGHBORS.tsv`.

## What this means, and does not
**Decision value.**
- Under R95's fixed rule the order-5 objective passes the objective check. Its order-4 predecessor fails it badly,
  which matches R94's diagnosis.
- Per the charter (§6.2–6.3), the next step is a separately specified **conditional-recovery work order**: at most two
  fixed optimizer variants; 48 true-U and 48 true-V conditions; ≥ 44/48 at ≥ 95/97 in each, and ≥ 5/6 per turnover
  cell.
- No K4 run, fresh gate or other search is authorized by this.

**Not established:**
- that the global optimum is the truth;
- that any search reaches it;
- that keys far from the truth score lower;
- anything about masked or misspelled text, false positives or K4.

This is a synthetic-truth-assisted diagnostic on spent, publicly known data. A one-swap neighborhood is a local test
only.

**R95's own record.** R95's evidence chain stays as its branch records it: primary outputs unpublished, verifier not
run. Whether this independent replication closes R95 is Tyler's decision.
- Because the computation is deterministic, any recovered original outputs must equal these. A disagreement would be
  a defect in one of the two code paths.
- Same-model subtasks are one review.

**Signed: Claude Code, 23 November 2026, independent-model verifier of ChatGPT's R95.**
