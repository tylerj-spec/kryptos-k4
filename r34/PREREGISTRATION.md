# R34 pre-registration (Claude Code, 28 Oct 2026): strict-blind runs on the shared harness, plus a solver-budget probe

Written before any R34 scan. All K4 runs use `strictblind/`: tests passed (`tests/run_all.sh`), blind code free of
clues, outputs frozen and committed before `sealed/` runs. Each experiment directory holds its manifest. Plants are
made **before** the blind runs, from `reference_messages.json` `r20_templates` indices never used before (9–12).

## E1: Carter × every keyword-columnar variant
- **Routes:** `routes.py columnar KRYPTOS,PALIMPSEST,ABSCISSA`: 32 read variants per word × 2 orders = 192
  route-orders.
  - R33 searched only the 24 "canonical" route-orders with Carter. The other 168 are new; all 192 are run.
- **Key:** `TEXT carter_az.txt` (sha256 6761a507…), 12 fixed conventions.
- **Plants:** `r20_templates[9]` and `[10]`, seeds 34001 and 34002, a random route-order from the 192 and a random
  Carter window.

## E2: 7-digit chain addition × K3-style routes
- **Routes:** `routes.py r27`: identity plus the 20 R27 routes × 2 orders = 41.
- **Key:** `CHAIN 7`, all 10,000,000 primers, 12 fixed conventions.
- **Plant:** `r20_templates[11]`, seed 34003.

## E3: Carter × every double rotation, widths 4–28 (runs last; about 1.5 hours per scan)
- **Routes:** `routes.py rot 4 28`: 5,000 route-orders (same set as R32 F2, which used 5-digit chain addition).
- **Key:** `TEXT carter_az.txt`, 12 fixed conventions.
- **Plant:** `r20_templates[12]`, seed 34004.

## Decision rule (unchanged from R32)
- **Candidate:** a frozen K4 top-100 row with all 24 known letters, or a whole-family setting with 24/24.
- Otherwise the result is no candidate, and **EXCL** for these fixed conventions if the whole-family max is below 24.
- Plants must rank #1. A failure is reported and qualifies the result; nothing is re-tuned.

## D1: development probe on planted data only (no K4)
- **Question:** is the clue-free failure of the two-free-alphabet solver (R30 L109: 0/8 at 64 restarts × 40,000
  proposals) cured by more search effort?
- **Setup:** the same 8 planted messages as L109 (seed 30009, calibration passages 0–7, 5-digit Gromark, random
  alphabets), true key given, all-unknown mask. `solver_s2kp` unchanged, at **256 restarts × 200,000 proposals**
  (20× the L109 budget).
- **Report:** how many are readable (≤ 5 wrong letters), and the true texts' W against the found W.
- **Rule:** if ≥ 4/8 are readable, a 20-message blind gate is pre-registered next round before any K4 use. Otherwise
  the result is recorded as "budget does not cure it".
