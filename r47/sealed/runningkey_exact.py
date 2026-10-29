#!/usr/bin/env python3
"""R47 SEALED ONLY: exact K4 24-anchor feasibility of historical running keys.
Not a blind decryption: no missing plaintext letters are inferred, and a
matching setting (if any) is only crib-assisted FEAS, never a solved K4.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "k4kit" / "tools"))
sys.path.insert(0, str(ROOT / "r45" / "sealed"))
from k4common import K4, KRY, AZ, ANCH  # noqa: E402
from keyword_exact import (  # noqa: E402
    candidates, digest, fixed_pa, fixed_ca, forward, invert_alphabet,
    load_plant_controls, possible
)

EXPECTED_PROTOCOL = "cbbe8b15fb658044d9a08c7513730a6205f6e8f2cd0a1965b97b9dccf5336dc9"
EXPECTED_CT = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
SOURCES = (
    ("K1K3", "k4kit/data/k1k3_plaintext.txt"),
    ("CARTER", "r34/carter_az.txt"),
)
NUMBERS = (("AZ", AZ), ("KRY", KRY))
DIRS = ("forward", "reversed")
N = 97


def key_sources():
    variants = []
    digests = {}
    for name, rel in SOURCES:
        p = ROOT / rel
        raw = p.read_text()
        clean = "".join(c for c in raw.upper() if "A" <= c <= "Z")
        if len(clean) < N:
            raise ValueError("source too short")
        digests[name] = {"file": rel, "sha256": digest(p),
                         "normalized_sha256": hashlib.sha256(clean.encode()).hexdigest(),
                         "normalized_length": len(clean)}
        for direction in DIRS:
            s = clean if direction == "forward" else clean[::-1]
            for alphabet_name, alphabet in NUMBERS:
                assert len(alphabet) == 26 and sorted(alphabet) == list(AZ)
                lookup = {ch: i for i, ch in enumerate(alphabet)}
                data = [lookup[c] for c in s]
                variants.append((name, direction, alphabet_name, data))
    return variants, digests


def all_windows(variants):
    for name, direction, alphabet, data in variants:
        for off in range(len(data) - N + 1):
            yield name, direction, alphabet, off, data[off:off+N]


def load_keyword_alphabets():
    kw = candidates(ROOT / "k4kit/data/word_model_orth.tsv")
    return [(alpha, word, invert_alphabet(alpha)) for alpha, word in kw]


def controls_test(variants, kw):
    plants = load_plant_controls()
    samples = []
    count = {"KW_PA": 0, "KW_CA": 0, "plus": 0, "minus": 0}
    for j, name in enumerate(sorted(plants)):
        _old_ciphertext, _old_key, obj = plants[name]
        plaintext = obj["plaintext"]
        assert len(plaintext) == N
        src, direction, numbering, data = variants[j % len(variants)]
        rng = random.Random(47200+j)
        off = rng.randrange(len(data)-N+1)
        key = data[off:off+N]
        sign = 1 if j % 4 in (0, 1) else -1
        if j % 2 == 0:
            pa = obj["plaintext_alphabet"]
            ca = obj["ciphertext_alphabet"]
            assert pa in {a for a, _w, _inv in kw}
            family = "KW_PA"
        else:
            ca = kw[rng.randrange(len(kw))][0]
            letters = list(AZ)
            rng.shuffle(letters)
            pa = "".join(letters)
            family = "KW_CA"
        ct = forward(plaintext, key, pa, ca, sign)
        anch = {i: plaintext[i] for i in ANCH}
        assert possible(key, ct=ct, anch=anch, sign=sign), "true key excluded by full-free graph"
        if family == "KW_PA":
            assert fixed_pa(ct, key, anch, invert_alphabet(pa), sign)
        else:
            assert fixed_ca(ct, key, anch, invert_alphabet(ca), sign)
        assert forward(plaintext, key, pa, ca, sign) == ct
        count[family] += 1
        count["plus" if sign == 1 else "minus"] += 1
        samples.append({"id": name, "source": src, "direction": direction,
                        "numbering": numbering, "offset": off, "sign": sign,
                        "family": family,
                        "ciphertext_sha256": hashlib.sha256(ct.encode()).hexdigest()})
    assert count == {"KW_PA": 10, "KW_CA": 10, "plus": 10, "minus": 10}
    return {"counts": count, "samples": samples}


def evaluate(ct, variants, keywords):
    survivors = 0
    enumerated = 0
    viable = []
    kw_pa = 0
    kw_ca = 0
    per_source = {}
    for name, direction, alphabet, off, key in all_windows(variants):
        enumerated += 1
        if not possible(key, ct=ct, anch=ANCH, sign=+1):
            continue
        if not possible(key, ct=ct, anch=ANCH, sign=-1):
            raise AssertionError("two-free +/- symmetry broken")
        survivors += 1
        per_source[name] = per_source.get(name, 0) + 1
        for kw_alpha, word, inv in keywords:
            for sign in (+1, -1):
                if fixed_pa(ct, key, ANCH, inv, sign):
                    kw_pa += 1
                    viable.append({"model": "KW_PA_FREE_CA", "source": name,
                                   "direction": direction, "numbering": alphabet,
                                   "offset": off, "sign": sign, "keyword": word,
                                   "keyword_alphabet": kw_alpha})
                if fixed_ca(ct, key, ANCH, inv, sign):
                    kw_ca += 1
                    viable.append({"model": "FREE_PA_KW_CA", "source": name,
                                   "direction": direction, "numbering": alphabet,
                                   "offset": off, "sign": sign, "keyword": word,
                                   "keyword_alphabet": kw_alpha})
    viable.sort(key=lambda v: (v["model"], v["source"], v["direction"],
                               v["numbering"], v["offset"], v["sign"], v["keyword_alphabet"]))
    return {"total_key_windows_checked": enumerated,
            "two_free_alphabet_surviving_windows": survivors,
            "two_free_survivors_by_source": per_source,
            "keyword_PA_feasible": kw_pa, "keyword_CA_feasible": kw_ca,
            "all_feasible_settings": viable}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -I r47/sealed/runningkey_exact.py OUT.json")
    target = Path(sys.argv[1])
    if target.exists():
        raise RuntimeError("refusing to overwrite existing R47 output")
    protocol = ROOT / "r47/PREREGISTRATION.md"
    assert digest(protocol) == EXPECTED_PROTOCOL, "R47 preregistration changed"
    assert (ROOT / "r47/PROTOCOL.sha256").read_text().split()[0] == EXPECTED_PROTOCOL
    original = ROOT / "r39/ic_gate/k4_ciphertext.txt"
    assert digest(original) == EXPECTED_CT, "original K4 bytes changed"
    ct = original.read_text().strip()
    assert ct == K4 and len(ct) == N
    assert (ROOT / "r45/R45_EXACT_RESULT.json").exists(), "R45 prerequisite missing"
    assert (ROOT / "r45/R45_RESULT.sha256").exists(), "R45 SHA256 missing"
    variants, source_digests = key_sources()
    keyword_alphabets = load_keyword_alphabets()
    controls = controls_test(variants, keyword_alphabets)
    print("R47 positive controls", controls["counts"], flush=True)
    print("R47 evaluating original K4", flush=True)
    k4 = evaluate(ct, variants, keyword_alphabets)
    print("R47 K4 windows", k4["total_key_windows_checked"],
          "twofree", k4["two_free_alphabet_surviving_windows"],
          "KW_PA", k4["keyword_PA_feasible"],
          "KW_CA", k4["keyword_CA_feasible"], flush=True)
    nulls = []
    for j in range(2):
        shuffled = list(ct)
        random.Random(47100+j).shuffle(shuffled)
        nullct = "".join(shuffled)
        print("R47 evaluating null", j, flush=True)
        out = evaluate(nullct, variants, keyword_alphabets)
        out["seed"] = 47100+j
        out["ciphertext_sha256"] = hashlib.sha256(nullct.encode()).hexdigest()
        nulls.append(out)
        print("R47 null", j, "twofree", out["two_free_alphabet_surviving_windows"],
              "KW_PA", out["keyword_PA_feasible"], "KW_CA", out["keyword_CA_feasible"], flush=True)
    nsettings = k4["keyword_PA_feasible"] + k4["keyword_CA_feasible"]
    result = {
        "type": "R47_known_clue_exact_runningkey_feasibility_NOT_BLIND_DECRYPTION",
        "protocol_sha256": EXPECTED_PROTOCOL, "program_sha256": digest(Path(__file__)),
        "original_K4_sha256_with_newline": EXPECTED_CT,
        "word_model_sha256": digest(ROOT / "k4kit/data/word_model_orth.tsv"),
        "source_sha256": source_digests,
        "unique_R44b_keyword_alphabets": len(keyword_alphabets),
        "four_variants_per_source": True, "operations": ["+k", "-k"],
        "keyword_orientations": ["KW_PA_FREE_CA", "FREE_PA_KW_CA"],
        "controls": controls, "K4": k4, "nulls": nulls,
        "K4_total_keyword_settings": nsettings,
        "classification": ("EXCL exactly two stated running-key sources/windows, both signs and keyword orientations, identity route"
                           if nsettings == 0 else
                           "FEAS only; published K4 anchors supplied as filter, NOT an independent solution"),
        "warning": "No K4 plaintext produced; this postfreeze check uses the published 24 known letters only to rule out or list algebraically possible settings."
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    print("R47 classification", result["classification"], flush=True)


if __name__ == "__main__":
    main()
