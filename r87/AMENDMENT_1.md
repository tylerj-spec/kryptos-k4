# R87 Amendment 1 (20 Nov 2026): kernel compile race in a fresh sandbox; no code change

**Written before the holdout truth was opened and before any K4 step.**

## What happened
In the gate run, the 4 pool workers of `run87.py` each found no compiled kernel in the fresh sandbox (`r87/.build/`).
They compiled it at the same moment into the same temporary path.
- One worker's rename failed (`FileNotFoundError` on `anneal_1b4171b5ba9f7e9a.tmp.so`), so its initializer raised.
- `multiprocessing.Pool` replaces a worker whose initializer fails. A worker takes no task until its initializer has
  finished, so no item was lost or half-run.
- The development runs and the isolation check never showed this, because there the kernel was already built or ran
  with 1 process.

## Why the results are unaffected, and how that is checked
1. **The kernel that ran is the right one.** The `.so` left in the sandbox is byte-identical to a clean compile of the
   pinned `anneal.c` with the same flags, and to the kernel used in development. All three have sha256 174f274b….
2. **Every item is deterministic.** Seeds come from (SEED, ciphertext, setting, pass), and the item order within the
   pool does not matter.
   - After the run, the first 8 holdout ids in input order (fixed now, before any output is seen) are re-run outside
     the sandbox with the already-built kernel and 1 process.
   - Their records must equal the sandbox records **byte for byte**. The comparison is `r87/holdout/run/DETERMINISM.json`.
3. **The resource log must say COMPLETE** (exit 0), as for any run.

## What changes
**Nothing in the pinned code.** The K4 run uses the same `run87.py`, so the race may recur.
- The same two checks are made for K4: the kernel hash, and the first 8 target ids (K4 and NULL_000–006) re-run
  outside the sandbox and compared byte for byte.
- If either check fails, the run is INCOMPLETE and is not evaluated.
