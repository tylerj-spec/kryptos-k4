#!/usr/bin/env python3
"""R46 SEALED ONLY: postfreeze exact feasibility for 24x8 S_then_T K3 rotations.
Uses 24 public plaintext letters solely as an exact exclusion / possibility oracle.
No K4 plaintext is recovered, and no published anchors are fed to a blind solver.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "k4kit" / "tools"))
sys.path.insert(0, str(ROOT / "r45" / "sealed"))
from k4common import K4, ANCH, route  # noqa: E402
from keyword_exact import (  # noqa: E402
    candidates, digest, evaluate, fixed_pa, fixed_ca, forward,
    invert_alphabet, load_plant_controls, possible
)

EXPECTED_PROTOCOL = "efcde4e8c05a91c82bb63c99483447407bf7b1623954ede7ae4e7f7c299c2e0f"
EXPECTED_CT = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
ROUTES = [
    "R24x8/CW/fwd", "R24x8/CW/inv",
    "R24x8/CCW/fwd", "R24x8/CCW/inv",
]


def transposition(name):
    perm = route(name)
    if sorted(perm) != list(range(97)):
        raise AssertionError("route is not a 97-position permutation")
    q = [None] * 97
    for j, i in enumerate(perm):
        q[i] = j
    assert all(isinstance(x, int) for x in q)
    return perm, q


def cipher_layer(ct, inverse_perm):
    assert len(ct) == 97
    return "".join(ct[inverse_perm[i]] for i in range(97))


def test_controls(kw_list, perms):
    allowed = {a for a, _ in kw_list}
    examples = load_plant_controls()
    counts = {"keyword_PA_positive": 0, "keyword_CA_mirror_positive": 0,
              "sign_plus": 0, "sign_minus": 0}
    audit_samples = []
    for j, label in enumerate(sorted(examples)):
        _ct, key, data = examples[label]
        p = data["plaintext"]
        assert len(p) == 97 and len(key) == 97
        rng = random.Random(46200+j)
        rname = ROUTES[j % len(ROUTES)]
        perm, q = perms[rname]
        sign = +1 if j % 4 in (0, 1) else -1
        if j % 2 == 0:
            pa = data["plaintext_alphabet"]
            ca = data["ciphertext_alphabet"]
            assert pa in allowed
            family = "KW_PA_FREE_CA"
        else:
            shuffled = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            rng.shuffle(shuffled)
            pa = "".join(shuffled)
            ca = kw_list[rng.randrange(len(kw_list))][0]
            family = "FREE_PA_KW_CA"
        subst = forward(p, key, pa, ca, sign)
        rotated = "".join(subst[perm[t]] for t in range(97))
        extracted = cipher_layer(rotated, q)
        assert extracted == subst, "inverse route failed"
        anch = {i: p[i] for i in ANCH}
        assert possible(key, ct=extracted, anch=anch, sign=sign), "true two-free key unexpectedly impossible"
        if family == "KW_PA_FREE_CA":
            assert fixed_pa(extracted, key, anch, invert_alphabet(pa), sign)
            counts["keyword_PA_positive"] += 1
        else:
            assert fixed_ca(extracted, key, anch, invert_alphabet(ca), sign)
            counts["keyword_CA_mirror_positive"] += 1
        counts["sign_plus" if sign == 1 else "sign_minus"] += 1
        audit_samples.append({"id": label, "route": rname, "operation_sign": sign,
                              "true_family": family,
                              "ciphertext_sha256": hashlib.sha256(rotated.encode()).hexdigest()})
    assert counts == {"keyword_PA_positive": 10, "keyword_CA_mirror_positive": 10,
                      "sign_plus": 10, "sign_minus": 10}, counts
    return {"counts": counts, "samples": audit_samples}


def run_full(ct, kw_list, permutations):
    results = {}
    for name in ROUTES:
        _perm, q = permutations[name]
        subst = cipher_layer(ct, q)
        outcome = evaluate(subst, ANCH, kw_list)
        outcome["substitution_layer_ciphertext_sha256"] = hashlib.sha256(subst.encode()).hexdigest()
        results[name] = outcome
        print("R46 route", name, "twofree", outcome["free_both_primer_count"],
              "KW_PA", outcome["keyword_PA_matches"],
              "KW_CA", outcome["keyword_CA_matches"], flush=True)
    return results


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -I r46/sealed/k3_keyword_exact.py OUT.json")
    output = Path(sys.argv[1])
    if output.exists():
        raise RuntimeError("refusing to overwrite existing R46 output")
    assert digest(ROOT / "r46" / "PREREGISTRATION.md") == EXPECTED_PROTOCOL
    assert (ROOT / "r46" / "PROTOCOL.sha256").read_text().split()[0] == EXPECTED_PROTOCOL
    original = ROOT / "r39" / "ic_gate" / "k4_ciphertext.txt"
    assert digest(original) == EXPECTED_CT
    ct = original.read_text().strip()
    assert ct == K4 and len(ct) == 97
    assert (ROOT / "r45" / "R45_EXACT_RESULT.json").exists(), "R45 result not frozen"
    assert (ROOT / "r45" / "R45_RESULT.sha256").exists(), "R45 output hash missing"
    assert (ROOT / "r44" / "holdout_b" / "FROZEN.sha256").exists(), "R44b freeze missing"
    word_path = ROOT / "k4kit" / "data" / "word_model_orth.tsv"
    kw_list = candidates(word_path)
    perms = {name: transposition(name) for name in ROUTES}
    controls = test_controls(kw_list, perms)
    print("R46 20 positive rotation controls PASS", controls["counts"], flush=True)
    primary = run_full(ct, kw_list, perms)
    nulls = []
    for j in range(2):
        shuffled = list(ct)
        random.Random(46100 + j).shuffle(shuffled)
        nullct = "".join(shuffled)
        nulls.append({
            "seed": 46100 + j,
            "ciphertext_sha256": hashlib.sha256(nullct.encode()).hexdigest(),
            "by_route": run_full(nullct, kw_list, perms)
        })
    nfeas = sum(x["keyword_PA_matches"]+x["keyword_CA_matches"] for x in primary.values())
    result = {
        "type": "K3_S_then_T_postfreeze_exact_24_letter_consistency_NOT_BLIND_DECRYPTION",
        "protocol_sha256": EXPECTED_PROTOCOL,
        "source_sha256": digest(Path(__file__)),
        "keyword_dictionary_sha256": digest(word_path),
        "K4_ciphertext_sha256_including_newline": EXPECTED_CT,
        "R45_frozen_output_sha256": digest(ROOT / "r45" / "R45_EXACT_RESULT.json"),
        "route_count": len(ROUTES), "key_primers_per_route": 100000,
        "distinct_keyword_alphabets": len(kw_list), "both_signs": True,
        "both_keyword_orientations": True, "controls": controls,
        "K4_results_by_route": primary,
        "K4_total_feasible_keyword_settings": nfeas,
        "nulls": nulls,
        "classification": ("EXCL this declared 4-route S_then_T/H-KW/decimal 5-digit model"
                           if not nfeas else
                           "FEAS only — preexisting clues filtered these hypotheses"),
        "warning": "No K4 plaintext produced. This is a postfreeze crib-assisted exact constraint test, not a blind solution."
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print("R46 K4 total feasible settings", nfeas, flush=True)
    print("R46 classification", result["classification"], flush=True)


if __name__ == "__main__":
    main()
