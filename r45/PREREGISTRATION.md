# R45 pre-registration — exact H-KW/Gromark feasibility audit of K4 (postfreeze; NOT a decryption)

Registered on 29 October 2026, against R44b's frozen success (commit `433572b9d78015c2411839ffa1d9da9dc19a044b`) and the previously frozen R39 *ciphertext-only* ranking. **Register and commit before looking at any R45 K4 result.**

## Research motivation

R44b correctly recovered 20 of 20 new planted, 97-letter messages with the **correct key supplied**, using a keyword-derived plaintext alphabet from the top-5000 English-model words (4,749 unique alphabets), and a completely free cipher alphabet. R44b does *not* identify a key. R39's independently frozen ranker produced zero K4 anchor-feasible primers among its top 1,000 (R40G), making a compute-heavy R44b sweep of those 1,000 an especially unproductive next test.

R45 performs a **separate exact necessary-and-sufficient 24-letter consistency test** on the full finite family, not a guessed-language search. It uses published K4 letters and thus is **crib-assisted / postfreeze** by construction. This check may *exclude* a narrowly defined model but cannot independently recover K4 plaintext or substantiate a positive K4 candidate.

## Hypothesis and scope (locked before results)

- Ciphertext: original unedited 97-character K4. Verify its SHA256 including newline as `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.
- Public constraint positions: zero-based 21–33 = `EASTNORTHEAST` and 63–73 = `BERLINCLOCK`, 24 letters total. Used **only in the sealed feasibility audit**, never to fill unknown plaintext.
- Permutation: **identity only**, no transposition.
- Keystream: each of the **100,000** five-digit decimal primers 00000–99999 with `k[i] = (k[i-5] + k[i-4]) mod 10`, including leading zeros.
- Arithmetic: BOTH signs `CA_rank(c_i) = PA_rank(p_i) + sign*k_i (mod 26)`, `sign=+1/-1`.
- Keyword list exactly as R44b: take the 5,000 highest log-score exact ORTH dictionary entries of lengths 5–10 (tie-break lexicographically), derive an alphabet by unique keyword letters followed by unused A–Z; expect **4,749 distinct alphabets**, identical to the R44b candidate construction.
- Evaluate BOTH orientations:
  - **H-KW-PA:** fixed keyword plaintext alphabet; cipher alphabet arbitrary one-to-one permutation.
  - **H-KW-CA:** fixed keyword cipher alphabet; plaintext alphabet arbitrary one-to-one permutation.

For any setting, the published letter relationships produce exactly a partial mapping from the 24 anchor letters to the unknown alphabet's ranks. A matching full permutation exists iff this mapping is a well-defined injection (same letter => same rank; different letter => different rank). This is **necessary and sufficient**, so a zero-count result excludes this exact finite model, *not* Gromark generally.

## Speed and independence guard

- Pre-screen all 100,000 primers with the already independently audited `key_oracle.possible()` over **both arbitrary alphabets**, separately for both signs. This pre-screen is a *necessary* condition for each keyword restriction and is **exact**. Cross-check the known historical K4 count of 39 for sign=+1; `+/-` should have the same count because reflection of both completely free alphabets changes the sign. Verify the main pre-screen independently on sampled controls before claiming any exclusion.
- Examine **every** pre-screen survivor, **all 4,749 alphabets**, both orientations and both signs. No ranking, key-shortlist, or language-model optimizer influences feasibility. Log exact pass counts and every passing (primer, keyword-alphabet, orientation, sign) setting.

## Controls and nulls (sealed, same checker)

1. **20 prior R44b holdout inputs**: reconstruct their 97-digit true key and each *published-from-the-plant* 24-letter mask; with the true keyword plaintext alphabet, all 20 must pass H-KW-PA for sign+ and independently re-encrypt exactly. These are already revealed and are used only as algebra unit controls; **do not count them as new holdout recovery**.
2. **20 mirrored positive controls:** independently generate 97-letter ciphertexts using keyword **cipher** alphabet and uniformly random plaintext alphabet, Gromark five-digit primers and both signs, and check H-KW-CA on the same 24 positions; every true configuration must pass and re-encrypt exactly.
3. **4 nulls:** independently shuffled K4 ciphertexts preserving exact letter frequencies (fixed seeds 45100–45103) evaluated against the *original public anchor positions* using exactly the same primer and alphabet family. These do not have an intended true plaintext; report null pass counts without cherry-picking.

Output must include full K4 pilot counts, keyword-list digest, actual candidate list (not just minimum), control pass totals, null counts, and method/source SHA256. Retain every failure. Do **not** contact an external Kryptos checker.

## Decision rule

- **0 K4 settings over both orientations and signs:** classify `EXCL` for *identity-route, decimal five-digit Gromark, ± operation, one R44b keyword alphabet and the other unrestricted*. This is a known-letter exact contradiction, **not a strict-blind K4 solve**.
- **1 or more K4 settings:** classify `FEAS` only. Their apparent published 24-letter agreement is tautological and **not evidence** of genuine plaintext; do not automatically run a fitted decryption or claim a K4 candidate.
- A worthy K4 solution requires a separately pre-registered original-ciphertext-only decryption run, frozen raw 97-letter output before revealing known letters, plus independent re-encryption and control recovery.
- If this family is excluded, prioritize changing **key family** or **transposition order** rather than spending hours rerunning the excluded R39 keys.

This preregistration reports no R45 results.
