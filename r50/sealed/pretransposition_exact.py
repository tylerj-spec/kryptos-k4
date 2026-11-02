#!/usr/bin/env python3
"""R50 sealed, exact postfreeze T_then_S algebraic screen. NOT a K4 decryptor.

24 artist-confirmed K4 letters are used *only* here to test exact necessary and
sufficient feasibility of finite, preregistered substitution families. Original
K4 ciphertext has no altered letters or positional holes. No guesses at the
other 73 plaintext positions, score, crib fitting or web submissions.
"""
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "k4kit" / "tools"))
sys.path.insert(0, str(ROOT / "r45" / "sealed"))
sys.path.insert(0, str(ROOT / "r46" / "sealed"))
from k4common import K4, ANCH, AZ, gromark_key  # noqa: E402
from keyword_exact import (candidates, kw_alpha, digest, invert_alphabet,
                           fixed_pa, fixed_ca, possible, load_plant_controls,
                           forward)  # noqa: E402
from k3_keyword_exact import ROUTES, transposition  # noqa: E402

PROTOCOL = "95d7d957c593f7cc952a41ecc83a04bafe31785a802eee05bb583c4e2213913f"
ORIGINAL_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
THEMED = ("KRYPTOS PALIMPSEST ABSCISSA BERLIN SHADOW EGYPT CARTER "
          "LANGLEY SANBORN SCHEIDT ILLUSION UNDERGROUND MAGNETIC "
          "POSITION WELTZEITUHR").split()
PREFILTER_PAIRS = 6


def kw_list():
    common = candidates(ROOT / "k4kit/data/word_model_orth.tsv")
    assert len(common) == 4749
    seen = {a for a, _ in common}
    extra = []
    for w in THEMED:
        a = kw_alpha(w)
        if a not in seen:
            extra.append((a, w))
            seen.add(a)
    return [(a, w, "COMMON", invert_alphabet(a)) for a, w in common], [
        (a, w, "THEMED", invert_alphabet(a)) for a, w in extra
    ]


def remap_anchors(perm, truth=ANCH):
    """The *input* Q[j] to substitution is P[perm[j]], not P[j]."""
    assert sorted(perm) == list(range(97))
    q = {j: truth[i] for j, i in enumerate(perm) if i in truth}
    assert len(q) == 24
    return q


def choose_pairs(ct, mask, orient):
    ids = sorted(mask)
    if orient == "KW_PA":
        pairs = [(i, j) for i in ids for j in ids if j > i and ct[i] == ct[j]]
    else:
        pairs = [(i, j) for i in ids for j in ids if j > i and mask[i] == mask[j]]
    return pairs[:PREFILTER_PAIRS]


class KeywordIndex:
    """Exact difference signature = necessary, final fixed_X injectivity = sufficient."""
    def __init__(self, ct, mask, words, orient):
        self.ct, self.mask, self.orient = ct, mask, orient
        self.words = words
        self.pairs = choose_pairs(ct, mask, orient)
        self.index = defaultdict(list)
        for alpha, word, class_name, inverse in words:
            if orient == "KW_PA":
                signature = tuple((inverse[mask[i]] - inverse[mask[j]]) % 26
                                  for i, j in self.pairs)
            else:
                signature = tuple((inverse[ct[i]] - inverse[ct[j]]) % 26
                                  for i, j in self.pairs)
            self.index[signature].append((alpha, word, class_name, inverse))
        assert sum(map(len, self.index.values())) == len(words)

    def signature(self, key, sign):
        if self.orient == "KW_PA":
            return tuple(sign * (key[j] - key[i]) % 26 for i, j in self.pairs)
        return tuple(sign * (key[i] - key[j]) % 26 for i, j in self.pairs)

    def matches(self, key, sign):
        result = []
        for alpha, word, class_name, inverse in self.index.get(self.signature(key, sign), []):
            valid = (fixed_pa(self.ct, key, self.mask, inverse, sign) if self.orient == "KW_PA"
                     else fixed_ca(self.ct, key, self.mask, inverse, sign))
            if valid:
                result.append((alpha, word, class_name))
        return result

    def brute(self, key, sign):
        result = []
        for alpha, word, class_name, inverse in self.words:
            valid = (fixed_pa(self.ct, key, self.mask, inverse, sign) if self.orient == "KW_PA"
                     else fixed_ca(self.ct, key, self.mask, inverse, sign))
            if valid:
                result.append((alpha, word, class_name))
        return result


def direct_controls(common, extra, permutations):
    """20 ALREADY REVEALED R44b messages, positive algebra only, never blind holds."""
    originals = load_plant_controls()
    assert len(originals) == 20
    indexed_common = {(alpha, word) for alpha, word, _, _ in common}
    counts = {"KW_PA": 0, "KW_CA": 0, "plus": 0, "minus": 0}
    wrong_order_rejected = 0
    samples = []
    for j, case_id in enumerate(sorted(originals)):
        original_ct, key, v = originals[case_id]
        pt = v["plaintext"]
        assert len(original_ct) == 97 and len(pt) == 97
        route_name = ROUTES[j % len(ROUTES)]
        perm, invperm = permutations[route_name]
        assert [perm[invperm[i]] for i in range(97)] == list(range(97))
        q = "".join(pt[perm[z]] for z in range(97))
        sign = +1 if j % 4 in (0, 1) else -1
        rng = random.Random(50000 + j)
        if j % 2 == 0:
            pa, ca = v["plaintext_alphabet"], v["ciphertext_alphabet"]
            assert (pa, v["keyword"]) in indexed_common
            kind = "KW_PA"
            kw = pa
        else:
            pa_chars = list(AZ)
            rng.shuffle(pa_chars)
            pa = "".join(pa_chars)
            ca = common[rng.randrange(len(common))][0]
            kind = "KW_CA"
            kw = ca
        ct = forward(q, key, pa, ca, sign)
        got_q = "".join(pa[(invert_alphabet(ca)[c] - sign * key[z]) % 26] for z, c in enumerate(ct))
        restored = "".join(got_q[invperm[i]] for i in range(97))
        assert restored == pt
        assert forward("".join(restored[perm[z]] for z in range(97)), key, pa, ca, sign) == ct
        shifted = remap_anchors(perm, {i: pt[i] for i in ANCH})
        assert possible(key, ct=ct, anch=shifted, sign=sign)
        inv = invert_alphabet(kw)
        if kind == "KW_PA":
            assert fixed_pa(ct, key, shifted, inv, sign)
        else:
            assert fixed_ca(ct, key, shifted, inv, sign)
        words = common + extra
        idx = KeywordIndex(ct, shifted, words, kind)
        matched = set(idx.matches(key, sign))
        assert any(a == kw for a, _, _ in matched), f"positive {case_id} key not found by index"
        assert set(idx.brute(key, sign)) == matched
        if kind == "KW_PA":
            wrong_order = fixed_pa(ct, key, {i: pt[i] for i in ANCH}, invert_alphabet(pa), sign)
        else:
            wrong_order = fixed_ca(ct, key, {i: pt[i] for i in ANCH}, invert_alphabet(ca), sign)
        wrong_order_rejected += not wrong_order
        counts[kind] += 1
        counts["plus" if sign == 1 else "minus"] += 1
        samples.append({"id":case_id,"route":route_name,"sign":sign,"orientation":kind,
                        "T_then_S_ciphertext_sha256":hashlib.sha256(ct.encode()).hexdigest()})
    assert counts == {"KW_PA": 10, "KW_CA": 10, "plus": 10, "minus": 10}, counts
    assert wrong_order_rejected >= 1, "wrong T/S order control did not distinguish models"
    return {"counts": counts,"wrong_order_true_keyword_rejected":wrong_order_rejected,"samples":samples}


def evaluate_one(ct, route_name, perm, common, themed):
    anchors = remap_anchors(perm)
    words = common + themed
    ip = KeywordIndex(ct, anchors, words, "KW_PA")
    ic = KeywordIndex(ct, anchors, words, "KW_CA")
    keys = []
    settings = []
    for primer in range(100000):
        key = gromark_key(primer)
        if not possible(key, ct=ct, anch=anchors, sign=+1):
            continue
        assert possible(key, ct=ct, anch=anchors, sign=-1), "both-free sign symmetry"
        keys.append(f"{primer:05d}")
        for sign in (+1, -1):
            for idx, model in ((ip,"KW_PA_FREE_CA"),(ic,"FREE_PA_KW_CA")):
                for alpha, word, keyword_class in idx.matches(key, sign):
                    settings.append({"family":model,"primer":f"{primer:05d}",
                                     "keyword":word,"keyword_alphabet":alpha,
                                     "keyword_class":keyword_class,"sign":sign})
    # Independently fully unindexed recheck of the first THREE 2-free keys,
    # both +/- directions and both alphabet orientations, the ENTIRE vocabulary.
    brute_cases = keys[:3]
    for pstr in brute_cases:
        key = gromark_key(int(pstr))
        for sign in (+1, -1):
            for idx in (ip, ic):
                assert set(idx.matches(key, sign)) == set(idx.brute(key, sign)), (
                    f"index false negative {route_name=} {pstr=} {sign=} {idx.orient=}"
                )
    settings.sort(key=lambda d: (d["family"],d["keyword_class"],d["primer"],
                                 d["keyword_alphabet"],d["sign"]))
    counter = {f"{source}_{orient}":sum(x["keyword_class"] == source and x["family"] == orient
                                      for x in settings)
               for source in ("COMMON","THEMED")
               for orient in ("KW_PA_FREE_CA","FREE_PA_KW_CA")}
    return {"free_both_primers":keys,"two_free_count":len(keys),
            "keyword_counts":counter,"all_settings":settings,
            "anchor_indices_in_substitution_order":sorted(anchors),
            "index_pair_counts":{"KW_PA":len(ip.pairs),"KW_CA":len(ic.pairs)},
            "direct_brute_crosscheck_primers":brute_cases}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -I r50/sealed/pretransposition_exact.py OUT.json")
    out = Path(sys.argv[1])
    if out.exists():
        raise RuntimeError("refusing to overwrite any R50 result")
    assert digest(ROOT / "r50/PREREGISTRATION.md") == PROTOCOL
    assert (ROOT / "r50/PROTOCOL.sha256").read_text().split()[0] == PROTOCOL
    original_path = ROOT / "r39/ic_gate/k4_ciphertext.txt"
    assert digest(original_path) == ORIGINAL_SHA
    ct = original_path.read_text().strip()
    assert ct == K4 and len(ct) == 97
    assert (ROOT / "r44/holdout_b/FROZEN.sha256").exists()
    assert (ROOT / "r45/R45_RESULT.sha256").exists()
    assert (ROOT / "r46/PROTOCOL.sha256").exists()
    common, extra = kw_list()
    print("R50 vocabulary common",len(common),"novel themed",len(extra),flush=True)
    perms = {nm:transposition(nm) for nm in ROUTES}
    controls = direct_controls(common, extra, perms)
    print("R50 positive algebra controls",controls["counts"],
          "wrong order rejected", controls["wrong_order_true_keyword_rejected"],flush=True)
    originals = {}
    for route_name in ROUTES:
        perm, inverse = perms[route_name]
        assert sorted(perm) == sorted(inverse) == list(range(97))
        original = evaluate_one(ct, route_name, perm, common, extra)
        originals[route_name] = original
        print("R50 K4",route_name,"two free",original["two_free_count"],
              "keyword",original["keyword_counts"],flush=True)
    nulls = []
    for j in range(2):
        shuffled = list(ct)
        random.Random(50100 + j).shuffle(shuffled)
        null_ct = "".join(shuffled)
        routes = {}
        for route_name in ROUTES:
            x = evaluate_one(null_ct, route_name, perms[route_name][0], common, extra)
            routes[route_name] = x
            print("R50 null",j,route_name,"two free",x["two_free_count"],
                  "keyword",x["keyword_counts"],flush=True)
        nulls.append({"seed":50100+j,"ciphertext_sha256":hashlib.sha256(null_ct.encode()).hexdigest(),
                      "by_route":routes})
    hits = sum(len(r["all_settings"]) for r in originals.values())
    result = {
        "type":"R50_POSTFREEZE_T_then_S_K3_exact_pub24_letter_feasibility_NOT_BLIND_K4_DECRYPTION",
        "protocol_sha256":PROTOCOL,
        "source_sha256":digest(Path(__file__)),
        "K4_ciphertext_sha256_with_newline":ORIGINAL_SHA,
        "dictionary_sha256":digest(ROOT / "k4kit/data/word_model_orth.tsv"),
        "routes":ROUTES,"T_then_S":True,"primer_count_each":100000,
        "arithmetic_signs":[+1,-1],
        "keyword_class_counts":{"COMMON":len(common),"THEMED_EXTRA":len(extra)},
        "themed_words_declared":THEMED,
        "positive_controls":controls,
        "K4_routes":originals,"nulls":nulls,
        "K4_total_keyword_feasible":hits,
        "classification":("EXCL the exactly pre-registered four T_then_S routes and one-keyword one-free 5-digit Gromark family"
                          if hits == 0 else
                          "FEAS ONLY: 24 published K4 letters used as a filter; no independent plaintext"),
        "warnings":[
            "No missing K4 plaintext was reconstructed, no unsupplied key was recovered.",
            "Positive plants were already revealed, not fresh blind recovery controls.",
            "A hit is tautologically 24-letter compatible, NOT proof of decipherment.",
            "No Berlin World Clock source material was used."
        ]
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print("R50 total K4 keyword-feasible",hits,"classification",result["classification"],flush=True)


if __name__ == "__main__":
    main()
