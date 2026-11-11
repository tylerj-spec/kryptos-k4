# K4 hypotheses for R77 (Claude Code design round, 11 Nov 2026)

Written by reasoning only. **No test was run for this file: no K4 decode, no synthetic run, no code that reads the
published letters.** Two small scripts counted family sizes and check counts from the published *positions* only.
Hand arithmetic on the published letters is marked **(by hand)**; every such result still needs a code confirmation
with a planted control before it goes into the ledger.

Tyler's rule applies to everything below: the published letters may motivate an idea and may be used in a check after
the blind results are frozen. They never choose a key, route or setting in the blind algorithm.

**Rules for every hypothesis** (unchanged from R75/R76):
1. Code and a sealed synthetic gate first. Plants with hidden settings must be recovered; random ciphertexts must give
   nothing confident. No K4 until the gate passes.
2. Blind part: ciphertext only. Freeze, push, verify re-encryption.
3. Only then the exact check with the published letters, labelled crib-assisted.
4. A hit is a full 97-letter decode that clears both cuts (letter model ≥ −1.45, word model ≥ −2.50 per letter) and
   beats every shuffle. Feasibility without a readable decode is not a hit.
5. On any hit: stop, do not tune, report the raw decode and setting.

**Notation.** Positions are 1-based in tables of letters and 0-based (`i` = 0..96) in formulas. A tableau stage is
R75's: `IDX[ca][c] = s·IDX[pa][p] + K (mod 26)`, s = ±1, with the 32 conventions `CONV` of `r75/sealed/exact.py`
(pa, ca in AZ / KRY / PAL / ABS). `K` is the key value at that position. "Small tier" = the 81 alphabets of
`r76/families.py: b1_alphabets()`. "Large tier" = the 77,229 alphabets of `r76/alphabets.py: large_tier()`.

---

## 1. Where the carried-over items stand

| Item (r76) | Status | What I do with it |
|---|---|---|
| H3 three keywords, three stages | Never run | Kept as **H12**, blind only, low odds |
| H4 grid key | R75 F4X: 0 feasible, widths 2–48, **four alphabets only** (L165) | Sharpened into **H9** (keyword alphabets; clock-hand form) |
| H5 physical overlay | Not run. **But L50's row already lists "K4's physical position overlaid with every shift, straight or mirrored" on the 28 × 32 tableau, 96 conventions: EXCL.** r76 said L50 used straight lines only; the ledger text says otherwise | **Not carried.** L50's script is not in this repo, so its layout cannot be audited. If ChatGPT's photo check (`r77/CHATGPT_TABLEAU_CHECK.md`) shows a layout different from 28 × 32, rerun r76's 595,200-method H5 family as a rider. Nothing else depends on the photos |
| Fact A (r76) | Overstated | Corrected: with PA = CA a self-encryption forces K = 0 for the additive form (s = +1) only. For s = −1 it forces K = 2·IDX[pa][p]. With PA ≠ CA it forces nothing |

---

## 2. New facts worked out by hand from the published letters

Pairs, plaintext→ciphertext, 1-based:

`22 E→F, 23 A→L, 24 S→R, 25 T→V, 26 N→Q, 27 O→Q, 28 R→P, 29 T→R, 30 H→N, 31 E→G, 32 A→K, 33 S→S, 34 T→S`
`64 B→N, 65 E→Y, 66 R→P, 67 L→V, 68 I→T, 69 N→T, 70 C→M, 71 L→Z, 72 O→F, 73 C→P, 74 K→K`

Plain A–Z key values used below (A = 0):
- difference c − p: `1 11 25 2 3 2 24 24 6 2 10 0 25 | 12 20 24 10 11 6 10 14 17 13 0`
- sum c + p: `9 11 9 14 3 4 6 10 20 10 10 10 11 | 14 2 6 6 1 6 14 10 19 17 20`

**Fact E (the three doubled ciphertext letters inside the published text).** NO→QQ (26–27), ST→SS (33–34),
IN→TT (68–69). All three sit in columns 5–6 of a 7-wide grid, as do BB (19–20) and ZZ (47–48); R71 measured that
ciphertext-only feature. In any tableau cipher the key step across a double is fixed by the plaintext alphabet:
`K(i+1) − K(i) = −s·(IDX[pa][p(i+1)] − IDX[pa][p(i)])`. Under plain A–Z the three steps are −1, −1, −5.

**Fact F (the sum form is how the carved tableau reads sideways).** The tableau's body cell under header letter H in
the row labelled R is `KRY[(AZ(R) + AZ(H)) mod 26]`. So "plaintext on the row labels, ciphertext on the header, key
letter in the body" is exactly c + p = constant in plain A–Z, with the key letter numbered in the KRYPTOS alphabet.
That may be why R75's key-shape test flagged the A–Z sum form. (The cell formula assumes header A stands over the
first body column; ChatGPT's photo brief, Task 1, checks that.) In that reading the implied key letters are
`CECHPTSDQDDDE | HYSSRSHDNLQ`. The triple D (and K4's triple 10 in any numbering) makes a natural-language
running key very unlikely for this form: prose has a letter three times in a row only across a word boundary, as in
"see each". This convention (pa = ca = AZ, key by KRY,
Beaufort) was inside every earlier 96-convention scan, so the reading adds no new family by itself.

**Closed by hand (C1–C5).** Each is a one-paragraph proof. Each must be coded as a control with planted messages
before it is recorded.

| # | Family (in place) | Why it cannot produce the published letters |
|---|---|---|
| C1 | **Wheel / strip ciphers** (Jefferson, M-94, M-138): any disks, any order, any block length ≥ 2 | Every letter of a block is moved the same number of steps on its own disk. A letter stays itself only at 0 steps, which leaves the whole block unchanged. S→S at 33 has neighbours A→K and T→S. Closes §17 item 4 in place |
| C2 | **Wheatstone "clock" cryptograph**: any outer ring of 27–38 symbols, any inner 26-letter ring, any start | The short hand moves as many cells as the long hand. Same ciphertext letter ⇔ the long hand's travel is ≡ 0 mod 26. SS at 33–34 forces the step S→T to be exactly 26. Positions 24 and 29 are both R, so the travel S→T→N→O→R→T is ≡ 0 mod 26. That travel is 26 + (a closed loop T→…→T = 27t, t = 1..3) ≡ t. Contradiction. With the rings' roles swapped, a doubled ciphertext letter can never occur, and K4 has six |
| C3 | **Any chart at all (26 unrelated row alphabets) with a repeating KRYPTOS, PALIMPSEST or ABSCISSA key** | Periods 7 and 10 are excluded for arbitrary per-slot alphabets (L21). ABSCISSA (period 8) repeats A in adjacent slots and S in slots 3, 6, 7. Merging the slots of equal key letters gives a clash at every phase (e.g. O→Q and O→F in one alphabet) |
| C4 | **One rotor stepping forward once per letter**, contacts in A–Z order, any wiring, any start | Needs R(p + i + φ) = c + i + φ. Positions 27 and 28 give R(15 + φ) = R(19 + φ) = 17 + φ. (Stepping backward, R(p − i) = c − i, is not closed by this pair; it is inside H8b as σ = 25) |
| C5 | **Slidefair** on the plain or the KRYPTOS tableau, any key | Each pair keeps IDX(c1) + IDX(c2) = IDX(p1) + IDX(p2) (or that + 2), whatever the key letter. Pair 23–24 fails one pairing (A–Z: the sums differ by 10; KRYPTOS: 13 against 18) and pair 22–23 fails the other (A–Z: differ by 12; KRYPTOS: 18 against 3) |

C1 and C2 are worth a ledger row once coded: they close two named hand devices for every alphabet.

---

## 3. The hypotheses

| # | Hypothesis in one line | My rough odds | Cost | New? |
|---|---|---|---|---|
| H7 | **Split key**: a repeating keyword plus a second stream (the message's own earlier letters, or sculpture text) | 1–1.5% | about 1 hour | Yes |
| H11 | **The message is its own key**: a K3-style rearranged copy of the plaintext keys the plaintext | 0.5–1% | 2–6 CPU-hours | Yes |
| H9 | **Grid key with a new alphabet keyword** (width 7 first), and the clock-hand form | 0.5–1% | minutes | Sharpens H4 |
| H8 | **Stepping devices**: key advanced by a free function of the previous letter; one free rotor | 0.5% | minutes | Yes (§17 item 5) |
| H10 | **Slidefair with keyword alphabets** (the tableau used on letter pairs) | 0.2% | minutes | Yes (§17 item 11) |
| H12 | Three sculpture keywords, three stages (r76's H3) | under 0.5% | 10 minutes | Carried |

The odds are my judgment after 166 negative rows, not a calculation. Together about 3–5%. I looked for ideas outside
the keyword-tableau-plus-route mould. H7, H8, H10 and H11 are outside it; H9 and H12 are inside it and are here
because they are cheap and still open.

---

## H7. Split key: a keyword plus a second stream

**Statement.** The key at each position is the sum of two parts: a repeating keyword (as in K1/K2) and a second
stream that never repeats. The second stream is either the message itself a fixed distance back (autokey) or text
carved on the sculpture.

**Why.**
- Scheidt spoke of masking the English and of K1–K3 teaching the techniques. An autokey over a keyword cipher is the
  textbook way to hide the keyword's period, and it leaves every letter in place, as Sanborn's clues require.
- Combining two key parts into a working key is the core of Scheidt's later key-management work (from memory;
  motivation only).
- Ciphertext feedback gives a flat letter count. K4's IC is 0.0361.
- The ledger tested each part alone and never the sum:
  - repeating keys: EXCL (L03, L04);
  - autokeys alone: L17, L18, L27, L58, L59, R68 (L157);
  - R55 (L144): feedback with a constant and a ±1 step, no keyword;
  - sums of repeating keys only: L36;
  - K1–K3 text as the whole key: L16, L90.
  I found no row with "known stream + repeating key". The builder should grep once more before pre-registering.

**Definition.** One stage, any convention of `CONV`:

`K[i] = U[(i + φ) mod m] + S[i] (mod 26)`, m in 1..26, U any m values, `S[i] = t·IDX[sa][x[i]]`, t = ±1, sa in A4.

Streams x:
- **CT-L:** `x[i] = c[i−L]`, L in 1..96; S[i] = 0 for i < L.
- **PT-L:** `x[i] = p[i−L]`, L in 1..96; S[i] = 0 for i < L.
- **TXT(T, o, d):** `x[i] = T[o + d·i]`, d = ±1, every offset that fits. T is the K1–K3 plaintext as carved (768
  letters, `k4kit/data/k1k3_plaintext.txt`, first copy of K3 only; see L135) or the K1–K3 ciphertext as carved with
  the `?` marks dropped (768 letters; `archive/2026-10-26_allinone_extras/source_key_extensions/r27_sources.py:
  CIA_CIPHER`). 672 offsets × 2 directions × 2 texts = 2,688 streams.

**H7b, two tableaux.** The stream stage on one convention and the keyword stage on another, in either order. Same
check with R75's two-stage tables: the stream stage is fully known, so it is applied first (or undone first) and
the keyword stage is then an ordinary any-key check.

**Blind part A (fixed methods).** 6,815,232 methods per ciphertext:
- keys: KRYPTOS, PALIMPSEST, ABSCISSA at every phase (25) and the other 77 words of `r75/data/kryptos_words.txt` at
  phase 0 (102 key rows);
- streams: CT-L and PT-L for L in 1..48 (96), plus the 2,688 text streams (2,784);
- conventions: (text alphabet, key-and-stream alphabet) in {(AZ, AZ), (KRY, KRY), (AZ, KRY), (KRY, AZ)} with
  pa = ca, × VIG / BEAU / VARB × t = ±1 (24).

Scan with the R76 runner. PT-L decodes left to right.

**Blind part B (any keyword, ciphertext feedback).** For CT-L the feedback can be removed from the ciphertext alone:
`u[i] = IDX[ca][c[i]] − S[i]`. What is left is a plain repeating-key cipher on u. For each L in 1..48, each of the 24
conventions and each m in 2..12: choose every key letter by the unigram fit of its column, then three sweeps of
coordinate ascent on the letter model. 12,672 solves per ciphertext. This is a ciphertext-only solver with no word
list.

**Sealed gate.** 60 positives (20 part-A keyword plants, 20 text-stream plants, 20 CT-L plants with random keys of
length 4–10) and 100 negatives, hidden settings. Bars as in R76: at least 54/60 recovered and confident, 0/100
negatives confident. Report part B's recovery by key length; I expect it to fade above m = 8, and the exact check
covers that range.

**Exact check H7X (crib-assisted, after the freeze).** `R = kall(c, pos, pk) − S[pos]`, then
`group_check(pos % m, R)`.
- CT-L and TXT: every published position is usable. Checks per period: 23 at m = 1 falling to 5 at m = 24. Use
  m in 1..24.
- PT-L: only positions whose source letter is also published. Lags 1–9 and 34–48 have 5 or more usable positions.
  Count checks as usable positions minus distinct slots; require 5.
- Size: about 2,880 streams × 24 periods × 32 conventions × 8 (sa, t) ≈ 18 million settings. Expected chance
  passes: about 0.1 in total. Shuffles confirm.
- Decode every feasible setting: slots pinned by the published letters as forced; the rest by
  `exact76.complete_periodic` with S added.

**Controls.**
- S ≡ 0 must reproduce F0X: 0 feasible for m in 1..24.
- CT-L with m = 1 must be infeasible for L in 1..67 (L17).
- K1–K3 plaintext with m = 1 must be infeasible (L90).
- 20 shuffles: about 0 feasible.

**Reuse.** `r75/sealed/exact.py: kall, group_check, decode_indexed`; `r76/sealed/exact76.py: complete_periodic`;
`r75/blind/run.py`; `r76/sealed/make_holdout.py, gate.py`.
**Cost.** Blind A about 15 minutes per batch of 100 ciphertexts on 4 cores (R76 did 13.7 million methods in about
20). Blind B under an hour. H7X minutes.
**Outside facts.** None needed. The K1–K3 ciphertext is the CIA transcription already in the archive.

---

## H11. The message is its own key (a rearranged copy)

**Statement.** Sanborn wrote out the plaintext, rearranged a copy of it with a K3-style sheet operation, and used
the rearranged copy as the running key for a K1/K2-style tableau. There is no keyword.

**Why.**
- It uses exactly the two techniques K1–K3 teach and nothing else. It also fits the PALIMPSEST idea of a text
  written over itself.
- The key is English letters in scrambled order. It has no word structure, so R59's and R61's running-key solvers
  (L149, L150), which need the key to read as prose, could not see it.
- **It is keyless, so the ciphertext alone decides it.** Follow each cycle of the rearrangement: one guessed letter
  fixes the whole cycle, and the guess must agree with itself when the cycle closes. That gives a real blind solver
  with no search over keys.
- Not in the ledger as far as I can find:
  - L27 / L58 / L59 are the fixed-lag case, plaintext i − L;
  - R68 used a lag along 10 routes;
  - L90 used K4's *ciphertext* as key;
  - H2 (R76) scrambled a *keyword*.
  L19 mentions a "self-fold" with no detail; the builder should check what that was.
- Against: English keyed by English usually gives an IC near 0.043. K4's 0.0361 is low for that at 97 letters, by
  roughly 1.5–2 standard deviations. This weighs on every running-key idea.

**Definition.** `c[i] = CA[(s·IDX[pa][p[i]] + t·IDX[ka][p[π(i)]]) mod 26]`, with (s, t) = (1, 1) VIG, (−1, 1) BEAU,
(1, −1) VARB. π is a permutation of 0..96 in the repo's convention `KEYTEXT[i] = P[π(i)]`.

Routes:
- the 64,782 routes of `r76/routes76.py: merged` (R72 sheet routes, all double and single rotations to width 48,
  every columnar of width 2–7, the R61 routes; inverses are already in that count);
- every map i → (a·i + b) mod 97 (9,311 non-identity maps; this includes cyclic shifts and mirrors).

Conventions: pa, ka, ca each AZ or KRY, three operations: 24.

**Blind solver.** For each route and convention:
1. Split π into cycles.
2. For each cycle and each of the 26 guesses for its first letter, walk the cycle:
   `p[π(i)] = KA[t·(IDX[ca][c[i]] − s·IDX[pa][p[i]])]`. Keep the guess only if the walk returns to it.
3. A cycle with no surviving guess kills the setting. This filter uses the ciphertext only.
4. Combine the surviving guesses of all cycles. Enumerate up to 20,000 combinations; beyond that use coordinate
   ascent over cycles on the letter model.
5. Rank all decodes by the letter model, then apply the two cuts.

Note for the self-test: when pa = ka = ca the walk is linear. BEAU and VARB then need the ciphertext values of each
cycle to sum to 0 mod 26; VIG on an odd cycle allows at most 2 guesses. So most settings die at step 3, and the
survivors have very few decodes.

**Sealed gate.** 60 positives (random route from the set, random convention) and 100 negatives. Bars 54/60 and
0/100. Plants whose route has a fixed point or a 2-cycle are legal; say how they are handled.

**Exact check H11X (crib-assisted, after the freeze).** A published position i is usable when π(i) is also
published. Each usable position is one complete check with no unknown: does the tableau send (p[i], p[π(i)]) to
c[i]?
- A random route has about 6 usable positions; 85% of the affine maps have 5 or more (counted).
- Run every route with at least 3 usable positions: the 24 conventions, then pa = ka = ca = each large-tier
  alphabet × 3 operations.
- A feasible setting is decoded by the blind solver, with the published letters as the cycle guesses where they fix
  one.

**Controls.**
- The lag routes π(i) = i − L must agree with L59 (no survivor with a repeated check at lags ≤ 25).
- The mirror π(i) = 96 − i must be infeasible. **(By hand)** under A–Z: positions 24 and 74 hold S and K, and none
  of S + K, K − S, S − K gives R.
- Shuffles: about 0 feasible at 3 or more usable positions.

**Reuse.** `r76/routes76.py`; `strictblind/blind/routes.py`; `r72/novelty.py`; the R75 scorer `core.Scorer`.
**Cost.** About 1.8 million settings per ciphertext. Roughly 75 s per ciphertext in vectorised numpy, so 2–6
CPU-hours for holdout, K4 and 100 shuffles; minutes if the walk is written in C++ like `r59/blind/rk_solve.cpp`.
H11X about 20 minutes.
**Outside facts.** None.

---

## H9. Grid key with a new alphabet keyword; the clock-hand key

**Statement.** The message was written in rows (7 wide first). One key runs along each row, a second key changes
once per row, and the tableau's alphabet is keyed by a word we have not tried.

**Why.**
- Three things point at width 7, the length of KRYPTOS: five of K4's six doubled letters start in column 5 (R71,
  ciphertext only); both published strings start in column 1 (r76 Fact B); and Fact E above.
- R75's F4X closed grid keys for the four known alphabets only (L165). R76's H1X closed new alphabet keywords for
  repeating keys only (L166). The combination is open.
- **(By hand)** At width 7, for every offset except o = 2 (where columns 5 and 6 straddle a row end), the three
  doubles put a sharp condition on the plaintext alphabet:
  `IDX(O) − IDX(N) = IDX(T) − IDX(S) = IDX(N) − IDX(I)`. Plain A–Z gives 1, 1, 5 and KRYPTOS gives 12, 24, 4, which
  agrees with F4X's zero. Few keyword alphabets will pass.

**Definition (H9a).** `q = i + o`, column `q mod w`, row `q div w`.
`IDX[ca][c] = s·IDX[pa][p] + A[column] + B[row]`, any A and B, pa and ca from the large tier, s = ±1.

**Definition (H9b, clock hands).** A fast key and a slow key that are not locked to one grid:
`K[i] = U[i mod m] + V[(i + φ) div h]`, m in 1..26, h in 2..31, φ in 0..h−1, V free (and also V repeating with
period 1..26), the four alphabets and R75's 1,024 two-stage configurations. F4X covered only h = m.

**Blind part.** 3,110,400 fixed methods: row-direction keyword W1 (80 words; width = its length), row-by-row keyword
W2 (80 words, one letter per row, repeating), offset 0, pa = ca = A for the 81 small-tier alphabets, key letters
numbered by AZ or by A, three operations.

**Sealed gate.** Plants from that family with random W1, W2 and alphabet word; bars as in R76.

**Exact check H9X (crib-assisted, after the freeze).**
- H9a: the published positions link column slots to row slots. Every independent cycle of that graph gives one
  equation `Σ ± IDX[ca][c] = s·Σ ± IDX[pa][p]`, with no key in it. Hash-join the two sides over the large tier, as
  `exact76.h1x` does.
  - Width 7 has 12–14 checks, depending on the offset (counted). Chance over 77,229² pairs is about 10⁻⁷.
  - Widths 14 and 21 have 9–10 checks. Width 31 (the carved rows) has 0–1 and cannot be decided this way.
  - Run every width and offset with at least 9 checks: that is widths 2–14, 20, 21 and 39–42. Expected chance
    passes in total: about 0.1.
  - Also run pa = ca (one alphabet, 77,229 of them) at every width 2–48 and offset with at least 6 checks.
- H9b: `r75/sealed/gridx.py: check_maps` with `Lmap = i mod m`, `Rmap = (i + φ) div h`.
- Decode feasible settings with `gridx.complete`.

**Controls.** The four known alphabets must give 0 (F4X). The self-test must show the Fact E filter and the full
check agree. Shuffles: about 0.

**Reuse.** `r75/sealed/gridx.py`; `r76/sealed/exact76.py: h1x, tier_arrays`; `r76/alphabets.py`.
**Cost.** Minutes. **Outside facts.** None.

---

## H8. Stepping devices: the key moves by a rule we do not know

**Statement.** A disk or rotor advanced after every letter, and the size of the advance depended on the letter just
enciphered. We do not assume the rule; we let it be any function.

**Why.**
- §17 items 4 and 5 (wheel ciphers, rotor-style stepping) were never tested. C1, C2 and C4 above close the textbook
  forms by hand. This is the general form that is left.
- A plaintext-driven advance hides letter frequencies without a long key. It is the same idea as the Wheatstone
  device (C2), which Sanborn's "clock" brought to mind.
- Earlier rows cover narrower rules: a constant advance (L13, L16), key equal to the previous letter (L17, L27),
  linear recurrences on the key alone (L49), and L20, whose scope is recorded only as "homogeneous arithmetic".

**Definition (H8a, step function).** `K[0] = κ`, `K[i] = K[i−1] + g(x[i−L])`, x = p or c, L in 1..4, g any function
from the 26 letters to 0..25. One stage, 32 conventions.

**Definition (H8b, one free rotor).** `IDX[eo][c[i]] = R[(IDX[ei][p[i]] + o[i]) mod 26] − o[i]`,
`o[i] = σ·((i + φ) div h)`, R any permutation, ei and eo in A4, σ in 1..25, h in 1..12, φ in 0..h−1. 31,200 settings.

**Blind part.** 297,128 fixed methods:
- H8a: `g(x) = a·IDX[ga][x] + b`, ga in A4, a = ±1, b and κ in 0..25, source p or c, L = 1, pa and ca in AZ / KRY,
  s = ±1 (86,528);
- H8b: R and R⁻¹ from the 81 small-tier alphabets, ei = eo in AZ / KRY, σ in 1..25, h = 1, start 0..25 (210,600).

**Sealed gate.** Plants from both parts; bars as in R76.

**Exact check H8X (crib-assisted, after the freeze).**
- H8a: `D[i] = K[i] − K[i−1]` at the 22 adjacent published pairs must be a function of x[i−L]. For L = 1 that is
  10 checks (plaintext-driven) or 8 (ciphertext-driven). **(By hand)** plain A–Z fails all four: plaintext-driven,
  T gives 1 then 8 (additive) and 15 then 10 (sum form); ciphertext-driven, Q gives 25 then 22 and 1 then 2.
- H8b: the 24 pairs (input contact, output contact) must form a partial permutation.
- Decode: H8a needs g on unseen letters; complete those by coordinate ascent. H8b needs R on unseen contacts; same.
  R76's warning applies: with many free values the completion alone can look like English, so feasibility is the
  result and readability is weak.

**Controls.** C1, C2 and C4 coded and infeasible, with planted wheel, Wheatstone and rotor messages feasible.
g constant must agree with L13. Shuffles: about 0.

**Reuse.** `exact.kall`; `core.Scorer`. **Cost.** Minutes.
**Outside facts (low stakes).** The Wheatstone device as I describe it (27-symbol outer ring with a blank, 26-letter
inner ring, hands geared one to one) is from memory. C2 holds for any outer ring of 27–38 symbols, so only the
basic principle needs confirming.

---

## H10. Slidefair with keyword alphabets

**Statement.** The tableau was used on pairs of letters: the two plaintext letters mark two corners of a rectangle
in the chart and the ciphertext is the other two corners.

**Why.**
- §17 item 11. Sanborn has said Scheidt taught him "matrix codes"; Slidefair is the standard way to use a Vigenère
  chart as a matrix on pairs.
- It keeps the message length and gives a flat count. Unlike Playfair it can turn a letter into itself, so S→S and
  K→K do not kill it.
- C5 closes the plain and KRYPTOS charts by hand. Keyword alphabets are open. L88 covers 25-letter squares only.

**Definition.** Pairs (i, i+1) with i ≡ a mod 2, a = 0 or 1; pair number j has key value `κ = U[j mod m]`.
`x1 = IDX[pa][p1]`, `x2 = IDX[ca][p2] − κ`.
- If x1 ≠ x2: `c1 = PA[x2]`, `c2 = CA[x1 + κ]`.
- If x1 = x2: `c1 = PA[x1 + 1]`, `c2 = CA[x1 + 1 + κ]`.
- Also the variant with c1 and c2 written in the other order.
- The one unpaired letter is enciphered as plain `CA[IDX[pa][p] + κ]`.

**Blind part.** 66,096 fixed methods: pa = ca from the 81 small-tier alphabets, key numbered by AZ or by that
alphabet, the 102 key rows of H7, a in {0, 1}, both output orders.

**Sealed gate.** Plants from that family; bars as in R76.

**Exact check H10X (crib-assisted, after the freeze).** The key cancels:
`IDX[pa][c1] − IDX[pa][p1] = IDX[ca][p2] − IDX[ca][c2]` for every pair in the normal case. Each alignment has 11
published pairs. Hash-join the left side (a function of pa only) against the right side (ca only) over the large
tier, for both alignments and both orders, allowing one pair to be the x1 = x2 exception. Chance over 77,229² pairs
is about 10⁻⁵. A feasible setting gives the key value of 11 pairs; test those for a period, then decode.

**Controls.** C5 (plain and KRYPTOS charts: 0). Shuffles: 0.
**Reuse.** `exact76.h1x` (hash join), `tier_arrays`. **Cost.** Minutes.
**Outside facts (low stakes).** The ACA's exact Slidefair rule: which corner is written first, and the same-column
rule. Both orders are in the family, so only the same-column rule needs checking.

---

## H12. Three keywords, three stages (r76's H3, unchanged)

**Statement.** KRYPTOS, PALIMPSEST and ABSCISSA are each used once, one stage after another, each on its own
alphabet.

**Why.** All three words are on the sculpture. With one tableau throughout it reduces to a summed key (L36, EXCL);
with different tableaux it does not. R75's F1X closed two stages for every key with periods up to 26; three were not
run.

**Definition and blind part.** As r76 H3: 6 orders × 560 phases × 1,728 stage conventions (each stage pa = ca = ka
in AZ / KRY / PAL / ABS, VIG / BEAU / VARB) = 5,806,080 fixed methods.

**Exact check.** None for all keys: 25 key letters against 24 published letters decide nothing. After the freeze,
only the whole-family letter count (`r75/sealed/reveal_k4.py: family_hits`).

**Reuse.** `r75/families.py`, `r75/blind/run.py`. **Cost.** About 10 minutes per 100 ciphertexts.

---

## 4. Considered and dropped

| Idea | Why dropped |
|---|---|
| H5 physical overlay | Inside L50 by the ledger's wording (§1) |
| Wheel / strip, Wheatstone | Closed by hand (C1, C2); kept as controls in H8 |
| Fractionated Morse, straddling checkerboard, ADFGVX | They change the length or regroup letters. Sanborn gave the clues letter for letter at fixed positions |
| Playfair-type on a 26-letter rectangle | No letter can become itself; S→S and K→K |
| Custom chart with a sculpture keyword | Closed by hand (C3) |
| Natural-language running key under the tableau's sideways reading | The implied key has a letter three times in a row (Fact F) |
| Letter chain-addition with a 9–12 letter primer | **(By hand)** plain A–Z fails for the Gromark taps at primer lengths 9–12; L15 covers 2–8 |
| Two free alphabets with an unknown key; an unknown running text with mixed alphabets | Still not solvable or decidable at 97 letters (L138). No new idea here |

---

## 5. Ranked table

| Rank | # | Odds | Decided for every key? | Truly blind solver? | Cost |
|---|---|---|---|---|---|
| 1 | H7 split key | 1–1.5% | Yes, periods 1–24 (plaintext feedback: lags 1–9, 34–48) | Part B, for ciphertext feedback | about 1 h |
| 2 | H11 self-keyed copy | 0.5–1% | Yes, it has no key; all listed routes | Yes | 2–6 CPU-h |
| 3 | H9 grid + new alphabet | 0.5–1% | Yes at width 7 and wherever checks ≥ 10 | Fixed methods only | minutes |
| 4 | H8 stepping devices | 0.5% | Yes (any step function; any rotor wiring) | Fixed methods only | minutes |
| 5 | H12 three stages | < 0.5% | No | Fixed methods only | 10 min |
| 6 | H10 Slidefair | 0.2% | Yes, 77,229² alphabet pairs | Fixed methods only | minutes |

## 6. Recommended R77 build

**Pre-register and run H7 and H11 first.**
- They are the two ideas that are new, that follow from what K1–K3 teach, and that have a real ciphertext-only
  solver (H7 part B, H11) as well as an exact check that decides the family for every key.
- Neither needs any outside fact. Nothing waits on the photo check.
- Both reuse the R75/R76 runner, gate and exact-check helpers. New code: the stream table and part-B solver for H7;
  the cycle walker for H11.

**In the same blind run, if time allows, add the small fixed-method families of H9, H8, H10 and H12** (about 9.3
million methods together), in that order. Then their exact checks can run after the same freeze. If they are left
out, do not run their exact checks alone; hold them for R78 with their blind families.

**Order of work.**
1. Self-tests with controls C1–C5 and the ledger controls named under each hypothesis. No K4.
2. Sealed holdout, blind run, freeze, verify, gate.
3. K4 and 100 shuffles: blind run, freeze, verify.
4. Reveal, then H7X and H11X (and the riders' exact checks), labelled crib-assisted.

**Fresh books for the gates.** The four named in r76 are used up. Candidates not found anywhere in the repo:
*Lord Jim*, *A Room with a View*, *My Ántonia*, plus one more to be chosen the same way. (*The Mysterious Affair at
Styles*, proposed in the first draft, is spent: R75 and R76 used it for development negatives.) Grep again, confirm
they are not in `r59/corpus/build_corpus.py`, and pin their sha256 in the pre-registration.

## 7. What to hand back
- Any readable decode: stop and report it raw, with its setting.
- For each of H7–H12: gate result; blind best score for K4 against the 100 shuffles; number of settings with enough
  checks; number feasible for K4 and for 20 shuffles (median and maximum); the best decode's two scores.
- C1–C5: confirmed or refuted in code, with planted controls. If confirmed, C1 and C2 get their own ledger rows.
- H7 part B: recovery rate by key length on the holdout, so the blind coverage is stated honestly.
- H11: how many settings survive the ciphertext-only cycle filter, for K4 and for the shuffles.
- Whether L19's "self-fold" and L20's "tableau stepping" overlap H11 or H8, if their code can be found.

## 8. Input needed from Tyler or ChatGPT
- **Nothing blocks H7 or H11.**
- **ChatGPT, low stakes:** confirm the Wheatstone device's principle (H8, C2) and the ACA Slidefair same-column
  rule (H10) from a printed or archived reference. No K4 plaintext sources.
- **ChatGPT, existing brief** (`r77/CHATGPT_TABLEAU_CHECK.md`): still useful for the record. It now decides only
  whether H5 is rerun as a rider.
- **Tyler:** say whether the riders (H9, H8, H10, H12) go into R77's blind run or wait for R78.
