# Cryptography reference: classical to modern, with Kryptos relevance

A working reference for this project, written in our own words (Claude Code, 1 Nov 2026). Each entry gives:
- how the cipher works;
- what it does to the letters (which tells you how to spot it);
- whether K4 could be this cipher.

Status of each family against K4: `CIPHER_TYPES_TESTED.md`. How to attack each family: `CRYPTANALYSIS_METHODS.md`.

## How to read the "fingerprint" lines
Three quantities tell families apart:
- **Letter counts:**
  - a **transposition** keeps them exactly;
  - a **monoalphabetic** substitution permutes them, so the frequency shape stays;
  - a **polyalphabetic** cipher flattens them.
- **Index of coincidence (IC):** the probability that two random letters of the text match.

  | Text | IC |
  |---|---|
  | English | about 0.066 |
  | Uniform random | 0.0385 |
  | K4 | 0.0361 |

- **Symbol set:** 25 letters (5×5 squares), 26, 27 (Trifid), digits only, or 5–6 letters (ADFGVX).
  - K4 uses all 26 letters, which rules out unmodified square, digit and ADFGVX outputs.

---

## 1. Transposition ciphers (rearrange letters)
**Fingerprint:** the letter counts equal the plaintext's, and the IC is English-like (about 0.066).
**Can K4 be this?** No, not as a pure transposition: K4 has 2 E's and the clues need 3. It is possible as one layer
of two.

| Cipher | How it works |
|---|---|
| **Rail fence** | Write the text in a zigzag over *n* rails, then read rail by rail. |
| **Columnar** | Write in rows of width *w*; read the columns in the order given by a keyword (letters ranked alphabetically). It is "incomplete" if the last row is short. |
| **Double columnar** | Columnar twice, often with two keywords. A serious WWI/WWII field cipher. |
| **Myszkowski** | Columnar, but repeated keyword letters read their columns together, row by row. |
| **Route** | Write in a grid; read along a path: spiral, boustrophedon (alternate directions), diagonals. |
| **Rotation / K3 style** | Write in rows of width *w1*, rotate the grid a quarter-turn, rewrite at width *w2*, rotate again. K3 uses grids of 24 and 8 columns (our route R24x8/CW/inv). |
| **Decimation** | Read every *d*-th letter, cycling (*d* coprime to the length). |
| **AMSCO** | Columnar where cells hold alternately 1 and 2 letters. |
| **Cadenus** | Columns of 25 rows, each rotated by a keyword letter's position, then read across (ACA type). |
| **Turning grille** (Fleissner) | A square card with holes; write through the holes, turn 90°, repeat four times. A 10×10 grille holds 100 letters, so K4's 97 would need 3 nulls. |
| **Cardan grille** | A mask over an innocent-looking letter or text; only the letters under the holes matter. This is steganography as much as cryptography (see the stego reference). |

## 2. Monoalphabetic substitution (one fixed alphabet)
**Fingerprint:** the IC equals the plaintext's; the frequency shape is preserved (the most common letter is
probably E, and so on).
**Can K4 be this?** No: `QQ` decrypts to `NO`.

| Cipher | Rule |
|---|---|
| **Caesar / shift** | `c = p + k mod 26` |
| **Atbash** | A↔Z, B↔Y, … |
| **Affine** | `c = a·p + b mod 26`, with `a` coprime to 26 |
| **Keyword / mixed alphabet** | The plaintext A–Z maps onto a keyword alphabet such as KRYPTOSABC… |
| **Aristocrat / Patristocrat** | ACA names for general simple substitution, with word breaks kept or removed. |
| **Homophonic** | Each plaintext letter has *several* cipher symbols, chosen to flatten frequencies (E might have 12, Z one). The output is often numbers; with exactly 26 output letters it is constrained but possible. **It fits K4's flat IC and has not been tested.** |
| **Nomenclator** | A substitution alphabet plus a code list for whole words and names (historical diplomatic use). |

## 3. Polyalphabetic substitution (the alphabet changes with position)
**Fingerprint:** a low IC. With a **periodic** key, IC and Kasiski tests reveal the period; with a non-repeating key
there is no period.
**Can K4 be this?** This is the family most consistent with K4's statistics. Short periods are excluded.

**The tableau cipher (core formula).** `c = CA[PA⁻¹(p) + k]`. The cipher letter is found in a 26×26 table (the
tableau) at row *k* and column *p*.

| Variant | Formula / alphabets |
|---|---|
| **Vigenère** | AZ/AZ, `c = p + k` |
| **Beaufort** | `c = k − p`. It is reciprocal: encryption = decryption. |
| **Variant Beaufort** | `c = p − k`, which is Vigenère decryption. |
| **Gronsfeld** | Vigenère with digit keys 0–9. |
| **Quagmire I** | keyed plaintext alphabet, A–Z cipher alphabet |
| **Quagmire II** | A–Z plaintext alphabet, keyed cipher alphabet |
| **Quagmire III** | the same keyed alphabet on both sides: **K1 and K2** (KRYPTOS alphabet; keys PALIMPSEST and ABSCISSA) |
| **Quagmire IV** | two different keyed alphabets |
| **Porta** | 13 reciprocal half-alphabets selected by key-letter pairs (A/B, C/D, …). Excluded for K4 (L88). |

Equivalences to remember:
- With free alphabets, VIG, BEAU and VARB are relabellings of each other. Count them as one setting (L92).
- **The KRYPTOS sculpture's right panel is a Quagmire III tableau:** the KRYPTOS alphabet, repeated with shifts.

**Key types:**

| Key type | How it works |
|---|---|
| **Periodic** | A keyword repeats. |
| **Progressive** | The alphabet shifts by a fixed step every period. |
| **Running key** | A long text (book, passage) gives the key letters. If the key text is English, `c − k` and `c − p` are both English, so the text can be split by "two-language" methods. |
| **Autokey** | After a primer, the key is the plaintext itself (autoclave) or the ciphertext, shifted by a lag *L*. |
| **Chain addition / Gromark** | Numeric primer extended by `k_i = k_{i−b} + k_{i−b+1} mod B`; used with a keyed cipher alphabet (ACA "Gromark"). |
| **Generated** | A linear recurrence or LFSR (an electronic-era idea). |
| **Interrupted** | The key restarts at chosen points. |
| **One-time pad** | A truly random key as long as the message, used once. **Provably unbreakable** if used correctly. Then K4 would be unsolvable without the pad. |

**Ciphers whose alphabets move during encryption (ACA types):**

| Cipher | How it works |
|---|---|
| **Ragbaby** | A keyed alphabet; each word's letters shift by an increasing count. |
| **Slidefair** | A digraphic slide of two alphabets. |
| **Portax** | A digraphic, Porta-style slide applied to text written under a periodic key. |
| **Chaocipher** (Byrne, 1918) | Two alphabets (left for cipher, right for plain) permuted after **every** letter, by a fixed rule. It acts like a self-modifying Quagmire. Not tested on K4. |
| **Alberti disk** (1467) | An outer fixed ring and an inner moving ring; the inner ring is turned every few letters. It is the ancestor of all polyalphabetics. |
| **Jefferson wheel / M-94** | 25–36 lettered disks on an axle. Set the plaintext along one row; send any other row. |
| **M-138 strip cipher** | The same idea with sliding strips. |

## 4. Polygraphic substitution (groups of letters)
**Fingerprint:** effects appear at even (or block) alignment; Playfair never has a doubled letter inside a pair and
uses 25 letters.

| Cipher | How it works |
|---|---|
| **Playfair** | A 5×5 keyed square (I = J); pairs are replaced by rules: same row, same column, rectangle. |
| **Two-square / Four-square** | Pairs looked up across 2 or 4 squares. |
| **Hill** | Blocks of *n* letters as vectors, multiplied by an invertible *n×n* matrix mod 26. Linear, so *n²* known plaintext–ciphertext pairs break it. Excluded for K4 (L11, L61). |

## 5. Fractionation (split letters into pieces, mix, rejoin)

| Cipher | How it works |
|---|---|
| **Polybius square** | Each letter becomes two coordinates (row, column) in a 5×5 grid. |
| **Bifid** (Delastelle) | Polybius coordinates written in two rows, read across in blocks of a chosen period, then re-paired into letters. |
| **Trifid** | The same with a 3×3×3 cube (27 symbols). |
| **ADFGVX / ADFGX** (WWI German) | Polybius with letters A, D, F, G, (V,) X as coordinates, then columnar transposition. The output uses only 5–6 letters. |
| **Straddling checkerboard** | Common letters become one digit, rare ones two. Used in the **VIC** cipher (Soviet, 1950s) and the **Nihilist** ciphers. The output is digits. |
| **Morse-based fractionation** | Pollux, Morbit, fractionated Morse: letters become dots and dashes, which are regrouped into new letters. Relevant because Kryptos has a Morse panel. |

## 6. Codes (word-level)
- **What they are:** a codebook replaces words or phrases by code groups.
- **Book ciphers** give page/line/word numbers, or the first letters of indexed words. Their output is numbers, but
  a Sanborn variant could index letters in K1–K3 or the tableau.
- **Fingerprint:** numbers, or letter groups of fixed length.

## 7. Machine ciphers (for completeness)
- **Rotor machines** (Hebern, Enigma, SIGABA, Typex): each key press steps one or more rotors, so every letter gets
  a new alphabet, with periods in the thousands to millions. K4 is hand-made, but "stepping alphabet" ideas are
  hand-operable.
- **Hagelin M-209:** pin-and-lug wheels generate a pseudo-random Beaufort key.
- **Fingerprint:** a flat IC and no short period. This resembles K4's statistics; with 97 letters it is
  indistinguishable from a running key.

## 8. Modern cryptography (not applicable to a hand-carved 1990 puzzle; here so we don't waste time)
- **Symmetric ciphers** (DES 1977, AES 2001): work on bits in blocks of 64/128 bits. Their output is binary and
  needs encoding (hex, Base64) to become letters. K4's A–Z text is not such an encoding.
- **Stream ciphers and XOR:** `c = p XOR keystream`. The letter analogue is Vigenère with a generated key (§3).
- **Public-key** (RSA 1977, Diffie–Hellman 1976): number theory. Irrelevant to a hand cipher.
- **Hash functions** (MD5, SHA-256): one-way, with no decryption. K4 cannot be "decrypted" from a hash (R54 note).
- **What modern ideas do carry over:**
  - Kerckhoffs's principle: assume the method is known and only the key is secret;
  - key-space size versus a practical search;
  - known-plaintext attacks, which is exactly what the 24 clue letters are.

## 9. Kryptos-specific constructions seen in K1–K3
- **K1:** Quagmire III; alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ`, key **PALIMPSEST**.
- **K2:** Quagmire III; same alphabet, key **ABSCISSA**.
  - Inserted X's act as sentence separators.
  - A carving omission (one character) was corrected by Sanborn in 2006: the ending reads "X LAYER TWO", not
    "ID BY ROWS".
- **K3:** transposition only, a double rotation (keyed by grid sizes, often described via KRYPTOS-columnar
  equivalents). The plaintext paraphrases Carter's 1922 account of opening Tutankhamun's tomb.
  - It ends "…CAN YOU SEE ANYTHING Q", with Q standing for the question mark.
- **K4:** unknown.
  - Scheidt has described a "masking" technique (WIRED, 2005).
  - Sanborn has said solving K4 is not the end: there is a further riddle, often called K5.

## Sources and further reading (public, standard references)
- **American Cryptogram Association (ACA):** cipher type descriptions, including Gromark:
  https://www.cryptogram.org/resource-area/cipher-types/
- **Books:**
  - Helen Fouché Gaines, *Cryptanalysis: A Study of Ciphers and Their Solution* (1939; Dover). The classic manual
    for transposition and substitution.
  - William F. Friedman, *Military Cryptanalysis* parts I–IV (public domain, NSA release). Periodic and aperiodic
    systems, IC, running keys.
  - David Kahn, *The Codebreakers* (1967/1996). History of every family above.
  - Elonka Dunin and Klaus Schmeh, *Codebreaking: A Practical Guide* (2020/2023). Modern hand methods, including a
    Kryptos chapter.
- **Chaocipher method:** Moshe Rubin, "Chaocipher Revealed: The Algorithm" (2010).
