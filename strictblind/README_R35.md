# R35 audit amendments

`rot-mixed LO HI OUT` is a separate route family of two independent quarter-turn directions (opposite in the two stages). It does not change `rot` or its historical outputs.

Run `python3 -I strictblind/tests/test_r35_integrity.py` to check generator permutation/count behavior and the write-once freeze guard. Run the full `bash strictblind/tests/run_all.sh` on a developer machine before merging.

New `blind/experiment.py` runs refuse to overwrite `FROZEN.sha256` and refuse nonempty output directories. **Use a new experiment directory for every scan.** The freeze now also fingerprints the scanner, executable, scoring table and experiment runner. Reusing existing historical freeze files is supported for reveal only: no previous R32–R34 experiment was retroactively rewritten. Whole-family verifies that every expected setting was counted, and now errors on worker failure.

Research limitation: the existing fixed-alphabet scan has not become a general K4 solver. R35 merely broadens route coverage and strengthens evidence quality. Do not interpret unrun tests or experiments as successes.
