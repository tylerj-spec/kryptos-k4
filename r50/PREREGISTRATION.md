# R50 preregistration — K3-style T_then_S, complete 5-digit Gromark, one arbitrary alphabet
**30 October 2026, before any R50 K4 output.**

## Rationale / novelty
K4 research L94 explored K3-neighborhood routes and a **two-free-alphabet** Gromark compatibility oracle, which yields numerous vacuous hits. R45 excluded *in-place* keyword/free 5-digit Gromark. R46/R46A excluded four double-rotation routes when **substitution is before transposition**. This round tests exactly the **opposite ordering**, a remaining meaningful model in Claude's October 29 review: **transposition before substitution**, anchored to independently known K3 double-rotation mechanics. No Berlin-clock data, city names, geographic assumptions or conjectured K4 plaintext words are inputs.

## Model: locked before calculation
- Original 97-letter K4, exact SHA256 (with newline) `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.
- Exactly FOUR fixed K3-style two-quarter-turn routes `R24x8/CW/fwd`, `R24x8/CW/inv`, `R24x8/CCW/fwd`, `R24x8/CCW/inv`, using the already independently verified `k4kit/tools/k4common.py::route`. If `perm[j]` is the original plaintext position, first form `Q[j]=P[perm[j]]`, then substitute `C[j]=CA[(PA^-1(Q[j]) + sign*k[j]) % 26]`. **The Gromark digit is indexed by j (the ciphertext order), not by perm[j].**
- Test all **100,000** decimal five-digit primers (00000 to 99999), recurrence `k[i]=(k[i-5]+k[i-4])%10`, both `sign=+1/-1`.
- **H1:** one alphabet is drawn from the **4,749** distinct R44b word-derived alphabets from exactly the top 5,000 ORTH vocabulary words (length 5–10); other is any complete 26-letter permutation. Check BOTH plaintext keyword/CA free and ciphertext keyword/PA free.
- **H2, separately reported:** add these EXACT 15 specifically chosen Kryptos-themed words not all in R44b vocabulary: `KRYPTOS PALIMPSEST ABSCISSA BERLIN SHADOW EGYPT CARTER LANGLEY SANBORN SCHEIDT ILLUSION UNDERGROUND MAGNETIC POSITION WELTZEITUHR`; deduplicate their keyed alphabets and omit those already in H1. Never silently expand H1 with H2 or count repeated alphabets twice.
- Exact 24 public plaintext letters at original zero-based 21–33 and 63–73 become **substitution-layer anchor indices `invperm[21..33,63..73]`**. The **original ciphertext remains unchanged**; it is not inverse-transposed. The letters are used **only in this sealed exact algebraic feasibility screen**, not to seed plaintext candidates or rank a language model.
- At every route/key first test the independently audited exact **two completely free alphabets** graph oracle. Keyword/free H1/H2 are subsets, so this is a sound necessary filter. For survivors use an equality-difference index followed by the *full* previously independently audited `fixed_pa/fixed_ca` injectivity test. A passing fixed-keyword result means an unrestricted counterpart alphabet can be completed; it does not reconstruct unknown K4 text.
- Preserve every viable primer and every keyword/alphabet/sign/route, and raw count histograms. No cutoff, no shortlist or score threshold. Frozen JSON and SHA256 manifests.

## Pre-specified controls
1. **20 algebraic positive plants:** use the **already revealed** R44b English test plaintexts, every four routes evenly, Gromark keys given only to checker, alternating signs, 10 keyword PA and 10 keyword CA with a fresh unrestricted counterpart alphabet. Encrypt Q then substitute; independently reverse transpose + substitution to recover original 97 letters and full re-encryption. All 20 must pass their expected exact graph, single-fixed-alphabet and keyword index tests. **These are not new blind holdouts.**
2. **Two ciphertext frequency-preserving nulls**, shuffled K4 with seeds **50100** and **50101**, receive all same 4 routes × 100,000 keys × 2 signs × keyword/free candidates. Report their H1/H2 pass counts; only two nulls, NOT calibrated p-values.
3. **First 3 two-free primer survivors per route on K4 and each null:** keyword index must match an independent unindexed brute-force check of **all** 4,749 common and extra themed candidates, both signs and both orientations. Failure invalidates output.
4. **Separate positive negative control:** regenerate at least one synthetic T_then_S message and intentionally evaluate with the wrong **S_then_T** mapping, to prove order is not silently confused. Do not require false negative for every random plant, but record at least one seed where the wrong-order true configuration fails a full-alphabet consistency check.

## Locked decision rule
- `EXCL` for H1/H2 under just the four named T_then_S routes if zero exact keyword/free-compatible settings.
- `FEAS` only if one or more survive. Being consistent with the 24 released letters **does not** count as a decryption or as independent evidence of words. Do not fit missing text to those anchors.
- If `FEAS` set is tractable, **separately** preregister and freeze a ciphertext-only blind English-solving experiment on fresh plants with **key unknown**. Full exact 97-letter recovery is the real target, at least 16/20 in new holdout; expose K4 outputs before comparing public words.
- If `EXCL`, change cipher family rather than retuning excluded Gromark/4-route models. This excludes neither other rotations, keys, two arbitrary alphabets, masked plaintext nor the World Clock as a possible *meaning* of the text.

No external verifier, no derived K4 plaintext, no merges to `main` in this round. This protocol reports no results.
