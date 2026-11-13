# R81a result: R79's families on the PALIMPSEST and ABSCISSA alphabets, new position rules, and two checks (Claude Code, 13 Nov 2026)

**Outcome: NO_SIGNAL.** No family gives a readable K4 decode. The check of the frozen blind work finds no setting
consistent with the published letters, exactly or with one letter set aside, in the four R81a families or R79's four
keyword families. G5X_SUMMARY

Pre-registered in `r81a/PREREGISTRATION.md` (commit 9f69f61, `r81a/PROTOCOL.sha256`).
- Candidates came from the ciphertext only. The blind run was frozen and pushed before any published letter was read.
- The published letters were used only as a check. Nothing was fitted to them.
- Nothing was sent to any outside checker.

## Steps
| Step | Commit | Result |
|---|---|---|
| Build, unit tests (`r81a/tests/test_r81a.py`) | 9866671, 2b4e8d0 | All pass |
| Development check on spent books (`r81a/results/DEV.json`) | 9f69f61 | 24/24 confident (21/24 at 95 letters, all at 85); 8/8 STRETCH; 0/26 negatives confident, best −1.50 |
| Pre-registration (cuts −1.30 / −2.50; recovered bar 85/97) | 9f69f61 | — |
| Sealed holdout, 196 ciphertexts (seed 810300; truth sha256 4850b73b…) | a65c599 | — |
| Holdout blind run, freeze | 31397a4 | — |
| Verify and gate (`r81a/holdout/GATE.json`) | b600cf1 | 1,764 witnesses re-encrypt; **all four families PASS** |
| K4 target: K4 + 100 shuffles (seed 810400) | 4ca79b8 | — |
| K4 blind run, all four families, with every setting's frozen blind score; freeze | fa745a0 | — |
| Verify (`r81a/k4/VERIFY.json`) | 689212a | 934 witnesses re-encrypt |
| Sealed reveal (`r81a/k4/REVEAL.json`) | 81c99bf | **NO_SIGNAL** |
| Check of the frozen blind work, exact and drop-one (`r81a/k4/VALIDATE.json`) | 2075f6b | 0 consistent settings in all eight families, on K4 and on 10 shuffles |
| Power control for that check (`r81a/k4/CONTROL_VALIDATE.json`; added after it) | 2075f6b | 48/48 |
| G5X exclusion check (`r81a/k4/G5X.json`) and its power control (`r81a/k4/CONTROL_G5X.json`) | this PR | G5X_STEP |

## Sealed gate (fresh books: *Silas Marner*, *Main Street*; negatives from *The Secret Garden*, *Howards End*)
| Family | Settings per ciphertext | Recovered and confident (bar 18/20) | Exact | ≥ 95 letters | Misspelled | Nonstandard spelling | STRETCH (11–12 letters) | Best negative (letter model) |
|---|---|---|---|---|---|---|---|---|
| H7CT_A | 41,472 | **20/20** | 18 | 19 | 6/6 | 4/4 | 4/4 | −1.55 |
| LIB_A | 512,448 | **20/20** | 19 | 20 | 6/6 | 4/4 | 4/4 | −1.46 |
| LIB_G4 | 168,000 | **20/20** | 17 | 19 | 6/6 | 4/4 | 4/4 | −1.55 |
| PROG_A | 1,123,200 | **20/20** | 20 | 20 | 6/6 | 4/4 | 4/4 | −1.45 |

**Positives.** 80/80 recovered and confident.
- The weakest such decode scores −1.14 (letter model) and −1.89 (word model).
- Six decodes are not exact. All six read as English, with 85–96 of 97 letters right.
  - Two were decoded by a neighbouring family (a LIB_A rule for an H7CT_A plant): the same keyword expressed by a
    slot rule.
  - The 85-letter one is a LIB_G4 plant decoded by a near-identical LIB_G4 rule.
- STRETCH (reported only): 16/16 confident, 14 exact; the other two have 93 and 86 letters right (LIB_G4).

**Negatives.** 0/100 confident.
- The best is −1.45 (Gromark). Every wrong-family generator stays between −1.45 and −1.56.
- The best word-model score is −2.16.

## K4 (blind run, then reveal)
**Outcome: NO_SIGNAL.**
- K4's best decode scores −1.587 (letter model) and −3.16 (word model). The cuts are −1.30 and −2.50.
- 64 of the 100 shuffles score at or above it. The shuffles' median best is −1.58 and their maximum −1.52.
- The best decode matches 1/24 published letters. Every shuffle's best matches at most 5.

Best decode of each family, raw:

| Family | Letter model | Word model | Published letters | Setting | Decode |
|---|---|---|---|---|---|
| PROG_A | −1.587 | −3.16 | 1 | outer, A1 = KRY, a = 16, b = 24, pa PAL, ca AZ, ka AZ, BEAU, key AKYHCSSPQGTF (12) | `PUITYMONSBEENCHABUOISXSETSIZERISTWORESREMCHUGIENWWREMITELERIMPENGMOSHSUDMOUINEAGEFULADSSXIRRUFFCC` |
| LIB_G4 | −1.599 | −2.63 | 2 | ROT d = 5, m 12, feedback lag 3, pa ABS, ca KRY, ka KRY, BEAU, key FNNOGUGHEYJL | `FKTHAPPICLAMBSASTHATGOWHENTLLECWAVEINNDISKSAARADNUKYTENVOHANFILMDRKHBUWISMARENADONSORGCMIRHEYRNUL` |
| H7CT_A | −1.609 | −2.74 | 1 | pa ABS, ca AZ, ka AZ, VARB, feedback lag 11, key ACVJJBRZJHLB (12) | `NCDACONMONDASIANDCEELEFTMEWEDOYDEJPOLKARDXTHDDCWOREBHICEBEEDMADERJOASORTUMIMBEHONORTRIKEAUNLWTPHX` |
| LIB_A | −1.618 | −2.57 | 1 | keyword restarts after each ciphertext V (TRIG), m 12, no stream, pa AZ, ca ABS, ka AZ, BEAU, key VTCDYITTEJMA | `GSRLETWEWASOURNRUBSSICAIAECMLKAIRCUTECCATHGRNTKNEVASSMOOPENIMOSOFINCAPERSIXWEBBYASATELIKASABNRAYQ` |

- Every family's best uses the largest keyword allowed (12 letters). That is what free key letters fitted to noise
  look like.
- **Theorem K** (reported only): log10 settings = 22.21. The cut at 10⁻⁶ expected false alarms is −1.124 against a
  uniform null and −0.914 against shuffles. K4's best is far from either.

## Check of the frozen blind work (after the freeze and reveal; crib-assisted, as in R70 Erratum 1; never a blind discovery)
Every setting of the four R81a families and of R79's four keyword families, keyword 1–12 letters.

| Family | Settings | K4: exact | K4: drop-one (G6) | 10 shuffles |
|---|---|---|---|---|
| H7CT_A | 41,472 | 0 | 0 | 0 each |
| LIB_A | 512,448 | 0 | 0 | 0 each |
| LIB_G4 | 168,000 | 0 | 0 | 0 each |
| PROG_A | 1,123,200 | 0 | 0 | 0 each |
| R79 H7CT | 13,824 | 0 | 0 | 0 each |
| R79 H7TXT | 774,720 | 0 | 0 | 0 each |
| R79 LIB | 170,816 | 0 | 0 | 0 each |
| R79 PROG | 374,400 | 0 | 0 | 0 each |

- A keyword of at most 12 letters puts the 24 published positions into at most 12 slots, so every setting has at
  least 12 checks; with one letter set aside, at least 11. None is consistent.
- So no setting was flagged, and there was no flagged blind decode to replay.
- **Exact, crib-assisted exclusion** of every setting of these eight families as defined, also allowing any one
  published letter to be wrong (G6).
  - It assumes the published letters sit at those plaintext positions, the cipher works in place, and the carving is
    correct (the ledger's standing assumptions).
  - It does not rest on the solver: it holds for any keyword letters.
- **Power control** (`r81a/sealed/control_validate81.py`, seed 810500; synthetic only; added after the K4 check, so
  reported, not pre-registered). Three plants per family, keyword 2–12:
  - the planted setting is flagged exactly in 24/24;
  - with one published letter wrong, it is flagged by drop-one at that position in 24/24.

## G5X: one unknown keyword alphabet (after the reveal; crib-assisted exclusion check)
G5X_SECTION

## What follows (pre-registered row)
G5X_FOLLOWS

**Not covered:**
- keywords of 13 or more letters;
- two unknown alphabets at once, or an unknown key-numbering alphabet with PAL or ABS on the main sides (R81a ran
  those sides with ka AZ or KRY only);
- PROG_A's progressive mask on alphabets other than the four named;
- rules outside R79's library and R81a's ROT, ALT, RESTART and SPLIT;
- plaintext-driven variants (G2), the self-progressing keyword (G3) and the rest of r77 H7 (R81b);
- two keyword stages on different tableaux (R80, after its synthetic gate R80a).

**Next (Tyler's call):** R80a, the synthetic gate of the two-stage solver (`r80/FABLE_IDENTIFIABILITY.md`), or
R81b.

**Limitations.**
- The recovered bar was lowered from R79's 95 letters to 85, before the holdout existed, because R81a's rules overlap
  (`r81a/PREREGISTRATION.md`). The gate also reports 95 letters: 78/80.
- The plants use random keywords. A real keyword would only be easier to read.
- The two power controls were added after the K4 checks returned zero. They use no K4 ciphertext and change no frozen
  result.
