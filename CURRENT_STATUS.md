# Current K4 research status (15 November 2026)

**No independently verified K4 solution. Nothing was submitted to an external verifier.**

**The K4 search hold was lifted by Tyler on 16 Nov 2026** (`audit/reviews/SEARCH_HOLD_LIFTED.md`). All guardrails stay in force.

**Latest search, R84 (17 Nov 2026):** R80a's two-keyword-stage families on K4, run strict blind in an isolated sandbox. Result: **NO_SIGNAL** (K4's best is no better than 60 of 100 shuffles; 4/24 published letters). See `r84/RESULT.md` and L173.

**Audit fixes merged 17 Nov:**
- #89: a broken workflow's YAML.
- #90: T1's WPX one-error strength labels were stale.
- The corrected statistic, recalibrated on K4 + 20 shuffles, gives K4 max s 2 (no setting at s ≥ 3) and p 0.38. No lead. See `r83/audit/WPX_STRENGTH.md`.

## November 2026 audit

- Two confirmed defects, both corrected by additive errata; original frozen files are unchanged:
  - **L172 (R83a):** the WPX "one published plaintext letter wrong" exclusion is withdrawn; PFX's drop-one count is not exhaustive (`r83/audit/ERRATUM.md`).
  - **L165 (R75):** F1X solution counts can overflow int64; those counts are unverified (`r75/audit/ERRATUM.md`).
- Independently re-derived and holding within their scope: L01–L04, L167.
- All other ledger exclusions are **unreplayed**, not disproved. No hash mismatch in any identifiable primary frozen file.
- Findings: `audit/historical/AUDIT_FINDINGS_AND_DECISIONS.md`. Rules for all future tests: `audit/FUTURE_TEST_GUARDRAILS.md`.
- **Work order progress (15 Nov, PR #86):**
  - **T1 done:** with one wrong published letter, WPX and PFX are both CHANCE. WPX has 2 survivors (inside the conservative 260); PFX has 22.
  - **T2 done:** F1X feasibility is confirmed setting by setting; only counts ≥ 2^63 were wrong.
  - **T3 done:** R81a's drop-one is sound. L35's Hill claim is flagged.
  - **T4, T5, T7 done:** documentation.
  - **T6 item 1 done (16 Nov):** R83a's EXACT results reproduced independently. LX was replayed in full on K4. There were 0 disagreements. Items 2–5 are not started.
  - The conditions for lifting the search hold now rest on review of T1/T2 and Tyler's decision.
- **What to do next:** `audit/NEXT_STEPS.md`.

The sections below are the status as of 31 October 2026 and remain valid. Rounds R55–R83 are recorded in `LEDGER.md`.

---

## Status as of 31 October 2026

**No independently verified K4 solution. Nothing was submitted to an external verifier.**

## Merged work

- R49 (PR #19): previously reconstructed Berlin World Clock 24-face chart preserved with provenance/uncertainty; **not** authenticated as a K4 key.
- R53 (PR #23): hard ciphertext-only / freeze-before-reveal K4 input firewall; the Caesar solver is **only a pipeline smoke test**.
- R54 (PR #24): isolated ciphertext-only cipher-family fingerprints. IC is **0.0360824742** for the original 97-character ciphertext and all 26 letters occur. The best lag-7 signal has corrected p ≈ 0.149; period-column p ≈ 0.958. No cipher, key, or plaintext is identified.

## Preserved earlier work in this branch

- R43: **failed** word-beam solver, retained as an algebraic audit and negative result. Never use for K4 plaintext recovery.
- R44b: **20/20 exact** controlled blind recovery of 97-letter English messages *given the true key*, with independent forward-re-encryption witnesses. This is a valid **known-key** alphabet solver, **not** an unknown-key method.

## Not suitable as independent K4 evidence

- Claude's later R52/R52b branch: used confirmed K4 letters/positions to **choose a key/route** before a separated final solver ran. Therefore its selection pipeline is **crib-conditioned**, even though the final run omitted those letters; its 1/24 K4 output match and four known-key plants do **not** exclude a broad cipher family.
- Other historical finite-family postfreeze clue screens (R40G, R45–R51) may remain archival mathematical exclusions within their exact scopes but cannot seed a new ciphertext-only key search.

## Mandatory next steps

1. Specify reversible cipher/masking mechanisms and independently sourced key hypotheses **without K4 known letters**.
2. Demonstrate fully blind 97-letter recovery on at least 16/20 **fresh hidden-plaintext, hidden-key** encrypted controls for the exact method and key-search procedure; include proper null/false-positive calibration and independently verify every forward-encryption witness.
3. Run the original 97-letter ciphertext only in isolation; freeze full outputs and algorithm/key metadata; independently evaluate K4 published words and positions only **after** the freeze.
4. Do not tune on failed known-letter results. Document prior exposure of hypotheses and rerun on genuinely new control families before considering another K4 attempt.

Canonical owner rule: `r53/BLIND_RULES.md`.
