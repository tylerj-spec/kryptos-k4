# R60 complete — code-talker-style semantic covertext versus letter encryption

**Result (1 Nov 2026): all R60 preregistered blind synthetic-control gates passed. No K4 decryption or specific masking method was discovered.** This research distinguishes *cryptographic recovery* of 97 letters from interpreting a hidden **English-to-English semantic codebook**.

## Historical motivation and correct scope

The owner's new hypothesis is **not** English deliberately misspelled as German/Dutch, and not a fully German/Dutch final message. It is an ordinary English covertext whose words may convey different hidden meanings, reminiscent of a Type-Two military code-talker vocabulary layered above ordinary language.

Ed Scheidt's [21 Jan 2005 WIRED interview](https://www.wired.com/2005/01/inside-info-on-kryptos-codes/) contains **two distinct ideas**:
1. Regarding K4, the familiar English-letter frequencies were deliberately concealed; the cryptographic masking method might not be publicly familiar.
2. In response to a discussion of already deciphered Kryptos text, Scheidt gave an illustrative private-code example where an innocuous word such as *cake* could indicate a meeting time. He did **not** confirm this as K4's construction.

Therefore, a semantic codebook is a **hypothesis**, not a historically authenticated K4 layer. A cipher can conceal letter frequencies without any semantic codebook, and a semantic codebook alone cannot generally flatten ordinary English frequencies.

## Fixed preregistration

The R60 protocol was committed **before** implementation or control creation. An amendment, also before generating controls, removed a possible ID-side-channel by shuffling all 40 controls before assigning IDs. [`PREREGISTRATION.md`](PREREGISTRATION.md) is the binding scope. Inputs and test code are under `sealed/`, `statistics/`, `tests/` and `frozen/`.

The only supported cryptographic models are the unchanged R58 four-family reference solver, with independent true cipher setting and key for each fixture:
- V, keyed position-dependent tableau proxy;
- T, six physical engraving routes;
- VT, tableau followed by route;
- TV, route followed by tableau.

**Twenty** newly written, 97-letter ordinary-English messages, five hidden-method/key cases per model, each contain one preselected visible word. Each word has *two incompatible private meanings* (e.g., a rendezvous at 0500 versus a delivery instruction at 2300) assigned in the **sealed generator**, not the solver. The independently generated ciphertext uses the **identical covertext and true key** in both semantic interpretations. Twenty iid-uniform ciphertext nulls are interleaved under IDs that reveal no truth label.

The original R58 ciphertext-only solver runs in a no-network, read-only, non-root container and sees only ciphertext, the unchanged model and generic word/quadgram priors. No actual private meaning maps, source English messages, generating cipher keys, original K4 ciphertext, K4 confirmed plaintext letters/positions or prior K4 candidates are mounted. **40 x 8 complete full 97-letter output candidates, keys, method/order, full intermediary text and raw scores were Git-frozen remotely BEFORE a separate evaluator had access to hidden truth.**

The original candidate output SHA-256 (pre-reveal): `ed751dea8bb8a8f962be1dc334fff1a3f1700a65f3086ea7b4e26556c76bfd71`.

## Strict-blind recovery on 40 newly generated ciphertexts — PASSED

| True cipher family | Whole raw 97-letter covertext AND correct hidden method/key/route | Abstentions |
|---|---:|---:|
| V | **5/5** | 0 |
| T | **5/5** | 0 |
| VT | **5/5** | 0 |
| TV | **5/5** | 0 |
| Unsupported random ciphertexts | **0/20 confident false discoveries** | 20 |

- **20/20** exact unknown-key, unknown-method full-length covertext recoveries, above preregistered overall 16/20 and each 3/5 per-family gates.
- **320/320** independently re-encrypted complete blind candidates matched their original 97-character ciphertexts.
- **20/20** true control ciphertexts were independently re-encrypted with the original hidden source key.
- **20/20 paired codebook controls = 40/40 private meaning assignments** yield exactly identical ciphertext under fixed visible covertext and key; the two semantic maps deliberately disagree.

One clear interpretation: recovering readable English covertext and encryption parameters **does not determine which semantic codebook was used**. These are arbitrarily constructed meaning mappings, so identifying the correct one from the ciphertext alone is an **unidentifiable problem** unless independent semantic information exists.

All code and controls are in this PR. [GitHub Actions run 41324255974](https://github.com/tylerj-spec/kryptos-k4/actions/runs/41324255974) passed both blinded and separate-after-freeze stages.

## Separate R60B original K4 letter-frequency test

The **unaltered original ciphertext** was read only by a separate diagnostic; no original K4 cryptanalytic solver run occurred in this round. Its byte-level SHA-256 matches `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.

Using original 97 ciphertext characters, we measured its index of coincidence:

- **Actual K4 IC:** `0.03608247422680412`.
- **Expected IC under a fixed generic English iid monogram model:** `0.06549800945363927`.
- **300,000** independent length-97 sequences were generated from that English monogram model with fixed seed 600061; **0/300,000** had IC at or below K4. Monte Carlo plus-one tail `3.333322222e-6`; for zero observations, one-sided 95% upper rate bound `9.9857e-6`.

This simulation is **NOT a test of every 97-letter coherent English covertext** (the iid English monogram model misses word and grammatical correlations), and **not** a formal exclusion of a clever semantic covertext whose words were deliberately frequency-balanced. The algebraic invariant **is exact**: a fixed one-to-one substitution and an arbitrary transposition, in either order, preserve the unordered letter-count multiset and IC. An independently chosen codebook *interpretation* of unchanged English letters also leaves the observed ciphertext unchanged. Thus ordinary-seeming English covertext plus a secret meaning alone is insufficient to explain how K4's ordinary-English statistics were hidden; an independently frequency-changing cipher/masking mechanism remains to be identified.

The separate result with all 26 ciphertext letter counts and the Monte Carlo sample count is `frozen/IC_DIAGNOSTIC.json`. This independent test never accessed published K4 known-plaintext letters/positions.

## R59 and existing-language work considered

- R59/PR #32 independently showed the original K4 four-feature omnibus test is compatible with iid-uniform output (familywise p ≈ 0.340); it detected **28/30** short periodic masks but **0/30** full-length book-derived masks, so neither proves an OTP nor rules out a nonperiodic running key.
- Claude/ChatGPT ledger L62–L69, L108 explored German/Dutch/Frisian/Low Saxon or Germanic-looking spellings and language-aware scoring, but **did not test a hidden private semantic codebook**. These existing tests are not evidence that the semantic hypothesis has been excluded.
- R58/PR #31 showed 75/80 exact source-known hidden-process controls, 0/40 wrong-family false confidence, and a K4 abstention under a particular tableau+physical route search; those finite operations are **not identified as K4's method**.

## What to do next, without inventing plaintext or keys

1. **Pursue independent evidence of the actual frequency-changing masking process** used by Sanborn/Scheidt, including contemporaneous 1988–1990 process notes, work-in-progress photographs, the backside tableau and any privately agreed codeword convention that can be documented separately from the 24 public letters.
2. If authentic codebook material is found, test its encoding/decoding independently on new hidden controls, without fitting dictionary meanings to K4 candidate ciphertext or claiming that arbitrary English words can be uniquely interpreted from a 97-letter input.
3. Continue cipher-family identification with truly new source-justified masking models and keys; preregister and freeze entire ciphertext-only original K4 outputs before any separate published-letter confirmation. Do not require weird Dutch/German spelling as a condition for a successful plaintext; an ordinary covertext could be meaningful even if its real interpretation is a separate problem.
4. **Do not search arbitrary 97-letter one-time pads and backsolve guessed plaintexts**: under an ideal OTP every guessed plaintext yields a matching key by construction.

**Research conclusion:** This round establishes that Code-Talker-style hidden *meaning* cannot be recovered from ciphertext-only cryptanalysis unless the semantic map is externally constrained. It does not identify K4's cipher, provide a K4 plaintext, or support a claim of a solve. **No external verifier used; `main` unchanged.**
