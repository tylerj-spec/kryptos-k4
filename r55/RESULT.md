# R55 result — completed strict-blind unknown-key affine-feedback K4 test

**Status: NO K4 SOLUTION. Negative result for the specifically enumerated, fixed low-parameter affine-feedback family.**

All source, scope, scorer, synthetic control passages and parameters were committed under `r55/PREREGISTRATION.md` before running K4. GitHub Actions [completed successfully](https://github.com/tylerj-spec/kryptos-k4/actions/runs/41261669415). The output ordering is immutable and public known K4 letters were read *only* by `r55/after_reveal/check_clues.py` after the separate raw-output freeze commit.

## Exact test scope

Cipher relation: `C[i]=(a*P[i] + b + d*i + sign*(i>=lag ? source[i-lag] : 0)) mod 26`, with `source` previous plaintext or previous ciphertext. Both are reversible because `a` is invertible mod 26. Grid = **29,952** fixed configurations; original **97-letter** K4 ciphertext, unchanged; generic 97-letter full-sequence quadgram score; top **12** independently generated full plaintexts frozen **before** clues; 12 frequency-preserving shuffled-ciphertext nulls.

## First: fresh synthetic unknown-key control results

- **20/20** synthetic 97-character natural-language plaintext messages recovered exactly as the highest-scoring candidate when both original plaintext and encryption key were unavailable to the solver.
- **20/20** true parameter sets also recovered exactly.
- **240/240** independent forward-encryption witnesses validated across the top 12 outputs for all 20 controls.
- Remote-frozen control output hash: `dc48f8d8a9dea73925f1bc3874b2ca229fd0ee525dcc54882691785b5614988b`.
- This proves reliable recovery *for the deliberately constructed same-family synthetic controls*, not K4.

## Then: authentic K4 search, unchanged blind algorithm

- **13** raw ciphertext inputs (original + 12 shuffled nulls) × **29,952** settings each.
- **156/156** independently verified full forward-encryption witnesses (12 full candidates each).
- Remote-frozen target output SHA-256: `09e1e33cb95f4af56b50b68e663efc596b89e4e5f771f0eefa6c936b59defc21`.
- Best blind language score for K4: **−640.80454636**. **2/12** shuffled null ciphertexts scored even better, giving a descriptive empirical upper-tail `(2+1)/(12+1)=0.230769`. Twelve nulls are insufficient for a precise p-value; nevertheless there is no exceptional language signal.
- After the separate frozen-output evaluation: top-ranked full plaintext matches **1/24** of the published characters; **the best of all 12 only matches 2/24**; **zero** match all 24. There is no readable English K4 message among the 12.

Top-ranked **raw** 97-letter plaintext (not corrected, not fitted):

```text
OZHBHAHHCDBTSREFRDEMJBKMSHETEIRKMWEPZZLABFAWYOLUNYRMRNTJHAYINGEOHDWOSTHICFEMLDLYKMHTHOKIBBCCUOSMV
```

The output fails the after-freeze clue check and the generic English coherence check. The complete raw candidate set is in `frozen/K4_RESULTS.jsonl` and the postfreeze letter agreements for each of the 12, in exact blind rank order, are in `frozen/AFTER_REVEAL_EVALUATION.json`. No subsequent reranking, fitting or algorithm/key tuning took place.

## Interpretation and next hypothesis

The R55 result is evidence **against** these short-lag, simple affine feedback masks as the mechanism for ordinary-language K4. It **does not mathematically exclude** the wider classes of plaintext autokey, ciphertext autokey, nonlinear evolving alphabets, Quagmire, combined substitution/transposition, or more complicated masks. The 20/20 success on known construction shows the code is sound *in its tested family*, but failed K4 coherence and known-letter comparisons do not identify a different cipher.

Next method-first hypothesis should be chosen based on independent mechanisms and controls—not the 1/24 K4 feedback and not any crib-conditioned key. Possible next research track: reversibly **evolving substitution alphabets / nonlinear autokey masks**, test initially with hidden-key planted cases and fresh controls before original K4. Keep `r53/BLIND_RULES.md` as the binding contract.

No external verifier contacted, and `main` unchanged.
