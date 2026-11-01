#!/usr/bin/env python3
"""Freeze blind outputs without known plaintext. Run before sealed evaluator."""
import hashlib,json,sys
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=8:
        raise SystemExit("freeze.py controls|target INPUT RESULTS BLIND_SOURCE QUAD PROTOCOL MANIFEST")
    _,kind,inp,results,src,quad,protocol,out=sys.argv
    assert kind in ("controls","target") and not Path(out).exists()
    a=Path(inp).read_text().splitlines()
    b=Path(results).read_text().splitlines()
    names=([f"PLANT_{i:02d}" for i in range(20)] if kind=="controls"
           else ["K4"]+[f"NULL_{i:02d}" for i in range(12)])
    assert len(a)==len(b)==len(names)
    for name,line,row in zip(names,a,b):
        fields=line.split("\t")
        assert len(fields)==2 and fields[0]==name
        assert len(fields[1])==97 and fields[1].isupper() and fields[1].isalpha()
        obj=json.loads(row)
        assert obj["id"]==name and obj["searched"]==97344
        assert len(obj["candidates"])==12
        assert all(len(x["plaintext"])==97 for x in obj["candidates"])
    m={"phase":kind,"classification":"R57_REMOTE_FROZEN_CIPHERTEXT_ONLY",
       "status":"FROZEN_WITHOUT_TRUTH","inputs":len(a),
       "searched_per_input":97344,"candidates_per_input":12,
       "input_sha256":sha(inp),"output_sha256":sha(results),
       "source_sha256":sha(src),"quad_sha256":sha(quad),
       "protocol_sha256":sha(protocol)}
    path=Path(out);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="ascii") as f:f.write(json.dumps(m,sort_keys=True,indent=2)+"\n")
    print("R57",kind,"blind frozen hash",m["output_sha256"])
if __name__=="__main__":main()
