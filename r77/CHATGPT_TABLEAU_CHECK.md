# Brief for ChatGPT: check the sculpture's layout from photographs (R77 prep)

Written by Claude Code, 11 Nov 2026, for Tyler to pass to ChatGPT. **No test depends on this yet.** The H5 overlay
hypothesis (`r76/HYPOTHESES.md`, H5) was written from memory, and nothing gets built on it until this check is done.

## Rules for this task
- **Do not look for, read or report any K4 plaintext or "solution".** That includes coverage of the 2025 archive
  story. If a page discusses it, close it and use another source.
- Submit nothing to Sanborn, to any checker or to any outside party.
- Copy **no photographs** into the repo; they are copyrighted. Transcribe the letters as text and link to each source.
- For every answer, say where it comes from:
  - **photo:** you read it yourself from a photograph; give the link, the photographer or archive, and the date if
    known;
  - **transcription:** someone else's typed copy; give the link;
  - **memory:** your own recollection. This is allowed, but it must be labelled.
- Where sources disagree, give each version. Do not pick one silently.

## Task 1. The tableau panel (right-hand half of the copper screen)
1. **Rows.** How many rows are there? Is it 28: one header row, 26 keyed rows and one footer row?
2. **Header and footer rows.** Give their exact text and letter count. The expected text is
   `ABCDEFGHIJKLMNOPQRSTUVWXYZABCD` (30 letters). Is there a blank cell at the left, above the label column?
3. **Keyed rows.**
   - Is each row a label letter (A–Z, top to bottom) followed by 30 letters of the KRYPTOS alphabet
     `KRYPTOSABCDEFGHIJLMNQUVWXZ`?
   - Does each row start one letter further along than the row above? The expected starts are row A `KRYPTOS…` and
     row B `RYPTOSA…`.
   - Transcribe at least rows A, B, M, N, O and Z exactly, with their letter counts.
4. **The extra L.** Which row has it? Where in the row is it, and how many letters does that row have?
5. **Anything else irregular** on the tableau panel: a misspelling, a raised or differently cut letter, a letter
   out of line, or uneven spacing.

## Task 2. The ciphertext panel (left-hand half) and how the two halves line up
1. **Rows and widths.** How many rows does the ciphertext panel have, and how many characters is each row?
   A table of row number, character count and first and last five characters is enough.
2. **Where K4 sits.**
   - Confirm or correct this layout: K4 fills the last four rows as 4 + 31 + 31 + 31 letters, so positions 1–4
     (`OBKR`) end row 25, and positions 5–35, 36–66 and 67–97 are rows 26, 27 and 28.
   - Does the `?` before `OBKR` take up a cell?
   - Transcribe the last four rows exactly as carved, with any `?` or spaces.
3. **Side by side or back to back?**
   - Are the ciphertext and the tableau on the same face of the screen, side by side?
   - Do their rows line up horizontally, with the same number of rows at the same heights?
   - If the halves do not line up row for row, describe how they are offset.

## Task 3. Re-derive one fact by hand (the published letters, used as a check only)
These are 1-based positions, plaintext → ciphertext:
`22 E→F, 23 A→L, 24 S→R, 25 T→V, 26 N→Q, 27 O→Q, 28 R→P, 29 T→R, 30 H→N, 31 E→G, 32 A→K, 33 S→S, 34 T→S,
64 B→N, 65 E→Y, 66 R→P, 67 L→V, 68 I→T, 69 N→T, 70 C→M, 71 L→Z, 72 O→F, 73 C→P, 74 K→K`.

1. **Confirm or refute each statement.** A tableau stage is `c = CA[s·PA⁻¹(p) + t·k]`, with Vigenère (s, t) =
   (1, 1), Beaufort (−1, 1) and variant Beaufort (1, −1).
   - If PA = CA, a self-encryption (p = c) forces k = 0 for Vigenère and for variant Beaufort, whatever the
     alphabet.
   - If PA = CA, Beaufort forces k = 2·PA⁻¹(p) (mod 26), not 0.
   - If PA ≠ CA, a self-encryption forces nothing on its own.
2. **Surviving periods.** For the Vigenère case with PA = CA and a repeating key of period m, a period dies when
   some other published position falls in the same key slot as 33 or 74 (positions i and j share a slot when
   i ≡ j mod m). List every m from 1 to 97 that survives.
   - Our earlier note said every period 1–26, 31–40 and 42–52 dies, leaving 27–30, 41 and 53 and up.
   - Say whether that is right, and show the colliding pair for each period that dies.

## What to send back
- **Preferred:** a PR adding one text file, `r77/chatgpt/TABLEAU_LAYOUT.md`, with Tasks 1–3 answered and sources
  for each answer. It should contain no images and change no other file.
- **Otherwise:** a message Tyler can paste to Claude.
