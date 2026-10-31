#!/usr/bin/env python3
"""R51 sealed postfreeze known-24-letter feasibility for K3 T_then_S plus ciphertext feedback.

Pure ciphertext-autokey: k[j>=L]=alphabet_rank(C[j-L]), no decimal Gromark;
initial seed k[:L] is UNKNOWN/free and its constraints are correctly omitted.
This is NOT a ciphertext-only K4 plaintext solver. No K4 missing text is guessed.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "k4kit" / "tools"))
sys.path.insert(0, str(ROOT / "r45" / "sealed"))
sys.path.insert(0, str(ROOT / "r46" / "sealed"))
sys.path.insert(0, str(ROOT / "r50" / "sealed"))
from k4common import AZ, KRY, ANCH, K4  # noqa: E402
from key_oracle import possible, checks  # noqa: E402
from keyword_exact import digest, invert_alphabet, fixed_pa, fixed_ca, load_plant_controls  # noqa: E402
from k3_keyword_exact import ROUTES, transposition  # noqa: E402
from pretransposition_exact import KeywordIndex, kw_list, remap_anchors  # noqa: E402

PROTOCOL = "a05b6dbe2c3e7e3932484146cd8b416438b668c1ad4ce92e72355d039ce3b65a"
ORIGINAL_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
LAGS = tuple(range(1, 25))
BASES = (("AZ", AZ), ("KRYPTOS", KRY))


def feedback_key(ct, lag, alphabet):
    """Unknown initial seed (positions < lag) replaced by irrelevant 0s.
    The graph's known anchor subset NEVER includes those positions.
    """
    assert 1 <= lag <= 24 and len(ct) == 97 and len(alphabet) == 26
    ainv = invert_alphabet(alphabet)
    return [0] * lag + [ainv[ct[j - lag]] for j in range(lag, 97)]


def encrypt_feedback(p, perm, lag, alphabet, pa, ca, sign, rng):
    """Independent forward ciphertext-feedback control; observe CT as it grows."""
    painv = invert_alphabet(pa)
    feedback_inverse = invert_alphabet(alphabet)
    seed = [rng.randrange(26) for _ in range(lag)]
    q = "".join(p[perm[j]] for j in range(97))
    ct = ""
    key = []
    for j in range(97):
        k = seed[j] if j < lag else feedback_inverse[ct[j-lag]]
        key.append(k)
        ct += ca[(painv[q[j]] + sign * k) % 26]
    assert len(ct) == len(key) == 97
    return ct, key, seed


def full_decrypt(ct, perm, key, pa, ca, sign):
    cinv = invert_alphabet(ca)
    invperm = [None] * 97
    for j, i in enumerate(perm):
        invperm[i] = j
    q = "".join(pa[(cinv[ct[j]] - sign * key[j]) % 26] for j in range(97))
    return "".join(q[invperm[i]] for i in range(97))


def positive_controls(common, themed, permutations):
    plants = load_plant_controls()
    words = common + themed
    known_common = {alpha for alpha, _, _, _ in common}
    counts = {"KW_PA":0,"KW_CA":0,"plus":0,"minus":0,
              "basis_AZ":0,"basis_KRYPTOS":0}
    samples = []
    for i, label in enumerate(sorted(plants)):
        _old, _key, item = plants[label]
        p = item["plaintext"]
        route = ROUTES[i % 4]
        perm, _ = permutations[route]
        lag = i + 1  # deliberately cover L=1..20
        base_name, alphabet = BASES[i % 2]
        sign = 1 if i % 4 in (0,1) else -1
        rng = random.Random(51000+i)
        if i % 2 == 0:
            pa = item["plaintext_alphabet"]
            ca = item["ciphertext_alphabet"]
            assert pa in known_common
            family = "KW_PA"
            expected = pa
        else:
            letters = list(AZ)
            rng.shuffle(letters)
            pa = "".join(letters)
            ca = common[rng.randrange(len(common))][0]
            family = "KW_CA"
            expected = ca
        ct, full_key, seed = encrypt_feedback(p, perm, lag, alphabet, pa, ca, sign, rng)
        assert full_decrypt(ct, perm, full_key, pa, ca, sign) == p
        known = feedback_key(ct, lag, alphabet)
        assert full_key[lag:] == known[lag:]
        mask = {j: x for j,x in remap_anchors(perm, {t:p[t] for t in ANCH}).items()
                if j>=lag}
        assert mask, "positive plant has no testable anchor positions"
        assert possible(known, ct=ct, anch=mask, sign=sign)
        invert = invert_alphabet(expected)
        assert (fixed_pa(ct, known, mask, invert, sign) if family=="KW_PA"
                else fixed_ca(ct, known, mask, invert, sign))
        idx = KeywordIndex(ct, mask, words, family)
        matches = idx.matches(known, sign)
        assert any(a == expected for a,w,source in matches)
        assert set(matches) == set(idx.brute(known, sign))
        # Full unknown-seed restoration: only the *visible* ciphertext prefix
        # plus arbitrary seeded first L positions can reconstitute all 97.
        recovered_seed = [(
            invert_alphabet(ca)[ct[j]] - invert_alphabet(pa)[p[perm[j]]]
        ) * sign % 26 for j in range(lag)]
        assert recovered_seed == seed
        counts[family] += 1
        counts["plus" if sign==1 else "minus"] += 1
        counts[f"basis_{base_name}"] += 1
        samples.append({"id":label,"route":route,"lag":lag,"basis":base_name,
                        "known_anchors":len(mask),"sign":sign,"orientation":family,
                        "ciphertext_sha256":hashlib.sha256(ct.encode()).hexdigest()})
    assert counts == {"KW_PA":10,"KW_CA":10,"plus":10,"minus":10,
                      "basis_AZ":10,"basis_KRYPTOS":10}
    return {"counts":counts,"cases":samples}


def evaluate(ct, common, themed, permutations, label):
    words = common + themed
    route_results = {}
    for route in ROUTES:
        perm, _ = permutations[route]
        full_mask = remap_anchors(perm)
        survivors = []
        hits = []
        crosscheck = 0
        lowcoverage_hits = 0
        highcoverage_hits = 0
        # All lags and both feedback alphabets, regardless of early contradiction.
        for lag in LAGS:
            mask = {j:x for j,x in full_mask.items() if j >= lag}
            known_positions = len(mask)
            graph_cycles = checks(ct=ct, anch=mask)
            ipa = KeywordIndex(ct, mask, words, "KW_PA")
            ica = KeywordIndex(ct, mask, words, "KW_CA")
            for base_name, alphabet in BASES:
                key = feedback_key(ct, lag, alphabet)
                if not possible(key, ct=ct, anch=mask, sign=+1):
                    continue
                assert possible(key, ct=ct, anch=mask, sign=-1), "twofree sign symmetry failed"
                survivors.append({
                    "lag":lag,"numbering":base_name,"anchor_coverage":known_positions,
                    "independent_cycles":graph_cycles
                })
                if crosscheck < 3:
                    for sign in (+1, -1):
                        for idx in (ipa, ica):
                            a=set(idx.matches(key,sign))
                            b=set(idx.brute(key,sign))
                            assert a==b, f"keyword index invalid: {route=} {lag=} {base_name=} {sign=} {idx.orient=}"
                    crosscheck+=1
                for sign in (+1,-1):
                    for idx,orient in ((ipa,"KW_PA_FREE_CA"),(ica,"FREE_PA_KW_CA")):
                        for alpha,word,kw_class in idx.matches(key,sign):
                            entry={"lag":lag,"numbering":base_name,"sign":sign,"orientation":orient,
                                   "keyword_class":kw_class,"keyword":word,
                                   "keyword_alphabet":alpha,"anchor_coverage":known_positions,
                                   "independent_cycles":graph_cycles,
                                   "evidence_tier":("HIGH_COVERAGE_NONZERO_CYCLES"
                                                    if known_positions>=20 and graph_cycles>0
                                                    else "LOW_COVERAGE_OR_NO_CYCLES")}
                            hits.append(entry)
                            if entry["evidence_tier"]=="HIGH_COVERAGE_NONZERO_CYCLES":
                                highcoverage_hits+=1
                            else:
                                lowcoverage_hits+=1
        hits.sort(key=lambda x:(x["lag"],x["numbering"],x["orientation"],
                                 x["sign"],x["keyword_class"],x["keyword_alphabet"]))
        route_results[route]={
            "total_lag_basis_settings":len(LAGS)*len(BASES),
            "two_free_surviving_lag_basis":len(survivors),
            "two_free_survivors":survivors,
            "keyword_hits":len(hits),
            "highcoverage_nonzero_cycle_hits":highcoverage_hits,
            "lowcoverage_or_zero_cycle_hits":lowcoverage_hits,
            "all_keyword_matches":hits,
            "unindexed_crosschecked_twofree_parameters":crosscheck
        }
        print("R51",label,route,"twofree",len(survivors),
              "keyword",len(hits),"highcoverage",highcoverage_hits,
              "direct_unindexed",crosscheck,flush=True)
    return route_results


def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: python3 -I r51/sealed/cipherfeedback_exact.py OUT.json")
    out=Path(sys.argv[1])
    if out.exists():
        raise RuntimeError("R51 refuses to overwrite existing output")
    assert digest(ROOT/"r51/PREREGISTRATION.md")==PROTOCOL
    assert (ROOT/"r51/PROTOCOL.sha256").read_text().split()[0]==PROTOCOL
    ct_path=ROOT/"r39/ic_gate/k4_ciphertext.txt"
    assert digest(ct_path)==ORIGINAL_SHA
    ct=ct_path.read_text().strip()
    assert len(ct)==97 and ct==K4
    common,themed=kw_list()
    assert len(common)==4749 and len(themed)==12
    permutations={r:transposition(r) for r in ROUTES}
    controls=positive_controls(common,themed,permutations)
    print("R51 forward positive controls",controls["counts"],flush=True)
    primary=evaluate(ct,common,themed,permutations,"K4")
    nulls=[]
    for j in range(2):
        ct_chars=list(ct)
        random.Random(51100+j).shuffle(ct_chars)
        shifted="".join(ct_chars)
        route_results=evaluate(shifted,common,themed,permutations,f"NULL{j}")
        nulls.append({"seed":51100+j,"ciphertext_sha256":hashlib.sha256(shifted.encode()).hexdigest(),
                      "by_route":route_results})
    total=sum(x["keyword_hits"] for x in primary.values())
    high=sum(x["highcoverage_nonzero_cycle_hits"] for x in primary.values())
    if not total: conclusion="EXCL exact tested T_then_S/ciphertext-feedback L1..24/basis AZ-KRY/keyword-free family"
    elif not high: conclusion="NO_HIGH_COVERAGE_FEAS; low-information settings survive (not solved)"
    else: conclusion="FEAS only; clue-filtered, NOT independently decrypted K4"
    result={
        "type":"R51_postfreeze_24_public_letter_ciphertext_feedback_exact_NOT_K4_PLAINTEXT",
        "protocol_sha256":PROTOCOL,
        "program_sha256":digest(Path(__file__)),
        "canonical_original_K4_SHA256_with_newline":ORIGINAL_SHA,
        "keyword_model_sha256":digest(ROOT/"k4kit/data/word_model_orth.tsv"),
        "candidate_keyword_alphabets":{"common":len(common),"themed_extra":len(themed)},
        "transposition":"T_then_S_K3_24x8_four_routes",
        "lags":list(LAGS),"base_numberings":[b[0] for b in BASES],"signs":[1,-1],
        "unknown_initial_seed":"first lag letters unconstrained; initial key never guessed",
        "positive_controls":controls,"K4_by_route":primary,"nulls":nulls,
        "total_K4_keyword_feasible":total,
        "K4_highcoverage_nonzero_cycle_hits":high,
        "classification":conclusion,
        "warnings":[
            "No K4 plaintext inferred, no unknown initial key recovered.",
            "Known K4 anchor letters were used ONLY for postfreeze feasibility.",
            "All positive controls are already revealed texts, not blind recovery.",
            "High coverage is an information criterion, NOT a p-value or independent confirmation."
        ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print("R51 K4 TOTAL",total,"highcoverage",high,"conclusion",conclusion,flush=True)


if __name__=="__main__":
    main()
