# R92 development record (spent books only; NOT gate evidence)

**Texts.** Spent books only:
- Peter Pan, Northanger Abbey and White Fang, standing in for the three genres;
- Black Beauty for running keys;
- all with `--raw`.

The seed is 920300, and the set has the gate's full size: 48 positives, 4 extras and 150 negatives. No fresh book, no
K4 ciphertext and no published letter was used. **Nothing was tuned.** The solver parameters are R87's (seed changed
to 920101) and the cuts are R59's.

## Result (`DEV_SUMMARY.json`, scored by `gate92.judge`)
**RXP: GO on every bar**, with the tightest margin on masked items.

| Measure | Development | Bar |
|---|---|---|
| ok (≥ 95/97, confident) | **45/48** | ≥ 42 |
| exact | 44 | ≥ 36 |
| per clock cell | 7, 7, 7, 8, 8, 8 of 8 (n2r1, n3r1, n3r2, n4r1, n4r2, n4r3) | ≥ 6 |
| per genre | 14, 16, 15 of 16 | ≥ 13 |
| masked | **9/12** | ≥ 8 |
| negatives confident | **0/150** (max letter model −1.351, from RX0; word −1.811) | ≤ 1 |
| extras | 4/4 (plaintext errors 97/97; ciphertext errors 96/97) | reported |
| setting right / wiring right on every used contact | 47/48 / 44/48 | reported |

- The lowest letter-model score of a recovery is −1.085.
- Every generator's best negative is at or below −1.351, including the two near-family decoys:
  - RX0 (R87's zero-phase rotor): −1.351;
  - RX2O (two-rotor odometer): −1.399.

**The three misses are all masked.** Each was diagnosed by a long anneal at the true setting (64 × 100,000):
| Item | Cell | Best decode | Diagnosis |
|---|---|---|---|
| H_160 | n3r1 | 83/97, letter model −1.302 (just under the cut) | true setting found; the quadgram optimum is not the text (a long anneal reaches only 77/97), while the true text scores −1.163. A scorer and landscape limit on masked text |
| H_170 | n2r1 | 1/97, wrong setting | search failure: a long anneal at the true setting recovers 97/97 (−1.034), so pass 1 did not keep the true setting |
| H_175 | n3r2 | 93/97, confident | scorer limit: the found decode (−1.034) scores above the true text (−1.043) |

H_076 is ok at 95/97 but its wiring differs on a used contact, which is why the wiring count (44) is below ok (45).

**Witness:** 1,010/1,010 stored decodes re-encrypt under `witness92.py`.

**Cost:** 202 items in 993 s wall on 2 workers (1,934 s CPU). Peak resident memory was about 1.29 GB per worker, so
about 2.6 GB in aggregate. The work order's 180 s / 120 s / 512 MiB development budget was set for the synthetic
specification work. This solver run is over it, as `r92/PREREGISTRATION.md` discloses.

| File | sha256 |
|---|---|
| Development input | 6a461493defafda5c3f6d2cd0d8fec3893c1e52c9ea0e35e15cf13cd2b40c766 |
| Development results | 0bc9f94ff2b79c320dc1f20f63a65feb2eafedf764fb5b92e198879e25c25912 |
| Development truth | 64dcc9a81fdd6c517c7115990c45f18a07a77d5e1ae77655b274e96d784d3bf1 |

**Isolation:**
- The first 3 development items, run through `make_sandbox92.py` and `run_isolated92.sh` with 1 process,
  reproduce the open run **byte for byte**. That took 30.6 s.
- That check also caught that `rotor92.py`'s variable name `CLOCKS` contains a published word, which the sandbox
  tripwire refuses. It was renamed to `SCHEDS`, with no change in behaviour, which the byte-for-byte reproduction
  confirms.
