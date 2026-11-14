#!/usr/bin/env python3
"""R82 NATURAL-PROSE development pilot, not a new sealed test or K4 run.

Source: 80 already-revealed SYNTHETIC R81a positive-plaintext controls
from Silas Marner and Main Street (a separate cipher round).
NO K4 ciphertext or any published K4 plaintext/clue is loaded.
The same 16 plaintexts are intentionally reused across each m,w
cell; these are *correlated spent controls*, not fresh holdouts.
The solver knows the cipher method, exact m, width and alphabets,
but not the keyword or plaintext. It is only a developer pilot.

Also score WRONG-FAMILY ordinary repeating-key cipher (old R79 family)
using the linked-key solver's full search, to expose false attribution.
Run with repo available: python3 -I r82/natural_pairwise_pilot.py
"""
from pathlib import Path
import json
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import models as M
import linked_key as LK
import pairwise_pilot as P

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "r81a" / "holdout" / "sealed_truth.json"
CONF = ((4,4),(5,5),(7,7),(9,9),(9,11),(9,31),(5,31),(12,31))
N = 16
RNG = np.random.default_rng(830823)
P.RNG = RNG


def recover(ct, m, w):
    codes = np.array([M.AZ.index(x) for x in ct], dtype=int)
    unary, edges = P.factors(codes, m, w)
    proposed, ll = P.solve(unary, edges, restarts=12, steps=100)
    decoded = "".join(
        M.AZ[int(P.DECODE[codes[i], proposed[i%m], proposed[(i+i//w)%m]])]
        for i in range(len(ct)))
    return proposed, float(ll), decoded


def main():
    truth = json.loads(SOURCE.read_text())
    positives = sorted((v["pt"],k) for k,v in truth.items()
                       if v.get("kind","").startswith("POS") and "pt" in v)
    assert len(positives) == 80
    assert all(len(p)==97 and set(p)<=set(M.AZ) for p,_ in positives)
    rows = []
    for m,w in CONF:
        recovered_keys, recovered_full, recovered_95 = 0,0,0
        partials, scores, wrong_scores, wrong_exact = [], [], [], 0
        for j in range(N):
            pt, source_id = positives[(j + 13 * m + w) % len(positives)]
            key = "".join(M.AZ[int(RNG.integers(26))] for _ in range(m))
            first = M.Stage("AZ","KRY",key)
            second = M.Stage("AZ","AZ",key)
            linked = LK.encrypt(pt, first, second, w)
            assert LK.decrypt(linked,first,second,w)==pt
            guessed, ll, candidate = recover(linked,m,w)
            guessed_key = "".join(M.AZ[int(v)] for v in guessed)
            right = sum(a==b for a,b in zip(candidate,pt))
            recovered_keys += guessed_key == key
            recovered_full += right == 97
            recovered_95 += right >= 95
            partials.append(right)
            scores.append(ll/97)

            # Same source, same m and key, but a simpler single-stage
            # cipher. The new solver must NOT confidently misidentify
            # these old-family controls as linked-key successes.
            simple = M.stage_encrypt(pt, first)
            _, wrong_ll, wrong_plain = recover(simple,m,w)
            wrong_scores.append(wrong_ll/97)
            wrong_exact += wrong_plain == pt
        rows.append({
            "m":m,"w":w,"n":N,"key_exact":recovered_keys,
            "plain_97":recovered_full,"plain_ge95":recovered_95,
            "mean_correct_letters":sum(partials)/N,
            "min_correct_letters":min(partials),
            "linked_model_score_per_char_mean":float(np.mean(scores)),
            "wrong_single_vigenere_score_per_char_mean":float(np.mean(wrong_scores)),
            "wrong_single_vigenere_score_per_char_max":max(wrong_scores),
            "linkeds_at_or_below_max_wrong":sum(x <= max(wrong_scores) for x in scores),
            "wrong_family_exact_plaintext_count":wrong_exact,
        })
        print(f"m={m} w={w}: key {recovered_keys}/{N}, full {recovered_full}/{N}, "+
              f"mean letters {sum(partials)/N:.1f}, link score {np.mean(scores):.3f}, "+
              f"old-method score {np.mean(wrong_scores):.3f}",flush=True)
    out = {
        "label":"Exploratory R82 natural-prose developer pilot, NOT fresh/independent holdout, NO K4",
        "source":"r81a/holdout/sealed_truth.json: 80 previously revealed POS ciphertext controls; only pt read",
        "seed":830823,"controls_per_cell":N,
        "fixed_cipher":"first AZ->KRY, then AZ->AZ, VIG, shared K with second-stage row rotation",
        "false_family":"single stage AZ->KRY Vigenere with same keyword",
        "solver":"known m/w/alphabet, unknown keyword; 12 starts x 100 annealing moves, iid unigram scorer",
        "rows":rows,
    }
    print("JSON_RESULT="+json.dumps(out,sort_keys=True))


if __name__=="__main__":
    main()
