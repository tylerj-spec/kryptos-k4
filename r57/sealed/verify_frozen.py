#!/usr/bin/env python3
"""R57 independently validate REMOTE-frozen full plaintexts by matrix forward encryptor.
No published K4 plaintext known or accessible in this file.
"""
import hashlib,json,math,sys
from pathlib import Path
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def enc(p,a,b,c,d):
    assert len(p)==97 and set(p)<=set(AZ)
    assert all(type(v)==int and 0<=v<26 for v in (a,b,c,d))
    assert math.gcd(a,26)==math.gcd((a*d-b*c)%26,26)==1
    out=[]
    for i in range(0,96,2):
        x=ord(p[i])-65;y=ord(p[i+1])-65
        out.append(chr(65+(a*x+b*y)%26))
        out.append(chr(65+(c*x+d*y)%26))
    out.append(chr(65+(a*(ord(p[96])-65)+b*23)%26))
    return "".join(out)
def check(kind,inp,results,manifest,source,quad,protocol):
    m=json.loads(Path(manifest).read_text())
    assert m["status"]=="FROZEN_WITHOUT_TRUTH" and m["phase"]==kind
    for path,field in ((inp,"input_sha256"),(results,"output_sha256"),
                       (source,"source_sha256"),(quad,"quad_sha256"),
                       (protocol,"protocol_sha256")):
        assert sha(path)==m[field],("frozen hash mismatch",path)
    inputs={}
    for line in Path(inp).read_text().splitlines():
        fields=line.split("\t");assert len(fields)==2
        lab,ct=fields
        assert lab not in inputs and len(ct)==97 and set(ct)<=set(AZ)
        inputs[lab]=ct
    ids=([f"PLANT_{i:02d}" for i in range(20)] if kind=="controls"
         else ["K4"]+[f"NULL_{i:02d}" for i in range(12)])
    assert list(inputs)==ids
    if kind=="target":
        assert inputs["K4"]=="OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        for lab in ids[1:]:assert sorted(inputs[lab])==sorted(inputs["K4"])
    outputs={}
    count=0
    for row in Path(results).read_text().splitlines():
        r=json.loads(row);lab=r["id"]
        assert lab in inputs and lab not in outputs and r["searched"]==97344
        assert len(r["candidates"])==12
        seen=set();last=float("inf")
        for cand in r["candidates"]:
            assert set(cand)=={"method","a","b","c","d","score","plaintext"}
            assert cand["method"]=="hill_2x2_mod26_padded_truncation"
            assert isinstance(cand["score"],(float,int)) and math.isfinite(cand["score"])
            assert cand["score"]<=last+1e-7;last=cand["score"]
            key=tuple(cand[z] for z in ("a","b","c","d"))
            assert key not in seen;seen.add(key)
            assert enc(cand["plaintext"],*key)==inputs[lab],("invalid witness",lab,key)
            count+=1
        outputs[lab]=r["candidates"]
    assert list(outputs)==ids
    return m,outputs,count
def main():
    if len(sys.argv) not in (9,10):
        raise SystemExit("verify.py controls|target IN RESULTS MANIFEST SOURCE QUAD PROTOCOL OUT [TRUTH]")
    _,kind,inp,results,manifest,source,quad,protocol,out,*truth_path=sys.argv
    assert kind in ("controls","target")
    assert (kind=="controls" and len(truth_path)==1) or(kind=="target" and not truth_path)
    assert not Path(out).exists()
    m,outputs,count=check(kind,inp,results,manifest,source,quad,protocol)
    report={"classification":"R57_POST_REMOTE_FREEZE_INDEPENDENT_FORWARD_AUDIT",
            "phase":kind,"raw_output_sha256":m["output_sha256"],
            "all_forward_witnesses_valid":True,"verified_witnesses":count,
            "inputs":len(outputs)}
    if kind=="controls":
        truth=json.loads(Path(truth_path[0]).read_text())
        assert truth.keys()==outputs.keys()
        exact=sum(outputs[k][0]["plaintext"]==t["plaintext"] for k,t in truth.items())
        key_exact=sum(all(outputs[k][0][x]==t[x] for x in ("a","b","c","d"))
                      for k,t in truth.items())
        report.update(top1_exact_plaintext=exact,top1_exact_key=key_exact,
                      required_exact=16,gate_passed=exact>=16,
                      limitation="closed-world synthetic controls, not identification of a K4 method")
    else:
        k4score=outputs["K4"][0]["score"]
        nulls=[outputs[f"NULL_{i:02d}"][0]["score"] for i in range(12)]
        report.update(k4_top_score=k4score,null_top_scores=nulls,
                      descriptive_upper_tail=(sum(x>=k4score for x in nulls)+1)/13,
                      limitation="twelve shuffled nulls give descriptive score only")
    path=Path(out);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="ascii") as f:f.write(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("R57",kind,"forward witnesses",count,
          "exact recovered" if kind=="controls" else "no clues evaluated",
          report.get("top1_exact_plaintext",""))
    if kind=="controls" and not report["gate_passed"]:
        print("R57 failed unknown-key gate; K4 job MUST NOT run",file=sys.stderr)
        sys.exit(2)
if __name__=="__main__":main()
