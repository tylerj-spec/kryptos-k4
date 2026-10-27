# R30 pre-registration (Claude Code, 27 Oct 2026)

Written before any R30 calibration or K4 computation. The only facts about K4 used to design it are structural and
already in the ledger: the crib-cycle count of each R27 route/order (L99; 12 route/order groups have 1 cycle) and
the oracle's chance rate (L90). The run scripts assert this file's sha256 (`PROTOCOL.sha256`).

Fresh hidden fixtures: `fixtures_punct.json`, sha256 `6e3169dd123018dcce79212028f735d4a594c63d64f7a7d73337579e6697bd6b`.
They were written for this round, contain the clues in place and K2/K3 punctuation (X = full stop, Q = question
mark), and are used only in C2.

## Common definitions
- **Substitution model** (as in `key_oracle`): c = CA[(PA⁻¹(p) + k) mod 26], both alphabets free, the key given.
  Positions are 0-based in code.
- **Solver:** `bin/solver_s2kp`, unchanged, 40,000 proposals, λ 0.05→0.
  - **Screen:** 16 restarts. **Full:** 64 restarts.
  - Seeds: `random.Random(label).randrange(1, 2**63)`. Replication runs use the label + `"|rep"`.
- **Models:**
  - **ORTH** = `data/word_model_orth.tsv` (unchanged).
  - **ORTHXQ** = ORTH plus two lines, `X -1.5 -1e+100` and `Q -2.5 -1e+100`, the costs fixed in the R29 handoff
    (§4 T2) before this round.
- **Readable:** ≤ 5 letters differ from the planted truth.
- **Forced letters** (reported for every listed output): a non-clue position whose plaintext letter is the same in
  every alphabet assignment consistent with the clue graph *within its component*. That is, the position's
  ciphertext node lies in a crib component and the implied plaintext rank falls on a plaintext node of the same
  component. This is a lower bound on what the clues determine.
- **Candidate rule** (unchanged from R28C), applied per model:
  - best W above the bar: −114.9 for ORTH; for ORTHXQ, the larger of −114.9 and the best wrong-key W seen in C2;
  - **and** a 64-restart replication with new seeds returns the same text within 5 letters.
  - A candidate's raw 97 letters go to Tyler unedited. No external submission.
- **Human-review shortlist** (not candidates): for each family, the 5 best outputs after replication, with raw text,
  forced mask, forced count, W, and the family's wrong-key/null context. They are labelled REVIEW ONLY.

## E1. Chain-addition (Gromark-style) decimal streams with longer primers, in place (handoff T4, extended)
- **Keys:** k_i = (k_{i−b} + k_{i−b+1}) mod 10, primer = the first b digits.
  - b = 6: all 1,000,000 primers (T4).
  - b = 7: all 10,000,000 primers (VIC-style chain addition uses the same rule with b = 10, which is too large
    for this pipeline).
- **Oracle:** `key_oracle.possible`, sign +1 (L92). Expected chance passes ≈ 3.9e-4 per primer (the rate seen for
  5-digit Gromark, 39/100,000).
- **Null on the pass count (b = 6 only):** the same 1,000,000 primers against 5 letter-count-preserving shuffles of
  K4 (seeds 3001–3005). Reported, not a decision criterion.
- **Calibration C1:**
  - The 20 R21 calibration passages; 10 encrypted with b = 6 and 10 with b = 7. Random primer and alphabets, seed
    30001.
  - True key given. Report readable at 16 and at 64 restarts.
- **Search:**
  - ORTH screen of every b = 6 and b = 7 pass at 16 restarts.
  - The 20 best by W are re-run at 64 restarts with new seeds (replication).

## E2. R27 route + 5-digit Gromark, all one-cycle settings (handoff T5, pre-registered subset)
- **Settings:** every pass from `route_gromark.py passes` with exactly 1 crib cycle.
  - The 12 groups: R23x8/CCW/fwd, R24x7/CCW/inv, R24x7/CW/fwd, R24x7/CW/inv, R24x9/CCW/inv and R24x9/CW/inv, each
    in both orders.
  - About 6,607 settings (L99). None has been English-searched before.
- **Calibration C3:**
  - The 20 R21 calibration passages, encrypted under those 6 routes (cycling through them), orders alternating.
    Random primer and alphabets, seed 30003.
  - True setting given. Report readable at 16 and at 64 restarts.
- **Search:** ORTH screen at 16 restarts, then the 20 best re-run at 64 restarts with new seeds.

## E3. K2/K3 punctuation as a word-model rule (handoff T2, ledger L87)
- **Calibration C2 (blind, gate):**
  - Each of the 22 fresh fixtures is encrypted in place with 5-digit Gromark: random primer, random alphabets, seed
    30002.
  - Its feasible primers are found by the oracle over all 100,000. The lines are the true primer plus up to 19 wrong
    feasible primers, drawn with seed 30002.
  - Both models are run on identical lines at 64 restarts.
  - **Blind readable:** the line with the best W is the true primer, and its text is readable.
  - **Gate:** ORTHXQ blind readable ≥ 11/22. Also reported: ORTH on the same lines, and both models on the 20 R21
    (unpunctuated) calibration passages with the true primer given (64 restarts), to show any cost on unpunctuated
    text.
- **K4 runs** (decision runs only if the gate passes; otherwise exploratory and labelled so):
  - **(a)** all 39 feasible 5-digit primers at 64 restarts;
  - **(b)** the 39 two-cycle R27 route settings at 64 restarts;
  - **(c)** all E1 passes at 16 restarts;
  - **(d)** all E2 settings at 16 restarts.
  - The 20 best across (c) and (d), and anything above the bar in (a) and (b), are re-run at 64 restarts with new
    seeds.

## E4 (conditional). Full Carter & Mace 1923 vol. I as running key (T1, L101)
Runs only if an edition-identified text becomes available in this session (archive.org is blocked by the session's
network policy as of writing).
- Before running, record the source URL or upload name, sha256 and edition evidence (title page, publisher, year).
- `tools/book_key_test.py` normalisation unchanged.
- Search: every oracle pass screened at 16 restarts (ORTH), the 20 best re-run at 64 with new seeds, and 20
  letter-shuffled copies as the pass-count null.
- Same candidate rule.

## What is not claimed
A "no candidate" outcome is qualified by the measured recovery rates (C1, C2, C3). It is not an exclusion of any
family. Pass counts at chance level are not evidence either way.
