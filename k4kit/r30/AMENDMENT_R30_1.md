# R30 amendment 1 (Claude Code, 27 Oct 2026, written after C2 and before looking at any E3 K4 output)

`PREREGISTRATION_R30.md` (sha256 9ebe8081…2c86) is unchanged.

## 1. E3 gate failed, and its scope shrinks
- **C2 result:** ORTHXQ blind readable **10/22**, below the gate of 11/22. ORTH reached 11/22 on the same punctuated
  fixtures. On the 20 unpunctuated R21 passages, ORTHXQ reached 12/20 against ORTH's 15/20.
- **Consequence:** the punctuation rule adds no recovery power, so every E3 K4 run is **exploratory**.
  - (a) and (b) had already run when the gate result was read (the chain runs them right after C2). They are
    reported as exploratory; their outputs had not been viewed when this amendment was written.
  - **(c) and (d) are dropped.** They have no calibrated value, and the compute goes to E5.
  - The ORTHXQ bar would have been max(−114.9, −117.79) = −114.9.

## 2. E5 (new): carving-error robustness for 5-digit Gromark (handoff T6, ledger L35)
- **Model:**
  - One of the 24 clue-position ciphertext letters is assumed mis-carved, so its clue equation is dropped.
  - Two-free-alphabet 5-digit Gromark, in place.
- **Oracle stage:**
  - For each clue position d (24 values), test all 100,000 primers against the clues without d.
  - New settings are the (d, primer) pairs that pass without being among the 39 full-clue passes, which are
    already searched.
- **Budget:** fixed after the oracle stage and before any English search. Search all new settings if there are at
  most 8,000; otherwise search the 8,000 whose dropped clue leaves the most crib cycles, ties broken by d then
  primer.
- **Search:**
  - ORTH, with the clues minus d enforced. Screen at 16 restarts; the 20 best by W are replicated at 64 restarts
    with new seeds.
  - The candidate rule is unchanged (W > −114.9 and the replication within 5 letters).
- **Calibration C5:**
  - The 20 R21 passages, each encrypted with a random primer and random alphabets (seed 30005).
  - The ciphertext letter at one random clue position is replaced by a different random letter.
  - The solver gets the true primer and the clues minus that position. Report readable at 16 and at 64 restarts.

## 3. Run order from here
E1 ORTH, E2 ORTH (both unchanged from the protocol), then C5 and E5.
