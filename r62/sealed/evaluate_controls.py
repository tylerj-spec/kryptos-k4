#!/usr/bin/env python3
"""R62 B separate AFTER-REMOTE-FREEZE independent control evaluator.
No K4 original ciphertext, released letters or published letter offsets are used.
Does NOT import the frozen solver or generator's encryptor.
"""
import hashlib,json,math,statistics,sys
from pathlib import Path
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ"
N=97
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fwd(plain,key,name):
    assert len(plain)==len(key)==N
    alpha,rule=name.split("_")
    a=AZ if alpha=="AZ" else KRY
    index={letter:i for i,letter in enumerate(a)}
    seq=[]
    for p,k in zip(plain,key):
        pi,ki=index[p],index[k]
        value=(pi+ki)%26 if rule=="VIG" else (ki-pi)%26 if rule=="BEAU" else None
        assert value is not None
        seq.append(a[value])
    return "".join(seq)

def main():
    if len(sys.argv)!=12:
        raise SystemExit("evaluate_controls.py INPUT RESULTS MANIFEST TRUTH PROVENANCE SOLVER LM WORDS RUNNER PROTOCOL MODERN OUT")
    _,inp,raw,manifest,truth_path,provenance,solver,lm,words,runner,protocol,modern,out=sys.argv
    assert not Path(out).exists()
    m=json.loads(Path(manifest).read_text())
    assert m["status"]=="FROZEN_BEFORE_KEY_FAMILY_OR_TEXT_REVEAL"
    for label,file in (
        ("input_sha256",inp),("raw_output_sha256",raw),("source_sha256",solver),
        ("lm_sha256",lm),("word_model_sha256",words),("runner_sha256",runner),
        ("protocol_sha256",protocol),("modern_messages_sha256",modern)):
        assert m[label]==h(file),("immutable remote freeze mismatch",label)
    provenance=json.loads(Path(provenance).read_text())
    assert provenance["input_sha256"]==m["input_sha256"]
    assert provenance["truth_sha256"]==h(truth_path)
    truth=json.loads(Path(truth_path).read_text())
    blind=Path(inp).read_text().splitlines()
    raws=[json.loads(x) for x in Path(raw).read_text().splitlines()]
    assert blind[0]=="id\tciphertext" and len(blind)==81 and len(raws)==80 and len(truth)==80
    plants=[];nulls=[];n_witness=0;n_orig=0
    for j,(line,r) in enumerate(zip(blind[1:],raws)):
        ident,ct=line.split("\t")
        assert ident==f"CASE_{j:03d}"==r["id"]
        assert len(ct)==N and set(ct)<=set(AZ)
        t=truth[ident]
        assert t["ciphertext"]==ct
        assert t["role"] in ("plant","shuffle")
        assert r["best"]==r["per_convention"][0]
        assert len(r["per_convention"])==4 and len(r["top"])==8
        for c in (r["best"],*r["per_convention"],*r["top"]):
            p=c["plaintext"];k=c["key"]
            assert len(p)==len(k)==N and set(p)<=set(AZ) and set(k)<=set(AZ)
            assert fwd(p,k,c["convention"])==ct,("forged witness",ident)
            n_witness+=1
        if t["role"]=="plant":
            assert fwd(t["plaintext"],t["key"],t["convention"])==ct
            n_orig+=1
            a=r["best"]["plaintext"];b=r["best"]["key"]
            actual=t["plaintext"]
            plants.append({
                "id":ident,"cohort":t["cohort"],"subgroup":t["subgroup"],
                "score":r["best"]["total"],"true_convention":t["convention"],
                "found_convention":r["best"]["convention"],
                "convention_ok":r["best"]["convention"]==t["convention"],
                "plain_stream_letters":max(sum(x==y for x,y in zip(a,actual)),
                                           sum(x==y for x,y in zip(b,actual))),
                "unordered_pair_correct":sum({x,y}=={u,v} for x,y,u,v in zip(a,b,actual,t["key"])),
                "plant_slot":t["plant_slot"]
            })
        else:
            nulls.append({"id":ident,"cohort":t["cohort"],"score":r["best"]["total"],
                          "plant_slot":t["plant_slot"]})
    assert n_witness==80*13 and n_orig==40
    assert len(plants)==len(nulls)==40
    assert len({p["plant_slot"] for p in plants})==40
    assert len({n["plant_slot"] for n in nulls})==40
    by_slot={n["plant_slot"]:n for n in nulls}
    orig_by_slot={p["plant_slot"]:p for p in plants}
    for k,v in by_slot.items():
        orig=next(t for t in truth.values() if t["role"]=="plant" and t["plant_slot"]==k)
        null=next(t for t in truth.values() if t["role"]=="shuffle" and t["plant_slot"]==k)
        assert sorted(orig["ciphertext"])==sorted(null["ciphertext"])
        assert orig["ciphertext"]!=null["ciphertext"]
        assert v["cohort"]==orig_by_slot[k]["cohort"]
    report={}
    for group in ("SANBORN","MODERN"):
        pp=[p for p in plants if p["cohort"]==group]
        nn=[n for n in nulls if n["cohort"]==group]
        assert len(pp)==len(nn)==20
        max_null=max(n["score"] for n in nn)
        found=sum(x["score"]>max_null for x in pp)
        report[group]={
            "samples":20,"detection_count":found,"detection_rate":found/20,
            "original_R59_gate_16_of_20_passed":found>=16,
            "null_max":max_null,"null_median":statistics.median(x["score"] for x in nn),
            "plants_above_own_matching_null":sum(p["score"]>by_slot[p["plant_slot"]]["score"] for p in pp),
            "correct_convention":sum(x["convention_ok"] for x in pp),
            "correct_unordered_pairs_ge60":sum(x["unordered_pair_correct"]>=60 for x in pp),
            "median_unordered_pair_correct":statistics.median(x["unordered_pair_correct"] for x in pp),
            "median_plain_stream_letters_correct":statistics.median(x["plain_stream_letters"] for x in pp),
            "details":[{**p,"strict_detected":p["score"]>max_null} for p in pp]}
    pooled_null_max=max(n["score"] for n in nulls)
    subgroups={}
    for name in ("K1_K2","K3_FIRST_ONLY","MODERN_UNIQUE"):
        pp=[p for p in plants if p["subgroup"]==name]
        subgroups[name]={"n":len(pp),
           "detected_vs_group_null_max":sum(p["score"]>report[p["cohort"]]["null_max"] for p in pp),
           "mean_score":statistics.mean(p["score"] for p in pp),
           "median_plain_stream_correct":statistics.median(p["plain_stream_letters"] for p in pp)}
    cross={
        "sanborn_nulls_higher_than_modern_null_max":sum(n["score"]>report["MODERN"]["null_max"] for n in nulls if n["cohort"]=="SANBORN"),
        "modern_nulls_higher_than_sanborn_null_max":sum(n["score"]>report["SANBORN"]["null_max"] for n in nulls if n["cohort"]=="MODERN")
    }
    result={
        "status":"COMPLETED_AFTER_REMOTE_GIT_FREEZE",
        "classification":"R62_INDEPENDENT_R59_POWER_CALIBRATION_NOT_K4_TEST",
        "raw_output_sha256":m["raw_output_sha256"],
        "source_hashes_verified":True,"full_97_character_candidate_witnesses":n_witness,
        "true_generating_ciphertexts_independently_verified":n_orig,
        "null_frequency_multisets_verified":40,
        "cohorts":report,"subgroups":subgroups,
        "all_40_nulls_threshold":pooled_null_max,
        "detected_against_all_40_nulls_by_cohort":{
           group:sum(p["score"]>pooled_null_max for p in plants if p["cohort"]==group)
           for group in ("SANBORN","MODERN")},
        "cross_cohort_null_diagnostics":cross,
        "limitations":[
           "R59 in-place solver only; no R61 transposition power test on modern English",
           "K3 source overlaps Carter and Mace 1923 included in R59 training",
           "K1/K2 text windows overlap and are not 12 independent messages",
           "Original 20 modern passages were author-written, 97-letter beginnings, not authentic K4 prose",
           "A high score is not full 97-letter recovery; per-stream and unordered pair correctness reported",
           "Only fixed R59 English-key AZ/KRY VIG/BEAU family, not novel masking"
        ]
    }
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    with Path(out).open("x",encoding="ascii") as f:json.dump(result,f,sort_keys=True,indent=2);f.write("\n")
    print("R62 B independent after-freeze:",{g:(report[g]["detection_count"],20) for g in report},
          "witnesses",n_witness,"source hashes verified")
if __name__=="__main__":main()
