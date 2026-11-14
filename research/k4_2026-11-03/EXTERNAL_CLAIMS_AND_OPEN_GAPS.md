# External solution claims, code-talker analogy, and open research leads

**Research-only, not a solver and not a K4 plaintext source.** Do not copy guessed plaintext from any external website into a local candidate generator. The only accepted K4 input to a new blinded solver is the original ciphertext from `r39/ic_gate/k4_ciphertext.txt`.

## 1. Distinguish four claims that online searches often confuse

1. **A full answer string was located:** a Smithsonian document or private archive disclosed the actual answer. This is historical document discovery, **not** an independent ciphertext-only decryption.
2. **A decoder can be made to produce a desired string:** an analyst chooses a key, table, alphabet or mask after seeing the target answer. This is **fitted explanation**, not evidence of the artist's original method.
3. **An independently derived process recovers a frozen complete text:** from ciphertext plus an authentic, independently justified source and a predeclared algorithm; a strong cryptanalytic *candidate* requires forward encryption, heldout power, no clue fitting, all released clue compatibility and new coherent plaintext.
4. **The original artist's algorithm/key source is reconstructed:** requires documentary provenance, unambiguous parameters and an independently reproducible method. A correct answer string alone, including a paid validation response, does **not** establish this.

The 2025 archival case is (1). In [Scientific American's report](https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/) and [WIRED's account](https://www.wired.com/story/kryptos-code-reveal/), Jarett Kobek and Richard Byrne found the K4 plaintext in Smithsonian materials and Sanborn confirmed that answer, but they did not recover it by deriving the cryptographic method/key.

[Paradigm's June 12, 2026 announcement](https://paradigm-vc.vercel.app/2026/06/kryptos) describes a full-solution SHA-256/HMAC-based checker and a $1 fee. It is potentially relevant **only to checking a candidate after a successful remote freeze**; its site does not establish the provenance of that candidate's method. No submission, paid query, or feedback loop was performed in this research.

## 2. Internet reconstructions and false-confidence checks

- **[SolveKryptos.com proposed mechanism](https://solvekryptos.com/method)** describes a multi-step Quagmire-related explanation. Its own methodology includes cards/lookup values **back-solved from an assumed answer** (the published site discusses 45/97 and a later smaller subset). Therefore its claimed forward-encryption coherence does not meet this repository's R53 rule: the generator/key must not be fitted to the target plaintext. Archive the link as **a claim requiring an independent blind reconstruction**, not an accepted solution, key source or plaintext.
- **[KryptosBot research-position report](https://github.com/jcolinpatrick/kryptos/blob/main/docs/REAL_K4_CURRENT_POSITION.md)** is another project's candid accounting of failed/limited models. It can expose ideas to reproduce but should not be merged into the ledger as exclusions until its ciphertext source, fixtures, full 97-letter outputs, source hashes, search breadth and evidence are verified locally.
- **[External negative-space analysis](https://github.com/nitsuah/kryptos/blob/main/docs/analysis/K4_NEGATIVE_SPACE.md)** likewise highlights that large-count enumerations may leave the actual artist's process untouched. Counts of trial settings, by themselves, do not establish cryptanalytic relevance.
- **[Independent Kryptos research notes](https://kryptos.tiki.vc/research.html)** may be useful for provenance pointers and the community's historical attempts. Distinguish the author's speculation from direct Sanborn/Scheidt testimony.
- Any alleged 2025/2026 "solved" headline should be checked for whether it means **plaintext obtained in archive, ciphertext-only recovered plaintext, unpublished proprietary confirmation, or derivation of the key and method**. These are very different statements.

### A quick credibility rubric for a newly proposed solve

Require:
- An **unaltered 97-letter original input** and a fully specified transformation;
- A *source-derived* key, alphabet or mechanical mapping **chosen before reading the proposed answer**;
- No published K4 plaintext fragments, offsets, or previous checker feedback in the generator, scoring, parameter selection or training exemplars;
- Full decrypted text and independent **forward-encryption witness**;
- Pre-reveal remote Git commit containing inputs, raw alternatives, source code/model/executable hashes and parameter provenance;
- An actual coherent independently produced new passage and proper all-clue compatibility **only after freeze**;
- Nontrivial hidden planted-message recovery and false-positive rates on matched null controls;
- Explicit look-elsewhere accounting and failure disclosure.

A process that lets the operator freely choose 97 key symbols cannot be validated merely by showing that it reproduces a desired English sentence. That is exactly the expected mathematical behavior of an unconstrained 97-position stream.

## 3. The Navajo Code Talker analogy: useful mechanism, not historical K4 evidence

The user's analogy to the Navajo Code Talkers points to a broader possibility than the spelling of English in a German accent.

[US National Archives teaching resources](https://www.archives.gov/education/lessons/code-talkers) and the [US Navy's historical Navajo code-talker dictionary](https://www.history.navy.mil/research/library/online-reading-room/title-list-alphabetically/n/navajo-code-talker-dictionary.html) describe at least **two distinguishable processes**:

- A **natural-language barrier**, where outsiders hearing unfamiliar language cannot straightforwardly recognize words;
- An additional **conventional code**, including assigned vocabulary for military concepts and words used to represent Roman letters. A native Navajo speaker with no codebook would not automatically understand every military term.

This suggests *researchable analogues* but is **not** evidence Sanborn copied military code-talkers:

- **Layered linguistic codebook → enciphering:** map English concepts/words to a small independent vocabulary, strip punctuation, then run a cipher. The recovered intermediate may read as a strange foreign-looking code, while the final message is English.
- **Acrophonic/initial-based enciphering:** source-language names represent letters or syllables. The decoder needs a frozen, independently obtained symbol vocabulary; manually deriving a dictionary from desired K4 output would be circular.
- **Phonetic transduction:** write English sound patterns through a deterministic unfamiliar orthography then encrypt. Unlike a codebook, this can cause spelling/length changes, which need a reproducible inverse.
- **Source-language key:** German prose or World Clock city names serve as a keystream but plaintext remains ordinary English, as R63 modeled. This does **not** test the three other processes.

**Discriminating control proposal:** independently create new English phrases *never containing K4 released fragments*, encode them with one of several source-dated codebooks/transducers, hide both the true codebook identity and the cipher method/key from the solver, and test whether it can recover the full new English on genuinely unseen messages. If it only recognizes encoded text when the dictionary is supplied as truth, that is weaker capability evidence.

## 4. Genuine open documentary questions

| Question | Existing evidence | What would settle it |
|---|---|---|
| What did Sanborn mean by an "unknown" masking technique? | Scheidt's 2005 direct interview describes frequency-statistics masking but **does not specify an operator** | Dated direct interview, independent working manuscript, legitimate access to Scheidt technical notes, or a reproducible matching construction |
| Was German/Dutch actually used? | Location/clock/visitor context and the user's idea, **not a creator statement** about language family | Original design-era key source or a blind control-powered recovered Germanic-like intermediate with all other steps derived |
| What was physically on the 1989 clock? | At least two incompatible original city counts, post-1997 replacements | 1969 original design drawings + complete pre-1990 plate inventory/photographic orbit |
| Could a clock-based date or hour index be a deterministic stream? | Clock has 24-zone panels and rotating hour display | Original operating/gear details and independently fixed date, phase and start position |
| What is the proper ciphertext/transcription? | Repository's SHA-pinned 97-letter canonical stream; known K2 missing-letter episode | Direct photographic cross-check of all original K4 copper letters, with disagreements logged |
| Is there enough information to recover a true OTP key? | K4 letter frequencies look near random, but this is not decisive | Independently obtained key material/source. Without it there is no unique ciphertext-only decryption. |
| Does masked English require variable-length text? | Linguistic transducers may expand `Ä` to `AE`, `IJ` to two letters, and so forth | A fixed end-to-end inverse that reconstructs coherent 97-letter output on hidden controls |

## 5. How to use external checks without contaminating discovery

External resources and historical articles may inspire **model-family selection**; public clues may inspire the *class of source* (a clock is okay), per the owner's clarification. They must **not** supply the literal validation letters or their positions to the generator. A future paid/public checker can be used on **a frozen candidate only** if permitted in that experiment's preregistration and by the owner. Repeated query feedback used to tweak keys would contaminate blind claims.

No external site in this research provided a verified independent cryptographic solve of K4. This is **not** an assertion that such a solution can never exist; it is the boundary of the sourced evidence reviewed here.
