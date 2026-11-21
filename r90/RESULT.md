# R90 result (Claude Code, 22 Nov 2026): the 15 F26L alphabet classes R89 left open are excluded too

## In plain words
**ChatGPT's whole original F26L design is now tested.** Its R89 review found that R89 had swapped 15 of the design's
20 alphabets for others. R90 tests exactly those 15 (ORCHARD … CIPHER), using every improvement the review asked for:
- **Scoring and retention rule:** all 104,340 settings scored, the best 256 rescored by the letter model.
- **Stricter gate:** the right *key* is required, not only the right text.
- **Error screen:** the corrected one-ciphertext-error check.
- **Resources:** an enforced aggregate memory and CPU budget.
- **Fresh controls:** sealed practice messages from four new books.

**Results:**
- **Practice:** the solver broke all 48 practice messages with the exact key and was fooled by none of 150 decoys.
- **K4, blind:** nothing better than in scrambled copies of K4.
- **K4 against the clues:** no setting gets close to the 24 published letters. The best match is 6 of 24, even
  allowing for one wrong letter of either kind.

## Sealed gate (fresh books; `r90/holdout/GATE.json`): **GO**
| Measure | Result | Bar |
|---|---|---|
| ok: F26C, **right key**, ≥ 95/97, confident | **48/48** (48 exact) | ≥ 42 (exact ≥ 36) |
| True setting retained by stage 1 (top 256 by quadgram) | **48/48, rank 1 every time** | ≥ 46 |
| Per block stratum / per genre (narrative, history, technical) / masked | 12/12 each / 16/16 each / 12/12 | ≥ 9 / ≥ 12 / ≥ 8 |
| Negatives confident (11 generators, incl. R89's excluded catalog and RCT) | **0/150** (max letter model −1.708) | ≤ 1 |
| Extras (one plaintext or ciphertext letter wrong) | 4/4 | reported |

**Run:**
- isolated sandbox via **`audit/run_bounded_agg.py`**: COMPLETE, 21.6 s, aggregate peak **2,568 MB** with 2
  workers;
- witness 1,259/1,259;
- determinism 8/8;
- freeze pushed (167afe6) before the truth was opened.

**Amendment 1.** The first launch used 4 workers and was **killed by the aggregate budget** at 4,184 MB, after 3.5 s
and before any output. The relaunch used 2 workers with the budget unchanged.

This is the first measurement of a 4-worker run's aggregate memory. It confirms ChatGPT's point that R87–R89's 4-worker
runs very likely exceeded 4 GB in aggregate. Only per-process memory was ever enforced in those rounds.

## K4 strict blind (`r90/k4/EVALUATION.json`): **NO_SIGNAL**
| Measure | K4 | Shuffles (200) |
|---|---|---|
| Best letter model per letter (over the 256 retained) | **−1.907** (cut −1.30) | median −1.895, max −1.808; **150** at or above K4 (**p_family 0.751**) |
| Word model | −4.76 | 0 shuffles clear both cuts |
| Published letters, best decode / any frozen decode | 1/24 / 2/24 | shuffles' frozen max 5 |
| Contenders (≥ 12/24) | 0 | — |

The raw best decode (MIRROR, b 11, u 2, v 8, PALIMPSEST −1, phase 6), unedited, is gibberish:
`PGFLQOLRENBSXSRMEPWHYDREKRVREFWPZHRFCEOWDDSEYLDDRBDGHAZIMZWYFOULBVUOFTTKANGNVURIYMAIDIINGGSLCWYKB`

**Run:**
- COMPLETE, 22.2 s, aggregate peak 2,568 MB;
- witness 1,302/1,302;
- determinism 8/8;
- freeze `r90/k4/FROZEN.sha256` pushed in ab3447b before any published letter was read. The remote results blob equals
  the local one.

## Post-freeze exact check (`r90/k4/EXACT.json`): **EXCLUDED, all three error models**
| Screen | K4 settings (of 104,340) | Shuffles |
|---|---|---|
| EXACT 24/24 | **0** | — |
| DROP-PT ≥ 23/24 (one wrong published plaintext letter) | **0** | — |
| DROP-CT ≥ 22/24 (necessary for one wrong ciphertext letter; ChatGPT's correction C) | **0** | — |
| Most published letters matched by any setting | **6/24** | max 9; every shuffle reaches ≥ 6 (p 1.0) |

- **Cross-check:** on K4, full decryption of every setting gives the same result (`EXACT_CROSSCHECK.json`).
- **Resources:** the check ran under the aggregate wrapper (`EXACT_RESOURCE_LOG.json`, COMPLETE).

## What this does and does not exclude
**Excluded exactly** (crib-assisted: the published letters right, or one plaintext or ciphertext letter wrong, in
order): every F26 / F26L setting over these 15 alphabet classes.
- Blocks 5, 7, 9 and 11, all u ≠ v, and PALIMPSEST/ABSCISSA on the KRYPTOS tableau at any sign and phase, or no outer
  stage.
- **With L178:** all 20 classes of ChatGPT's original F26L design are now closed in this scope (AZ, KRYPTOS,
  PALIMPSEST, ABSCISSA and CANDLE in R89; these 15 here), plus R89's 15 others.

**Not excluded:**
- other alphabets, block sizes, zero offsets or outer keys;
- other fractionation shapes;
- insertion or deletion errors;
- transposition;
- masking;
- non-English plaintext.

## Review
**Independent review: NONE.** One model (Claude Code) built and ran R90, to the requirements of ChatGPT's R89 review.
The natural independent check is ChatGPT's `r89/audit/independent_exact.py`, pointed at the 15 alphabets.
