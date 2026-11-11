# K4 hypotheses for the next rounds (Claude Code, 10 Nov 2026)

Written by reasoning only: **no test was run for this file, on K4 or on synthetic data.** It is a specification for
whoever runs the tests. Hand arithmetic on the published letters is marked as such; Tyler has said clue-motivated
ideas are fine as long as the known text is a check and not part of the algorithm that produces solutions.

**How to use it:**
- **H0** is already built and pre-registered as R75 (`r75/RUNBOOK.md`). Run that first.
- **H1–H6** are new. Each has an exact definition, the test that decides it, and the existing code to reuse. Build
  them as R76 with their own short pre-registration.
- **Rules for every hypothesis** (unchanged from R75):
  1. Write the code and a synthetic self-test first. Plants with random settings must be recovered; random
     ciphertexts must give nothing readable. No K4 until that passes.
  2. Blind part first: ciphertext only, then freeze and push.
  3. Only then the exact check with the published letters, labelled crib-assisted.
  4. A hit means a full 97-letter decode that clears both confidence cuts (letter model ≥ −1.45, word model ≥ −2.50
     per letter). Feasibility without a readable decode is not a hit.
  5. On any hit: stop, do not tune, report the raw decode and setting.

## Facts worked out by hand from the published letters
Positions are 1-based here. Pairs are plaintext→ciphertext.

`22 E→F, 23 A→L, 24 S→R, 25 T→V, 26 N→Q, 27 O→Q, 28 R→P, 29 T→R, 30 H→N, 31 E→G, 32 A→K, 33 S→S, 34 T→S`
`64 B→N, 65 E→Y, 66 R→P, 67 L→V, 68 I→T, 69 N→T, 70 C→M, 71 L→Z, 72 O→F, 73 C→P, 74 K→K`

- **Fact A (self-encryptions).** S→S at 33 and K→K at 74.
  - In any cipher of the K1/K2 type (the same alphabet on both sides, key added or subtracted), the key is zero at
    both places, whatever the alphabet.
  - A period m is impossible if some other published position sits in the same key slot as 33 or 74 and is not
    self-encrypting.
  - That kills every period 1–26, 31–40 and 42–52. It leaves 27–30, 41 and 53+.
  - **So K4 is not a K1/K2-type cipher with any alphabet keyword at any period up to 26.** A self-test must
    reproduce this.
- **Fact B (where the strings start).** Both published strings start at a position that is 1 more than a multiple of
  21: 22 = 21 + 1 and 64 = 3 × 21 + 1. They also start at column 1 of a 7-wide grid.
  - Taken at face value the chance is about 1 in 440 (1 in 49 for width 7).
  - It is noticed after the fact, but it points the same way as two ciphertext-only features: doubled letters in
    columns 5–6 at width 7, and vertical pairs at width 21 (R71).
- **Fact C (plain A–Z sums).** With A = 0 … Z = 25, the totals c + p (mod 26) at the 24 positions are
  `9 11 9 14 3 4 6 10 20 10 10 10 11 | 14 2 6 6 1 6 14 10 19 17 20`.
  - There are 22 equal pairs; chance gives about 10.6.
  - Runs: 10 at positions 29, 31, 32, 33 (and 71); 6 at 66, 67, 69 (and 28).
  - "c + p + key = constant" is the arithmetic of a reciprocal one-time-pad table, the standard US manual system of
    the period, which a CIA cryptographer would know well.
  - R75's diagnosis (part C3) calibrates this properly. Until then it is a lead, not a result.
- **Fact D.** R→P occurs twice (28 and 66, 38 apart).

## The hypotheses, in the order I would run them

| # | Hypothesis in one line | My rough odds | Cost | Status |
|---|---|---|---|---|
| H0 | Two layers on different tableaux; interrupted key; held key; plus the key diagnosis | 1–2% | About 1 hour | Built (R75) |
| H1 | K1/K2's method with a **new alphabet keyword** on one or both sides and a longer key | 2–3% | Minutes | To build |
| H2 | The **key** was scrambled the way K3's text was; the message stayed in place | 1–2% | Under 1 hour | To build |
| H3 | All three sculpture keywords, one stage each, on different alphabets | under 1% | Minutes | To build |
| H4 | A **grid**: one keyword across the columns, another down the rows | 1% | Minutes | To build |
| H5 | **Physical overlay**: each K4 letter is keyed by the tableau letter beside it on the sculpture | 1% | Minutes | To build |
| H6 | A **dropped or extra letter** between the two published strings (as in K2) | under 1% | Free (a parameter) | To build |

The odds are my judgment after 164 negative results, not a calculation. Together they come to perhaps 5–8%.

---

## H0. Already built: R75
See `r75/PREREGISTRATION.md`. It covers two keyword stages on different tableaux (any keys, periods ≤ 26, via F1X),
interrupted keys (F2X), held keys (F3X), and the key-shape and key-class diagnosis.

**Read the diagnosis before H1–H6.** It tells which of the hypotheses below fit the key's shape.

---

## H1. A new alphabet keyword (one stage, any key, period 8–52)
**Statement.** K4 uses one tableau stage like K1 and K2, but the plaintext alphabet, the ciphertext alphabet or both
are keyed by a word other than KRYPTOS, and the key is longer than K1's or K2's.

**Why.**
- Only four alphabets (A–Z, KRYPTOS, PALIMPSEST, ABSCISSA) were ever tried with repeating keys (L04).
- For arbitrary alphabets the ledger leaves periods 8, 11–13, 16, 18–20, 22–24 and 26+ open (L21).
- The ciphertext-only repeat statistic is compatible with periods 20 and 28–48 (L89).
- Fact A says the two alphabets cannot be the same at periods up to 26. So the live case is two different
  alphabets, as in Quagmire I, II and IV.

**Definition.** `IDX[CA][c_i] = s·IDX[PA][p_i] + k[i mod m]` (mod 26), with s = +1 or −1, m in 8..52, any key letters.
PA and CA come from a set 𝒜 of alphabets:
- for every word w: `core.keyed(w)` (the word's letters, then the rest ascending: the K1/K2 construction);
- the same with the rest descending;
- the ACA columnar alphabet, `r38/aca_alphabet.py`;
- plus A–Z and Z–A.

Two tiers of words:
- **Small:** `r75/data/kryptos_words.txt`.
- **Large:** every word of 4–15 letters in `k4kit/data/word_model_orth.tsv`.

**Exact test (after the freeze): a hash join, no search.**
1. For period m, take the published positions that share a key slot, and pair each with the next one in its slot.
   Call the pairs L_m.
2. For an alphabet A, the ciphertext signature is the tuple of `IDX[A][c_i] − IDX[A][c_j]` over L_m. The plaintext
   signature for sign s is the tuple of `s·(IDX[A][p_i] − IDX[A][p_j])`.
3. (PA, CA, s, m) is feasible exactly when the two signatures are equal. Index the ciphertext signatures in a
   dictionary and look up each plaintext signature.
4. Use only periods with enough pairs, so that chance matches are negligible:
   - large tier: at least 8 pairs, which is m in 8–16, 19–22, 37–45;
   - small tier: at least 5 pairs, which adds 17, 18, 23, 24, 34–36, 46–48.
5. For each feasible setting, the published letters pin some key letters. Fill the rest blind by coordinate ascent
   on the quadgram score (each unpinned key letter in turn, best of 26, repeat until nothing changes, three starts).
   Score the decode.

**Blind part (before the freeze).** A fixed-method family: PA and CA from the small tier, key = a word of the small
tier, phase 0, VIG/BEAU/VARB, key numbering AZ or KRY. About 3 million methods; scan it with the R75 runner.

**Self-test must show:**
- plants with random alphabet words and random keys are found and decoded;
- with PA = CA and s = +1 nothing is feasible at periods 8–26, 31–40, 42–52 (Fact A).

---

## H2. The key was scrambled, the message stayed in place
**Statement.** A keyword was written out repeatedly, that key stream was rearranged by a K3-style sheet operation,
and the rearranged key enciphered the message letter by letter.

**Why.**
- It uses the two techniques Sanborn is known to have used (keyword tableau, sheet rotation).
- It leaves the published letters in place.
- It gives a key that never repeats, which is what the ciphertext looks like (L89).
- R68 tried the idea on 10 routes only. R72's reconstruction of a K4-sized sheet was never run, because routing the
  *text* needed every solver. Routing the *key* needs only an exact check.

**Definition.** `K[j] = W[perm[j] mod m]`, where W is any m letters (m in 2..24) and `perm` is a route in the
convention `out[j] = in[perm[j]]`. Then one stage: `IDX[ca][c_j] = s·IDX[pa][p_j] + K[j]`, with the 32 conventions of
`r75/sealed/exact.py` (`CONV`).

**Routes, each with its inverse:**
1. R72's 36 sheet routes: the 9 orderings in `r72/data/SHEET98_ORDERINGS.tsv`, extra cell first or last
   (`r72/novelty.py: drop_cell`).
2. Every double rotation `R{w1}x{w2}` with w1, w2 in 2..48, CW or CCW, and the mixed-direction ones
   (`strictblind/blind/routes.py: rotation, mixed_rotation`).
3. Every single rotation, width 2..48 (`routes.rot`).
4. Columnar with every column order for widths 2–7, all fill and read variants (`routes.columnar`).

**Exact test.** For each route and period: `res = perm[POS] % m`; `exact.group_check(res, exact.kall(...))`; decode
with `exact.decode_indexed`. Count only settings with at least 5 checks.

**Blind part.** Keywords KRYPTOS, PALIMPSEST, ABSCISSA at every phase, route sets 1–3, alphabets AZ/KRY, about 10
million methods.

**Two companion checks, both cheap:**
- **H2b, text routed, plaintext-position reading of the clues.** R72's 36 routes only, any key of period ≤ 24, both
  orders.
  - Substitute then route: the published letter at plaintext position q sits at ciphertext position `inv[q]` and uses
    key slot `q mod m`.
  - Route then substitute: key slot `inv[q] mod m`.
  - This closes R72's on-hold item for repeating keys.
- **H2c, R74's sandwich on R72's routes.** Run `r74/scan.py` with the 36 sheet routes in place of `r61/routes.txt`.

---

## H3. Three keywords, three stages
**Statement.** KRYPTOS, PALIMPSEST and ABSCISSA are each used once, one stage after another, each stage on its own
alphabet.

**Why.** It is the natural next step after R75's two layers, and all three words are on the sculpture. With the
same tableau throughout it reduces to a summed key, which is excluded (L36); with different tableaux it does not.

**Definition.**
- Order of the three words: 6.
- Phases: 7 × 10 × 8 = 560.
- Each stage is the same-alphabet type (`pa = ca = ka`) with alphabet AZ, KRY, PAL or ABS and VIG, BEAU or VARB: 12
  per stage, 1,728 in all.
- Total: 5,806,080 fixed methods.

**Test.** Blind scan with the R75 runner, then the whole-family letter count after the freeze
(`r75/sealed/reveal_k4.py: family_hits`). There is no all-keys check here: 25 key letters against 24 published
letters decide nothing.

---

## H4. A grid: one key across, one key down
**Statement.** The message was written in rows of w letters. One keyword runs along each row (it repeats every w
letters); a second key changes once per row.

**Why.** Fact B and the two width-7 and width-21 features of the ciphertext all point to a grid of 7 or 21 columns,
and 7 is the length of KRYPTOS. A row key that changes every line is not a repeating key, so the earlier exclusions
do not reach it.

**Definition.** With grid offset o: column `(i + o) mod w`, row `(i + o) div w`; w in 2..48, o in 0..w−1. Two forms:
- **Additive:** key = column key + row key on one tableau.
- **Two-stage:** the column key on one tableau, then the row key on a different one.

**Exact test.** Generalise `r75/sealed/exact.py: f1x` so the two node maps are passed in. It now uses `(i mod m1,
i mod m2)`; pass `(column, row)` instead. The 1,024 configurations already include both forms (the additive form is
the case ca1 = pa2). At width 7 the published letters touch 7 columns and 4 rows, which leaves 14 checks.

**Decode.** Rows that hold no published letter have an unknown row key. Fill them with a left-to-right beam: 26
choices per row, letter-model score, beam 50.

**Also run the same generalised check with** `(i mod m, ((i + φ) div h) mod m2)`: one repeating key and one held
key, m and m2 in 1..26, hold h in 2..31.

---

## H5. Physical overlay with the tableau
**Statement.** The key letter for each K4 letter is the tableau letter at the matching place on the facing panel.

**Why.** Sanborn has warned against assuming the answer is purely mathematical. K1–K3 never use the tableau's A–Z
header, its row labels or the extra L. Earlier overlay tests used straight lines (L50), not K4's own footprint.

**Layout.**
- **K4 on the ciphertext panel:** the last four rows, as 4 + 31 + 31 + 31. Positions 1–4 are columns 28–31 of row
  25; positions 5–35, 36–66 and 67–97 are rows 26, 27 and 28, columns 1–31.
- **Tableau panel, 28 rows:**
  - row 1 and row 28: `ABCDEFGHIJKLMNOPQRSTUVWXYZABCD`;
  - rows 2–27: the label letter A–Z, then 30 letters of the KRYPTOS alphabet starting one further along each row
    (row A starts `KRYPTOS…`, row B `RYPTOSA…`);
  - row N carries one extra letter, L, at its end.
- Check this layout against a photograph or the archive before use; I wrote it from memory of the sculpture.

**Family.**
- K4's four rows map to four consecutive tableau rows starting at any row 1..25, in the same order or flipped.
- Columns map as `(col + d)` or `(d − col)` for d in 0..30, wrapping within the row's own letters.
- With or without the label column.
- That gives 6,200 key streams. With 96 one-stage conventions (pa, ca in the four alphabets, ka in AZ/KRY, three
  operations): 595,200 fixed methods.

**Test.** Blind scan, then the whole-family letter count.

---

## H6. A dropped or extra letter between the published strings
**Statement.** K4 is one of the already-excluded simple ciphers, but one or two letters were dropped or added in
positions 35–63, as happened in K2. Every key that depends on position is then out of step for the second string.

**Test.** No new family. In every exact check (F0X, F1X, F3X, H1, H2, H4), run again with the key index of the second
string shifted by −2, −1, +1 and +2. R75's F2X already covers the one-stage case with any shift.

---

## What to hand back
- Any readable decode: stop and report it raw.
- R75's key class, with its six z-scores. It decides which of H1–H6 deserve a second, wider pass.
- For each hypothesis: the number of settings with enough checks, the number feasible, and the best decode's two
  scores, for K4 and for 20 shuffles.

## Fresh books for the sealed gates
Never used in this project and not in the letter model's training text: *The Woman in White* (GITenberg 583), *The
Sign of the Four* (2097), *The Invisible Man* (5230), *The Jungle Book* (236). Pin their sha256 in the
pre-registration.
