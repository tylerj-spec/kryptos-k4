#!/usr/bin/env python3
"""R62 B blind-output freeze. Never reads truth or any K4 plaintext clue."""
import hashlib, json, sys
from pathlib import Path
AZ=set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=10:raise SystemExit("freeze_b.py INPUT RAW SOLVER LM WORDS RUNNER PROTOCOL GENERATOR MODERN OUT_MANIFEST")
    _,inp,out,solver,lm,words,runner,protocol,gen,modern,manifest=sys.argv
    assert not Path(manifest).exists()
    src=Path(inp).read_text(encoding="ascii").splitlines()
    raw=Path(out).read_text(encoding="ascii").splitlines()
    assert src[0]=="id\tciphertext" and len(src)==81 and len(raw)==80
    for j,(line,result) in enumerate(zip(src[1:],raw)):
        tag,ct=line.split("\t")
        assert tag==f"CASE_{j:03d}" and len(ct)==97 and set(ct)<=AZ
        r=json.loads(result)
        assert r["id"]==tag and "best" in r and len(r["per_convention"])==4 and len(r["top"])==8
        assert r["best"]==r["per_convention"][0]
        for cand in [r["best"]]+r["per_convention"]+r["top"]:
            assert len(cand["plaintext"])==len(cand["key"])==97
            assert set(cand["plaintext"])<=AZ and set(cand["key"])<=AZ
            assert cand["convention"] in ("AZ_VIG","AZ_BEAU","KRY_VIG","KRY_BEAU")
    man={"classification":"R62_FROZEN_BLIND_B_NO_TRUTH",
        "status":"FROZEN_BEFORE_KEY_FAMILY_OR_TEXT_REVEAL",
        "input_sha256":h(inp),"raw_output_sha256":h(out),"source_sha256":h(solver),
        "lm_sha256":h(lm),"word_model_sha256":h(words),"runner_sha256":h(runner),
        "protocol_sha256":h(protocol),"sealed_generator_sha256":h(gen),
        "modern_messages_sha256":h(modern),"inputs":80,
        "complete_candidate_fields_per_case":13,"recovered_key_97char_in_every_candidate":True,
        "original_K4_attempted":False}
    Path(manifest).parent.mkdir(parents=True,exist_ok=True)
    with Path(manifest).open("x",encoding="ascii") as f:json.dump(man,f,sort_keys=True,indent=2);f.write("\n")
    print("R62 B RAW RESULTS frozen: 80x13 full 97-char output pairs, sha",man["raw_output_sha256"])
if __name__=="__main__":main()
