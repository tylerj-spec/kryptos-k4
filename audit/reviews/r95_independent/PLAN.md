# R95 independent-model verification plan (Claude Code)

Reviewer: Claude Code, a different model from R95's builder (ChatGPT). Tyler, 23 Nov 2026: "Can you verify R95".

**Subject.** Branch `chatgpt/r95-fixed-score-challenge-20261122` at 8f59313:
- registration c02b7a9 (`r95/PREREGISTRATION.md`);
- executed source b347130;
- interruption record `r95/INTERRUPTION_STATUS.json`.

R95's primary ran once in ChatGPT's workspace, and that workspace was then lost. Only one of 48 neighbor shards was
published (`r95/development/neighbors/D_000.jsonl`). The registered verifier never ran. R95 is recorded as
PUBLICATION_AND_REVIEW_INCOMPLETE.

**What this review can and cannot do.**
- It **cannot** publish or verify R95's lost primary outputs.
- It does **not** rerun R95's primary, consume its allowance or alter its branch.
- It **can**:
  1. check R95's chronology and pins;
  2. **rebuild the registered model** from the pinned builder and training file and check it against the registered
     digest;
  3. compute R95's registered question **independently**, with a different model's code written from
     `PREREGISTRATION.md`;
  4. verify the one recovered shard against that computation.

The computation is fully deterministic: fixed inputs, fixed model and a fixed 650-swap neighborhood, with no seeds,
search or choice. Repeating it cannot select a favourable outcome. Its answer is a different-model replication of
R95's endpoint, labelled as such. It is not R95's own primary evidence.

**Order.** Each step is pushed before the next:
1. this plan;
2. the review source and hashes;
3. one bounded job;
4. the result note.

I do not read `r95/score_challenge.py`, `r95/verify_score_challenge.py` or `r95/rebuild_model.py` before my source
is published.

## Steps
**A. Provenance.**
- c02b7a9 is an ancestor of b347130, which is an ancestor of 8f59313.
- The R95 branch's `PROTOCOL.sha256` entries match the branch files.
- The panel files (`r94/inputs/PANEL.tsv` 9b3ed6b4…, `PANEL_TRUTH.json` 27aecaf0…), the baseline model
  (`r91/R59_LOWER4_FROM_K5.bin`, 85b4adf2…) and the builder (`r59/blind/lm_build.cpp`, 87b521d7…) match R95's
  registered digests.

**B. Model reconstruction.**
- `lm_build TRAIN.txt OUT.bin 5`, with the pinned builder compiled here, on the pinned training file (sha256
  871627e5…, 23,373,369 bytes).
- The output must be 49,426,528 bytes with sha256 **e9c0848f…** (R95's `MODEL_SPEC.json`).
- Its orders 1–4 must equal the baseline file's tables byte for byte.
- On any mismatch: INCOMPLETE, and nothing below is interpreted.

**C. Independent computation** (own code, from the registration):
- For each of the 48 panel records:
  - check that the true wirings encipher the true plaintext to the ciphertext, and decrypt it back;
  - enumerate the 650 one-swap neighbors in the registered order (U swaps for x < y, then V swaps);
  - decrypt each one and forward-encrypt it back to the ciphertext (witness);
  - score truth and neighbors under K = 4 (baseline) and K = 5 (candidate).
- Scores: the float32 table values summed in float64, order min(i + 1, K) at position i.
- Comparisons use ε = 1e-9 on the full sum.
- **Primary endpoint** for each K: cases with **any** neighbor below 95/97 that scores above truth.
- **Registered rule:** K = 5 at ≤ 2/48 is GO_FOR_CONDITIONAL_DEVELOPMENT; more is SCORE_NO_GO.
- **Secondary, as registered:**
  - per case and cell: wrong-text neighbors above truth;
  - 95/96-letter neighbors above truth;
  - ties, including same-plaintext aliases;
  - match classes;
  - the best wrong-text and best below-95 witnesses;
  - whether each true plaintext occurs verbatim in the training file.

**D. Recovered-shard check.** Every one of the 650 records in `D_000.jsonl` must equal this computation:
- same swap label and order;
- same text and matches;
- same alias flag;
- both sums and both deltas within 1e-8;
- forward witness true.

**E. Report.**
- The replication's endpoint for both K, with the registered rule applied.
- The shard agreement.
- R95's own chain status: still INCOMPLETE unless ChatGPT recovers and publishes its evidence, or Tyler decides this
  replication closes R95.
- Same-model subtasks are one review.

## Budget (`BUDGET.json`, `audit/run_bounded_agg.py`)
| Job | Limits | Retries |
|---|---|---|
| Model rebuild | 120 s wall, 90 s CPU, 512 MiB | 0 |
| Computation and comparison | 300 s wall, 240 s CPU, 1,024 MiB, one process | 0 |

**Outputs:**
- per-case summaries and witnesses;
- a compact per-neighbor file (label, matches, both deltas, alias flag);
- no K4 data at any stage;
- nothing enters a blind search.

The 49 MB model is not committed; its digest and rebuild command are.

## What this cannot establish (R95's own limits, unchanged)
It is a synthetic-truth-assisted diagnostic of one fixed objective on spent data.
- **A pass** permits only a separately specified conditional-solver work order.
- **A failure** rejects this one objective under this selection rule, not a cipher family.
- **Either way:** no K4 claim.
