# Cryptanalysis methods: how to attack classical ciphers, and how this project does it

Claude Code, 1 Nov 2026. Part A covers the general techniques. Part B covers this project's methods: the
exact-feasibility oracles, the blind solvers, and the evidence rules.

---

## Part A — general techniques

### A1. Frequency and index of coincidence (IC)
- **Letter frequencies** (English, approximately): E 12.7%, T 9.1%, A 8.2%, O 7.5%, I 7.0%, N 6.7%, S 6.3%, H 6.1%,
  R 6.0%. The rare letters are J, Q, X, Z.
- **IC:** `Σ n_i(n_i−1) / (N(N−1))`.

  | Text | IC |
  |---|---|
  | English | ≈ 0.066 |
  | Random | 1/26 ≈ 0.0385 |
  | K4 | 0.0361 |

- **Friedman's estimate of a Vigenère period:**
  `m ≈ 0.027·N / ((N−1)·IC − 0.0385·N + 0.066)`.
- **Column IC:** split the text into *m* columns. If *m* is the period, each column's IC rises to English level.
- **Caveat for K4:** 97 letters is short. The IC's standard error is about 0.004, so only large effects are visible.

### A2. Kasiski examination
Repeated n-grams (3+ letters) in the ciphertext are often the same plaintext under the same key phase. The distances
between repeats share the period as a factor.
- **K4:** K4 has almost no repeats.

### A3. Chi-squared and n-gram fitness
- **Chi-squared** compares observed letter counts with the expected counts under each candidate shift. It solves
  each column of a known-period Vigenère.
- **Fitness scores** sum log-probabilities of n-grams: quadgrams are standard, and words are better. They rank
  candidate decryptions.
  - **Project data:** `k4kit/data/quad_log10.f32` and `k4kit/data/word_model_orth.tsv`.
- **Warning (L138):** at 97 letters, an optimizer can make wrong text score as well as the truth on quadgrams. Use
  word-level scores and planted controls.

### A4. Hill-climbing and simulated annealing
1. Start from a random key.
2. Make a small change (swap two alphabet letters, change one key value).
3. Keep it if the score improves, or sometimes even if it worsens (annealing temperature).
4. Restart many times.

**Variants:**
- **Parallel tempering:** several temperatures that swap states.
- **Beam search:** keep the best *B* partial solutions.

**This is the workhorse for substitution ciphers with unknown alphabets.** It works when the key is right and only
the alphabet is unknown (R42, R44b).

### A5. Known-plaintext and crib attacks
- **Crib:** a guessed or known plaintext fragment, e.g. EASTNORTHEAST.
- **Crib dragging:** slide the crib along the ciphertext and see which positions give a consistent key.
- **With a known position:** each crib letter gives one equation `c = CA[PA⁻¹(p) + k]`. Enough equations pin down or
  contradict a whole family; see B1.
- **Isomorphs:** the same plaintext under the same alphabets, but a different key offset, gives ciphertext with the
  same *pattern* of repeats. This was used historically to recover keyed alphabets.

### A6. Running-key and two-text separation
If both the key and the message are English, `c = p + k` is a sum of two English texts. Try common words as `p` at
each position and check whether `k` reads as English too (Friedman's method).
- **Power:** low on 97 letters without a known source (L31).

### A7. Transposition attacks
- **Anagramming with frequency kept:** try column orders and score the result with digrams/quadgrams.
- **Multiple anagramming:** two messages of the same length with the same key can be unscrambled together.
- **Exhaustive routes:** generate every route of a family (`strictblind/blind/routes.py`) and test each one.

### A8. Algebraic attacks
- **Hill, linear recurrences, LFSRs:** solve linear equations mod 26 from known plaintext (L11, L49).
- **Union-find with offsets:** for tableau ciphers with free alphabets, the crib equations form a graph. A
  contradiction anywhere proves the setting impossible. This is the project's "EdgeGraph" (see B1).

### A9. Statistical identification of the cipher type
Use these features to guess the family before searching:
- IC;
- the number of distinct letters;
- doubled letters;
- even or odd length;
- the presence of J or Z;
- digram statistics;
- periodic IC;
- the long-repeat count.

**References:** the ACA and the "BION" classifier, and NCID neural classifiers. **R54** applied this to K4: the IC is
too flat for a substitution or transposition of normal English.

### A10. Side information
History, the designer's habits, and other ciphers by the same author.
- **For Kryptos:**
  - K1–K3 methods;
  - the tableau;
  - Sanborn's statements;
  - the misspellings;
  - the Morse panel.
- **Rule:** side information sets **priors**, not facts. Every idea it inspires still needs a blind test.

---

## Part B — the methods built in this project

### B1. Exact feasibility oracles (crib-assisted, proof-grade)
Given a key sequence, the 24 known letters give 24 equations `CA⁻¹(c_i) − PA⁻¹(p_i) = k_i (mod 26)`.

- **Two free alphabets** (`k4kit/tools/key_oracle.py`, R43 EdgeGraph, `r44/audit/*.cpp`):
  - Build a graph whose nodes are cipher letters and plaintext letters, with edges weighted by `k_i`.
  - Union-find with potentials detects a contradiction around any cycle.
  - Then check that each side can still be a bijection (the "packing" check).
  - **Cycles are what give power.** A setting whose constraints form a forest is always feasible and proves
    nothing (R51).
- **One fixed or keyword alphabet:** `PA⁻¹(p)` is known, so equal cipher letters must have equal `PA⁻¹(p)+k`. This is
  a fast pattern check (R45, L141, R52).
- **Fully fixed alphabets:** decrypt and count matches (strictblind's `whole_family`).
- **Since R53 (owner rule, 31 Oct 2026):** these give **exclusions only**. Their survivors must not seed blind
  searches.

### B2. Blind solvers (ciphertext only)
- **Fixed alphabets × key family:** `strictblind/` scans every key and ranks by quadgram score. Plants must come back
  #1 (L120).
- **Free plaintext alphabet** (R40): for each key, `y = CA⁻¹(c) − k` is a simple substitution of the plaintext.
  - **Screen:** sorted letter counts against English frequencies (very sharp).
  - **Solve:** a substitution solver.
- **Free cipher alphabet** (R42): Hungarian-assignment unigram screen, then quadgram annealing of the cipher
  alphabet.
- **Keyword plaintext alphabet × free cipher alphabet, key given** (R44b; `r44/blind/kwpa_solve.cpp` + `polish.cpp`):
  enumerate 4,749 keyword alphabets, anneal the cipher alphabet, then word-score polish. **20/20 on a fresh
  holdout.**
- **Two free alphabets, key given** (`r43dev/`): parallel tempering. **Not solved.** The truth is identifiable by
  word score, but search doesn't reach it (L138, L139).

### B3. The evidence rules (why we trust a negative and would trust a positive)
These are adopted from R31 onward and tightened in R53.

1. **Pre-register:** write the hypothesis, search space, solver, scoring and success bar first. Commit the file
   with its sha256. Only dated amendments are allowed before evaluation.
2. **Blind:** the solver sees only the ciphertext, the declared key source and a language model. It never sees the
   24 known letters or their positions (R53).
3. **Freeze:** hash and commit all outputs before any comparison.
4. **Reveal:** a separate program re-encrypts each output and counts the known letters.
5. **Controls:**
   - **Planted messages** (fresh text, unseen by development) must be recovered at a pre-set rate, e.g. ≥ 16/20.
   - **Nulls** (shuffled ciphertexts) show what chance produces under the same search.
6. **A candidate must:**
   - read as language;
   - come from a blind run;
   - re-encrypt exactly;
   - have all 24 letters.

   **A fitted key or alphabet proves nothing:** any 97-letter text can be "encrypted" to K4 with a fitted key (L60,
   R52 ChatGPT).
7. **Report raw text unedited.** Count exclusions only for the exact scope tested.
8. **Multiple testing:** correct for every choice made (lags, alphabets, guesses). R52-ChatGPT's "period 7" vanished
   after correction.

### B4. Practical recipes
- **Testing a new key family:**
  1. Write a generator.
  2. Run the exact screen (B1) as a labelled crib-assisted exclusion. If 0 feasible, stop.
  3. If survivors exist, build a blind solver.
  4. Gate it on fresh plants with the key **unknown**.
  5. Only then run it on K4 blind (B3).
- **Testing a physical or historical key source:**
  1. Authenticate the source first: primary photographs, edition, sha256.
  2. Pre-register the reading order(s).
  3. Treat every uncertain reading as its own declared variant.
- **Testing a steganographic idea:** see `STEGANOGRAPHY_REFERENCE.md` §5.
