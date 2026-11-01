# R49 correction: World Clock primary-data work was ALREADY DONE in R23

**29 October 2026, user correction:** "We should already have gotten that with the old photos & chart we created." **Correct.** My original R49 plan erroneously presented a pre-1990 24-panel source map as entirely missing and proposed reaching out to the clock's original manufacturer before auditing previous work. **Do not request redundant data from the user or Kunsch Metallbau.** No outreach has been sent.

## Recovered actual project artifacts on `main`

- **Historical map (built 25 October 2026 from photos supplied by Tyler):** [`archive/2026-10-26_chatgpt_starter/sources/world_clock_360.md`](../archive/2026-10-26_chatgpt_starter/sources/world_clock_360.md) (repository-relative link from this directory; authoritative URL: https://github.com/tylerj-spec/kryptos-k4/blob/main/archive/2026-10-26_chatgpt_starter/sources/world_clock_360.md).
- **Historical research and 1990 photograph transcriptions:** [`archive/2026-10-26_chatgpt_starter/sources/2026-10-22_world_clock_and_sources.md`](https://github.com/tylerj-spec/kryptos-k4/blob/main/archive/2026-10-26_chatgpt_starter/sources/2026-10-22_world_clock_and_sources.md).
- **Entire prior working chart in structured form:** [`r49/prior_photo_360_chart.json`](prior_photo_360_chart.json). This is a **verbatim extracted 24-face working composite**, including every original upper/lower cell, year tags, conflicting readings, original Markdown line, and exact Git blob SHA. **It is not a newly authenticated single-year 1988 chart.**
- **Original ledger:** `LEDGER.md` L37–L42 and L74–L79, and R23 round-specific source/key files in the historical handoff archive. These record prior real experiments, not proposals.
- `r49/world_clock_pre1991_inventory.json` remains an **all-null separate strict primary-verification registry**, not evidence that no reconstruction exists. It explicitly must not replace, obscure, or invalidate the R23 photo-derived working chart.

## What was already recovered from original photographs

- 24 sequential UTC offsets (−11 through +12) mapped to panels around the full drum, with upper and lower lists. The hour ring is **not fixed**: its numbers shift according to local time.
- Historical photographs **1969/70, 1972, 1980, 1984, 1989, 3 October 1990** and modern comparisons, with uncertainty per cell.
- Approximate geographic orientation: `UTC +1 / BERLIN` panel **177° (south)**; `UTC +8` panel **72°**, close to ENE (67.5°). This is a **±5–8° photographic estimate**, not an authenticated measured alignment.
- UTC +1 upper: **AMSTERDAM, BERLIN, BRÜSSEL, BUDAPEST, MADRID, PARIS, PRAG, STOCKHOLM, WARSCHAU** (1970/1980); 1970 lower: **KOPENHAGEN, LONDON, WIEN, ROM, BELGRAD, TUNIS**.
- UTC +8: upper **IRKUTSK, ULAN BATOR** (1972/1984), lower **PEKING, SHANGHAI, MANILA** (1972/1984/1990).
- The originally documented changes from earlier engravings to post-1997 names, including `LENINGRAD`→`ST. PETERSBURG`, `TOKIO`→`TOKYO`, time-zone movements and additions, were already recognized in R23. **Do not rediscover them and call them new evidence**.

## Prior clock-based experiments ALREADY completed

- **L37:** 1969/1980s clock texts as running keys, both directions, 7 alphabets, 3 operations, 3 rank mappings: **56,330,694 settings** in rerun; maximum 8/24 public anchors, no independent plaintext.
- **L38:** 24-face drum transpositions, 192 permutations, no convincing result.
- **L39:** city names keyed to faces and name-length/hour numeric keys, no signal within tested scope.
- **L40:** letter selection by clock-hour ring, including changing clock time, **2,112** cases, no signal.
- **L42:** photo-derived clock orientation and ENE face-specific keys, no signal.
- **L75:** 48-state compass/24-hour cycle hypothesis, excluded within tested family.
- **L76:** two-free alphabet 48-state variants, **484** published-crib-compatible assignments but no signal vs 64 shuffled nulls (`p≈0.569`); none is a verified plaintext.
- **L77:** 1969–72 and 1980s city-name face strings with ENE/BERLIN starts, bidirectional word-letter keys, **2,880** settings, **0** passes among **2,080** adequately covered.
- **L78:** six letters per face in the 42-letter known clue gap, **25,760** settings, **0** passes within the covered family.
- **L79:** 97=4×24+1 candidate drum pathways, **13,056** sufficiently sourced settings, no signal.

**Scientific scope:** these failures rule out the *specified key extraction recipes*, not the clock's possible role as a message subject or a different physical mechanism.

## Only remaining genuinely missing evidence (narrow and optional)

The R23 chart clearly identifies **specific gaps**, not an absent map:
1. **Exact late-1980s** lettering for some western/Pacific/Americas panels (`−12 .. −4` represented primarily by 1969–70 photos), not proof the R23 readings are wrong.
2. Some **lower inscriptions** and apparent changes to **+10** between 1972/1984/1989 remain ambiguous.
3. Orientation estimated photographically within ±5–8 degrees; a precisely measured 1988 alignment is not documented.

**No outreach needed now.** Only contact an archive or original builder if a *new preregistered cipher construction* demonstrably depends on one of these particular missing cells/orientations and cannot handle the known uncertainty. Prefer reading the existing files first and trying assumptions or sensitivity tests that require no new external data.

## Revised next experiment priority

Stop repeated city-list extraction and redundant clock-key sweeps. Revisit the already recovered R23 chart **only** if a novel, externally motivated encryption architecture calls for it. The high-value cryptanalytic gate is **unknown-key full plaintext recovery on fresh 97-letter controls**, with the key not supplied (unlike R44b), plus exact independent forward-reencryption. The clock could be purely a **narrative reference**; preserve that alternative.

No new K4 plaintext produced. No external checker or maker contacted. `main` is unchanged.
