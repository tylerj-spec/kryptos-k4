# T3: does L170 (R81a) share the R83a drop-one defect? (15 Nov 2026)

**Answer: no.** In every family L170 covers, no later key or state depends on an earlier **plaintext** letter. The
validator puts each published letter into exactly one equation. So "one published plaintext letter wrong" breaks
exactly one equation, and R81a's drop-one (set that equation aside) is the exact test for it.

Label: post-freeze documentation review. Nothing was run on K4 and no file was changed.

## Per family: does later key or state depend on earlier plaintext?
| Family | Plaintext-driven state? | Evidence |
|---|---|---|
| R79 H7CT | No. Stream = ciphertext letter i − L | `r79/families.py:220-222` (`_stream_letter` reads `out_so_far`, the ciphertext); `r79/PREREGISTRATION.md` table: "ciphertext feedback `IDX[ka][c[i−L]]`" |
| R79 H7TXT | No. Stream = fixed K1–K3 text at an offset | `r79/families.py:224` (`texts()[...]`) |
| R79 LIB (982 slot rules: WK-C, REV, OMIT, IKN, CNT, CLS, REP, HELD, TRIG) | No. Every rule is fed the **cipher** letter just written, or is purely positional | `r79/families.py:191-205` (`feed(ch)`), called as `state.feed(c)` at `:250` (encrypt) and `:273` (decrypt); the walking key steps by the cipher letter (`:197`). `r79/PREREGISTRATION.md:45`: "Deferred (not in R79): the plaintext-driven walking key (WK-P) and plaintext feedback" |
| R79 PROG | No. Mask shift a·i + b is positional | `r79/families.py:240-242, 246-248` |
| R81a H7CT_A | No. As H7CT, on new alphabets | `r81a/families81.py:146` (`sl = out[i - L]`, ciphertext) |
| R81a LIB_A | No. R79's rules unchanged, stream none or ciphertext feedback | `r81a/families81.py:146, 153` (`state.feed(c)`) |
| R81a LIB_G4 (ROT, ALT, RESTART, SPLIT) | No. Slot sequences are fixed in advance from the position alone; `feed` only advances a counter | `r81a/families81.py:84-112` (precomputed `seq`), `:119-123` |
| R81a PROG_A | No. Positional mask | `r81a/families81.py:143-145, 149-151` |

Ciphertext feedback does make a plaintext change ripple into later **ciphertext** letters. But the validator reads
the actual ciphertext, so the slots and streams it computes are right whatever the plaintext is:
- `r81a/sealed/validate81.py:42` builds Z and R from `mod.chunks(fam, ct)`, which reads the ciphertext only.
- The published letters enter only at `:43-44`, one column per published position:
  `V = inv[OI, POS, WANT]; D = V − Z[:, POS]`.
- A wrong letter at position a therefore changes only D[:, a]. Setting column a aside (`ok1`, `:54`) is exact.

## How the "one-off" control is built
`r81a/sealed/control_validate81.py:59-62`:
- one **plaintext** letter of the planted message is altered (`pt2[p] = …`);
- the ciphertext is **re-encrypted** from the altered plaintext (`ct2 = mod.encrypt("".join(pt2), st)`);
- the checker still uses the published letters.

That is the correct control for a plaintext-error claim, unlike R83a's original ciphertext-letter control.

## Other ledger rows with "one letter wrong", "drop-one" or "set aside"
Searched in `LEDGER.md`. Besides L170 and L172 (handled in T1, `r83/audit/EXACT_DROP.md`):

- **L35** (robustness of exact exclusions to carving errors, `one_error.py`). The source file is **NOT FOUND** in the
  repository or in `R32_handoff_original.zip`, so its test cannot be read.
  - Its periodic, progressive and per-slot-bijection families have position-only keys. For those, a wrong plaintext
    letter breaks one equation, so a one-error claim is sound in principle.
  - **Hill 2×2 / 3×3** ("unaffected") is different. A wrong plaintext letter enters every equation of its block (two
    or three), not one. If L35's Hill claim was made by setting aside one equation, it has the R83a defect. If it
    meant ciphertext carving errors (one equation per ciphertext letter), it is fine.
  - **Status: UNVERIFIED; flag for T5/T6.** No ledger change made here.
- **L172 F1XD** (R75's F1X with one letter set aside). Both stages are periodic and position-keyed, with no
  plaintext-driven state. A plaintext error at one position breaks only that position's edge, so removing the edge
  is exact. Sound in principle. The F1X counts themselves are T2's subject.
- **Ledger summary line for R83a** (Changes section): it still says the walking key is excluded "also with one
  published letter wrong". That is superseded by the L172 erratum and T1 (WPX DROP = CHANCE). A pointer was added
  there; see `audit/reviews/R81A_T3_DROP_ONE.md`.

Independent review: NONE (one model).
