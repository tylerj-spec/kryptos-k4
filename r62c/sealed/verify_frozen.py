#!/usr/bin/env python3
"""R62C independent AFTER-REMOTE-GIT-FREEZE 41,730 full text/key forward witnesses
and prespecified stage-one route-score GAP G calibration. No published K4 words
or offsets, no K4 answer checker, no reranking or candidate generation.
"""
import hashlib,json,math,statistics,sys
from pathlib import Path
N=97
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CANONICAL="2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
LM="b1a2a3c777dafd6eadc277ee50eb988858253a7843fedfc6903700c61a92a85a"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def substitution(plain,key,convention):
    # Independent arithmetic, no calls to R59 solver or its stage1 wrapper.
    assert len(plain)==len(key)==N
    name,op=convention.split("_")
    alpha=AZ if name=="AZ" else "KRYPTOSABCDEFGHIJLMNQUVWXZ"
    assert len(alpha)==26 and set(alpha)==set(AZ)
    ind={ch:n for n,ch in enumerate(alpha)}
    if op=="VIG":
        return "".join(alpha[(ind[p]+ind[k])%26] for p,k in zip(plain,key))
    if op=="BEAU":
        return "".join(alpha[(ind[k]-ind[p])%26] for p,k in zip(plain,key))
    raise AssertionError("unsupported frozen convention")

def routes_from_source(path):
    base={}
    for line in Path(path).read_text().splitlines():
        if not line.strip():continue
        name,op,seq=line.split()
        assert op=="S_then_T"
        p=[int(x) for x in seq.split(",")]
        assert len(p)==N and sorted(p)==list(range(N))
        base[name]=p
    assert len(base)==10
    return base

def route_for(original,shift):
    out={}
    for name,p in original.items():
        out[name]=[(i+shift)%N for i in p] if name.startswith(("COL_","SNAKE_")) else p[:]
    return out

def percentile_nearest(x,p):
    arr=sorted(x);assert len(arr)>0
    return arr[max(0,min(len(arr)-1,math.ceil(p*len(arr))-1))]

def main():
    if len(sys.argv)!=10:raise SystemExit("verify.py FROZEN_INPUT FULL_RAW FROZEN_MANIFEST STAGE1_SOURCE ROUTES WORDS PROTOCOL CANONICAL_K4 OUT_REPORT")
    _,inp,raw,manifest,blind,routes,word,protocol,k4path,out=sys.argv
    assert not Path(out).exists()
    m=json.loads(Path(manifest).read_text())
    assert m["status"]=="FROZEN_BEFORE_ANY_R62C_STATISTICS_OR_K4_PLAINTEXT_REVEAL"
    assert m["full_97_letter_plaintext_key_pairs"]==41730 and m["cases"]==321
    assert m["original_canonical_K4_source_sha256"]==sha(k4path)==CANONICAL
    for field,path in (
       ("input_sha256",inp),("complete_321_case_raw_output_sha256",raw),
       ("blind_stage1_source_sha256",blind),("routes_sha256",routes),
       ("word_model_sha256",word),("protocol_sha256",protocol)):
        assert m[field]==sha(path),(field,"source or raw Git freeze altered")
    assert m["model_sha256"]==LM
    assert m["fixed_statistic"]=="G=highest stage1 route total minus second-highest"
    original=Path(k4path).read_text(encoding="ascii").strip()
    assert len(original)==N and set(original)<=set(AZ)
    ts=Path(inp).read_text(encoding="ascii").splitlines()
    assert ts[0]=="id\tciphertext\tshift" and len(ts)==322
    inputs={}
    for i,line in enumerate(ts[1:]):
        id_,ct,s=line.split("\t")
        assert id_==f"CASE_{i:03d}" and id_ not in inputs and len(ct)==N
        s=int(s);assert s==(i if i<=20 else 0)
        if i<=20:assert ct==original
        else:assert sorted(ct)==sorted(original) and ct!=original
        inputs[id_]=(ct,s)
    assert len({v[0] for k,v in inputs.items() if int(k[5:])>=21})==300
    base=routes_from_source(routes)
    full=json.loads("null") if False else [json.loads(l) for l in Path(raw).read_text(encoding="ascii").splitlines()]
    assert len(full)==321
    g_values={}
    route_tops={}
    fw=0
    scores_valid=0
    for i,row in enumerate(full):
        id_=f"CASE_{i:03d}"
        ct,shift=inputs[id_]
        assert row["id"]==id_ and row["ciphertext"]==ct and row["route_shift"]==shift
        assert row["model"]=="R61_STAGE1_ONLY_30000_NO_POLISH"
        assert len(row["routes"])==10
        expected_perms=route_for(base,shift)
        route_scores=[]
        seen=set()
        for route in row["routes"]:
            name=route["name"]
            assert name in expected_perms and name not in seen
            seen.add(name)
            perm=route["permutation"]
            assert perm==expected_perms[name],(id_,"mismatched source route",name)
            info=route["solver_record"]
            assert info["id"]==f"{id_}__{route['original_route_index']}"
            assert len(info["per_convention"])==4 and len(info["top"])==8
            candidates=[info["best"]]+info["per_convention"]+info["top"]
            assert len(candidates)==13 and info["best"]==info["per_convention"][0]
            for z in candidates:
                p,k=z["plaintext"],z["key"]
                assert len(p)==len(k)==N and set(p)<=set(AZ) and set(k)<=set(AZ)
                stage=substitution(p,k,z["convention"])
                recovered="".join(stage[perm[j]] for j in range(N))
                assert recovered==ct,("INDEPENDENT FORWARD FAILED",id_,name,z["convention"])
                fw+=1
            top=info["best"]
            assert abs((top["lm"]+top["word"])-top["total"])<=.0003
            scores_valid+=1
            route_scores.append((top["total"],name))
        assert len(seen)==10
        route_scores.sort(key=lambda x:(-x[0],x[1]))
        g=route_scores[0][0]-route_scores[1][0]
        assert g>=-1e-8
        g_values[id_]=g
        route_tops[id_]={"first":route_scores[0][1],"second":route_scores[1][1],
                         "top1":route_scores[0][0],"top2":route_scores[1][0]}
    assert fw==41730 and scores_valid==3210
    g0=g_values["CASE_000"]
    controls=[g_values[f"CASE_{j:03d}"] for j in range(21,321)]
    alternative=[g_values[f"CASE_{j:03d}"] for j in range(1,21)]
    exceeds=sum(x>=g0-1e-9 for x in controls)
    alt_exceeds=sum(x>=g0-1e-9 for x in alternative)
    historical_gap=21.2131
    comparable=abs(g0-historical_gap)<=.0002
    p=(exceeds+1)/301
    pp=exceeds/300
    z=1.96
    center=(pp+z*z/(2*300))/(1+z*z/300)
    margin=z*math.sqrt(pp*(1-pp)/300+z*z/(4*300*300))/(1+z*z/300)
    pass_screen=comparable and p<.01 and alt_exceeds/20<.05
    output={
       "classification":"R62C_AFTER_REMOTE_FREEZE_INDEPENDENT_GAP_CALIBRATION_NO_K4_CLUES",
       "status":"FORWARD_AUDIT_PASS",
       "raw_output_sha256":m["complete_321_case_raw_output_sha256"],
       "original_ciphertext_sha256":CANONICAL,
       "all_41730_independent_97_character_forward_witnesses_valid":True,
       "verified_witnesses":fw,
       "all_3210_stage1_route_scores_checked":scores_valid,
       "historical_R61_G":historical_gap,
       "contemporary_K4_G":g0,
       "contemporary_K4_top_routes":route_tops["CASE_000"],
       "matches_historical_gap_within_0_0002":comparable,
       "fresh_nulls":300,
       "nulls_at_or_above_K4_G":exceeds,
       "empirical_plus_one_tail":p,
       "null_gap_median":statistics.median(controls),
       "null_gap_q95_nearest_rank":percentile_nearest(controls,.95),
       "null_gap_q99_nearest_rank":percentile_nearest(controls,.99),
       "null_gap_max":max(controls),
       "null_gap_sorted":sorted(controls),
       "null_tail_binomial_fraction":pp,
       "null_tail_wilson_95pct":[max(0,center-margin),min(1,center+margin)],
       "alternative_route_families":20,
       "alternate_gaps_at_or_above_original":alt_exceeds,
       "alternate_rate":alt_exceeds/20,
       "all_alternative_gaps":[{"shift":j,"g":v,"top":route_tops[f"CASE_{j:03d}"]}
                               for j,v in enumerate([g0]+alternative)],
       "predeclared_screen_passed":pass_screen,
       "screen_decision":("WORTH_TARGETED_PHYSICAL_MECHANISM_RESEARCH_NOT_K4_SOLVE"
                          if pass_screen else "NO_CORROBORATED_UNIQUE_COL_LT_GAP"),
       "meaning":"Posthoc-selected G; shuffle calibration descriptive; correlated alternative route families do NOT provide formal selection-adjusted probability",
       "limitations":[
          "Original 21.2131 stage1 G was selected after seeing R61 original table",
          "20 offsets are correlated, partly arbitrary nuisance families and not authenticated physical K4 routes",
          "R59 scoring with English plain+key is a closed-world method and can manufacture valid but meaningless witnesses",
          "No plaintext interpretation, source-backed key derivation or known-letter K4 validation",
          "An ordinary semantic codebook is not tested; Germanic phonetic spelling also not tested",
          "The negative is only against specialness of this predeclared stage1 route gap under sampled alternatives"
       ]
    }
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    with Path(out).open("x",encoding="ascii") as f:json.dump(output,f,sort_keys=True,indent=2);f.write("\n")
    print("R62C afterfreeze: all",fw,"forward witnesses verified; G",g0,
          "nulls >= G",exceeds,"of 300; alternative >= G",alt_exceeds,"of 20; screen",pass_screen)
if __name__=="__main__":main()
