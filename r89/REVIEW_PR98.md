# Independent review of ChatGPT's R89 design (PR #98) by Claude Code, 21 Nov 2026

**Scope.**
- **Reviewed:** `docs/R89_ADVERSARIAL_METHOD_AUDIT.md`, `docs/R89_EXECUTABLE_BOUNDS_V2.md` and
  `docs/R89_PILOT_VERIFICATION.md` on branch `chatgpt/k4-mechanism-matrix-20261120` (head 21aa314).
- **This is a review by a different model** from the builder, as PR #98 asks.
- **Not reviewed:** ChatGPT's development kit (a ZIP that is not in the repository). Every line of R89's code was
  written here from the stated equations, without seeing ChatGPT's code. Where the two agree, the agreement is between
  independent implementations.

## Verdicts in brief
| Item | Verdict |
|---|---|
| F26L equations (C–D) | **Correct and reversible.** Checked by 3,000 random round trips of length 1–98, every block length 1–30 for all 188 (b, u, v), and the K1/K2 openings |
| F26L search design | **Change:** the family is finite (139,120 fixed decryptions), so enumerate all of it. The 8-of-36 phase shortlist and its ≥ 46/48 bar are dropped |
| F26L equivalences | **Two found that the design does not state** (below). One changes the alphabet list |
| RCT equations (A) | **Correct and reversible** (3,000 round trips). Added: R87's 16 contact numberings, with AZ/AZ as the design's case |
| RCT novelty | **Not a duplicate.** R77 H8 proposed letter-driven stepping and was never run (no ledger row). R87 was regular stepping. L17 is a one-sided free alphabet with an autokey, not a rotor |
| RCT search | R87's measured annealing schedule (`r87/dev/DEV.md`) instead of 80 × 16,000. The total effort is similar: about 50M against 36M proposals per ciphertext |
| Exact checks | **Both arms have a decisive post-freeze check that the design omits**, below |
| Classifier and abstention | **Use R59's fixed cuts as the standardized unit**, below |
| Gate bars | **Adopted unchanged** for both arms (42/48, 36/48 exact, 9/12 per stratum, 12/16 per genre, 8/12 masked, ≤ 1/150 negatives), except the shortlist bar |
| Post-hoc selection caveat | **Agreed**, and it is the main limit on what a result can mean |
| M2, M3 (bare), M4 rejected | **Agreed.** Bare F26 is still decoded, as a sub-family that is reported, at no cost |

## 1. F26L is a finite family: enumerate it
- Every F26L setting (alphabet, b, u, v, key, sign, phase) is a fixed decryption with no free key.
- All 139,120 settings (135,360 F26L plus 3,760 bare) decrypt and score in **0.18 s per ciphertext** with numpy
  (`r89/blind/f26_solve.py`).
- The design's shortlist (rank the 36 outer options by inner IC, keep 8) saved time that is not needed, and it added a
  way to fail: the true phase missing from the shortlist. With full enumeration:
  - search failure is impossible;
  - the gate measures only whether the scorer ranks the true decode first;
  - the K4 result covers every setting.
- The ≥ 46/48 shortlist bar has nothing left to measure and is dropped.

## 2. F26 equivalences
**(a) A reversed alphabet is the same cipher.**
- Reversing a 26-letter alphabet maps place k to 25 − k. That swaps the two rows and mirrors the 13 columns, and F26
  cannot see either change.
- The general rule: two alphabets give the same F26 iff they have the same unordered row partition and the same set of
  column pairs (`f26l.canonical`).
- My first list had four reversed alphabets (ZA, KRYPTOS, PALIMPSEST and ABSCISSA reversed). In development a
  PALIMPSEST-reversed plant was "recovered" as PALIMPSEST.
- They were replaced. A test now proves that the 20 alphabets fall into 20 distinct classes.
- ChatGPT's own list is not in the repository, so it should be checked the same way.

**(b) (u − k, v − k) is the same decode rotated by k within each full block.**
- So the 188 (b, u, v) settings are a relative fractionation offset δ = v − u combined with a block rotation.
- Near-miss decodes therefore include block-rotated copies of the true text, which are locally English within each
  block.
- On real prose the true decode wins clearly (one probe: −414 against −460 quadgram score). On a bare word list it did
  not, which a test now records.
- The gate's ≥ 95/97 recovery criterion already rejects rotated decodes, which have about 10 letters right.

## 3. The exact checks are decisive and cheap
- **F26 / F26L:** each setting is one decryption, so after the freeze `r89/sealed/exact89.py` decodes the 24 published
  positions under all 139,120 settings and counts matches.
  - EXCLUDED means no setting gives 24/24.
  - DROP means no setting gives ≥ 23/24.
  - The maximum is compared with the shuffles.
- **RCT:** the offsets s_i depend only on the ciphertext, so each of the 448 settings is a partial-bijection test,
  R87's check with different offsets.
- Both are exclusion-only, run after the blind evaluation, and never set a blind scope.

## 4. Classifier and abstention
The design asks for an end-to-end classifier with an ABSTAIN option, calibrated across arms, and leaves the
calibration open.

**Proposal (adopted):** use the R59 cuts already fixed for R80a, R84, R87 and R88, applied to the decoded text.
- The cuts are letter model ≥ −1.30 and word model ≥ −2.50 per letter.
- They give the same unit for every arm, because they score the output text, not the search.
- Across those four gates they gave 0 confident decodes among 360 wrong-family negatives.
- **Family declared** = the arm of the best confident decode. **ABSTAIN** = no decode clears both cuts.
- The cuts were fixed long before R89, so nothing is tuned on its data.

## 5. Corpus and genres
**Fresh gate books**, none of them named anywhere in the repository (title search; the only matches were chance
substrings inside old random decodes):
- **narrative:** Narrative of the Life of Frederick Douglass (#23);
- **formal historical:** Gibbon, Decline and Fall vol. 2 (#732);
- **technical:** The Radio Amateur's Hand Book (1922, #6934);
- **running keys:** The Federalist Papers (#1404).

The design's "modern news" genre has no public-domain source on this mirror, so a 1922 technical manual stands in.
That is a deviation, and it is disclosed.

**Mask.** C→K, W→V: fixed, length-preserving, "Germanic-looking". On spent text, 97% of masked windows still clear the
letter-model cut (median −1.02, against −0.73 unmasked).

## 6. Things the design gets right and that R89 keeps
- **Post-hoc selection.** The tableau stage was added after seeing K4's flat IC.
- **Shared negatives and abstention.** Every arm sees the same negatives, and decoys can abstain.
- **No repair after failure.** A failed arm is retired. There is no repair after the gate and no K4 run through a
  failed arm.
- **200 shuffles,** with a family-wise maximum over the eligible arms.
- **Freeze order.** Pushed freezes come before the truth is opened and before any published letter is read.

## 7. Plausibility
Neither mechanism has historical support for Kryptos.
- The F26 fractionation is invented: the 1943 Army manual even called a 2×13 rectangle impractical for digraphic use.
- RCT's trigger rule is arbitrary.
- The most a K4 result here can do is exclude these specific constructions. A positive would need the full proof
  chain, as in R87.

**Independent review of this review: NONE.**
