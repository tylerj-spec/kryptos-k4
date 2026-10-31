# R50 measured result — K3 double quarter-turn BEFORE Gromark substitution

**Date:** 30 October 2026. **Conclusion:** exact contradiction with public 24 K4 letters for the *pre-registered finite hypothesis* only. **NO K4 plaintext recovered.**

## Protocol and execution
- [Pre-registration](PREREGISTRATION.md), SHA256 `95d7d957c593f7cc952a41ecc83a04bafe31785a802eee05bb583c4e2213913f`, committed **before** ciphertext analysis.
- [Full CI audit](https://github.com/tylerj-spec/kryptos-k4/actions/runs/41159610341) **SUCCESS**; 20/20 synthetic forward/inverse controls, full original K4 + two shuffled originals, first three two-free primer survivors per route/ciphertext independently unindexed-checked against **all** 4,761 alphabets in both arithmetic directions and both orientations.
- [Raw frozen report](R50_EXACT_RESULT.json) generated and committed by Actions, with [SHA256 manifest](R50_RESULT.sha256).
- Original K4 and its 24 known plaintext letters used only in a sealed, postfreeze mathematical compatibility test. **No cribbed/candidate plaintext string or language score was produced.**
- Four routes test `Q[j]=P[perm[j]]`, `CT[j]=CA[(PA^-1(Q[j])±k[j])%26]`. This is **T_then_S**, NOT R46's S_then_T.
- All 100,000 five-digit Gromark primer streams, ± signs, both keyword orientations; 4,749 common keyed alphabets and **12** previously excluded-from-common distinct themed alphabets (from 15 declared keywords).
- Explicit positive **wrong-order** control: original true keys/alphabet fail the incorrect no-route mapping in **20 of 20** plants.
- **Independent C++ replay** implemented separately after preregistration: SHA256 of source `1ccf665c2cc962502c9d04cba04e7aba5a5c4cb8b54c7264c81ba032086275c3`; independently re-derives graph potentials, complete alphabet packability, same four route orders. Its in-place 39-count, all four earlier R46 S_then_T counts and all four new T_then_S two-free counts exactly match GitHub.

## Original K4

| K3-style transposition applied **before** substitution | Two arbitrary alphabets (compatible 5-digit primers) | 4,749 common-keyword PA/CA + 12 themed keyword arrangements |
|---|---:|---:|
| R24x8/CW/fwd | **52** | **0** |
| R24x8/CW/inv | **1,569** | **0** |
| R24x8/CCW/fwd | **1,479** | **0** |
| R24x8/CCW/inv | **8,805** | **0** |

Every two-free survivor was checked against **every** keyword alphabet, ± and both orientations (the indexed necessary signature may skip only mathematically impossible candidates, with independent full-vocabulary checks on sampled survivors). All four *keyword*-family counts **0**.

## Two fixed shuffled ciphertext nulls
- Seed 50100: two-free possible keys by above route order **481 / 4,550 / 24 / 296**, all keyword counts zero.
- Seed 50101: two-free possible keys **209 / 284 / 43 / 1,321**, all keyword counts zero.
- Only two nulls, no statistical p-value. Zero keyword matches in nulls is consistent with stringent keyword restrictions.

## Meaning and next scientific experiment

- **EXCL** only the four named 24×8 K3 transposition-first routes, 5-digit Gromark recurrence, both operations, one of the 4,761 fixed keyword alphabets and another fully arbitrary alphabet.
- **NOT EXCL** other routes, other keystream rules, masking/salt, arbitrary alphabets on both sides, or K4's World Clock reference as message *content*.
- STOP rerunning any branch of the same excluded finite family. Next task should change the source of the keystream or the cipher architecture; independently blind-decrypt on fresh 97-letter controls with **unknown key** before claiming progress. Distinguish a mathematically feasible witness (sometimes thousands per route) from actual English.

No outside K4 verifier contacted, and `main` unchanged. This result does not imply K4 is solved.
