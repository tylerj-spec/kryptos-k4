# Historical facts and released clues — VALIDATION / HUMAN RESEARCH ONLY

**DATA-ISOLATION WARNING: DO NOT MOUNT, IMPORT, COPY, EMBED, PROMPT-WITH, INDEX-FOR-SEARCH-OPTIMIZATION, OR PASS THIS FILE TO ANY BLIND SOLVER, CANDIDATE GENERATOR, LANGUAGE MODEL USED IN THE SOLVE, OR KEY-SCORING PROGRAM.** It deliberately contains the *published plaintext*, which is permitted **only for independent checks after raw candidates and their algorithm/key have been frozen and pushed to remote Git**. This file is not an algorithm input.

This is a public-source register, not a copy of the unpublished 2025 archival answer. See [source register](SOURCES.md), especially S01–S17.

## 1. What exists and who knows what

- **Construction:** CIA commissioned `Kryptos` under a GSA art process, selected artist Jim Sanborn in 1988 and dedicated the work November 3, 1990. The work is a *physical installation*, not merely a 97-character string: copper screen, reversed Vigenere-type alphabet panel, granite, water, petrified wood, Morse inscriptions, lodestone and compass rose. [CIA](https://www.cia.gov/legacy/headquarters/kryptos-sculpture).
- **Working partnership:** Cryptographer Ed Scheidt described four processes, saying K4 deliberately masked its English statistical signature. Sanborn applied and possibly altered processes on his own. Treat cryptographic creator statements as primary evidence of *intent* but not a complete specification. [Scheidt interview](https://www.wired.com/2005/01/inside-info-on-kryptos-codes/) / [Sanborn interview](https://www.wired.com/2005/01/solving-the-enigma-of-kryptos/).
- **K1–K3 solved:** the first two use keyed Vigenere-family polyalphabetic substitution; K3 uses rearrangement/transposition. Their established spellings and misprints are part of the physical object, not editorial typos to silently "repair". [CIA](https://www.cia.gov/legacy/headquarters/kryptos-sculpture) / [Dunin corrected K2](https://elonka.com/kryptos/CorrectedK2Announcement.html).
- **2006 correction:** the initially appealing K2 ending `IDBYROWS` was **wrong**. A missing ciphertext character shifted the polyalphabetic key phase; Sanborn confirmed `XLAYERTWO` after repair. This is a decisive warning that *even coherent accidental English is not proof*. It also makes insertion, skipped text and phase errors historically relevant to test **without asserting the same defect exists in K4**. [Participant report](https://elonka.com/kryptos/CorrectedK2Announcement.html).
- **K4's exact cryptographic method/key remain unpublished:** Kobek and Byrne found the 97-character *plaintext* in publicly accessible Smithsonian scraps in September 2025 and Sanborn confirmed it, but they did **not** derive the key/algorithm from ciphertext. It has not been published as a public cryptanalytic derivation. [WIRED](https://www.wired.com/story/kryptos-code-reveal/) / [Scientific American](https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/).
- **Stewardship:** Sanborn's archive including claimed K4 method sold November 20, 2025 for $962,500 incl. premium. Paradigm publicly identified itself as the purchaser/steward June 12, 2026, and describes an answer verifier based on SHA-256 and cloud HMAC. The verifier can check a submitted **full answer**, not teach us the method. No answer submission occurred in preparing this dossier. [Auction](https://www.rrauction.com/auctions/details/730-decoding-history-kryptos-enigma-and-the-rosetta-stone/) / [Paradigm](https://paradigm-vc.vercel.app/2026/06/kryptos).

## 2. Published literal plaintext fragments — never in generation

The source for 97 ciphertext letters in *computational tests* is the repository file `r39/ic_gate/k4_ciphertext.txt`, whose historical SHA-256 **including trailing newline** is `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`. It must be used without adding, removing or correcting letters.

Only the following fragments of the K4 plaintext are authenticated publicly:

| Public disclosure | 1-based plaintext offsets | 0-based offsets | Ciphertext at those offsets | Known plaintext | Independent source |
|---|---:|---:|---|---|---|
| 2010 | 64–69 | 63–68 | `NYPVTT` | `BERLIN` | [WIRED 2010](https://www.wired.com/2010/11/clue-kryptos/) |
| 2014 | 70–74 | 69–73 | `MZFPK` | `CLOCK` | [Dunin clue history](https://elonka.com/kryptos/) |
| January 2020 | 26–34 | 25–33 | `QQPRNGKSS` | `NORTHEAST` | [Dunin clue history](https://elonka.com/kryptos/) |
| 2020, approved for public release August | 22–25 | 21–24 | `FLRV` | `EAST` | [Dunin clue history](https://elonka.com/kryptos/) |

Thus 24 different positions in the **post-decryption, final full 97-letter plaintext** are known (13 + 11). The words' locations and literal values MUST NOT be present in the code/data accessible to candidate generation. Do not compute candidate-specific derived shifts, conditional route keys, inverse masks, or fit a plaintext from these mappings.

The four 2020/2010/2014 disclosures need not be grammatical word boundaries; do not invent surrounding words, locations, compass measurements or text length from them. `EASTNORTHEAST` is a directional phrase; **67.5 degrees** is a standard 16-point compass nominal bearing, but the art provides no verified instruction to rotate/index anything by that number. The words naming a physical clock could describe a subject, an object, a location, or a key-source clue; they **do not** prove any one cryptographic operator.

## 3. New creator context reported November 12, 2025

At an International Spy Museum event / creator open letter, Sanborn provided *interpretive context*, according to [Scientific American's direct report](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/):

- His **1986 trip to Egypt** and the **1989 fall of the Berlin Wall** figure in the solution. These are not proofs that the dates are the numeric keystream.
- The clock intended is the **Urania World Clock / Weltzeituhr at Berlin's Alexanderplatz**, not automatically the Berlin-Mengenlehreuhr ("Berlin Clock" puzzle of lights).
- Kryptos codes concern **"delivering a message"**. This is interpretive guidance, not a literal decrypted phrase.
- Sanborn described **K5** as thematically related to a K2 passage and reportedly said it would be another 97-character cipher with some ciphertext words shared at the same positions. K5's actual ciphertext is not currently public in the source inspected. This is *not* evidence that K5 can be used as a known-plaintext oracle.
- Sanborn challenged purely mathematical assumptions, while Scheidt directly described mathematical/statistical frequency masking. **Avoid reading the two remarks as a contradiction:** both can be true if a reproducible process depends on physical/visual construction.
- The Scientific American article appears to have a **"79 encrypted letters"** typo in one sentence. Multiple primary references and the physical transcription establish **97**.

## 4. Known puzzle-wide text vs K4 clues

- K1's `IQLUSION`, K2's `UNDERGRUUND`, K3's `DESPARATLY`, plus K2's `XLAYERTWO` illustrate unusual spellings/missing-character effects in **already solved** sections. Do not treat them as wordlist seeds or K4 plaintext.
- K2 specifies a coordinate pair in northern Virginia, and sculpture geometry includes a compass rose and lodestone. A geographic interpretation may matter to the *riddle* after decryption, but coordinates are not an independently discovered K4 key.
- The tableau's intentionally reversed orientation is **directly described by CIA**; an attacker should model a physically observed read direction before assuming a standard textbook table. Source transcripts have known historical missing letters.
- K3's narrative is borrowed from the discovery of Tutankhamun's tomb; its transposition is solved and independently testable. That fact connects the story to Egypt but does not establish K4's encryption.

## 5. Research discipline / validation hierarchy

1. Blind generate a full **97-character** candidate from the unchanged cipher with a declared, externally sourced method and a derived key; record all routes/alternatives, score functions, seeds, models and executable hashes.
2. Commit and verify a **successful remote freeze** containing raw output and all source/hash manifests **before** any known plaintext comparison.
3. A separate evaluator checks complete round-trip encryption on the exact original ciphertext and compares the four known passages at the above positions.
4. Full 24/24 matches are necessary but insufficient; require independently derived key, coherent novel English, meaningful cryptographic method, reproducible forward encryption and a predeclared selection rule accounting for multi-testing. Passing a proprietary checker, by itself, would authenticate the answer string but not establish that it was found by cryptanalysis.
5. Refuse to build a 97-position free key from the desired answer or to update generation after seeing clue mismatches. Document negative checks rather than feeding them back into the same blind search.

**Read with `r53/BLIND_RULES.md`.** Human research can be informed by the clues (e.g., clock or German history) but the clue bytes and offsets are prohibited from entering the solving algorithm. This is the owner's clarified rule.
