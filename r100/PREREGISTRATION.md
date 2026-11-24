# R100 pre-registration (Claude Code, 24 Nov 2026): Quagmire-type plaintext autokey with two tier alphabets — exact scope

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY (type B, charter §5).** It decodes nothing, completes no
key and publishes no surviving setting.

**Approval:** Tyler, 24 Nov 2026: "continue with the plan", pointing to PR #113, the post-R96 plan in
`audit/reviews/POST_R96_NEXT_STEPS_20261123.md`.
- **The plan's open item:** the construction-discovery lane allows up to three mechanisms. R98 and R99 used two.
  The fresh gate is unreachable, because R97 failed.
- **This round:** the lane's third slot. It is choice 1 of `audit/reviews/CONSTRUCTION_LANE_REVIEW_20261124.md`.

**Independent review: NONE** (one model). ChatGPT is the named reviewer. No different-model review of R98 or R99
exists yet; the PR #113 branch has no new commits.

## 1. Model (exact)
Positions are 0-based; there are 97 letters. **A** is the plaintext alphabet and **B** the ciphertext alphabet; both
range over R76's large tier (77,229 orderings, sha256 563ae44a…), and A = B is allowed. The feedback ranks use
**F ∈ {A, B, AZ}**: the plaintext alphabet, the ciphertext alphabet (the Quagmire key-letter convention), or the
straight alphabet.

**Encryption:**
- B⁻¹(C_i) = s1·A⁻¹(P_i) + s2·F⁻¹(P_{i−L}) + c (mod 26) for i ≥ L;
- B⁻¹(C_i) = s1·A⁻¹(P_i) + k_i for i < L.

Here (s1, s2) ∈ {±1}², the constant c ∈ Z26 absorbs any indicator offset, the primer k is any sequence, and the lag
is L ∈ 1..96.

**Named cases** (all with F = B, the key letter located in the cipher alphabet):
- Quagmire I autokey: B = AZ;
- Quagmire II: A = AZ;
- Quagmire III: A = B;
- Quagmire IV: A ≠ B, both keyword alphabets.

**Labelled settings:** 77,229² × 4 × 3 = 7.157 × 10¹⁰ per lag.

## 2. The check: necessary conditions from the direct links
A **direct link** is a pair (i, j = i + L) with both plaintext letters published. Each gives

    B⁻¹(C_j) − s2·F⁻¹(P_i) − s1·A⁻¹(P_j) ≡ c.

Each side depends on one alphabet only:
- the **B-side** g holds B⁻¹(C_j), together with −s2·B⁻¹(P_i) when F = B or −s2·AZ(P_i) when F = AZ;
- the **A-side** h holds s1·A⁻¹(P_j), together with +s2·A⁻¹(P_i) when F = A.

**Eliminating c.** The constant c is eliminated against the first link. A pair (A, B) satisfies all m links iff the
code of (g_k − g_0)_k computed over B equals the code of (h_k − h_0)_k computed over A. So all 77,229² pairs are
counted by a sort-and-search join, exactly and for every c and every primer.
- A join uses at most the first 10 links (9 differences, exact in float64).
- When a lag has more links, every matched pair is verified directly on all its links.

**Why only direct links.** Chains through unpublished positions (L27's "anchor chain") are not used. With F ≠ A they
compose the two alphabets non-linearly. So the check is **necessary, not sufficient**:
- a count of 0 is an exact exclusion;
- a non-zero count only says "not excluded by these links".

**Two screens.**
- **EXACT:** the setting fits every direct link of the lag.
- **DROP:** the setting fits after one published position p is set aside, which removes the ≤ 2 links that use p.
  - This covers one wrong published letter.
  - It also covers one wrong ciphertext letter at a published position, because a direct link reads ciphertext only
    at its own published endpoint j.
  - DROP counts the distinct (A, B, signs, F) feasible for some p.
  - **How it is computed:** the link graph's components are split into two groups that no single cut touches
    together. Candidates are the pairs that fit either group fully, and each candidate is then verified against
    every cut.

**Chance and scanned lags.** A setting passes EXACT by chance with probability about 26^(1−m) at m links. The DROP
estimate below multiplies by up to 24 positions to cut, and each cut removes up to 2 links.

| Screen | Requirement | Expected chance per lag | Lags |
|---|---|---|---|
| EXACT | m ≥ 10 direct links | ≤ 0.013 | 1–7 and 39–43 (12 lags) |
| DROP | m ≥ 14 direct links | ≤ 5 × 10⁻⁴ | 1–5 |

Only these lags are scanned. All other lags have fewer than 10 direct links and are **OPEN** for this family.

**Published letters.** The 24 letters at positions 21–33 and 63–73 are read from the `CLUES` literal of
`r73/sealed/reveal_k4.py` (sha256 63121cea…) by `ast` parsing.

## 3. Equivalence (G0) with earlier rows
- **L188 (R99): A = B with F = A,** the full chain criterion. R100's A = B, F = A cases at lags 1–7 and 39–43 are a
  subset of R99's excluded lags, so they must give 0. That serves as a replication check.
- **L172 (R83a PFX, m = 1):** the four named alphabets on every side, at the lags R83 decided. Those cases must also
  give 0 at lags 1–7.
- **L27 / L58:**
  - plain and feedback ranks are AZ or KRYPTOS, and the cipher alphabet is free;
  - that covers the F = A cases with A ∈ {AZ, KRYPTOS} for any B, which were left feasible rather than excluded
    there;
  - R100 decides the tier sub-case exactly, by necessary conditions.
- **L157 (R68 PTAK), L166 (R76 H1X, periodic keys), L17/L169 (ciphertext feedback):** different or narrower.

**New scope:** a plaintext autokey with two different tier alphabets (Quagmire I/II/IV types), at every lag with ≥ 10
direct links.

## 4. Correctness gate (EXACT_CHECKER_CORRECTNESS; synthetic only; seed 1000901; budget file `budgets/GATE_BUDGET.json`)
| Check | Pass condition |
|---|---|
| V1 cipher | Reference encrypt and decrypt round-trip on 400 random texts × random A, B, F, L 1–96, signs, c and primer |
| V2 brute-force oracle | A 16-alphabet sub-tier (A–Z + 15 drawn), so 256 (A, B) pairs. 16 inputs: 8 planted on random 13- and 11-letter windows, 8 random with short windows. Each uses 6 random lags with ≥ 2 links plus the planted lag. DROP is computed on the chosen lags with ≥ 6 links. The oracle tries every c ∈ 0..25 with the reference **encryptor**, link by link. The fast path's and the simple path's (EXACT, DROP) must equal the oracle's for every (L, signs, F), and ≥ 4 inputs must have EXACT > 0 |
| V2b simple-path agreement | On a 300-alphabet sub-tier, 8 inputs on random 13- and 11-letter windows (4 planted), every lag with ≥ 10 links, DROP at every lag with ≥ 14 links: the fast path equals the simple path (direct residuals over all 90,000 pairs) |
| V3 full-tier plants | 32 plants on random 13- and 11-letter windows (not the K4 positions), with random A, B, F, signs, c and primer. 16 use a lag with ≥ 14 links, 16 a lag with 10–13. Each must be counted in EXACT. For the 16 DROP-lag plants: with one published letter corrupted on a link, and separately with the ciphertext letter at a link's endpoint corrupted, each must be counted in DROP |
| V4 Quagmire cases | 4 plants each of Quagmire I, II, III and IV autokeys (F = B) are found by the full-tier scan |
| V5 throughput | The full scan (12 EXACT lags × 4 signs × 3 F, DROP at 5 lags) on 3 synthetic K4-shaped inputs, plus one planted input that must be found. Forecast 2 × max per-input wall/CPU × 101 + 10 s < 80% of the target caps |

Any mismatch is NO-GO, and an incomplete run is INCOMPLETE. Either blocks the target; no retry.

## 5. Target (once, after the gate's GO is pushed)
- **Inputs:** the unchanged K4 ciphertext (`r39/ic_gate/k4_ciphertext.txt`, sha256 2797de14…) plus **100**
  frequency-preserving shuffles. They are made with `random.Random(1000400)`, list shuffle, rejecting the original
  and duplicates, cap 10,000.
- **Why 100 shuffles, not 200:** a scan costs about 3.5 s CPU per input on one thread. The R83 and R68 rounds used
  100.
- **Per input and lag, only:** link count, EXACT-feasible settings, and DROP-feasible settings (lags 1–5).

**Decision:**
- **EXCLUDED** if K4 has EXACT 0 at all 12 scanned lags and DROP 0 at lags 1–5;
- **LEAD** if K4's EXACT total or its DROP total is positive and above every shuffle's;
- otherwise **CHANCE**.

**Output:** counts only. No plaintext, key, alphabet name or setting list.

## 6. Budget (`audit/run_bounded_agg.py`; zero retries; BLAS pinned to one thread)
| Job | Wall | CPU | Memory |
|---|---|---|---|
| Gate | 300 s | 240 s | 1,024 MiB |
| Target | 1,800 s | 1,200 s | 1,024 MiB |

## 7. Order (each step pushed before the next)
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`.
2. Source and `SOURCE.sha256`.
3. Gate and `holdout/GATE_FROZEN.sha256`.
4. Target, then `k4/FROZEN.sha256`.
5. Evaluation, a post-freeze cross-check of K4 by a second algorithm (per-cut joins with integer codes), the result,
   the ledger row and the review note.

## 8. Limits
**Not excluded:**
- lags with fewer than 10 direct links;
- the information in chains through unpublished positions (not used);
- alphabets outside the tier;
- a keyword combined with the autokey;
- ciphertext autokey;
- transposition;
- insertion or deletion;
- two errors.

**Source caveat.** The ACA's Quagmire pages could not be fetched from this environment. The key-letter convention F
covers the three natural readings, and c covers any indicator position.

Nothing from R100 enters any blind search.
