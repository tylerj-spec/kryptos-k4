# R101 pre-registration (Claude Code, 25 Nov 2026): plaintext autokey on ONE ARBITRARY alphabet (free-alphabet Condi type), lags 1–5 — exact scope

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY (type B, charter §5).** It decodes nothing, completes no
key and publishes no surviving setting.

**Approval:** Tyler, 25 Nov 2026: "Stick with the plan developed that is in git, we are good to continue with it".
- **The plan's next unfinished item:** shortlist S3 (`audit/reviews/CONSTRUCTION_SHORTLIST_20261124.md`), the
  free-alphabet versions of S1 and S2, listed again in `audit/reviews/R100_RESULT.md`.
- **What the G0 work found:** S3 splits in two.
  - **S1 (Slidefair) with free alphabets** still has no exact check. It is left for the type C work order.
  - **S2 with one free alphabet** does have an exact check. In rank space the autokey recursion is linear, so the
    constraints become linear congruences in the 26 unknown ranks (§2).
- **This round:** the exact half. It is also ledger L26's OPEN "unknown-alphabet feedback autokey", in its
  one-alphabet form.

**Independent review: NONE** (one model). ChatGPT is the named reviewer.

## 1. Model (exact)
R99's model (L188), with the alphabet **arbitrary**: any of the 26! orderings.
- **Encryption:** y_i = s1·x_i + s2·x_{i−L} + c (mod 26) for i ≥ L, where x_i = r(P_i), y_i = r(C_i) and r = A⁻¹ is
  the unknown rank function.
- **Primer:** y_i = s1·x_i + k_i for i < L, with k any.
- **Signs:** (s1, s2) ∈ {±1}².
- **Constant:** c ∈ Z26.
- **Lags:** **L ∈ 1..5**.

**Named case:** ACA Condi with any keyed alphabet is L = 1, (+, +).

The reference cipher is R99's `r99/autokey99.py` (sha256 in `PROTOCOL.sha256`), which accepts any 26-letter alphabet.

## 2. The exact criterion (every alphabet, every c and every primer decided)
R99's complete chain criterion (§2 there) holds for any alphabet, because decryption is linear in rank space:
x_q = σ·x_{q−L} + s1·(y_q − c), with σ = −s1·s2.

Each link (i, j = i + tL) between consecutive published letters of a residue chain gives a **homogeneous** linear
congruence in the unknown ranks r(ℓ) and c:

    r(P_j) − σ^t·r(P_i) − s1·Σ_{u=1..t} σ^{t−u}·r(C_{i+uL}) + s1·S_t·c ≡ 0 (mod 26),   S_t = Σ_{v<t} σ^v.

A cell (L, s1, s2) is **feasible** iff some *bijective* r and some c satisfy every link.
- **Necessary and sufficient**, as in R99:
  - the primer is free;
  - letters outside the chains are free;
  - unpublished letters on a chain are A[x_q], which is always a letter.
- **Only letters that occur in the links are unknowns.** The others take the remaining ranks.

**Primary solver** (`r101/freealpha101.py`). It uses 26 = 2·13 and the Chinese remainder theorem.
- Compute the solution spaces mod 13 and mod 2 by Gaussian elimination over the two fields.
- A rank vector is injective mod 26 iff:
  - every value mod 13 occurs at most twice among the involved letters;
  - and the bit mod 2 separates each such pair.
- So enumerate the mod-13 solutions projectively (the system is homogeneous), keep those with every value at most
  twice, and solve the resulting separation system over GF(2).
- **Cap:** it decides every cell whose mod-13 solution space has dimension ≤ 7. Larger cells are recorded as
  UNDECIDED.

**Second solver** (`r101/dfs101.py`). A depth-first search over the ranks mod 26.
- It enumerates c in the outer loop, then assigns the involved letters one at a time, with forward checking:
  - an equation with one unassigned letter whose coefficient is a unit forces that letter;
  - repeated ranks are pruned.
- It does not use the field decomposition, kernels or enumeration.
- It has a node cap; on reaching the cap the result is UNDECIDED.

**Chance rate** (development, synthetic random inputs on the K4 positions' shape). 0 of 104 cells at lags 1–5 were
feasible. Feasible cells begin at lag 6, at 2 of 16. So lags 1–5 are the decidable range, and higher lags are not
run.

**No DROP screen.** Re-solving with each published position set aside costs 24 times as much, and leaves fewer
equations with less power. One wrong letter is therefore **not** covered; it is stated as a limit.

**Published letters.** The 24 letters at positions 21–33 and 63–73 are read from the `CLUES` literal of
`r73/sealed/reveal_k4.py` (sha256 63121cea…) by `ast` parsing.

## 3. Equivalence (G0)
- **L188 (R99)** is the keyword sub-case: 77,229 tier alphabets, every lag. R101 generalizes it to all 26! alphabets
  at lags 1–5.
- **L27 / L58:** a free *cipher* alphabet with fixed AZ/KRYPTOS plain and feedback ranks. That is a different
  constraint shape, so the two do not overlap except where A ∈ {AZ, KRYPTOS}, which L188 already excluded at these
  lags.
- **L17:** a ciphertext autokey with a free alphabet, which is a different family.
- **L26:** this round decides its one-alphabet plaintext-feedback case at lags 1–5.

## 4. Correctness gate (EXACT_CHECKER_CORRECTNESS; synthetic only; seed 1010901; budget `budgets/GATE_BUDGET.json`)
| Check | Pass condition |
|---|---|
| V1 cipher | `autokey99` encrypt and decrypt round-trip on 400 texts with uniformly random alphabets, L 1–5, signs, c and primer |
| V2 soundness on plants | 60 plants (uniformly random alphabet, lag 1–5, signs, c, primer; random 13- and 11-letter windows, not the K4 positions). Every plant the primary decides is feasible (0 misses), and ≥ 50 are decided |
| V3 two-solver agreement | 32 cells on random windows (16 planted, 16 random), lags 1–5. The primary and the DFS agree on every cell both decide, and ≥ 24 cells are decided by both |
| V4 ACA Condi | 16 encryptions by the separately coded `condi_encrypt` with uniformly random alphabets are feasible at L = 1, (+, +) |
| V5 chance rate and throughput | 6 random inputs × 20 cells: feasible fraction reported. Forecast 2 × max per-input wall/CPU × 21 + 10 s < 80% of the target caps |

Any miss or disagreement is NO-GO, and an incomplete run is INCOMPLETE. Either blocks the target; no retry.

## 5. Target (once, after the gate's GO is pushed)
- **Inputs:** the unchanged K4 ciphertext (`r39/ic_gate/k4_ciphertext.txt`, sha256 2797de14…) plus **20**
  frequency-preserving shuffles. They are made with `random.Random(1010400)`, list shuffle, rejecting the original
  and duplicates, cap 10,000.
- **Per input and cell (L 1–5 × 4 signs), only:** link count, mod-13 solution dimension, and FEASIBLE / INFEASIBLE /
  UNDECIDED.

**Decision:**
- **EXCLUDED** if all 20 K4 cells are INFEASIBLE;
- **EXCLUDED_WHERE_DECIDED** if none is FEASIBLE but some are UNDECIDED, with the cells listed;
- **LEAD** if K4 has more FEASIBLE cells than every shuffle;
- otherwise **CHANCE**.

**Output:** counts and statuses only. No plaintext, alphabet or setting.

**Post-freeze:** the DFS solver re-decides K4's 20 cells as a second implementation, and its log is kept.

## 6. Budget (`audit/run_bounded_agg.py`; zero retries)
| Job | Wall | CPU | Memory |
|---|---|---|---|
| Gate | 900 s | 600 s | 1,024 MiB |
| Target | 1,800 s | 1,200 s | 1,024 MiB |
| Post-freeze DFS cross-check (K4 only) | 1,800 s | 1,200 s | 1,024 MiB |

## 7. Order (each step pushed before the next)
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`.
2. Source and `SOURCE.sha256`.
3. Gate and `holdout/GATE_FROZEN.sha256`.
4. Target, then `k4/FROZEN.sha256`.
5. Evaluation, the DFS cross-check, the result, the ledger row and the review note.

## 8. Limits
**Not excluded:**
- lags 6–96;
- one wrong letter (no DROP screen);
- separate plaintext, cipher and feedback alphabets (two free alphabets: the type C half of S3);
- a keyword combined with the autokey;
- ciphertext autokey;
- transposition;
- insertion or deletion.

Nothing from R101 enters any blind search.
