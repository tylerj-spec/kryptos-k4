# Kryptos K4 source register (research cutoff: 2026-11-03)

**Research-only.** This file is an annotated bibliography, not candidate-generation input. Source links are leads/evidence, not permission to import published K4 plaintext clues into a solver. No copyrighted source text, photograph, source corpus, or confidential archival material is copied into this branch.

## Evidence grades

- **P1**: originating institution, author, owner, original interview, contemporaneous document, or directly recorded statement. The speaker may still be mistaken or selective.
- **P2**: specialist/expert summary or a contemporaneous report based on direct interviews and/or primary records.
- **P3**: community analysis, historical secondary source, unverified reconstruction, or working hypothesis. Requires independent replication.
- **I**: local repository measurement with frozen artifacts and explicit bounds. It is not external historical corroboration.

"Verified" means the cited page was located and inspected during this research session, not that its every claim was independently authenticated.

## Original construction, the sculpture, and K1–K3

| ID | Class | Source | What it establishes / caution |
|---|---|---|---|
| S01 | P1 | [CIA: Kryptos sculpture and commission](https://www.cia.gov/legacy/headquarters/kryptos-sculpture) | 1988 selection, Nov. 3, 1990 dedication, multiple installation components: courtyard copper screen, tableau, entrance Morse, lodestone, compass rose, water and stone. CIA text transcriptions have documented errors; do not use this page as the canonical byte source for K4. |
| S02 | P1 | [CIA Museum artifact](https://www.cia.gov/legacy/museum/artifact/kryptos/) | Institutional description of artwork, material and intended encryption. |
| S03 | P2 / direct participant record | [Elonka Dunin: corrected K2, Apr. 19, 2006](https://elonka.com/kryptos/CorrectedK2Announcement.html) | A missing ciphertext character shifted the keystream alignment; Sanborn confirmed the revised ending **LAYER TWO**, not the initially plausible **ID BY ROWS**. Critical counterexample to accepting plausible English as correctness. |
| S04 | P2 | [Elonka Dunin: Kryptos chronology](https://elonka.com/kryptos/KryptosTimeline.html) | Timeline, initial solvers, transcript correction and clues. Curated community record; verify against dated material. |
| S05 | P2 | [Elonka Dunin: FAQ](https://elonka.com/kryptos/faq.html) | Notes that some common CIA/site transcripts and a tableau transcription are inaccurate; seek image-grounded or consensus canonical bytes. |

## Creator and cryptographer: intent, masking, and public clues

| ID | Class | Source | What it establishes / caution |
|---|---|---|---|
| S06 | P1 interview | [WIRED interview with Ed Scheidt, Jan. 21, 2005](https://www.wired.com/2005/01/inside-info-on-kryptos-codes/) | Scheidt describes four processes, says all four sections use English, and specifically says K4 disguises English statistical structure. He says the masking technique *may* be unfamiliar. Do **not** translate this into a claim that the plaintext is in Dutch/German or a proof of any named cipher. |
| S07 | P1 interview | [WIRED: Sanborn and Scheidt, Jan. 21, 2005](https://www.wired.com/2005/01/solving-the-enigma-of-kryptos/) | Sanborn's personal modifications and source-vs-execution difference; public accounts of exactly who knew the answer varied. |
| S08 | P1 interview/record | [NPR June 9, 2005 transcript mirrored by Dunin](https://elonka.com/kryptos/mirrors/npr/2005transcript.html) | Scheidt says he masked English frequency clues. **Phonetic spelling examples in the journalist's narration are speculation, not a statement that Scheidt used them.** |
| S09 | P1 creator statement | [Sanborn open letter, Aug. 2025](https://www.elonka.com/kryptos/OpenLetterAug2025.html) | 97-character K4, stewardship, future verifier concept, K5 continuing riddle. The parenthetical "(CLUE)" is deliberately ambiguous: do not turn rhetoric into a derived key. |
| S10 | P1 event interview / P2 reporting | [Scientific American, Nov. 12, 2025: Sanborn's final clues](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/) | Author reported 1986 Egypt trip, fall of Berlin Wall, *Weltzeituhr*, message delivery, and K5 relationship to K2. Also reports Sanborn's emphasis on creative rather than necessarily mathematical insight; K5 is described as 97 characters and related to K4. **Article contains one apparent typo ("79 encrypted letters") despite repeated 97 references.** |
| S11 | P2 contemporaneous | [WIRED Nov. 21, 2010: BERLIN disclosed](https://www.wired.com/2010/11/clue-kryptos/) | Dates the first published K4 fragment. Exact validation-only positions are maintained separately. |
| S12 | P2/participant record | [Elonka's collected Kryptos clue chronology](https://elonka.com/kryptos/) | Dates CLOCK 2014, NORTHEAST 2020, EAST public approval Aug. 2020; original 2010 clue. Use only for sealed postfreeze validation. |
| S13 | P2 | [Scientific American, Oct. 22, 2025: Smithsonian discovery](https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/) | Archival text recovery was not discovery of encryption method. |
| S14 | P2 | [WIRED: accidental archive reveal, 2025](https://www.wired.com/story/kryptos-code-reveal/) | Kobek and Byrne photographed Sanborn papers; recovered a full confirmed text but not cipher algorithm. Sanborn distinguished archival discovery and cryptographic solving. |

## Post-2025 stewardship and checking

| ID | Class | Source | What it establishes / caution |
|---|---|---|---|
| S15 | P1 institution | [RR Auction catalogue, lot 2001](https://www.rrauction.com/auctions/details/730-decoding-history-kryptos-enigma-and-the-rosetta-stone/) | Nov. 20, 2025 archive sale at **$962,500 including buyer premium**, including claimed K4 method and source materials. Auction description is provenance, not independent validation of any cipher. |
| S16 | P1 owner | [Paradigm, June 12, 2026, Project Kryptos](https://paradigm-vc.vercel.app/2026/06/kryptos) | Paradigm publicly identified itself as steward, says Sanborn entered the plaintext on a fresh computer and only SHA-256/HMAC validation data was retained. It offers a **$1 paid submission** and later K5 release; the published explanation is the owner's claim, not an independent security audit. |
| S17 | P2 | [AP: archival discovery and sale, Nov. 2025](https://apnews.com/article/cb8ee8554ca473910cbd0592f8bdb350) | Confirms the plaintext-vs-method distinction and transfer of artist's archive. |

## Berlin World Clock: historical state and discrepancy

| ID | Class | Source | What it establishes / caution |
|---|---|---|---|
| S18 | P1 operator/specialist | [Weltzeituhr Berlin: Urania Worldtimeclock](https://www.weltzeituhr-berlin.de/en/urania-worldtimeclock) | Sept. 30, 1969 construction; **original 80 city names** claimed and **present 146**; 24 time zones, central rotating hour ring, rotating model of planets. |
| S19 | P1 municipal | [Berlin city visitor page](https://www.berlin.de/en/attractions-and-sights/3561749-3104052-world-clock.en.html) | Design by Erich John; 24 corners, names on aluminum panels, rotating hour ring and solar model. |
| S20 | P1 municipal | [Berlin Senate heritage register](https://denkmaldatenbank.berlin.de/daobj.php?obj_dok_nr=09020854) | Monument registration (no validated historic word-for-word inscription list). |
| S21 | P1 municipal/historical report | [City of Berlin historical article on Alexanderplatz (2019)](https://www.berlin.de/aktuell/ausgaben/2019/dezember/aktuell-104-webversion.pdf) | 80 cities were selected/approved before 1969; later names changed. Historical photos and records may be needed for original ordering. PDF link registered but not used as a machine-read plaque transcription. |
| S22 | P2 contemporaneous | [Berliner Zeitung, Dec. 12, 1997](https://www.berliner-zeitung.de/article/20-staedtenamen-wurden-bei-der-restaurierung-ergaenzt-frisch-poliert-die-weltzeituhr-dreht-sich-bald-7079) | 20 names added in 1997 renovation; earlier names/times changed. Strong evidence that today's plate text is not a 1989 key. |
| S23 | P2 interview | [B.Z. interview with Erich John, Mar. 4, 2019](https://www.bz-berlin.de/archiv-artikel/so-tickt-die-weltzeituhr-auf-dem-alexanderplatz) | Photo caption reports **original 97** and then 148 names, **conflicting with S18/S21's original 80 and current 146**. The conflict is unresolved; do not cherry-pick 97 because K4 happens to have 97 characters. |
| S24 | P1 museum | [Haus der Geschichte: 1968 clock model](https://www.hdg.de/lemo/bestand/360grad/360gradobjekt-weltzeituhr-modell.html) | Dated model from 1968 / 1972 commemorative gift. Potential visual corroboration, not proof of full original inscriptions. |

## German, Dutch, historic corpora and orthography

| ID | Class | Source | What it establishes / caution |
|---|---|---|---|
| S25 | P1 corpus publisher | [Europarl corpus by Philipp Koehn](https://statmt.org/europarl/index.html) | Parliamentary German/Dutch/English corpora cover **1996–2011**. Useful detector benchmarks but **not period-correct text for a cipher composed by 1989–1990**. |
| S26 | P1 linguistics institution | [IDS Mannheim: DeReKo archives](https://www2.ids-mannheim.de/cosmas2/projekt/referenz/archive.html) | German corpora and specifically **Wendekorpus** 1989–1990. Access may be restricted; no corpus downloaded or modeled here. |
| S27 | P1 linguistics institution | [IDS: Wende corpus collection metadata](https://repository.ids-mannheim.de/records/m10a2-a5718) | 1990 German reunification-era text as potential dated controls. |
| S28 | P1 Dutch language institute | [INT historical dictionaries](https://ivdnt.org/english/documenting-the-dutch-language/lexicography/historical-dictionaries/) | Dutch WNT to 1976, historical spelling variants and lexicon. |
| S29 | P1 Dutch language institute | [INT historic corpora listing](https://ivdnt.org/historisch-nederlands/) | Eindhoven 20th-century corpus and other dated Dutch sources; inspect license and genre before training. |
| S30 | P1 language standard | [German orthography council: reform overview](https://www.rechtschreibrat.com/service/handreichungen/) | 1996 and 2006 reforms. Reconstruct pre-1996 spellings when testing period text, not modernized text by default. |

## Cryptography and research-method references

| ID | Class | Source | What it establishes / caution |
|---|---|---|---|
| S31 | P1 original paper | [C. E. Shannon, *Communication Theory of Secrecy Systems*, 1949](https://doi.org/10.1002/j.1538-7305.1949.tb00928.x) | Theoretical baseline: perfect secrecy, information and unicity. Does not establish that K4 is OTP. |
| S32 | P2 mathematical | [Wolfram MathWorld: one-time pad](https://mathworld.wolfram.com/One-TimePad.html) | True OTP uses uniform independent one-time key as long as message; ciphertext-only testing cannot uniquely recover plaintext without key evidence. |
| S33 | P1 archival institution | [NSA William F. Friedman historical publications](https://www.nsa.gov/Helpful-Links/NSA-FOIA/Declassification-Transparency-Initiatives/Historical-Releases/Friedman-Documents/Publications/) | Primary historical descriptions of substitution, mixed alphabets, polyalphabetic, aperiodic and concealed writing mechanisms; do not assume every family was used in K4. |
| S34 | P3 unverified internet claim | [SolveKryptos: proposed mechanism](https://solvekryptos.com/method) | Its authors acknowledge portions of the decoding worksheet are **back-solved from proposed plaintext**, so reproducing its own fitted output does **not** independently derive K4. Never use it as a source of hidden plaintext or seed generator. |
| S35 | P3 independent analysis | [KryptosBot research status](https://github.com/jcolinpatrick/kryptos/blob/main/docs/REAL_K4_CURRENT_POSITION.md) | Another project's scoped negative results and evidence-gap warning; independent replication required before porting exclusions. |
| S36 | I | [This repo: canonical test catalogue](https://github.com/tylerj-spec/kryptos-k4/blob/main/docs/CIPHER_TYPES_TESTED.md) | Tests to R63 include bounded excludes and statistical nulls; see `LEDGER.md` for scope and freeze commits. |

## Known source conflicts / corrections requiring future work

1. **Clock city count:** S18/S21: 80 original; S23: 97 original. Modern reports range 146–148. Obtain dated before-1990 360-degree photos, 1969 blueprints, and original face-by-face inscriptions before choosing a historically exact word order.
2. **Transcription:** S01 includes known erroneous historic plaintext/cipher text; S03/S05 document corrections. Treat the repository's SHA-pinned 97-character `r39/ic_gate/k4_ciphertext.txt` as current computational authority and independently check sculpture photographs.
3. **Archive disclosure vs solve:** S13/S14 document full text found in 2025, while S06/S16 distinguish method derivation. No externally confirmed independent K4 method was established in this review.
4. **Phonetic masking:** S08 gives an example of *cryptanalyst speculation* in a journalist's narration. It is not testimony that Sanborn used pseudo-Dutch or pseudo-German English spelling.
5. **Source coverage:** Web availability and indexing are imperfect; this bibliography is broad but is **not** a claim that every interview, museum document, or physical source was recovered. Sources requiring full archival reproduction are marked as gaps.
