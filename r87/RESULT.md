# R87 result (Claude Code, 20 Nov 2026): one stepping rotor with an unknown wiring is excluded for K4

## In plain words
**The rotor idea is ruled out.** We tested whether K4 could have been enciphered with a single scrambled wheel that
turns a notch every few letters (a Hebern-type rotor).
- **Search without the clues:** the solver first had to prove it could break such messages on 150 sealed practice
  messages. It broke 45 of 48 genuine rotor messages and was never fooled by 90 decoys.
- **K4 itself:** the solver found nothing better than what it finds in scrambled copies of K4.
- **Exact check with the clues:** this decides every possible wiring at once. **No setting of this kind of rotor can
  turn K4 into the 24 published plaintext letters**, even if one or two of them were wrong.

So K4 is not this cipher, under the stated assumptions. The search for the method moves to the next family.

## What was tested
- **Family RX** (`r85/DESIGN.md` §4; `r87/PREREGISTRATION.md`):
  - one rotor with any of the 26! wirings;
  - contacts numbered AZ, KRYPTOS, PALIMPSEST or ABSCISSA on each side (16 pairs);
  - a step of d = ±1 every n letters, in place.
- **Blind step:** n 1–32, 1,024 settings.
- **Exact step:** n 1–96, 3,072 settings. n ≥ 97 is a single alphabet, which L02 excludes.

## Sealed gate (fresh books; `r87/holdout/GATE.json`): **GO**
| Measure | Result | Bar |
|---|---|---|
| Positives recovered (≥ 95/97) and confident | **45/48** (39 exact; setting right 47/48) | ≥ 40 |
| By stratum S1 (n 1–4) / S2 (5–8) / S3 (9–16) / S4 (17–32) | 11 / 11 / 11 / 12 of 12 | ≥ 9 each |
| Plain / 2 letters changed | 24/24 / 21/24 | reported |
| Wrong-family negatives confident (9 generators, incl. two rotors) | **0/90** (max letter model −1.357, word −1.791) | ≤ 1 |
| One ciphertext letter wrong (reported) | 10/12 (misses at 84 and 94 letters, right setting) | — |

- **Misses:**
  - two confident decodes at 90 and 93 of 97 letters (scorer limits);
  - one search failure (S3, n 12).
- **Run:**
  - isolated sandbox, `audit/run_bounded.py`: COMPLETE, 841 s;
  - independent witness 750/750;
  - determinism 8/8;
  - freeze pushed (a0b2fa9) before the truth was opened;
  - truth sha256 equal to the commitment made before the run.

## K4 strict blind (`r87/k4/EVALUATION.json`): **NO_SIGNAL**
| Measure | K4 | Shuffles (100) |
|---|---|---|
| Best letter model per letter | **−1.419** (cut −1.30) | median −1.444, max −1.349; **22** at or above K4 (**p_family 0.228**) |
| Word model of that decode | −2.12 (cut −2.50) | 0 shuffles clear both cuts |
| Published letters matched by the best decode | **2/24** | — |
| Most matched by any frozen decode (top 5) | 3/24 | max 8; 56 shuffles reach ≥ 3 |
| Contenders (≥ 12/24) | 0 | — |

Raw best decode (ABS/AZ, n 16, d +1), unedited:
`EAYONELEFUNDASEDWELLKESBONNVBDTILLUSHSALCALLDBYYOFMANCHISFOSTERTHINGGRETISVUPSEWEBOILANMYMWMRNOWE`
It is not English. Scores like this are what the solver finds in shuffled copies of K4.

**Run:**
- isolated sandbox: COMPLETE, 557 s;
- independent witness 505/505;
- determinism 8/8 (K4, NULL_000–006);
- the sandbox kernel is identical to a clean compile;
- freeze `r87/k4/FROZEN.sha256` pushed in a204614 before `evaluate87.py` read any published letter. The remote blob of
  `RESULTS.jsonl` equals the local one.

## Post-freeze exact check (`r87/k4/EXACT.json`): **EXCLUDED**
| Check | K4 feasible settings (of 3,072) | Shuffles with any |
|---|---|---|
| EXACT: all 24 published letters | **0** | 0/100 |
| DROP: any one letter set aside (24 choices) | **0** | 0/100 |
| Extra, NOT pre-registered: any two set aside (276 choices) | **0** | not run |

Cross-checked on K4 with the second, separately written implementation (`EXACT_CROSSCHECK.json`); it agrees.

**Assumptions of the exclusion.**
- It is crib-assisted: the published letters are taken as right (up to one, or two, wrong), in place and in the
  carved order.
- DROP also covers one wrong **ciphertext** letter at a published position. Errors elsewhere do not enter the check.

## What this does and does not exclude
**Excluded exactly**, under the assumptions above: every single stepping rotor with any wiring, contacts numbered
AZ/KRYPTOS/PALIMPSEST/ABSCISSA on either side, and steps d = ±1 every n = 1–96 letters.
- That covers ChatGPT's R86 scope (AZ/AZ, n 1–4; PR #95, statistical NO_SIGNAL), now exactly.
- It also covers the structured n = 1 case of L21's open period-26 per-slot alphabets.

**Not excluded:**
- two or more rotors (odometer, SIGABA-like);
- stepping triggered by letters, or irregular stepping;
- other contact numberings (e.g. a keyed alphabet from another word);
- steps other than ±1 per move;
- transposition before or after the rotor;
- masking or nulls;
- non-English plaintext;
- more than two errors among the published letters.

**Next (as pre-registered):** RQ, a progressive Quagmire with one free alphabet (`r85/DESIGN.md` §5). It has the same
kind of decisive exact check and is nearly free to add.

## Review
**Independent review: NONE.** One model (Claude Code) built, ran and audited R87. The exclusion is recorded as
single-model and is not promoted (guardrail rule 10). A ChatGPT or human replay of `exact87.py` is the natural
independent check: it runs in 22 s.
