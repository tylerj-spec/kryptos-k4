#!/usr/bin/env python3
"""R56 separate after-REMOTE-freeze independent forward verifier and synthetic control evaluator.
Does not contain/read any known K4 plaintext letters, positions, masks or words.
"""
from pathlib import Path
import hashlib,json,math,sys

AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rotate(a,k):return a[k%26:]+a[:k%26]
def check_forward(p,alpha,side,phase):
    assert len(p)==97 and set(p)<=set(AZ)
    assert len(alpha)==26 and set(alpha)==set(AZ)
    assert side in ("left","right") and type(phase)==int and 0<=phase<26
    left=alpha if side=="left" else AZ
    right=rotate(alpha if side=="right" else AZ,phase)
    cipher=[]
    for letter in p:
        j=right.index(letter)
        cipher.append(left[j])
        left=rotate(left,j)
        char=left[1]
        left=left[:1]+left[2:14]+char+left[14:]
        right=rotate(right,j+1)
        char=right[2]
        right=right[:2]+right[3:14]+char+right[14:]
    return "".join(cipher)
def validate(kind,inputs,results,manifest,source,words,quad,protocol):
    m=json.loads(Path(manifest).read_text())
    assert m["status"]=="FROZEN_NO_EVALUATION" and m["phase"]==kind
    for path,field in ((inputs,"input_sha256"),(results,"output_sha256"),
                       (source,"source_sha256"),(words,"word_model_sha256"),
                       (quad,"quad_model_sha256"),(protocol,"protocol_sha256")):
        assert sha(path)==m[field],("frozen source/outputs mismatch",path)
    inrows={}
    for line in Path(inputs).read_text().splitlines():
        cols=line.split("\t");assert len(cols)==2
        ident,ct=cols
        assert ident not in inrows and len(ct)==97 and set(ct)<=set(AZ)
        inrows[ident]=ct
    expected=([f"PLANT_{i:02d}" for i in range(20)] if kind=="controls"
              else ["K4"]+[f"NULL_{i:02d}" for i in range(12)])
    assert list(inrows)==expected
    if kind=="target":
        assert inrows["K4"]=="OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        for name in expected[1:]: assert sorted(inrows[name])==sorted(inrows["K4"])
    candidates={}
    checks=0
    for line in Path(results).read_text().splitlines():
        r=json.loads(line)
        ident=r["id"]
        assert ident in inrows and ident not in candidates
        assert r["searched"]==m["searches_per_input"] and r["keyword_alphabets"]==m["keyword_alphabets"]
        assert len(r["candidates"])==12
        s=float("inf")
        seen=set()
        for c in r["candidates"]:
            assert set(c)=={"method","keyword_side","keyword_alphabet",
                             "right_initial_phase","score","plaintext"}
            assert c["method"]=="two_wheel_evolving_alphabet"
            assert type(c["score"]) in (int,float) and math.isfinite(c["score"])
            assert c["score"]<=s+1e-7
            s=c["score"]
            assert type(c["plaintext"])==str and len(c["plaintext"])==97
            k=(c["keyword_side"],c["keyword_alphabet"],c["right_initial_phase"])
            assert k not in seen;seen.add(k)
            assert check_forward(c["plaintext"],c["keyword_alphabet"],c["keyword_side"],c["right_initial_phase"])==inrows[ident],("wrong forward witness",ident,k)
            checks+=1
        candidates[ident]=r["candidates"]
    assert list(candidates)==expected
    return m,candidates,checks
def main():
    if len(sys.argv) not in (10,11):
        raise SystemExit("verify_frozen.py controls|target INPUT RESULTS MANIFEST SOURCE WORDS QUAD PROTOCOL OUT [TRUTH]")
    _,kind,inputs,results,manifest,source,words,quad,protocol,out,*extra=sys.argv
    assert kind in ("controls","target")
    assert (kind=="controls" and len(extra)==1) or (kind=="target" and not extra)
    assert not Path(out).exists()
    m,cands,checks=validate(kind,inputs,results,manifest,source,words,quad,protocol)
    result={"classification":"R56_POST_REMOTE_FREEZE_INDEPENDENT_AUDIT",
            "phase":kind,"raw_output_sha256":m["output_sha256"],
            "all_forward_witnesses_valid":True,"verified_witnesses":checks,
            "candidates_per_input":12,"inputs":len(cands)}
    if kind=="controls":
        truth=json.loads(Path(extra[0]).read_text())
        assert truth.keys()==cands.keys()
        exact=sum(cands[k][0]["plaintext"]==t["plaintext"] for k,t in truth.items())
        settings=sum(all(cands[k][0][key]==t[key] for key in
                    ("keyword_side","keyword_alphabet","right_initial_phase"))
                     for k,t in truth.items())
        result.update(top1_exact_plaintext=exact,top1_exact_key=settings,
                      gate_passed=exact>=16,required_exact=16,
                      limitation="closed-world synthetic keys, not an identification of K4 encryption")
    else:
        v=cands["K4"][0]["score"]
        nulls=[cands[f"NULL_{i:02d}"][0]["score"] for i in range(12)]
        exceed=sum(x>=v for x in nulls)
        result.update(k4_top_score=v,null_top_scores=nulls,
                      descriptive_upper_tail=(exceed+1)/13,
                      limitation="Only twelve shuffled nulls; no K4 clues evaluated in this stage")
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    with Path(out).open("x",encoding="ascii") as f:f.write(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("R56",kind,"forward witnesses",checks,
          "exact controls" if kind=="controls" else "K4 still unexamined",
          result.get("top1_exact_plaintext",""))
    if kind=="controls" and not result["gate_passed"]:
        print("R56 CONTROL GATE FAILED: NO K4 SEARCH PERMITTED",file=sys.stderr)
        sys.exit(2)
if __name__=="__main__":main()
