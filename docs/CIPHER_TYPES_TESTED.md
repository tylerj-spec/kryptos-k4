# Cipher types tested on K4 so far (Claude Code and ChatGPT, rounds 1–57)

Written 1 Nov 2026 by Claude Code. The canonical record is `LEDGER.md`: rows L01–L142 on `main`.

**Where the newer rounds live:**
- **L143,** Claude's crib-conditioned R52, is on the unmerged PR #12.
- **ChatGPT's R49, R53, R54, R55, R56 and R57** are on `main`.
- **ChatGPT's R45–R48 and R50–R52** are on their own branches and PRs.

This page explains, in plain words:
- what each cipher family is;
- why it was worth testing on Kryptos;
- what we found.

Status words are the ledger's:

| Word | Meaning |
|---|---|
| **EXCL** | Mathematically impossible for K4 within the stated scope. |
| **FEAS** | A full witness exists. It is usually gibberish, so it is not evidence. |
| **STAT** | Statistically unremarkable. |
| **WEAK** | Too few constraints to decide. |
| **OPEN** | Not settled. |

**Bottom line: no K4 solution. Every family below either cannot produce K4 (EXCL) or produced nothing better than
chance.** The most important open items are in §17.

> **Two kinds of test.**
> - **Crib-assisted exact checks** use the 24 published letters (EASTNORTHEAST at 22–34, BERLINCLOCK at 64–74) to
>   prove a family impossible.
> - **Strict-blind searches** decrypt from the ciphertext alone and compare with the 24 letters only after
>   freezing.
>
> Since **R53 (owner rule, 31 Oct 2026)**, only the blind kind can produce a candidate. The crib-assisted exclusions
> remain valid as negative results, labelled as such.

---

## 0. Notation used everywhere

| Symbol | Meaning |
|---|---|
| `p`, `c` | plaintext and ciphertext letter |
| `k` | key value at that position |
| PA | plaintext alphabet (a permutation of A–Z) |
| CA | cipher alphabet (a permutation of A–Z) |
| `PA⁻¹(p)` | the position of `p` in PA |

**The general "tableau" cipher** (covers Vigenère, Beaufort and Quagmire I–IV):

`c = CA[ PA⁻¹(p) + k mod 26 ]` (VIG) or `c = CA[ k − PA⁻¹(p) mod 26 ]` (BEAU) or `c = CA[ PA⁻¹(p) − k mod 26 ]` (VARB).

| Name | Plaintext alphabet | Cipher alphabet |
|---|---|---|
| Vigenère | A–Z | A–Z |
| Quagmire I | keyed | A–Z |
| Quagmire II | A–Z | keyed |
| Quagmire III | the same keyed alphabet on both sides | (same) |
| Quagmire IV | keyed | a different keyed alphabet |

- **K1 and K2 are Quagmire III,** with the KRYPTOS alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ` and keys PALIMPSEST and
  ABSCISSA. That is why this family dominates our work.
- **Keyword alphabet:** the keyword with repeated letters dropped, then the unused letters in A–Z order.
- **ACA "columnar-keyed" alphabet:** write the keyword as a row, fill A–Z underneath, then read the columns in
  alphabetical order of the keyword letters (`r38/RESEARCH_NOTES.md`).
- **Free alphabet:** any of the 26! permutations. The search must find it.

---

## 1. Pure transposition (letters rearranged, not changed)
- **What it is:** the plaintext letters are reordered by a rule: columns, routes, a rail fence, grilles.
- **Why test it:** K3 is a transposition.
- **Result: EXCL (L01).** K4 contains only 2 E's, but the known plaintext needs 3 (two in EASTNORTHEAST and one in
  BERLINCLOCK). A rearrangement cannot create letters. This holds for **every** pure transposition, including any
  grille.

## 2. Monoalphabetic substitution (one fixed alphabet): Caesar, Atbash, affine, keyword substitution
- **What it is:** each plaintext letter is always replaced by the same cipher letter.
- **Result: EXCL (L02).** Ciphertext `QQ` at positions 26–27 decrypts to `NO`. One letter cannot stand for two
  letters.
- **The in-place contradiction does NOT extend to substitution followed by transposition.** The latter changes position alignment. Toy counterexample: plaintext `ABCA` -> fixed substitution `QRSQ` -> transpose `QQRS`; adjacent final `QQ` now occupies positions corresponding to *different* plaintext letters. A fixed substitution also relabels letter frequencies. Every layered hypothesis needs its own scoped proof or blind solver.

## 3. Periodic polyalphabetic: Vigenère, Beaufort, variant Beaufort, Quagmire I–IV, Gronsfeld, Porta
- **What it is:** the key repeats with period *m*, so every *m*-th letter uses the same alphabet.
- **Results:**
  - **EXCL** for periods 1–26 and 30–52 in the eight standard variants (L03).
  - 16 alphabet pairs, both operations: **EXCL** to period 25–26 (L04).
  - Multiplied key `c = a·p + k`: **EXCL** where testable (L05).
  - Per-slot arbitrary alphabets (any 26! alphabet in each column): **EXCL** at many periods; the rest are **OPEN**
    but underdetermined (L21, L53).
  - A repetition statistic shows K4 behaves like a **non-repeating** key at most small periods (L89).
  - The result survives one or two mis-carved clue letters (L35).
  - **Porta:** EXCL (L88).
  - **Gronsfeld** (Vigenère with digit keys) is a special case of the decimal keys in §5.
- **"Multi-clock" sums of 2–4 periodic keys** (stacked Vigenère stages): **EXCL/WEAK** (L36).

## 4. Progressive and generated keys
- **What it is:** the key changes by a rule, for example +1 each letter, or a linear recurrence
  `k_n = c1·k_{n−1} + … + d (mod 26)`. This covers LFSR-style and Fibonacci-style generators.
- **Results:**
  - Progressive key **EXCL** at m 1–25 (L13).
  - **Every** affine linear recurrence of order 1–6 mod 26, in place: **EXCL**, 0 fits (L49).
  - Base-26 lagged Fibonacci with any cipher alphabet: **EXCL** (L15).

## 5. Gromark and chain-addition keys (the most-tested family)
- **What it is:** the Gronsfeld-with-mixed-alphabet-and-running-key cipher of the American Cryptogram Association
  (ACA).
  - A short numeric **primer** (e.g. 5 digits) is extended by `k_i = k_{i−b} + k_{i−b+1} mod B` (lagged Fibonacci).
  - The digits are then used as Vigenère shifts, usually with a keyed cipher alphabet.
- **Why test it:**
  - It is a classic ACA type.
  - Ed Scheidt, who designed Kryptos's systems with Sanborn, was chairman of the CIA's Cryptographic Center. A key
    generator of this kind is a natural professional choice; that is our guess, not his statement.
  - Scheidt spoke of a "masking" technique for K4 (WIRED, 2005).
- **What was covered:**

  | Variable | Range covered |
  |---|---|
  | Primer length | 4–8 digits |
  | Base | 3–26 |
  | Alphabets | fixed AZ/KRYPTOS/PALIMPSEST/ABSCISSA (keyword and ACA forms), keyword alphabets (4,761), or fully free |
  | Placement | in place, or with K3-style transpositions before or after |

- **Results:**
  - Fixed alphabets: **EXCL** (L14, L111, L114, L115, L122, L129–L131).
  - Two free alphabets: 39 primers are mathematically feasible. Searched for English, none readable (L22, L72,
    L102, L105).
  - Ciphertext-only IC ranker: no Gromark signature in K4 (L132, L137).
  - Keyword × free alphabet:
    - **EXCL** (crib-assisted) for base-10 5-digit keys, in place and with K3 rotations (R45 = L141; R46 = L142; R50).
    - **EXCL** for 46 of R52's 47 chain families (L143, unmerged PR #12).
    - R52's B26/b5 family keeps one crib-selected setting. A single known-key heuristic solve of it gave gibberish,
      which is negative evidence, not an exclusion (**WEAK/OPEN**).
    - R52 as a whole is crib-conditioned exploratory work.

## 6. Running keys (the key is a long text)
- **What it is:** a book or passage supplies one key letter per plaintext letter (Vigenère with a non-repeating
  key).
- **Why test it:**
  - K3 quotes Howard Carter.
  - Sanborn cites Egypt.
  - K1–K3 are the obvious in-sculpture text.
- **Sources tried:**
  - K1–K3 plaintext and ciphertext;
  - Carter's diary and lecture excerpts;
  - all of Carter & Mace, *The Tomb of Tut·ankh·Amen*, vol. I (1923), with 282,924 letters;
  - K2 coordinates, dates, the World Clock city text (§11), and the Morse-panel text.
- **Results:**
  - **EXCL** with fixed alphabets (L16, L19, L109, L111, L114, L124, L126, L127).
  - **EXCL** with K1–K3 as key and two free alphabets (L90).
  - Carter with two free alphabets: 585 feasible windows, none readable (L106).
  - Keyword alphabet × free alphabet: **EXCL** (R47, replicated in L142).
  - An *unknown* English running key is only **STAT** (L31). This is still a live idea, but unmeasurable without
    the source.

## 7. Autokey (the message keys itself)
- **Ciphertext autokey:** `k_i` comes from `c_{i−L}`.
  - Free alphabet: **EXCL** for lags 1–67; lags 73–96 are **OPEN** (L17).
  - K3 transposition first, keyword alphabets: **EXCL** for lags 1–24 (R51).
- **Plaintext autokey (autoclave):** `k_i` comes from `p_{i−L}`.
  - Exact partition: 127 EXCL and 257 FEAS, all with gibberish witnesses (L27, L52, L58, L59).
  - At long lags this model can turn *any* ciphertext into pseudo-English, so it cannot identify a solution (L52).

## 8. Transposition combined with substitution (two layers)
- **What it is:** substitute, then rearrange (S_then_T), or the reverse (T_then_S).
  - K3 used a double quarter-turn rotation of a grid (write in rows of width *w1*, rotate, rewrite at *w2*, rotate
    again).
  - We call these routes `R{w1}x{w2}/CW|CCW/fwd|inv`.
- **Routes covered:**
  - complete columnar, widths 2–10 (L06);
  - 9,312 circular routes (L07);
  - double grids (L08);
  - fold and back maps (L09);
  - 41,502 routes: all K3-style rotations at grid sizes 2–48, decimations, every columnar of width 2–7, and 41
    keyword columnars (L47);
  - rail fence, spirals, diagonals, double columnar and Myszkowski (L48, with 46,621 routes);
  - a 24-face drum transposition (L38);
  - clock-keyword columnars (L41);
  - keyword irregular columnar with KRYPTOS/PALIMPSEST/ABSCISSA (L118, L121);
  - 5,000 double rotations with widths 4–28 (L115, L124, L126);
  - the four 24×8 K3 rotations in both orders with keyword alphabets (R46, R50, R51; R52 on PR #12).
- **Results:** **EXCL** or at chance **only within the declared routes, keys, and operation orders**; not an exclusion of all layered ciphers.
  - The after-order high-check count was not significant under the pre-registered null (L56, p ≈ 0.07).
  - Decimation plus a summed periodic key gives a FEAS witness that is not a candidate (L55).

## 9. Polygraphic substitution (letters enciphered in groups)
- **Hill cipher** (matrix multiplication mod 26):
  - direct, 2×2 to 5×5, with AZ or KRYPTOS numbering: **EXCL** (L11);
  - Hill as a masking layer before or after transposition: **EXCL** within enumerated scope (L61).
  - **R57:** a separate, explicitly *nonstandard* pad-X/truncate convention for odd 97-letter input: 97,344 invertible 2x2 matrices, 20/20 synthetic hidden-key controls; K4 top 0/24, best 2/24, no readable output. Not an exclusion of all Hill variants.
- **Playfair, two-square, four-square:** **EXCL** (L88).
  - These use 25-letter squares, but K4 has all 26 letters.
  - Playfair also cannot encrypt a doubled letter within a pair.

## 10. Fractionation (letters split into coordinates, mixed, rejoined)
- **Bifid 5×5 and Polybius:** **EXCL**, because of the 25-symbol alphabet (L88).
- **Trifid** (3×3×3 cube, 27 symbols):
  - fixed cubes: **EXCL** (L12);
  - **any** cube at every period 1–97 and every block phase: **EXCL**, 0/4,752 (L91), independently confirmed
    (L95).
- **Not tested:**
  - ADFGVX and ADFGX: their output alphabet is 5–6 letters, so it is excluded by the alphabet unless re-encoded;
  - Bifid 6×6 or 26-letter variants;
  - straddling-checkerboard systems (VIC, Nihilist): their output is digits.

## 11. Keys taken from physical objects or the sculpture itself
- **Berlin World Clock (Weltzeituhr)** at Alexanderplatz. Sanborn named it in 2025 as the clock in BERLINCLOCK.
  Tested as:
  - city-name running keys (L37);
  - per-face keyed alphabets and lookup tables (L39);
  - hour-index keys (L40);
  - clock-keyword columnars (L41);
  - the ENE-facing face (L42);
  - 48-state hour/wind cycles (L75, L76);
  - face strings (L77–L79).
  - **All EXCL or chance, within the source text we could reconstruct.**
  - The historical 1988–90 inscriptions are not fully verified (L25, `r49/`).
- **The KRYPTOS tableau** (the right-hand panel):
  - straight-line paths at every slope as key: **EXCL** (L50);
  - "tableau stepping": **EXCL** (L20);
  - a literal reverse-side stream from an unauthenticated website: 0/52 (R48, not replicated; its source is
    unverified).
- **Morse panel ("K0")** letters and dots/dashes as key: **EXCL narrowly** (L96–L98). The physical reading order is
  unverified.
- **Dates and coordinates** (9 Nov 1989, 3 Nov 1990, the K2 coordinates): **EXCL** (L16, L90).
- **Geography:** the WSW bearing, the CIA-to-KGB line, Tyler's ideas (L44, L44b). No crib signal.

## 12. Null letters and masking layers
- **What it is:** extra letters inserted, a pre-encoding step, or "salt".
- **Results:**
  - periodic null removal (L82);
  - nulls marked by key digits (L83);
  - bounded null deletion (L81).
  - **None gave a coherent text.**
  - The general masking layer is still **OPEN** (L26).

## 13. Plaintext not in standard English
- **What was tested:**
  - German, Dutch, Frisian, Low German, Swedish, French, Spanish, Italian, Latin and transliterated Russian word
    scans (L62–L64, L108);
  - English spelled in a Dutch- or German-looking way (L66–L69);
  - deliberate misspellings like K1–K3's (IQLUSION, UNDERGRUUND, DESPARATLY; L45, L51);
  - X/Q punctuation, where X is a full stop and Q a question mark, as in K2/K3 (L87, L104).
- **Result: no readable candidate in any language.**

## 14. "One free alphabet" families (R40–R44b, the method breakthrough)
- **What it is:** one alphabet is a known kind and the other is any of the 26! permutations.
  - With the key known, this becomes a simple-substitution-like problem.
- **Results:**
  - R40/R41, free plaintext alphabet: exact rule-outs of 3.4 × 10⁸ and 1.09 × 10¹⁰ settings (L134, L135).
  - R42, free cipher alphabet: L136.
  - **R44b recovers 20/20 fresh planted messages blind** when the key is given (L140).
  - **Two free alphabets at once are still unsolved blind.** At 97 letters the quadgram score cannot tell the
    true text from wrong ones; only the word score can (L138, L139).

## 15. Statistics of K4 itself (R54, L32, L89)
- **Index of coincidence:** 0.0361, close to random (0.0385) and far below English (about 0.066).
  - No 97-letter window of K1–K3's plaintext is that flat (minimum 0.053).
- **What that means:** a single substitution or pure transposition of *typical* English is unlikely. Such flattening can also arise from long-period keys, running keys, homophonic systems and layered masks. The IC alone **cannot identify the algorithm**.
- **Ruled-out key behaviour:** no significant periodicity at lags 1–48. The strongest, lag 7, has a family-wise
  p of about 0.15.

## 16. Summary table

| Family | Example names | K4 status | Main rows |
|---|---|---|---|
| Pure transposition | columnar, route, rail fence, grille | **EXCL (letter counts)** | L01 |
| Monoalphabetic | Caesar, Atbash, affine, keyword | **EXCL** | L02 |
| Periodic polyalphabetic | Vigenère, Beaufort, Quagmire I–IV, Porta | **EXCL** for short periods; per-slot bijections partly OPEN | L03–L05, L21, L88, L89 |
| Generated keys | progressive, linear recurrences, LFSR | **EXCL** (in place) | L13, L15, L49 |
| Chain addition | Gromark, 4–8 digits, bases 3–26 | **EXCL** (fixed alphabets; keyword alphabets except one B26/b5 setting, WEAK/OPEN); two free alphabets FEAS/unreadable | L14, L22, L72, L141, L143 |
| Running key | K1–K3, Carter 1923, coordinates | **EXCL** (fixed/keyword); two free alphabets unreadable; unknown book OPEN | L90, L106, L109, R47 |
| Autokey | ciphertext/plaintext feedback | partly EXCL; long lags OPEN; R55 narrow affine feedback negative | L17, L27, L58, R51, R55 |
| Two-layer | substitution plus K3-style rotation or columnar | **EXCL/chance only in enumerated scopes**, general combinations OPEN | L47, L48, L115, L124, R46, R50 |
| Polygraphic | Hill, Playfair, 2/4-square | **EXCL only within tested variants**; R57 bounded Hill negative | L11, L61, L88, R57 |
| Fractionation | Bifid, Trifid | **EXCL** | L12, L88, L91 |
| Physical keys | World Clock, tableau, Morse, dates | **EXCL**/chance within reconstructed sources | L37–L42, L50, L96 |
| Nulls/masking | periodic nulls, salt | no coherent result; general case OPEN | L26, L81–L83 |
| Other languages | German, Dutch and others | no candidate | L62–L64, L108 |

## 17. What remains insufficiently tested (candidates for future rounds)
1. **Two fully free alphabets with an unknown key**, solved blind. The capability is missing (L138); this is the
   main technical gap.
2. **Homophonic substitution** (several cipher letters per plaintext letter). It fits K4's flat letter counts. Not
   tested.
3. **More general evolving alphabets.** R56 did test standard Chaocipher wheel updates with one word-keyed wheel, one standard wheel, and 26 phases: 51,324 states, 20/20 synthetic hidden-key controls; K4 top 0/24, best 3/24, no readable output. **Untested:** two arbitrary wheels, alternative mechanisms and transposition layers. The Chaocipher method was invented before 1990 but revealed publicly in 2010; this alone cannot prove whether Scheidt or Sanborn knew it.
4. **Cylinder/wheel ciphers** (Jefferson wheel, M-94, M-138 strip cipher). Hand devices of the US government.
   Not tested.
5. **Rotor-machine-style stepping** (alphabets that step like Enigma or Hebern). Only arithmetic "tableau stepping"
   was tested (L20).
6. **Interrupted or irregular keys** (the key restarts at markers). Not tested.
7. **Running keys from other named texts** (Bible passages, *The Egyptian Book of the Dead*, the Berlin Wall
   speeches of 1989, CIA documents, Sanborn's own texts), each with an edition hash.
8. **Long-lag autokeys** (lags 73–96) and plaintext autokey with free alphabets.
9. **Other transpositions combined with substitution:** turning grilles, AMSCO, Cadenus, and other grid sizes for
   double rotation with free alphabets.
10. **A masking step before encryption.** Scheidt has spoken of "masking"; the form is unknown (L26).
11. **ACA types with mixed alphabets that change during encryption:** Ragbaby, Slidefair, Portax, Alberti-style
    disk moves.

See `CRYPTOGRAPHY_REFERENCE.md` for how each of these works and `CRYPTANALYSIS_METHODS.md` for how to test them.

## 18. Merged R55–R57 method experiments (strict blind, all negative)
- **R55 affine-feedback:** 29,952 reversible settings; 20/20 exact synthetic unknown-key controls; top K4 1/24, best 2/24; 2/12 shuffled null scores higher.
- **R56 evolving two-wheel Chaocipher:** 51,324 initial states; 20/20 exact synthetic unknown-key controls; top K4 0/24, best 3/24; 4/12 nulls higher.
- **R57 Hill 2x2 with nonstandard 97-letter convention:** 97,344 matrices; 20/20 synthetic unknown-key controls; top K4 0/24, best 2/24; 6/12 nulls higher.
- Each experiment independently forward-reencrypted 240/240 synthetic and 156/156 K4/null witnesses, **froze full 97-letter raw outputs remotely in Git before any public-letter comparison**, and found no coherent K4 solution. Control passes mean the solver works for its *assumed, deliberately finite* model—not that the model matches K4.
- See [R55–R57 methodological audit](R55_R57_METHODOLOGY_AUDIT.md) for evidence hierarchy and prioritized follow-up.
