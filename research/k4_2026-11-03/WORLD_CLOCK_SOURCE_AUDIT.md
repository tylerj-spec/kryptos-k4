# Berlin Urania World Clock — historical-source audit, not a derived key

**Scope:** identify the physical clock meant by Sanborn's 2025 clarification, the material/temporal uncertainties that R63 did **not** settle, and what would make a future clock-based cipher hypothesis reproducible. This document contains no published K4 plaintext clue words or offsets. It is **not** a new key, nor authorization to run K4 before control gates.

## 1. Confirmed physical object

- **Urania-Weltzeituhr, Alexanderplatz, East Berlin**, designed by industrial designer Erich John, unveiled **September 30, 1969**. The Berlin municipal visitor page and the clock's specialist site agree on the date and broad mechanics. [Municipality](https://www.berlin.de/en/attractions-and-sights/3561749-3104052-world-clock.en.html); [specialist site](https://www.weltzeituhr-berlin.de/en/urania-worldtimeclock).
- The exterior is a **24-sided / 24-zone** cylinder. Aluminum panels display geographically/time-zone-grouped city names. A **rotating hour band** inside the cylinder encodes local time for those zones. Above is a rotating model of the planetary system. This supplies several *different* potential material processes: letters, zones, hour numerals, rotation/time, direction and physical reading order. None is known to be the K4 key.
- A reconstructed city-name set is not the same as the *exact 1989 inscriptions*, let alone their panel order, line layout, source spelling, or state at a given hour.
- Designer/historical context: the original city selection was political as well as geographical. The [Berlin Senate's 2019 historical overview](https://www.berlin.de/aktuell/ausgaben/2019/dezember/aktuell-104-webversion.pdf) reports 80 city names approved by GDR authorities on 24 aluminum plates. Contemporary name and time-zone changes can break modern reconstructions.

## 2. Unresolved numerical contradiction — don't quietly choose a convenient count

| Source / date | Original city count claimed | Modern count claimed | Reliability / issue |
|---|---:|---:|---|
| [Weltzeituhr Berlin specialist website](https://www.weltzeituhr-berlin.de/en/urania-worldtimeclock) | **80** | **146** | Direct clock-specific site; unclear whether count includes regions vs names in some inventories. |
| [Berlin Senate magazine, Dec. 2019, p. 49](https://www.berlin.de/aktuell/ausgaben/2019/dezember/aktuell-104-webversion.pdf) | **80** | — | Institutional reporting, historical original approval. |
| [B.Z. interview with designer Erich John, Mar. 4, 2019](https://www.bz-berlin.de/archiv-artikel/so-tickt-die-weltzeituhr-auf-dem-alexanderplatz) | **97** | **148** | Photo caption says original 97 vs then 148. Could be a caption mistake, different units, or a later expansion; cannot choose by convenience. |
| [Berliner Zeitung, Dec. 12, 1997](https://www.berliner-zeitung.de/article/20-staedtenamen-wurden-bei-der-restaurierung-ergaenzt-frisch-poliert-die-weltzeituhr-dreht-sich-bald-7079) | — | **20 added at 1997 restoration** | Independent evidence text changed. This does not by itself explain the 80/97 or 146/148 disagreements. |

**Do not infer that the 97 in one caption is connected to K4's 97 letters.** The coincidence is intriguing but **not a measurement of 1989 clock inscriptions**. R49's prior photo chart, R63's 107-name union, 80 original, 97 captioned, and 146/148 modern are **different populations**. A run against one is not an exclusion of the others.

## 3. Source-integrity requirements for a literal clock-key hypothesis

Before presenting any clock inscription sequence as "historical," require:

1. A photograph or design drawing dated **no later than 1990** (or explain lower temporal certainty), with publication/location and provenance.
2. A **24-face** inventory: panel index 0..23, center coordinates/azimuth if known, ordered inscription rows, exact glyphs, old names, breaks and abbreviations, independent transcription confidence. No reconstructed sequence may be promoted to verified original without a full wrap-around photographic record or an original drawing.
3. An explicit orientation convention: absolute clock-face 0, clockwise/counterclockwise, upper/lower row, which side viewed, compass-rose vs face-index reference. A wrong origin rotates the entire key.
4. What turns vs what is fixed: **city labels fixed on panel, hour ring rotates**, planet model rotates above. Don't rotate names merely because hours move.
5. Which date/time was used for a reading: 1986 Egypt, November 1989 Wall fall, dedication Nov. 1990 are *events*, not verified clock-setting time-stamps; alternative time bases UTC, East Berlin local time, summer-time and date line need predeclared treatment.
6. Typed provenance and hashes: photographer, archive, capture date, known cropping and transformations, derived A–Z stream plus letter-for-letter path back to the original panel image; avoid reusing post-1997 city names as if original.
7. A disagreement file of disputed labels (two readers independently transcribe; unresolved letters marked unknown **without guessing**).

The [House of History 1968 world-clock model](https://www.hdg.de/lemo/bestand/360grad/360gradobjekt-weltzeituhr-modell.html), [Berlin monument register](https://denkmaldatenbank.berlin.de/daobj.php?obj_dok_nr=09020854), and Berlin historical magazines offer promising provenance leads but do not yet supply a complete audited 1989 inventory.

**Copyright/permissions:** cite image source and use cropped research references only with lawful access/licensing. Do not commit unauthorised full-resolution historic photographs, museum scans, or copyrighted page reproductions to Git.

## 4. Which physical data could encode a key? (Hypotheses, not discoveries)

Ordered by testability, **not** asserted probability:

| Candidate input | Testable key operator | Missing fact / failure condition |
|---|---|---|
| Historically accurate ordered **panel text** | Letters read fixed by panel index and row rule | Full original inventory, exact German spelling and face zero |
| **Hour ring** by integer zone | 24-hour digit or zone offset stream, as decimal/binary mod-26 | Which local time/date/zone origin, treatment of multiple names per face |
| **Local solar/planetary model** | Wheel stepping, phase increments or cyclic index | Actual gear ratios/initial orientation; don't infer from sculpture metaphor |
| **Compass rose / orientation** | Read-order rotation, location-bearing-derived start index | Surveyed orientation at artist's work, mapping sculpture vs Berlin clock |
| **Mixed source** (name index + hours) | Finite-state/irregular keystream with a source-derived reversible rule | Must predefine composition rule without fitting 97 outputs |
| **Textual source about World Clock** | German running key from a pre-1990 brochure/design note | Authentic edition, source length, independent index/offset |

**Do not** conflate the Urania clock with the "Berlin Clock" / `Mengenlehreuhr` four-row binary-light timepiece. The latter is an unrelated object and lacks the same city-name panels. Sanborn's 2025 indication identifies Urania, so unrelated clock-based guesses have lower evidence grade.

## 5. Relationship to current repository experiments

- `r49/prior_photo_360_chart.json` + R23 material: **reconstructed chart**, source mixture, orientation and historical plate caveats (see `LEDGER.md` rows L25, L37, L77).
- `r63/data/clock_names.txt`: a **107-name model vocabulary**, not an authenticated 1989 physical sequence. R63 key model trained on a synthetic stream of names; clock holdout **10/10** detection applies to *this* distribution. K4 **81/100 nulls scored >=** K4: no in-place signal under this family.
- **Not yet established:** exact 1988–90 name order, digit/hour setting, time-zone-offset normalization, a numerical wheel mechanism, or Clock-name model combined with transposition (proposed R64).
- `r61` and `r62c` found a post-selected `COL_LT` score gap that was retested as a *fixed structural statistic*. It should not be interpreted as evidence that a Berlin clock face points to a particular column or key. Multiple-testing/selection caveats apply.

## 6. Highest-value archival requests / public research

1. **Erich John original design/sketches** and Hans-Joachim Kunsch inscription/cutting patterns from c. 1968–69; request permission to inspect a complete plate inventory (do not claim they are online).
2. **Pre-1990 images** from East Berlin municipal collections, Haus der Geschichte or press agency covering all 24 faces; date, azimuth and original caption per image.
3. **1997 restoration log / replacement plate list**: can reconcile which names were added, changed or corrected, and perhaps the 80-vs-97 conflict.
4. **Independent transcription challenge**: two blind human transcribers for the same photo; count unresolved letters; only then hash final time-stamped variants for cryptographic tests.
5. **Time-band mechanics manual** from clock specialist/designer: ratio, hour line and reset; freeze the *physical operator* before trying ciphertext.

### Release threshold for a future clock search

**Only a verified, date-stamped pre-1990 inscription inventory or engineering mechanism should justify a new strict physical-source key search.** Otherwise use exploratory models (clearly labelled) with independent planted controls and avoid extrapolating negative or positive R63 statistics to authentic mechanical clock behavior.
