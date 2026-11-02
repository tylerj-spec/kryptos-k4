#!/usr/bin/env python3
"""Freeze full R58B 101-case blind output and source hashes before known-letter checking."""
from pathlib import Path
import hashlib,json,sys

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=10:
        raise SystemExit("freeze_target.py INPUT RESULTS BLIND WORDS QUAD R58A_PROTOCOL R58B_PROTOCOL PREPARER MANIFEST")
    _,inputs,outputs,source,words,quad,prior_protocol,protocol,preparer,manifest=sys.argv
    assert not Path(manifest).exists()
    a=Path(inputs).read_text(encoding="ascii").splitlines()
    b=Path(outputs).read_text(encoding="ascii").splitlines()
    assert len(a)==len(b)==101
    searched=None
    for i,(inrow,outrow) in enumerate(zip(a,b)):
        tag,ct=inrow.split(chr(9))
        expected="K4" if i==0 else f"NULL_{i-1:03d}"
        assert tag==expected and len(ct)==97
        assert set(ct)<=set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        x=json.loads(outrow)
        assert x["id"]==tag and x["route_count"]==6 and len(x["candidates"])==8
        assert x["searched"]==x["key_count"]*13+6
        assert all(len(z["plaintext"])==97 for z in x["candidates"])
        if searched is None:searched=x["searched"]
        else:assert searched==x["searched"]
    m={
      "classification":"R58B_REMOTE_FROZEN_ORIGINAL_K4_CIPHERTEXT_ONLY",
      "status":"FROZEN_BEFORE_ANY_K4_CLUE",
      "phase":"target",
      "inputs":101,"searched_per_input":searched,
      "full_candidates_per_input":8,
      "input_sha256":sha(inputs),"output_sha256":sha(outputs),
      "blind_source_sha256":sha(source),
      "generic_words_sha256":sha(words),"generic_quad_sha256":sha(quad),
      "original_prereg_sha256":sha(prior_protocol),
      "target_protocol_sha256":sha(protocol),
      "target_preparer_sha256":sha(preparer)
    }
    Path(manifest).parent.mkdir(parents=True,exist_ok=True)
    with Path(manifest).open("x",encoding="ascii") as f:
        json.dump(m,f,sort_keys=True,indent=2);f.write(chr(10))
    print("R58B BLIND K4 remote-freeze SHA256",m["output_sha256"])
if __name__=="__main__":main()
