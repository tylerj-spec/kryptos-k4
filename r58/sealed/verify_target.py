#!/usr/bin/env python3
"""R58B independent after-remote-freeze forward witness audit, NO KNOWN K4 PLAINTEXT.
Uses earlier independent control encryptor, NOT the blind decryptor.
"""
import hashlib,importlib.util,json,math,sys
from pathlib import Path

AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N=97
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_independent_forward():
    src=Path(__file__).with_name("verify_frozen.py")
    spec=importlib.util.spec_from_file_location("r58_separate_forward",src)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    if len(sys.argv)!=11:
        raise SystemExit("verify_target.py INPUT FROZEN_RESULTS MANIFEST SOLVER WORDS QUAD ORIGINAL_PROTOCOL TARGET_PROTOCOL PREPARER OUT")
    _,inputs,outputs,manifest,solver,words,quad,origproto,protocol,preparer,outfile=sys.argv
    assert not Path(outfile).exists()
    m=json.loads(Path(manifest).read_text())
    assert m["status"]=="FROZEN_BEFORE_ANY_K4_CLUE" and m["phase"]=="target"
    files={
       "input_sha256":inputs, "output_sha256":outputs,
       "blind_source_sha256":solver, "generic_words_sha256":words,
       "generic_quad_sha256":quad,"original_prereg_sha256":origproto,
       "target_protocol_sha256":protocol,"target_preparer_sha256":preparer
    }
    for field,path in files.items():
        assert sha(path)==m[field],("frozen code/data mismatch",field)
    data=Path(inputs).read_text().splitlines()
    rows=[json.loads(s) for s in Path(outputs).read_text().splitlines()]
    assert len(data)==len(rows)==101
    fwd=load_independent_forward()
    perm=fwd.routes()
    n=0
    bests=[]
    texts=[]
    for i,(line,row) in enumerate(zip(data,rows)):
        a=line.split(chr(9))
        assert len(a)==2
        name,ct=a
        expected="K4" if i==0 else f"NULL_{i-1:03d}"
        assert name==expected and row["id"]==name
        assert len(ct)==97 and set(ct)<=set(AZ)
        if i==0:
            assert ct=="OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
            authentic=ct
        else:
            assert sorted(ct)==sorted(authentic)
            assert ct!=authentic
        assert row["searched"]==m["searched_per_input"]
        assert row["route_count"]==6
        assert len(row["candidates"])==8
        assert row["detected_family"] in ("V","T","VT","TV","ABSTAIN")
        if row["detected_family"]!="ABSTAIN":
            assert row["best_score"]>=-525 and row["next_distinct_margin"]>=10
            assert row["detected_family"]==row["candidates"][0]["family"]
        last=float("inf")
        for cand in row["candidates"]:
            assert set(cand)=={"family","key","route","score","plaintext","first_reversed_intermediate"}
            cls=cand["family"]
            assert cls in ("V","T","VT","TV")
            p=cand["plaintext"]; key=cand["key"];route=cand["route"]
            assert len(p)==97 and set(p)<=set(AZ)
            assert math.isfinite(cand["score"]) and cand["score"]<=last+1e-7
            last=cand["score"]
            assert fwd.enc(p,cls,key,route,perm)==ct,("invalid forward encryption",name,cls)
            mid=cand["first_reversed_intermediate"]
            if cls=="VT": assert mid==fwd.enc_v(p,key)
            elif cls=="TV":assert mid==fwd.enc_t(p,route,perm)
            else:assert mid is None
            n+=1
        bests.append(row["best_score"])
        texts.append(row["detected_family"])
    assert n==808
    score=bests[0]
    exceeded=sum(x>=score for x in bests[1:])
    report={
       "classification":"R58B_POST_REMOTE_FREEZE_INDEPENDENT_K4_AND_NULL_AUDIT_NO_K4_CLUES",
       "status":"VALIDATED_FORWARD_ONLY",
       "raw_output_sha256":m["output_sha256"],
       "all_forward_witnesses_valid":True,
       "verified_forward_witnesses":n,
       "null_count":100,
       "k4_blind_detected_family":texts[0],
       "k4_blind_top_score":score,
       "k4_blind_next_distinct_margin":rows[0]["next_distinct_margin"],
       "shuffled_null_scores_greater_or_equal_to_k4":exceeded,
       "empirical_upper_tail_rank_101":(exceeded+1)/101,
       "null_confident_detections":sum(x!="ABSTAIN" for x in texts[1:]),
       "limitation":"Descriptive frequency-preserving null distribution, not proof of cipher-family identification or a K4 solve."
    }
    path=Path(outfile);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="ascii") as f:
        json.dump(report,f,indent=2,sort_keys=True);f.write(chr(10))
    print("R58B separate forward auditor:",n,"witnesses exact; K4 blind family",
          report["k4_blind_detected_family"],"nulls exceeding K4",exceeded)
if __name__=="__main__":main()
