#!/usr/bin/env python3
"""Write-only R58 controls manifest. No plaintext truth, keys or K4 clues are read."""
import hashlib,json,sys
from pathlib import Path

def h(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    if len(sys.argv)!=9:
        raise SystemExit("freeze.py INPUT RESULTS BLIND WORDS QUAD PROTOCOL GENERATOR MANIFEST")
    _,input_file,results,blind,words,quad,protocol,generator,manifest=sys.argv
    mpath=Path(manifest)
    assert not mpath.exists()
    inp=Path(input_file).read_text(encoding="ascii").splitlines()
    raw=Path(results).read_text(encoding="ascii").splitlines()
    assert len(inp)==len(raw)==120
    previous_ids=set()
    search_count=None
    for i,(text,line) in enumerate(zip(inp,raw)):
        fields=text.split(chr(9))
        assert len(fields)==2 and fields[0]==f"CASE_{i:03d}" and len(fields[1])==97
        assert fields[1].isupper() and fields[1].isalpha()
        o=json.loads(line)
        assert o["id"]==fields[0] and len(o["candidates"])==8
        assert o["route_count"]==6 and o["searched"]==o["key_count"]*13+6
        assert all(len(c["plaintext"])==97 for c in o["candidates"])
        if search_count is None:search_count=o["searched"]
        else:assert search_count==o["searched"]
        assert o["id"] not in previous_ids;previous_ids.add(o["id"])
    data={
      "classification":"R58_CIPHERTEXT_ONLY_ALL_FAMILIES_UNKNOWN",
      "phase":"controls","status":"FROZEN_BLIND_R58",
      "input_sha256":h(input_file),"output_sha256":h(results),
      "blind_source_sha256":h(blind),"generic_words_sha256":h(words),
      "generic_quad_sha256":h(quad),"protocol_sha256":h(protocol),
      "generator_sha256":h(generator),
      "inputs":120,"full_candidates_per_input":8,
      "searched_settings_per_input":search_count,
      "known_plaintext_exposed_to_solver":False,
      "published_K4_clues_supplied_to_solver":False
    }
    mpath.parent.mkdir(parents=True,exist_ok=True)
    with mpath.open("x",encoding="ascii") as f:
        f.write(json.dumps(data,indent=2,sort_keys=True)+chr(10))
    print("R58 frozen raw SHA256:",data["output_sha256"],"searches",search_count)
if __name__=="__main__":
    main()
