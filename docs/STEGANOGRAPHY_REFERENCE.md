# Steganography reference: hidden messages, and the anomalies on Kryptos

Claude Code, 1 Nov 2026.
- **Cryptography** hides the *meaning* of a message.
- **Steganography** hides the *fact* that there is a message.

Kryptos is a sculpture, so physical and visual hiding matters as much as letter arithmetic. This page lists:
- the classical techniques;
- the known oddities of the sculpture;
- a protocol for testing a hidden-message idea without fooling ourselves.

## 1. Classical techniques

### 1.1 Linguistic (hidden in text)

| Technique | How it works |
|---|---|
| **Null cipher** | The real message is the 1st (or *n*-th) letter of each word, line or sentence of an innocent text. |
| **Acrostic** | First letters of lines spell a word; **telestich** uses last letters, **mesostich** middle letters. |
| **Cardan grille** | A card with holes laid over a letter; only the letters under the holes form the message. A turning grille (see the crypto reference) is the transposition version. |
| **Baconian cipher** (Francis Bacon; full description 1623) | Each letter becomes 5 binary symbols (A/B: aaaaa = A, aaaab = B, …). These are hidden as two typefaces, upper/lower case, two colours, or any two-way property. 26 letters need 5 bits. |
| **Jargon / open code** | Pre-agreed innocent words stand for meanings ("the weather is fine" = proceed). Undetectable without the codebook. |
| **Deliberate misspellings and letter substitutions** | Errors placed at chosen positions, whose wrong letters or positions carry the message. |
| **Word or letter counts** | Line lengths or word lengths encode numbers (e.g. 3-1-4-1-5). |

### 1.2 Physical and visual

| Technique | How it works |
|---|---|
| **Invisible inks** | Lemon juice, milk, chemical inks revealed by heat, reagents or UV. |
| **Microdots** | A photographically shrunk page hidden as a full stop (WWII). |
| **Positional marks** | Pinpricks or tiny dots under chosen letters of a book or newspaper. |
| **Typography** | Letter spacing, size, raised or lowered letters, font shape differences. **Kryptos has raised or superscript letters** (see §2). |
| **Anamorphosis and viewing angle** | The image or text only resolves from one viewpoint, or with a mirror or cylinder. |
| **Shadows and light** | Sanborn's works project text as shadows (the *Cyrillic Projector*). Kryptos has a lodestone, a compass rose and a pool; the K1 plaintext mentions "shading" and "the absence of light". |
| **Objects and placement** | The orientation, latitude/longitude and bearing of parts of the installation. K2 gives coordinates near the sculpture. |

### 1.3 Digital (not relevant to a 1990 copper sculpture, listed for completeness)
- least-significant-bit image hiding;
- audio echo hiding;
- whitespace/zero-width characters;
- text-format tricks;
- network timing.

**Detection tools:** steganalysis by chi-squared on LSB pairs, RS analysis, and tools like `zsteg`, `stegseek` and
`binwalk`. Use them only on files *we* produced or on authenticated images, never on copyrighted photos committed to
the repo.

## 2. Known anomalies on Kryptos (candidate hidden channels)
These are widely reported features. **Each is a prior, not a fact about K4's method.** Verify against primary
photographs before relying on exact letters or positions.

| Anomaly | Where | What it is | Tested here? |
|---|---|---|---|
| **IQLUSION** for ILLUSION | K1 plaintext | Q in place of L | Misspelling-tolerant scoring (L45, L51); no direct stego test |
| **UNDERGRUUND** for UNDERGROUND | K2 plaintext | U in place of O | Same |
| **DESPARATLY** for DESPERATELY | K3 plaintext | A for E, E dropped | Same |
| **DIGETAL** for DIGITAL, **INTERPRETATI(U)** | Morse panel | E for I; final letters cut or misread | Morse key tests L96–L98 |
| **Misspelling letters as a set** | K1–K3 and Morse | The "wrong" letters Q, U, A, E (and others) are often proposed as a hidden word or key | **Not systematically tested.** |
| **K2 "ID BY ROWS" → "X LAYER TWO"** | K2 ending | One character was left out when carving (the X separator; its ciphertext letter is an S); Sanborn corrected it in 2006 | Carving-error robustness L35 |
| **X separators** | K2 (and K3's "MIST X CAN YOU SEE") | X used as a full stop | Punctuation model L87, L104 (no gain) |
| **Q = "?"** | K2 and K3 endings | Q stands for a question mark | Same |
| **Raised or superscript letters** | Cipher side (K1–K2 area) | A few letters are reported to sit slightly higher than their neighbours (commonly read as Y, A, R; some lists add D) | **Not tested;** needs primary photographs |
| **Extra L on the tableau** | Right panel, KRYPTOS tableau | One row has an extra letter L, breaking the regular pattern | Tableau-path keys L50 included the carved grid |
| **Morse panel ("K0")** | Granite and copper at the entrance | Phrases: VIRTUALLY INVISIBLE, SHADOW FORCES, LUCID MEMORY, T IS YOUR POSITION, DIGETAL INTERPRETATI(U), SOS, RQ, with many extra isolated E's | Morse letters and dots/dashes as key L96–L98; extra E's kept |
| **Compass rose and lodestone** | Granite slabs near the sculpture | An engraved compass rose with a lodestone (magnetic rock) nearby; its exact bearing and meaning are debated | Bearing ideas L42, L44 |
| **K4 length 97 (prime)** | K4 | A prime length rules out full rectangles; 97 = 4×24 + 1 was explored | L79 |
| **The "?" between K3 and K4** | Cipher side | Whether the "?" belongs to K3 or K4 is debated | Our ciphertext is the standard 97 letters |
| **Antipodes** (Hirshhorn Museum, 1997) | A sister sculpture | Reported to carry the Kryptos ciphertext (with small differences) and the *Cyrillic Projector* text | **Not compared;** primary photos needed |
| **Sanborn's other works** | *Cyrillic Projector* (UNC Charlotte, 1997) | Encrypted Russian text, projected as light and shadow | Context only |

### Notes on the Morse panel
- **Source:** R28 used a 1999-photo-backed transcription (rumkin.com/reference/kryptos/k0/), which keeps the isolated
  E's.
- **Reading order:** the physical reading order of the panels is **unverified**, so every order is a separate
  declared variant.
- **Ideas not yet tested:**
  - the count or positions of the extra E's as numbers;
  - the E's as Baconian bits;
  - "T IS YOUR POSITION" as an instruction (T = the 20th letter, or a tableau row);
  - "RQ" read as a prosign or abbreviation, or reversed.

### Notes on the misspellings
- **Wrong letters, in order K1 → K2 → K3:** Q (for L), U (for O), A (for E), plus a dropped E in DESPARATLY.
- **Popular readings:** taking the correct or wrong letters as a key or a word. A small, cheap family, but a
  **garden of forking paths**: there are many ways to read "the" misspelled letters. Fix the reading rules in
  advance (§5).

## 3. Steganography combined with cryptography
A message can be encrypted and *then* hidden, or hidden *inside* the plaintext before encryption (a "masking" step).
For K4 this suggests:
- **Null letters:** extra letters added before or after encryption (tested in part, L81–L83).
- **A pre-encoding of the plaintext:** a shift, reversal or code words before the main cipher. Scheidt's "masking"
  comment. **OPEN** (L26).
- **A key hidden on the sculpture:** a key taken from positions marked physically (raised letters, the extra L,
  Morse E's).

## 4. Detecting hidden text: what statistics can and cannot do
- **Linguistic stego** (null ciphers, acrostics): extract by rule, then score with a language model against nulls
  that use the same rule on random texts.
- **Baconian:** look for a two-way feature with a 5-bit period. Test whether the bit stream decodes to language
  better than shuffled streams.
- **Short sources** like the misspellings or raised letters give only a few symbols. Almost any reading can be made
  to "mean" something. Only a pre-registered rule plus a null distribution makes a result evidence.

## 5. Protocol for testing a stego hypothesis on Kryptos (same rules as the cipher work)
1. **Authenticate the source:** primary photographs or published transcriptions with provenance. Record which, and
   their uncertainties. **Do not commit copyrighted photos;** cite them by URL and archive ID.
2. **Pre-register the extraction rule(s):**
   - which letters;
   - in what order;
   - how they are converted (A=0 or A=1, KRYPTOS ranks, Baconian grouping);
   - every variant you will try.

   Commit the rule with its sha256 before extracting.
3. **Decide in advance what counts as success:**
   - a readable word of length ≥ *n*;
   - a key that decrypts K4 **blind**;
   - beating ≥ 99% of nulls.
4. **Nulls:** apply the identical rule to shuffled sources or to random positions on the sculpture. Correct for the
   number of variants tried.
5. **If the hidden text is a key for K4:** run it through the blind pipeline (`CRYPTANALYSIS_METHODS.md` B3).
   Freeze the output before looking at the 24 known letters.
6. **Report raw output unedited,** including failures, in `LEDGER.md`.

## Further reading
- **Fabien Petitcolas, Ross Anderson and Markus Kuhn, "Information Hiding — A Survey",** *Proc. IEEE* 87(7), 1999.
  The standard overview of the field.
- **David Kahn, *The Codebreakers*:** chapters on open codes, invisible inks and microdots.
- **Francis Bacon, *De Augmentis Scientiarum* (1623):** the biliteral cipher.
- **Kryptos anomaly lists:** Elonka Dunin's Kryptos pages (elonka.com/kryptos) collect the misspellings, the Morse
  transcription, the tableau's extra L and Antipodes differences, with photos. Use them as pointers to primary
  sources.
