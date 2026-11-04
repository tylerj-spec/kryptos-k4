# R65 result (Claude Code, 4 Nov 2026): the German route gap is real, but it is not a German running key

**No K4 solution.**
- **R65:** **REPLICATED**, ciphertext-only.
- **R65b:** the published-letter check is **NOT LANGUAGE-LIKE** on both anomalous routes.
- **Not done:** no external checker was contacted.

## Plain words
- **What R64 noticed after its reveal:** under the German key model, one route (SNAKE_L, which reads the sculpture's
  rows back and forth) stood 28.5 points ahead of the next best for K4. That was more than any of R64's 100 shuffled
  copies.
- **R65 fixed that statistic in advance and tested it on 300 new shuffles.** None reached K4's gap; the largest was
  27.8. So the effect is real, not luck from looking: p = 1/301.
- **R65b then asked what it would mean if the effect came from a German running key on that route.** In that case the
  key letters implied at the 24 published positions would read as German, under one of the 6 conventions.
  - They do not. The best pair is `JIDHFPCNOKOPH` / `OCGCIPMPICE`.
  - Random rearrangements of K4 do as well 4% of the time; the pre-registered bar was 1%.
  - R61's COL_LT oddity (English key) fails the same check badly: p = 0.90.
- **Conclusion:** K4's letters, read in SNAKE_L order, have some structure the German model partly fits, which
  shuffles lack. A German running key on that route does not explain it. The full decode on that route is still word
  salad (R64: 3/24 published letters).

## R65 (`r65/PREREGISTRATION.md`, ciphertext-only; no published letters)
| Step | Commit | Result |
|---|---|---|
| Pre-registration | 64ec3cd | — |
| Target (K4 + 300 fresh shuffles, seed 650070) | 810c792 | — |
| Freeze (all raw work files) | e45e1b2 | — |
| Evaluation (`r65/k4/EVALUATION.json`) | b8b6d16 | **REPLICATED** |

- **K4's re-run gap:** 28.4979 on SNAKE_L, reproducing R64's frozen value exactly.
- **Fresh nulls ≥ K4:** **0/300**, p = 1/301 = 0.0033. The null gaps have median 5.16, 99th percentile 20.45 and
  maximum 27.81.
- **Pooled with R64's 100 nulls:** 0/400, p = 0.0025.
- **Witnesses:** 45,150 raw stage-1 witnesses re-encrypt through their routes.

### Exploratory decomposition (after the evaluation; frozen numbers only, no published letters)
| Stage-1 quantity | K4 | Nulls ≥ K4 (of 300) |
|---|---|---|
| Best route total (SNAKE_L) | −320.9 | 4 |
| Second-best route total | −349.4 | 247 |
| Median of the 10 route totals | −360.8 | 272 |

- **Both halves contribute:** SNAKE_L is unusually good, and K4's other 9 routes are slightly worse than the shuffles'.
- **It is SNAKE_L in particular:** the mirror reading SNAKE_R scores −360.5, and K4 in its carved order scores −357.3
  under the same settings.

## R65b (`r65/FOLLOWUP_PREREGISTRATION.md`, pushed in 9fb8e9d before computing)
- **Statistic:** the best of 6 conventions of the order-6 letter-model score of the two implied key fragments (13 and 11
  letters), against 10,000 random permutations of K4 (seed 650071).

| Hypothesis | Route | Key language | Best convention | Score | Null median / 99th pct / max | p | Outcome |
|---|---|---|---|---|---|---|---|
| H1 | SNAKE_L | German | AZ_BEAU | −41.50 | −45.55 / −40.00 / −36.26 | 0.040 | **NOT LANGUAGE-LIKE** |
| H2 | COL_LT | English | KRY_BEAU | −46.34 | −44.19 / −38.97 / −31.72 | 0.905 | **NOT LANGUAGE-LIKE** |

**Implied key fragments (raw; `r65/k4/IMPLIED_KEY_CHECK.json`):**
```
H1 SNAKE_L  AZ_VIG   BITVFNUBACOFV MUYGSPITGYK      H2 COL_LT  AZ_VIG   FUIUAHVWZVCSH TQJZGTJDRUH
            AZ_BEAU  JIDHFPCNOKOPH OCGCIPMPICE                 AZ_BEAU  NUSGAJDINDCCT VYRVWTNZTYB
            AZ_VARB  ZSHFVNGZAYMVF OGCUILSHUCQ                 AZ_VARB  VGSGATFEBFYIT HKRBUHRXJGT
            KRY_VIG  RBERGPJLKYXMR ELYDMJLQJXU                 KRY_VIG  OHRIKLLZZHYQP GDSCJQBHAHR
            KRY_BEAU WVWCZGMZYXFTC RGTMVYCYKJU                 KRY_BEAU RYGWFRNARDJSE PSBLQSKVLSR
            KRY_VARB ZMIZGWDCKXYBZ ICXJBDCSDYO                 KRY_VARB UFZEKCCRRFXSW GJQLDSMFNFZ
```

## What this means
- **The SNAKE_L effect is a real property of K4's letter order** under that reading (STAT).
- **Rejected with high power (STAT, not an exact exclusion), given the published letters:** a running key whose key
  text is German, combined with SNAKE_L, under any of the 6 conventions, with ordinary English plaintext. The same for
  an English key with COL_LT.
  - The check needs no solver, only letter statistics of the 24 implied key letters. Its power is measured below.
  - *Correction (4 Nov 2026, after ChatGPT's R67 review on PR #50):* an earlier version said "Excluded" and the
    ledger said "EXCLUDED". p = 0.040 is a statistical rejection, not a mathematical exclusion.
- **Not explained:** what structure the German model is picking up. One possibility: K4's sequence is not a random
  arrangement of its letters, and SNAKE_L keeps more of whatever process made it than the K3-style rotations do.
  Shuffled copies are a weak null for any real, structured cipher.
- **Suggested only, not run:** a structure-preserving null, e.g. ciphertexts from other known keyed systems of the same
  length, would show whether any real ciphertext shows such gaps.

## Addendum (4 Nov 2026, post hoc): power of R65b (`r65/sealed/implied_key_power.py`, `r65/k4/IMPLIED_KEY_POWER.json`)
- **Question:** if K4 really were a German running key on SNAKE_L, would R65b have passed it?
- **Method:** real German key fragments at the published-position spacing (13 letters, then 11 starting 42 later),
  scored exactly as R65b scores them. 2,000 random windows of each source, seed 7.

| Key text | Median score | Lowest score | Share at or above R65b's 1% bar (−40.00) | Share at or above K4's −41.50 |
|---|---|---|---|---|
| Europarl file 10 (modern; unseen by the model's training) | −18.2 | −35.3 | 100% | 100% |
| Thomas Mann, *Der Tod in Venedig* (1912, old spelling) | −23.8 | −37.0 | 100% | 100% |

- **R65b has essentially full power against a German key**, modern or old-spelling.
  - R64's low literary-German power (2/6) concerned its blind solver, which must reconstruct the whole key. R65b
    only scores 24 key letters that the published plaintext forces.
  - K4's best implied fragments (−41.50) score below every one of the 4,000 real German samples.
- **Remaining caveats:** a German key text unlike either source (for example lists of names or numbers spelled out);
  plaintext not ordinary English at the published positions; conventions outside the 6 tested.
