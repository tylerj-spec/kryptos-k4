#!/usr/bin/env python3
"""R45 SEALED ONLY — finite exact K4 keyword-alphabet consistency audit.
This is crib-assisted POSTFREEZE mathematical exclusion, NOT a blind decoder.
Does not synthesize K4 plaintext or read any unpublished K4 reconstruction.
"""
import hashlib
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "k4kit" / "tools"))
from k4common import ANCH, K4, gromark_key  # noqa: E402
from key_oracle import possible  # noqa: E402

PROTOCOL = "c9100fb08941a803877b968b73bda65bf3537a3472e2d39723c1f73c157976a1"
CANON_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kw_alpha(w):
    return "".join(dict.fromkeys(w + AZ))


def candidates(path):
    words = []
    with path.open() as fp:
        for line in fp:
            tok = line.split()
            if len(tok) != 3:
                raise ValueError("unexpected ORTH model row")
            word, score, _edit = tok
            score = float(score)
            if score > -1e90 and 5 <= len(word) <= 10:
                if not (word.isascii() and word.isalpha() and word.isupper()):
                    raise ValueError("word model unexpected token")
                words.append((-score, word))
    words.sort()  # -score ascending == exact C++ score descending; lexical ties
    assert len(words) >= 5000
    representative = {}
    for _negative_score, w in words[:5000]:
        representative.setdefault(kw_alpha(w), w)
    assert len(representative) == 4749, len(representative)
    return [(alpha, representative[alpha]) for alpha in sorted(representative)]


def invert_alphabet(alpha):
    if len(alpha) != 26 or sorted(alpha) != list(AZ):
        raise ValueError("not a full alphabet permutation")
    return {char: i for i, char in enumerate(alpha)}


def fixed_pa(ct, key, anch, pa_inverse, sign):
    """Necessary AND sufficient: fixed PA, an arbitrary injective CA mapping."""
    cipher_to_rank, used = {}, set()
    for i, plain in anch.items():
        cipher = ct[i]
        rank = (pa_inverse[plain] + sign * key[i]) % 26
        old = cipher_to_rank.get(cipher)
        if old is not None:
            if old != rank:
                return False
        else:
            if rank in used:
                return False
            cipher_to_rank[cipher] = rank
            used.add(rank)
    return True


def fixed_ca(ct, key, anch, ca_inverse, sign):
    """Necessary AND sufficient: fixed CA, an arbitrary injective PA mapping."""
    plain_to_rank, used = {}, set()
    for i, plain in anch.items():
        rank = (ca_inverse[ct[i]] - sign * key[i]) % 26
        old = plain_to_rank.get(plain)
        if old is not None:
            if old != rank:
                return False
        else:
            if rank in used:
                return False
            plain_to_rank[plain] = rank
            used.add(rank)
    return True


def forward(plain, key, pa, ca, sign):
    pinv = invert_alphabet(pa)
    return "".join(ca[(pinv[p] + sign * key[i]) % 26] for i, p in enumerate(plain))


def load_plant_controls():
    inp = ROOT / "r44" / "holdout_b" / "blind.tsv"
    truth = json.loads((ROOT / "r44" / "holdout_b" / "sealed_truth.json").read_text())
    result = {}
    for line in inp.read_text().splitlines()[1:]:
        label, ct, ks = line.split("\t")
        digits = list(map(int, ks.split(",")))
        assert len(digits) == 97 and len(ct) == 97
        result[label] = (ct, digits, truth[label])
    assert len(result) == len(truth) == 20
    return result


def test_plant_controls(kw_list):
    allowed = {a for a, word in kw_list}
    plants = load_plant_controls()
    npa = 0
    nca = 0
    for label, (ct, key, item) in plants.items():
        pt, pa, ca = item["plaintext"], item["plaintext_alphabet"], item["ciphertext_alphabet"]
        assert len(pt) == 97
        assert kw_alpha(item["keyword"]) == pa
        assert pa in allowed
        anch = {i: pt[i] for i in ANCH}
        assert forward(pt, key, pa, ca, +1) == ct
        assert possible(key, ct=ct, anch=anch, sign=+1)
        assert fixed_pa(ct, key, anch, invert_alphabet(pa), +1)
        npa += 1

        # Mirror controls: random free PA, keyword CA, both +/- signs.
        # Use the already-revealed passage ONLY as synthetic *control plaintext*.
        rng = random.Random(45200 + int(label[-2:]))
        palist = list(AZ)
        rng.shuffle(palist)
        mirror_pa = "".join(palist)
        mirror_ca = kw_list[rng.randrange(len(kw_list))][0]
        sign = +1 if npa % 2 == 0 else -1
        ct_mirror = forward(pt, key, mirror_pa, mirror_ca, sign)
        assert possible(key, ct=ct_mirror, anch=anch, sign=sign)
        assert fixed_ca(ct_mirror, key, anch, invert_alphabet(mirror_ca), sign)
        assert len(ct_mirror) == 97
        nca += 1
    return {"prior_R44b_keyword_PA_controls": npa,
            "new_keyword_CA_mirror_controls": nca,
            "mirror_operations": "10 plus, 10 minus"}


def free_survivors(ct, anch):
    """Exact prior two-free-alphabet feasibility oracle, ALL primers."""
    plus = []
    minus = []
    for primer in range(100000):
        key = gromark_key(primer)
        if possible(key, ct=ct, anch=anch, sign=+1):
            plus.append(primer)
        if possible(key, ct=ct, anch=anch, sign=-1):
            minus.append(primer)
    # Reflection of two arbitrary alphabets makes the sign sets identical.
    if plus != minus:
        raise AssertionError("both-free alphabet +/- reflection identity broken")
    return plus


def evaluate(ct, anch, kw_list):
    precandidates = free_survivors(ct, anch)
    # Every PA/CA keyword candidate must be in this complete two-free set.
    found = []
    for primer in precandidates:
        key = gromark_key(primer)
        for alpha, word in kw_list:
            ainv = invert_alphabet(alpha)
            for sign in (+1, -1):
                if fixed_pa(ct, key, anch, ainv, sign):
                    found.append({"family": "KW_PA_FREE_CA", "primer": f"{primer:05d}",
                                  "keyword": word, "keyword_alphabet": alpha, "sign": sign})
                if fixed_ca(ct, key, anch, ainv, sign):
                    found.append({"family": "FREE_PA_KW_CA", "primer": f"{primer:05d}",
                                  "keyword": word, "keyword_alphabet": alpha, "sign": sign})
    found.sort(key=lambda x: (x["family"], x["primer"], x["keyword_alphabet"], x["sign"]))
    sizes = {family: sum(x["family"] == family for x in found)
             for family in ("KW_PA_FREE_CA", "FREE_PA_KW_CA")}
    return {"free_both_primer_count": len(precandidates),
            "free_both_primers": [f"{x:05d}" for x in precandidates],
            "keyword_PA_matches": sizes["KW_PA_FREE_CA"],
            "keyword_CA_matches": sizes["FREE_PA_KW_CA"],
            "all_settings": found}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -I r45/sealed/keyword_exact.py OUTPUT.json")
    output = Path(sys.argv[1])
    protocol = ROOT / "r45" / "PREREGISTRATION.md"
    assert digest(protocol) == PROTOCOL, "pre-registered protocol changed"
    assert (ROOT / "r45" / "PROTOCOL.sha256").read_text().split()[0] == PROTOCOL
    source = ROOT / "r39" / "ic_gate" / "k4_ciphertext.txt"
    assert digest(source) == CANON_SHA, "original K4 bytes changed"
    ct = source.read_text().strip()
    assert ct == K4 and len(ct) == 97
    assert (ROOT / "r39" / "ic_gate" / "FROZEN.sha256").is_file(), "R39 freeze missing"
    assert (ROOT / "r44" / "holdout_b" / "FROZEN.sha256").is_file(), "R44b freeze missing"
    dictionary = ROOT / "k4kit" / "data" / "word_model_orth.tsv"
    kw_list = candidates(dictionary)
    controls = test_plant_controls(kw_list)
    print("R45 controls", controls, flush=True)
    results = {"type": "postfreeze_exact_known_letter_consistency_NOT_BLIND_DECRYPTION",
               "protocol_sha256": PROTOCOL, "canonical_ciphertext_sha256": CANON_SHA,
               "word_model_sha256": digest(dictionary),
               "source_sha256": digest(Path(__file__)),
               "R44b_freeze_sha256": digest(ROOT / "r44" / "holdout_b" / "FROZEN.sha256"),
               "R39_freeze_sha256": digest(ROOT / "r39" / "ic_gate" / "FROZEN.sha256"),
               "keyword_word_count": 5000, "distinct_keyword_alphabets": len(kw_list),
               "primers_exhaustively_checked": 100000, "operations": ["+k", "-k"],
               "orientations": ["KW_PA_FREE_CA", "FREE_PA_KW_CA"],
               "controls": controls}
    print("R45 evaluating unmodified original K4", flush=True)
    main_result = evaluate(ct, ANCH, kw_list)
    assert main_result["free_both_primer_count"] == 39, (
        "R45 original K4 two-free 39-primer historical cross-check failed")
    results["K4"] = main_result
    print("R45 K4 two-free primer count", main_result["free_both_primer_count"],
          "keyword_PA_matches", main_result["keyword_PA_matches"],
          "keyword_CA_matches", main_result["keyword_CA_matches"], flush=True)
    nulls = []
    for j in range(4):
        rng = random.Random(45100 + j)
        shuffled = list(ct)
        rng.shuffle(shuffled)
        n = evaluate("".join(shuffled), ANCH, kw_list)
        n["seed"] = 45100 + j
        n["null_ciphertext_sha256"] = hashlib.sha256("".join(shuffled).encode()).hexdigest()
        nulls.append(n)
        print("R45 null", j, "two-free", n["free_both_primer_count"],
              "keyword_PA", n["keyword_PA_matches"],
              "keyword_CA", n["keyword_CA_matches"], flush=True)
    results["nulls"] = nulls
    total_matches = main_result["keyword_PA_matches"] + main_result["keyword_CA_matches"]
    results["classification"] = ("EXCL (exact contradiction limited to declared H-KW five-digit"
                                  " identity-route, both-sign family)"
                                  if total_matches == 0 else
                                  "FEAS only; crib-assisted, NOT blind K4 recovery")
    results["IMPORTANT"] = ("No plaintext was produced. Published 24 letters were used solely "
                            "to test exact feasibility of a frozen, finite hypothesis family. "
                            "Do not mistake an anchor-compatible setting for a K4 solution.")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise RuntimeError("output exists: refuse overwrite")
    output.write_text(json.dumps(results, indent=2) + "\n")
    print("R45 classification", results["classification"], flush=True)


if __name__ == "__main__":
    main()
