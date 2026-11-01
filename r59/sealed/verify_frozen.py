#!/usr/bin/env python3
"""R59 post-REMOTE-freeze evaluator, wholly separate from ciphertext-only scanner.
No released K4 plaintext, offsets or clues appear in this file.
It verifies 90 synthetic full 97-letter forward witnesses independently and
measures preregistered fingerprint power and confidence.
"""
from pathlib import Path
import hashlib
import json
import math
import statistics
import sys

AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N=97
FAMILIES=("SIMULATED_UNIFORM_PAD","PERIODIC_MASK","BOOK_RUNNING_KEY")

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def independently_encrypt(p,key):
    assert len(p)==len(key)==N
    assert set(p)<=set(AZ) and set(key)<=set(AZ)
    result=[]
    for pc,kc in zip(p,key):
        x=ord(pc)-65
        y=ord(kc)-65
        result.append(AZ[(x+y)%26])
    return "".join(result)

def main():
    if len(sys.argv)!=10:
        raise SystemExit("verify.py FROZEN_INPUT FROZEN_RESULTS MANIFEST BLIND_SOURCE PRIOR PROTOCOL GENERATOR SEALED_TRUTH OUTPUT")
    _,inputfile,rawfile,manifest,source,prior,protocol,generator,truthfile,out=sys.argv
    assert not Path(out).exists(),"do not overwrite an evaluator report"
    m=json.loads(Path(manifest).read_text())
    assert m["phase"]=="controls_plus_K4"
    assert m["status"]=="FROZEN_BEFORE_ANY_SEALED_TRUE_FAMILY_OR_KEY"
    for path,field in (
        (inputfile,"input_sha256"),(rawfile,"output_sha256"),
        (source,"blind_source_sha256"),(prior,"monogram_prior_sha256"),
        (protocol,"protocol_sha256"),(generator,"sealed_generator_sha256")
    ):
        assert sha(path)==m[field],("Git-frozen input/output/source changed",path)
    rows=Path(inputfile).read_text(encoding="ascii").splitlines()
    outputs=[json.loads(z) for z in Path(rawfile).read_text(encoding="ascii").splitlines()]
    assert len(rows)==len(outputs)==91
    truth=json.loads(Path(truthfile).read_text(encoding="utf-8"))
    assert len(truth)==90
    per_family={k:[] for k in FAMILIES}
    independent_witnesses=0
    for i,(line,record) in enumerate(zip(rows,outputs)):
        values=line.split(chr(9))
        assert len(values)==2
        ident,ct=values
        assert len(ct)==97 and set(ct)<=set(AZ)
        assert record["id"]==ident and record["n"]==97
        assert len(record["feature_values"])==4 and len(record["feature_upper_tail_p_values"])==4
        assert all(math.isfinite(v) for v in record["feature_values"])
        assert all(0<v<=1 for v in record["feature_upper_tail_p_values"])
        assert record["departure_flag"]==(record["familywise_uniform_null_p"]<=0.01)
        if i==90:
            assert ident=="K4"
            assert len(ct)==97
            k4=record
            continue
        assert ident==f"CASE_{i:03d}"
        t=truth[ident]
        family=t["family"]
        assert family in FAMILIES
        plain=t["plaintext"]
        key=t["full_key"]
        assert independently_encrypt(plain,key)==ct,("invalid 97-letter independent witness",ident)
        if family=="SIMULATED_UNIFORM_PAD":
            assert len(t["details"])==0
        elif family=="PERIODIC_MASK":
            d=t["details"]
            period=d["short_period"]
            shortkey=d["short_key"]
            assert 3<=period<=6 and len(shortkey)==period
            assert key==(shortkey*((97+period-1)//period))[:97]
        else:
            assert t["details"]["key_source"]!=t["book"]
        per_family[family].append(record["familywise_uniform_null_p"])
        independent_witnesses+=1
    assert independent_witnesses==90 and all(len(v)==30 for v in per_family.values())

    report_families={}
    for name,ps in per_family.items():
        report_families[name]={
            "count":len(ps),
            "departure_flags_p_le_0_01":sum(v<=0.01 for v in ps),
            "not_flagged":sum(v>0.01 for v in ps),
            "median_omnibus_p":statistics.median(ps),
            "min_omnibus_p":min(ps),
            "max_omnibus_p":max(ps)
        }
    otp_false=report_families["SIMULATED_UNIFORM_PAD"]["departure_flags_p_le_0_01"]
    periodic_hits=report_families["PERIODIC_MASK"]["departure_flags_p_le_0_01"]
    calibration_ok=otp_false<=2
    period_power_ok=periodic_hits>=20
    p=k4["familywise_uniform_null_p"]
    report={
        "classification":"R59_POST_REMOTE_FREEZE_MASKING_FINGERPRINT_EVALUATION_NO_K4_PLAINTEXT",
        "phase":"controls_plus_K4","status":"COMPLETE",
        "raw_output_sha256":m["output_sha256"],
        "independent_full_forward_witnesses":independent_witnesses,
        "all_forward_witnesses_valid":True,
        "synthetic_family_results":report_families,
        "simulated_uniform_false_positive_target_met":calibration_ok,
        "periodic_mask_power_target_met":period_power_ok,
        "K4":{
            "familywise_uniform_null_p":p,
            "feature_names":k4["feature_names"],
            "feature_values":k4["feature_values"],
            "feature_upper_tail_p_values":k4["feature_upper_tail_p_values"],
            "departure_flag":k4["departure_flag"],
            "interpretation":(
                "Unusual compared with iid uniform under preregistered omnibus test; "
                "does not recover a key or identify a specific mask."
                if p<=0.01 else
                "No statistically significant departure from iid uniform; "
                "cannot infer a true one-time pad or rule out a structured mask."
            )
        },
        "limitations":[
            "Reproducibly generated pseudo-uniform pad controls are NOT operationally secure one-time pads.",
            "Periodic detection power is specific to period 3..6 and 97-letter English sources.",
            "Failure to reject a uniform ciphertext distribution never proves that a true OTP was used.",
            "A book key is deterministic and source-dependent even when its output looks uniform.",
            "No K4 plaintext, key or published-letter fit was generated or used."
        ]
    }
    target=Path(out)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("x",encoding="ascii") as f:
        json.dump(report,f,sort_keys=True,indent=2);f.write(chr(10))
    print("R59 COMPLETE, after REMOTE freeze; all",independent_witnesses,"synthetic forward witnesses valid")
    print("simulated-uniform false flags",otp_false,"/30; periodic mask detection",periodic_hits,"/30")
    print("K4 p",p,"uniform-departure flag",k4["departure_flag"],"period power gate",period_power_ok)

if __name__=="__main__":main()
