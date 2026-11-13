# R79 result: H7, the state-rule library with the walking key, a progressive mask, and the rest of H11 (Claude Code, 13 Nov 2026)

**Outcome: NO_SIGNAL.** No family gives a readable K4 decode. The crib-assisted validator finds no setting of the four
keyword families consistent with the published letters.

Pre-registered in `r79/PREREGISTRATION.md` (commit 9439b1a, `r79/PROTOCOL.sha256`). Nothing was sent to any outside
checker.

## Steps
| Step | Commit | Result |
|---|---|---|
| Build, unit tests (`r79/tests/test_r79.py`) | b285bd8 | All pass |
| Sealed scripts | 6880528 | — |
| Development check on spent books (`r79/results/DEV.json`) | 9439b1a | 30/30 positives, 8/8 STRETCH, 0/26 negatives confident; best negative −1.53, weakest positive −1.09 |
| Pre-registration (letter-model cut −1.30, from the development check) | 9439b1a | — |
| Sealed holdout, 216 ciphertexts (seed 790300; truth sha256 60a6e742…) | 572c77f | — |
| Holdout blind run, freeze | 99dbd07 | — |
| Verify and gate (`r79/holdout/GATE.json`) | 4fb7c1b | 2,160 witnesses re-encrypt; **all five families PASS** |
| K4 target: K4 + 100 shuffles (seed 790400) | 6f9c000 | — |
| K4 blind run, all five families, freeze | 72b2c2d | — |
| Verify (`r79/k4/VERIFY.json`) | e8328c2 | 1,035 witnesses re-encrypt |
| Sealed reveal (`r79/k4/REVEAL.json`) | f9c5530 | **NO_SIGNAL** |
| Crib-assisted validator (`r79/k4/VALIDATE.json`) | this PR | Keyword families: 0 consistent settings; H11: chance level |

## Sealed gate (fresh books: *Lord Jim*, *A Room with a View*; negatives from *My Ántonia*, *Ethan Frome*)
| Family | Settings per ciphertext | Recovered and confident (bar 18/20) | Exact | Misspelled | Nonstandard spelling | STRETCH (11–12 letters) | Best negative (letter model) |
|---|---|---|---|---|---|---|---|
| H7CT | 13,824 | **19/20** | 19 | 5/6 | 4/4 | 4/4 | −1.56 |
| H7TXT | 774,720 | **20/20** | 20 | 6/6 | 4/4 | 4/4 | −1.53 |
| LIB | 170,816 | **20/20** | 19 | 6/6 | 4/4 | 4/4 | −1.55 |
| PROG | 374,400 | **20/20** | 20 | 6/6 | 4/4 | 3/4 | −1.53 |
| H11 | 1,176,592 | **19/20** | 14 | 5/6 | 4/4 | — | −1.82 |

**Positives.**
- 98/100 recovered and confident. The weakest such decode scores −1.13 (letter model) and −1.81 (word model).
- **The two misses read as English.**
  - An H11 plant came back with 85/97 letters right; some cycles chose the wrong closing letter.
  - An H7CT plant came back with 94/97; a LIB setting gave a slightly different text.
- STRETCH plants, reported only: 15/16. The miss was a PROG plant with a 12-letter keyword (3/97).
- H11's exact count (14/20) is below its recovered count because single-letter and two-letter cycles can close in
  more than one way (r78 §1.6).

**Negatives.** 0/100 confident.
- The best is −1.53 (RUNKEY); every wrong-family generator stays between −1.53 and −1.56.
- The best word-model score is −2.13.

## K4 (blind run, then reveal)
**Outcome: NO_SIGNAL.**
- K4's best decode scores −1.554 (letter model) and −2.62 (word model). The cuts are −1.30 and −2.50.
- 11 of the 100 shuffles score at or above it. The shuffles' median best is −1.58 and their maximum −1.52.
- The best decode matches 2/24 published letters. Every shuffle's best matches at most 7.

Best decode of each family, raw:

| Family | Letter model | Word model | Published letters | Setting | Decode |
|---|---|---|---|---|---|
| PROG | −1.554 | −2.62 | 2 | inner, A1 = PAL, a = 18, b = 18, pa KRY, ca AZ, VIG, key TGHFJIXSJCDM (12) | `LDYOUARTNRGOBROISDIHYUDANDOPEXXPHPPIDMCUSEPINGTELLITANUGHRUTGALPICHONYOUTASIDYETBTHYTAUSTIPEDESAR` |
| H7CT | −1.585 | −2.54 | 3 | KRY/KRY/KRY, BEAU, feedback lag 25, key EVUHSWNCXASR (12) | `SHUGEMUTENEDPJJWLEERRUIKIACESZEAWHIMOKAGAMZEUTNNIEEMCALFCSILVALIDDLEKKAHANOOFWESTSTHEYARETIDLEINV` |
| H7TXT | −1.606 | −2.74 | 0 | AZ/AZ/AZ, VARB, K1–K3 plaintext from offset 291 forward, key JUXFZWOOGDAE (12) | `TOOELGLUTSMAKEECLTHPIMIOLSENONCEFORBLERBAROLDLRHAYDARUCKSVOUTOMAKEOPUTRNASGOUTBCSTULMEUSEISDOAFIG` |
| LIB | −1.616 | −3.00 | 4 | REV at E, m 12, feedback lag 1, AZ/KRY/KRY, BEAU, key WFTFLMAKBNKD | `SJMLXIOTASTOGOFATVLATEVACOEDTANNCTBLEFOAHOVADLISTCHANTWEDIRANTIBOJHLIMAFAPHWAUBUCOORMORREDOFSERMD` |
| H11 | −1.872 | −3.79 | 0 | route colall:C4:0312/F0S0O0V1/fwd, pa AZ, ka KRY, ca KRY, VARB | `SOOPWALKRYECRYNKWARDUNSYCLWQHWXPANELNEERBSDMMTKQCMJDECACCCZYDGAUTGQGOSIMGJDOUZPERDSTHRGGHSYOSCLOG` |

- Every family's best uses the largest keyword allowed (12 letters) or, for H11, sits at the bottom of the range.
  That is what free key letters fitted to noise look like.
- **Theorem K** (reported only): log10 settings = 22.05. The cut at 10⁻⁶ expected false alarms is −1.126 against a
  uniform null and −0.916 against shuffles. K4's best is far from either.
- **H11's ciphertext-only cycle filter** (descriptive; not a pre-registered test):
  - K4 has 107,452 settings whose cycles all close; the shuffles have 104,928–118,852 (median 111,818).
  - K4 is second lowest of 101.
  - Fewer closing cycles is, if anything, evidence against H11.

## Crib-assisted validator (after the freeze; labelled as in R70 Erratum 1; never a blind discovery)
| Family | K4: settings consistent with the 24 published letters | 10 shuffles |
|---|---|---|
| H7CT | 0 of 13,824 | 0 each |
| H7TXT | 0 of 774,720 | 0 each |
| LIB | 0 of 170,816 | 0 each |
| PROG | 0 of 374,400 | 0 each |
| H11 (3+ exact checks) | 1 (KRY/AZ/AZ/VARB, 3 checks) | 0, 3, 0, 2, 0, 2, 1, 0, 0, 0 |

- **Keyword families.** A keyword of at most 12 letters puts the 24 published positions into at most 12 slots, so
  every setting has at least 12 checks. None is consistent.
  - This is an exact, crib-assisted exclusion of every setting of H7CT, H7TXT, LIB and PROG as defined.
  - It assumes the published letters sit at those plaintext positions, the cipher works in place, and the carving
    is correct (the ledger's standing assumptions).
  - It does not rest on the solver: it holds for any keyword letters.
- **H11.** Only positions whose key position is also published give checks. K4's one consistent setting is at the
  shuffles' level (mean 0.8). Most routes give 3 or fewer checks, so H11 is not decided by the published letters.

## What follows (pre-registered row)
"Everything negative": the five families are closed in the stated scope.

**Closed scope:**
- H7CT, H7TXT, LIB and PROG: blind, STAT (gate passed). They are also excluded exactly, crib-assisted, for
  keywords of 1–12 letters with these alphabets, streams and rules.
- H11's open conventions: blind, STAT, over the 73,537 listed routes.

**Not covered:**
- keywords of 13 or more letters;
- keyword alphabets other than A–Z and KRYPTOS on the plaintext, key and ciphertext sides (PALIMPSEST and ABSCISSA
  appear only as the progressive alphabet and as H11's ciphertext alphabet);
- other stream texts;
- rules outside the library;
- the plaintext-driven walking key and plaintext feedback (deferred);
- routes outside the list (H11).

**Next:** LAYERSOLVE, two keyword stages on different tableaux with unknown keywords (`r78/FABLE_MASKING.md` §B7),
with its own pre-registration and gate.

**Limitations.**
- The R79 letter-model cut (−1.30) was set from the development check, before the holdout existed, because these
  families raise the negatives' ceiling to about −1.53. The holdout confirmed it: the best negative was −1.53 and
  the weakest recovered positive −1.13.
- The plants use random keywords. A real keyword would only be easier to read.
