# R98 pre-registration (Claude Code, 24 Nov 2026): Slidefair with keyword alphabets, any key — exact scope

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY (type B, charter §5).** It decodes nothing, completes no
key and publishes no surviving setting.

**Approval:** Tyler, 24 Nov 2026: "Go for it & all necessary follow on actions until you've worked your way thru
enough of the plan for review". This is shortlist item S1 of `audit/reviews/CONSTRUCTION_SHORTLIST_20261124.md`, the
post-R96 construction-discovery lane.

**Independent review: NONE** (one model). ChatGPT is the named reviewer.

## 1. Model (exact)
Positions are 0-based; there are 97 letters. Plaintext is taken in pairs (i, i+1) with i ≡ a (mod 2), a ∈ {0, 1}.
Each pair has its own key value κ ∈ 0..25, **any sequence** (periodic, aperiodic, anything). PA and CA are 26-letter
alphabets, and IDX_X[ℓ] is the position of letter ℓ in alphabet X.

**Roles:**
- *r = 0:* the upper (PA) letter u is the pair's first letter and the lower (CA) letter w its second.
- *r = 1:* the reverse.

**Tableau t (lower-row letter at column x):**
- **Vigenère:** CA[x + κ]. The Variant slide CA[x − κ] gives identical constraints, because the key cancels.
- **Beaufort:** CA[κ − x].

**Encryption of (u, w):** x_u = IDX_PA[u]. The lower-row column x_w solves lower(x_w) = w.
- If x_u ≠ x_w: c_up = PA[x_w] and c_low = lower(x_u), the opposite corners.
- If x_u = x_w (same column): c_up = PA[x_u + 1] and c_low = lower(x_u + 1), the letters to the right.

**Output o:**
- *o = 0:* c_up is written at the pair's first position and c_low at the second.
- *o = 1:* the reverse.

**Convention count:** 2 tableaux × 2 roles × 2 outputs × 2 parities = **16 conventions**.

**Alphabets:** PA and CA each range over **R76's large tier**: `r76/alphabets.py large_tier()`, 77,229 distinct
orderings.
- It contains every 4–15-letter word of the R59 word model, plus R75's sculpture words, each in asc/desc/ACA forms,
  plus A–Z.
- sha256 of the newline-joined orderings: 563ae44a….

**Scope:** 16 × 77,229² = **95,428,212,656 labelled (convention, PA, CA) settings**, each with any key.

**Source caveat.** The ACA's own Slidefair page could not be fetched from this environment (host unreachable). The
rule follows `r77/HYPOTHESES.md` H10.
- Every ordering choice is enumerated.
- The same-column rule is "letters to the right".
- A different same-column rule at one pair is covered by DROP.

## 2. Why every key is decided (the checker's criterion)
For one pair, let F = IDX_PA[c_up] − IDX_PA[u] and H = IDX_CA[c_low] − IDX_CA[w] (mod 26).
- **Vigenère:** normal F = −H; same column F = 1, H = 1.
- **Beaufort:** normal F = H; same column F = 1, H = 25.

κ cancels. With G = −H (Vigenère) or G = H (Beaufort), a setting fits a pair **iff (F = G and F ≠ 0) or (F = 1
and G = 25)**.

F = 0 means c_up = u. That would force x_w = x_u, which is the same-column case. So F = 0 can never be the normal
case.

**Necessity** follows from the equations. **Sufficiency:** κ is free per pair.
- **Normal case:** κ = IDX_CA[w] − IDX_PA[c_up] (Vigenère), or the analogue (Beaufort), reproduces both letters
  whenever F = G ≠ 0.
- **Same-column case:** κ = IDX_CA[w] − x_u, or the analogue, does so whenever (F, G) = (1, 25).

The gate checks both directions against a forward-cipher oracle that tries every κ.

**Screens:**
- **EXACT:** the setting fits every published pair.
- **DROP:** the setting fits all but at most one published pair.
  - One wrong published plaintext letter, or one ciphertext substitution at a published position, changes exactly
    one pair, because pairs do not interact.
  - So does an unknown same-column rule at one pair.
  - DROP covers each of those separately.

**Published pairs:** the observations are the 24 published letters at 0-based positions 21–33 and 63–73. They are
read from the `CLUES` literal of `r73/sealed/reveal_k4.py` (sha256 63121cea…) by `ast` parsing, not by import.
- **Parity 0:** pairs (22,23)…(32,33) and (64,65)…(72,73), 11 pairs.
- **Parity 1:** pairs (21,22)…(31,32) and (63,64)…(71,72), 11 pairs.
- Both are re-derived by the code from the literal.

## 3. Correctness gate (EXACT_CHECKER_CORRECTNESS; synthetic only; before any target computation)
| Check | Pass condition |
|---|---|
| V1 cipher | Reference encrypt and decrypt round-trip on 400 random texts × random conventions, alphabets and per-pair keys, including forced same-column pairs |
| V2 brute-force oracle | On a 120-alphabet sub-tier, for 30 random and 30 planted inputs, the checker's EXACT and DROP counts equal a brute-force count. The brute force enumerates every (convention, PA, CA) and tries every κ per pair with the reference **encryptor** |
| V3 full-tier plants | 32 plants: random conventions, alphabets from the full tier, random per-pair keys, random 13- and 11-letter windows (not the K4 positions). The planted setting is counted in EXACT. With one observed letter corrupted, it is counted in DROP |
| V4 same-column plants | 16 plants with a forced same-column pair are accepted in EXACT |
| V5 throughput | The full 16-convention scan on 3 random synthetic inputs. The forecast (2 × measured per-input wall and CPU × 201 + 10 s) is < 80% of the target caps |

Any mismatch is NO-GO, and an incomplete run is INCOMPLETE. Either blocks the target; no retry.

## 4. Target (once, after the gate's GO is pushed)
- **Inputs:** the unchanged K4 ciphertext (`r39/ic_gate/k4_ciphertext.txt`, sha256 2797de14…) plus **200**
  frequency-preserving shuffles. They are made with `random.Random(980400)`, list shuffle, rejecting the original
  and duplicates, cap 10,000.
- **Per input, only:**
  - EXACT-feasible settings;
  - DROP-feasible (setting, dropped pair) count;
  - the number of conventions with any feasible setting.
- **Decision:**
  - **EXCLUDED** if K4 has 0 EXACT and 0 DROP;
  - **LEAD** if K4 has feasible settings and no shuffle reaches K4's count;
  - otherwise **CHANCE**.
- **Output:** counts only. No plaintext, key, alphabet name or setting list.

## 5. Budget (`audit/run_bounded_agg.py`; zero retries)
| Job | Wall | CPU | Memory |
|---|---|---|---|
| Gate | 300 s | 240 s | 1,024 MiB |
| Target | 1,800 s | 1,200 s | 1,024 MiB |

## 6. Order (each step pushed before the next)
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`.
2. Source and hashes.
3. Gate and `holdout/GATE_FROZEN.sha256`.
4. Target inputs and outputs, then `k4/FROZEN.sha256`.
5. Result, ledger row, review note.

## 7. Limits
**Not excluded:**
- free (arbitrary) alphabets: with PA and CA arbitrary, the 11 constraints are generally satisfiable, so no exact
  check exists (shortlist S3);
- keyword alphabets outside the tier;
- other digraphic rules;
- transposition layers;
- insertion or deletion;
- simultaneous errors at two pairs.

The exact contradiction is language-independent, but it assumes the published letters are in place and in order.
Nothing from R98 enters any blind search.
