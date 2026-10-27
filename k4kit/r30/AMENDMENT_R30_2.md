# R30 amendment 2 (Claude Code, 27 Oct 2026): E4 source fixed before any scan of it

**Source.**
- **File:** Tyler's upload `content.pdf`, 16,586,238 bytes, sha256
  `64e3133d79b5052bb535139d284fe3f1c65be6d6348ddf4198f9028366ac5fa3`.
- **Scan:** a Google Books scan of the University of Virginia Library copy (X000421837), 397 pages.
- **Edition evidence (title and copyright pages in the text layer):** "THE TOMB OF TUT·ANKH·AMEN, discovered by the
  late Earl of Carnarvon and Howard Carter, by Howard Carter and A. C. Mace … THE FIRST VOLUME … New York, George
  H. Doran Company … Copyright, 1923". This is the US printing of Carter & Mace vol. I (1923), not G. Elliot
  Smith's book.
- **The K3 source passage is present** on pp. 141–142: "Slowly, desperately slowly … the remains of passage debris
  that encumbered the lower part of the doorway were removed … With trembling hands I made a tiny breach in the
  upper left hand corner … Can you see anything?"

**Text.**
- The PDF's own text layer (Google OCR, not proofread), extracted with poppler `pdftotext` in default
  reading-order mode (no `-layout`).
- Saved as `archive/sources/carter_mace_1923_v1_doran_google_ocr.txt`, with its sha256 recorded in the run output.

**Normalisation:** unchanged from the protocol (`book_key_test.py` rule, as reproduced in `e4_book.py`). Known
limitations, accepted in advance:
- 8 of the 140 page-header lines are OCR variants that the rule does not remove (Greek look-alike letters, or a page
  number on the same line). Plate captions and footnotes also sit between pages.
- These can only spoil windows whose clue span straddles one of them, roughly 1–2% of windows.
- Single-letter OCR errors in a window's 24 clue-aligned letters also break that window.
- The London (Cassell) printing may differ in small wording details; none is known.

**Run:**
- `python3 -I e4_book.py <text> --anchor-phrase TREMBLINGHANDSIMADEATINYBREACH --label carter_v1_doran`
- Search as pre-registered: every pass at 16 restarts (ORTH), the 20 best replicated at 64 with new seeds, 20
  letter-shuffled copies as the pass-count null.
- Candidate rule unchanged.
- E4 runs alongside the E2 run already in progress (shared CPU); results are unaffected.
