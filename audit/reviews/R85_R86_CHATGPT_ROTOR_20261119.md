# R85 and R86 rotor pilot review (19 Nov 2026, ChatGPT GPT-6)

Affected ledger IDs: L174, L175
Validation: R85 preregistered gate FAIL 15/20 ≥95/97 and 14/20 exact; no K4 run; 120/120 independent 97-letter forward re-encryptions. R86 used a separate preregistration and independent fresh 20-item gate (17/20 ≥95, 15/20 exact, 20/20 rotor step and direction correct, each n stratum 4/5,4/5,4/5,5/5); 120/120 controls and 606/606 K4+null output witnesses forward-re-encrypt. K4 best -1418.868044; 32 of 100 frequency-preserving shuffles scored at least as high; family-wise p 33/101=0.3267326733; verdict NO_SIGNAL. The complete original K4 and null output file (SHA256 5460f72117b585ec0f35dc07910a2024f26af9521129a55f8116747faca875b5), target file, keys, scores, witness and resource report were frozen before published-letter validation in commit 26dee4e72524f3ad74248a3163bffebb6bb27645. After this commit, a separate checker compared the six immutable K4 outputs with the 24 released plaintext positions; best-score candidate 1/24, maximum 3/24, no survivor. All six fail; no "prospect" is promoted. Independent Git blob SHA comparison succeeded for the six frozen GitHub files.
Independent review: NONE

Builder and evaluator were both ChatGPT GPT-6 in the same extended interaction, and the independent mathematical witness means *separate code path*, **not an independent model/person**. This review does NOT promote any ledger exclusion, and no `Promotes:` entry is claimed. The R85 gate and R86 gate do not belong to the same random trial and must not be pooled into a 32/40 estimate. R86's increased computational budget was preregistered after R85's miss, with a new gate. R85's failure stands.

Scoped limitations: R86 is AZ/AZ, n1–4, two directions, one rotor, free wiring searched heuristically rather than exhaustively. The solver did not read published words or their positions; the after-freeze clue checker does, only to reject. No proof that K4 cannot use such a rotor, and no implication for KRY/PAL/ABS alphabets, longer steps, multiple/irregular rotors, transposition, masking, non-English or deliberately nonstandard spelling. Empirical null based on K4 unigram-preserving shuffles is one reference population, not a universal likelihood estimate. Positive controls are one movie-review genre. The run was bounded by a custom RLIMIT_AS runner, not the repository's audited launcher; reported max_rss_mb reflects that conservative memory bound rather than an observed peak. One gate-run shell footer was interrupted, although outputs were completely recorded and verified. No external checker submitted.

Source hashes and byte-level artifacts:
- `r86/PREREGISTRATION.md`, committed 6442ffcdde9480f6f0da8e023c2b349d347ea6d1 before the new gate;
- `r86/holdout/GATE.json`, committed b144e2bf3d5adfb1d07cabc5b1d2b406acf457c8 before the K4 freeze;
- `r86/k4/FROZEN.sha256` on pushed commit 26dee4e72524f3ad74248a3163bffebb6bb27645;
- `r86/k4/POSTFREEZE_REVEAL.json`, intro commit 278c271d2bf02a97b37d3bad31b10d014c9cff1e after the freeze;
- `r85/PILOT_RESULT.md` and `r86/RESULT.md`.

Methodological warning: the fact that *all 606 blind texts* reencrypt to their own input is a useful invariant, NOT evidence that the plaintext is meaningful. Re-ranking on the published clues would destroy the independence of this candidate test. No other experiments or historical exclusions are promoted by this review.
