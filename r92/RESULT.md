# R92 result (Claude Code, 22 Nov 2026): the 192 boundary-phase single-rotor labels are excluded for K4

## In plain words
**R87's rotor is now closed at every step-boundary phase for n ≤ 4.**
- R87 (L176) tested one stepping rotor with a secret wiring that advances every n letters, starting at a step
  boundary.
- ChatGPT's multi-rotor review found the gap: the rotor could also step part-way through its first period (phase
  r). Those 192 settings with n ≤ 4 were never tested.
- R92 tests exactly those, with R87's solver and the full strict-blind protocol.

**Results:**
- **Practice:** the solver broke 47 of 48 sealed practice messages from four new books and was fooled by none of
  150 decoys. The decoys included R87's rotor and a two-rotor machine.
- **K4, blind:** nothing better than in scrambled copies of K4.
- **K4 against the clues:** no setting and no wiring produces the 24 published letters, even allowing one wrong
  letter of either kind at a published position.

## Sealed gate (fresh books; `r92/holdout/GATE.json`): **GO**
| Measure | Result | Bar |
|---|---|---|
| ok (≥ 95/97, confident) | **47/48** (44 exact) | ≥ 42 (exact ≥ 36) |
| Per clock cell (n2r1, n3r1, n3r2, n4r1, n4r2, n4r3) | 8, 8, 8, 8, 8, 7 of 8 | ≥ 6 |
| Per genre (narrative / descriptive / technical) | 15 / 16 / 16 of 16 | ≥ 13 |
| Masked (C→K, W→V) | 11/12 | ≥ 8 |
| Negatives confident (10 generators, incl. RX0 and RX2O) | **0/150** (max letter model −1.350, from PTAK) | ≤ 1 |
| Setting recovered / wiring right on every used contact (reported) | 48/48 / 44/48 | — |
| Extras: one plaintext or ciphertext letter wrong (reported) | 4/4 | — |

The one miss (H_000, n4r3, masked) is a confident partial decode at 93/97, with the true setting. The near-family
decoys stay well under the cut:
- RX0 (R87's zero-phase rotor): −1.396;
- RX2O (two-rotor odometer): −1.421.

**Run:**
- isolated sandbox through `audit/run_bounded_agg.py`: COMPLETE, 966 s, 1,906 s CPU, aggregate peak 2,564 MB with
  2 workers;
- witness 1,010/1,010;
- determinism 8/8;
- freeze pushed (92ba8ed) before the truth was opened. The truth's sha256 matches the hash committed before the run.

## K4 strict blind (`r92/k4/EVALUATION.json`): **NO_SIGNAL**
| Measure | K4 | Shuffles (200) |
|---|---|---|
| Best letter model per letter | **−1.431** (cut −1.30) | median −1.450, max −1.343; **50** at or above K4 (**p_family 0.254**) |
| Word model of that decode | −2.52 (cut −2.50) | 0 shuffles clear both cuts |
| Published letters, best decode / any frozen decode | **0/24** / 2/24 | shuffles' frozen max 8; 189 reach ≥ 2 |
| Contenders (≥ 12/24) | 0 | — |

Raw best decode (PALIMPSEST / AZ contacts, n 4, r 3, d +1), unedited. It is not English:
`CKODAALAISFERNTHEILLTGOBETTHOUAITISTOOSEKANNEBEERBUTANOCELIZAGTFRNROOMSWABYFALSIAARIEUFTSPOPKTOPR`

**Run:**
- COMPLETE, 1,022 s, 2,013 s CPU, aggregate peak 2,563 MB;
- witness 1,005/1,005;
- determinism 8/8;
- freeze `r92/k4/FROZEN.sha256` pushed in 25026ff before any published letter was read. The remote results blob
  equals the local one.

## Post-freeze exact check (`r92/k4/EXACT.json`): **EXCLUDED, EXACT and DROP**
| Screen | K4 feasible settings (of 192) | Shuffles with any |
|---|---|---|
| EXACT: all 24 published letters right | **0** | 0/200 |
| DROP: each published letter set aside in turn (one wrong letter of either kind at a published position) | **0** at every one of the 24 positions | 0/200 |

- **Cross-check:** `rotor92.exact_check`, a second implementation, agrees on every EXACT and DROP count
  (`EXACT_CROSSCHECK.json`).
- **Resources:** 4.0 s under the aggregate wrapper (`EXACT_RESOURCE_LOG.json`).
- No random shuffle passes either. The screen excludes; it cannot rank K4 against chance.

## What this does and does not exclude
**Excluded exactly** (crib-assisted: the published letters right, or one of them wrong, in place and in the carved
order): every RXP setting in scope, with any wiring.
- The 16 contact pairs over AZ, KRYPTOS, PALIMPSEST and ABSCISSA.
- d ±1, with (n, r) in {(2,1), (3,1), (3,2), (4,1), (4,2), (4,3)}.

**With L176**, R87's single rotor is excluded at every boundary phase for n ≤ 4, and at phase 0 for n ≤ 96.

**Not excluded:**
- boundary phases for n 5–96 (145,920 labels; deferred by the work order);
- two or more rotors, including RX2-O, whose solver development stopped without power (below);
- letter-driven or irregular stepping;
- other contact numberings;
- transposition, masking or nulls;
- non-English plaintext;
- insertion or deletion errors.

**Separation from RX2.** Nothing from R92 entered the RX2-O work, as the work order requires: no survivor (there are
none), no wiring, no ranking.

## The other work in this PR: RX2-O solver development stopped (`audit/backlog/multirotor/solver/RESULT.md`)
Work order Priority 1 gave the RX2-O solver three development versions, on spent data only. **All three failed, so
it stops: SOLVER_NO_POWER on development data.** No full gate and no K4 run follow. RX2-O stays **OPEN**.
- **v1:** INCOMPLETE. The letter model could not be mapped under the 2,048 MiB per-process limit, and no output was
  written.
- **v2:** 0/48. The quadgram objective is fooled: in 16/48 plants it finds non-English decodes scoring above the
  truth.
- **v3:** 0/48 with an order-5 letter-model objective. That objective now ranks the truth above every found decode in
  47/48 plants, but the search never reaches it.

Joint random-start annealing of two free wirings does not work on 97 letters, even with the structure supplied and
no slow-rotor turnover.

## Review
**Independent review: NONE.** One model (Claude Code) built and ran R92 and the RX2-O development.
- The pre-registration discloses two departures from the work order: the mode was reviewed by one model only, and the
  solver development run was over the synthetic-job budget.
- The natural independent checks are:
  - a replay of `exact92.py`, which takes seconds;
  - a separate partial-bijection implementation over the 192 settings.
