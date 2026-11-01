# R56 preregistration: evolving-alphabet rotor (Chaocipher update) — ciphertext-only, unknown-key gate

**Committed before building the generator, running synthetic controls, or decrypting original K4.**

## Rationale and historical limitation
Ed Scheidt described disguising K4's English frequency signal (WIRED, Jan 2005). A genuinely evolving substitution alphabet changes the mapping after every letter and can flatten frequencies without arbitrary 97-position key fitting. R56 examines the **specific documented Chaocipher two-wheel permutation algorithm**, as a method-class control. **The original Chaocipher algorithm was publicly revealed in 2010, after Kryptos's creation; we do NOT claim Sanborn used it or that it was independently available in 1990.** The mechanism and key family are chosen solely from a public cryptographic model, not from published K4 plaintext.

## Mechanism (completely reversible)
Two ordered 26-letter alphabets L (cipher) and R (plaintext). At each step encrypt plaintext letter P by its index j in R to ciphertext L[j]. Decrypt ciphertext C by its index j in L to plaintext R[j]. Then update both wheels deterministically:
1. Rotate L left j positions, remove its element at zero-based position 1 and insert at position 13.
2. Rotate R left (j+1) positions, remove element at zero-based position 2 and insert at position 13.

Those are the standard Chaocipher wheel updates (not additive Vigenere or R55 affine feedback). They depend on the recovered character at each step, so a wrong initial key rapidly diverges. The independent forward encryptor must perfectly reproduce all 97 characters.

## Frozen initial-state/key search
The initial alphabet key is drawn from a GENERIC pre-existing corpus, **not the published K4 plaintext, not prior crib-selected key lists**:
- Read `k4kit/data/word_model_orth.tsv`; order words of lengths 5–10 by decreasing generic model score (tie alphabetical), take exactly the top 1024 words, map each to its keyed alphabet (unique letters in first-appearance order followed by unused A–Z), de-duplicate the alphabets, sort the resulting alphabets lexicographically.
- Enumerate every such alphabet as **one** initial wheel (either L or R); the opposite wheel is the ordinary A–Z ordering.
- Enumerate 26 initial R-wheel rotation phases, 0..25.
- No K4-specific English word, physical clock inscription, published K4 phrase, position, clue-derived survivor, or guessed plaintext enters the candidate list or search algorithm.
- Score each 97-character candidate by the full pre-existing `quad_log10.f32` quadgram model. Deterministic descending score then key/side/phase tie break. Freeze **top 12** complete raw 97-letter candidates with all keys. No discretionary ranking.

Total configurations per ciphertext = `52 * unique(keyword_alphabets(top_1024_words))`, computed and verified at runtime. No other parameters will be tuned after checking K4.

## Controls, required before any K4 run
- 20 new, independently written English 97-letter passages (different from prior R44 and R55 passages). Use deterministic random key choice from exactly this fixed family with **both real plaintext and real key hidden** from the solver (seed 560056).
- Perform full family enumeration on the ciphertexts in a read-only no-network unprivileged Docker container mounting **only the compiled solver, ciphertext-only TSV, pre-existing generic word-model corpus, and quadgram model**. No source repo, K4 plaintext data, truth files, historical crib reports, or network mounted.
- Freeze raw 20-case results, exact input source and scores, script/hash metadata by remote Git commit **before** independent sealed controls evaluator reads true plaintexts/keys.
- **Mandatory pass gate: at least 16/20 exact 97-letter top-1 plaintexts**, and every frozen candidate must re-encrypt identically using a separately implemented encryptor. Do not run K4 if gate fails. Report exact recovered key settings separately.
- Calibration is closed-world synthetic; success only supports recoverability *within this limited, publicly specified family*, not K4 or keys outside dictionary.

## K4 ciphertext-only run if and only if gate passes
- Use the original 97-letter K4 ciphertext byte-for-byte from `r39/ic_gate/k4_ciphertext.txt` (cryptographic hash verified) and 12 deterministic frequency-preserving shuffled null sequences (seed 560070), with precisely the same solver and fixed settings.
- Freeze all 13 × 12 raw 97-letter plaintexts, keys and scores in a second REMOTE Git commit; only after this may a distinct evaluator process any published K4 plaintext letters or positions.
- The after-freeze evaluator independently forward-encrypts all witnesses and compares the fixed output, *without re-ranking or tuning*, to the public 24-letter positional clues. Exact match to all 24 plus independently coherent English and valid forward witness is necessary, not sufficient, for a candidate solution.
- 12 nulls provide only descriptive context; avoid claiming precise statistical significance.
- No external K4 checker/submission. Do not merge to main without review. Preserve failures.

## Prior exposure
R55's affine-feedback family passed 20/20 hidden-key synthetic controls but failed its K4 trial (top 1/24, best 2/24). R56 changes the actual **mechanism**, not its parameters based on the failed known-letter comparison. We are explicitly NOT using R55 outputs, K4 public letters, or clue-conditioned excluded keys to rank hypotheses.

Sources used to define model: Chaocipher Revealed: The Algorithm (Rubin) and published two-wheel rotation rules; WIRED Jan 2005 Scheidt interview. No external checker contacted.
