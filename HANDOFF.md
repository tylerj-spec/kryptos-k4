# Kryptos K4: R40–R42 handoff (Claude Code, 28–29 Oct 2026). Earlier briefs: R34 in git history; ChatGPT's in `r33/`–`r39/`.

## Start here (state at hand-off, 29 Oct 2026, R44b)
- **No verified K4 solution. Nothing submitted to any external checker.**
- **Status on GitHub:**
  - **`main`:** includes R35–R42, R40G (PR #9) and this handoff's earlier rounds.
  - **PR #11 (ChatGPT R43, word-constraint beam; open, do not merge as a solver):** reviewed in
    `r44/REVIEW_PR11.md`. The algebra is correct; the beam must be replaced. Reason: the true text closes almost
    no checkable constraints in its first 30–40 letters.
  - **PR #12 (Claude R44/R44b; draft, targets PR #11's branch):** review, audit and a new solver.
- **New capability (L140):** a blind solver for **keyword plaintext alphabet × completely free cipher alphabet**,
  with the true key given.
  - **Pre-registered fresh holdout:** **20/20 exact** (bar 16), 0 invalid witnesses.
  - **Code:** `r44/blind/kwpa_solve.cpp` (enumerates 4,749 keyword alphabets and anneals the cipher alphabet), then
    `r44/blind/polish.cpp` (word-score polish).
  - **Not covered:** two *uniformly random* alphabets are still unsolved (L138, L139).
- **Correction (owner review on PR #12):** do **not** run the R44b solver on K4 with Gromark keys.
  - R39's top 1,000 IC primers contain no crib-feasible primer even with two free alphabets (L137).
  - PR #13 and an independent replication (`r44/audit/KW_EXACT_CHECK_RESULT.md`, L141) show **0 feasible K4
    settings**, in place, for all 100,000 primers × 4,749 keyword alphabets × both operations × both orientations.
- **Next worthwhile hypotheses change the keystream or the order of operations, then apply R44b where it fits:**
  - running keys (K1–K3, Carter) × keyword alphabet;
  - other keyword dictionaries;
  - transposition before or after the substitution.
  - **First do the cheap exact feasibility check** (as in `kw_exact_check.cpp`, pre-registered), and only run the
    blind solver on families that are still feasible.
- **Checks before any push:** `bash strictblind/tests/run_all.sh`, `bash verify_all.sh`,
  `python3 -I r44/tests/test_contract.py`.
- **Rules:** `k4kit/CLAUDE.md`.
  - Pre-register, plant controls and nulls, freeze and commit before any reveal, report raw text.
  - Never `git stash` while jobs write tracked files.

## What this round means (plain words)
- **ChatGPT's R35–R39 checks out.**
  - **Replays:** all 23 K4 blind scans and all 31 R39 score vectors replay byte for byte.
  - **Integration:** PR #8 merges the stacked PRs #2–#6, plus harness fixes and PR #10's test fix.
  - **Results:** every family tested gives chance-level matches with the known letters. R39's key ranker works on
    planted data and shows no Gromark signature in K4.
- **R34 is finished.** E3 (Carter × 5,000 double rotations, 6.8 × 10¹⁰ settings) has a best match of 12/24, which
  is chance level, and its plant ranked #1 (L124).
- **New this round: the "one unknown alphabet" families.** Every earlier blind round fixed **both** alphabets, and
  two unknown alphabets cannot be solved blind at 97 letters (L109, L123). But when **one** alphabet is fixed and
  the other is free, the problem becomes solvable:
  - **R40, free plaintext alphabet:** each key turns K4 into a simple substitution.
    - The first stage ranks every setting by letter counts. It also detects any transposition applied *before*
      the substitution.
    - **Result: no candidate.** The in-place family is excluded exactly: 0 of 337,634,136 settings fit the 24 known
      letters. All 12 plants passed (L134).
  - **R41, free plaintext alphabet, substitution then K3-style transposition:** 116 R27/columnar routes and 5,000
    double rotations. Result: no candidate; an exact rule-out of 10.9 billion settings under any plaintext alphabet (L135).
  - **R42, free cipher alphabet:** Quagmire II and the ACA standard Gromark with any keyword.
    - With the key known, annealing the cipher alphabet recovers planted text blind: 24/24 in development.
    - Result: no candidate, and an exact in-place rule-out under any cipher alphabet (171 million settings). But the blind gate failed (4/6 plants), so the blind solve is trusted for C10b5 keys only (L136).

## Are we close? (honest view)
**No.**
- **What this round adds:** the families ruled out now include every plaintext alphabet (R40, R41) or every cipher
  alphabet (R42) for these key families, not just a few fixed ones. Their plants come back #1.
- **Still open:**
  - two unknown alphabets at once (a search problem; see below);
  - other key sources;
  - other transpositions applied after substitution;
  - methods outside the Vigenère/Gromark family.

## Method notes for the next agent
- **Free plaintext alphabet:**
  - **Detection:** y = CA⁻¹(c) ∓ k is a substitution of the plaintext. Score L1 = sorted counts × sorted English
    log-frequencies. It is very sharp: plants rank 1–4 among 3.4 × 10⁸ settings.
  - **Reading:** a simple-substitution solve.
- **Free cipher alphabet:**
  - **Stage 1:** the unigram-optimal alphabet is an exact 26 × 26 assignment (Hungarian method). It is weaker:
    it works for about 10⁶ settings, but a true key ranked about 30,000th among 3 × 10⁷.
  - **Stage 2:** annealing the alphabet with quadgrams is reliable once the key is right: 16 restarts gave 24/24.
- **Two free alphabets (L138, `r43dev/`):**
  - **Quadgrams cannot identify the text at 97 letters.** With strong parallel tempering, wrong texts match or beat
    the true text's score. This corrects the earlier "search-only failure" reading.
  - **The word model can.** True texts score W −71 to −94, the wrong optima −144 to −164.
  - **What remains is search:** on quadgrams + words the truth is 50–150 points better than anything found, but
    alphabet-swap search does not reach it.
- **Exact whole-family checks:**
  - **Free PA:** equal letters ⇔ equal y.
  - **Free CA:** equal ciphertext letters ⇔ equal PA⁻¹(p) ± k.
  - Both are cheap (10⁸ settings in seconds) and exact.
- **Twins:** a base-10 primer's digit complement, with the opposite operation, gives nearly the same text.
- **Lesson:** never run `git stash` while a background job writes tracked files. It detached E3's log; the log was
  recovered from the live process.

## Files
- `r40/`, `r41/`, `r42/`:
  - `PREREGISTRATION.md` and `PROTOCOL.sha256`;
  - `blind/` (contract-tested) and `sealed/`;
  - the experiment directories, with FROZEN, REVEAL and whole-family outputs.
- `LEDGER.md`:
  - L124 (E3);
  - L131–L133 (R38, R39, review);
  - L134 (R40);
  - L135–L136 (R41, R42);
  - L137 (review of ChatGPT's PR #9, R40G Gromark IC audit);
  - L138 (two-free-alphabet identifiability).
- `r43dev/`: the parallel-tempering development solvers (planted data only).

## Suggested next
1. **ChatGPT:**
   - Audit R40–R42: replay a frozen stage-1 file, recount a whole-family histogram independently, and check the
     plants.
   - Move PR #9's files from `r40/` to `r40g/`. They clash with CC's R40, which is why PR #9 conflicts. Its
     findings were replayed and are in L137.
2. **A stronger free-cipher-alphabet screen,** so that C10b6, C10b7 and Carter can be solved blind and not only
   checked exactly. For example, a quick anneal started from the Hungarian alphabet, or pruning on bigram
   structure.
3. **Two free alphabets:** still open.
   - **Already tried in development, planted only, and failed:**
     - the nested solver;
     - an alternating solver (fix PA and anneal CA, then fix CA and anneal PA), at 200 starts × 10 rounds. It ends
       at −422 and −438 on the L109 plants, against truth −384 and −395, with 78–85 letters wrong.
   - Also tried and failed: parallel tempering on quadgrams (wrong texts outscore the truth) and on
     quadgrams + words (the truth is identifiable but not reached) (L138).
   - **Next to try:** word-level moves. For example:
     - place a dictionary word at a position and propagate the alphabet constraints it implies, like crib
       dragging with candidate words instead of the published clues;
     - a beam search over word segmentations consistent with one pair of alphabets.
   - **Gate before any K4 use:** at least 16 of 20 planted messages recovered.
4. **Other key texts** with edition checks, run through R40/R42 (both are cheap per key).

No submissions to any external checker.
