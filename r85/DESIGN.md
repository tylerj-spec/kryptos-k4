# R85 design: which cipher family to test next, and how (Claude Code, 17 Nov 2026)

**Status: design only.**
- No K4 run.
- No published letter was used by new code, except the two existing crib-derived facts cited in §1 and §3, which
  are labelled.
- The model code and synthetic pilot behind §4 are ready. They will be committed with the pre-registration, because
  CI requires a QA manifest for code in a new round.

## In plain words
- **Recommendation: test a stepping-rotor cipher next.** This is the Hebern type, the family behind the US government's
  rotor machines. One scrambled wheel (the "wiring") turns a notch every few letters, so each letter is enciphered
  through a slightly turned wheel.
- **Why it fits K4:**
  - it enciphers letter for letter in place, as Sanborn's clues require;
  - it flattens letter counts like K4's;
  - it allows a letter to encipher to itself, which K4 does twice;
  - nobody has tested it on K4 in this project.
- **Why it is worth doing first:** it sits exactly in one of the few gaps the exact checks left open, and it can be
  tested decisively.
  - On synthetic data, a quick check against the 24 published letters never passed by chance in 153,600 trials.
  - A blind solver recovered the hidden wiring from 97 letters in 5 of 6 test messages, the sixth at 90/97.
- **If it fails,** the same machinery extends to two rotors, and three runner-up families are listed in §5.
- **Two other families can be ruled out by reasoning alone:**
  - wheel and strip ciphers (Jefferson wheel, M-94, M-138);
  - reflecting rotor machines (Enigma type).
  Both make self-encipherment impossible, and K4 has it.

## 1. What any candidate must satisfy
| Fact | Source | What it rules in or out |
|---|---|---|
| 97 letters, all 26 present; IC 0.0361, near random | ✔ `docs/KRYPTOS_FACTS.md` §3, L32/R54 | 25-letter squares are out (Playfair, Bifid 5×5). Periodic keys with short periods are out; aperiodic or long-period polyalphabetics fit |
| Three plaintext E's, two ciphertext E's | ✔ crib-derived, L01 | Pure transposition is out |
| `QQ` → `NO` at positions 26–27 | ✔ crib-derived, L02 | A single fixed alphabet in place is out |
| Self-encipherment at positions 33 (S→S) and 74 (K→K) | ✔ crib-derived (`KRYPTOS_FACTS.md` §3) | Any direct system that cannot encipher a letter to itself is out (§3) |
| The clues are letter-aligned: "NYPVTT deciphers to BERLIN", at given positions | ✔ | The **final step works in place**, one ciphertext letter per plaintext letter at the same position. A transposition **after** the substitution would break the alignment |
| K5 "has a similar coding system to K4" and BERLINCLOCK "in the same position" | ~ second-hand quote of Sanborn's Nov 2025 open letter (numberworld.blogspot.com; not reachable from this session) | Supports a position-preserving system |
| Sanborn: the "scrambled plain text was found", but not the method or key | ~ same source | Could mean a scrambling step **before** an in-place substitution. Because the clues are aligned, that would **not** reopen any family the in-place exact checks closed (§5, item 6) |
| Scheidt: K4 uses a "masking technique" | ~ WIRED 2005, L33 | The form is unknown |
| Sanborn: do not assume K4 is purely mathematical | ~ Scientific American, Nov 2025 (`docs/RESEARCH_LOG.md`) | Mechanical or hand-operated systems are in |

## 2. What is already closed, by mechanism (from `LEDGER.md`, `docs/CIPHER_TYPES_TESTED.md`)
- **In-place tableau ciphers with structured keys: closed exactly.** This covers periodic keys to 26 and beyond,
  progressive keys, linear recurrences, Gromark (fixed and keyword alphabets), running keys from every named text
  tried, short-lag autokeys, interrupted, held and grid keys, two periodic stages (F1X), and the R83 families.
- **Flexible-key families: closed only statistically, by blind solvers.** This covers unknown running keys, two-stage
  keyword ciphers (R84) and others.
- **Per-slot arbitrary alphabets: OPEN at many periods, including m = 26** (L21). L53 says these periods "stay OPEN;
  only extra structure (e.g. slots sharing one keyed alphabet)" can decide them.

**A rotor is exactly that extra structure.** All 26 slots share one wiring, rotated by the step.

## 3. Ruled out by reasoning (no run; both rely on the two self-encipherment facts above)
- **Wheel and strip ciphers in direct form** (Jefferson wheel, M-94, M-138-A).
  - The plaintext is set along one row (or column) of the disks or strips. The ciphertext is read from another row
    at a fixed non-zero offset for that line.
  - Each disk or strip holds every letter once. A letter can encipher to itself only at offset 0, which would leave
    the line in clear.
  - K4 enciphers S→S at 33 and K→K at 74, in two different 25-letter lines. **Excluded in direct form.** A variant
    with a per-letter offset is another cipher.
- **Reflecting rotor machines in direct form** (Enigma type). The reflector makes the enciphering an involution with
  no fixed points, so no letter can encipher to itself. **Excluded.** Non-reflecting rotor systems are not affected
  (§4).

## 4. Recommended family: RX, a stepping rotor with an unknown wiring
**Model.**
- Contacts are numbered by an input alphabet E_in and an output alphabet E_out: AZ, KRYPTOS, PALIMPSEST or ABSCISSA.
- The wiring W is any of the 26! permutations.
- The rotor advances d = ±1 every n letters: s_i = d·⌊i/n⌋.
- Encryption: `E_out(c_i) + s_i = W(E_in(p_i) + s_i)` (mod 26).
- The starting position is absorbed by W.
- With n = 1 the period is 26: L21's open m = 26. With n ≥ 97 it is a single alphabet, excluded by L02.
- **3,072 settings** (16 alphabet pairs × 2 directions × n = 1–96), each with a free wiring.

**Why this family is plausible.**
- **Era and source:** rotor systems were the mainstream professional ciphers of Ed Scheidt's era at the CIA (~;
  inference, not his statement). A single rotor can be worked by hand or with a paper slide ("not purely
  mathematical", ~).
- **Fits the facts in §1:**
  - in place;
  - flattens the IC through a period-26n polyalphabetic;
  - allows self-encipherment (4 per 97 letters in a random plant);
  - no letter-count contradiction.
- **Not already covered:** L13 and L20 used fixed alphabets and arithmetic stepping, not a free wiring between two
  shifts.

**Technique 1: exact crib-assisted check (exclusion-only).**
- Every published position is one equation of the single permutation W. A setting is feasible only if the 24 pairs
  form a partial bijection.
- **Synthetic measurement** (`r85/dev/pilot85.py` and `PILOT.json`, committed with the pre-registration):

  | Test | Result |
  |---|---|
  | Random ciphertexts with random letters at K4's positions | **0 of 153,600** setting trials pass |
  | A true setting's constraints on English-frequency plants | median 10 (range 4–14) |

- So this check either excludes RX outright or flags a setting no shuffle reaches. It runs in seconds on K4 + 100
  shuffles.

**Technique 2: strict-blind solver.**
- Simulated annealing over the wiring in the rotor frame, scored by quadgrams. The model is the same as a monoalphabetic
  solve, plus a known position-dependent shift.
- **Synthetic pilot** on spent development text, setting given, wiring hidden:
  - 5/6 recovered **97/97**, 1/6 at 90/97 (its score equals the true text's, so the quadgram model tied);
  - the same solver under a wrong step period scores about 0.8 per quadgram lower, a gap of about 75 log-points.
- **Cost:** 2.5 s per annealing run in Python. Over 3,072 settings × 101 ciphertexts that is too slow. It needs a C
  port (about 100× faster) or a first pass limited to n ≤ 26 (832 settings): roughly 1–2 hours on 4 cores.

**Plan, with R84's controls throughout** (isolated sandbox, independent witness checker, one-ciphertext-error
diagnostic, freeze and push before the evaluation).
1. **Pre-register** R85, `PROTOCOL.sha256` and QA manifest, with the code above.
2. **Decision for Tyler (see below):**
   - (a) run the exact check first, as with R83a, which Tyler accepted for exclusion-only checks;
   - or (b) blind first, as R53 prefers, with the exact check after the freeze.
3. If the exact check leaves settings above the shuffles, or if (b) is chosen:
   - a C annealer;
   - a sealed gate (fresh books; strata by n and by alphabet pair; wrong-family negatives);
   - then K4 + 100 shuffles, blind.

**What a negative would and would not mean.**
- **Would exclude** (exact): every single-rotor setting in scope, for any wiring.
- **Would not cover:**
  - two or more rotors (odometer or irregular stepping);
  - stepping triggered by letters;
  - other contact numberings;
  - a reflector, which §3 excludes anyway;
  - transposition plus rotor.

## 5. Runner-up families, ranked
| # | Family | Why | Decisive exact check? | Blind power at 97 letters | Note |
|---|---|---|---|---|---|
| 2 | **RQ: progressive Quagmire with one free alphabet** (`E_out(c) = PA_free(p) + s_i`, or the mirror) | A structured subfamily of the same open per-slot space. L13 used fixed alphabets only | Yes: a partial-bijection check like RX; bundle it into R85 | Good (R44b-type single-free-alphabet solving) | Nearly free to add |
| 3 | **RX2: two or more rotors** (odometer: rotor 2 steps every 26n letters, any phase) | The natural next step if RX is excluded; Hebern multi-rotor, SIGABA-like | Needs a constraint solver over two unknown permutations | Harder; annealing on two wirings | Design after R85 |
| 4 | **Chaocipher with two arbitrary wheels** | Evolving alphabets; R56 tested only one keyed wheel plus a standard one | Weak: the 29-letter gap loses the state | Low on 97 letters | Needs a new solver; low priority |
| 5 | **Alberti disk with irregular turns** (one mixed alphabet, shift changed by hand at unmarked points) | 15th-century hand system; "masking" by unannounced turns | Partly: F2X/F3X covered keyword-derived held and interrupted keys only | Medium | Overlaps L165 |
| 6 | **Scrambled plaintext, then an in-place substitution** | Sanborn's "scrambled plain text" (~) | The clues bind the substitution in place, so every in-place exact exclusion still applies | Only flexible-key families lose blind power (n-gram scores need order). The implied key at the clue positions is not English (L31), which disfavours running keys here too | Affects how future blind solvers should score: add an order-free (unigram or bag-of-words) score as a second channel |

**Explicitly not recommended** (already closed or near-vacuous): more periodic, Gromark, running-key-text or
two-keyword-stage variants in place; nulls; other languages without a new mechanism.

## 6. Decisions for Tyler
1. **Go for R85 = RX**, with RQ bundled? It needs a pre-registration PR first.
2. **Order:**
   - (a) the exact check first. It takes seconds and is decisive, so it is the efficient choice, and it is how R83a
     was approved.
   - (b) blind first, per R53. It costs a C port, a gate and about 2 hours, even if the exact check would have
     excluded the family.

   My recommendation is **(a)**, with the blind round built only if K4 survives at a level the shuffles don't reach.

**Independent review: NONE.** One model did this design.

Sources (public statements, ~):
- [Scientific American, Nov 2025](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/)
- [numberworld blog reproducing the open letter](https://numberworld.blogspot.com/2025/11/jim-sanborn-open-letter.html)
- [rumkin.com K4 notes](https://rumkin.com/reference/kryptos/k4/)
- [ScienceBlogs on the masking technique](https://scienceblogs.de/klausis-krypto-kolumne/2019/03/15/cnn-documentary-about-kryptos-a-making-of-report-with-many-photographs/)
- WIRED 2005 (Scheidt), cited in `docs/RESEARCH_LOG.md`
