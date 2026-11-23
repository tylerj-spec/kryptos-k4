# Amendment 1 (before the computation): model reconstruction needs a correctly rounded log10f

**What happened.** Step B of `PLAN.md` compiled the pinned `r59/blind/lm_build.cpp` here (g++ 13.3, Ubuntu glibc 2.39)
and built K = 5 from the pinned training file (sha256 871627e5…, verified). The result is 49,426,528 bytes as
registered, but its sha256 is **09a1966f…**, not R95's registered **e9c0848f…**. Its orders 1–4 also differ from
R95's baseline `r91/R59_LOWER4_FROM_K5.bin` (`BUILD.json`, `BUILD_RESOURCE_LOG.json`). Per the plan, this path is
INCOMPLETE.

**Diagnosis** (model files only; nothing about R95's endpoint was computed or seen).
- My build's orders 1–4 equal the canonical R59 model `lm6.v2.bin` bit for bit. That model's sha256 b1a2a3c7… is
  pinned in `r59/blind/LM_SHA256` and was used by R59–R92.
- R95's baseline differs from both by **at most one float32 unit in the last place**, in 58 order-2, 1,010 order-3
  and 24,851 order-4 entries. The largest difference is 4.8e-7 log10.
- Five compiler and flag variants (FMA, x87, -O2, GNU mode, -march=native) all reproduce 09a1966f…. So the arithmetic
  is stable, and the difference is in the C library.
- The builder's only library call on the output path is `log10f(p)`. glibc 2.39's `log10f` is not correctly rounded.
  R91/R95's recorded toolchain is Debian g++ 14.2, whose glibc (≥ 2.41) ships correctly rounded float functions.
- Replacing that one line with the correctly rounded `(float)log10((double)p)` reproduces **e9c0848f… exactly**, and
  its orders 1–4 equal R95's baseline byte for byte.

**Amendment.**
- The model is reconstructed by `build_cr.py`. It applies exactly that one-line substitution, checks that nothing
  else differs, builds K = 5, and requires R95's registered digest and the baseline's orders 1–4.
- `verify95.py run` accepts either `BUILD.json` or `BUILD_CR.json` as the reconstruction record. That is its only
  change.
- The registered binding is the model's digest, and it is met exactly. Steps C–E are unchanged.

**Finding for the record (additive; changes no earlier result).**
- `r91/MODEL_RECEIPT.json` calls the baseline the "Exact lower-order 1-4 tables of the archived R59 K=6
  construction". Bit for bit that is not so against the canonical `lm6.v2.bin`: it differs by ≤ 1 ulp in about 5% of
  order-4 entries, because of `log10f` rounding.
- The effect on a 97-letter sum is at most about 97 × 4.8e-7 ≈ 5e-5 log10, far below every margin that R91–R95
  decisions used.
- The R59 builder's output is therefore C-library dependent. A future model pin should record the libm version or use
  a correctly rounded log.
