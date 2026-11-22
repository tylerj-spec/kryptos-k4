# Prospective archive-format clarification

After publishing the plan and synthetic tests in `dea5bb84ec983b3d7fc978e11efeebe7f0fd72df`, but before reading the target ciphertext or running the new recount, inspection of the archived aggregate JSON showed that it preserves **summaries**, not every histogram bin. It contains setting totals, maximum match count, one maximum-setting witness, the full24 list and cumulative counts at thresholds8,9,10,11,12.

Accordingly, the full replay will publish a newly computed25-bin histogram for each of the five jobs and compare **every retained numerical statistic**, plus independently verify the archived maximum-setting witness. Original bins0–7 cannot be compared because they are not present. Do not state that those missing bins were byte-identical to a historical artifact. This changes no family, parameter, count, cutoff, budget or target decision. The synthetic pretarget choice remains FULL, not sampled.

Full closure means the independently computed full setting counts and all retained summary statistics agree. This resolves the formerly unrecounted7.10-billion-setting aggregate; it does not recover missing original stdout or certify the statistical independence of labeled settings.
