# R55 preregistration — blind affine feedback masking, 31 Oct 2026

**This protocol is committed BEFORE the first generated control or K4 ciphertext-only solve.**
Motivation: K4's unusually flat unigram distribution and Ed Scheidt's comments about an additional masking technique. No public plaintext, plaintext offsets, crib-fitted keys, prior K4 key survivors, or previous crib rankings influence the family or candidate ranking.

## Reversible mechanism (fixed search space)

For original 97-letter A–Z text, write (p_i,c_i\in\{0,...,25\}\).
For a lag \(L\), source \(F\), multiplier \(a\), feedback sign \(s\), offset \(b\), step \(d\):

`c[i] = (a * p[i] + b + d*i + (i>=L ? s * source[i-L] : 0)) mod 26`

Here `source` is either **previous plaintext** `p` or **previous ciphertext** `c`. Since `a` is coprime to 26, both modes invert exactly and are realistic low-parameter linear/frequency-masking transformations. `p` feedback uses already-decoded plaintext and `c` feedback uses the original ciphertext. The first L characters have NO separately fitted per-character key.

Enumerate **all 14,976** parameter tuples:
- `source` = plaintext or ciphertext (2)
- `L` = 1..8 (8)
- `a` = 1,3,5,7,9,11,15,17,19,21,23,25 (12)
- `s` = -1 or +1 (2)
- `b` = 0..25 (26)
- `d` = -1,0,+1 (3).

These fixed ranges are not derived from K4 known plaintext. A high ranking in this family is only a hypothesis until independent validation. No arbitrary 97-position shift streams or fitted substitutions are allowed.

## Immutable language model, scorer, and output

- Language score: sum of the *existing* `k4kit/data/quad_log10.f32` quadgram scores over the entire 97-letter decrypted text; no owner clues, keyword forcing, word fitting, or after-reveal reranking.
- Sort by descending quadgram score, with deterministic parameter tie breaking; output the top **12** complete raw plaintexts with full parameters for every input. Never fill or redact unknown characters.
- Blind solver input is EXACTLY `id<TAB>ciphertext` per record (two fields); original K4 is copied byte-for-byte from `r39/ic_gate/k4_ciphertext.txt` and checked against SHA256 `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.
- Execute in a no-network read-only Docker container with **only** reviewed blind solver binary, ciphertext-only input, and generic quadgram model mounted.
- All ciphertext decryption candidates must be full 97 letters with correct reversible algebra, not a plaintext fitted to confirm words.

## Fresh unknown-key holdout gate (BEFORE K4 run)

A sealed generator has 20 newly written natural-language English passages (not from prior R44's holdout); each is cleaned to 97 letters and encrypted with random but reproducible independently selected true parameters spanning the above space (seed 550551). Neither true keys nor true messages are mounted in the blind container. The same solver and entire 14,976-configuration search run on all controls. **Pass only if at least 16 of 20 exact 97/97 top-1 recoveries and ZERO invalid independent re-encryption witnesses.** A failure aborts the workflow *before K4 decryption*; no restarts or tuning on these controls.

The sealed evaluator only opens the control truth AFTER all 20 raw outputs and input/source hashes are committed to the remote Git branch. Controls are fresh to this particular round but authored by the experimenter; results do not generalize beyond this synthetic family and corpus.

## Original K4 round and nulls (ONLY if holdout gate passes)

- Generate ciphertext-only K4 plus 12 separate frequency-preserving shuffled-K4 nulls (null RNG seed 550088) with no published word or location available to the solver.
- Freeze raw input, all 13 outputs (12 complete candidate plaintexts per ciphertext), full search parameters, source/quad/ciphertext hashes, and manifest in a REMOTE Git commit **before a separate evaluator is allowed to read the public K4 letters and their positions**.
- Independent evaluator first checks hashes, every forward-re-encryption witness, and absence of malformed candidates. Only then checks the 24 confirmed K4 letters and reports per-candidate total matches. The known-letter check is NEVER used to change the scorer, candidate list, models, parameters, or future key candidates.
- Report top score versus null distribution descriptively. Twelve nulls are insufficient for a precise low-p-value significance claim.
- Success threshold: the blind output must be coherent independently recovered English, exact full forward re-encryption, a genuinely derived low-parameter key, **and all 24 published letters** only at postfreeze validation. Matching just a few letters or forward-reencrypting any text does not demonstrate a solve.

## Research integrity

All previous R40–R52 crib-assisted screens are archival and never input into R55. If this attempt fails, preserve it as a negative result and start a new preregistered experiment with independent controls; do not reuse these controls as fresh. No external Kryptos verifier submission is authorized.
