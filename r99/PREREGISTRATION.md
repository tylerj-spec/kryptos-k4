# R99 pre-registration (Claude Code, 24 Nov 2026): K1/K2's keyed tableau with a plaintext autokey (Condi type), any tier alphabet — exact scope

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY (type B, charter §5).** It decodes nothing, completes no
key and publishes no surviving setting.

**Approval:** Tyler, 24 Nov 2026: "Go for it & all necessary follow on actions until you've worked your way thru
enough of the plan for review". This is shortlist item S2 of `audit/reviews/CONSTRUCTION_SHORTLIST_20261124.md`. It
is run because S1 closed (R98, L187: EXCLUDED).

**Independent review: NONE** (one model). ChatGPT is the named reviewer.

## 1. Model (exact)
Positions are 0-based; there are 97 letters. A is one 26-letter alphabet, used for the plaintext ranks, the
ciphertext ranks and the feedback ranks, as in K1/K2's tableau. Write x_i = IDX_A[P_i] and y_i = IDX_A[C_i].

**Encryption:** y_i = s1·x_i + s2·x_{i−L} + c (mod 26) for i ≥ L, and y_i = s1·x_i + k_i for i < L.
- **Lag** L ∈ 1..96.
- **Signs** (s1, s2) ∈ {+1, −1}²:
  - (+, +): Vigenère autokey on a keyed tableau, the Quagmire III / K1–K2 style. ACA Condi is L = 1, (+, +),
    c = 1 with 1-based numbering.
  - (+, −): Variant.
  - (−, +): Beaufort.
  - (−, −): the reversed-rank Vigenère.
- **Constant** c ∈ Z26: any fixed offset, such as a 1-based numbering or a constant key letter.
- **Primer:** k_0..k_{L−1}, any.

**Decryption:** x_i = s1·(y_i − s2·x_{i−L} − c).

**Alphabets:** A ranges over R76's large tier: `r76/alphabets.py large_tier()`, 77,229 orderings, sha256 of the
newline-joined orderings 563ae44a…. It is the same tier as R98.

**Labelled settings:** 77,229 × 4 × 96 = 29,655,936 (A, signs, L), each with any c and any primer.

## 2. The exact criterion (every c and every primer decided)
Let σ = −s1·s2. Decryption gives x_q = σ·x_{q−L} + s1·(y_q − c). Iterating t steps along one residue chain mod L:

    x_{i+tL} = σ^t·x_i + s1·Σ_{u=1..t} σ^{t−u}·y_{i+uL} − s1·S_t·c,   where S_t = Σ_{v=0..t−1} σ^v.

**Links.** Sort the published positions within each chain mod L. Each consecutive published pair (i, j = i + tL) is a
**link**, giving one congruence in c alone:

    a·c ≡ b (mod 26),  a = −s1·S_t,  b = x_j − σ^t·x_i − s1·Σ_{u=1..t} σ^{t−u}·y_{i+uL}.

**Criterion.** A setting (A, L, s1, s2) is feasible iff some c ∈ Z26 satisfies every link.
- **Necessity:** decryption is deterministic given c and the primer.
- **Sufficiency:**
  - the primer is free and fixes each chain's letters before its first published position;
  - letters after a chain's last published position are free;
  - so the links are the only constraints.

This is the complete chain criterion, the same structure as L27's "anchor chain".

**Two screens.**
- **EXACT:** feasible with every link.
- **DROP:** feasible after cutting the chain at one published position p, which removes the ≤ 2 links adjacent to p.

  This covers:
  - one wrong published letter;
  - or one wrong ciphertext letter anywhere, because a ciphertext letter lies on at most one link.

  DROP counts the distinct settings feasible for at least one p.

**Link counts per lag** (from the 24 published positions only):
- 23 at L = 1, falling to 11 at L = 13–14;
- 7–11 at L = 15–23;
- 5, 3 and 1 at L = 24–26;
- 1–11 at L = 30–52, peaking at L = 40–42;
- **none** at L = 27–29 and 53–96.

Lags with no link carry no information and stay **OPEN**.

**Chance rate.** A setting passes EXACT by chance with probability about 26^(1−k) at k links; 308,916 settings are
tested per lag.
- **EXACT-decided lags:** k ≥ 6, where the expected chance count is < 0.03 per lag. These are L = 1–23 and 35–47.
- **DROP-decided lags:** k ≥ 9, because a cut removes up to 2 links. These are L = 1–15, 19–22 and 38–44.

The shuffles calibrate the effect of alphabet structure.

**Published letters.** The 24 letters at 0-based positions 21–33 and 63–73 are read from the `CLUES` literal of
`r73/sealed/reveal_k4.py` (sha256 63121cea…) by `ast` parsing.

## 3. Equivalence (G0) with earlier rows
- **L172 (R83a PFX), keyword + plaintext autokey with m = 1:** covers A ∈ {AZ, KRYPTOS, PALIMPSEST, ABSCISSA} at the
  lags R83 decided. That is lags 1–10 for m = 1 (`r83/RESULT.md`). In R99 those cases act as a **replication**: they
  must give 0 if R83 is right.
- **L157 (R68 PTAK):**
  - AZ/KRYPTOS plaintext autokey, lags 1–96, **without** the constant c;
  - R99 adds c and every other tier alphabet.
- **L27 / L58 (autoclave):**
  - a free cipher alphabet with AZ or KRYPTOS plain and feedback ranks;
  - that is wider in the cipher alphabet but limited to two rank alphabets, and their 257 / 269 feasible settings are
    not exclusions;
  - R99's A = AZ / KRYPTOS cases are sub-cases of those feasible families, which R99 can decide exactly.
- **L166 (R76 H1X):** the same keyed-tableau method and the same tier, but with **repeating** keys (periods 2–52),
  not autokeys.
- **L17, L169:** ciphertext feedback, a different family.

**New scope:** plaintext autokey on any of the other ~77,225 tier alphabets at every lag, plus the constant c on
AZ/KRYPTOS beyond R83's lags.

## 4. Correctness gate (EXACT_CHECKER_CORRECTNESS; synthetic only; before any target computation)
Gate seed **990901**. The gate budget file is `r99/budgets/GATE_BUDGET.json`.

| Check | Pass condition |
|---|---|
| V1 cipher | Reference encrypt and decrypt round-trip on 400 random texts × random A, L 1–96, signs, c and primer |
| V2 brute-force oracle | On one 120-alphabet sub-tier (A–Z + 119 drawn), 30 inputs (15 planted on random 13- and 11-letter windows, 15 random with short windows so chance fits occur), every lag with a link, 4 signs. The oracle propagates each link with the reference **decryptor**, one letter at a time, for each c ∈ 0..25. The EXACT and DROP counts of both checker paths (fast mask path and simple path) must equal the oracle's per (L, signs), and at least 10 inputs must have EXACT > 0 |
| V3 full-tier plants | 32 plants: random A from the full tier, random signs, c and primer, a lag with ≥ 6 links on random 13- and 11-letter windows (not the K4 positions). Each must be counted in EXACT. With one published letter corrupted, it must be counted in DROP. With one ciphertext letter corrupted on a link, it must be counted in DROP |
| V4 Condi | 16 encryptions by a separately written ACA Condi function (keyed alphabet numbered 1–26; the first shift is a start number; each later shift is the number of the previous plaintext letter) are found at L = 1, (+, +) |
| V5 throughput | The full fast scan (every lag with a link × 4 signs × 77,229) on 3 synthetic inputs. The simple path must agree on one of them at 3 random lags with links (all 4 signs). The planted full scan must find its plant. Forecast 2 × max per-input wall/CPU × 201 + 10 s < 80% of the target caps |

Any mismatch is NO-GO, and an incomplete run is INCOMPLETE. Either blocks the target; no retry.

## 5. Target (once, after the gate's GO is pushed)
- **Inputs:** the unchanged K4 ciphertext (`r39/ic_gate/k4_ciphertext.txt`, sha256 2797de14…) plus **200**
  frequency-preserving shuffles. They are made with `random.Random(990400)`, list shuffle, rejecting the original and
  duplicates, cap 10,000.
- **Per input and lag, only:** link count, EXACT-feasible settings, DROP-feasible settings.

**Decision per lag:**
- **EXCL** if K4's count is 0 (EXACT, or DROP for the DROP screen);
- otherwise **FEAS**, reported with K4's rank among the shuffles.

**Family decision:**
- **EXCLUDED** if K4 has EXACT 0 in every EXACT-decided lag and DROP 0 in every DROP-decided lag;
- **LEAD** if K4's EXACT total over the EXACT-decided lags, or its DROP total over the DROP-decided lags, is
  positive and above every shuffle's;
- otherwise **CHANCE**.

Weak lags (k 1–5) are reported only descriptively.

**Output:** counts only. No plaintext, key, alphabet name or setting list.

## 6. Budget (`audit/run_bounded_agg.py`; zero retries)
| Job | Wall | CPU | Memory |
|---|---|---|---|
| Gate | 300 s | 240 s | 1,024 MiB |
| Target | 1,800 s | 1,200 s | 1,024 MiB |

## 7. Order (each step pushed before the next)
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`.
2. Source and `SOURCE.sha256`.
3. Gate and `holdout/GATE_FROZEN.sha256`.
4. Target, then `k4/FROZEN.sha256`.
5. Evaluation, result, ledger row, review note.

## 8. Limits
**Not excluded:**
- lags 27–29 and 53–96 (no information);
- separate plain, cipher and feedback alphabets (for example Quagmire I/II/IV autokeys), except as already covered by
  L27/L58/L172;
- keyed alphabets outside the tier;
- a keyword combined with the autokey (m > 1, R83 PFX only for the four named alphabets);
- ciphertext autokey;
- transposition;
- insertion or deletion;
- two errors.

**Source caveat.** The ACA's own Condi page could not be fetched from this environment. Condi's definition (V4)
follows standard descriptions, and the general family (all signs, any c) contains it.

The exact contradiction is language-independent, but it assumes the published letters are in place and in order.
Nothing from R99 enters any blind search.
