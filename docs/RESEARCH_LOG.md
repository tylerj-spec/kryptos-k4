# Research log for the `docs/` library (Claude Code, 1 Nov 2026)

What was read to write `docs/`, and what each source said. The record lets anyone check or redo the research. No
experiments were run.

## 1. Repository sources read
- **`LEDGER.md`,** rows L01–L146: the model, exact scope, status and key numbers of each recorded round, summarised in
  `CIPHER_TYPES_TESTED.md`. L143 was integrated on `main` **only as a historical, crib-conditioned row**; its code remains on unmerged PR #12. L144–L146 document negative R55–R57 findings.
- **Reviews and handoffs:** `HANDOFF.md`, `r44/REVIEW_R45_R48.md`, `r44/REVIEW_PR11.md`.
- **Research notes:**
  - `r38/RESEARCH_NOTES.md`: the ACA Gromark alphabet rule and Sanborn's November 2025 statements.
  - `archive/sources/README.md`: provenance of the Carter 1923 text.
  - `archive/2026-10-26_chatgpt_starter/KRYPTOS_K4_MASTER_AGENT_HANDOFF_2026-10-26.md`: the Morse/K0 transcription
    source and Scheidt's "masking" quote.
  - `archive/2026-10-26_chatgpt_starter/r28_morse_experiment.py`: the Morse panel phrases as transcribed.
- **Code headers** of every tool listed in `TOOLS_INDEX.md`.
- **Computed from the ciphertext:** the K4 letter counts, IC 0.0361, the sha256
  `2797de14…0f0a5a3` (with newline), and the clue alignment, including the self-encryptions S→S at 33 and K→K at 74.

## 2. ChatGPT branches read (tip commits as fetched 1 Nov 2026; R49, R53 and R54 have since merged to `main`)

| Branch | Tip | What it tests | Result |
|---|---|---|---|
| `chatgpt/r48-physical-tableau-key-hypothesis` | 360059d | Literal 97-letter "reverse tableau" stream from a third-party website, as key | 0/52; source unauthenticated |
| `chatgpt/r49-historical-world-clock-evidence` | 55415be | World Clock source inventory: 1969 / 1980 / 1997 changes, Kunsch drawings | Evidence only; no contact made |
| `chatgpt/r50-pretransposition-keyword-feasibility` | 0e21101 | K3 24×8 rotation **before** Gromark substitution, keyword × free alphabet | Two-free 52 / 1,569 / 1,479 / 8,805; keyword **0** |
| `chatgpt/r51-ciphertext-feedback-k3-feasibility` | dc8ba97 | K3 rotation before a ciphertext-autokey substitution, lags 1–24 | Two-free 37 of 192 (all with 0 graph cycles); keyword **0** |
| `chatgpt/r52-educated-plaintext-probe` | 7644e7a | Eight hand-written plaintext guesses; test of fitted-key periodicity | Family-wise p ≈ 0.29; no signal |
| `chatgpt/r53-hard-blind-output-first-contract` | 83847e0 | **Owner rule:** a solver never sees the known letters; Docker firewall CI | Rule adopted; Caesar smoke test fails K4, as expected |
| `chatgpt/r54-method-fingerprints-no-crib` | c9c840e | Ciphertext-only statistics of K4 against English and synthetic families | IC 0.0361, below every 97-letter K1–K3 window (min 0.053); lag 7 not significant (≈ 15%) |

## 3. Web sources consulted (1 Nov 2026)

**Query: "Kryptos K4 auction result November 2025 Sanborn solution sold"**
- **Sale:** RR Auction (Boston) sold Sanborn's K4 archive to an anonymous bidder. Reports say $962,500 or $963,000,
  on 20 Nov 2025, above the $300,000–500,000 estimate. The winner gets a private meeting with Sanborn.
- **Not public:** the solution has not been released by the buyer or the finders.
- **Sources:**
  - https://www.wbur.org/news/2025/11/24/kryptos-sculpture-cia-headquarters-decipher-boston-auction
  - https://www.barchart.com/story/news/36262226/info-to-decipher-secret-message-in-kryptos-sculpture-at-cia-headquarters-sells-for-close-to-1m
  - https://news.artnet.com/art-world/cia-kryptos-sculpture-code-auction-2677451

**Query: "Kryptos K4 plaintext found Smithsonian archives Kobek Byrne 2025"**
- **The find:** in early September 2025, Jarett Kobek and Richard Byrne found K4 materials in Sanborn's papers at the
  Smithsonian's Archives of American Art and derived the plaintext from them. They do not have the encoding method.
- **The papers:** Sanborn says the scraps were included by mistake.
- **Not published:** NYT, 16 Oct 2025, reported that the finders will not publish the plaintext.
- **Archive sealed:** reportedly for about 50 years (until about 2075).
- **Sources:**
  - https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years
  - https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/
  - https://www.rrauction.com/jim-sanborn-kryptos-k4-solution-auction/

**Query: "Kryptos K2 LAYER TWO ID BY ROWS 2006 Sanborn omitted letter"**
- **The correction:** in April 2006 Sanborn told the Kryptos Group that K2's ending is "X LAYER TWO", not "ID BY
  ROWS". He found the error while comparing plaintext and ciphertext letter by letter for a book.
- **Which letter was omitted:**
  - Sanborn describes the plaintext X separator as omitted.
  - Analyses say the missing ciphertext letter is an S. With it, the last line decodes to
    `…TESFORTYFOURSECONDSWESTXLAYERTWO`.
  - Wikipedia says the letter was left out "to keep the sculpture visually balanced".
- **Sources:**
  - https://elonka.com/kryptos/CorrectedK2Announcement.html
  - https://en.wikipedia.org/wiki/Kryptos
  - https://wirednews.pages.dev/2006/04/typo-confounds-kryptos-sleuths

**Already in the repo and re-used**
- https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/ (Sanborn, Nov 2025:
  the Weltzeituhr, Egypt 1986, the Berlin Wall 1989, "delivering a message").
- https://www.cryptogram.org/downloads/aca.info/ciphers/Gromark.pdf (the ACA Gromark rule).
- World Clock sources listed in ChatGPT's `r49/RESEARCH_STRATEGY.md`: berlin.de, weltzeituhr-berlin.de, Berliner
  Zeitung 1997, Bundesarchiv photos.

## 4. Facts stated from general knowledge, not re-checked online this session
These are marked "~" in `KRYPTOS_FACTS.md`. Check them before building an experiment on any of them:
- the NSA solution of K1–K3 around 1992–93;
- David Stein's 1998 solution;
- Gillogly's 1999 solution;
- the dates of the clue releases (Nov 2010, Nov 2014, Jan 2020, Aug 2020);
- the details of the raised letters, the extra L on the tableau and Antipodes;
- Chaocipher's history (Byrne 1918; method published 2010).

The definitions of classical ciphers in `CRYPTOGRAPHY_REFERENCE.md` are standard textbook material (Gaines, Friedman,
Kahn, the ACA).

## 5. Corrections made while writing
- **Masking quote:** it is attributed to **Scheidt** (WIRED 2005), not Sanborn.
- **Chaocipher:** use in 1990 is described as *unlikely*, because the method was published only in 2010.
- **Bacon's cipher:** dated to its full description in 1623.
- **Uncertain items reworded as reported:** the raised letters, the compass rose and lodestone, and Antipodes.

## 6. Independent methodological review and integration (1 Nov 2026)
- R55, R56 and R57 merged to `main` after passing frozen-source, synthetic hidden-key, independent forward-encryption, and K4 separate-after-freeze checks. The negative outcomes and exact scopes are in [`R55_R57_METHODOLOGY_AUDIT.md`](R55_R57_METHODOLOGY_AUDIT.md); their complete raw outputs live in the respective round directories.
- Corrected an **overbroad exclusion** in the original reference library: direct `QQ` versus `NO` rejects an *in-place monoalphabetic substitution*, not an unknown substitution-plus-transposition. Likewise direct self-encryption logic is not invariant under a subsequent permutation.
- Primary statements rechecked: [Ed Scheidt's Jan 2005 WIRED interview](https://www.wired.com/2005/01/inside-info-on-kryptos-codes/) on K4 masking and the possibility that its technique is unknown; [Sanborn's Nov 2025 remarks](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/) cautioning against assuming K4 is exclusively mathematical.
- New status absent from the original Claude draft: Paradigm's June 12, 2026 [Project Kryptos](https://www.paradigm.xyz/writing/kryptos) announcement identified the new archive steward and described an automated answer checker; this is a first-party representation, not an independent audit or authorization to submit guesses.
- A 2026 [independent CTF solution account](https://asynchronous.win/post/solving-pk1-pk7-at-paradigms-ctf/) documents combinations of Quagmire, transposition and Hill as *separate contest puzzles*. They might be useful independent solver-control tasks, but their mechanisms are not evidence of the original K4 encryption method.
- **No new K4 decryptions were generated by the documentation review itself**; future experiments must continue honoring R53's ciphertext-only-before-freeze rule.
