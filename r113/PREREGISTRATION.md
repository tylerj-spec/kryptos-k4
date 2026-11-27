# R113 pre-registration (Claude Code, 27 Nov 2026): P5 step 1, does a lag-21-adjacency transposition plus periodic substitution explain R₂₁ = 11? (synthetic)

**Type: synthetic simulation. No K4 input.** Two published K4 constants serve as thresholds: K4's IC (0.03608, from
R71) and R₂₁ = 11 (R71, L160; R110, L198). No K4 letter is read.

**Approval:** Tyler, 27 Nov 2026: "continue on along with any logical next steps that you suggest". This is step 1
of P5 in `audit/ROLLING_QUEUE.md`, as worded after `audit/reviews/LAG21_NOVELTY_REVIEW_20261127.md`.

**Independent review: NONE** (one model). R113 joins audit batch C.

## 1. The family (the one lag-21 mechanism not covered by R71 or the ledger)
**Transposition** (0-based positions, n = 97):
- **D37:** C_j = X_{(37·j) mod 97}. Since 37 = 21⁻¹ mod 97, plaintext neighbours m and m + 1 land at ciphertext lag
  +21, wrapping mod 97.
- **D60:** the same with step 60, which places them at lag −21.

No decimation mod 98 or 99 has an inverse of 21, since gcd(21, 98) = 7 and gcd(21, 99) = 3.

**Substitution:** periodic, period p uniform on 2–30, with an independent random alphabet per slot (the most general
periodic form). It is applied either:
- **after** the transposition, indexed by the ciphertext position j; or
- **before** it, indexed by the plaintext position m.

**Arms:** {D37, D60} × {after, before} = **4**, and a **RUNKEY** baseline. RUNKEY is a Vigenère running key from
English, R71's highest baseline, with no transposition.

**Texts:**
- plaintext: Carter OCR windows from the **first half** of the corpus;
- running-key text: from the **second half**.

Both skip windows that contain a published K4 word.

## 2. Measurement
**Per arm:** 100,000 generation attempts. A message is **IC-matched** if its IC lies in [0.0341, 0.0381], which is
K4's 0.03608 ± 0.002.

**On the matched messages:**
- q₁ = P(R₂₁ ≥ 11), with R110's weight n(n − 1)/2;
- q₂ = P(R71count₂₁ ≥ 11), with R71's weight max(n − 1, 0), summed over distinct pairs.

**Also reported:** acceptance rates; q₁ by period band (2–5, 6–10, 11–20, 21–30); and the chained-triple repeat count
at lags (21, 42), as an exploratory prediction.

## 3. Decision (registered stop rule)
**The test.** For each of the 4 arms, compute the conservative ratio:
- **numerator:** the 99% Clopper–Pearson lower bound of the arm's q₁;
- **denominator:** the 99% upper bound of RUNKEY's q₁.

**The decision:**
- **CONTINUE** (P5 step 2 may be proposed) if the conservative ratio is ≥ 10 for at least one arm;
- **CLOSE** otherwise. P5 closes, with no K4 run.

The same test on q₂ is reported for agreement only.

**Seed:** 1130901. **Budget:** `audit/run_bounded_agg.py`, 1,800 s / 1,800 s / 2,048 MiB, zero retries.

**Controls** (gate checks; a failure is a stop condition):
- **C1:** the decimation inverse is right: D37 and D60 decrypt back to the plaintext, and plaintext neighbours land at
  ±21 (mod 97) for 96/96 pairs.
- **C2:** R₂₁ is implemented twice (a Counter, and sorted codes) and agrees on 1,000 random strings.
- **C3:** a sanity arm (D37 with **no** substitution, IC not matched) has a mean R₂₁ far above a shuffle of the same
  messages.
