# Low-power nulls: where a "no signal" is informative (T7, audit/NEXT_STEPS.md), 15 Nov 2026

Documentation only; no status changed. A row is listed here if its K4 result is NO_SIGNAL, STAT, WEAK or no
candidate, **and** its synthetic gate failed, was not run, or passed on only part of the parameter range. Ranges are
taken from the rows and their RESULT files as cited. The sample sizes behind them are often small (3–6 plants per
stratum), so "informative" means "the solver was shown able to find the truth there", not a measured power level.

**These are the families a future search may legitimately revisit**, in the uninformative ranges only. An exact
(crib-assisted) exclusion in the same row is separate, and stands or falls on its own scope.

| Row | What the gate showed | Null informative for | Not informative for (open to revisit) | Exact check in the same row |
|---|---|---|---|---|
| **L136** R42, free cipher alphabet, in place | Pre-registered gate FAILED, 4/6 #1. C10b5 plants 3/3; K1K3 plants 1/3: two true settings fell just below the stage-1 cutoff | Blind: C10b5 keys (3 plants) | Blind: K1–K3 running keys with a free cipher alphabet | EXCL for any cipher alphabet over C10b5–7, CARTER, K1K3 (171 M settings), independent of the gate. A blind revisit adds little in place |
| **L157** R68, keyed ciphers along carved paths | Gate PER 5/6, GRO 6/6, CTAK 6/6, PTAK 4/6. Development: PTAK solved for L 2–12, failed for L ≥ 14; PER only partly solved at p ≥ 12 | GRO; CTAK L ≤ 24; PER p ≤ ~11; PTAK L ≤ 12 | **PTAK (plaintext autokey along a path) L 13–24 blind**; PER p 12–20 blind | GRO EXCL; PER EXCL p ≤ 25; CTAK EXCL L ≤ 71; PTAK only 1–2 checks (38 survivors, nulls median 46), so PTAK is effectively open beyond L 12 |
| **L153** R64, World Clock / German running key then a route | CLOCK_RAND 6/6, CLOCK_RING 6/6, GERMAN_EP 6/6, GERMAN_LIT 2/6 (low power) | Clock keys; Europarl-style German keys | **Literary (1910s) German running keys** | — |
| **L171** R80a, two keyword stages (one listed, one free) | Gate only; K4 never run. Free length 1–7: 53/53; 8–10: 22/27; 11–12: 12/16. lcm ≥ 49: 3/5 | (No K4 null exists) | The whole family blind. But R75's F1X (L165) covers 171 of its 180 length cells exactly; the 9 low-check cells (listed 11–15 × free 8–12) are the real gap | Via L165 F1X (count caveat, T2) |
| **L167** R78, self-keyed cipher; T-RK | T-RK has no gate. Its own row says no conclusion (low power) | — | **T-RK as a whole**. The sum-invariant EXCL is exact and unaffected | EXCL Beaufort/variant all alphabets; Vigenère AZ/PAL. OPEN Vigenère KRY/ABS and mixed alphabets |
| **L105** R30, one mis-carved clue letter, two-free-alphabet Gromark | Plants with one corrupted clue: 4/20 (16 restarts), 6/20 (64); about 30–45% power | — | **The whole one-error Gromark search** (3,178 settings) | — |
| **L104** R30, punctuation word model | Gate failed (10/22 vs 11/22 plain) | — | The punctuation model gives no extra power. Plain ORTH's ~50% on X-punctuated text is the relevant level | — |
| **L139** R44 H-KW, keyword plaintext alphabet × free cipher alphabet | Holdout FAILED 14/20 exact (bar 16); 19/20 within 3 letters | (No K4 run) | Family not run on K4 | — |
| **L162** R73 R26 (word-number Ragbaby-like) | Gate FAILED 88/100, so K4 was not run for R26 | — | Superseded by **L163** (R73b): gate passed 100/100, K4 NO_SIGNAL. No gap remains | R26X EXCL (L163) |
| **L93, L94, L96** source / route-Gromark compatibility | No synthetic gate; WEAK by construction (0–2 independent crib cycles) | — | Near-vacuous: these say little either way | — |
| **L128** | WEAK, not confirmatory (its own row) | — | As stated | — |

## Exact checks whose decided range has gaps (not NO_SIGNAL, listed so they are not mistaken for full exclusions)
- **L172 (R83a):**
  - PFX lags 11–12, most of 9–10, and gaps at 3–8 (< 3 checks);
  - SLX m ≥ 11; SLX-A and SSX m 26;
  - LX's m 18–20 cells are near chance.
  - The one-wrong-letter WPX and PFX results are CHANCE, not EXCL (T1).
- **L165 (R75 F1X):** the solution counts at periods 15–18 are being re-checked (T2). Feasibility is unaffected by
  the overflow.
- **L35:** source missing; the Hill one-error claim is unverified (`r81a/audit/DROP_ONE_REVIEW.md`).

## Rows whose recorded gate passed over their stated range (from the row text; not re-run)
L149, L150, L152, L163, L164, L165 (blind), L166, L169, L170: by the row text, the gate passed on every stratum the row claims. The
STRETCH strata are reported separately and were not used to claim exclusions beyond them.

Independent review: NONE (one model).
