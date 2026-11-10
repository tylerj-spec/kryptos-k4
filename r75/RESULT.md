# R75 result (Claude Code, 10 Nov 2026): identify K4's method class

Pre-registration: `r75/PREREGISTRATION.md`, with Amendment 1 (a677504). Runbook: `r75/RUNBOOK.md`.

## Part A: sealed synthetic gate (no K4 data)
| Step | Commit | Result |
|---|---|---|
| Holdout (seed 750300; truth sha256 cf55a7bb… withheld) | 2d6cea8 | 160 ciphertexts |
| Blind run (about 12 min on 4 cores) and freeze | a6f65c6 | 6,934,560 fixed methods per ciphertext |
| Verify (truth not opened) | this commit | **PASSED**: 1,751 stored decodes re-encrypt |
| Gate (truth hash matched; `r75/holdout/GATE.json`) | this commit | **PASS** |

| | Recovered and confident | Bar | Worst score (letter / word model) |
|---|---|---|---|
| 60 positives (*The Lost World*, *Three Men in a Boat*) | **58/60** (misspelled 11/12) | 54 | −0.99 / −1.40 |
| 100 negatives | **0/100 confident** | 0 | best −1.76 / −3.03 (cuts −1.45 / −2.50) |

- **By sub-family:** 10/10 for five of the six. Interrupted key with sculpture keywords (F2A) got 8/10.
- **The two misses** are both F2A and both have 95–96 of 97 letters right.
  - **ITALL… read as KSALL…** A different interrupted-key setting matches the true one everywhere except the first
    two letters.
  - **NOWTHE… read as HOWTHE…** The same setting one phase off, which differs only in the first letter.
- So recovery is not the issue. Under an interrupted key, only the opening letters depend on the phase.
