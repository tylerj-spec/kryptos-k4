#!/usr/bin/env python3
"""R48 SEALED: test only a literal unverified physical letter packet, not a K4 solution.
Literal packet comes from a third-party field guide accompanying a fitted
plaintext reconstruction: that reconstruction is NEVER used here.
No missing K4 plaintext is generated; published 24 letters solely filter exact
necessary/sufficient keyword/free-alphabet feasibility.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "k4kit" / "tools"))
sys.path.insert(0, str(ROOT / "r45" / "sealed"))
from k4common import K4, ANCH, AZ, KRY  # noqa: E402
from keyword_exact import (  # noqa: E402
    candidates, digest, fixed_pa, fixed_ca, invert_alphabet,
    load_plant_controls, forward, possible
)

PROTOCOL = "ce9bcd61e36b58cdbb009bca5b3bb2fc88763944959f850fdda1c2ae52df9c9f"
CT_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
PACKET = (
    "WXZK"
    "YXZKRYPTOSABCDEFGHIJLMNQUVWXZKR"
    "ZZKRYPTOSABCDEFGHIJLMNQUVWXZKRY"
    "_ABCDEFGHIJKLMNOPQRSTUVWXYZABCD"
)
assert len(PACKET) == 97 and PACKET.count("_") == 1 and PACKET.index("_") == 66


def keys():
    for blank in AZ:
        packet = PACKET.replace("_", blank)
        for number_name, alphabet in (("AZ", AZ), ("KRY", KRY)):
            inverse = invert_alphabet(alphabet)
            k = [inverse[c] for c in packet]
            assert len(k) == 97
            yield blank, number_name, k


def keyword_alphabets():
    return [(a, w, invert_alphabet(a))
            for a, w in candidates(ROOT / "k4kit/data/word_model_orth.tsv")]


def controls(kw):
    controls = load_plant_controls()
    allowed = set(a for a, w, inv in kw)
    variants = list(keys())
    counts = {"KW_PA": 0, "KW_CA": 0, "plus": 0, "minus": 0}
    for j, label in enumerate(sorted(controls)):
        _oldct, _oldk, row = controls[label]
        plain = row["plaintext"]
        b, num, key = variants[j % len(variants)]
        sign = 1 if j % 4 in (0, 1) else -1
        if j % 2 == 0:
            pa = row["plaintext_alphabet"]
            ca = row["ciphertext_alphabet"]
            assert pa in allowed
            orientation = "KW_PA"
        else:
            rng = random.Random(48200+j)
            pa = list(AZ)
            rng.shuffle(pa)
            pa = "".join(pa)
            ca = kw[rng.randrange(len(kw))][0]
            orientation = "KW_CA"
        ct = forward(plain, key, pa, ca, sign)
        anch = {i: plain[i] for i in ANCH}
        assert possible(key, ct=ct, anch=anch, sign=sign), "true key failed free/free feasibility"
        if orientation == "KW_PA":
            assert fixed_pa(ct, key, anch, invert_alphabet(pa), sign)
        else:
            assert fixed_ca(ct, key, anch, invert_alphabet(ca), sign)
        assert forward(plain, key, pa, ca, sign) == ct
        counts[orientation] += 1
        counts["plus" if sign == 1 else "minus"] += 1
    assert counts == {"KW_PA": 10, "KW_CA": 10, "plus": 10, "minus": 10}, counts
    return counts


def evaluate(ct, kw):
    settings = []
    free = []
    for blank, numbering, key in keys():
        plus = possible(key, ct=ct, anch=ANCH, sign=+1)
        minus = possible(key, ct=ct, anch=ANCH, sign=-1)
        if plus != minus:
            raise AssertionError("both-free plus/minus reflection symmetry failed")
        if not plus:
            continue
        free.append({"blank_letter": blank, "numbering": numbering})
        for alpha, word, inv in kw:
            for sign in (+1, -1):
                if fixed_pa(ct, key, ANCH, inv, sign):
                    settings.append({"family": "KW_PA_FREE_CA", "blank_letter": blank,
                                     "numbering": numbering, "sign": sign,
                                     "keyword": word, "keyword_alphabet": alpha})
                if fixed_ca(ct, key, ANCH, inv, sign):
                    settings.append({"family": "FREE_PA_KW_CA", "blank_letter": blank,
                                     "numbering": numbering, "sign": sign,
                                     "keyword": word, "keyword_alphabet": alpha})
    settings.sort(key=lambda x: (x["family"], x["blank_letter"],
                                  x["numbering"], x["sign"], x["keyword_alphabet"]))
    return {
        "total_full_97letter_keystreams": 52,
        "both_free_feasible_keys": len(free),
        "both_free_which": free,
        "keyword_PA_feasible": sum(x["family"] == "KW_PA_FREE_CA" for x in settings),
        "keyword_CA_feasible": sum(x["family"] == "FREE_PA_KW_CA" for x in settings),
        "all_feasible_settings": settings
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -I r48/sealed/physical_key_exact.py OUT.json")
    target = Path(sys.argv[1])
    if target.exists():
        raise RuntimeError("output already exists; refuse overwrite")
    assert digest(ROOT / "r48/PREREGISTRATION.md") == PROTOCOL
    assert (ROOT / "r48/PROTOCOL.sha256").read_text().split()[0] == PROTOCOL
    original = ROOT / "r39/ic_gate/k4_ciphertext.txt"
    assert digest(original) == CT_SHA
    ct = original.read_text().strip()
    assert ct == K4 and len(ct) == 97
    assert (ROOT / "r45/R45_RESULT.sha256").exists()
    kw = keyword_alphabets()
    verify = controls(kw)
    print("R48 positive controls", verify, flush=True)
    k4 = evaluate(ct, kw)
    print("R48 K4 twofree", k4["both_free_feasible_keys"],
          "KW_PA", k4["keyword_PA_feasible"],
          "KW_CA", k4["keyword_CA_feasible"], flush=True)
    nulls = []
    for j in range(4):
        chars = list(ct)
        random.Random(48100+j).shuffle(chars)
        nullct = "".join(chars)
        result = evaluate(nullct, kw)
        result["seed"] = 48100+j
        result["ciphertext_sha256"] = hashlib.sha256(nullct.encode()).hexdigest()
        nulls.append(result)
        print("R48 null", j, "twofree", result["both_free_feasible_keys"],
              "KW_PA", result["keyword_PA_feasible"],
              "KW_CA", result["keyword_CA_feasible"], flush=True)
    total = k4["keyword_PA_feasible"] + k4["keyword_CA_feasible"]
    output = {
        "type": "R48_SPECULATIVE_physical_packet_24_public_letter_consistency_NOT_BLIND_DECRYPTION",
        "protocol_sha256": PROTOCOL,
        "program_sha256": digest(Path(__file__)),
        "canonical_K4_sha256_with_newline": CT_SHA,
        "keyword_model_sha256": digest(ROOT / "k4kit/data/word_model_orth.tsv"),
        "unverified_literal_packet": PACKET,
        "blank_options": 26, "numbering_alphabets": ["AZ", "KRY"],
        "num_key_sequences": 52, "operations": ["+k", "-k"],
        "keyword_orientations": ["KW_PA_FREE_CA", "FREE_PA_KW_CA"],
        "keyword_alphabets": len(kw),
        "positive_controls": verify,
        "K4": k4, "nulls": nulls,
        "classification": ("EXCL this literal packet and model ONLY"
                           if total == 0 else
                           "FEAS only; using public K4 clues and unverified packet"),
        "scientific_limit": (
            "Packet is copied literally from a third-party field guide also "
            "offering a fitted/non-authentic plaintext; it is NOT certified "
            "from original sculpture photographs. No reconstructed K4 plaintext "
            "or back-fitted gate/card shift was used in this run."
        ),
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2) + "\n")
    print("R48 classification", output["classification"], flush=True)


if __name__ == "__main__":
    main()
