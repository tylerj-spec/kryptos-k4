# German / Dutch / Germanic masking research (historically constrained)

**Research only; no K4 solution or new K4 candidate.** Treat this as a set of falsifiable linguistic hypotheses. **Do not feed published K4 plaintext words or positions to a generator, scorer, training examples, selected keys or hyperparameter search.** See the sealed validation-only register only after a completed remote freeze.

## 1. First establish what Scheidt actually said

In his [Jan. 2005 WIRED interview](https://www.wired.com/2005/01/inside-info-on-kryptos-codes/), Ed Scheidt said **all four plaintext sections were English**, with K4's normal English frequency signal deliberately disguised. In a [June 2005 NPR segment](https://elonka.com/kryptos/mirrors/npr/2005transcript.html), the reporter mentioned phonetic spellings as **solver speculation**, **not** as an admission by Scheidt that he used Dutch, German or any particular code-talker scheme.

This yields **three distinct hypotheses**, not one:

1. **H-DE-KEY:** K4's *final plaintext* is normal English; encryption key is German prose (R63 already tested in-place) or a particular historically grounded German/clock inscription (not fully tested).
2. **H-DE-NL-ORTHO:** The *intermediate* pre-encryption stream is English deliberately written with German-/Dutch-looking spelling or sound-to-letter substitutions; it then undergoes a cipher and perhaps a transposition/mask. Scheidt's "English" statement remains potentially consistent, depending on what he meant by plaintext.
3. **H-DE-NL-LITERAL:** The final recovered plaintext is actually Dutch or German. **This conflicts with Scheidt's express English-language account** and is a lower-priority hypothesis, though not mathematically impossible if his account was incomplete or Sanborn transformed it.

**Negative R63 German running-key results do not test H-DE-NL-ORTHO.** R63's German is a **key-side** model; it scores the plaintext side as ordinary English. Prior project word scans in `docs/CIPHER_TYPES_TESTED.md` are narrower than a full, trained phonetic transducer combined with an independently derived cipher.

## 2. Period correctness and corpus domain shift

**R63 limitation:** its German key language model was trained on modern Europarl data. The [original Europarl release](https://statmt.org/europarl/index.html) covers parliamentary proceedings **1996–2011**, whereas K4 was prepared by 1990. A 20/20 well-designed synthetic detection gate validates *that frozen model family*; it is not proof of power on informal 1988 East German text, propaganda slogans, museum inscriptions, handwritten keys, or odd mixed-language word lists.

Potential independent, documented source families:

| Corpus / resource | Dating and genre | Value and constraint |
|---|---|---|
| [IDS DeReKo / Wendekorpus (1989–1990)](https://www2.ids-mannheim.de/cosmas2/projekt/referenz/archive.html) | Reunification-era German writing | Best temporal fit for a Berlin-related key. Verify exact source provenance, size and rights. If training here, **hold out different publication/author/date** for tests. |
| [IDS DeReKo metadata for Wendekorpus](https://repository.ids-mannheim.de/records/m10a2-a5718) | 1990, West German reunification-era text | Suitable historical resource discovery; an archive index is not itself a wordlist file. |
| [INT Dutch historical dictionaries, WNT 1500–1976](https://ivdnt.org/english/documenting-the-dutch-language/lexicography/historical-dictionaries/) | Historical lexicon and spelling variants | Good for historical graphemes and variants. A dictionary is *not* a representative probability distribution over 97-letter Dutch prose. |
| [INT historic Dutch corpora](https://ivdnt.org/historisch-nederlands/) | Includes 20th-century Eindhoven corpus | A better genre/period comparator than modern parliamentary Dutch; confirm actual sampled dates before use. |
| [Europarl publisher](https://statmt.org/europarl/index.html) | German and Dutch, 1996–2011 | Use as modern out-of-domain control and for engineering smoke tests, **not** as period-authentic key evidence. |

**Pre/post-1996 German orthography is a real issue.** The [German spelling council's official overview](https://www.rechtschreibrat.com/service/handreichungen/) documents the 1996 and 2006 reforms. A model trained only on post-reform `dass`, `muss`, `Fluss`, etc. can diverge from pre-reform `daß`, `muß`, `Fluß`. This difference must be measured, not inferred from one word. Older East/West spellings and city names on plates are potentially different again. Preserve the original source *verbatim* separately from any normalized A–Z stream.

## 3. German orthography: normalization is an operation, not a fact

Model at least two **pre-registered**, deterministic transformations from the actual source text to letters used by a 26-letter cipher:

- **G-DE1 (transliteration):** `Ä -> AE`, `Ö -> OE`, `Ü -> UE`, `ß -> SS`, then uppercase A–Z. This may **expand** one source character to two cipher letters.
- **G-DE2 (folding):** `Ä -> A`, `Ö -> O`, `Ü -> U`, `ß -> SS` (or separately document a `ß -> S` variant if historically warranted). This differs in length and may not preserve pronunciation.
- **Source variants:** `Koeln/Köln`, `Kiew/Kyiv`, `Leningrad/St. Petersburg`, compound-word segmentation, hyphen loss, numerals (spelled digits vs digit-to-letter encoding), regional spellings and improper umlaut stripping. These are *illustrations of ambiguity*, not proposed secret key fragments.

The choice of normalization changes both length and aligned keystream positions. **Never quietly normalize a test input**, especially when ciphertext must be 97 letters. Record a reversible source-to-stream provenance map and a loss/expansion audit; otherwise a negative exclusion cannot be reproduced.

German compounds (`Weltzeituhr`, `Uhrzeit`, `Zeitzone`, `Welt`) and city names require a separate tokenization model. A learned letter model may generate plausible *but unattested* names. A city-name sequence model is fundamentally different from a fixed, historically authenticated ring-read order.

## 4. Dutch orthography and likely confusions

Dutch and German both use Latin letters and share some Germanic-looking components, but are not interchangeable. In Dutch:

- `IJ/ij` is often treated as a digraph in orthography and can be a single linguistic unit though **two A–Z letters**.
- `OE` and `OU/AU`, `SCH`, `CH`, `EI/IJ`, `UI`, `EU` are useful *grapheme groups*, not universal English-to-Dutch replacements. They may be multiple letters per one vowel sound and differ across dialects/contexts.
- Dutch borrowed or regional spellings and German `SCH` do not prove the target was written with such a system. A phonetic generator must use a published or frozen transformation rule, not one chosen after looking at a K4 candidate.

[INT's dictionaries and lexica](https://ivdnt.org/english/documenting-the-dutch-language/lexicography/historical-dictionaries/) can establish authentic spelling alternatives. Use an explicit `source_language`, `date_range`, `genre`, `normalization_version` and `license` for every corpus. Without these, the model cannot be audited.

## 5. The more interesting hypothesis: English disguised by a *consistent* written code

A **testable** construction is a two-stage transformation:

```
English message (clean 97-char reference)
  -> fixed phoneme/grapheme transformation (Germanic-looking or other)
  -> optional length-preserving padding/shortening rule (if any)
  -> declared reversible cipher(s) / transposition
  -> 97-character ciphertext
```

Caution: if orthographic spelling **changes length**, it is not automatically possible to compare intermediate positions one-to-one with the published final plaintext positions. A valid model must specify **where** normalization, re-spacing, stripping, padding and any null mechanism occurs. Do not retrospectively insert/delete letters until known fragments line up. If reversible full 97-letter output is mandatory, establish a well-defined inverse transduction or carry enough side information to reconstruct the final English text.

### Recommended independent benchmark

1. First define a *small, finite* set of 2–4 phonetic/graphemic transformation families from general linguistic principles and pre-1990 published examples **without K4 clues**. Version and hash every rule set.
2. Generate at least 20 hidden English messages from **independent books** and 20 separate modern author-written messages (new sources unlike the original R59 text). Avoid composing control messages around K4's disclosed phrases.
3. Apply the Germanic text transform, then known random route and cipher parameters. **Hide both transform and key** from solver; if the transform is non-invertible, require faithful recovery of source English or an explicit ambiguity set, not just the intermediate stream.
4. Use null controls that match length, unigram composition, and preprocessing. Crucially add **wrong-language/transducer controls** and actual unseen 1988–1990 German or Dutch samples to measure false positives.
5. Report detection, recovered English letter accuracy, true transform identification, key and operator recovery, and error classes. Preregister a power gate before looking at target ciphertext.
6. Only if that gate passes, freeze raw full outputs and source manifest on remote Git before the separate published-plaintext check. A lucky resemblance in the first 97 letters must never cause model refinement in the same search.

### Negative-control pitfall

If every planted test uses **a single predeclared spelling rule** and the solver is provided that rule, successful recovery proves only that the cipher stage is solvable. To demonstrate the hypothesis can be **discovered**, vary the transformation and withhold its identity; include unseen spellings and registers. R63 recovered 10/10 German-text-key plants, but this is not power evidence for a disguised-English plaintext.

## 6. Decision table for future work

| Observation on genuinely hidden tests | Interpretation |
|---|---|
| Solver recovers ordinary English keys/normal plaintext but fails Germanic-masked messages | Linguistic masking requires a new decoder; R59/R63 negatives do not transfer. |
| High detection for actual dated pre-1990 German keys but not for K4 | Deprioritize that bounded source model only, not all alternate encodings. |
| Germanic decoder succeeds only on modern Europarl / ordinary dictionary words | Domain-overfit; **inconclusive** about 1989 manuscript/clock. |
| A model generates superficially readable English but can't reverse encrypted evidence | Fit, not a cryptanalytic solve. |
| English-looking output from K4 remains at null rank and unrelated to original source | No signal for that fixed family. |

## 7. Research verdict

**German/Dutch is worth preserving as an explicit, under-tested *masking hypothesis*, not as a demonstrated clue.** Scheidt's remarks give a strong reason to investigate frequency concealment generally, but **they do not single out a Germanic language**. Clock vocabulary is a historically motivated source class; literal German text in the key and deliberately altered English spelling are different mechanisms and should not share a negative-result label.

A high-value next step would be improving *the language and orthographic control design*, not manually reading arbitrary near-English K4 word salads through a German accent.
