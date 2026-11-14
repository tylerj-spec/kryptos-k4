#!/usr/bin/env python3
"""R62C single-writer combined 321-case 41,730-full-pair remote-Git freeze validator.
Does not compute gap statistics, read known plaintext or use any R61 K4 reveal.
"""
import hashlib,json,sys
from pathlib import Path
N=97
AZ=set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
SHA_ORIGINAL="2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=9:
        raise SystemExit("freeze.py INPUT SHARDS_DIR SOURCE ROUTES PROTOCOL WORDS FROZEN_RAW FROZEN_MANIFEST")
    _,inputpath,shards,source,routes,protocol,words,outraw,outmanifest=sys.argv
    out=Path(outraw);mf=Path(outmanifest)
    assert not out.exists() and not mf.exists()
    records=Path(inputpath).read_text(encoding="ascii").splitlines()
    assert records[0]=="id\tciphertext\tshift" and len(records)==322
    inputs={}
    for i,line in enumerate(records[1:]):
        id_,ct,shift=line.split("\t")
        assert id_==f"CASE_{i:03d}" and len(ct)==N and set(ct)<=AZ and int(shift)==(i if i<=20 else 0)
        inputs[id_]=(ct,int(shift))
    allitems={}
    metadatas=[]
    for i in range(12):
        shard=Path(shards)/f"shard_{i:02d}.jsonl"
        manifest=Path(shards)/f"shard_{i:02d}.manifest.json"
        assert shard.is_file() and manifest.is_file(),(shard,manifest)
        m=json.loads(manifest.read_text())
        assert m["shard"]==i and m["input_sha256"]==sha(inputpath)
        assert m["routes_sha256"]==sha(routes)
        assert m["word_model_sha256"]==sha(words)
        assert m["source_sha256"]==sha(source)
        assert m["lm_sha256"]=="b1a2a3c777dafd6eadc277ee50eb988858253a7843fedfc6903700c61a92a85a"
        assert m["shard_raw_sha256"]==sha(shard)
        assert m["solver_params"]==["30000","2000","1","AZ_VIG,AZ_BEAU,KRY_VIG,KRY_BEAU","0","20000"]
        assert m["original_K4_published_plaintext_loaded"] is False
        metadatas.append(m)
        actual=0
        for line in shard.read_text(encoding="ascii").splitlines():
            item=json.loads(line)
            ident=item["id"]
            assert ident in inputs and ident not in allitems
            assert int(ident.split("_")[1])%12==i
            assert (item["ciphertext"],item["route_shift"])==inputs[ident]
            assert item["model"]=="R61_STAGE1_ONLY_30000_NO_POLISH"
            assert len(item["routes"])==10
            names=set()
            for route in item["routes"]:
                assert route["name"] not in names
                names.add(route["name"])
                perm=route["permutation"]
                assert len(perm)==N and sorted(perm)==list(range(N))
                s=route["solver_record"]
                assert s["id"]==f"{ident}__{route['original_route_index']}"
                assert s["best"]==s["per_convention"][0]
                assert len(s["per_convention"])==4 and len(s["top"])==8
                for cand in [s["best"]]+s["per_convention"]+s["top"]:
                    assert len(cand["plaintext"])==len(cand["key"])==N
                    assert set(cand["plaintext"])<=AZ and set(cand["key"])<=AZ
                    assert cand["convention"] in ("AZ_VIG","AZ_BEAU","KRY_VIG","KRY_BEAU")
            allitems[ident]=item
            actual+=1
        assert actual==m["cases"]
    assert len(allitems)==321 and sum(x["cases"] for x in metadatas)==321
    assert len({x["lm_sha256"] for x in metadatas})==1
    assert len({x["solver_binary_sha256"] for x in metadatas})==1, "shards used different binaries; abort"
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="ascii") as f:
        for j in range(321):
            f.write(json.dumps(allitems[f"CASE_{j:03d}"],sort_keys=True,separators=(",",":"))+"\n")
    result={
      "classification":"R62C_BLIND_10_ROUTE_STAGE1_ALL_97_TEXT_AND_KEY_PAIRS",
      "status":"FROZEN_BEFORE_ANY_R62C_STATISTICS_OR_K4_PLAINTEXT_REVEAL",
      "original_canonical_K4_source_sha256":SHA_ORIGINAL,
      "input_sha256":sha(inputpath),
      "complete_321_case_raw_output_sha256":sha(out),
      "blind_stage1_source_sha256":sha(source),
      "routes_sha256":sha(routes),"protocol_sha256":sha(protocol),
      "word_model_sha256":sha(words),
      "model_sha256":metadatas[0]["lm_sha256"],
      "solver_binary_sha256":metadatas[0]["solver_binary_sha256"],
      "full_97_letter_plaintext_key_pairs":41730,
      "cases":321,"original_ciphertext_route_families":21,
      "fresh_frequency_matched_nulls":300,
      "base_route_count":10,"fixed_alternative_offsets":list(range(1,21)),
      "fixed_statistic":"G=highest stage1 route total minus second-highest",
      "shard_manifest_sha256":[sha(Path(shards)/f"shard_{i:02d}.manifest.json") for i in range(12)],
      "shard_raw_sha256":[metadatas[i]["shard_raw_sha256"] for i in range(12)],
      "known_K4_plaintext_used":False,
      "K4_letter_checker_called":False,
      "independent_forward_verifier_not_yet_run":True
    }
    with mf.open("x",encoding="ascii") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("R62C remotely ready to freeze SHA",result["complete_321_case_raw_output_sha256"],
         "cases",321,"full 97-char pairs",41730)
if __name__=="__main__":main()
