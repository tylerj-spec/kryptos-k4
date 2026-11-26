# R107 pre-registration (Claude Code, 26 Nov 2026): does a periodic or keyword key make free-alphabet Slidefair testable?

**Type: analysis + synthetic verification. No K4 input of any kind.**
- **Batch:** `audit/reviews/BATCH_WORK_ORDER_R102_R107.md`, item R107 (an independent branch, authorized at once).
- **Procedure:** `audit/OPERATING_PROCEDURE_ROLLING.md`.
- **Dependencies:** none on unverified results. R107 uses R98's reference cipher `r98/slidefair98.py` (L187, audit
  batch A) only as an encryptor, and T1 below re-verifies every property used.

**Independent review: NONE** (one model). Batch B (R102–R105) is closed and awaits ChatGPT; R107 opens audit batch C.

## 1. Question
R98 excluded Slidefair with keyword alphabets from R76's tier under **any** key (L187). Free (arbitrary) alphabets
were left open (shortlist S3) because, with any key, they looked untestable. The batch asks whether a **structured
key** changes that: a key that repeats over the pairs with period p, which includes every keyword key of length p.

## 2. Algebra (claims, verified by T1)
Notation: a = PA⁻¹ and b = CA⁻¹ are the ranks in the two free alphabets. For one pair, u is the upper (PA-row) input,
w the lower input, k the key value, cu the upper output and cl the lower output. The 16 conventions of R98 fix which
plaintext and ciphertext positions play which role.

| Case | Vigenère (or Variant) slide | Beaufort slide |
|---|---|---|
| Normal (columns differ) | a(cu) = b(w) − k,  b(cl) = a(u) + k | a(cu) = k − b(w),  b(cl) = k − a(u) |
| Same column (R98's rule: letters to the right) | a(cu) = a(u) + 1,  b(cl) = b(w) + 1 | a(cu) = a(u) + 1,  b(cl) = b(w) − 1 |

**Consequences:**
1. **Letter identity.** cu ≠ u in every pair, under every convention, alphabet and key.
2. **Reciprocal pair map.** In the normal case, (u, w) ↦ (σ_k(w), σ_k⁻¹(u)), with σ_k = PA ∘ (x ↦ x − k) ∘ CA⁻¹
   (Vigenère) or PA ∘ (x ↦ k − x) ∘ CA⁻¹ (Beaufort).
3. **Alignment.** Each ciphertext letter is σ_k or σ_k⁻¹ of one plaintext letter of its pair:
   - for the 8 conventions where the output order equals the role order (o = r), the plaintext letter is the
     **other** one of the pair (the pair is swapped);
   - for the 8 where o ≠ r, it is the letter **in place**.
4. **Periodic key.** With period p, the cipher is (a pair swap, or nothing) followed by 2p substitution slots, which
   are tied to the two alphabets. This holds except at same-column pairs (about 1 pair in 26).
5. **Exact crib check.** With a periodic key, each fully known crib pair gives two homogeneous linear equations mod 26
   in (a, b, k_{j mod p}), plus the letter identity. Without a key period, the two equations of each pair have their
   own k, so only their key-free sum constrains a and b.

**Overlap with the ledger:**
- For o ≠ r and no same-column crib pair, consequence 4 makes periodic Slidefair a special case of L21 (per-slot
  arbitrary bijections in place, m = 2p).
- For o = r it is L21's model after a pair swap, which L21 did not test.
- L89's per-column repetition statistic applies at m = 2p to the aligned text (T5).
- X107 is stronger than either:
  - it uses the tying of all slots to two alphabets;
  - it covers both alignments;
  - it allows one same-column or wrong pair (DROP).

## 3. The check X107 (fixed here; source `r107/x107.py`)
**Inputs:**
- a ciphertext;
- a partial plaintext hypothesis;
- one of the 16 conventions;
- a period p ≥ 1, or "any key" (one free value per pair).

Only crib pairs with both plaintext letters given are used.

**Branches.** EXACT treats every crib pair as normal. DROP_q sets crib pair q aside; this covers any same-column rule
or any error at that one pair.

**Exclusion rule.** A branch is **excluded** if either holds:
- a kept pair has cu = u; or
- the homogeneous normal-case system forces a collision:
  - two distinct letters of one alphabet are equal mod 2 and equal mod 13 on every solution; or
  - three letters are equal mod 13. Only two residues mod 26 share a residue mod 13.

Forced equality comes from the null space mod 2 and mod 13. Every condition is necessary for a valid key, so an
exclusion is sound.

**Outputs:**
- EXCLUDED_DROP: EXACT and every DROP_q are excluded;
- EXCLUDED_EXACT: only EXACT is excluded;
- OPEN.

**OPEN is not a consistency proof.**

**Reference.** `r107/ref107.py` decides forced equality by a different route: x and y are forced equal mod p if and
only if e_x − e_y lies in the row space, which it tests by rank, with no null space.

## 4. Registered computations (seed 1070901)
**Masks:** two random windows of 13 and 11 letters, non-overlapping, as R102 C5. The published crib positions are not
used.

| Step | What | Size and pass rule |
|---|---|---|
| **T1 structure** | Against `r98/slidefair98.py`, every pair satisfies: the table (normal or same column); the letter identity; the round trip; the reciprocal pair map; and, for normal pairs, the alignment of consequence 3. Random plaintext, random free alphabets, all 16 conventions, periodic keys p 1–12 | 400 messages (19,200 pairs), **0 failures** |
| **T2 soundness** | Carter windows encrypted with random free alphabets, conventions cycling, p ∈ {1, …, 12, 16, 24, any}, masked. X107 never gives EXCLUDED_EXACT or EXCLUDED_DROP when no crib pair is same-column, and never EXCLUDED_DROP when at most one is | 400 plants, **0 failures** |
| **T3 two implementations** | X107 with the null-space test and with the rank reference give the same verdict | every cell of T2 plus every cell of the first 10 messages of T4 (2,960 cells), **0 disagreements** |
| **T4 chance power** | Uniform random ciphertexts with random plaintext in the masks: share of EXCLUDED_DROP and of EXCLUDED_EXACT ∪ EXCLUDED_DROP | 60 messages × 16 conventions × each p in {1, …, 12, 16, 24, 36, any}. Any key equals every p ≥ 48 (at most 48 pairs) |
| T5 ciphertext-only invariant (exploratory) | For plants with p 1–6, the per-column repetition count T_{2p} of the ciphertext against that of the aligned plaintext (consequence 3). Report the share equal, and the mean absolute difference; same-column pairs make them differ | 120 plants |

## 5. Verdict per period (registered)
If T1–T3 pass, each p (and "any key") gets one label:
- **TESTABLE** if the T4 EXCLUDED_DROP share is ≥ 0.50;
- **WEAK** if only the EXCLUDED_EXACT ∪ DROP share is ≥ 0.50;
- **NOT_TESTABLE** otherwise.

A failure of T1–T3 is a stop condition.

**Development figures** (seeds 1071–1074; not this run):

| Item | Dev result |
|---|---|
| T1-style check | 19,200 pairs, 0 failures; 743 same-column (3.9%) |
| Soundness | 300 plants, 0 unsound |
| Two implementations | 3,200 cells, 0 disagreements; a reduced smoke run of the registered script (seed 97) gave 2,960 more, also 0 |
| Chance power, EXCLUDED_DROP | p 1–2 1.00; p 3 0.975; p 4 0.90; p 5 0.76; p 6 0.72; p 8 0.58; p 10 0.54; p 12 0.49; p 16 0.35; p 24 0.33; any key 0.22 |
| Chance power, EXCLUDED_EXACT or DROP | p 1–2 1.00 down to p 12 0.81, p 24 0.70, any key 0.65 |

**What a TESTABLE label leads to.** A K4 run of X107 would be a separately registered, crib-assisted, exclusion-only
round under the usual gate, and is **proposed for approval**, not run here. Nothing from R107 enters a blind search.

**Budget:** `audit/run_bounded_agg.py`, 1,800 s / 1,800 s / 2,048 MiB, zero retries. Development estimate about
300 s, most of it in the rank reference.

## 6. Order
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`, pushed alone.
2. Source and `SOURCE.sha256`.
3. The run, then `run_v1/OUTPUTS.sha256`.
4. The result note.
