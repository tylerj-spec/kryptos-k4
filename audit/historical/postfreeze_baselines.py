#!/usr/bin/env python3
"""Independent post-freeze baseline exclusion recheck for L01-L04.

ONLY callable in post-freeze verification mode. No decryptor, no language
model, no key generation from the known K4 letters. Performs algebraic
constraint checks and counts, NOT blind candidate creation.
"""
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPH = {
    "AZ": AZ,
    "KRY": "".join(dict.fromkeys("KRYPTOS" + AZ)),
    "PAL": "".join(dict.fromkeys("PALIMPSEST" + AZ)),
    "ABS": "".join(dict.fromkeys("ABSCISSA" + AZ)),
}


def permutation_compatible(ciphertext, known):
    need = Counter(known.values())
    avail = Counter(ciphertext)
    return all(avail[letter] >= count for letter, count in need.items())


def mono_conflicts(ciphertext, known):
    cipher_to_plain = {}
    conflicts = []
    for i, p in sorted(known.items()):
        c = ciphertext[i]
        if c in cipher_to_plain and cipher_to_plain[c][1] != p:
            conflicts.append((cipher_to_plain[c][0], i))
        else:
            cipher_to_plain.setdefault(c, (i, p))
    return conflicts


def periodic_compatible(ciphertext, known, pa, ca, sign, m):
    if m < 1 or sign not in (-1, 1):
        raise ValueError("bad period or sign")
    if set(pa) != set(AZ) or set(ca) != set(AZ):
        raise ValueError("not a tableau alphabet permutation")
    slots = {}
    for i, p in sorted(known.items()):
        r = i % m
        implied = (ca.index(ciphertext[i]) - sign * pa.index(p)) % 26
        if r in slots and slots[r] != implied:
            return False
        slots[r] = implied
    return True


def synthetics():
    pt = (AZ * 4)[:97]
    pos = list(range(7, 27)) + list(range(52, 65))
    # Different from K4 published positions. Plant 3-symbol repeating
    # key using two unrelated alphabets and test its repeated-slot law.
    pa, ca, sign, m = ALPH["PAL"], ALPH["KRY"], -1, 3
    shifts = (5, 20, 2)
    ct = "".join(ca[(sign * pa.index(c) + shifts[i % m]) % 26]
                 for i, c in enumerate(pt))
    known = {i: pt[i] for i in pos}
    assert periodic_compatible(ct, known, pa, ca, sign, m)
    bad = dict(known)
    bad[pos[4]] = AZ[(AZ.index(bad[pos[4]]) + 1) % 26]
    assert not periodic_compatible(ct, bad, pa, ca, sign, m)
    assert not mono_conflicts("ABCDEFGHIJKLMNOPQRSTUVWXYZ"*4,
                              {0:"A", 26:"B"})
    assert mono_conflicts("A"*97, {1:"C",2:"D"})
    assert permutation_compatible(pt, known)
    assert not permutation_compatible("B"*97,{0:"A"})
    return {"synthetic": "PASS",
            "statement": "Independent witness, contradicted letter and mono/pure-permutation checks"}


def postfreeze_report():
    frozen = ROOT / "r83/k4/run/FROZEN.sha256"
    target = ROOT / "r83/k4/TARGET.tsv"
    frozen_digest = hashlib.sha256(target.read_bytes()).hexdigest()
    hashes = [line.split()[0] for line in frozen.read_text().splitlines()
              if line.endswith("r83/k4/TARGET.tsv")]
    if hashes != [frozen_digest]:
        raise AssertionError("original ciphertext target does not match frozen hash")
    lines = [ln.split("\t") for ln in target.read_text().splitlines()[1:] if ln]
    ct = dict(lines)["K4"]
    assert len(ct) == 97 and set(ct) <= set(AZ)
    # Published clues are imported only inside this post-freeze verifier,
    # never in any candidate search or model-training module.
    path = ROOT / "r73/sealed/reveal_k4.py"
    spec = importlib.util.spec_from_file_location("published_postfreeze_only", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    known = {i: ch for i, ch in mod.POS}
    assert len(known) == 24
    compatibility = []
    for pa_name, pa in ALPH.items():
        for ca_name, ca in ALPH.items():
            for sign in (1,-1):
                for m in range(1,27):
                    if periodic_compatible(ct, known, pa, ca, sign, m):
                        compatibility.append({"pa":pa_name,"ca":ca_name,
                                              "sign":sign,"m":m})
    e = Counter(ct)
    p = Counter(known.values())
    needed_more = {k:int(v-e[k]) for k,v in p.items() if v > e[k]}
    return {
        "label":"POSTFREEZE_CRIB_ASSISTED_EXCLUSION_ONLY",
        "blinded_candidate_generation":"NONE",
        "source":"r83/k4/TARGET.tsv, hash checked against R83 frozen manifest",
        "L01_pure_permutation_compatible":permutation_compatible(ct,known),
        "L01_insufficient_letters":needed_more,
        "L02_monoalphabet_conflict_pairs":mono_conflicts(ct,known),
        "L03_L04_model":"in-place periodic c=CA[(sign*IDX(PA,p)+k[i%m]) mod 26]",
        "L03_L04_periods_tested":"m1..26, signs+/-1, 4x4 named alphabets",
        "L03_L04_tested_labeled_settings":26*2*4*4,
        "L03_L04_compatible_settings":compatibility,
        "interpretation":"No K4 plaintext candidate or completed key is generated; in-place assumption required.",
    }


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "--postfreeze":
        raise SystemExit("Explicit --postfreeze OUTPUT.json required; no blind mode")
    synthetics()
    data = postfreeze_report()
    target = Path(sys.argv[2])
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "pure_permutation":data["L01_pure_permutation_compatible"],
        "mono_conflicts":len(data["L02_monoalphabet_conflict_pairs"]),
        "periodic_settings_tested":data["L03_L04_tested_labeled_settings"],
        "periodic_survivors":data["L03_L04_compatible_settings"],
    },sort_keys=True))


if __name__=="__main__":
    main()
