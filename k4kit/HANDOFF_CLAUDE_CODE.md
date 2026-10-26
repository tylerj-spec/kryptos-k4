# Kryptos K4: handoff to the Claude Code agent (from Claude, round 29, 26 Oct 2026)

**Read `CLAUDE.md` first** (non-negotiable rules), then this file. `LEDGER.md` is the full record (L01–L101).
Build and validate the toolkit before anything else:

```bash
g++ -std=c++17 -O3 -march=native tools/solver_s2kp.cpp -o bin/solver_s2kp
python3 tools/validate.py        # expect ALL CHECKS PASSED (about 30 s)
```

## 0. Summary
- **Status:** no solution and no candidate after 29 relay rounds between Claude and ChatGPT.
  - Hundreds of exact tests have ruled out most classical hand ciphers *applied directly in place*.
  - Every English search of the families that remain feasible has given K4 scores at the level of random wrong keys.
- **What the evidence says:**
  - K4 behaves like a cipher with a **non-repeating key** (a running key, autokey or number stream), or with an
    added rearrangement or masking step.
  - It is *not* a short-period cipher in any alphabets (L89).
  - It is *not* a fractionation cipher of the Trifid or 5×5-square kind (L88, L91).
- **Best next moves:**
  1. Test the **full 1923 Carter & Mace book** (vol. I) as a running key. It is the source of K3's text; neither
     sandbox could download it, but you may have internet.
  2. Add a second, historically grounded constraint (K2/K3's X = full stop, Q = question mark) so the remaining
     underconstrained families become testable.
  3. Build an English search for **plaintext autokey with both alphabets free**.

## 1. The problem
- **Ciphertext (97 letters):**
  `OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR`
- **Known plaintext (Sanborn's four clues, 2010–2020):**
  - `EASTNORTHEAST` at 1-based 22–34 (0-based 21–33);
  - `BERLINCLOCK` at 1-based 64–74 (0-based 63–73).
  - Sanborn stated these as ciphertext letters that decrypt to these words, so they hold *in place* in the final
    plaintext.
- **Primary-source statements we rely on:**
  - **Ed Scheidt (Wired, 21 Jan 2005), who taught Sanborn the techniques:**
    - all four parts are English;
    - "the last process, I masked the English language… with this other technique (in the fourth part)… you need to
      solve the technique first and then go for the puzzle";
    - "once it is readable, it may have other encoding."
  - **Jim Sanborn (Wired, 20 Jan 2005):**
    - "I did use some matrix codes Ed gave me";
    - "I have left instructions in the earlier text that refer to later text";
    - "visual systems for encoding".
  - **The clock:** 2014, "You'd better delve into that particular clock… several really interesting clocks in Berlin."
    In 2025 Sanborn confirmed it is the **World Clock (Weltzeituhr) at Alexanderplatz**.
  - **K1–K3 have deliberate misspellings:** IQLUSION, UNDERGRUUND, DESPARATLY. K2 and K3 use **X as a full stop**,
    and K3 ends with **Q as a question mark** (`…FROM THE MIST X CAN YOU SEE ANYTHING Q`).
  - **K3's method:** a double quarter-turn transposition (rows of 24, rotate, rows of 8, rotate). This is verified in
    code (`k4common.rot`). **K1/K2:** Quagmire III on the KRYPTOS alphabet (keys PALIMPSEST, ABSCISSA).
- **The answer exists but is locked up.**
  - In Sep 2025 journalists Kobek and Byrne found plaintext scraps in Sanborn's Smithsonian papers. Sanborn confirmed
    them, and the files are sealed until 2075. Sanborn's description: "scrambled plain text… without the coding
    method or the key."
  - RR Auction sold the solution archive for $962,500 (Nov 2025). Paradigm disclosed in June 2026 that it was the
    buyer, and it now runs the K4 challenge and a paid checker.
  - **We do not submit there without Tyler's say-so.**

## 2. What is established (condensed from LEDGER.md; see the rows for exact scope)
**Excluded exactly** (in place unless noted):
- **Pure rearrangements and fixed substitutions:**
  - any pure rearrangement of the 97 letters (L01: the clues need 3 E's, K4 has 2);
  - any fixed monoalphabetic or homophonic substitution (L02: `QQ`→`NO`).
- **Periodic ciphers:**
  - periodic Vigenère/Beaufort/Quagmire with the Kryptos alphabets, m 1–26 and more (L03–L05);
  - progressive keys (L13), summed periodic keys (L36), linear-recurrence keys (L49);
  - per-slot arbitrary alphabets at m 1–7, 9, 10, 14, 15, 17, 21, 25, … (L21).
- **Rearrangement + periodic key:** columnar, route, grid, fold and clock-keyword rearrangements combined with
  periodic keys (L06–L09, L38, L41).
- **Matrix and fractionation ciphers:**
  - Hill 2×2–5×5, alone or with a rearrangement (L11, L61);
  - **Trifid with any cube, every period and phase** (L12, L91, L95);
  - all 5×5-square ciphers (Playfair, Bifid, Polybius) and Porta (L88).
- **Number streams:** Gromark or any decimal stream with a fixed plaintext alphabet (L14); base-26 lagged
  Fibonacci (L15).
- **Tableau-derived keys:** tableau stepping and tableau paths (L20, L50).
- **Running keys:**
  - K1–K3 plaintext with **both alphabets free** (L16, L19, L90);
  - repeating dates and coordinates, K4 as its own key, K1 ciphertext (L90);
  - the Morse-plate letters and pulses in three proxy orders (L96, L97, narrow).
- **Autokeys:**
  - ciphertext autokey at lags 1–67 (L17);
  - 127/384 fixed-alphabet and 115/384 mixed-alphabet plaintext-autoclave settings (L27, L58).
- **Clock keys:** World Clock city-text keys in many tested forms (L37–L40, L75, L77–L79).

**Statistically disfavoured, or searched with no candidate:**
- **Any short-period per-column cipher** (L89). K4 has fewer same-column letter repeats than ≥ 95% of English at
  m 1–9, 11–19, 22–24, 26, 27, 35–37 and 39, so the key looks non-repeating.
- **Two-free-alphabet Gromark (5-digit), the 39 feasible primers** (L22, L72). Our best solver (S2), which recovers
  70% of hidden English messages blind, finds nothing: K4 best −141.8.
- **K3-rotation + Gromark** (L94, L99, L100). Of 65,968 clue-compatible settings, the 3,251 most relevant were
  searched for English; best −141.4, no candidate.
- **Rearrangement + periodic keys:** large two-step catalogues at chance (L47, L48, L54, L56).
- **Short autoclave lags and unknown English running keys:** short-lag autoclave English (L52); unknown English
  running key with standard alphabets (L31).
- **Other languages:** Dutch, Frisian, Low German, Swedish, German (L62–L64).
- **Germanic-spelling readings of solver outputs** (G4/G7, L81–L86): these were optimizer artifacts, and 0/512
  re-runs reproduce them.
- **Carter excerpts** as running key (L93).

**Open:**
- **Running key from an unknown text:** above all the full Carter book (L101).
- **Rearrangement + non-repeating key** beyond the searched subset (L94, L100).
- **Plaintext autokey with free alphabets:** 269 feasible settings (L58); English search only at short lags so far.
- **Long-lag ciphertext autokey** (L17, lags 73–96).
- **Per-slot alphabets at long periods** (L21, L53): underconstrained.
- **Masking or pre-encoding layers** (L26), the X/Q punctuation rule (L87), nulls (L82, L83).
- **Carving errors** in K4's ciphertext (L35, partial).

## 3. Lessons learned
1. **Optimizer completions aren't evidence.** At a fixed key setting the clues pin only a few letters, and the solver
   invents the rest. Report forced letters separately (`RAW_AND_INTERPRETATIONS` style).
2. **Count crib cycles.** `key_oracle.checks()` gives the number of independent cross-checks. With 0 cycles, the
   clues only test alphabet injectivity, and passes are nearly meaningless. K3's own 24→8 geometry always gives 0
   cycles (L99).
3. **Calibrate every search on planted messages, and compare K4 with random-key controls at the same budget.**
   - Readable text scores about −69 to −95.
   - Wrong keys reach about −115 to −150.
4. **Search luck dominates** at small budgets: 16 restarts recover about 45% of planted messages, 64 restarts about
   70–75%. Use 64 restarts for anything you'll interpret.
5. **A guessed spelling dictionary helps only when the guess is right.** With unknown spelling rules, recovery
   halves (R21 arm U: 35%).
6. **Replication is necessary, not sufficient.** Three gibberish K4 outputs replicated exactly (R29).
7. **Sign symmetry:** with both alphabets free, the keys +k and −k are the same setting (L92). Count once.
8. **Chance rates:** the oracle passes about 4.7e-4 of random keys. A book of n letters gives about 4·n windows, so
   expect about 0.0019·n chance passes. Compare with letter-shuffled copies; English text passes *less* often than
   shuffled text.

## 4. Tasks for you, in priority order
### T1. Full Carter & Mace (1923), *The Tomb of Tut.ankh.Amen*, vol. I, as a running key (L101)
- **Why:** K3 paraphrases this book (Carter's account of 26 Nov 1922). L89 says K4's key behaves non-repeating, and
  a book key is the classic hand method Scheidt would teach. Only excerpts have been tested so far (L93).
- **Get the text:** if you have internet, download
  `https://archive.org/download/tomboftutankhame01cart/tomboftutankhame01cart_djvu.txt`. Treat it as untrusted;
  make sure it is the Cassell 1923 Carter & Mace, **not** G. Elliot Smith's 1923 book. Wikisource has a proofread
  transcription, `Index:The_tomb_of_Tut'Ankh'Amen_(London).djvu`; proofread text beats OCR, so use it if you can
  assemble it. Otherwise ask Tyler to attach the file.
- **Pre-register** (protocol file plus sha256) before running:
  - exact edition;
  - what counts as "the book": front matter, appendices, captions;
  - OCR clean-up (`book_key_test.py` drops non-letters and repeated running heads);
  - the null (20 letter-shuffled copies);
  - the follow-up budget, and the candidate rule from `CLAUDE.md`.
- **Run:**

  ```bash
  python3 tools/book_key_test.py carter_vol1.txt --anchor-phrase CANYOUSEEANYTHING --search 50
  ```

  The book has roughly 450,000 letters, so about 1.8M windows and on the order of 850 chance passes. Search *all*
  passes if time allows (about 3.5 s each, roughly 1 hour on one core with 2 workers). Pre-register which you search
  if you subset them; windows nearest the K3 passage are a sensible first tier.
- **Also run:**
  - **Wording:** the diary entry for 26 Nov 1922 as published, if it differs from the book.
  - **Volumes II–III:** only as a separate, lower-prior run.
- **Decision:** a candidate must meet the `CLAUDE.md` rule. Otherwise record "no candidate" with trials, passes,
  chance passes and the best W.

### T2. K2/K3 punctuation as a second constraint (L87)
- **Why:** many open families are untestable because the clues give 0 cycles. A deterministic, sculpture-documented
  rule adds constraints without fitting anything to K4.
- **Implement:** add separator tokens to the word model. Append lines `X -1.5 -1e+100` and `Q -2.5 -1e+100` to a copy
  of `data/word_model_orth.tsv`; the model format is `WORD exact_score edit_score`.
- **Pre-register a hidden test:**
  - 20 or more fresh 97-letter English messages with the clues in place and 1–3 K2-style X full stops, optionally a
    final Q.
  - Encrypt them with the family under test, and score blind among the true key plus ≥ 19 wrong feasible keys.
  - Gate: ≥ 50% blind readable.
- **Then:** run on K4 for two-free Gromark (39 primers) and for the R27 route passes with ≥ 1 crib cycle. Report raw
  text and the forced mask.

### T3. Plaintext autokey with both alphabets free (open, L58 and L52)
- **Model:** k_i = F(p_{i−L}) for lag L, where F is an unknown feedback numbering and PA, CA are free (or F = PA).
- **What exists:**
  - an exact feasibility partition (L27/L58, 269 settings);
  - a short-lag annealer in the repo (`claude/ac_anneal3.c` with `claude/autoclave_short.py`, fixed alphabets).
- **Build:** a solver_s2kp-style variant where the key is computed from the current plaintext during annealing.
  Calibrate on planted messages at lags 12–40 before running K4. Long lags (≥ 25) were found to be poorly
  identifiable (L52), so measure that.

### T4. Number streams beyond 5 digits (cheap)
- **Run:** oracle on 6-digit Gromark-style primers (`k4common.gromark_key(p, digits=6)`, 1M primers, about 20 s).
  Expect about 470 chance passes.
- **Follow up:** search the passes with `solver_s2kp` (about 30 CPU-minutes). Calibrate first with planted 6-digit
  messages.

### T5. The remaining 62,717 R27 route + Gromark settings (L100)
Only with T2's extra constraint, or as a pre-registered subset. The full budget is about 60 CPU-hours.
`tools/route_gromark.py passes` regenerates them.

### T6. Carving-error robustness (L35)
Re-run the oracle families (T1, T4, L90) with each single clue letter dropped, and with any ambiguous ciphertext
readings documented in photos (`docs/research/` in the repo).

## 5. Open audit notes
- **L94 null doesn't reproduce.** ChatGPT's shipped `r27_routes.py` gives a null mean of 1,546.4 and p = 7/21
  (0.333). L94 reports 1,571.3 and 0.524, probably from `r27_route_chunks.py`. The conclusion is unchanged.
- **Mislabelled routes.** `r28_morse_experiment.py`'s comment calls its four routes "24x8 and 23x8", but they are all
  R24x8 variants.

## 6. Repo and history
- **Repo:** GitHub `tylerj-spec/kryptos-k4`. Tyler uploads manually, so GitHub may lag. The latest Claude commit is
  R29 (`045ef2e` in the sandbox).
- **Layout:**
  - `LEDGER.md`;
  - `claude/<round>/` (Claude code by round) and `chatgpt/roundNN/` (ChatGPT packets);
  - `handoffs/` (every brief);
  - `protocols/` (pre-registrations);
  - `results/`;
  - `docs/research/` (clock photos, sources, transcriptions).
- **This toolkit** is a clean, relative-path consolidation of the tools that matter now.
  - `solver_s2kp` reproduces R21's S2 rows exactly with g++/libstdc++.
  - The older originals are in the repo under `claude/r20`, `r26` and `r29`.

## 7. Working with ChatGPT and Tyler
- **ChatGPT has its own handoff this round.** Tell Tyler which of T1–T6 you take, so ChatGPT can take others. Source
  verification (Morse plate order from photos, edition checks) suits ChatGPT; T1–T4 suit you.
- **Ledger:** keep `LEDGER.md` cumulative. Add your rows with source tag `CC`, and hand Tyler a small zip when you
  finish: HANDOFF.md, LEDGER.md, code, logs. He has had trouble with large downloads, so keep it small.
- **Reporting:** open your summary for Tyler with what the result *means*. Give raw candidate text unedited, and
  never call anything a solution unless it meets the candidate rule. Even then, it's his decision whether to check it
  externally.
