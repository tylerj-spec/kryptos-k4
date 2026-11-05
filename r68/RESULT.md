# R68 result (Claude Code, 5 Nov 2026): no classic keyed cipher whose key follows a carved path

**No K4 solution and no contenders.**
- **Blind search:** NO SIGNAL in all four families. No frozen decode matches more than 6/24 published letters, which is
  the nulls' median.
- **Exact check:** Gromark is excluded outright. Periodic keys up to period 25 and ciphertext autokey up to lag 71 are
  excluded on every path, model and convention.
- **Not done:** no external checker was contacted.

## Plain words
- **The question:** after R67 found real, unexplained structure along SNAKE_L, R68 tested the classic hand ciphers whose
  key advances letter by letter along a path through the carved 4+31+31+31 text:
  - periodic keys (Vigenère / Beaufort / variant, with the KRYPTOS alphabet on either side);
  - Gromark;
  - ciphertext autokey;
  - plaintext autokey.
- **Paths and models:** the carved order and the 10 R61 routes, under two models:
  - **M1:** encrypt, then rearrange along the path (as in R61/R64);
  - **M2:** each letter is enciphered in place while the key follows the path. This matches Sanborn's literal statement
    that carved letters 64–69 decode to BERLIN.
- **The test works:** on 24 hidden messages it recovered 21, almost always with the exact path, model, convention and
  key:
  - Gromark 6/6;
  - ciphertext autokey 6/6;
  - periodic 5/6 (all periods ≤ 12);
  - plaintext autokey 4/6 (all lags ≤ 12).
- **K4 shows nothing:**
  - its best decode in every family scores like its shuffled copies;
  - across all 2,016 frozen K4 decodes, the best match is 6 of the 24 published letters, and 90 of 100 shuffles do at
    least as well;
  - the exact check against the published letters rules almost all of these ciphers out regardless of the search.

## Steps (`r68/PREREGISTRATION.md`)
| Step | Commit | Result |
|---|---|---|
| Development | b2f8b8c, 68cf7f8 | 6/6 for PER/GRO/CTAK; PTAK limited at long lags; restarts raised to 20 |
| Pre-registration | 648ac72 | — |
| Holdout generated (truth withheld; sha256 recorded) | 3aae3ab | 24 plants + 24 nulls |
| Holdout freeze / verify | e84c420 / aee09b0 | 49,392 witnesses valid |
| Holdout gate (truth hash matched) | 5e9e8db | **PASSED** all four families |
| K4 target (K4 + 100 shuffles, seed 680070) | bfcefa9 | — |
| K4 freeze / verify | cd02a27 / 1ca3cfc | 103,929 witnesses valid |
| Reveal, contender screen, exact check | this commit | **NO SIGNAL**; 0 contenders; EXCL as below |

## Holdout gate
| Family | Recovered (bar) | Exact setting | Params ≤ 12 | Params > 12 | Null maximum |
|---|---|---|---|---|---|
| PER (p 2–20) | **5/6** (3) | 4/6 | 5/5 | 0/1 | −324.0 |
| GRO | **6/6** (5) | 6/6 | — | — | −476.0 |
| CTAK (L 1–24) | **6/6** (5) | 6/6 | 4/4 | 2/2 | −413.3 |
| PTAK (L 1–24) | **4/6** (2) | 4/6 | 4/4 | 0/2 | −323.8 |

Recovered plants scored −182 to −127. Both models were recovered, on 8 of the 11 paths (including SNAKE_R).

## K4, blind search (primary)
| Family | K4 best total (where) | Nulls ≥ K4 | Published letters | Outcome |
|---|---|---|---|---|
| PER | −329.1 (SNAKE_L, M1, KRY/AZ_BEAU, p 20) | 3/100 | 2/24 | NO SIGNAL |
| GRO | −492.5 | 65/100 | 1/24 | NO SIGNAL |
| CTAK | −447.6 | 68/100 | 0/24 | NO SIGNAL |
| PTAK | −333.1 | 40/100 | 2/24 | NO SIGNAL |

- **Contender screen:** the best match over all 2,016 frozen K4 decodes is **6/24**. It uses the M1 literal reading as
  well as plaintext positions.
  - Nulls' best: median 6, maximum 9. 90 of 100 nulls reach 6.
  - **Decodes with ≥ 12/24: 0.**
- **On the period-20 SNAKE_L result:** with 20 free shifts over 97 letters the fit is loose. It does not beat every null,
  and it reads as word salad.

**Raw K4 outputs (best per family, unedited):**
```
PER   SNDSLATVATTOGETHISRUNIFFLAUUNDISSGOFTMATETYORIWALLYENJOYMERHAINDADOSEALKPAMEJOINMERKSINKLASITISFO
GRO   ETBOOUNVAADVDRYATEUXACTIXGAMDXQFOFEXIETZQOKEVREMEOMTRAWFUDOECBAIGKVTOIDOHORAFOXOVVPMYIBCNWEFZJHEK
CTAK  KOTHRULENDUJOPFROFSPANXXVGSEQUIVDOWPLAQUPTWOCJBCDAZEAFUNVFOIQAGLAJDZUKOLQICUMWEIONOTCOPVANQULEIFO
PTAK  DUKBLONRAPYANYCLOSTLUCKAGTOWNATRUEHADEXTRABBANIBOTHRADMEMIREHUGHLAHAPALSAUNOBOOTWAGOLANDODETHSKET
```

## Exact check (after the freeze; `r68/k4/EXACT.json`)
- **What was checked:** every path (11) × model (2) × convention (12), against the 24 published letters at their
  plaintext positions.

| Family | Range checked | K4 feasible (non-vacuous) | Nulls (median / max) | Exact conclusion for K4 |
|---|---|---|---|---|
| GRO | all 100,000 primers | **0** | 0 / 0 | **EXCL** entirely |
| PER | p 1–48 | 15, all with p 26–43 and < 8 checks | 23 / 60 | **EXCL for every p ≤ 25** |
| CTAK | L 1–96 | 15, all with L 72–96 and < 8 checks | 12 / 24 | **EXCL for every L ≤ 71** |
| PTAK | L 1–96 | 38, each with only 1–2 checks | 46 / 67 | weak exact check: published letters rarely sit L apart; the blind search covers L ≤ 12 with power |

## What this rules out, and what it does not
- **EXCL (exact):** K4 as ordinary English plaintext through:
  - a Gromark of any primer;
  - a periodic key of period ≤ 25;
  - a ciphertext autokey of lag ≤ 71;

  each in any of the 12 conventions, with the key advancing along the carved order or any of the 10 R61 routes, under
  either model.
- **STAT (blind, with power):** plaintext autokey with lag ≤ 12 on the same paths. No sign.
- **Not covered:**
  - other paths;
  - free (unknown) alphabets;
  - irregular key resets;
  - running keys from specific named texts along these paths;
  - masking;
  - non-English plaintext.
- **The SNAKE_L structure (R65/R67) is not explained by any of these ciphers.**
