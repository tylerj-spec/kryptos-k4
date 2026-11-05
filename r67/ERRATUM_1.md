# R67 Erratum 1 (Claude Code, 5 Nov 2026): transcription error in `r67/REFERENCE_SHA256`, corrected before any production step

- **What was wrong.** The `solver_source` pin read
  `d1be0d9c475b66ec47e39125f7ee9f8ce7617e3df1df3c262b23f5e66f03c4216`. That is 65 characters: the first 29 characters
  of the correct solver-source hash spliced onto the last 36 characters of R65's **results** hash
  (`b53f5884…f8ce7617e3df1df3c262b23f5e66f03c4216`).
- **The correct value.** `d1be0d9c475b66ec47e39125f7ee9b3398ae63ff550175222081d851b50f7009`.
  - This is the `solver_source` line of `r65/k4/run/FROZEN.sha256` on main, which `r67/PREREGISTRATION.md` names as the
    source of these pins.
  - It is also the current sha256 of `r63/blind/rk2_solve.cpp` on main.
- **Effect if left unfixed:**
  - `r67/sealed/stage_blind.py` refuses non-64-character pins, so staging would stop;
  - `r67/verify_controls.py` would mark any run INVALID.

  So the error could not have let a bad run through. It would only have blocked a good one.
- **What did not change:** `r67/PREREGISTRATION.md`, `r67/PROTOCOL.sha256` (d1e7208b…) and every other pin. The other
  nine pins were checked line by line against R65's frozen manifest and match.
- **Timing:** this erratum is committed and pushed before the sources are built, the controls are generated or anything
  is staged or scored.
