# R58 preregistration: identify the sequence of operations, not just a key

FROZEN BEFORE R58 CODE, CONTROL GENERATION OR K4 SEARCH. Date: 2026-11-01 UTC.

## Source-based construction

- CIA original transcription: https://www.cia.gov/legacy/headquarters/kryptos-sculpture — K4 occupies the final 4 cells of one physical row and the following 3 complete 31-cell rows. The tableau is intentionally reversed; K1–K3 used tableau and matrix mechanisms.
- Ed Scheidt, 2005: https://www.wired.com/2005/01/inside-info-on-kryptos-codes/ — four different processes, frequency masking in K4; does NOT establish K4 as exactly two layers.
- The historical K1/K2 keywords KRYPTOS, PALIMPSEST and ABSCISSA are public independently of K4 clues.
- A fixed bijective substitution and a transposition, in any order, preserve the original count multiset and IC. This combination alone cannot turn ordinary-English frequencies into K4's unusually flat distribution. A changing alphabet or other frequency-altering process is required if its underlying 97-letter message has typical English statistics.

## Fixed test families (all settings unknown to one common blind solver)

1. V = keyed-tableau periodic addition on KRYPTOS-mixed 26-letter alphabet A: E(P,i,K)=A[(index_A(P[i])+index_A(K[i%len(K)])) mod 26].
   This is a Quagmire-inspired proxy, NOT independently established to be the exact K1/K2 equation.
2. T = physical-route permutation: write 97 consecutive letters into the engraving sites, row0 cols27..30, rows1..3 cols0..30, then read them in one of precisely 6 different orders: column-major (left-to-right/right-to-left crossed with top-to-bottom/bottom-to-top), or row snake in two alternating directions. Zero null cells/padding.
3. VT = encrypt with V then apply T; ciphertext = T(V(plaintext)).
4. TV = encrypt with T then apply V; ciphertext = V(T(plaintext)).

The V key vocabulary is exactly KRYPTOS, PALIMPSEST, ABSCISSA, plus the top 64 distinct A-Z uppercase words of length 5–10 ranked by the generic pre-existing k4kit/data/word_model_orth.tsv score column (decreasing score, alphabetical ties). No K4 known-word strings, positions, guessed full plaintext, R52 crib-selected keys, K4 known-letter scores or prior K4 output rankings may inform selection. Every V setting, T route, VT and TV order is enumerated from CIPHERTEXT ALONE. Score the complete 97-letter final plaintext by existing generic k4kit/data/quad_log10.f32 quadgrams, never the intermediate stage. Freeze top 8 complete raw 97-letter texts, exact keys/routes/order, first reversed intermediate for composite models and scores with deterministic ties. Record ambiguous observationally equivalent solutions.

## R58A full unseen-family-and-key benchmark, mandatory before K4

Synthetic generator separate from blind solver, RNG seed 580058, 20 new unique English 97-letter messages for each V/T/VT/TV class (80 total); 20 97-letter out-of-family Hill digraphic ciphertexts with hidden independent matrix keys, plus 20 independently shuffled-English nulls. All 120 IDs randomly interleaved and opaque CASE_000 etc (IDs cannot reveal the generating family). Blind solver receives exactly ID<TAB>CIPHERTEXT, its own source, generic quadgrams and generic keyword file; no source passage templates, encryption generator, known truth or keys, K4 plaintext clues, K4 previous output, repo history or network. CI mounts only reviewed blind code, input, existing generic models and output in a no-network, read-only unprivileged container.

Conservative frozen ABSTAIN rule: report confident class ONLY if top full-text quadgram log10 score >= -525.0 AND margin over the next DISTINCT plaintext >= 10.0 log10 units. Otherwise ABSTAIN and still retain top-8 raw candidates. Thresholds are historical development priors based on English scores around -400 and R55–R57 gibberish around -640, not tuned to new sealed examples or K4 letters.

Commit entire 120-case input+raw output, source/model hashes and manifest to a REMOTE Git commit BEFORE a different sealed evaluator reveals family, key, plaintext. Pass iff (a) each of four families has >=16/20 exact full 97-letter plaintext AND correct class, (b) each family has >=16/20 correct true route/key settings, (c) each out-of-family group has <=1/20 confident false discovery, and (d) every frozen candidate independently forward-encrypts to its original ciphertext. Failure records negative evidence and forbids R58B K4. Do not tune on the now-seen controls; choose fresh new controls for substantial revisions.

## R58B only if all R58A gates pass

Original ciphertext must be read from r39/ic_gate/k4_ciphertext.txt with SHA256 including newline 2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3, unchanged 97 A–Z. Search with identical reviewed solver and key/route model; run >=100 frequency-preserving shuffled-K4 nulls in identical full search for corrected familywise calibration. Remotely freeze full 97-letter raw K4 texts and all keys/order/intermediates/hashes BEFORE an independent verifier can read the 24 published K4 plaintext letters or positions. The separate verifier independently forward-encrypts candidates, then compares to fixed released-letter positions, only to reject or corroborate FROZEN outputs; no tuning or ranking by these checks.

Only independently fluent novel English, derived non-fitted key, exact complete re-encryption and 24/24 known-letter agreement after freeze qualifies as a K4 candidate. No external answer checker or claims of a solution without those criteria. Main branch unchanged until review.

## Limitations and interpretation

The sculpture's 4/31/31/31 layout constrains a physical-route *hypothesis*; it is NOT proof K4 used a columnar route. The 20-per-family controls are closed-world; passing them does not prove K4 uses the family. Original 97-character length need not correspond to a plaintext row count. K1/K2 tableaux equations here are a proxy, not necessarily identical to historical encryption. If the combined test fails, document it and investigate the construction process / physical source instead of silently broadening keyspaces.

## Amendment A (2026-11-01 UTC, BEFORE generating any controls or running R58A)

The original paragraph specified **newly written natural-English messages**. To strengthen source diversity and allow exact independent reproduction without model-authored fixtures, replace that one source requirement with **120 nonoverlapping 97-letter natural-English windows selected from two pinned public-domain novels**:

- Lewis Carroll, *Alice's Adventures in Wonderland*: GITenberg `GITenberg/Alice-s-Adventures-in-Wonderland_11`, immutable commit `7f18748e114b994d5d9454d5793581bc0b9cf9d7`, file `11-0.txt`, exact Git blob SHA-1 `0f25e9af379233267a09623e0c650472f9e463ea`.
- Jane Austen, *Pride and Prejudice*: GITenberg `GITenberg/Pride-and-Prejudice_1342`, immutable commit `81db45c9c48c592f0b77f01fc59e677ad0a5634e`, file `1342-0.txt`, Git blob SHA-1 `20c3737a33af2501e4c0597285ad630ef42e8e46`.

The preparation script verifies exact Git blob SHA-1 against source bytes, extracts the literary body rather than headers/licenses, strips non-ASCII A–Z, and samples nonoverlapping windows using the predeclared seed 580058, evenly split between books, ensuring distinctness. Both books are in the U.S. public domain. These are *fresh unseen controls for this project*, not newly authored writing. Only ciphertext and opaque IDs enter the blind process; full source books, selected offsets, keys, and plaintext remain outside its isolated filesystem. A 97-letter sample can start/end mid-sentence; this is declared, not a decryptor failure. **No key ranges, scores, route list, thresholds, recovery gates, K4 inputs, or candidate selection rules change.** No K4 decryption has yet run under R58.
