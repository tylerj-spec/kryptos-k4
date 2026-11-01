# R49 — K4 strategy reset: historical-source acquisition and unknown-key blind gate

> **CORRECTION — PRIOR WORK RECOVERED (29 Oct 2026).** This strategy originally framed the original World Clock chart as missing. That was incorrect. Tyler and Claude already created a 24-face historical photo-derived 360° map on 25 October, at `archive/2026-10-26_chatgpt_starter/sources/world_clock_360.md`, with 1969–1990 upper/lower lettering, source dates, uncertain rows, ENE orientation and prior K4 tests. It is now preserved verbatim in `r49/prior_photo_360_chart.json`; see `r49/PRIOR_WORK_CORRECTION.md`. The all-null `world_clock_pre1991_inventory.json` is **only a stricter primary-verification checklist**, not a claim that our working reconstruction is absent. **No manufacturer contact is needed now.** Historical-drawing outreach is deferred unless a specific missing inscription or surveyed alignment can change a fresh, independently motivated cipher hypothesis. Avoid all redundant city-text/clock-key experiments (ledger L37–L42, L75–L79).

**29 October 2026. Status: EVIDENCE ACQUISITION, not a new K4 decryption.** This is a self-contained branch based on `main` to avoid importing the failed R43 beam or stacked PRs #11–#17 before review. Live tracking: [Issue #18](https://github.com/tylerj-spec/kryptos-k4/issues/18).

## Decision: why past search methods are no longer the critical path

The record proves some exact exclusions of finite cipher families, but **no independently recovered new K4 plaintext letters**. Claude's R44b model recovered 20/20 fresh 97-letter messages when the true keystream was **given**; K4's keystream is unknown. Under the tested direct, running-key and K3-transposed families (R45–R48), original K4's 24 published letters made all keyword/free combinations impossible, so spending hours on those specific variants has no value.

The scientific obstacle is *identifying the method and key source*, not scoring another billion random settings. New proposals must answer: **what independently observable object would have supplied the key in 1988–1990?** What is the precise reversible algorithm? Can we **recover the key blindly** on fresh encrypted 97-letter controls when the key is *not supplied*?

### Primary-source correction that changes a large part of the old Berlin-clock search

Sanborn's 2025 statement identifies the `BERLINCLOCK` word with **Erich John's Weltzeituhr (World Clock), Alexanderplatz**, rather than the lamp-based Mengenlehreuhr. This comes from creator remarks, not an inference from a guessed plaintext:
- November 2025 report of official 2025 clue announcement, Scientific American: https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/

Berlin's official site confirms the World Clock has **24 sided segments**, a **rotating hour ring**, and a **compass-rose ground mosaic**; after reunification names were added and original time-zone errors were corrected:
- https://www.berlin.de/en/attractions-and-sights/3561749-3104052-world-clock.en.html

Original designer-family account: **80 city names in 1969, 146 today**, across the same 24 segments:
- https://www.weltzeituhr-berlin.de/en/urania-worldtimeclock

A contemporary December **1997** newspaper explicitly says **20 names were newly added**, including previously omitted Oslo, Jerusalem and Cape Town; other names/time zones updated:
- https://www.berliner-zeitung.de/article/20-staedtenamen-wurden-bei-der-restaurierung-ergaenzt-frisch-poliert-die-weltzeituhr-dreht-sich-bald-7079
- https://taz.de/!1367509/

**This creates a fatal reproducibility issue:** modern Berlin Clock city lists cannot be treated as the 1988 candidate key without proving historic equivalence. The 24 faces are stable geometry; *the text engraved on them is not*. Nor is 1969 necessarily identical to 1986/1988: historical photographs suggest modifications before the main 1997 restoration, so record the edition date and confidence for each panel.

### New source discovery (not yet obtained)

B.Z.'s 23 Nov **2024** interview identifies **Stefan Kunsch** at the original metalwork business as custodian of original fabrication drawings and original letter samples. His father built the clock's outer housing in 1969; Stefan said they still have all needed construction documents. **This is our best identified first-party source of the physical panel inventory**, far stronger than modern photo guesses.
- Article: https://www.bz-berlin.de/berlin/mitte/weltzeituhr-reparatur
- Maker's project record: https://kunsch-metallbau.de/referenzen-/weltzeituhr-berlin-alexanderplatz/
- Official business contact: https://kunsch-metallbau.de/kontakt/ (`info@kunsch-metallbau.de`, +49 30 5578167). NO contact has been sent or authorized yet.

Other independently dated physical snapshots:
- Federal archive World Clock, **15 July 1980**, `Bild 183-W0715-026`: https://www.bild.bundesarchiv.de/dba/en/search/?query=Bild+183-W0715-0026
- Federal archive, **3 Oct 1969**, `Bild 183-E1003-0001-001`: https://www.bild.bundesarchiv.de/dba/en/search/?query=Bild+183-E1003-0001-001
- Haus der Geschichte's **1972** physical 360° model, accession `1995/09/0108`: https://www.hdg.de/lemo/bestand/360grad/360gradobjekt-weltzeituhr-modell.html
- (Different modern commercial models must not silently supply 1969 text.)

## Specific evidence we must acquire and freeze, not invent

1. Exact **upper and lower** engraved city/region names from the **24 panels** before 1990; preserve historical spellings `LENINGRAD` etc., not modern replacements.
2. Which inscription belongs to each of 24 consecutive fixed time zones; direction of rotation/readout; where the date-line panel falls; orientation relative to Berlin's compass-rose mosaic.
3. Dated source images/build drawings, independent verification on visible segments, link and checksum of each original image. Record unknowns as `null` rather than guessed letters.
4. If supplied by Kunsch or a museum, permission to use/quote/redistribute the source. A research-only transcription may be stored with provenance; copyrighted photographs are not automatically redistributable.

Use `r49/world_clock_pre1991_inventory.json` for a strictly **incomplete, explicitly blank** 24-panel data contract. `r49/validate_inventory.py` must reject its promotion to a complete ciphertext key until actual primary records have been supplied.

## Hypothesis discipline and decision criteria

Two separate, explicitly conditional tracks:

**A — Historical physical clock key hypothesis (MEDIUM PRIOR, UNTESTED).** The clock could be only *subject matter* of the plaintext; its 24 physical zones don't automatically imply a 97-position key. Once the period-correct panel map is acquired, predeclare at most two low-parameter reversible procedures that use actual city inscriptions / clock progression / compass orientation and are fixed **without looking at K4's known words**. Distinguish mechanical transposition, keystream extraction, and English narrative interpretation. If missing primary data remains, STOP as `BLOCKED_BY_SOURCE`.

**B — Unknown-key solver gate (HIGH VALUE even if clock hypothesis fails).** For any new cipher model, establish full blind key+plaintext recovery on 20 genuinely new planted 97-letter English messages with the correct keystream **not supplied**. At least 16/20 exact complete messages; all returned witnesses re-encrypt exactly. Lock parameters and controls before the target. First ciphertext-only K4 raw output must be committed with 97 letters **before** checking the 24 artist-confirmed words. The old 20/20 **known-key** R44b benchmark is not sufficient for this key-discovery gate. Shuffled nulls and control matching are mandatory.

**This round produces no K4 plaintext by design.** No automated external checker calls or payments; no owner action to merge an experimental solver. The goal is to acquire new independent information instead of multiplying computationally cheap but historically unmotivated exclusions.

## Human outreach — precise request (do not auto-send)

To the original builder's firm: ask for the original **1969 panel drawings showing the exact engraved names on both 24-segment rings**, and whether any panel inscriptions or date-line orientations changed during **1969–1989**. Ask for a photograph or permitted transcription of the plans, and identify year/date, panel numbering, and permissions. If their drawings predate a 1980s update, request updates or referral to the Berlin heritage archive.

**Owner task if approved:** send a short email to Kunsch Metallbau, or authorize an outreach draft; see Issue #18. No Git commit is necessary from the owner.
## Chronology uncertainty (added before use of any R49 historical data)

Sanborn's 2025 remarks connect a 1986 trip, writing around 1988, and the **1989** fall of the Berlin Wall, despite the chronology. The invention date of any potential K4 physical key is **not known**, and may fall as late as the 1990 installation. The source inventory therefore accepts physical evidence depicting **1969–1990**, with date/era shown per panel; no hard-coded 1988 condition is allowed. A 1969 build drawing alone does not prove its text was unchanged in 1989. See the amended `world_clock_pre1991_inventory.json` and validation tests.
