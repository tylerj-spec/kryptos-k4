#!/usr/bin/env python3
"""R60 immutable raw candidate freeze. Must not open the sealed true meanings/keys."""
import hashlib
import json
import math
import sys
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if len(sys.argv)!=9:
        raise SystemExit("freeze.py INPUT RAW_OUTPUT BLIND_SOLVER WORDMODEL QUAD PROTOCOL GENERATOR MANIFEST")
    _,inputfile,output,source,words,quad,protocol,generator,manifest=sys.argv
    assert not Path(manifest).exists()
    inp=Path(inputfile).read_text(encoding="ascii").splitlines()
    raw=Path(output).read_text(encoding="ascii").splitlines()
    assert len(inp)==len(raw)==40
    models=set()
    n=0
    for i,(ctrow,row) in enumerate(zip(inp,raw)):
        lab,ct=ctrow.split(chr(9))
        assert lab==f"CASE_{i:03d}"
        assert len(ct)==97 and set(ct)<=set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        record=json.loads(row)
        assert record["id"]==lab and record["route_count"]==6
        assert record["searched"]==record["key_count"]*13+6
        assert record["searched"]==877
        assert len(record["candidates"])==8
        assert record["detected_family"] in ("V","T","VT","TV","ABSTAIN")
        for cand in record["candidates"]:
            assert len(cand["plaintext"])==97
            assert cand["family"] in ("V","T","VT","TV")
            assert math.isfinite(cand["score"])
            models.add(cand["family"])
            n+=1
    assert n==320 and len(models)>=2
    data={
        "classification":"R60_STRICT_BLIND_HIDDEN_MEANING_CODEBOOK_CONTROLS",
        "status":"FROZEN_BEFORE_ANY_SEMANTIC_TRUTH_REVEAL",
        "phase":"controls",
        "original_ciphertext_search_attempted":False,
        "published_K4_letters_supplied_to_solver":False,
        "rows":40,"candidates_per_row":8,
        "searched_per_input":877,
        "input_sha256":sha(inputfile),
        "raw_output_sha256":sha(output),
        "blind_solver_sha256":sha(source),
        "generic_words_sha256":sha(words),
        "generic_quad_sha256":sha(quad),
        "protocol_sha256":sha(protocol),
        "sealed_generator_sha256":sha(generator),
    }
    path=Path(manifest)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="ascii") as f:
        json.dump(data,f,indent=2,sort_keys=True);f.write(chr(10))
    print("R60 FROZEN:",data["raw_output_sha256"],"40x8 full raw candidates")
if __name__=="__main__":main()
