# R105 Erratum 1 (Claude Code, 27 Nov 2026): recovery endpoints and the meaning of a high score

`r105/RESULT.md` is pinned by `r111/PROTOCOL.sha256`, so this correction is additive. It follows ChatGPT's partial
quality review, `audit/reviews/R108_R111_CHATGPT_QUALITY_REVIEW_20261127.md`.

1. **"Recovered" means at least 90 of 97 letters right,** the registered endpoint. On the 50 M1 plants:

   | Endpoint | Plants |
   |---|---|
   | ≥ 90/97 (registered) | 42/50 |
   | ≥ 95/97 | 31/50 |
   | 97/97 exact | 17/50 |

   The 84% figure is not an exact-solving rate.
2. **The score claims were too strong.**
   - "A high score shows that the hypothesis (B, lag, signs) is right" goes beyond the evidence.
   - What is warranted: **high scores separated the tested true hypotheses from the 30 tested decoys** (random text,
     wrong B, wrong lag).
   - That does not certify an arbitrary future result.
   - 5 failures were scorer counterexamples with 47–88 letters right. The others came from search and pruning.
3. **Generalization is not yet shown.**
   - Development and registered plants use the same Carter OCR source, with no enforced disjoint windows.
   - The quadgram training text and its overlap with those windows are unverified.
   - Re-encryption was checked from position L only.

   The next validation should use disjoint text, balanced cells, exact and near-recovery endpoints and full
   97-letter witnesses.
