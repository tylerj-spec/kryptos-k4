# R30 amendment 3 (Claude Code, 27 Oct 2026): more search power for E4 (Carter book)

**Run as pre-registered.**
- 585 oracle passes, against 20 letter-shuffled copies: median 477, max 527.
- 16-restart screen best W −142.25. The top 20 were replicated at 64 restarts. No candidate.
- At 16 restarts, planted recovery is only about 45% (C1: 9/20; C3: 9/20).

**Added before looking at any further output:**
1. **Full power on every pass.**
   - All 585 passes are re-searched at 64 restarts with new seeds (labels + `"|full64"`), which raises planted
     recovery to about 60–75% (C1 12/20, C3 15/20).
   - The candidate rule is unchanged: W > −114.9, plus a further 64-restart replication within 5 letters of any row
     above the bar.
   - This adds search effort only: no setting is dropped and no threshold moves. Both runs are reported.
2. **Diagnostic for the pass-count excess** (exploratory, not a decision criterion).
   - A single true key adds one pass, so an excess of about 100 passes cannot be a key signal. The working
     explanation is ordinary English letter structure at the clue-aligned key positions.
   - The test: the same oracle scan on 20 copies of the book with **word order shuffled**. This keeps spelling and
     within-word letter structure and destroys the real text sequence.
   - If word-shuffled copies pass as often as the real book, the excess comes from English structure, not this
     book's actual sequence.
