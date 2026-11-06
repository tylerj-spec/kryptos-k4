# R70 pre-registration (Claude Code, 6 Nov 2026): running keys from five named, pinned source texts

Written before the holdout plants are generated and before any R70 run on K4. Follows `r53/BLIND_RULES.md` as
clarified by Tyler: clue-motivated ideas are fine; **the algorithm reads only the ciphertext, the pinned source texts
and generic models**; the published letters are used only as a check after everything is frozen and pushed. Tyler
approved running this on 6 Nov 2026 ("get these started as long as we are making progress to K4") and enabled
archive.org access for the sources.

## Why
- **The hypothesis:** K4 is a running-key cipher whose key is a contiguous passage of a book Sanborn could have used.
- **Where the books come from:** the Deep Research report (relayed by Tyler, 6 Nov 2026) proposed a narrow,
  theme-matched corpus. Sanborn confirmed in 2025 that K4 relates to Berlin (the World Clock), his 1986 Egypt trip and
  the fall of the Berlin Wall, and K3 is from Howard Carter's account of the Egyptian tomb.
  - **Source selection is clue-motivated** (Berlin, Egypt), which the owner's rule allows. It is disclosed here.
- **What is new against earlier rounds:**
  - R59 and R61 tested an *unknown* English running key at about 80% and 65% power.
  - A named-text test has power close to 1 for the exact editions.
  - It adds model M2 (key along a path) and the KRYPTOS tableau.
  - A clean negative excludes these editions under these models.

## Sources (pinned; `r70/corpus/fetch_sources.py`, `r70/corpus/normalize.py`)
Each archive.org OCR file (`_djvu.txt`) was fetched through the item's `/stream/` page. It was accepted only because
its SHA-1 equals the SHA-1 in archive.org's own metadata, so the bytes are archive.org's file. Full records are in
`r70/data/SOURCES.json` and `r70/data/NORM_MANIFEST.json`.

| Key | Edition | archive.org item | Normalised letters | Normalised sha256 |
|---|---|---|---|---|
| BERLIN_1912 | Baedeker, *Berlin and Its Environs*, 5th English ed., 1912 | berlinitsenviron00karl | 517,144 | 0f4f4718… |
| EGYPT_1908 | Baedeker, *Egypt and the Sûdân*, 6th ("sixth remodelled") ed., 1908 | 00491772.5459.emory.edu | 1,386,690 | c88ef5e1… |
| MURRAY_1907 | Murray's *Handbook for Egypt and the Sudan*, 11th ed., London: Stanford 1907 | handbookforegyp00hallgoog | 1,977,829 | 7aa62048… |
| COOK_1876 | *Cook's Tourists' Handbook for Egypt, the Nile, and the Desert*, 1876 | cookstouristsha07ltdgoog | 511,251 | bb3e3e3c… |
| BUDGE_1898 | Budge, *The Book of the Dead: An English Translation…* (Theban recension), Kegan Paul 1898 | bookdeadanengli00budggoog | 120,736 | 373f57b9… |

- **Substitutions, disclosed:**
  - The report's Cook edition (1897) is only on Google Books, which this environment cannot reach. The 1876 edition of
    the same title is used instead.
  - The report's Budge (*Papyrus of Ani*, 1895) exists on archive.org only as an access-restricted 1967 reprint. Budge's
    1898 public-domain translation of the same Theban recension is used instead.
- **Normalisation** (code, not prose): UTF-8 → NFKD → uppercase → keep A–Z only.
  - The whole OCR file is kept, in file order: front matter, advertisements, headers, index and OCR noise.
  - No discretionary cleanup.
- **Offsets:** every offset o = 0 … len − 97, key read forward. That is 4.51 M offsets in total.

## Hypotheses (exactly what is tested)
- **Rows (21, as R68):** ID (in place) plus the 10 frozen R61 routes × two models:
  - **M1** (substitute, then transpose): Y[t] = E(P[t], key[o + t]) with CT[j] = Y[perm[j]]. The plaintext is in path
    order.
  - **M2** (position-aligned, key along the path): CT[j] = E(P[j], key[o + perm[j]]). The plaintext is in carved order.
- **Conventions (6):** a single tableau alphabet A ∈ {AZ, KRYPTOS} for the plaintext, ciphertext *and* key letter.
  - With x = A⁻¹(p), y = A⁻¹(c), k = A⁻¹(key letter): VIG y = x + k, BEAU y = k − x, VARB y = x − k (mod 26).
  - These are R63/R64's running-key conventions; KRYPTOS / VIG is K1–K2's tableau.
  - Mixed-alphabet variants are not tested.
- **Plaintext:** ordinary English.
- **Count:** 4.51 M × 21 × 6 ≈ 5.7 × 10⁸ settings per ciphertext.

## Blind pipeline (frozen: `r70/blind/run.py`, `r70/blind/rk_text_scan.cpp`)
- **Stage A:** every setting is decrypted and scored with the order-4 slice of the R59 English model. The exact top
  1000 are kept; dropping a candidate early is admissible because every log-probability is ≤ 0.
- **Stage B:** those 1000 are rescored with the order-6 model + 1 × the R59 word score (the "total", as R68).
- **Kept:** the best 200 per ciphertext, frozen in `work/`. Rank 0 is the answer.
- **No tuning after this file is committed.**
- **Build:** `g++ -O3 -march=x86-64-v2 -std=c++17 -pthread` (g++ 13.3.0).
  - Scanner binary sha256 95671f68…;
  - sealed `exact_scan` binary sha256 0682230b….

## Development record (development plaintext only; K4 never run)
- **Development plant:** *Tom Sawyer* plaintext, key = EGYPT_1908 at offset 693,653, SNAKE_L / M2 / KRY_BEAU.
  - Recovered exactly at rank 0, total −142.0.
  - Rank 1 (same key, wrong model) scored −356.2; the best unrelated decode scored −472.4.
- **Contract test:** 3 more plants (ID, SNAKE_R / M1, COL_RB / M2) were all recovered at rank 0 with their exact
  setting.
- **Speed:** about 170–190 core-seconds per ciphertext (5.69 × 10⁸ settings).

## Holdout gate (fixed now)
- **Plants:** `r70/sealed/make_plants.py hold_pt.txt NORM 700001 OUT` (seed 700001).
  - Plaintext: R64's held-out English (*The Call of the Wild* + *The Hound of the Baskervilles*, sha256 17f61fafc…).
  - Key: a random offset in a random source; random row and convention.
  - **20 CLEAN** plants: the key is the normalised window itself.
  - **10 NOISY** plants, a model of OCR differing from print: 5 with 2 substituted key letters, and 5 with 2
    substitutions plus one deleted letter (the rest of the key shifted by one).
  - **20 nulls:** frequency-preserving shuffles of 20 plant ciphertexts.
- **Definitions:**
  - *recovered* = the rank-0 total is above the maximum null rank-0 total **and** ≥ 60/97 letters are correct;
  - *setting_ok* = source, offset, path, model and convention are all exact.
- **Gate:** PASS iff ≥ 18/20 CLEAN plants are recovered and `verify.py` passes (every frozen decode is a forward
  witness). NOISY recovery is reported as an OCR-robustness estimate.
- **If the gate fails:** INCONCLUSIVE; no K4 run.

## K4 phase
- **Target:** `r70/sealed/prepare_k4.py`: unchanged K4 (sha256 2797de14…) + 50 frequency-preserving shuffles
  (seed 700070).
- **Steps:**
  1. Run.
  2. Freeze (all 200 decodes per ciphertext).
  3. Push.
  4. `verify.py`.
  5. Only then the sealed steps below, which are the only R70 code holding the published letters.

### Sealed step 1: `reveal_k4.py`
Published letters: 0-based plaintext positions 21–33 EASTNORTHEAST and 63–73 BERLINCLOCK; plaintext order as R68.

| Outcome | Condition |
|---|---|
| **SIGNAL** | K4's rank-0 total exceeds all 50 nulls' **and** its plaintext matches ≥ 10/24 |
| **SCORE_ANOMALY** | The first condition without the second |
| **NO_SIGNAL** | Otherwise |

- **Contender screen:** every one of K4's 200 frozen decodes matching ≥ 12/24 is listed raw, with the nulls' maximum.

### Sealed step 2: `exact.py`, exhaustive block check
- **What it does:** every one of the 5.7 × 10⁸ settings is decrypted at the 24 published positions, on K4 and on the
  50 nulls.
- **Full block:** 13/13 (EASTNORTHEAST) or 11/11 (BERLINCLOCK). One OCR insertion or deletion between the blocks
  still leaves one block exact.
- **EXCL(source)** iff no setting of that source gives a full block on K4.
- **Chance level:** full blocks appear by chance about 26⁻¹¹ × 5.7 × 10⁸ ≈ 2 × 10⁻⁷ times per ciphertext. The nulls
  show the empirical rate.
- **Survivors:** a full-block setting is *reported*. It is not a candidate unless the blind ranking also found it (R53).

## Not tested (scope)
- Other editions, OCR versions or normalisations; keys read backwards or skipping letters.
- Mixed alphabets; transpositions other than the 10 R61 routes.
- Non-English plaintext; any masking layer.

A negative result excludes these five pinned texts under these 21 rows × 6 conventions, and nothing more.
