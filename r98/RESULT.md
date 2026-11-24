# R98 result (Claude Code, 24 Nov 2026): Slidefair with keyword alphabets is EXCLUDED for every key

## In plain words
**Slidefair is ruled out for K4 with any two keyword alphabets from R76's tier, under any key sequence.**
- Slidefair is the ACA's two-letter cipher on a sliding Vigenère or Beaufort chart. It was proposed as `r77` H10 and
  never run.
- The two alphabets range over the tier's 77,229 keyword alphabets: every 4–15-letter English word of the word model,
  the sculpture words, and A–Z.
- The key can be anything: periodic, running or random, a new key letter for every pair.

**What was checked.** The key cancels out of the check, so every key is decided at once. The question is whether any
of 95 billion (convention, alphabet, alphabet) settings reproduces K4's ciphertext at the 24 published letters.
- **Answer:** none does.
- **Even allowing one wrong pair:** still none. That allowance covers one wrong letter, or a different same-column
  rule at one pair.

**Shuffles.** All 200 shuffled copies of K4 also give zero. Chance passes are expected to be rare, about 10⁻⁵
(EXACT) and 10⁻⁴ (DROP), so the screen excludes; it cannot rank K4 against chance.

## Gate (`holdout/CHECKER_GATE.json`, seed 980901): **GO**
| Check | Result |
|---|---|
| V1 reference round trip | 400/400, including 402 forced same-column pairs |
| V2 brute-force oracle (forward encryptor, every κ) | 30 inputs × 16 conventions × 120² alphabets: **0** per-convention mismatches for the fast path, **0** for the simple path. 26 inputs have EXACT > 0 and 30 have DROP > 0 |
| V3 full-tier plants | 32/32 counted in EXACT, and 32/32 in DROP with one letter corrupted (per-setting and full-count checks) |
| V4 same-column plants | 16/16 |
| V5 throughput | fast and simple paths agree; planted full scan EXACT 1; forecast 604 s CPU (limit 960) |

**Run:** COMPLETE through `audit/run_bounded_agg.py`, 107.6 s wall, 106.8 s CPU, peak 101 MB (cap 300 / 240 /
1,024). Gate freeze 960607c was pushed before any K4 input was read.

## Target (`k4/AGGREGATES.json`, frozen in 3afd9f6): **EXCLUDED**
| Input | EXACT settings | DROP (setting, dropped pair) | Conventions with any |
|---|---|---|---|
| **K4** | **0** | **0** | **0** |
| 200 shuffles (seed 980400) | 0 in all 200 | 0 in all 200 | 0 |

- **Published pairs:** 11 per parity, re-derived from the `CLUES` literal (sha256 63121cea…).
- **Run:** COMPLETE, 263 s wall, 261 s CPU, peak 106 MB (cap 1,800 / 1,200 / 1,024), zero retries.
- **Freeze:** pushed in 3afd9f6. The remote blobs equal the local ones, checked before `evaluate98.py` read the
  aggregates.

**Decision** (`k4/EVALUATION.json`): EXCLUDED. K4 has 0 EXACT and 0 DROP.

## Post-freeze cross-check (`k4/CROSSCHECK.json`)
`crosscheck98.py` is a second implementation of the criterion: pure Python, tuples and Counters, no numpy and no
base-26 codes.
- It recomputes K4 and the first five shuffles from the frozen inputs, and agrees with them: all zero.
- It ran through the wrapper: 174 s, 135 MB (`k4/CROSSCHECK_RESOURCE_LOG.json`).

**Positive control** (`dev/CROSSCHECK_CONTROL.json`, synthetic). On two planted inputs it matches the fast path for
all 16 conventions, with non-zero counts of up to 5 EXACT and about 1,000 DROP, and it finds both plants.

## What this excludes, and what it does not
**Excluded exactly** (crib-assisted: the published letters in place and in the carved order):
- **Cipher:** Slidefair with PA and CA any two alphabets of the 77,229-alphabet tier, any per-pair key, under any of
  the 16 conventions:
  - Vigenère, or the identical Variant slide; or Beaufort;
  - either role order;
  - either output order;
  - either pair parity.
- **Same-column rule:** letters to the right, or any different rule at one pair.
- **Errors:** one wrong pair is allowed. That covers one wrong published letter, or one ciphertext substitution at a
  published position.

It includes `r77` C5's AZ/KRYPTOS sub-case, which was already closed by hand.

**Not excluded:**
- free (arbitrary) alphabets (shortlist S3);
- keyword alphabets outside the tier, such as other words or other constructions;
- a different same-column rule at two or more pairs (about 6% of keys put ≥ 2 of 11 pairs in a column);
- other digraphic rules;
- a transposition layer;
- insertion or deletion;
- errors at two pairs;
- non-English keywords.

Nothing from R98 enters any blind search.

## Notes and errata (additive; the pre-registration is unchanged)
1. **Setting count.** The pre-registration's "95,428,212,656 labelled settings" is an arithmetic slip. The correct
   figure is 16 × 77,229² = **95,429,095,056**, as recorded in `AGGREGATES.json`. The scope is otherwise as
   registered.
2. **Duplicate labels.** For the Vigenère tableau, convention (r, o) with alphabets (PA, CA) imposes exactly the same
   constraints as (1 − r, 1 − o) with (CA, PA). The positive control shows identical counts. So the labelled count
   double-counts some settings. This does not affect an exclusion.
3. **Amendment 1** (`AMENDMENT_1.md`) was committed with the source, before the gate ran:
   - it halved V2's inputs to 30, for the CPU cap;
   - it added two checks (fast/simple agreement, full-tier counts);
   - it made the decision's "K4's count" exact.
4. **Source caveat (disclosed at registration).** The ACA's own Slidefair page was unreachable from this environment.
   The rule follows `r77/HYPOTHESES.md` H10, and every ordering variant was enumerated.

## Review
**Independent review: NONE.** One model (Claude Code) registered, built and ran R98. ChatGPT is the named
reviewer. The natural independent checks are:
- re-running `crosscheck98.py` on all 201 inputs, about 100 minutes in pure Python;
- or a separately written checker of the same criterion;
- and re-deriving the criterion from the cipher definition (`PREREGISTRATION.md` §2).
