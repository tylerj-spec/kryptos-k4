# Source map for the 57 weakly sourced ledger rows (T5, audit/NEXT_STEPS.md), 15 Nov 2026

Documentation only. **No status was changed.** The rows are the ones `audit/historical/scan.py` classes as
GENERIC_SOURCE (51: the source column is only a tag such as C/G) or UNRESOLVED_PATH (6).

How the files were looked for (`audit/historical/source_map.py`, raw output `SOURCE_MAP.json`):
- every file name the row mentions was searched by basename among tracked files and inside
  `R32_handoff_original.zip`;
- `k4kit/tools/`, `k4kit/results/`, `k4kit/protocols/` and `archive/` were checked by hand for the legacy rows.

"Scope" is the row's own method column. Parameter bounds are as stated there; nothing was re-derived except where
a note says so.

**Summary:**
- 47 rows: NOT FOUND, no script or result file in the repository.
- 4 rows (L01–L04): the original script is NOT FOUND, but the claim has since been re-derived independently.
- 6 rows (L12, L25, L37, L71, L98, L107): some related file found. Only L98 (the R28 outputs it audited) and L107 (its run outputs) have their own result files; no row has its own script.

| Row | Recorded status | Tag | Script / result file | Scope (from the row) |
|---|---|---|---|---|
| L01 | EXCL | C/G | Re-derived independently: `audit/historical/postfreeze_baselines.py` (L01–L04). | Any pure permutation of the 97 letters |
| L02 | EXCL | C/G | Re-derived independently: `audit/historical/postfreeze_baselines.py`. | In-place fixed monoalphabetic (incl. Atbash, affine) |
| L03 | EXCL m 1–26, 30–52; OPEN 27–29, 53–97 (no checks) | C/G | Re-derived independently: `audit/historical/postfreeze_baselines.py`. | In place, periodic, 8 variants |
| L04 | EXCL additive 1–25, Beaufort 1–26; additive m 26 SCORE | G/C | Re-derived independently: `audit/historical/postfreeze_baselines.py`. | In place, periodic, 16 pairs, additive / Beaufort |
| L05 | EXCL where ≥ 3 checks; WEAK 26–29, 52 | C/G | NOT FOUND | Multiplied periodic c = a·p + k |
| L06 | EXCL | C/G | NOT FOUND | Complete columnar, w 2–10 (all orders) + periodic 1–14, 8 variants |
| L07 | EXCL m 1–21 (8 variants and 16 pairs, both operations); WEAK… | C/G | NOT FOUND | Circular routes (9,312) + periodic |
| L08 | EXCL 8 variants 1–23, 25; 16 pairs additive 1–23, Beaufort 1… | G/C | NOT FOUND | Padded double grids (242) + periodic |
| L09 | 16 pairs EXCL additive 1–22, Beaufort 1–21; compatible fits … | C/G | NOT FOUND | Fold (946) and back (6) maps + periodic |
| L10 | SCORE | C/G | NOT FOUND | All 22,955 compatible fixed-alphabet configurations in L07–L09 |
| L11 | EXCL | G/C | NOT FOUND | Direct Hill 2×2–5×5, all alignments, AZ or KRYPTOS |
| L12 | EXCL | G/C | RELATED, not the original: `k4kit/tools/trifid_any.py` (R26, arbitrary 27-symbol cube, periods 1–97) with `k4kit/results/trifid_any.log`; covers a superset of L12's 4 arrays. | Trifid: 4 arrays, periods 1–97, 6 orders |
| L13 | EXCL m 1–25; m 26 SCORE (24 settings) | C/G | NOT FOUND | Progressive key (v4 spec) |
| L14 | EXCL | G/C | NOT FOUND | Gromark / any decimal stream, any cipher alphabet, plain AZ or KRYPTOS |
| L15 | EXCL | G/C | NOT FOUND | Base-26 lagged-Fibonacci, L 2–8, both taps, any cipher alphabet |
| L16 | EXCL | C | NOT FOUND | Free-alphabet keystreams: K1–K3 running keys (both directions, both ranks), K2 coordinates, 9 dates, affine progressive |
| L17 | EXCL lags 1–67; WEAK 68–72; OPEN 73–96 | C/G | NOT FOUND | Ciphertext autokey, free alphabet, free seed |
| L18 | WEAK | G/C | NOT FOUND | Fixed-alphabet autokey (full recurrence) |
| L19 | EXCL (no full match) | C/G | NOT FOUND | K1–K3 running key, fixed alphabets; physical overlays; self-fold |
| L20 | EXCL | C/G | NOT FOUND | Tableau stepping (homogeneous arithmetic only) |
| L21 | EXCL m 1–7, 9, 10, 14, 15, 17, 21, 25, 34, 42, 43, 45, 50; S… | C/G | NOT FOUND | Per-slot arbitrary bijections, in place |
| L23 | recovery test failed (decoys outscore truth 2,560/2,560) | G/C | NOT FOUND | Period-8 recovery with quadgram objective |
| L25 | OPEN: partial 1969–72 and mixed-date 1980s face lists recove… | C (research) | Research note only: `archive/2026-10-26_chatgpt_starter/sources/2026-10-22_world_clock_and_sources.md` (the cited `docs/research/` path moved here). `2026-10-25_research_round3.md`, `photo_sources.md` NOT FOUND. | World Clock-derived keys |
| L28 | Not adopted: no gain over v2 on K4-structured development (1… | C | NOT FOUND | Offset-aware solver v3 (every anchor-offset configuration, free-letter annealing) |
| L29 | SCORE diagnostic only, not recovery or a family exclusion; o… | G | NOT FOUND | Frozen word-score sensitivity to nonstandard spelling |
| L30 | Advisory only; no semantic or cryptographic validation | G | NOT FOUND | Local character-transition gibberish diagnostic (not the linked website) |
| L31 | STAT for supplied conventional-English reference only; not E… | C/G | NOT FOUND | Unknown English running key, direct alignment; 16 alphabet pairs x 3 operations x 4 key alphabets |
| L32 | STAT within stated surrogate populations, not cipher identif… | C/G | NOT FOUND | Eight ciphertext features under 13 supplied simulation families and four R9 boundary populations |
| L34 | TOOL: necessary tests only under explicitly shared key, alph… | C/G | NOT FOUND | Conditional K5 shared-keystream diagnostic kit |
| L35 | Periodic substitution (16 pairs, both operations) still EXCL… | C | `one_error.py` NOT FOUND. Hill one-error claim flagged in `r81a/audit/DROP_ONE_REVIEW.md`. | Robustness of exact exclusions to carving errors (K2 precedent) |
| L36 | EXCL for every setting with ≥ 3 checks (mod 13), also with a… | C | NOT FOUND | "Multi-clock" key in place: key = sum of 2–4 periodic keys (= stacked chained-alphabet Vigenère/Beaufort/Quagmire stages, as in Paradigm PK3/PK8); 16 … |
| L37 | 1969 and 1980s face text reconstructed from photos; uncertai… | C | Source text description only: `archive/2026-10-26_chatgpt_starter/sources/world_clock_360.md`; no script. | World Clock text as running key |
| L38 | EXCL periods 1–24 for every setting (49 pairs, both operatio… | C | NOT FOUND | 24-face drum transposition (write in rows of 24, read by faces: 24 starts × 2 directions × up/down × 2 roles) + periodic substitution |
| L39 | EXCL within scope: (a) best 6/24 (random 5–8); (b) best 7/24… | C | NOT FOUND | Clock as lookup table. (a) Each face has its own keyed alphabet built from its text (full/upper/first city), letters assigned to faces 1 or 4 at a tim… |
| L40 | EXCL as direct keys: best 8/19 and 9/23 (random-key maximum … | C | NOT FOUND | Tyler's hour-index keys: each face's hour number selects a letter from its text, giving 24 letters (top, bottom or both; joined or with spaces; wrap o… |
| L41 | EXCL: 0 settings with ≥ 3 checks (random 0–2); only 1-check … | C | NOT FOUND | Clock-keyword columnar transposition (BERLINCLOCK, WELTZEITUHR, EASTNORTHEAST, ALEXANDERPLATZ and 6 compounds; widths 11–25) + periodic substitution m… |
| L42 | Faces: Berlin/+1 about 177 deg (south), UTC 0 SSW, −5 west, … | C | NOT FOUND (mentions `orientation.py`; none in the repository) | Clock orientation (orientation.py; 1972 photo L0328-0018, tower and clock coordinates, cross-checked with the 2015 photo) and the face pointing east-n… |
| L43 | No word stands out. Running-key English test: max z 3.76, 10… | C | NOT FOUND (mentions `crib_words.py`; none in the repository) | Guessed plaintext words (Tyler's spy/Moscow theme; 82 words incl. MOSCOW, MOSKAU, KGB, KREMLIN, LENIN, STASI, AGENT, DEADDROP, MESSAGE, DELIVER, WALL,… |
| L44 | No word stands out: no flags. T3 max z 3.54 (POTSDAMER at 35… | C | NOT FOUND (mentions `wsw_geometry.py`, `crib_words.py`, `wsw_words.txt`; none in the repository) | Tyler: the clock is ENE *of* the point K4 is about, so that point is WSW of the clock (wsw_geometry.py). The 247.5 deg ray from the clock passes withi… |
| L45 | No signal. The pre-specified flag fired (real max z 5.60 bea… | C | NOT FOUND (mentions `misspell_cribs.py`, `misspell_followup.py`; none in the repository) | Tyler: the guessed words misspelled or spelled by sound (misspell_cribs.py, misspell_followup.py). 149 words from L43, L44 and L44b give 8,403 variant… |
| L46 | (a) Nothing beyond chance. Only shared 4-gram: PRNG (in K1–K… | C | NOT FOUND (mentions `whole_text.py`, `results/r12_whole_text.log`; none in the repository) | Tyler: K4 together with K1–K3 (whole_text.py). (a) K4 letter sequences that recur in the K1–K3 ciphertext, the tableau side or the K1–K3 plaintext, ag… |
| L47 | Substitute, then rearrange: counts match chance at every lev… | C | NOT FOUND (mentions `two_step.py`, `two_step_followup.py`; none in the repository) | Two-step search (two_step.py; Tyler chose it): 41,502 distinct rearrangements (K3's own double quarter-turn at every grid size 2–48, verified on K3; a… |
| L48 | No candidate. Substitute-first: 1.70 billion settings; count… | C | NOT FOUND (mentions `engine.py`, `engine_check.py`; none in the repository) | General engine (engine.py, engine_check.py; Tyler: "let's solve Kryptos", with his suspected-word idea). 46,621 rearrangements (L47's plus rail fence … |
| L49 | EXCL: 0 settings fit (random ciphertexts: 0/500, so any hit … | C | NOT FOUND (mentions `lin_recur.py`; none in the repository) | Legacy keystream generator, in place (lin_recur.py; Tyler: identify the algorithm): key = any affine linear recurrence k_n = c1·k_{n−1} + … + cL·k_{n−… |
| L50 | EXCL within scope: K4 best 9/24 anchors; 30 random ciphertex… | C | NOT FOUND (mentions `tableau_paths.py`; none in the repository) | Tableau-path masks, in place (tableau_paths.py): the key read off the physical KRYPTOS tableau (28×32 as carved, with header rows, label column and th… |
| L51 | No signal. K4 outputs look like the SAME solver run with wro… | C | NOT FOUND (mentions `gromark_rescore.py`, `gromark_rescore2.py`; none in the repository) | Misspelling-tolerant re-score of saved candidates (gromark_rescore.py, gromark_rescore2.py; untrusted inputs read with -I): ChatGPT R7's 9,984 K4 Grom… |
| L52 | Identifiability first: at lags ≥ about 25 the model has too … | C | NOT FOUND (mentions `ac_anneal.c/ac_anneal3.c`, `autoclave_search.py`, `autoclave_focus.py`, `autoclave_short.py`; none in the repository) | English search inside the 257 feasible plaintext-autoclave settings (L27), misspelling-tolerant scoring on top (ac_anneal.c/ac_anneal3.c + autoclave_s… |
| L53 | OPEN, highly underconstrained in the stated model (not an un… | C | NOT FOUND | Decidability of per-slot arbitrary alphabets at the open periods (L21: m 8, 11, 12, 13, 16, 18, 19, 20, 22, 23, 24) |
| L56 | No statistically supported excess under the pre-registered p… | C | NOT FOUND (mentions `protocols/L56_PREREGISTRATION.md`, `l56_null.py`; none in the repository) | Pre-registered follow-up of L47/L54 (protocols/L56_PREREGISTRATION.md, sha256 06db7875…5d1c91, written before computing; l56_null.py, independent of C… |
| L61 | EXCL within scope. Hill-then-rearrange: 1,162,084 settings, … | C | NOT FOUND (mentions `protocols/L61_PREREGISTRATION.md`, `hill_layer.py`; none in the repository) | Pre-registered masking rule (protocols/L61_PREREGISTRATION.md, sha256 fa3f9a2d…6e3118; hill_layer.py): Hill cipher ("matrix codes Ed gave me"; the tab… |
| L62 | No signal. L48 forced letters (5,654 unbiased decryptions): … | C | NOT FOUND (mentions `foreign_scan.py`, `data/foreign_words.txt`; none in the repository) | Other-language word scan (Tyler; foreign_scan.py, data/foreign_words.txt): common 5+ letter words of German, Dutch, French, Spanish, Italian, Latin an… |
| L63 | No flag in any language. A: K4 max z inside the null range i… | C | NOT FOUND (mentions `protocols/L63_PREREGISTRATION.md`, `data/corpus_*.txt`, `langmodels.py`, `lang_tests.py`, `lang_autoclave.py`, `results/r17_lang_*.log`, `r17_lag22_*.log`; none in the repository) | Other plaintext languages (Tyler: Dutch, West Frisian, Low German, Swedish; German added), pre-registered (protocols/L63_PREREGISTRATION.md, sha256 18… |
| L70 | R20 REPRODUCED (16/16 fixtures, 512/512 witnesses, 256/256 r… | C R21 | NOT FOUND (mentions `claude/r20/audit_r20.py`, `primer_blind.py`, `PRIMER_BLIND_PROTOCOL.md`; none in the repository) | Claude audit of R20 plus a primer-blind discrimination test (claude/r20/audit_r20.py, primer_blind.py, PRIMER_BLIND_PROTOCOL.md sha256 2dd955cf…16ca25… |
| L71 | S2 blind readable: arm 0 14/20, arm K 10/14, arm U 7/20 (exa… | C R21 | Protocol found: `k4kit/protocols/S2_PREREGISTRATION.md` (cited as `claude/r20/…`); solver `k4kit/tools/solver_s2kp.cpp` per its header; fixture `k4kit/fixtures/s2_k4_primer88254_rows.jsonl`. | S2 pre-registered (claude/r20/S2_PREREGISTRATION.md + amendment): your solver's model and moves, orth dictionary, quadgram term λ 0.05→0, 64 restarts … |
| L85 | R24 REPRODUCED. `REPORT.json` and `ORTH_PROBE.json` identica… | C R25 | NOT FOUND (mentions `claude/r24/g4_checks.py`, `REPORT.json`, `ORTH_PROBE.json`, `verify_packet.py`; none in the repository) | Claude audit of R24 (scripts replayed in a copy with `python3 -I`; own Gromark and forced-mask code, `claude/r24/g4_checks.py`) |
| L98 | R28 REPRODUCED. `R28_MORSE_TEST.json` and `R28_MORSE_PULSES.… | C R29 | Results found: `archive/2026-10-26_chatgpt_starter/r28_results/R28_MORSE_TEST.json`, `R28_MORSE_PULSES.json` (ChatGPT R28 outputs); Claude's `independent_morse.py` NOT FOUND. | Claude audit of R28 (replay on a copy with `python3 -I`; independent driver `claude/r29/independent_morse.py`: own stream assembly, own K3-route compo… |
| L107 | 39 Gromark primers, ORTH, 64 restarts: best −140.88 (L72 −14… | CC R30 | Results found: `k4kit/r30/runs/` (`R30_SUMMARIES.json`, `c1.json`, …). | R30 reference re-runs with new seeds and audits |

**What this means.** Most legacy exclusions (L01–L63) come from early ChatGPT and Claude sessions whose
scripts were never committed. They cannot be replayed from this repository. They stay as recorded, not
verified. An independent re-derivation is the only way to verify one, as was done for L01–L04 and L167.

Independent review: NONE (one model).
