# R102 pre-registration (Claude Code, 25 Nov 2026): S3b algebra — the two-free-alphabet plaintext autokey

**Type: analysis with synthetic verification. No K4 input of any kind** (no ciphertext and no published letter).
- **Batch:** `audit/reviews/BATCH_WORK_ORDER_R102_R107.md`, item R102.
- **Approval:** the batch was endorsed by Tyler, 25 Nov 2026 ("This seems like a better approach for you to do more
  work").
- **Procedure:** `audit/OPERATING_PROCEDURE_ROLLING.md`.
- **Dependencies:** none. Nothing here relies on R98–R101.

**Independent review: NONE** (one model). The round is part of ChatGPT's next audit batch.

## 1. Model
For i ≥ L:

    B⁻¹(C_i) = s1·A⁻¹(P_i) + s2·F⁻¹(P_{i−L}) + c   (mod 26).

For i < L: B⁻¹(C_i) = s1·A⁻¹(P_i) + k_i.

**Parameters:**
- A and B are any of 26! alphabets;
- F ∈ {A, B, AZ};
- s1, s2 = ±1;
- c ∈ Z26;
- the primer k is any sequence;
- L ∈ 1..96.

The reference encryptor is `r100/autokey100.py` (sha256 in `PROTOCOL.sha256`).

## 2. Claims (each checked by a registered computation in §3)
**T1. Latin-square reduction.**
- **Definitions:** α = s1·A⁻¹, β = s2·F⁻¹, and γ(z) = B[z + c].
- **Claim:** C_i = γ(α(P_i) + β(P_{i−L})) for every i ≥ L.
- **Consequence:** each ciphertext letter is the entry of a Latin square g(a, b) = γ(β(a) + α(b)), isotopic to
  (Z26, +), at the plaintext pair (P_{i−L}, P_i).
- **The F modes tie the maps together:**
  - F = A: β = s1·s2·α;
  - F = B: β = s2·(γ⁻¹ + c);
  - F = AZ: β = s2·(rank in A–Z).

**T2. Gauge.** For any t, u ∈ Z26 and unit k ∈ Z26*, the triple (k(α + t), k(β + u), γ(k⁻¹·z − t − u)) gives the same
square. The key space is therefore about (26!)² (α and γ, tied as above), up to a gauge group of 26·26·12.

**T3. Exact consistency test for a closed hypothesis.**
- **Definition:** a hypothesis P is *closed* if, for every known position i ≥ L, P_{i−L} is also known. A prefix of
  any length and a full plaintext are closed.
- **Claim:** a closed hypothesis is consistent with C (some A, B, c and primer encrypt it to C at every known
  position) iff the linear system

      b(C_i) − s1·a(P_i) − s2·f(P_{i−L}) − c ≡ 0,

  over the known i ≥ L, has a solution in which a = A⁻¹ and b = B⁻¹ are both **bijective** on the letters they
  involve. Here f = a, b or the A–Z rank.
- **For a hypothesis that is not closed** (scattered known letters, such as crib windows), the same equations from
  the direct pairs are **necessary but not sufficient**.

**Solver** (`r102/s3b102.py`, primary). It extends R101's method:
- solve the system mod 13 and mod 2;
- enumerate the mod-13 solution space, requiring each value at most twice within the a-letters and within the
  b-letters;
- solve a GF(2) separation system for both groups;
- output a **witness** (a, b, c) when the hypothesis is consistent.

Cells whose mod-13 solution dimension is > 7 are UNDECIDED.

**Second solver** (`r102/dfs102.py`). A depth-first search mod 26 with forward checking: every coefficient is a
unit, so an equation with one unknown forces it. It has a node cap; on reaching the cap the result is UNDECIDED.

**T4. Crib-only underdetermination (why S3b has no exact crib check).** On scattered windows like the published
letters' shape, the direct-pair equations number at most ~22, against up to 53 unknowns. So almost every random
input passes, and no exact exclusion is possible.

**T5. Ciphertext-only prediction.** Because C_i and C_{i+L} share P_i, a repeated plaintext L-spaced trigram
(P_{i−L}, P_i, P_{i+L}) produces a repeated ciphertext pair (C_i, C_{i+L}).

The statistic is R_L(C) = #{i < j : C_i = C_j and C_{i+L} = C_{j+L}}.
- **Prediction:** plants exceed letter-preserving shuffles of themselves at L = 1. The effect is weak at L ≥ 2,
  where spaced trigrams rarely repeat.
- **Reported:** the power at a 5% false-positive rate.

## 3. Registered computations (one run, `r102/run102.py`, seed 1020901)
**Plaintext source:** random 97-letter windows of the Carter 1923 OCR text (`r33/data/source_carter_mace_1923_google_ocr.txt`,
sha256 in `PROTOCOL.sha256`), reduced to A–Z. It is development text, not a sealed holdout. Windows containing a published K4 plaintext word (EASTNORTHEAST, NORTHEAST, BERLIN, CLOCK) are skipped, so no synthetic text carries a clue word.

| Check | Pass condition |
|---|---|
| C1 (T1) | 400 random cases (A, B, F, L 1–96, signs, c, primer, random text): the identity holds at every i ≥ L. 400/400 |
| C2 (T2) | 200 random (α, β, γ) with random gauges give identical squares. 200/200 |
| C3 (T3 soundness) | 120 planted cases: L ∈ {1, 2, 3, 5, 8, 13, 21, 40}, random A, B, F, signs, c, primer. The true plaintext (full, and the first 60 letters) is CONSISTENT, and the witness re-encrypts to C at every constrained position (verified with `autokey100`). 240/240 |
| C4 (two solvers) | 60 closed hypotheses (30 true, 30 unrelated English windows; lengths 60 and 97): the primary and the DFS agree on every case both decide, and ≥ 40 are decided by both |
| C5 (T4) | 40 synthetic crib-shaped windows (13 + 11 letters at random positions), all F, lags 1–10. The share CONSISTENT under the direct-pair conditions is reported; prediction ≥ 90% |
| C6 (T5) | 200 plants and 200 shuffles of those plants, at L = 1, 2, 3: R_L's distributions and the power at 5% are reported (prediction, not a gate) |

**Verdict:** VERIFIED if C1–C4 pass; C5 and C6 are reported. Any failure in C1–C4 is a stop condition.

**Budget:** `audit/run_bounded_agg.py`, 1,800 s wall / 1,800 s CPU / 2,048 MiB, zero retries.

## 4. Order
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`.
2. Source and `SOURCE.sha256`.
3. The run, then `OUTPUTS.sha256`.
4. The result note.

Nothing from R102 touches K4.
