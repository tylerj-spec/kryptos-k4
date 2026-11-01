# Kryptos fact sheet (what is known, with sources and confidence)

Claude Code, 1 Nov 2026. These facts are widely published.

| Mark | Meaning |
|---|---|
| ✔ | Checked in this repo, or with a primary or major-press source |
| ~ | Widely reported, not independently checked by us |

Context for interpretation only. Per the project rules, none of this may be fed to a blind solver as a crib or
mask.

## 1. The sculpture
- **What and where:** *Kryptos*, by **Jim Sanborn**, was dedicated **3 November 1990** in the courtyard of the CIA's
  New Headquarters Building, Langley, Virginia. ✔
- **Cipher design:** with **Ed Scheidt**, retired chairman of the CIA Cryptographic Center. ✔
- **Layout:** two S-shaped copper screens.
  - The **left half** holds the ciphertext, about 865 characters in four parts K1–K4.
  - The **right half** holds a **Vigenère-style tableau** keyed with KRYPTOS. ✔
- **Surroundings:** granite slabs, a compass rose with a lodestone, a pool, and copper plates with **Morse code**
  (the "K0" text) near the entrance. ~
- **Sister works:** *Antipodes* (Hirshhorn Museum, 1997) and *Cyrillic Projector* (UNC Charlotte, 1997). ~

## 2. The four sections

| Part | Method | Key / alphabet | Plaintext (as carved, misspellings kept) |
|---|---|---|---|
| **K1** | Quagmire III (keyed Vigenère) | alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ`, key **PALIMPSEST** | BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF **IQLUSION** |
| **K2** | Quagmire III | same alphabet, key **ABSCISSA** | IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE ? THEY USED THE EARTHS MAGNETIC FIELD X THE INFORMATION WAS GATHERED AND TRANSMITTED **UNDERGRUUND** TO AN UNKNOWN LOCATION X DOES LANGLEY KNOW ABOUT THIS ? THEY SHOULD ITS BURIED OUT THERE SOMEWHERE X WHO KNOWS THE EXACT LOCATION ? ONLY WW THIS WAS HIS LAST MESSAGE X THIRTY EIGHT DEGREES FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST X LAYER TWO |
| **K3** | Transposition (double rotation; our route R24x8/CW/inv) | grid sizes / KRYPTOS columnar equivalent | SLOWLY **DESPARATLY** SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER PART OF THE DOORWAY WAS REMOVED WITH TREMBLING HANDS I MADE A TINY BREACH IN THE UPPER LEFT HAND CORNER AND THEN WIDENING THE HOLE A LITTLE I INSERTED THE CANDLE AND PEERED IN THE HOT AIR ESCAPING FROM THE CHAMBER CAUSED THE FLAME TO FLICKER BUT PRESENTLY DETAILS OF THE ROOM WITHIN EMERGED FROM THE MIST X CAN YOU SEE ANYTHING Q |
| **K4** | **Unknown** | unknown | 24 of 97 letters known (below) |

**Checks and notes on the table:**
- The K1–K3 plaintext in `k4kit/data/k1k3_plaintext.txt` matches this table. ✔ (That file holds K3 twice; L135.)
- **K2's ending:** in April 2006 Sanborn said a character had been left out of the carving. In the plaintext it is
  the X sentence separator; analyses identify the missing ciphertext letter as an S. The ending therefore reads
  "X LAYER TWO", not the earlier "ID BY ROWS". ✔
  ([Kryptos Group announcement](https://elonka.com/kryptos/CorrectedK2Announcement.html))
- **K2's coordinates** (38°57′6.5″N, 77°8′44″W) point to a spot on the CIA grounds near the sculpture. ~
- **K3** paraphrases Howard Carter's account of opening Tutankhamun's tomb on 26 November 1922. ✔

## 3. K4 ciphertext and the published clues
```
         1         2         3         4         5         6         7         8         9
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```
- **Length:** 97 letters, all 26 letters present.
- **sha256** (with a trailing newline): `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`. ✔
- **Letter counts:**
  `A4 B5 C2 D3 E2 F4 G4 H2 I4 J3 K8 L4 M1 N3 O5 P3 Q4 R4 S6 T6 U6 V2 W5 X2 Y1 Z4`.
  - **IC:** 0.0361. ✔

**Published plaintext (1-based positions):**

| Released | Positions | Ciphertext | Plaintext |
|---|---|---|---|
| Nov 2010 | 64–69 | NYPVTT | **BERLIN** |
| Nov 2014 | 70–74 | MZFPK | **CLOCK** |
| Jan 2020 | 26–34 | QQPRNGKSS | **NORTHEAST** |
| Aug 2020 | 22–25 | FLRV | **EAST** |

The dates are ~; the positions and letters are ✔ and used throughout the repo.

**Facts that follow directly** (all ✔):
- **Three plaintext E's but only two ciphertext E's:** not a pure transposition (L01).
- **`QQ` (26–27) → `NO`:** not a single substitution alphabet (L02).
- **Self-encryptions:** position 33 S→S and position 74 K→K. A cipher in which no letter can encrypt to itself
  (Enigma-style) is excluded in place.
- **Layout:** 21 unknown + 13 known + 29 unknown + 11 known + 23 unknown. 73 letters are unknown.

## 4. Solution history
- **Who solved K1–K3:**
  - An NSA team solved K1–K3 around 1992–93; this was disclosed later. ~
  - CIA analyst David Stein solved them by hand in 1998. ~
  - Jim Gillogly published a computer solution in 1999. ✔ (widely reported)
- **Scheidt's statements:** he said all four passages were in English and that K4 used a technique to mask English
  characteristics (WIRED, 2005; L33). ~
- **Further riddle:** Sanborn has said solving K4 leads to a further riddle (often called K5). ~
- **2025:**
  - **September:** two writers, **Jarett Kobek and Richard Byrne**, found K4 plaintext material in Sanborn's papers
    at the Smithsonian's Archives of American Art. They recovered the plaintext, **not the method**, and have said
    they will not publish it. ✔
    ([Scientific American](https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years),
    [RR Auction note](https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/))
  - **20 November:** RR Auction (Boston) sold Sanborn's K4 archive (solution, charts and a meeting with Sanborn) to
    an anonymous buyer for about **$962,500**; reports give $962,500–$963,000. ✔
    ([WBUR](https://www.wbur.org/news/2025/11/24/kryptos-sculpture-cia-headquarters-decipher-boston-auction))
  - **12 November talk and open letter:** Sanborn tied BERLINCLOCK to the **Weltzeituhr** (Urania World Clock) at
    Alexanderplatz, Berlin, not the Mengenlehreuhr. He linked K4's ideas to his late-1986 Egypt trip and the 1989
    fall of the Berlin Wall, and described its theme as "delivering a message". ✔
    ([Scientific American](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/);
    `r38/RESEARCH_NOTES.md`)
- **As of 1 Nov 2026:** no plaintext or method has been published; the method remains unknown publicly. **This
  project seeks an independently reproducible method.** It does not use leaked or archival plaintext, and we know of
  none that is public.

## 5. The Weltzeituhr (Urania World Clock), Alexanderplatz
- **Design:** by **Erich John**, inaugurated in 1969 in East Berlin. ✔ (`r49/`, berlin.de)
- **Physical form:** a **24-sided** drum, one face per time zone, with city names; a rotating hour ring; a compass-rose
  ground mosaic (later lost). ✔
- **City names:** about 80 in 1969 and 146 today. About 20 were added in the **1997** restoration, so modern lists are
  **not** the 1988–90 text. ✔ (`r49/RESEARCH_STRATEGY.md`)
- **Our reconstruction:** photo-derived 1969–1990 face text and orientation, in
  `archive/2026-10-26_chatgpt_starter/sources/world_clock_360.md` and `r49/prior_photo_360_chart.json`.
- **Relation to Kryptos:** the 1990 dedication predates the 1997 changes.
- **ENE from the clock:** the ENE direction from the clock falls on the +8 face (L42).

## 6. Things NOT to rely on
- **Websites presenting a "solved" K4:**
  - their key tables are back-solved from their own chosen plaintext (L60, R48 notes);
  - any 97-letter text can be fitted that way.
- **Modern World Clock city lists** used as if they were the 1990 text.
- **Copyrighted photos:** do not commit them to the repo. Cite them by URL or archive ID.
