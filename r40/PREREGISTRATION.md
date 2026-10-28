# R40 preregistration — Gromark IC unit-symmetry and max-score null calibration
Date: 2026-10-28. Base commit `00baaa94868103f5450f40f778bc866a0dc0da0d`.

## Purpose (before new null results)
Evaluate whether R39's K4 maximum key-conditional IC is distinguishable from the null distribution after searching the **entire 100,000-primer family**, and diagnose exact mathematical duplicate keys. This is a **blind ciphertext-only audit**, not a plaintext recovery and not evidence for any specific Gromark key.

## Hypothesis and exact equivalence
For key recurrence `k[i]=(k[i-5]+k[i-4]) mod 10`, multiplying the five initial digits by any unit `u in {1,3,7,9}` modulo 10 permutes every key digit through a bijection. R39's IC partitions ciphertext by *digit equality* only, so every member of the same unit-multiplication orbit has **exactly the same IC** on every ciphertext. Burnside's lemma gives `(100000 + 3*32)/4 = 25024` unit-symmetry orbits. There could conceivably be additional coincident partitions, but all 100000 primer settings are covered by these 25024 representatives.

The experiment must verify this equality and verify a fresh independent implementation reproduces R39's frozen K4 maximum `0.07510729613733906` and four tied top primers. Known K4 clue words and positions are excluded from the program.

## Predeclared empirical test
- Input: original fixed 97-letter K4 ciphertext, SHA256 including newline `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.
- Generate exactly **1,000** independently shuffled versions of the K4 ciphertext preserving its entire unigram histogram, using C++ `std::mt19937_64(40001)` and `std::shuffle` on an independent copy of the original text for each null. Output a SHA256 of inputs and executable where available; avoid claiming portable byte-identical shuffle across different C++ standard libraries.
- For K4 and every null, compute the **maximum** key-conditioned IC over all 25,024 unique unit-multiplication primer classes. Correct equal-pair counting (without ordering pairs) yields `sum_{d,c} n(d,c)*(n(d,c)-1)/sum_d n(d)*(n(d)-1)`; precomputed key-digit equality bitsets may accelerate exact counting. Verify the bitset numerator/denominator against a reference grouped-counter on predetermined sample primers/ciphertexts.
- Do not use any K4 clue, known plaintext, training corpus, language scoring, or tuned parameter.
- Primary statistic: `N_ge`, number of 1,000 null maxima **greater than or equal to** the original K4 maximum; report empirical Monte Carlo exceedance estimate `(N_ge+1)/1001` with its null-exchangeability qualification.
- Secondary: null max-score quantiles; number of distinct top-ranking unit-classes; a separate exact check of the 4-way tie.
- Interpretation: if K4's maximum is common under shuffling, the IC maximum alone has **no discriminating evidence** for Gromark on K4. Even if rare, a high value is not decryption evidence and cannot justify a K4 plaintext.
- No automatic external checker submission; disclose every result and any failed verification.

No conclusions from new 1,000-null experiment are known at registration.
