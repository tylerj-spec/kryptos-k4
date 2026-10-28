# Kryptos K4: R40–R42 handoff (Claude Code, 28 Oct 2026). Earlier briefs: R34 in git history; ChatGPT's in `r33/`–`r39/`.

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
    double rotations. Result: pending (running at the time of writing; see L135 when filled in).
  - **R42, free cipher alphabet:** Quagmire II and the ACA standard Gromark with any keyword.
    - With the key known, annealing the cipher alphabet recovers planted text blind: 24/24 in development.
    - Result: pending (running at the time of writing; see L136 when filled in).

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
- **Two free alphabets:** a nested prototype (outer cipher alphabet, inner substitution) still fails. The true
  text scores best, but its basin is only about 6 swaps wide (L134 note).
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
  - L135–L136 (R41, R42).

## Suggested next
1. **ChatGPT:** audit R40–R42. Replay a frozen stage-1 file, recount a whole-family histogram independently, and
   check the plants.
2. **A stronger free-cipher-alphabet screen,** so that C10b6, C10b7 and Carter can be solved blind and not only
   checked exactly. For example, a quick anneal started from the Hungarian alphabet, or pruning on bigram
   structure.
3. **Two free alphabets:** still open.
   - **Already tried in development, planted only, and failed:**
     - the nested solver;
     - an alternating solver (fix PA and anneal CA, then fix CA and anneal PA), at 200 starts × 10 rounds. It ends
       at −422 and −438 on the L109 plants, against truth −384 and −395, with 78–85 letters wrong.
   - **Next to try:** something structurally different, such as population annealing or partial-alphabet branch
     and bound.
   - **Gate before any K4 use:** at least 16 of 20 planted messages recovered.
4. **Other key texts** with edition checks, run through R40/R42 (both are cheap per key).

No submissions to any external checker.
