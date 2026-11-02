#!/usr/bin/env python3
"""R58 SEALED independent implementation: re-encrypt frozen candidates, then evaluate
hidden family, hidden keys, and hidden plaintext. No K4 known letters or offsets.
"""
import hashlib, json, math, sys
from pathlib import Path

AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
A="".join(dict.fromkeys("KRYPTOS"+AZ))
N=97

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def routes():
    sites=[(0,c) for c in range(27,31)]+[(r,c) for r in range(1,4) for c in range(31)]
    out={}
    for col in ["L","R"]:
        for row in ["T","B"]:
            cs=range(31) if col=="L" else range(30,-1,-1)
            rs=range(4) if row=="T" else range(3,-1,-1)
            out["COL_"+col+row]=tuple(sites.index((r,c))
                           for c in cs for r in rs if (r,c) in sites)
    for start in ["L","R"]:
        indices=[]
        for r in range(4):
            line=[i for i,s in enumerate(sites) if s[0]==r]
            if (r%2==1)==(start=="L"):line.reverse()
            indices.extend(line)
        out["SNAKE_"+start]=tuple(indices)
    assert len(out)==6 and all(sorted(v)==list(range(N)) for v in out.values())
    return out

def enc_v(p,key):
    assert key and len(p)==N
    s=[]
    for i,ch in enumerate(p):
        pi=A.index(ch)
        ki=A.index(key[i%len(key)])
        s.append(A[(pi+ki)%26])
    return "".join(s)

def enc_t(p,route,perms):
    assert route in perms and len(p)==N
    return "".join(p[i] for i in perms[route])

def enc(p,cls,key,route,perms):
    if cls=="V":return enc_v(p,key)
    if cls=="T":return enc_t(p,route,perms)
    if cls=="VT":return enc_t(enc_v(p,key),route,perms)
    if cls=="TV":return enc_v(enc_t(p,route,perms),key)
    raise ValueError("bad method family")

def verify(input_path,outputs,manifest_path,blind_source,words,quad,protocol):
    m=json.loads(Path(manifest_path).read_text())
    assert m["phase"]=="controls" and m["status"]=="FROZEN_BLIND_R58"
    checks={
      "input_sha256":input_path,
      "output_sha256":outputs,
      "blind_source_sha256":blind_source,
      "generic_words_sha256":words,
      "generic_quad_sha256":quad,
      "protocol_sha256":protocol,
    }
    for field,path in checks.items():
        assert sha(path)==m[field],("frozen checksum mismatch",field)
    input_lines=Path(input_path).read_text(encoding="ascii").splitlines()
    raw_lines=Path(outputs).read_text(encoding="ascii").splitlines()
    assert len(input_lines)==len(raw_lines)==120
    perm=routes()
    out={}
    witnesses=0
    for i,(line,data) in enumerate(zip(input_lines,raw_lines)):
        lab,ct=line.split(chr(9))
        assert lab==f"CASE_{i:03d}" and len(ct)==97 and set(ct)<=set(AZ)
        item=json.loads(data)
        assert item["id"]==lab and item["route_count"]==6
        assert item["searched"]==item["key_count"]*13+6
        assert len(item["candidates"])==8
        assert item["detected_family"] in ("V","T","VT","TV","ABSTAIN")
        assert item["confidence_reason"] in (
          "full_text_score_and_margin_passed",
          "observationally_aliased",
          "insufficient_english_score_or_margin"
        )
        top=item["candidates"][0]
        assert abs(top["score"]-item["best_score"])<1e-6
        scores=[z["score"] for z in item["candidates"]]
        assert scores==sorted(scores,reverse=True)
        if item["detected_family"]!="ABSTAIN":
            assert item["detected_family"]==top["family"]
            assert item["best_score"]>=-525 and item["next_distinct_margin"]>=10
        for cand in item["candidates"]:
            assert set(cand)=={"family","key","route","score",
                                "plaintext","first_reversed_intermediate"}
            cls=cand["family"]
            assert cls in ("V","T","VT","TV")
            p=cand["plaintext"]
            assert len(p)==97 and set(p)<=set(AZ)
            key=cand["key"]
            route=cand["route"]
            assert (key is not None)==(cls in ("V","VT","TV"))
            assert (route is not None)==(cls in ("T","VT","TV"))
            assert enc(p,cls,key,route,perm)==ct,("failed forward witness",lab,cls)
            intermediate=cand["first_reversed_intermediate"]
            if cls=="VT": assert intermediate==enc_v(p,key)
            elif cls=="TV":assert intermediate==enc_t(p,route,perm)
            else: assert intermediate is None
            witnesses+=1
        assert lab not in out
        out[lab]=item
    assert witnesses==960
    return out,m,witnesses

def main():
    if len(sys.argv)!=10:
        raise SystemExit("verify.py FROZEN_INPUT FROZEN_RESULTS MANIFEST SOLVER WORDS QUAD PROTOCOL TRUTH OUT")
    _,input_path,results,manifest,blind_source,words,quad,protocol,truth_path,outfile=sys.argv
    assert not Path(outfile).exists()
    rows,meta,n=verify(input_path,results,manifest,blind_source,words,quad,protocol)
    truth=json.loads(Path(truth_path).read_text())
    assert truth.keys()==rows.keys()
    families=("V","T","VT","TV","HILL","SHUFFLE")
    counts={}
    for family in families:
        subset=[(k,r,truth[k]) for k,r in rows.items() if truth[k]["family"]==family]
        assert len(subset)==20
        correctly_classified=sum(r["detected_family"]==family for k,r,t in subset)
        exact_text=sum(r["detected_family"]==family and
                       r["candidates"][0]["plaintext"]==t["plaintext"]
                       for k,r,t in subset)
        key_exact=sum(r["detected_family"]==family and
             r["candidates"][0]["plaintext"]==t["plaintext"] and
             r["candidates"][0]["key"]==t["key"] and
             r["candidates"][0]["route"]==t["route"]
             for k,r,t in subset)
        confident_false=sum(r["detected_family"]!="ABSTAIN" for k,r,t in subset) if family in ("HILL","SHUFFLE") else 0
        counts[family]={"n":20,"correct_family":correctly_classified,
                        "exact_full_text_and_family":exact_text,
                        "exact_settings_and_text":key_exact,
                        "confident_false_positive":confident_false,
                        "abstentions":sum(r["detected_family"]=="ABSTAIN" for k,r,t in subset)}
    passed=(all(counts[z]["exact_full_text_and_family"]>=16 and
                counts[z]["exact_settings_and_text"]>=16 for z in families[:4])
            and all(counts[z]["confident_false_positive"]<=1 for z in families[4:]))
    report={
       "classification":"R58_POST_REMOTE_FREEZE_HIDDEN_FAMILY_AND_KEY_EVALUATION",
       "status":"PASSED" if passed else "FAILED",
       "gate_passed":passed,"counts":counts,
       "total_cases":len(rows),"verified_forward_witnesses":n,
       "all_forward_witnesses_valid":True,
       "frozen_output_sha256":meta["output_sha256"],
       "required_min_exact_per_known_family":16,
       "required_max_false_positives_per_other_family":1,
       "warning":"Closed-world controlled models; matching ciphertext with an arbitrary fitted key is not K4 recovery."
    }
    p=Path(outfile);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("x",encoding="ascii") as f:json.dump(report,f,indent=2,sort_keys=True);f.write(chr(10))
    print("R58 sealed evaluation, after remote freeze:",report["status"])
    for cls in families:print(cls,counts[cls])
    if not passed:sys.exit(2)
if __name__=="__main__":
    main()
