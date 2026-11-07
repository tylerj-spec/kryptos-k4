# Cryptographic method atlas and evidence-driven experiment design

**Purpose:** identify what forms of K4's reported English-statistics **masking** remain consistent with the physical/historical record and what experiment would actually *discriminate* between them. This is research and design, **not** a solver, candidate key or K4 decryption.

Sources: [Scheidt's interview](https://www.wired.com/2005/01/inside-info-on-kryptos-codes/), [CIA](https://www.cia.gov/legacy/headquarters/kryptos-sculpture), [Friedman historical manual catalogue, NSA](https://www.nsa.gov/Helpful-Links/NSA-FOIA/Declassification-Transparency-Initiatives/Historical-Releases/Friedman-Documents/Publications/), [Shannon 1949](https://doi.org/10.1002/j.1538-7305.1949.tb00928.x), [OTP definition](https://mathworld.wolfram.com/One-TimePad.html), and local `docs/CRYPTOGRAPHY_REFERENCE.md`, `docs/CRYPTANALYSIS_METHODS.md`, `docs/CIPHER_TYPES_TESTED.md`.

## 1. What the K4 evidence actually constrains

- Original ciphertext = **97 letters**, all 26 symbols present. A verified source file and SHA exist in `r39/ic_gate/k4_ciphertext.txt`. No formatting, line-wrap or inferred omission should change that byte stream.
- Local `docs/CIPHER_TYPES_TESTED.md` reports **index of coincidence 0.0361** vs uniform random 1/26 ≈ 0.03846. At **n=97**, a slightly subrandom IC is not proof of a true OTP; it indicates no obvious simple monoalphabetic/pure-transposition footprint. Sampling variance matters.
- A pure transposition preserves the complete letter-count multiset. That is **incompatible with ordinary-English frequency reconstruction under the authenticated plaintext checks** within the scope in the ledger; it may be one *layer* but cannot explain flattened counts by itself.
- Scheidt said he deliberately masked the **statistical availability of the English language**, and suggested the masking technique might not be standard. This is **evidence for masking of some sort**, but not that K4 uses a particular one of: homophony, phonetic spelling, nulls, wheels, running key, or external codebook.
- K4 is short. Simultaneously optimizing a free plaintext, an arbitrary 97-position key, a route and one or more unknown alphabets is underdetermined. The ability to derive a 97-letter key *from any proposed plaintext* is not evidence. Require independent constraints on the key generator.

## 2. Distinguish the stage order before testing keys

These processes do **not** commute:

- **Substitute then transpose (S→T):** `X[i] = S(P[i],K[i]); C[j] = X[perm[j]]`. Reversing the route exposes the original substituted stream, then a letterwise running-key solver can be used. R61 tested this with an **English** key for ten route families.
- **Transpose then substitute (T→S):** `X[j] = P[perm[j]]; C[j] = S(X[j],K[j])`. An ordinary letterwise solver can extract scrambled plaintext `X` but English scoring on `X` is invalid; the route must be incorporated in decoding/scoring. R61 did **not** test this family with unknown free keys.
- **Mask then substitute or transposition:** `P -> M(P) -> S -> T`. The model can make English invisible at the letter statistics stage while preserving semantic English upon inversion. Define the mask's reversibility and length behavior.
- **Substitute then mask:** `P -> S -> M -> T`. Could look similarly flat, but a mask on ciphertext is a different operator with different expected signatures.
- **Codebook and multi-stage semantics:** a word/phrase can encode a concept before or after ciphering. Without an independently specified lookup source and inverse rule, arbitrary dictionary guesses are untestable.

**Invariant audit before any K4 run:** specify whether length is preserved at each stage, which alphabet each operator maps, which state is updated after each letter, whether separators and skipped/null characters consume key positions, and whether an operator is bijective. Treat these as preregistered parameters, not adjustable artifacts after seeing a clue mismatch.

## 3. Mechanism families relevant after R59/R61/R63

| Family | Why it can conceal English statistics | Testable signature or control | Scope in this repo |
|---|---|---|---|
| Running key (two texts) | Full-length key can flatten frequencies | Independent texts from same source/genre should score apart from shuffled controls if solver has power | R59/R62B (English in place), R61 (English S→T, ten routes), R63 (clock-city / German **in place**) all no K4 signal. **German/clock with T remains open**. |
| OTP / truly uniform one-time key | Perfect-secrecy construction suppresses all plaintext statistical evidence | Cannot uniquely decrypt ciphertext-only without independent key provenance; test only physical/source derivation, not arbitrary 97-shift fitting | Open; do **not** label "ruled out" or "solved" based on null scores. |
| Homophonic substitution | Multiple cipher symbols can encode one plaintext symbol, flattening output | Fit synthetic 26-symbol homophonic systems with source-derived tables; compare true-message recovery and letter totals | No complete authenticated 26-letter K4 test found in main inventory. |
| Null insertion/deletion / irregular padding | Preserves secret message but scrambles lengths and phase | Test hidden inserted/skipped positions, independently chosen schedules; recovery of both plaintext and deletion map | Periodic/bounded variants tested; general **mask open**. K2's corrected missing character is historical motivation, not proof for K4. |
| Deliberate spelling/phonetic recoding | Makes ordinary English language models fail, may alter letter counts | Hidden-English-to-masked training data, explicit transducer and inverse, wrong-language controls | Germanic-like scans exist (L62–L69), but not a validated multi-stage decoder spanning authentic spellings and variable lengths. |
| Free alphabets / mixed alphabets | Arbitrary tableau order obscures simple known-alphabet statistics | Planted recovery with **two independently unknown alphabets and unknown key**; reject overfitting | R44b's known-key synthetic recovery 20/20 is **not** a K4 unknown-key test. |
| Evolving wheels/rotors | Stateful substitution changes effective alphabet by position | Reconstruct full state transition with reversible controls and independently derived starting state | Standard Chaocipher-like R56 bounded negative; free wheels/other stepping remain open. |
| Polygraphic/fractionation + layering | Redistributes per-character statistics; nontrivial symbol groupings | Exact invertible operator and all-position witnesses; compare alphabet constraints first | Hill, Trifid, Playfair etc have bounded exclusions. Do not generalize to every 26-letter adaptation. |
| Interrupted keys / irregular reset | Produces no short global period even if local repeats exist | Plant random visible/hidden reset schedules, recover segmentation without truth | General irregular reset under-tested. |
| Position-dependent sculptural mapping | Physical 24-panel/compass/text grid changes read order or keystream | Independently authenticated mapping, grid orientation and no invented coordinates | World Clock historical source incomplete; R61/R62C physical COL_LT anomaly is post-selected, not mechanism proof. |
| Two independent ciphers / nested code | Whole-stream statistics may not identify individual layer | Predefined inverse chain with stage-internal control checks | General layer pairing remains open and combinatorial. |

## 4. The one-time-pad question

A **true OTP** uses a uniformly random, independent, single-use secret key with at least as much information as the message. For such a scheme, **any 97-letter candidate English plaintext has some corresponding full-length key**, so reverse-fitting one proves nothing; Shannon's [1949 result](https://doi.org/10.1002/j.1538-7305.1949.tb00928.x) explains the fundamental ambiguity. The [MathWorld definition](https://mathworld.wolfram.com/One-TimePad.html) gives the necessary conditions.

A hand-generated stream, clock reading, book text or 97-letter phrase is **not** automatically a true OTP just because it is nonrepeating. Those are structured running/algorithmic keys and have detectable biases in principle.

Useful falsifiable OTP-adjacent question: **Can a historically justified, independently obtained 1988–90 source generate exactly the required key stream under a previously documented rule?** Without that source, a null-looking ciphertext is not enough.

## 5. Formal tests and statistical hygiene

A small proportion of published letters matched by chance is normal:
- With an unrelated uniform 26-letter candidate, expected matches to a fixed 24-letter validation set = `24/26 ≈ 0.923`; 0–4 is unremarkable.
- Even for a correctly generated 97-letter encryption witness, **forward encryption establishes arithmetic consistency only**. If the key was inferred from the proposed plaintext or fitted known fragments, the witness gives no independent evidence.
- A shuffled-letter control **preserves frequency** but not language/spacing or artist process. It is a reasonable null for many ciphertext-only scores, not a universal sample from an alternative cryptographic hypothesis.
- The strict empirical `(r+1)/(N+1)` tail with **100 shuffled nulls** has minimum nonzero value **1/101 ≈ 0.00990** when none exceeds the target; with 300, **1/301 ≈ 0.00332**. Two simultaneous key models and ten route searches create *selection/multiple-testing costs*.
- R61's `COL_LT` score gap was *noticed after viewing K4*. R62C's 300 fresh shuffles (2/300 >= historical gap; plus-one 3/301) support a targeted structural anomaly under the new fixed null, but **do not reverse the original post-selection**. The 20 alternate-route families are correlated. This is not a validated physical decoder.

**Predeclared multi-axis gate:** score/rank detection, correct route and convention, true 97-letter accuracy on hidden plants, key/source recovery, complete forward witness validity, and null/alternative-family calibration. Specify exactly what is being excluded if a gate passes and K4 has no signal. An unsuccessful power gate is **INCONCLUSIVE**, not "family mathematically impossible."

**Blind generative independence:** all development and holdout messages must be newly sampled with source hashes and no K4 disclosed clue phrases (the four R63 numeric-key planted controls did include clue phrases as synthetic truth; do not use them as a claim of generic-message generalization). The blind solver must never receive those words/positions even indirectly via scoring or input choice.

## 6. Evidence to collect before writing another broad solver

A ranking by **information added per experiment**, not by ease of CPU execution:

1. **Historical/authenticated physical source:** full pre-1990 World Clock face text and hour-band mechanism, original Kryptos photographic transcription, original 1990 setup orientation. Those data constrain key hypotheses more strongly than million-key brute forcing.
2. **Generative masking model** with independent reversible controls: choose one plausible finite operator with behavior unlike R59/R61/R63, and show it can be recovered *from ciphertext* without hidden truth.
3. **Non-English key + transposition** as the nearest cheap, bounded experiment. The current review-only `PR #45` sketches R64; it must become a real preregistration before holdouts/K4.
4. **Alternative operator order** T→S, especially because R61 tested only S→T and the English text model may be applied at the wrong stage.
5. **Two unknown alphabets** and irregular/interrupted key selection only when hidden-planted power exists.
6. **Stop if constraints are insufficient:** if every candidate is compatible under an unconstrained key, state "underdetermined," acquire evidence, and decline a manufactured plaintext.

## 7. A compliant result standard

**Never fit plaintext to known K4 letters.** Freeze raw complete outputs, parameters and source hashes in a verified **remote Git commit** *before* the sealed postfreeze checker runs. Then require: correct original ciphertext; independent forward re-encryption; all published letters at fixed offsets; coherent and independently recovered non-anchor text; real source derivation for every key/route step; control power; statistical correction for search breadth; external checker only for independently produced, fully frozen candidates if user authorizes that specific check.

Nothing here claims to identify the encryption algorithm. This prevents *false success* and highlights which operator has a genuine chance to be distinguished.
