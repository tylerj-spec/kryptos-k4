# R47 pre-registration — non-Gromark running-key sources × keyword/free alphabet families

29 October 2026. Registered on top of R45's already frozen `1aa8fb3285a959bbfd656e2978024249e9f6a49b` exclusion, **before** running any R47 K4 analysis. Independent of pending R46 rotations.

## Exact changed hypothesis

R45 ruled out the original direct five-decimal-digit Gromark recurrence with 4,749 common-keyword alphabets, both signs, and either the keyword-PA/free-CA or free-PA/keyword-CA orientation. R47 preserves **identity position order** and those two substitution-alphabet models but REPLACES the numeric Gromark key with full 97-letter windows from two independently defined, historically motivated text streams:

1. `k4kit/data/k1k3_plaintext.txt` (the plaintext of Kryptos K1–K3, including artist spelling).
2. `r34/carter_az.txt` (the already pinned Carter & Mace 1923 book text, as historically discussed in repo research).

For each source strip non-A–Z characters and uppercase ASCII. For each window of 97 letters including offsets 0 through `len(text)-97`, test **four key variants**: source forward/reversed (reverse the *whole normalized string*, not individual windows) × letters numbered by alphabet AZ or KRYPTOS. Each key is a sequence of 97 mod-26 integer values, not necessarily decimal digits. Test **both** `+k` and `-k` operations.

For each source/variant/window, test:
- H-KW-PA: plaintext alphabet is one of the exact 4,749 R44b common-word keyword alphabets; ciphertext alphabet any permutation.
- H-KW-CA: ciphertext alphabet is one of those 4,749 keyword alphabets; plaintext alphabet any permutation.

Each family is in-place only, with the original untouched 97-character K4 ciphertext; no transposition, null insertion or plaintext guessed. The source texts, word model and K4 bytes must be SHA256 fingerprinted. All source windows, both directions, both numbering alphabets, both arithmetic signs and both keyword orientations must be covered — no unreported shortlist.

## Method and evidence boundary

This is an **exact, sealed, postfreeze, 24-public-letter consistency test** only. As in R45, the already independently audited `key_oracle.possible` applies the full **two arbitrary alphabets** feasibility condition to each keystream, before the narrower exact checks of every keyword. Pre-screening is mathematically sound because every keyword/free setting belongs to the two-arbitrary-alphabet superset.

Anchor constraints: `EASTNORTHEAST` at zero-based 21–33, `BERLINCLOCK` at zero-based 63–73, used solely to ask whether a complete 26-letter permutation exists. If a key/keyword survives, it is `FEAS` **by construction, not independently decrypted plaintext**. We will NOT run a fitted solver on that short list and call 24/24 agreement evidence.

## Controls, nulls and reporting

- Positive controls: 20 already revealed 97-letter R44b English passages. Independently choose key windows from both text sources, both source directions and alphabets, both signs, both keyword-orientation cases. Encrypt with complete arbitrary counterpart alphabet and test that the exact oracle admits each true setting, and the complete independent forward-encryption equals the synthetic ciphertext. At least 10 controls per orientation and exactly 20/20 must pass.
- Nulls: exactly **two** shuffled copies of the original K4 ciphertext preserving all 97 letter counts (fixed seeds **47100** and **47101**), run through the **same full** key-source/variant/window/keyword family with the K4 public anchors.
- For K4 and each null, list the number of full key windows enumerated, the exact number passing the two-free-alphabet prescreen, keyword-PA and keyword-CA feasible counts, and **every viable (source,direction,numbering,offset,sign,orientation,keyword)** setting (untruncated). Never present 2 nulls as a calibrated statistical p-value.
- Record the 40-character original K4 and both source digests, ORTH model digest, preregistered protocol SHA256, program digest, and full raw output digests, committed on the R47 review branch with GitHub Actions logs/artifacts.
- The experiment must stop on missing sources or mutated frozen R45 result; do not consult any external K4 checker.

## Decision

- Zero K4 viable settings: `EXCL` only these TWO full source streams, all 97-character windows and four numbering/reading variants, BOTH signs and both keyword/free substitution arrangements, identity route. Do not infer other manuscripts, editions, physical enciphering aids or transpositions are excluded.
- One or more settings: `FEAS` only; not a blind K4 solution. Investigate separately with fully blind candidate generation before reading known words. Never mistake a crib-assisted 24-letter fit for an independently recovered 97-letter text.

R47 is a distinct family from R45 and R46. No R47 K4 results are known at registration.
