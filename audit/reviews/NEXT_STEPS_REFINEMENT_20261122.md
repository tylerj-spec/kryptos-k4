# Refinement of the 21 November work order (Claude Code, 22 Nov 2026)

Affected ledger IDs: none (planning). This refines `audit/NEXT_STEPS.md` (ChatGPT, PR #103) at Tyler's request
("Can you refine these next steps then do the next round?"). Everything that work order closed stays closed: R32, R41,
R82/R91, PTAK and the R90 review. Its rules carry over unchanged:
- no K4 or clue material in development;
- caps on development versions;
- INCOMPLETE is not a result;
- top-ranked recovery is reported separately from recall;
- overlap and equivalence rules are fixed before a gate.

Validation: arithmetic below; the timings are R87's measured kernel speed (`r87/dev/DEV.md`).
Independent review: NONE. A different model (Claude Code) is reviewing a ChatGPT work order. This is one review of a plan, not a verified result.

## 1. Phase gap (Priority 2): run it as one complete small round, R92
The 192 labels are R87's single rotor with a step-boundary phase:
- the schedule is s_i = d·⌊(i + r)/n⌋, with n 2–4, r 1..n−1, d ±1 and 16 contact pairs;
- R87's blind kernel takes any offset array, so only the offset formula changes;
- R87's exact check (a partial bijection of contact pairs) is likewise unchanged apart from the offsets.

So the work order's two steps can be one small round with the full protocol:
1. synthetic oracle;
2. pre-registration;
3. sealed gate on fresh books;
4. K4 plus 200 shuffles, strict blind;
5. post-freeze exact check.

The cost is about 17 minutes per run on 2 workers: development took 993 s for 202 items.

**Budget note.** The work order's 180 s / 120 s / 512 MiB per development job fits the oracle and tests, which run in
under 1 s. A solver development run at gate size does not fit: it is the same kind of job as R87–R90's, at about
2.6 GB aggregate. `r92/PREREGISTRATION.md` discloses this.

As the work order requires, nothing from R92 enters RX2-O: no survivor, wiring or ranking. R92 is registered separately,
so its K4 result is a scope closure only.

## 2. RX2-O (Priority 1): what the numbers imply, and the version plan
**Identifiability.** Two free wirings carry about 2·log2(26!) ≈ 176 bits. English redundancy is about 3.2 bits per
letter, so the unicity distance is about 55 letters.
- Recovery from 97 letters is possible in principle, but not by a wide margin.
- Within a slow-rotor segment the cipher is a single rotor followed by a fixed arbitrary output substitution. That is
  R87 with a free output numbering in place of four fixed ones.
- So the n = 4 cells with 0–1 turnovers are the most like R87.

**Throughput.** The full unknown-structure gate allows 7,200 CPU s for 5,990,400 labeled branches, about 1.2 ms per
branch.
- R87's kernel runs about 4–5 million annealing proposals a second. That is about 5,000 proposals per branch.
- A single-rotor recovery in R87 used 3 × 20,000 proposals per setting in pass 1 alone, and two wirings need more.
- **So per-branch annealing over all 16,640 labels cannot meet the gate budget**, by a factor of 10–100.

The full-gate design therefore needs a hierarchical search to be designed first. One shape it could take:
- fix the fast frame (n, r, d1, E_in);
- the free W2 absorbs the output numbering within a segment;
- treat the turnover (h, d2) as a one-dimensional boundary search.

That is a design question for version 2 or 3, decided on spent data. It is not a reason to change the gate's
recovery bars.

**Version plan within the work order's caps** (each version ≤ 1,800 s wall, ≤ 1,800 s aggregate CPU,
≤ 2,048 MiB aggregate):
- **v1: supplied-structure joint annealer.** This is the screen's solver, measured on a fixed development panel of
  spent text, 6 per turnover cell (48).
  - Kernel: R87-style, with two inverse wirings and swaps on either.
  - Scoring: quadgrams for the search, the R59 letter model for the final choice.
  - Report top-1 and any-of-8 recovery per cell.
- **v2 (only if v1 is credible):** more restarts or a staged search, to fix whatever v1's failures show; plus a
  measured unknown-structure prototype on a subset of labels.
- **v3:** the hierarchical unknown-structure pipeline and its throughput forecast.

**Stop rule:** as the work order sets it, stop after v3 without a viable prototype, and never use K4 or a fresh holdout
to diagnose a failure.

## 3. Unchanged
- PTAK and narrow R82 stay parked.
- RX2-D, wider phase domains and the RX2 exact audit stay deferred.
- No external submission without Tyler's go.
