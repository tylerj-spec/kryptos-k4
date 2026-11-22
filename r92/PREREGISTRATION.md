# R92 pre-registration (Claude Code, 22 Nov 2026): the 192 boundary-phase single-rotor labels (RXP): sealed gate, then K4 strict blind, then a post-freeze exact check

**Label: STRICT BLIND, gate first.** R87–R90's isolation and freeze protocol applies unchanged:
- The blind solver runs in an isolated sandbox. It sees only an input TSV, the generic English scorers and the family
  code, with no network and no repository.
- Nothing about K4 is run until the sealed gate below says GO.
- The published letters are read only by `r92/sealed/evaluate92.py` and then `r92/sealed/exact92.py`. Both run after
  the frozen K4 outputs and their independent witness check are committed **and pushed**.

**Approval and source.**
- Tyler, 22 Nov 2026: "Can you refine these next steps then do the next round?" The standing approval is "You can merge
  code & do more in each run. Please try to get a legit solution for K4".
- The labels are Priority 2 of ChatGPT's work order (`audit/NEXT_STEPS.md`, PR #103). The multi-rotor review
  (`audit/backlog/multirotor/DESIGN.md`, "Phase caveat") found them outside R87's tested schedule.
- `audit/reviews/NEXT_STEPS_REFINEMENT_20261122.md` (this PR) proposes running them as one complete small round.

**Two departures from the work order, disclosed.**
1. **Review of the mode.** The work order says a K4 phase audit "needs its own reviewed mode, synthetic validation,
   registration and budget". This file is the registration and budget, and §G2 the synthetic validation.
   - The mode's review is single-model only: **Independent review: NONE** before K4.
   - Everything is frozen and pushed before any published letter is read, so ChatGPT can review afterwards without
     loss.
2. **Development budget.** The work order budgets the synthetic specification work at 180 s wall, 120 s CPU and
   512 MiB per development job.
   - The oracle and tests fit: `r92/tests/test_r92.py` runs in under 1 s.
   - The solver development run (§G2) is the same kind of job as R87–R90's. It used 993 s wall on 2 workers and
     about 2,600 MB aggregate memory, which is over that budget.

**Separation from RX2 (work order, binding).** Nothing from R92 enters the RX2-O solver work: no survivor, wiring,
ranking or score. R92's K4 result is a scope closure for these 192 labels only.

## G0. Hypothesis, scope and equivalent old models
**Hypothesis (family RXP, `r92/rotor92.py`).** K4 is ordinary English, enciphered in place by R87's single stepping
rotor, with a **step-boundary phase**.
- **Contacts:** numbered on the input side by alphabet E_in and on the output side by E_out. Each is one of AZ,
  KRYPTOS, PALIMPSEST or ABSCISSA (keyword first, then the rest of A–Z).
- **Wiring:** W is any of the 26! permutations. An initial angular offset is absorbed by W.
- **Stepping:** the rotor advances d = ±1 at the step boundaries s_i = d·⌊(i + r)/n⌋, with i counted from 0.
- **Encryption:** `E_out-place(c_i) + s_i = W[E_in-place(p_i) + s_i]` (mod 26), R87's equation with the new offsets.
- **Independent encipherer:** `r92/sealed/witness92.py`, standard library only.

**Scope: 192 labels.** 16 contact pairs × d ±1 × (n, r) in {(2,1), (3,1), (3,2), (4,1), (4,2), (4,3)}, each with a
free wiring. The blind search and the exact check cover the same 192.

**Schedule-equivalence accounting** (`test_r92.py` test 1):
- None of the 12 clocks (n, r, d) equals any R87 zero-phase schedule (n 1–96, d ±1) up to a constant. So none of these
  labels is absorbed by W into R87's excluded scope.
- The 12 clocks are distinct from each other up to a constant.
- **Synthetic phase oracle:** with n = 2 and r = 1, the time-dependent maps satisfy F0 ≠ F1 = F2. Every zero-phase
  schedule with n ≥ 2 has F0 = F1 (test 2).

**Equivalent and overlapping old models.**
- **R87 (L176):** the same rotor with r = 0, n 1–32 blind and 1–96 exact. It is excluded and does not overlap.
- **RX2-O (work order Priority 1):** a two-rotor odometer with W2 = identity embeds RX0. It does not embed RXP labels
  with r > 0, since the slow rotor's turnovers are not at these boundaries. RX2-O stays open; R92 says nothing about it.
- **Wider phase domains:** n ≤ 96 with every r gives 145,920 labels. They stay **deferred**, as the work order says.

**Prior exposure (R53 rule 5).**
- The 192 labels are ChatGPT's. The multi-rotor review derived them algebraically, from the RX2-D collapse, not from
  K4.
- **R87's K4 results were known before this pre-registration:** NO_SIGNAL, EXCLUDED for r = 0. They changed nothing
  here.
- The parameters are R87's, unchanged except for the seed. No published letter was used to choose anything.

**Cannot rule out:**
- other phases or periods;
- two or more rotors, letter-driven or irregular stepping;
- other contact numberings;
- transposition, masking or nulls;
- non-English plaintext;
- insertion or deletion errors.

A blind NO_SIGNAL is statistical and excludes no setting. The exact step excludes settings only under its stated
assumptions: the published letters right (up to one wrong letter for DROP), in place and in the carved order.

## G1. Sealed gate (fresh, genre-balanced books; before anything touches K4)
**Books.** Fresh Project Gutenberg texts (GITenberg mirror), none named anywhere in the repository and none in the
letter-model corpus. Headers are stripped (`--raw`).

| Role | Book | sha256 |
|---|---|---|
| G1 narrative | Franklin, Autobiography (#148, `b_148.txt`) | 683973e0555f19cb9cf41da3dedbb675f09320bc484c1a28836495b2e785cca9 |
| G2 formal / descriptive | Darwin, The Voyage of the Beagle (#944, `b_944.txt`) | 24b8d915eb5f61c091ee66403096bb3a950e3c0cb310caf086b6be0cc86781f1 |
| G3 technical | Taylor, The Principles of Scientific Management (#6435, `b_6435.txt`) | f44094afc0b9fb5b9f05fa991e8d51ba871be15a7f66ef3a63aceb3dde3c3e5b |
| Running keys for the RUNKEY negatives | Washington, Up From Slavery (#2376, `b_2376.txt`) | a5769b384951cf65f41950d4c181471c01474318eaffbe64aaceb91cb01fd776 |

**Items.** `r92/sealed/make92.py G1,G2,G3 KEY 920500 OUT --raw` gives **202** items, with shuffled ids:
- **48 RXP positives:** 6 clock cells × 8. Genres rotate, giving 16 per genre. Two per cell are masked (C→K, W→V),
  giving 12. Each has a random contact pair, direction and wiring.
- **4 extras:** two with one plaintext letter wrong, two with one ciphertext letter wrong. Reported only.
- **150 negatives**, 10 generators × 15:
  - two near-family decoys: **RX0** (R87's zero-phase rotor, n 2–4) and **RX2O** (ChatGPT's two-rotor odometer);
  - **RXN** (R87's rotor, n 5–32);
  - R89's RQ, periodic, running-key, substitution + transposition and PTAK;
  - R89's RCT;
  - English anagrams.

**Scoring.**
- *Best* is the decode with the highest letter-model score over all 192 settings.
- A positive is **ok** if its best decode has ≥ 95 of 97 letters equal to the enciphered text and is confident.
- *Confident* means letter model ≥ −1.30 and word model ≥ −2.50 per letter (R59's cuts).
- **Reported, not gated:** the setting recovered; the wiring agreeing on every contact the message used; exact
  recoveries; extras; each generator's best negative score.

**GO iff all of the following hold:**
- ok ≥ **42/48**;
- exact ≥ **36/48**;
- ≥ **6/8** in every clock cell;
- ≥ **13/16** in every genre;
- ≥ **8/12** masked;
- negatives confident ≤ **1/150**;
- the witness check passes.

On NO-GO: SOLVER_NO_POWER, **no K4 run and no exclusion**.

**Gate order** (each step a separate commit, pushed):
1. This pre-registration and `PROTOCOL.sha256`.
2. `QA_MANIFEST.json` (stage preregistered), `holdout/BLIND.tsv` and `holdout/TRUTH_SHA256`. The truth stays outside
   the repository and the sandbox.
3. The blind run (sandbox, through `audit/run_bounded_agg.py`), witness, determinism and `holdout/GATE_FROZEN.sha256`.
   Pushed.
4. Then the truth file and `holdout/GATE.json` (`gate92.py`, which checks the truth against the committed hash).

## G2. Development and checks done before this commit (spent books)
- **Development** (`r92/dev/DEV.md`; spent books, full gate size, seed 920300). Nothing was tuned.

  | Measure | Development | Bar |
  |---|---|---|
  | ok | **45/48** (44 exact) | ≥ 42 (exact ≥ 36) |
  | per cell | ≥ 7/8 | ≥ 6 |
  | per genre | ≥ 14/16 | ≥ 13 |
  | masked | **9/12** | ≥ 8 |
  | negatives confident | **0/150** (max −1.351, from RX0) | ≤ 1 |

  - The three misses are all masked: two scorer limits and one search failure, diagnosed by long anneals at the true
    setting.
  - Masked items have the smallest margin (9/12 against 8). The bar was not changed.
- **Tests** (`r92/tests/test_r92.py`, all pass):
  - round trips, and the witness encipherer equal to the reference on 400 random settings;
  - schedule-equivalence accounting, and the synthetic phase oracle (§G0);
  - the kernel's score equal to the quadgram score of `rotor92.decrypt`, and true-setting recovery;
  - three implementations of the exact check agreeing on 1,647 cases, and the one-error property;
  - witness failures on a changed letter, wiring, ciphertext letter, phase or best;
  - the holdout maker: counts, cells, genre balance, masks, generators, re-encryption, determinism;
  - the gate bars, and sandbox refusals.
- **Isolation:** 3 development items reproduce the open run **byte for byte** in the sandbox.
- **Letter model:** `lm6.v2.bin`, sha256 b1a2a3c7… (`r59/blind/LM_SHA256`).

## G3. K4 blind run (only after GO; each step a separate commit, pushed)
1. **Target.** `r92/sealed/prepare_k4.py` (R73's script, seed 920400) writes `r92/k4/TARGET.tsv`: K4 unchanged
   (sha256 2797de14…) plus **200** frequency-preserving shuffles.
2. **Run.** The same sandbox and runner as the gate (2 workers), started through `audit/run_bounded_agg.py`.
3. **Freeze.** `witness92.py` checks every stored decode, and `determinism92.py` re-runs the first 8 ids outside the
   sandbox. Then `r92/k4/FROZEN.sha256` lists the target, results, runner freeze, witness, sandbox record, code,
   resource log and letter-model hash. Commit and **push**.
4. **Evaluation** (`evaluate92.py`). Commit and push.
5. **Exact check** (`exact92.py`, G5). Commit and push.

No tuning, re-running, re-ranking or filtering of blind outputs after the evaluation.

## Decision rules (fixed now; R84/R87 rules)
"Best" is the letter-model maximum over all 192 settings, for K4 and every shuffle alike.

| Outcome | Condition |
|---|---|
| **CONFIDENT** | K4's best clears −1.30 / −2.50 **and** is above every one of the 200 shuffles' bests |
| **SIGNAL** | CONFIDENT and ≥ 10/24 published letters |
| **SCORE_ANOMALY** | CONFIDENT without that |
| **NO_SIGNAL** | Otherwise |
| **p_family** (reported) | (1 + shuffles with best ≥ K4's) / 201 |
| **Contender** (raw; not a solution) | Any frozen K4 decode (top 5) with ≥ 12/24 |

## G5. Post-freeze exact check (crib-assisted, exclusion-only)
`exact92.py` runs on K4 and the 200 shuffles after the evaluation. For each of the 192 settings it asks whether some
wiring maps all 24 published positions correctly: the (input contact, output contact) pairs must form a partial
bijection. checks = positions − distinct inputs.

| Screen | Assumes | Labels |
|---|---|---|
| **EXACT** | all 24 published letters right | EXCLUDED if K4 has no feasible setting; LEAD if K4 has one with ≥ 3 checks and no shuffle reaches K4's maximum; otherwise CHANCE |
| **DROP** | each published letter set aside in turn | the same labels |

The offsets depend on the position only, so one wrong letter of **either** kind at a published position changes
exactly one pair (`test_r92.py` test 4). DROP therefore covers one wrong published plaintext letter and one wrong
ciphertext letter at a published position. An error elsewhere does not enter the check.

The exact step decrypts nothing. It never changes the blind verdict and is never used to choose a blind search.

## What follows (fixed now)
| Result | Next |
|---|---|
| **SIGNAL** | Stop; report raw. R87's proof steps. **No external submission without Tyler's go** |
| **SCORE_ANOMALY or a contender** | Report raw; not a solution |
| **NO_SIGNAL with EXACT and DROP EXCLUDED** | Ledger: RXP's 192 labels **EXCL (exact, crib-assisted)**, with blind STAT. Together with L176 this closes R87's rotor at every boundary phase for n ≤ 4. Next: RX2-O solver development (work order Priority 1), unaffected by this result |
| **NO_SIGNAL, EXACT or DROP not EXCLUDED** | Ledger: STAT NO_SIGNAL; feasible settings listed with their counts only. They may **not** set the scope of any blind search or enter RX2 |
| **NO-GO** | SOLVER_NO_POWER; no K4 run |

**Prior expectation:** NO_SIGNAL and EXCLUDED. R87's exact check found no feasible setting for r = 0, and random
ciphertexts almost never pass.

## G4. Review
**Independent review: NONE.** One model (Claude Code) is builder, breaker and auditor here. That does not count as
independent review (guardrails G4 and rule 10). No `Promotes:` line will be written without one.

## Budget (`QA_MANIFEST.json`; enforced by `audit/run_bounded_agg.py`)
- **Limits:** 2 h wall per run, **4 GB aggregate** resident memory over all workers, **28,800 s aggregate CPU**.
- **Workers:** 2, since each worker holds the letter model (R90 Amendment 1).
- **Candidates:** at most 1,005 kept K4 candidates (201 × 5).
- **No retries.**
- **Expected:** about 17 minutes per run (development: 202 items in 993 s on 2 workers).
