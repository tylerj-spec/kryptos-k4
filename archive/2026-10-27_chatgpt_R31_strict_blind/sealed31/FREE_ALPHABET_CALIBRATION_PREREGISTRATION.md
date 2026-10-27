# R31 diagnostic of blind decryption with two unknown alphabets (pre-registered)
The R30 code passes the 24 known clue letters to its solver. This diagnostic passes '????????...'(97) instead.
- Use unchanged solver_s2kp C++ with all '?' mask (zero crib information).
- Budget exactly 16 restarts / 40000 proposals / lambda 0.05 to 0, with fixed orthographic English model and quadgram table.
- Eight planted 97-letter messages (reference_messages.json calibration[0:8]), ciphertext independently encrypted under random unknown PA and CA, and key supplied to solver. Four are Gromark b5; four use random full-book Carter key windows. This is an *easier* diagnostic with the true key supplied, not a complete key-recovery calibration.
- Additionally examine only top 2 blind-selected G5 and top 2 blind-selected Carter keys on original K4. No keys from known-clue oracle are used. Search sees only original CT, key and '?' mask.
- All 12 raw outputs are frozen by SHA256 before any plaintext or crib checking.
- Planted success threshold readable <=5 wrong letters. Report 0/8 honestly if that occurs; no post-hoc changes.
