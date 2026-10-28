# Research notes, 22 Oct 2026: World Clock (Weltzeituhr) 1988–90, and other K4 material

Claude did this research directly with web search after the deep-research run could not start.
Limits of this session: no image viewing; and Wikimedia Commons, the Wayback Machine, ZEFYS page images, opencaching and X posts could not be opened from here.
Labels: **[P]** = primary source (archive record, the organisation's own page or rules); **[S]** = secondary; **[I]** = Claude's inference, not documented.

## 1. World Clock: what is documented

| Fact | Source |
|---|---|
| Unveiled 30 Sep 1969; designer Erich John; about 10 m tall, 16 t | [S] de.wikipedia |
| One source says it started moving on 3 Oct 1969 | [S] DDR Museum blog 2017 |
| 24-sided drum, one face per main time zone; city names milled or punched into aluminium | [S] de.wikipedia; Bildhauerei in Berlin |
| City plates: 24 rectangular, reddish-brown enamelled plates; the original plates were hand-engraved | [S] Bildhauerei in Berlin; Berliner Kurier, 31 Oct 2024 |
| About 146 place names plus one date-line entry (other sources say 148) | [S] de.wikipedia; en.wikipedia; geocache GC7B92Q |
| Hour ring 1–24, colour-coded; each number sits under one face | [S] en/de.wikipedia |
| The hour ring runs 5% fast; cams stop it on each hour, and the DCF77 (Mainflingen) time signal releases it | [S] de.wikipedia |
| Planet model turns once per minute; wind-rose mosaic underneath; four CET clocks on the column | [S] de/en.wikipedia |
| **1997 renovation, Oct–Dec 1997:** Leningrad → Sankt Petersburg; Alma Ata → Almaty; Bratislava → "Pressburg" (Slovakia protested); 20 cities added; time-zone assignments changed (e.g., Kiev); Jerusalem and Tel Aviv first added in 1997 | [S] de.wikipedia, citing Berliner Zeitung 12 Dec 1997 and 20 Dec 1997, taz 20 Dec 1997, Märkische Allgemeine 24/25 Dec 1997 |
| Tel Aviv, Cape Town and Seoul were among the cities added; New Delhi is engraved "NEW DELHI +30" | [S] en.wikipedia |
| Current UTC−8 face includes Vancouver, Dawson, San Francisco, Los Angeles | [S] lepetitjournal.com |

### New: a primary 1990 record of the pre-renovation faces
The Deutsche Kinemathek / bpb archive "Wir waren so frei" holds photos by Monika Waack taken at the clock on **3 Oct 1990** (reunification night), when the clock still had its 1969 configuration. The catalogue field "Text im Bild" transcribes the legible faces **[P]**:
- Object 1612: "Krasnojarsk / Novosibirsk / Hanoi / Bangkok / Pnom Penh / Singapur + / Jakarta / [...] / Peking / Shanghai / Manila / Jakutsk / [...] / Tokio / [...] / Sydney / Canberra / Melbourne". Image: `http://wwsf.deutsche-kinemathek.de/media/wwsf/images/1/4/3775_ca_object_representations_media_1444_mediumlarge.jpg`
- Object 1615: "Dacca / Jakarta / [...] / Tokio". Image: `http://wwsf.deutsche-kinemathek.de/media/wwsf/images/1/4/75279_ca_object_representations_media_1447_mediumlarge.jpg`

**[I]** The names group into consecutive faces:
- UTC+7: Krasnojarsk, Novosibirsk, Hanoi, Bangkok, Pnom Penh, Singapur +(30), Jakarta
- UTC+8: Peking, Shanghai, Manila
- UTC+9: Jakutsk, Tokio
- UTC+10: Sydney, Canberra, Melbourne
- Dacca sits on the face before UTC+7.

**[I] Evidence the 1969 plates were already out of date by 1989–90:**
- Singapore is shown as +30 min on the +7 face, i.e. UTC+7:30. Singapore left UTC+7:30 on 31 Dec 1981 (en.wikipedia "Singapore Time").
- Novosibirsk on the +7 face matches the Soviet-era offset: +07 until 1991 and again 1992–93 (IANA tz).

This fits the 1997 reports that "some cities were in the wrong time zone".

### Still not documented
- The complete face-by-face city list, pre-1997 or post-1997. No transcription exists on any page reached.
- Which face is the reference face, and how the faces line up with the wind rose.
- An explicit statement of the rotation direction.

**[I] Direction can be derived from photos.** Each fixed face must see its hour number increase, so the ring turns opposite to the direction in which the time zones increase around the drum.
- If the Kinemathek transcriber read left to right (+7 → +10 left to right, seen from outside), the zones increase counter-clockwise seen from above, so the hour ring turns clockwise seen from above.
- To confirm, one needs either two photos of the same face with known times or one view with legible faces and ring numbers.

### Where to look next (needs a browser or the linked desktop app)
1. The two Kinemathek images above, and other photos in that archive: the 4 Nov 1989 demonstration (e.g., object 7480 by Jan Kornas) and the 7 Oct 1989 photos.
2. ZEFYS *Neues Deutschland* online archive (ZDB 2532889X, freely viewable issues via DFG-Viewer). Check issues of 30 Sep – 4 Oct 1969 for the inauguration report and any city list.
3. Berlinische Galerie BG-AS 1436.005915: "Alexanderplatz, Weltzeituhr", June 1970, Ostberliner Fotoarchiv, Erich John. No online image.
4. Industriesalon Schöneweide, Kurt Schwarz slide KS-7-NB_1013 (1970s), via museum-digital.
5. Wikimedia Commons, category of the Weltzeituhr, including Bundesarchiv Bild 183 donations.
6. The 1997 press articles listed above, which name the renamed and added cities.

### Status for L25 (World Clock-derived keys)
Still **OPEN**. What is new: a primary 1990 record of four or five consecutive faces, and evidence that the pre-1997 plates carried outdated offsets.

The remaining free choices for any clock-derived key rule:
- the full city list on each face
- the reference face
- the reading direction
- which quantity becomes key material (first letters, city counts, ring numbers…)
- the date and time setting

A related public project, kryptos.today, reports that one narrow "Weltzeituhr first-letter keystream" cell failed (0/96 crib-passing, 2 May 2026) **[S]**.

## 2. Other K4 material

- **Paradigm (12 Jun 2026), Robinson & Huang [P].**
  - They bought the archive.
  - Sanborn typed the plaintext on a fresh laptop; its SHA256 went to Google Cloud KMS, which produced an HMAC tag. "The plaintext never left the device."
  - Candidate checks cost $1 each. The rules say "No prize will be awarded for K4 unless Sponsor states otherwise".
  - "We plan to release K5 in the future" (not released as of these notes).
  - Normalisation rules for submissions are not stated.
- **Paradigm Kryptos CTF, PK1–PK10 ($1,000 each) [P].** All ten were solved by about early Oct 2026 (TheBenMeadows PR: PK9/PK10 accepted 3 Oct 2026). Dan Robinson posted "PK9 and PK10 have fallen … Now on to K4!". The solvers' published ground truth [S] (ahardkore PR #14; benjacasas02 README):

  | Puzzle | Method |
  |---|---|
  | PK1 | Quagmire III, KRYPTOS alphabet, key PROVENANCE (period 10) |
  | PK2 | complete columnar, width 7 |
  | PK3 | Quagmire III with key = sum of a period-10 and a period-8 key (PENTIMENTO + ORDINATE) |
  | PK4 | T(8) → Q(5) → Q(9) |
  | PK5 | T(8) → running key = PK4 plaintext |
  | PK6 | T(9) → T(9) → Q(6) |
  | PK7 | Q(6) → Hill 3×3 |
  | PK8 | four stacked Quagmires, periods 4, 5, 6, 7 |
  | PK9 | Q(7) Q(6) Q(5) T(8) |

  Nothing says these share K4's method; Paradigm say they do not know the K4 plaintext. They are still the clearest public picture of the method space the new stewards consider "Kryptos-like". **This motivated L36 (multiclock.py).**
- **Discovery story [S].**
  - The plaintext scraps were 1990 copies, cut into strips and taped out of order (RR Auction, 23 Oct 2025).
  - Sanborn: "K4 has not been solved. K4 has been discovered and it points in the direction of K5."
  - The Smithsonian files are sealed until about 2075 (en.wikipedia "Kryptos").
- **Antipodes [S].** It includes K4 (Elonka Dunin's Antipodes page). The reported differences are two extra dots (in part 2), spacing and alignment. No K4 letter difference is reported, so Antipodes gives no correction for a possible K4 carving error.
- **Bean 2021 [P].** "Cryptodiagnosis of Kryptos K4", HistoCrypt 2021, pp. 25–33: evidence for a one-to-one plaintext/ciphertext letter relation, pointing to Gromark. This is our L14/L22.
- **solvekryptos.com [S].** A reconstructed plaintext plus a mechanism that the site itself says is mostly back-solved from that reconstruction. It is not usable as evidence.

## Sources
- de.wikipedia, "Weltzeituhr (Alexanderplatz)": https://de.wikipedia.org/wiki/Weltzeituhr_(Alexanderplatz)
- en.wikipedia, "World Clock (Alexanderplatz)": https://en.wikipedia.org/wiki/World_Clock_(Alexanderplatz)
- Bildhauerei in Berlin, "Urania-Weltzeituhr": https://bildhauerei-in-berlin.de/bildwerk/urania-weltzeituhr-7851/
- Deutsche Kinemathek "Wir waren so frei", object 1612: https://wwsf.deutsche-kinemathek.de/index.php/Detail/Object/Show/object_id/1612/lang/en_US
- Deutsche Kinemathek "Wir waren so frei", object 1615: https://wwsf.deutsche-kinemathek.de/index.php/Detail/Object/Show/object_id/1615/lang/en_US
- Deutsche Kinemathek "Wir waren so frei", object 7480: https://wwsf.deutsche-kinemathek.de/index.php/Detail/Object/Show/object_id/7480
- Berlinische Galerie, item 150237: https://sammlung-online.berlinischegalerie.de/en/collection/item/150237/
- museum-digital, Kurt Schwarz slide: https://berlin.museum-digital.de/pdf/object/110253.pdf?lang=en
- ZEFYS, Neues Deutschland calendar: https://zefys.staatsbibliothek-berlin.de/kalender/auswahl/date/1969-9-14/2532889X/
- DDR Museum blog: https://www.ddr-museum.de/en/blog/2017/world-time-clock
- Le Petit Journal: https://lepetitjournal.com/berlin/histoire-et-fonctionnement-de-lhorloge-de-lalexanderplatz-66307
- Berliner Kurier, 31 Oct 2024: https://www.berliner-kurier.de/ddr/erfinder-der-demolierten-weltzeituhr-kein-respekt-mehr-vor-dem-ddr-erbe-li.2267830
- Singapore Time: https://en.wikipedia.org/wiki/Singapore_Time
- IANA tz, Novosibirsk: https://mm.icann.org/pipermail/tz/2016-June/023820.html
- Paradigm, "Project Kryptos": https://www.paradigm.xyz/writing/kryptos
- Paradigm, CTF rules: https://paradigm.xyz/kryptos-ctf/rules
- TheBenMeadows PR #196: https://github.com/TheBenMeadows/tbm/pull/196
- ahardkore PR #14: https://github.com/ahardkore/Buttcrack---Cipher-Breaker/pull/14
- benjacasas02 README: https://github.com/benjacasas02/independent-cryptography-research/blob/main/research/paradigm-kryptos/README.md
- kryptos.today progress: https://kryptos.today/progress
- RR Auction: https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/
- en.wikipedia, "Kryptos": https://en.wikipedia.org/wiki/Kryptos
- Elonka Dunin, Antipodes: https://elonka.com/kryptos/sanborn/antipodes.html
- Bean 2021, HistoCrypt: https://ecp.ep.liu.se/index.php/histocrypt/article/view/153
- solvekryptos.com: https://solvekryptos.com/solution
