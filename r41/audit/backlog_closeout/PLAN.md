# R41 historical closeout plan

Scope: independent, post-freeze, crib-assisted feasibility-count audit for L135. No plaintext decoding, missing-alphabet completion, candidate ranking, new family or new key search. Preserve every original artifact.

The audit re-derives all116 PartA routes and all5,000 PartB routes from coordinates. It preserves original multiplicities. PartA uses every C10b5/C10b6 primer and every CARTER/K1K3 window in both directions and both numberings. PartB uses C10b5 and K1K3. All7 cipher alphabets and both operations remain included.

## Complete feasibility through an equality index

For each repeated plaintext letter, choose its first occurrence as representative. A free plaintext alphabet requires the corresponding numeric values `y_i = CA^-1(C[q_i]) +/- key_i` to be equal. Index every fixed keystream by the vector of differences between its repeated-letter positions and their representatives. For each route, cipher alphabet and operation, query the required vector from the routed ciphertext. Then check every full partial-bijection constraint on each returned key, including distinct-letter inequalities. Hash collisions are explicitly rechecked and cannot remove or invent feasible settings.

This is a complete algebraic join over the full setting set, not a route/key sample. It avoids visiting the overwhelmingly incompatible Cartesian-product pairs. The emitted total number of labeled settings is separately calculated from Python integer factors. The result covers feasibility and consistent-setting counts, not the original full violation histograms or minimum positive violation values.

Compare both parts for every archived input: K4, two nulls and six plants. Compare complete consistent-setting counts and settings totals. For plants, independently verify that the planted configuration survives. Do not interpret the historical blind gate or language-model scores as exact exclusions.

## Checks and limits

Before K4: exhaustive toy comparison with all permutations of the free alphabet; synthetic compiled-kernel versus scalar feasibility on arbitrary masks and routes; planted maximum primer/window boundaries; and synthetic route reconstruction comparisons. No original solver is imported by the independent checker.

Budget: one process, at most2,400 wall seconds and1,800 aggregate CPU seconds for the complete replay;2,048 MB aggregate resident memory. Synthetic development/benchmark separately at180 wall/120 CPU seconds. No retry after inspecting target results. Every target-reading job runs through the current bounded wrapper, with aggregate CPU/RSS accounting. If the synthetic benchmark projects beyond80% of a cap, use a frozen sample of every100th route plus first/last, explicitly labeled SAMPLED_REPLAY and leaving complete feasibility open.

Any count disagreement, missing plant, target survivor, timeout or memory breach stops the affected audit. Publish additive results and disclose exactly which old claims were and were not independently recalculated. Full feasible-count agreement can validate the bounded exact exclusion; it must not be called a full replay of the original violation histograms.
