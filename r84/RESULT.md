# R84 result: R80a's two-keyword-stage families on K4, strict blind (Claude Code, 17 Nov 2026)

**Outcome: NO_SIGNAL.** These families show no sign of K4. Nothing here is a candidate, and nothing was sent to any
outside checker.

## In plain words
- The solver had shown it can find this kind of cipher: 75 of 80 hidden test messages recovered exactly, and none of
  100 decoys marked as a hit.
- It also still works with one ciphertext letter wrong: 12/12.
- On K4 its best answer is gibberish. It scores no better than on randomly shuffled copies of K4: 60 of 100 shuffles
  did as well or better.

So K4 is very unlikely to be ordinary English under two keyword stages of this kind with a free key of up to about 7
letters, where the test is strongest. It is somewhat less unlikely for free keys of 8–12 letters.

## Numbers (`r84/k4/EVALUATION.json`; rules fixed in `r84/PREREGISTRATION.md`)
| Measure | K4 | 100 shuffles |
|---|---|---|
| Best letter model, over all four families (cut −1.30) | −1.570 | median −1.564, max −1.476; 60 at or above K4 → **p_family 0.60** |
| Its word model (cut −2.50) | −2.37 | — |
| Clears both cuts | no | 0 of 100 |
| Published letters matched by the best decode (SIGNAL needs ≥ 10) | 4/24 | — |
| Most matched by any frozen decode (contender bar 12) | 4/24 | max 7/24; 42 shuffles reach ≥ 4 |
| Contenders | 0 | — |

**Per family (K4's best):**

| Family | Letter model | Word model | Published letters | Listed key | Free key |
|---|---|---|---|---|---|
| L1 | −1.570 | −2.37 | 4 | ASSIGNMENT | QQQOLZSPJTWX |
| L2 | −1.632 | −2.66 | 4 | MARYA | VOFAHSOPVHFM |
| X1 | −1.630 | −2.42 | 2 | IWD | ULDGVEGLXRG |
| X2 | −1.615 | −3.12 | 2 | CRS | YSMPUACLCIE |

Every family's best uses an 11- or 12-letter free key, the longest allowed. That is where free letters can best fit
noise.

**Raw best decode, unedited** (L1, KRY/KRY/AZ/KRY, VIG, ka KRY, free-stage sign −1):
`DCHTAYPITBRACETOOBADEBSBBTOSACOWTTHEFATEISFRIESLEFEVEKENPASELOCAPTOSNTLEGOLIJHEWOTGTULYNOADIVISRE`.
Fragments such as "TOO BAD", "THE FATE IS" are optimiser-filled. Under the working rules they are not evidence.

## Quality controls (all done; details in the pre-registration)
| Control | Result |
|---|---|
| Gate (R80a, sealed, fresh books) | All four families PASS; 0/100 negatives confident |
| Solver reproduces its archived holdout output in the sandbox | Byte for byte |
| Letter model rebuilt from pinned sources | Hash equal (b1a2a3c7…) |
| One-ciphertext-letter-error diagnostic (synthetic, before K4) | 12/12 recovered, 96/97 each |
| Isolation | Separate mount and network namespace. The repository, the published letters, the scratchpad and `/root` were invisible; no network. 12 allowlisted files, hash-checked; tripwire clean |
| Independent witness check (stdlib, no solver code) | 909/909 stored decodes re-encipher exactly |
| Freeze pushed before the evaluation | 7701b3f, then the evaluation |
| Bounded run | COMPLETE: 7,016 s of 14,400; 1.24 GB of 4 GB |
| Determinism | The aborted first launch's 8 outputs (Amendment 2) are byte-identical to the full run |
| Amendments | 1: a one-line crash fix in the diagnostic script. 2: the first launch was stopped before the background-shell limit and relaunched detached; no output was read |

## What this closes and what it does not
- **STAT, NO_SIGNAL** (not an exclusion) for:
  - families L1/L2 (listed word at phase 0, 28,943 words) and X1/X2 (any 1–3-letter key);
  - a free key of 1–12 letters;
  - AZ/KRY alphabets, VIG/BEAU/VARB, both orders, in place, English plaintext.
- **Informative** for free keys ≤ 7 (gate 53/53). Weaker for 8–10 (22/27) and 11–12 (12/16).
- Robust to one ciphertext error.
- **Not covered:**
  - listed keys at other phases;
  - PALIMPSEST/ABSCISSA;
  - words outside the list;
  - free keys ≥ 13;
  - both keys free;
  - transposition;
  - masking;
  - non-English plaintext.
- Most of this ground was already excluded exactly by F1X (L165). The new ground is a blind, crib-free confirmation
  and F1X's 9 low-check cells. Both come out negative.

**Independent review: NONE.** One model did this work.

## Scope independence (added 18 Nov 2026, after review)
- R84's search scope is **R80a's own pre-registered scope, unchanged**: all four families, listed words at phase 0,
  1–3-letter keys, free keys 1–12, all 96 conventions (`r80a/PREREGISTRATION.md`, d31202e, fixed before R80a's
  holdout existed).
- **No key length, convention or setting was selected or removed using the crib-assisted F1X results (L165)** or any
  other published-letter result. F1X is cited in the pre-registration only as prior context, to say what a
  negative would add.
- So R84's blind NO_SIGNAL stands on its own. Crib-assisted exclusions may be applied to it only after the freeze, as
  separate evidence.
