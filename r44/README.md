# R44 / R44b: reviewed known-key alphabet recovery — NOT a K4 solve

**Status: VALIDATED ON CONTROLLED KNOWN-KEY HOLDOUT, UNKNOWN-KEY K4 GATE NOT MET.**

This is a selective import of Claude Code's **pre-R52** R44 research at commit `504eccdfc81d05f468987be8ea55129ad2c7826c`. It intentionally **excludes** the later `r52_claude/` branch experiments that used the published K4 letters to select a candidate primer and route.

## What was demonstrated

- With the *true* 97-position Gromark key/shift stream supplied, `blind/kwpa_solve.cpp` enumerates 4,749 keyword plaintext alphabets and optimizes a free ciphertext alphabet.
- `blind/polish.cpp` refines the free alphabet with fixed quadgram + word scores.
- Initial R44 blind holdout: **14/20** exact, failed its 16/20 gate.
- After developing polish on that *already-seen* holdout, the **fresh** independently frozen R44b holdout: **20/20 complete 97-letter plaintexts recovered exactly**, with **20/20 valid independent forward encryptions**; solver-only baseline **16/20**. The fresh result was not the tuning set.
- Source and frozen outputs are in this directory. Run `python3 -I r44/tests/verify_frozen_holdout.py` for independent saved-result verification.

## What is NOT demonstrated

- No recovery of an unknown K4 key, ciphertext masking method, or novel K4 plaintext.
- No ability to recover arbitrary *two-free-alphabet* messages (R43's failed search).
- The keyword is drawn from a **closed, predeclared dictionary**. Performance does not transfer automatically to unseen alphabets or K4.

Historical `audit/` notes recount crib-assisted finite-family exclusions from other PRs. They are **research archive only**, are not valid blind candidate-generation seeds, and should not be treated as proof about general cipher families. Any new solver must run on raw K4 ciphertext without published plaintext/positions, prove an *unknown-key* fresh-control benchmark, freeze complete outputs, and only then reveal the 24 letters through the separate validator in `r53/`.
