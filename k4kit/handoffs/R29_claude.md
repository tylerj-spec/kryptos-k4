# K4 HANDOFF: Claude → ChatGPT, round 29 (26 Oct 2026)

## For Tyler
- **No solution or candidate.** ChatGPT's round 28 (Morse keys) **reproduces exactly**, and an independent recount
  agrees.
- **New this round:** the 65,968 "K3 rotation + Gromark" settings from round 27 had only been checked against the
  clues. Claude ran the first English search on them:
  - the 39 settings that actually cross-check the clues;
  - all 3,212 settings for K3's own rotation.

  **No candidate:** the best score is −141.4, against −69 to −79 for planted real messages.

  The solver was tested on planted messages first: 15/20 recovered at full budget, 9/20 at the screening budget.
- **The full Carter book is still untested.** archive.org is blocked from Claude's workspace too. The test is ready
  (`book_key_test.py`); it needs the book's plain-text file (see §3).

## 1. Audit of R28
| Item | Method | Result |
|---|---|---|
| `r28_morse_experiment.py`, `r28_morse_pulses.py` | replayed on a copy with `python3 -I` | JSON outputs **identical** (ignoring elapsed time); `r28_morse_passes.csv` identical |
| Both-free Morse letter passes | independent driver (`claude/r29/independent_morse.py`): own stream assembly, own route composition, own anchor remapping, R26 oracle | **7 / 12 / 5 of 360** per order, exactly as reported. Every pass is at a 0-cycle route. The identity route has 2 crib cycles and **0 passes** |
| Sign symmetry (your L92) | algebra: reflect both alphabets, x → −x | **agreed**; R26's ± counts are halved (4-digit Gromark: 3 settings; K4-reversed: 1) |
| Script note | `r28_morse_experiment.py` comment | The "first four frozen routes" are all **R24x8** variants (CW/CCW × fwd/inv), not "24x8 and 23x8". The results are unaffected |

**R27 replay (`r27_routes.py` as shipped).**
- The total of 65,968 compatible settings reproduces.
- **Your L94 null does not reproduce.** The shipped script gives null mean **1,546.4**, with 6/20 nulls ≥ 1,604, so
  **p = 7/21 = 0.333**. L94 reports mean 1,571.3 and p = 0.524, which probably came from `r27_route_chunks.py` or a
  different seed. The conclusion (not significant) is unchanged; please note which script produced L94.
- **Crib cycles depend only on (route, order)**, not on the primer: 59,322 settings have 0 cycles, 6,607 have 1,
  and 39 have 2.
- **K3's own geometry (24 then 8) gives 0 cycles in every variant.** So for the most K3-like routes, the clues test
  only alphabet injectivity, and their passes are nearly uninformative.

## 2. English search of the R27 passes (pre-registered: `claude/r29/R28C_PREREGISTRATION.md`, sha256 `f691a865…7ddd99`)
- **Solver:** `solver_s2kp` = S2k plus an optional permutation, so the text is un-rearranged before scoring
  (needed for rearrange-then-substitute). Same dictionary, quadgram term and polish as R21 S2.
- **Calibration:** 20 planted messages (the R21 fresh base passages, clues in place) encrypted with K3's own variant
  **R24x8/CW/inv**, 10 per order, solver given the true setting.

  | Budget | Readable | Rearrange then substitute | Substitute then rearrange |
  |---|---|---|---|
  | 16 restarts | 9/20 | 5/10 | 4/10 |
  | 64 restarts | 15/20 | 8/10 | 7/10 |

  Readable W −69 to −79.
- **Tier A** (all 39 two-cycle settings, routes R25x8/CW/inv and R24x9/CW/fwd, 64 restarts): best **−148.32**
  (`R24x9/CW/fwd|S_then_T|34068`). Wrong-key level; **no candidate**.
- **Tier B** (all 3,212 settings of K3's own variant R24x8/CW/inv, both orders; 16-restart screen, top 20 re-run at
  64 restarts with new seeds):
  - Best **−141.43** (`R24x8/CW/inv|S_then_T|95330`); median −178.1; **0/3,212 above −114.9**.
  - In the re-runs, 17 of the top 20 changed by 19–65 letters, so they are optimizer noise.
  - **Three re-ran to identical text** (0 letters changed: primers 76294, 79534, 38065), but they score only −148.6,
    −152.6 and −152.8, and are gibberish. Their clue structure pins the optimizer into the same local optimum.
  - **Lesson:** replication is necessary but not sufficient. The pre-registered rule requires both conditions, and it
    held.
  - **No candidate.**
- **Not searched:** the remaining 62,717 settings (other 0- and 1-cycle routes). At full budget they would take
  about 60 CPU-hours.

## 3. Requests to ChatGPT (pick at most 2)
1. **The Carter text (blocked for both of us).**
   - Archive.org's plain-text file is at
     `https://archive.org/download/tomboftutankhame01cart/tomboftutankhame01cart_djvu.txt`.
   - Tyler can download it in a browser and attach it, or allow archive.org under Settings → Capabilities. Then run
     `python3 -I book_key_test.py <file> --anchor-phrase CANYOUSEEANYTHING --search 50`.
   - If you can reach Wikisource's proofread pages for the same edition, that is better than OCR.
   - Write the protocol first: which pages count as "the book", OCR handling, the shuffle null and the candidate rule.
2. **Make the R27 composition informative.** For the 0-cycle routes, the clues can't separate keys. Either:
   - search them for English at a budget the calibration supports, using `solver_s2kp` (about 60 CPU-hours at full
     budget, so choose a pre-registered subset); or
   - better, add a *second* constraint source before searching, e.g. the X/Q punctuation rule (L87) or the
     carving-error variants.

   State the choice before running.

Standing rules unchanged: pre-registration, planted and hidden controls, untrusted archives with `-I`, no Paradigm
submissions (Tyler's decision).

## Files (`claude/r29/`)
- **Audit:** `independent_morse.py` and `.log`; `r27_replay.log`.
- **Search:**
  - `R28C_PREREGISTRATION.md`, `r28c_run.py`, `solver_s2kp.cpp`;
  - `r28c_calib.log`, `r28c_tierA.log`, `r28c_tierB.log`, `r28c_tierB2.log`;
  - ranked JSONs and outputs.
- **Book test:** `book_key_test.py`.
