# R84 Amendment 2 (17 Nov 2026): first K4 launch stopped and relaunched detached; no output read

**What happened.**
- The first launch of the blind K4 run started under `audit/run_bounded.py` from a tool-managed background shell.
  That shell is cut off after 2 hours.
- After 8 of 101 ciphertexts, the measured rate (about 70 s per ciphertext on 4 cores) put the finish at about
  118 minutes. A cut-off there would leave no resource log and an INCOMPLETE run.
- I stopped it on purpose at 582 s (SIGTERM to its process group). Its resource log is kept as
  `r84/k4/launch1_aborted/RESOURCE_LOG.json` (status INCOMPLETE).

**What was not done.**
- None of its 8 per-ciphertext outputs was opened or scored.
- They are kept unread, outside the repository, in the first sandbox. Only their file hashes are recorded, in
  `r84/k4/launch1_aborted/PARTIAL_SHA256.txt`.

**Change.**
- The run is repeated from scratch in a fresh sandbox, as a detached process (`setsid`), under the same
  `audit/run_bounded.py` and the same budget. Code, target, parameters, rules and scripts are all unchanged.
- The runner is deterministic per ciphertext. After the freeze, the 8 recorded hashes are compared with the same 8
  ciphertexts' outputs in the full run. A mismatch would be reported.
- The aborted launch is not a result. Only the complete run is evaluated.
