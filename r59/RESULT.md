# R59 result (Claude Code, 2 Nov 2026): K4 shows no sign of a running key from an unknown English text

**No K4 solution. NO SIGNAL under the pre-registered rule.**
- **Rule followed:** the solver never saw K4's published letters. Every output was frozen and pushed before the
  separate reveal.
- **Not done:** no external checker was contacted.

## Plain words
- **The question:** could K4 have been made with the K1/K2-style tableau, with a key taken from some unknown English
  text (a running key), while the plaintext is ordinary English?
- **Why it was a natural guess:** this is the simplest way to make English as flat in letter counts as K4 is. 12–13% of
  simulated running-key ciphertexts are as flat as K4.
- **The solver works:** on 20 hidden test messages from books it had never seen, it identified the tableau every time.
  It recovered most letters (median 72 of 97 letter pairs correct), and 16 of 20 messages scored above every shuffled
  copy.
- **On K4 it found nothing:**
  - K4 scored like shuffled letters: 46 of K4's own 100 shuffled copies scored as high or higher.
  - It scored **below every one of the 20 test messages**.
  - Its output matches only 3 of the 24 published letters, which is typical of the shuffled copies.
- **Conclusion:** within the tested model, K4 does not look like an English running key.

## Pre-registered steps (`r59/PREREGISTRATION.md`, commit f1848ad)
| Step | Commit | Result |
|---|---|---|
| Pre-registration (solver, gate, K4 rule, hidden-meaning protocol) | f1848ad | — |
| Holdout generated after registration; truth withheld, sha256 recorded | c8794a6 | 20 plants, 20 nulls |
| Holdout freeze (blind outputs) | f3f9e3f | — |
| Holdout gate (`r59/holdout/GATE_REPORT.json`; truth hash matched) | e62da2e | **PASSED**: detected 16/20 (bar 16), convention 20/20 (bar 16), pair-correct ≥ 60 in 18/20 (bar 12), witnesses valid; median pair-correct 72/97; best 97/97 pairs (HOLD_18) |
| K4 target: unchanged K4 + 100 shuffles (seed 590070) | edd871d | — |
| K4 freeze | c59703c | — |
| Reveal (`r59/k4/REVEAL.json`) | this commit | **NO SIGNAL** |

**Note on the base branch:** PR #37, which held the first two commits, was merged into `main` by the owner account
while the holdout was running. The freezes and results continue on the same branch, restarted from that `main`.

## K4 numbers
| Measure | Value |
|---|---|
| K4 best total F | −325.91 (convention KRY_VIG) |
| Nulls (100 shuffles of K4): min / median / max | −338.0 / −326.4 / −310.1 |
| Nulls scoring ≥ K4 | **46 / 100** (empirical p = 0.47) |
| Holdout plants scoring above K4's score | **20 / 20** (lowest plant −321.9) |
| Holdout plants above K4's null maximum (power of the strict r = 0 rule) | 16 / 20 (80%) |
| Published letters matched by K4's frozen best output | 3/24 in one text, 0/24 in the other |
| The same count for the 100 nulls' best outputs | median 2, max 6 |
| Re-encryption witnesses checked | 1,313 / 1,313 exact |

**Raw K4 output, unedited.** This is the best pair under the model. It is word salad, exactly like the outputs on
shuffled letters, so it is **not** a decryption:
```
text A  NREWARDJACKGIRLSBUTQUESTINMUSICFORBEINGCENSUREINMINEASLOOKUPHESHALLPRESSINGTOBACKDOORSCLAYWASPOSS
text B  FAITHTHISOUTNOHEALTHYREWARYBUTTHROWNBEAWORKEDIDSOMEONETODAYFORYOUFORPANSHADCOMMITSTOHALTANDHOWTRU
```

## What this rules out, and what it does not
- **Evidence against (STAT, not an exact exclusion):** K4 as an **in-place** running key in which both the plaintext
  and the key are ordinary English letters, under AZ or KRYPTOS × Vigenère / Beaufort / variant Beaufort.
  - With the strict rule, a true example would have been detected about 80% of the time.
  - K4 is not even near the edge: it sits in the middle of the null distribution and below every test message.
- **Not covered:**
  - a running key **combined with a transposition** (K3-style or other);
  - other tableaux, mixed alphabets or two different alphabets;
  - keys that are not ordinary English: other languages, numbers, coordinates, or text with deliberate errors;
  - a masking step before encryption;
  - autokey and other feedback;
  - plaintexts that are not ordinary English.
- **The working hypothesis survives:** "readable English covertext plus a frequency-flattening layer" is still open.
  This round removes the simplest version of that layer.
- **The second question** (a hidden meaning) still waits for a decryption, per `r59/SECOND_MEANING_PROTOCOL.md`.

## What R59 adds as a tool
`r59/blind/rk_solve.cpp` is a validated blind solver for running keys with an unknown English key: it passed a
pre-registered gate. Possible reuse:
- a running key after undoing a candidate transposition (K3 routes, columnar);
- other tableaux;
- testing a specific suspected key text, where it is much stronger than for an unknown one.

## Reproduce
1. **Corpus:** `python3 -I r59/corpus/build_corpus.py fetch RAW; build RAW OUT NLTK_DIR`. The pinned hashes are in the
   script.
2. **Model:** `lm_build OUT/train.txt lm6.bin 6`. Its sha256 must equal `r59/blind/LM_SHA256`.
3. **Solve:** `python3 -I r59/blind/run.py IN.tsv OUTDIR lm6.bin rk_solve`.
4. **Score:** `r59/sealed/gate.py` for the holdout, `r59/sealed/reveal_k4.py` for K4.
