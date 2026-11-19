# R86: strict-blind AZ/AZ single-stepping-rotor experiment (19 Nov 2026)

**Verdict: STAT_NO_SIGNAL. No credible K4 plaintext candidate. Do not promote this to an exact rotor-family exclusion. No outside answer-checker submission.**

## What was tested
Starting from original 97-character K4 ciphertext (newline SHA256 `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`), a single arbitrary-wiring 26-contact rotor with alphabet AZ both sides. Step state s_i = d floor(i/n) modulo 26; n = 1,2,3,4; d = ±1. Inverse permutation W is free (26! potential values). The blind solver was a heuristic annealer, **not exhaustive**: 80 random starts, 16,000 swaps per start per setting, seed 8600, 2/3/4-gram scores plus generic dictionary refinement. Top six raw 97-letter decodes and inverse wirings retained per input. Neither the solver, key search nor language model had the published K4 words/positions. This is the narrow R85 proposal, not all possible rotor ciphers.

## Hidden-positive gate and negative controls
- Previous R85 developer pilot FAILED its 16/20 gate (15/20 at ≥95 letters, 14/20 exact); K4 not run under R85.
- R86 fresh sealed gate `r86/holdout/GATE.json`: **GO, 17/20** with correct n,d and ≥95/97, **15/20 exact**; n,d correct 20/20; by n the successes were 4/5,4/5,4/5,5/5 (minimum 3/5 passed). Independently forward-encrypted **120/120** control decodes. Source hash, independent test and raw gate TSV preserved under `r86/holdout/`.
- Wrong-family negatives: 20 inputs (10 long-key Vigenere, 10 shuffled English), searched identically; **120/120** retained decodes independently re-encrypted by the frozen trial wiring. Best negative model-score range −1443.4 through −1363.1, median −1402.4. They are not proof of zero false positives, and no scoring threshold was tuned from them.

## Original K4 + 100 frequency-preserving shuffles
- Complete target: `r86/k4/TARGET.tsv`, sha256 `d381e372b444438786fce14fb02bfff4c12b522af501311c9a6a7ebeef362969`.
- Complete 606 raw outputs (six per K4 or shuffle): `r86/k4/run/RESULTS.tsv`; SHA256 `5460f72117b585ec0f35dc07910a2024f26af9521129a55f8116747faca875b5`.
- Independent forward-encryption witness: **606/606** exact for every letter, plus 280 synthetic oracle property checks; `r86/k4/run/WITNESS.json`. Exact re-encipherment proves internal cipher consistency, **not** that the plaintext is correct.
- K4 best unedited score **−1418.868044**, state n=3, d=−1. Best decoder output:
  `ECONOTARHINGMISWMVEESNMVALLAMOLANESOAFRIOUTTANDDHEXCEARMEMAPHONGCEWEETWAINESETAINEDATHFNINFQUANDA`
- Of 100 controls, **32** scored at least as highly. Prespecified family-wise p = (1+32)/101 = **0.32673**, with null median −1427.115695, maximum −1373.307829. The high-scoring decode is not coherent English. **NO_SIGNAL.** No rotor parameter or deciphered text is supported as a K4 lead.

## Strict freeze and *separate* clue evaluation
All 101 input rows, 606 complete outputs, 606-key configurations, scores, independent witness report, score report and resource record were pushed and SHA256-frozen in GitHub commit **`26dee4e72524f3ad74248a3163bffebb6bb27645`**, before any released plaintext check. Each file's remote Git blob SHA was compared with the independent local Git blob and matched.

Only then did a separate script (`r86/sealed/postfreeze_reveal.py`) read the 24 published plaintext letters. It **did not** fit, regenerate, reorder, optimize or filter candidates. **Top-score output 1/24 match; best of retained six outputs 3/24; none 24/24.** This is `r86/k4/POSTFREEZE_REVEAL.json`. The known-letter information must never be fed back into the blind solver.

## Resource, trust and scope caveats
- Custom local allowlisted process copied exactly the binary, target, 2/3/4-gram generic models and dictionary; no repo/crib file was passed. The container does not represent the repository's fully audited Docker mount/network isolation, so full R53 environment-equivalence has **not** been independently demonstrated.
- Full 101-case solver process **COMPLETE** (exit 0, 606 expected outputs), 384.3263 seconds, 3600-second limit. RLIMIT_AS was set at 1024 MiB; the resource record's `max_rss_mb` is that conservative *address-space bound*, **not a measured peak resident set size**. The custom runner was not `audit/run_bounded.py`. Synthetic gate had a missing terminal wallclock footer from an interrupted local shell session, despite complete frozen 120 candidate records/witnesses.
- Training and holdout are limited in genre; no external independent cryptographer/second model audited this test. **Independent review: NONE.**
- No direct test of KRYPTOS/PALIMPSEST/ABSCISSA contact alphabets; any n≥5, irregular stepping, two rotors, physical transposition, nonstandard language, hidden orthography or extra stages remain OPEN. The annealer cannot exclude the n≤4 AZ/AZ family even though it passed a limited hidden gate.
- Any new RX search must use fresh sealed controls, a new preregistration and seeds, and must not reuse this postfreeze result to select key parameters.

## Next highest-information follow-up
Test progressively keyed Quagmire (RQ) or RX with a second contact alphabet, but use a **separate fresh hidden-family gate**, not a known-clue feasibility screen as a generator. A tougher and more creative option is an irregular-step rotor or mask with ciphertext-only state and documented hand-operable mechanism. Prioritize independent audit of the negative-result methodology before increasing search to n=26 or multiple rotors. Under no condition turn a chance-level fragment into an alleged plaintext.
