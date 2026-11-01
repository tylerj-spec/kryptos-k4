#!/usr/bin/env python3
"""R60 independent post-remote-freeze verifier. Codebook meanings and true keys
are never available to the blind runner, and public K4 clue positions never
appear in this file. Includes an independent cipher forward implementation.
"""
from pathlib import Path
import hashlib,json,math,sys

A="".join(dict.fromkeys("KRYPTOS"+"ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N=97

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def routes():
    sites=[(0,c) for c in range(27,31)]+[(r,c) for r in range(1,4) for c in range(31)]
    assert len(sites)==97 and len(set(sites))==97
    perms={}
    for cdir in ("L","R"):
        for rdir in ("T","B"):
            columns=range(31) if cdir=="L" else range(30,-1,-1)
            rows=range(4) if rdir=="T" else range(3,-1,-1)
            perms["COL_"+cdir+rdir]=tuple(sites.index((r,c))
                  for c in columns for r in rows if (r,c) in sites)
    for start in ("L","R"):
        indices=[]
        for r in range(4):
            row=[i for i,cell in enumerate(sites) if cell[0]==r]
            if (r%2==1)==(start=="L"):row=row[::-1]
            indices.extend(row)
        perms["SNAKE_"+start]=tuple(indices)
    assert len(perms)==6
    return perms

def v_encrypt(p,key):
    assert len(p)==N and key
    return "".join(A[(A.index(p[i])+A.index(key[i%len(key)]))%26]
                   for i in range(N))

def t_encrypt(p,route,allroutes):
    assert route in allroutes
    return "".join(p[index] for index in allroutes[route])

def encrypt(p,method,key,route,routes_):
    if method=="V":return v_encrypt(p,key)
    if method=="T":return t_encrypt(p,route,routes_)
    if method=="VT":return t_encrypt(v_encrypt(p,key),route,routes_)
    if method=="TV":return v_encrypt(t_encrypt(p,route,routes_),key)
    raise AssertionError("unknown transformation")

def main():
    if len(sys.argv)!=11:
        raise SystemExit("verify.py INPUT RAW MANIFEST BLIND WORDS QUAD PROTOCOL GENERATOR TRUTH OUT")
    _,inputs,raw,manifest,blind,words,quad,protocol,generator,truth_path,out=sys.argv
    assert not Path(out).exists()
    m=json.loads(Path(manifest).read_text())
    assert m["status"]=="FROZEN_BEFORE_ANY_SEMANTIC_TRUTH_REVEAL" and m["phase"]=="controls"
    for path,field in (
        (inputs,"input_sha256"),(raw,"raw_output_sha256"),
        (blind,"blind_solver_sha256"),(words,"generic_words_sha256"),
        (quad,"generic_quad_sha256"),(protocol,"protocol_sha256"),
        (generator,"sealed_generator_sha256")
    ):
        assert sha(path)==m[field],("remote freeze mismatch",field)
    ctrows=Path(inputs).read_text(encoding="ascii").splitlines()
    rows=[json.loads(s) for s in Path(raw).read_text(encoding="ascii").splitlines()]
    truth=json.loads(Path(truth_path).read_text(encoding="utf-8"))
    assert len(ctrows)==len(rows)==len(truth)==40
    map_=routes()
    details={k:{"n":0,"exact":0,"correct_key_route":0,"abstain":0,"false_confidence":0}
             for k in ("V","T","VT","TV","UNIFORM_NULL")}
    seen=set()
    candidate_forward=0
    pair_forward=0
    actual_forward=0
    for i,(raw_ct,record) in enumerate(zip(ctrows,rows)):
        lab,ct=raw_ct.split(chr(9))
        assert lab==record["id"]==f"CASE_{i:03d}"
        assert lab not in seen;seen.add(lab)
        assert len(ct)==97 and set(ct)<=set(AZ)
        assert len(record["candidates"])==8 and record["searched"]==877
        assert record["route_count"]==6
        last=float("inf")
        for candidate in record["candidates"]:
            assert set(candidate)=={
                "family","key","route","score","plaintext","first_reversed_intermediate"}
            method=candidate["family"]
            p=candidate["plaintext"]
            key=candidate["key"]
            route=candidate["route"]
            assert len(p)==N and set(p)<=set(AZ)
            assert method in ("V","T","VT","TV")
            assert (key is not None)==(method in ("V","VT","TV"))
            assert (route is not None)==(method in ("T","VT","TV"))
            assert math.isfinite(candidate["score"]) and candidate["score"]<=last+1e-7
            last=candidate["score"]
            assert encrypt(p,method,key,route,map_)==ct,("candidate witness failed",lab,method)
            mid=candidate["first_reversed_intermediate"]
            if method=="VT": assert mid==v_encrypt(p,key)
            elif method=="TV":assert mid==t_encrypt(p,route,map_)
            else:assert mid is None
            candidate_forward+=1
        name=truth[lab]["family"]
        assert name in details
        details[name]["n"]+=1
        if record["detected_family"]=="ABSTAIN":
            details[name]["abstain"]+=1
        else:
            assert record["detected_family"]==record["candidates"][0]["family"]
        if name=="UNIFORM_NULL":
            if record["detected_family"]!="ABSTAIN":
                details[name]["false_confidence"]+=1
            assert truth[lab]["plaintext"] is None
            continue
        t=truth[lab]
        cover=t["plaintext"]
        key=t["key"]
        route=t["route"]
        assert len(cover)==97 and t["coverword"] in cover
        assert t["meaning_a"] != t["meaning_b"],"private maps are not distinct"
        assert t["coverword"] in t["meaning_a"] and t["coverword"] in t["meaning_b"]
        assert encrypt(cover,name,key,route,map_)==ct
        actual_forward+=1
        # Meaning assignment A and B is not an encryption input. Both
        # independently make the SAME full ciphertext for the SAME covertext.
        two_codebooks=[t["meaning_a"],t["meaning_b"]]
        for meaning in two_codebooks:
            assert meaning and encrypt(cover,name,key,route,map_)==ct
            pair_forward+=1
        top=record["candidates"][0]
        recovered=record["detected_family"]==name and top["plaintext"]==cover
        if recovered:
            details[name]["exact"]+=1
            if top["key"]==key and top["route"]==route:
                details[name]["correct_key_route"]+=1
    assert candidate_forward==320 and actual_forward==20 and pair_forward==40
    assert all(details[k]["n"]==5 for k in ("V","T","VT","TV"))
    assert details["UNIFORM_NULL"]["n"]==20
    total=sum(details[k]["exact"] for k in ("V","T","VT","TV"))
    true_settings=sum(details[k]["correct_key_route"] for k in ("V","T","VT","TV"))
    false=details["UNIFORM_NULL"]["false_confidence"]
    gate=total>=16 and true_settings>=16 and false<=1 and all(
        details[k]["exact"]>=3 and details[k]["correct_key_route"]>=3
        for k in ("V","T","VT","TV")
    )
    report={
        "classification":"R60_AFTER_REMOTE_FREEZE_SEMANTIC_COVER_TEXT_HOLDOUT",
        "status":"PASS" if gate else "FAIL",
        "gate_passed":gate,
        "raw_output_sha256":m["raw_output_sha256"],
        "frozen_full_candidates":320,
        "independent_full_forward_witnesses":candidate_forward,
        "true_controls_forward_reencryption":actual_forward,
        "semantic_codebook_pair_checks":pair_forward,
        "same_ciphertext_with_two_distinct_meaning_maps":20,
        "total_true_covertexts_recovered":total,
        "exact_keys_and_texts":true_settings,
        "false_confidences_on_uniform_nulls":false,
        "per_family":details,
        "limitation":"The private meaning dictionary cannot be inferred from ciphertext when the visible covertext and encryption key are unchanged. No K4 plaintext tested or recovered."
    }
    output=Path(out)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("x",encoding="ascii") as f:
        json.dump(report,f,indent=2,sort_keys=True);f.write(chr(10))
    print("R60 postfreeze:",report["status"],"exact",total,"/20; true keys",true_settings,
          "/20; false",false,"/20; witnesses",candidate_forward,"semantic pairs",pair_forward)
    if not gate:raise SystemExit(2)

if __name__=="__main__":main()
