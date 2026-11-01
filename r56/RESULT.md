# R56 complete: exact synthetic hidden-key recovery; negative K4 result

**No K4 solution.** PR #28 tests a narrowly defined, reversible two-wheel Chaocipher update under fixed generic keyword-alphabet initialization. All changes, protocols, and controls were committed before K4 was run. GitHub Actions [41262349526](https://github.com/tylerj-spec/kryptos-k4/actions/runs/41262349526) completed **successfully** with strict separate, remotely frozen results.

## Preregistered family
- One evolving plaintext/ciphertext wheel initialized with a generic keyword alphabet from the top 1,024 existing words; other wheel initialized alphabetically.
- **987 unique keyword alphabets**, two key-side choices and 26 initial R phases => **51,324** keys evaluated per ciphertext.
- Both wheels permute after every letter, matching the standard Chaocipher algorithm (verified with published reference vector). This method was publicly disclosed in 2010, and its use for a work created circa 1990 is **not claimed**.
- Plaintext only scored by the pre-existing generic quadgram language model. Top 12 raw full 97-letter candidates frozen for each input; no known K4 plaintext or position entered candidate generation.

## Hidden-key controls before touching K4
- **20/20** exact top-ranked 97-letter synthetic plaintexts recovered **with actual keys unknown to solver**.
- **20/20** exact true initialization settings recovered.
- **240/240** independently verified forward-reencryption witnesses.
- Controls output SHA256 frozen in remote Git: `14c04d3f2bbd627f6a75ee6ee167cc38c8a4ec8f2fa552b4f6ef74075344099d`.
- The controls deliberately sample from this closed-world family. That result demonstrates code recoverability for that family, not the identity of K4's encryption method.

## Original K4 ciphertext-only run, then separate reveal
- **13 ciphertexts**: unchanged canonical K4 + 12 independently generated frequency-preserving shuffles.
- Each searched all **51,324** keys; **156/156** frozen candidate forward witnesses verified.
- Remote-frozen K4 output SHA256 `4260f7cea9a02919b3918aacb675c12dbd0a25d77ab5ed8955e1bac6d6723e4f`. Raw 13×12 results in `frozen/K4_RESULTS.jsonl`.
- Blind best full 97-letter output (unedited):
  `DSKIOISMVUTNBYCALMDOMFDRSBKDOZSSDMKBARFRASLANPROUEQXUACTUBTAXTYEMHBTUZRGMWFYPLPEMIYASONBYMBEYSOWJ`
- Highest K4 quadgram score **−645.11949611**. Four shuffled controls scored better; descriptive empirical tail `5/13≈0.3846`, which is not a precise hypothesis p-value.
- **Only AFTER Git froze all outputs**, the independent evaluator found **0/24** confirmed characters matched by the top-ranked candidate, and **3/24** as the highest overlap among the frozen 12. **0/12** candidates match all published 24. None is readable English.

## Interpretation
The tested (standard-wheel-update, generic-keyword-initialization, one keyed wheel plus alphabetical wheel, 26 right phases) family finds no credible K4 solution. This is a **negative** within a precisely declared finite model, **not** a proof that all evolving-alphabet systems fail: two arbitrary wheels, alternative keyed permutations, different update rules, and combinations with transpositions remain untested.

The known-letter check only rejects frozen candidates and was not used for key or cipher tuning. No external verifier contacted. Main unchanged. Review the full research archive in PR #28.
