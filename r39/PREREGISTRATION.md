# R39 — Can a Gromark primer be found without either alphabet or K4 plaintext?

Pre-registered before the planted trial. Richard Bean's *Cryptodiagnosis of Kryptos K4* (HistoCrypt 2021, DOI 10.3384/ecp183153), citing Blackman's 1989 Gromark work, describes ranking five-digit Gromark primers via the **index of coincidence of ciphertext grouped by key digit**. This technique is meaningful even when both cipher and plaintext alphabets are unknown, because the same digit acts as one fixed substitution in its group. We test whether it actually works at K4's short length of 97.

## Exact blind ranker

- For each of all 100,000 base-10, five-digit primers, recursively expand `k[i]=(k[i-5]+k[i-4]) modulo 10`.
- Partition the ciphertext's 97 positions by the ten numeric digits of that key; no ciphertext-to-plaintext comparison or alphabet guessing.
- Define `IC(key) = sum(d,c) n(d,c)*(n(d,c)-1) / sum(d) n(d)*(n(d)-1)`, where n(d,c) counts ciphertext letter c at positions with key digit d, n(d) is group size.
- Rank by decreasing IC, tie-breaking by ascending five-digit numeric primer. Freeze the full 100,000-score vector as binary float64 and the top 100 ranks. **No clue masks, known K4 words, word models, transposition, or keyword guesses are present in the blind ranker.**
- Scan exact original 97-character K4 ciphertext (SHA256 `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`) using the same procedure as every control.

## Hidden planted controls

- 20 unrelated 97-character English messages: 4 from original `r35/controls.json` passages; 16 fixed pseudo-random windows from the previously solved K1-K3 plaintext (not K4 text). Normalization strips spaces; explicitly assert none contains the K4 published clue phrases.
- A completely random secret A-Z plaintext alphabet, a separately random ciphertext alphabet, a random uniform five-digit Gromark primer and standard VIG shift for *each* control. Random seed for control generation: **39000**. Only ciphertext files are exposed to `r39/blind`; secret 20 primers and two alphabets held in `sealed/truth.json`.
- 10 independently shuffled ciphertext null controls, seeds 39100–39109, retaining original K4 ciphertext letter counts. These only calibrate max IC against the original K4 (descriptive, not formal p-value at n=10).
- 31 blind runs, 3.1 million total primer scorings. No early exit; every rank is recorded.

## Decision rule declared before evaluation

- The method passes its **development gate** only if at least **16/20 planted true primers** are in the top 5,000 of 100,000 and the median planted true-primer rank is **at most 1,000**. Otherwise the key-ranked K4 output **cannot be used as a trusted shortlist**.
- After all blind output hashes are committed to GitHub, a separately coded checker recomputes 10 sample scores per file from the frozen ciphertexts, re-encrypts each planted truth with its secret alphabets and key, and reports the exact true-primer rank in the frozen full score array.
- If the gate passes, record K4 top100 numeric primers as candidates for future *independent* two-alphabet search only. High IC alone never implies a K4 solve. If gate fails, report a negative key-ranking result and don't infer anything about K4's actual unknown key.
- No known K4 plaintext used at any stage (not even post-freeze for this key-only development experiment); no external verifier. The unconditional outputs and full negative trials remain auditable.
