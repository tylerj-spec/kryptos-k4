# R38 source-led technical distinctions — October 2026

## Actual ACA Gromark keyed alphabet (different from R37)

American Cryptogram Association, *GROMARK (100–150 letters)*, https://www.cryptogram.org/downloads/aca.info/ciphers/Gromark.pdf, gives the cipher alphabet as the **columnar readout** of a transposition block:
1. Deduplicate the keyword (e.g. ENIGMA).
2. Write the keyword as the first row; fill remaining letters of A-Z underneath row-wise.
3. Read columns sorted by the top keyword letters.

The source's ENIGMA example yields `AJRXEBKSYGFPVIDOUMHQWNCLTZ`. With primer 23452, the 35-character text `THEREAREUPTOTENSUBSTITUTESPERLETTER` encrypts exactly to `NFYCKBTIJCNWZYCACJNAYNLQPWWSTWPJQFL`. The R38 regression test checks both the cipher alphabet and the example ciphertext.

By this rule:
- KRYPTOS → `KAHUOFNPDLXRBIVSGQTEMZYCJW`
- PALIMPSEST → `ACOZEJWIFRLDQMGUPBNYSHVTKX`
- ABSCISSA → `ADJOUZBEKPVCGMRXIHNTYSFLQW`

R37 used *keyword prefix + remaining AZ* and is therefore a **distinct** hypothesis, not a test of canonical ACA Gromark. Neither should be generalized to arbitrary alphabets.

## November 2025 Sanborn statements

Sanborn's November 12, 2025 talk and open letter, reported by Scientific American (https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/), clarified that the K4 BERLINCLOCK reference is the **Weltzeituhr / World Clock at Alexanderplatz** (not the separate Mengenlehreuhr commonly called the Berlin Clock). He also connected the plaintext's ideas to his late-1986 Egypt trip and the 1989 fall of the Berlin Wall, and described the theme as “delivering a message”. The statements are **historical context**, not permissible masks or training snippets for blind K4 search. If a candidate emerges from an entirely blind run, these may be used for *after-freeze interpretation* only.

Sanborn told the Associated Press in November 2025 that archival researchers discovered text but not the key/method; this project seeks a independently replicable mathematical method, not an archival transcript.

## R38 interpretation

Tests only 4 fixed alphabet constructions (AZ, ACA KRYPTOS, ACA PALIMPSEST, ACA ABSCISSA). No claim that the true K4 cipher follows ACA Gromark or uses any of these exact alphabets. Strict-blind controls and independent counts remain mandatory.
