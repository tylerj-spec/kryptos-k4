# R111 pre-registration (Claude Code, 27 Nov 2026): blind K4 run of R105's solver S105, cipher alphabet from a fixed short list

**Mode: BLIND.** The solver gets only the 97-letter ciphertext (hash-checked) and the models registered here. No
published plaintext letter, position, phrase or mask enters the search, scoring or selection. A clue check runs only
after the outputs are frozen and pushed (§5).

**Approval:** Tyler, 27 Nov 2026: "Do the 4 proposals then we'll do the audit". This is proposal P3 of
`audit/ROLLING_QUEUE.md`.

**Dependency (stated deviation from the rolling procedure §3):**
- R111 relies on R105's solver GO (L194). That GO is **not yet independently verified**: it is in audit batch B.
- The procedure would make R111 wait for that audit. Tyler's instruction above explicitly puts the four proposals
  before the audit.
- R111's own sealed gate (§3) re-tests S105 under the exact search R111 uses. Every conclusion stays **provisional
  until batch B is audited**.

**Independent review: NONE** (one model). R111 belongs to audit batch C.

## 1. Model (exact)
**The cipher (R105's mode):**

    B⁻¹(C_i) = s1·A⁻¹(P_i) + s2·A⁻¹(P_{i−L}) + c   (mod 26),   i ≥ L

The first L ciphertext letters use a primer, as in `r100/autokey100.py`.
- **Free:** the plaintext alphabet A (any of 26!), c, the primer, and the signs. The signs are scanned as one
  representative per σ = −s1·s2: (1, −1) for σ = +1 and (1, 1) for σ = −1. R105's G1b proved that (−s1, −s2) with
  A reflected gives the same ciphertext.
- **Cipher alphabet B, registered short list:**
  - `AZ` = ABCDEFGHIJKLMNOPQRSTUVWXYZ;
  - `KRY` = KRYPTOSABCDEFGHIJLMNQUVWXZ, the K1–K3 tableau alphabet.
- **Lag:** L ∈ {1, …, 5}, the range R105 validated.
- **Cells:** 2 × 5 × 2 = **20**, all searched for every input.

**Solver:** `r105/solve105.py`, unchanged (sha256 in `PROTOCOL.sha256`), run once per cell.

**Per-input statistic:** T = the highest S105 score over the 20 cells.

## 2. What R111 can and cannot show
**It can find:** a plaintext under this family that scores like English (R105: right hypotheses scored −424 to −352,
decoys ≤ −459).

**It cannot exclude the family.** S105 recovers 84% of synthetic plants, so a miss is not an exclusion: the label for
a miss is NO_SIGNAL.

**It does not cover:**
- B outside the list;
- lags above 5;
- F ≠ A;
- any transposition or other layer;
- any non-English plaintext.

R109 (P1, crib-assisted) tests the same algebraic family exactly, with both alphabets free. Under the blindness rule,
R111 does **not** use R109's results to choose or skip cells.

## 3. Sealed synthetic gate (`r111/gate111.py`; before any K4 input)
**Seeds:** plants 1110901, solver 1110902.

**Plants.** There are **8**:
- B alternates AZ and KRY;
- L cycles 1–5;
- σ follows +1, +1, −1, −1;
- the sign pair is random within σ;
- A, c and the primer are random;
- each plaintext is a Carter OCR window that contains no published K4 word.

Each plant gets the **full 20-cell search**. A plant is **recovered** if the top-scoring cell is its true (B, L, σ)
and that output has ≥ 90/97 letters right.

**Decoys.** There are **5**, each with the full 20-cell search:
- 3 letter-shuffles of plants 0–2;
- 2 wrong-family ciphertexts: periodic Quagmire III on the KRY alphabet, periods 7 and 8, on fresh Carter windows.

**Re-encryption.** Every output (every cell of every input) re-encrypts to its input at positions L…96 under
`r100/autokey100.py`.

**GO** requires all three:
- ≥ 6/8 plants recovered;
- every recovered plant's T above every decoy's T;
- re-encryption 100%.

Otherwise the result is **NO-GO**: K4 is not run, and nothing is recorded about K4.

**Gate budget:** `audit/run_bounded_agg.py`, 3,600 s wall / 3,600 s CPU / 2,048 MiB, zero retries. The estimate is
260 solves at about 7 s, or about 1,850 s.

## 4. Target (`r111/run_target111.py`; only after the gate's GO and its freeze are pushed)
**Inputs:**
- K4, from `r39/ic_gate/k4_ciphertext.txt` (sha256 2797de14…);
- **15** letter-shuffles of K4 (seed 1110400) as nulls.

**The run:**
- Every input gets the identical full 20-cell search. The solver's random stream is seeded 1110402.
- **Written for every input and cell:** the score, and the re-encryption witness flag.
- **Written for K4 only:** each cell's 97-letter plaintext, A, c′ and offsets.
- No published letter is read.

**Target budget:** 3,600 s wall / 3,600 s CPU / 2,048 MiB, zero retries. The estimate is 320 solves, about 2,250 s.

**Decision** (`r111/evaluate111.py`, from the frozen outputs only):
- **CANDIDATE:** T(K4) is above the T of every null, **and** T(K4) ≥ −440.
  - −440 lies between R105's lowest recovery (−423.6) and its highest decoy (−458.9).
  - A CANDIDATE is a **stop condition** (a possible K4 plaintext): report at once, and make no claim before
    independent review.
- **NO_SIGNAL:** anything else. The family is not excluded.

## 5. Post-freeze clue check (`r111/cluecheck111.py`)
**When:** only after `k4/FROZEN.sha256` and the evaluation are pushed.

**What:** for every K4 cell output, count agreement with the 24 published letters at their positions. The source is
the `CLUES` literal of `r73/sealed/reveal_k4.py` (sha256 63121cea…).

**Labels:**
- **VERIFIED_CANDIDATE:** CANDIDATE, with ≥ 18/24 agreement in the top cell.
- **FALSE_CANDIDATE:** CANDIDATE, with fewer.

The counts are reported for every cell. They change nothing in §4.

## 6. Order
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`, pushed alone.
2. Source and `SOURCE.sha256`.
3. The gate, then `holdout/GATE_FROZEN.sha256` and the manifest's GO, pushed.
4. The target, then `k4/FROZEN.sha256`, pushed.
5. The evaluation, then the clue check, then the result note.
