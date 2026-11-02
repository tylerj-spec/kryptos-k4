# Primary-source correction and stronger historical evidence (1 November 2026)

This addendum changes **no** algorithm, preregistration, hidden control, cipher selection, ciphertext-only output, or after-freeze evaluation. It was written after the R60 experiment and is a historical-context addendum, NOT evidence that R60 decrypts K4.

## Contemporaneous 1991 evidence outweighs guesses about invented language masks

**Associated Press, Robert M. Andrews, 28 April 1991**, syndicated in the Los Angeles Times, [“Sculpture With Code Poses Mystery at the CIA”](https://www.latimes.com/archives/la-xpm-1991-04-28-mn-1468-story.html):

- Sanborn gave Director William Webster **two sealed envelopes** at the 1990 dedication, described as one containing a **translation of the message** and the other containing **“key words required to break the code.”** This was near-contemporaneous reporting; we do **not** know whether the envelopes' keys were specific to K4, covered the entire sculpture, or whether AP's wording compressed distinctions in the original conversation. Do not infer an actual K4 key from this source.
- Sanborn independently cautioned that the meaning of the decrypted text would remain a mystery: decipherment and final **interpretation** are different tasks. He framed the engraved text as clues to a **larger mystery**. That supports looking for semantic/physical interpretation *after* cryptographic recovery, but does **not** establish a private Code Talker-style dictionary, a German or Dutch spelling convention, or an encrypted full-language substitution.
- The 1991 article also floated a possible prominent fiction-writer collaborator, but Sanborn later said the author collaboration **never happened** ([Elonka Dunin's Sanborn Q&A](https://www.elonka.com/kryptos/faq.html)); do not treat the CIA's unrevised collateral wording or the early interview as proof of an external literary author/key source.

**CIA, official Kryptos sculpture overview**, [CIA original institutional account](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/):
- CIA separately preserves Sanborn's distinction between readable writing and unresolved meaning; it gives K4's exact **4/31/31/31 physical inscription layout** and the flipped tableau, but never authenticates the K4 cipher or any language mask.
- The 1991 source's key-word description is a stronger reason to investigate **independently documented keyword generation or placement rules** than to assume a truly random 97-letter one-time pad. A word-key report does NOT mathematically rule out a pad-derived key, nonperiodic cipher, or an additional physical layer.

**Ed Scheidt, January 2005 WIRED interview**:
- In the question specifically about K4, he explained that he disguised conventional **English statistical patterns** and said the technique might not be publicly known.
- His innocuous word **cake** analogy came in a separate question about an *already decoded* passage. Applying that analogy to K4 is a hypothesis, not a confession about the K4 method.

## Distinguish two owner ideas without forcing an interpretation

The owner's references to Dutch/German can plausibly refer to:
1. **Phonetic English with Germanic-looking graphemes** that an English speaker can *sound out* without knowing German or Dutch, NOT a fully German/Dutch message and NOT standard English spelling.
2. **English text with hidden codeword meanings**, like a Code Talker-style private vocabulary.

These differ. R60 tested **(2)** as a cryptanalytic identifiability problem; it did not test **(1)**, although Claude/ChatGPT earlier explored partly related Germanic-respelling scoring in canonical ledger L45, L51 and L62–L71 (including weaker recovery on unfamiliar spelling rules). Do not imply that R60 rules out Germanic phonetic masking.

Neither a semantic dictionary applied *after* decipherment nor straightforward phonetic English on its own guarantees uniform-looking frequencies. Original K4's IC 0.03608 and genuinely unknown cipher process still require independent attention. R58's failed tableau+physical routes and R59's uninformative OTP-compatible p=0.340 do not identify any mechanism.

## Specific next experiments worth considering

- **Phonetic branch (if independent historical writing rules emerge):** new held-out passages with graph-to-sound transformations and *previously unseen* Germanic-like spellings, then truly unknown cipher-family and key recovery. Score pronunciation/recoverability separately from letter-level decryption; do NOT tune rules using the released K4 words or a lucky high-scoring K4 output.
- **Cipher/key branch:** study contemporary field-agent pencil-and-paper keyword systems and sculpture layout that are demonstrably accessible to the creators in 1988–1990. Establish a compact forward rule and actually unknown keys, preregister, then test hidden keys/families; after passing, search original K4 unmodified ciphertext alone. Exact re-encryption and 24 postfreeze known letters are necessary. A 97-character arbitrary fitted shift array is never an independent key.
- **Meaning branch:** once a **real** 97-letter recovered plaintext exists, investigate historical/semantic references independently. Don't invent codebook senses and score them as if they were ciphertext evidence.

**Status:** source review only; no K4 plaintext or key obtained. R60 negative-scope / positive synthetic controls unchanged. 
