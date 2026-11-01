#!/usr/bin/env python3
"""No-overwrite remote-freeze manifest for ciphertext-only R56 results.
This code never reads sealed truth or public K4 plaintext.
"""
from pathlib import Path
import hashlib,json,sys
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=9:
        raise SystemExit("freeze.py controls|target INPUT RESULTS SOURCE WORDMODEL QUAD PROTOCOL OUT")
    _,kind,inputfile,results,source,words,quad,protocol,out=sys.argv
    assert kind in ("controls","target")
    assert not Path(out).exists(),"refuse overwrite"
    lines=Path(inputfile).read_text(encoding="ascii").splitlines()
    outputs=Path(results).read_text(encoding="ascii").splitlines()
    expect=20 if kind=="controls" else 13
    assert len(lines)==len(outputs)==expect
    expected_names=([f"PLANT_{i:02d}" for i in range(20)] if kind=="controls"
                    else ["K4"]+[f"NULL_{i:02d}" for i in range(12)])
    searched=None
    alphas=None
    for i,(line,r) in enumerate(zip(lines,outputs)):
        fields=line.split("\t")
        assert len(fields)==2 and fields[0]==expected_names[i]
        assert len(fields[1])==97 and fields[1].isupper() and fields[1].isalpha()
        rec=json.loads(r)
        assert set(rec)=={"id","searched","keyword_alphabets","candidates"}
        assert rec["id"]==fields[0] and len(rec["candidates"])==12
        assert rec["searched"]==52*rec["keyword_alphabets"]
        assert rec["keyword_alphabets"]>0
        if searched is None:searched=rec["searched"];alphas=rec["keyword_alphabets"]
        else:assert searched==rec["searched"] and alphas==rec["keyword_alphabets"]
        for candidate in rec["candidates"]:
            assert len(candidate["plaintext"])==97 and candidate["plaintext"].isupper()
    p=Path(out)
    p.parent.mkdir(parents=True,exist_ok=True)
    manifest={
        "classification":"REMOTE_FROZEN_R56_CIPHERTEXT_ONLY_UNREVEALED",
        "phase":kind,"status":"FROZEN_NO_EVALUATION",
        "input_count":expect,"searches_per_input":searched,
        "keyword_alphabets":alphas,"candidates_per_input":12,
        "input_sha256":sha(inputfile),"output_sha256":sha(results),
        "source_sha256":sha(source),"word_model_sha256":sha(words),
        "quad_model_sha256":sha(quad),"protocol_sha256":sha(protocol)
    }
    with p.open("x",encoding="ascii") as f:f.write(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("R56 frozen",kind,"sha256",manifest["output_sha256"],"results",expect)
if __name__=="__main__":main()
