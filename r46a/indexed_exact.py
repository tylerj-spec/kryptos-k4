#!/usr/bin/env python3
"""R46A SEALED exact optimization, preserving R46 frozen scientific family.

This code sees public 24-letter known K4 positions ONLY for mathematical
feasibility. It never builds or claims unknown K4 plaintext.

Optimization is a necessary equality signature index over alphabet candidates;
the full R45 fixed_pa/fixed_ca checks still run for every indexed survivor.
"""
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "k4kit" / "tools"))
sys.path.insert(0, str(ROOT / "r45" / "sealed"))
sys.path.insert(0, str(ROOT / "r46" / "sealed"))
from k4common import K4, ANCH, gromark_key  # noqa
from keyword_exact import (candidates, digest, fixed_pa, fixed_ca,
                           invert_alphabet, possible)  # noqa
from k3_keyword_exact import (transposition, cipher_layer, test_controls,
                              ROUTES, EXPECTED_PROTOCOL, EXPECTED_CT)  # noqa

HERE = Path(__file__).resolve().parent
SIX = 6


def keyword_list():
    return [(a, w, invert_alphabet(a))
            for a, w in candidates(ROOT / "k4kit/data/word_model_orth.tsv")]


def chosen_pairs(ct, orientation):
    indices = sorted(ANCH)
    if orientation == "KW_PA":
        pairs = [(i, j) for i in indices for j in indices
                 if j > i and ct[i] == ct[j]]
    else:
        pairs = [(i, j) for i in indices for j in indices
                 if j > i and ANCH[i] == ANCH[j]]
    return pairs[:SIX]


class KeywordIndex:
    def __init__(self, ct, kw, orientation):
        self.ct, self.orientation = ct, orientation
        self.pairs = chosen_pairs(ct, orientation)
        self.table = defaultdict(list)
        for a, w, inv in kw:
            if orientation == "KW_PA":
                feat = tuple((inv[ANCH[i]] - inv[ANCH[j]]) % 26
                             for i, j in self.pairs)
            else:
                feat = tuple((inv[ct[i]] - inv[ct[j]]) % 26
                             for i, j in self.pairs)
            self.table[feat].append((a, w, inv))
        assert sum(map(len, self.table.values())) == len(kw)

    def candidates(self, key, sign):
        if self.orientation == "KW_PA":
            sig = tuple((sign * (key[j] - key[i])) % 26
                        for i, j in self.pairs)
        else:
            sig = tuple((sign * (key[i] - key[j])) % 26
                        for i, j in self.pairs)
        return self.table.get(sig, [])

    def matches(self, key, sign):
        if self.orientation == "KW_PA":
            return [(a, w) for a, w, inv in self.candidates(key, sign)
                    if fixed_pa(self.ct, key, ANCH, inv, sign)]
        return [(a, w) for a, w, inv in self.candidates(key, sign)
                if fixed_ca(self.ct, key, ANCH, inv, sign)]

    def brute(self, key, sign, all_keywords):
        if self.orientation == "KW_PA":
            return [(a, w) for a, w, inv in all_keywords
                    if fixed_pa(self.ct, key, ANCH, inv, sign)]
        return [(a, w) for a, w, inv in all_keywords
                if fixed_ca(self.ct, key, ANCH, inv, sign)]


def evaluate(ct, kw, route_name):
    IPA = KeywordIndex(ct, kw, "KW_PA")
    ICA = KeywordIndex(ct, kw, "KW_CA")
    possible_count = 0
    best_key_samples = []
    found = []
    for primer in range(100000):
        key = gromark_key(primer)
        if not possible(key, ct=ct, anch=ANCH, sign=1):
            continue
        if not possible(key, ct=ct, anch=ANCH, sign=-1):
            raise AssertionError("two-free +/- reflection failed")
        possible_count += 1
        if len(best_key_samples) < 3:
            best_key_samples.append(primer)
        for sign in (+1, -1):
            for index, model in ((IPA, "KW_PA_FREE_CA"),
                                 (ICA, "FREE_PA_KW_CA")):
                for alpha, word in index.matches(key, sign):
                    found.append({
                        "family": model,
                        "primer": f"{primer:05d}",
                        "keyword": word,
                        "keyword_alphabet": alpha,
                        "sign": sign,
                    })
    # Sample direct full unindexed scans serve as an algebraically independent
    # check of the exact index. Since a shortlist could miss, full scan only
    # on validation samples is not used to determine ANY K4 count.
    for primer in best_key_samples:
        k = gromark_key(primer)
        for sign in (+1, -1):
            for index in (IPA, ICA):
                a = set(index.matches(k, sign))
                b = set(index.brute(k, sign, kw))
                assert a == b, (
                    "indexed keyword filter differs from full scan "
                    f"for route {route_name} key {primer} sign {sign} "
                    f"orientation {index.orientation} miss={len(b-a)} "
                    f"false_hit={len(a-b)}"
                )
    found.sort(key=lambda x: (
        x["family"], x["primer"], x["keyword_alphabet"], x["sign"]
    ))
    return {
        "free_both_primer_count": possible_count,
        "free_both_primers": None,  # Complete set is tracked below and filled before return.
        "keyword_PA_matches": sum(x["family"] == "KW_PA_FREE_CA" for x in found),
        "keyword_CA_matches": sum(x["family"] == "FREE_PA_KW_CA" for x in found),
        "all_settings": found,
        "index_diagnostics": {
            "route": route_name,
            "pairs_PA": IPA.pairs,
            "pairs_CA": ICA.pairs,
            "unique_signature_buckets_PA": len(IPA.table),
            "unique_signature_buckets_CA": len(ICA.table),
            "full_scan_crosscheck_primers": [f"{p:05d}" for p in best_key_samples],
        },
    }


def evaluate_full(ct, kw, route_name):
    IPA = KeywordIndex(ct, kw, "KW_PA")
    ICA = KeywordIndex(ct, kw, "KW_CA")
    keys = []
    matches = []
    for primer in range(100000):
        key = gromark_key(primer)
        if not possible(key, ct=ct, anch=ANCH, sign=1):
            continue
        assert possible(key, ct=ct, anch=ANCH, sign=-1)
        keys.append(f"{primer:05d}")
        for sign in (+1, -1):
            for index, model in ((IPA, "KW_PA_FREE_CA"),
                                 (ICA, "FREE_PA_KW_CA")):
                for alpha, word in index.matches(key, sign):
                    matches.append({
                        "family": model,
                        "primer": f"{primer:05d}",
                        "keyword": word,
                        "keyword_alphabet": alpha,
                        "sign": sign,
                    })
    for pstr in keys[:3]:
        key = gromark_key(int(pstr))
        for sign in (+1, -1):
            for idx in (IPA, ICA):
                assert set(idx.matches(key, sign)) == set(idx.brute(key, sign, kw))
    matches.sort(key=lambda x: (
        x["family"], x["primer"], x["keyword_alphabet"], x["sign"]
    ))
    return {
        "free_both_primer_count": len(keys),
        "free_both_primers": keys,
        "keyword_PA_matches": sum(x["family"] == "KW_PA_FREE_CA" for x in matches),
        "keyword_CA_matches": sum(x["family"] == "FREE_PA_KW_CA" for x in matches),
        "all_settings": matches,
        "signature_indices": {
            "kwpa_pair_count": len(IPA.pairs),
            "kwca_pair_count": len(ICA.pairs),
            "kwpa_distinct_signatures": len(IPA.table),
            "kwca_distinct_signatures": len(ICA.table),
        },
        "brute_crosscheck_primers": keys[:3],
    }


def run_all(ct, kw, perms, name):
    results = {}
    for route_name in ROUTES:
        perm, inverted = perms[route_name]
        sub = cipher_layer(ct, inverted)
        x = evaluate_full(sub, kw, route_name)
        x["substitution_layer_ciphertext_sha256"] = hashlib.sha256(sub.encode()).hexdigest()
        results[route_name] = x
        print("R46A", name, route_name, "free_both", x["free_both_primer_count"],
              "keywordPA", x["keyword_PA_matches"],
              "keywordCA", x["keyword_CA_matches"],
              "direct_crosschecks", x["brute_crosscheck_primers"], flush=True)
    return results


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -I r46a/indexed_exact.py OUT.json")
    destination = Path(sys.argv[1])
    if destination.exists():
        raise RuntimeError("refuse to overwrite existing indexed results")
    assert digest(ROOT / "r46/PREREGISTRATION.md") == EXPECTED_PROTOCOL
    assert digest(ROOT / "r39/ic_gate/k4_ciphertext.txt") == EXPECTED_CT
    assert (ROOT / "r45/R45_RESULT.sha256").exists()
    kw = keyword_list()
    perms = {name: transposition(name) for name in ROUTES}
    controls = test_controls([(a,w) for a,w,_ in kw], perms)
    print("R46A original positive controls pass", controls["counts"], flush=True)
    k4 = ROOT / "r39/ic_gate/k4_ciphertext.txt"
    ct = k4.read_text().strip()
    assert ct == K4 and len(ct) == 97
    runs = run_all(ct, kw, perms, "K4")
    nulls = []
    for j in range(2):
        cts = list(ct)
        random.Random(46100+j).shuffle(cts)
        text = "".join(cts)
        nulls.append({
            "seed": 46100+j,
            "ciphertext_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "by_route": run_all(text, kw, perms, f"NULL{j}"),
        })
    n = sum(x["keyword_PA_matches"]+x["keyword_CA_matches"] for x in runs.values())
    result = {
        "type": "R46A_INDEXED_exact_K3_S_then_T_known_letter_feasibility_NOT_DECRYPTION",
        "preexisting_R46_protocol_sha256": EXPECTED_PROTOCOL,
        "R46A_amendment_sha256": digest(HERE / "AMENDMENT.md"),
        "optimized_source_sha256": digest(Path(__file__)),
        "K4_original_sha256_with_newline": EXPECTED_CT,
        "keyword_model_sha256": digest(ROOT / "k4kit/data/word_model_orth.tsv"),
        "route_count": 4,
        "key_primers_per_route": 100000,
        "distinct_keyword_alphabets": len(kw),
        "both_signs": True,
        "both_keyword_orientations": True,
        "controls": controls,
        "K4_results_by_route": runs,
        "K4_total_feasible_keyword_settings": n,
        "nulls": nulls,
        "classification": (
            "EXCL declared four K3 S_then_T routes, both signs/orientations and all 100k decimal primers"
            if not n else "FEAS only; public 24 K4 letters were used to filter, not decryption"
        ),
        "warning": (
            "No missing K4 plaintext constructed. Correctness of keyword index checked "
            "against full unindexed scan of first three surviving primers per route per "
            "ciphertext, both orientations and signs."
        ),
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2)+"\n")
    print("R46A total K4 viable", n, "classification", result["classification"], flush=True)


if __name__ == "__main__":
    main()
