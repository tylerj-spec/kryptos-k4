# Claude Code handoff — audited R44b holdout and R45–R48 K4 family exclusions

**Date:** 29 October 2026. **Status:** No K4 solution or 97-letter independently decoded plaintext. No external checker queries. `main` remains unchanged. All K4 public letters were used only for separate **postfreeze exact exclusions**; there was **no clue-conditioned blind plaintext generator** in R45–R48.

## Validated known-key breakthrough

Claude R44b [PR #12](https://github.com/tylerj-spec/kryptos-k4/pull/12): independent comparison of frozen holdout B original inputs, sealed truths, plaintext outputs and original encryption gives **20/20 exact 97-character texts with 20/20 full bijective forward witnesses**. Before polish 16/20. Protocol preregister `7f86578`, new holdout generated `f192c7b`, outputs frozen `433572b`, truths evaluated after. Scope requires the **correct keystream given** and **one** alphabet from a finite set of 4,749 common-word keyword alphabets, with the other alphabet free. This is an impressive solver result, but it does NOT identify a K4 key.

## Exact historical K4 exclusions, all using original ciphertext and 24 published anchor positions only after registration

| PR | Precisely tested model | Full test results | Controls | Classification |
|---|---|---|---|---|
| [#13 R45](https://github.com/tylerj-spec/kryptos-k4/pull/13) | In-place, every 5-decimal-digit Gromark primer, +/-, 4,749 keyword alph on either side | 39/100,000 primers feasible with both arbitrary alphabets; **0** compatible with keyword/free arrangement | 40/40 | **EXCL exact finite model** |
| [#14 R46](https://github.com/tylerj-spec/kryptos-k4/pull/14) | S_then_T, four predeclared K3-like 24×8 double quarter-turn routes, all 100,000 Gromark primers/route, +/-, both keyword orientations | K4 two-free feasible by CW fwd/inv, CCW fwd/inv = **79, 1,643, 1,486, 9,502**, but **0** keyword-compatible across all | 20/20; 2 nulls | **EXCL exact finite model** |
| [#15 R47](https://github.com/tylerj-spec/kryptos-k4/pull/15) | In-place, every 97-letter window of K1–K3 plaintext and Carter & Mace 1923 text, forward/reverse × AZ/KRY numbering, ±, both keyword orientations | **1,135,348** key windows; **585** two-free feasible; **0** keyword-compatible | 20/20; 2 nulls | **EXCL exact finite model** |
| [#16 R48](https://github.com/tylerj-spec/kryptos-k4/pull/16) | **Speculative third-party reverse-tableau 97-letter packet**, 26 possibilities for one blank × AZ/KRY numbering, ±, both keyword orientations, in place | **0/52** even with two arbitrary alphabets; 0 keyword matches | 20/20; 4 nulls | **EXCL literal packet/model ONLY** |

**Source caution R48:** Public [CIA transcript of Kryptos](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/) independently corroborates the exact Y/Z tableau row lettering and intentionally flipped tableau, but **NOT** the third-party author's proposed physical 97-position alignment or extra leading-blank footer. The third-party page also publishes a **plaintext-fitted** mechanism. None of those fitted plaintext/gate/shift cards entered our research. Revalidate any future physical packet from PRIMARY photographs/transcript.

## R46 reproducibility — two independent full reports, exactly identical shared fields

- Original R46 [Actions 40928087044](https://github.com/tylerj-spec/kryptos-k4/actions/runs/40928087044) completed successfully, raw artifact ID **12921939261**, uncompressed `R46_EXACT_RESULT.json` SHA256 `352e4547b527531be5bec3ad0eceb0e49f055d5b06f5dca98e797bc1b0f248be`.
- Independently optimized [R46A PR #17](https://github.com/tylerj-spec/kryptos-k4/pull/17), [Actions 40931330834](https://github.com/tylerj-spec/kryptos-k4/actions/runs/40931330834), raw artifact ID **12922327694**, uncompressed `R46A_RESULT.json` SHA256 `fde17a2eaea03985703b0b270d91a6e01c380a3f5669f5afbe1b7a5052e46692`.
- Local independent Python compared **every shared field** in all four original K4 route reports and all eight null-route reports: complete *two-free feasible primer lists*, all *keyword feasible settings*, every rotated ciphertext SHA256, counts, seeds, and control data — **perfectly identical**. Indexed code also brute-forced the full 4,749 dictionary for 3 sample surviving keys per route per ciphertext and 2 signs/2 orientations (direct exact checks), all pass. Independent C++ key-oracle reproduced original K4 four-route free-key counts. [Permanent R46 verification summary](https://github.com/tylerj-spec/kryptos-k4/blob/chatgpt/r46-k3-rotation-keyword-feasibility/r46/VERIFIED_RESULT.md).

## What to do now (targeted review)

1. Independently audit the *exclusion scopes*, especially route direction/order and whether the publicly confirmed 24 letters are at the original 1-based 22–34, 64–74 before or after each declared S_then_T route. Confirm source stream editions/digests and 4,749-word vocabulary construction; do NOT overgeneralize an exclusion to an untested model.
2. Do **not** spend more resources on the pre-excluded direct Gromark top 1,000 keys or the already-excluded four rotation variants. **Change the cipher architecture:** new/non-Gromark key streams, genuinely independent source-derived physical mechanism, or independent permutation/order, with pre-registered blind plants and nulls.
3. A real K4 candidate must be generated by the **original ciphertext-only solver** without using the 24 public plaintext letters, then raw full 97-letter text frozen/committed, and only afterward compare the artist-confirmed clues; independent forward re-encryption and independent validation of novel unseen text required. No external verifier without owner's explicit go-ahead.
4. **GitHub integration caution:** [PR #11](https://github.com/tylerj-spec/kryptos-k4/pull/11) contains an **unsuccessful** prior R43 beam solver. [PR #12](https://github.com/tylerj-spec/kryptos-k4/pull/12), the successful R44b replacement, is stacked on that branch, and PRs #13–#17 stack subsequently. Before any merges to `main`, review and propose a clean branch/merge plan so the failed prototype is not mistaken for validated K4 software.
5. If a true physical alignment mechanism is to be investigated, prefer authoritative **high-resolution front and back photographs of the corresponding lower panel cells**; official CIA text supplies a basic row transcription but does not certify alignment. Provide a reproducible coordinate-to-character map before calling it a key.

**Outcome sought from Claude:** an independent code/science review and a NEW, explicitly bounded, preregistered model that restores complete blind planted plaintext before any K4 experiment; not another K4 plaintext reconstruction fitted to EASTNORTHEAST or BERLINCLOCK.

No claims of solved K4. No action needed from Tyler to preserve current research; raw GitHub Actions artifacts are also available as downloadable archives for review, with SHA256 recorded permanently.
