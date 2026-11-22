#!/usr/bin/env python3
"""R93 exact-checker correctness gate, not blind recovery. Synthetic input only."""
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import random
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference93 as ref
import runner93 as run
import scope93


def cpu():
    parent = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return parent.ru_utime+parent.ru_stime+child.ru_utime+child.ru_stime


def worked_example(binary):
    alphabet="ABCDE"
    text="ABCDEABCD"
    wiring=[2,4,1,0,3]
    ciphertext=ref.encrypt(text,wiring,alphabet,alphabet,5,4,-1)
    assert ciphertext=="CDACBEAEB"
    assert ref.decrypt(ciphertext,wiring,alphabet,alphabet,5,4,-1)==text
    row=run.setting_line(text,ciphertext,list(range(9)),alphabet,alphabet,5,4,-1)
    words, receipt=run.run_records(binary,"--settings",[row])
    assert words==[(1<<10)-1]
    return {"plaintext_indices":[0,1,2,3,4,0,1,2,3],
            "ciphertext_indices":[2,3,0,2,1,4,0,4,1],"receipt":receipt}


def toy_gate(binary, smoke=False):
    lines, expected, strata = [], [], {}
    for q, maximum in ((2,6),(3,5),(4,4)):
        count=0
        for k in range(1, maximum+1):
            for case, values in enumerate(product(range(q*q), repeat=k)):
                if smoke and case>=40:
                    break
                pairs=[divmod(value,q) for value in values]
                exact, omissions=ref.brute_pair_verdict(q,pairs)
                expected.append(omissions | (int(exact)<<k))
                flat=[str(c) for pair in pairs for c in pair]
                lines.append(" ".join([str(q),str(k),*flat]))
                count+=1
        strata[str(q)]={"max_observations":maximum,"cases":count}
    words, receipt=run.run_records(binary,"--pairs",lines)
    assert words==expected, "complete-key oracle disagrees with production verdict"
    if not smoke:
        assert len(words)==141793
    return {"cases":len(words),"strata":strata,"false_exclusions":0,
            "false_feasibilities":0,"omission_mask_disagreements":0,"receipt":receipt}


def boundary_positions(n,phase,rng):
    boundaries=list(range(n-phase,97,n))
    chosen={0,1,95,96}
    for point in {boundaries[0],boundaries[len(boundaries)//2],boundaries[-1]}:
        chosen.update(i for i in (point-1,point,point+1) if 0<=i<97)
    choices=[i for i in range(97) if i not in chosen]
    chosen.update(rng.sample(choices,24-len(chosen)))
    return sorted(chosen)


def change(text, index):
    return text[:index]+run.AZ[(run.AZ.index(text[index])+1)%26]+text[index+1:]


def plant_gate(binary, smoke=False):
    rng=random.Random(930101 if not smoke else 930000)
    lines, required, periods, modes = [], [], Counter(), Counter()
    plants=0
    bulk_boundaries=[]
    ns=(5,96) if smoke else range(5,97)
    for n in ns:
        for phase in (1,n//2,n-1):
            for direction in (-1,1):
                for ia in run.ALPHABETS:
                    for oa in run.ALPHABETS:
                        wiring=list(range(26)); rng.shuffle(wiring)
                        kind=plants%3
                        if kind==0:
                            text="".join(rng.choice(run.AZ) for _ in range(97))
                        elif kind==1:
                            text=("ABACADABRA"*10)[:97]
                        else:
                            text=(run.AZ*4)[:97]
                        ciphertext=ref.encrypt(text,wiring,ia,oa,n,phase,direction)
                        assert ref.decrypt(ciphertext,wiring,ia,oa,n,phase,direction)==text
                        positions=boundary_positions(n,phase,rng)
                        if (n,phase,direction,ia,oa) in (
                            (5,1,-1,run.ALPHABETS[0],run.ALPHABETS[0]),
                            (96,95,1,run.ALPHABETS[3],run.ALPHABETS[3])):
                            label_index=32*sum(k-1 for k in range(5,n))+32*(phase-1)
                            label_index+=16*(direction==1)+4*run.ALPHABETS.index(ia)+run.ALPHABETS.index(oa)
                            bulk_boundaries.append((text,ciphertext,positions,label_index))
                        omission=plants%24
                        index=positions[omission]
                        new_text=change(text,index)
                        reencrypted=ref.encrypt(new_text,wiring,ia,oa,n,phase,direction)
                        assert sum(a!=b for a,b in zip(ciphertext,reencrypted))==1
                        assert ref.decrypt(reencrypted,wiring,ia,oa,n,phase,direction)==new_text
                        outside=next(i for i in range(97) if i not in positions)
                        variants=[(text,ciphertext,1<<24),
                                  (new_text,reencrypted,1<<24),
                                  (new_text,ciphertext,1<<omission),
                                  (text,change(ciphertext,index),1<<omission),
                                  (text,change(ciphertext,outside),1<<24)]
                        for plain,ct,requirement in variants:
                            lines.append(run.setting_line(plain,ct,positions,ia,oa,n,phase,direction))
                            required.append(requirement)
                        plants+=1; periods[str(n)]+=1; modes[str(kind)]+=1
    words,receipt=run.run_records(binary,"--settings",lines)
    assert all(word & need for word,need in zip(words,required)), "plant/error model falsely excluded"
    if not smoke:
        assert plants==8832 and set(periods.values())=={96}
    bulk_receipts=[]
    assert len(bulk_boundaries)==2
    for text,ciphertext,positions,index in bulk_boundaries:
        aggregates,bulk_receipt=run.scan(binary,[("SYNTHETIC_BOUNDARY",ciphertext)],positions,
            "".join(text[p] for p in positions),
            synthetic_required_codes={"SYNTHETIC_BOUNDARY":(index,(1<<25)-1)})
        assert aggregates["SYNTHETIC_BOUNDARY"]["exact_feasible_labels"]>=1
        bulk_receipts.append({"registered_label_index":index,"receipt":bulk_receipt})
    return {"parameter_plants":plants,"setting_checks":len(words),"forward_inverse_roundtrips":plants*2,
            "plaintext_reencrypt_single_position_checks":plants,"wrong_plaintext_dropout_checks":plants,
            "observed_ciphertext_dropout_checks":plants,"outside_observations_exact_checks":plants,
            "false_exclusions":0,"by_period":dict(periods),"text_types":dict(modes),"receipt":receipt,
            "first_and_last_bulk_catalog_plants":bulk_receipts}


def adversarial_gate(binary):
    one=[(0,0),(0,1),(2,2),(3,3)]
    disjoint=[(0,0),(0,1),(2,2),(2,3)]
    records=[]; expected=[]
    for pairs in (one,disjoint):
        exact,mask=ref.brute_pair_verdict(4,pairs)
        expected.append(mask|(int(exact)<<4))
        records.append("4 4 "+" ".join(str(v) for pair in pairs for v in pair))
    words,receipt=run.run_records(binary,"--pairs",records)
    assert words==expected==[3,0]
    high=[(j,j) for j in range(24)]
    high[23]=(22,23)
    separated=list(high);separated[1]=(0,1)
    high_rows=["26 24 "+" ".join(str(v) for pair in pairs for v in pair)
               for pairs in (high,separated)]
    high_words,high_receipt=run.run_records(binary,"--pairs",high_rows)
    assert high_words==[(1<<22)|(1<<23),0]
    rng=random.Random(930103)
    wiring=list(range(26));rng.shuffle(wiring)
    text="".join(rng.choice(run.AZ) for _ in range(97))
    offsets=ref.event_clock(97,5,3,1)
    lost=[v if i<2 else v-1 for i,v in enumerate(offsets)]
    base=ref.encrypt_offsets(text,wiring,run.AZ,run.AZ,offsets)
    corrupted=ref.encrypt_offsets(text,wiring,run.AZ,run.AZ,lost)
    changed=[i for i,(a,b) in enumerate(zip(base,corrupted)) if a!=b]
    assert len(changed)>1 and min(changed)>=2
    return {"one_conflict_valid_deletions":2,"disjoint_conflict_valid_deletions":0,
            "lost_update_changed_positions":len(changed),"lost_update_covered_by_drop":False,
            "receipt":receipt,"high_omission_bit_receipt":high_receipt}


def benchmark(binary, smoke=False):
    rng=random.Random(930102 if not smoke else 930001)
    positions=sorted(rng.sample(range(97),24))
    observations="".join(rng.choice(run.AZ) for _ in positions)
    inputs=[(f"SYNTH_{i}","".join(rng.choice(run.AZ) for _ in range(97)))
            for i in range(1 if smoke else 3)]
    before_cpu,before_wall=cpu(),time.perf_counter()
    reports,receipt=run.scan(binary,inputs,positions,observations)
    elapsed_wall,elapsed_cpu=time.perf_counter()-before_wall,cpu()-before_cpu
    assert all(row["settings"]==145728 for row in reports.values())
    factor=2*201/len(inputs)
    forecast_cpu=factor*elapsed_cpu+10
    forecast_wall=factor*elapsed_wall+10
    assert forecast_cpu<0.8*1200 and forecast_wall<0.8*1800,"registered forecast bar failed"
    return {"inputs":len(inputs),"scope_settings_per_input":145728,
            "wall_seconds":elapsed_wall,"cpu_seconds":elapsed_cpu,
            "forecast_target_wall_seconds":forecast_wall,"forecast_target_cpu_seconds":forecast_cpu,
            "forecast_multiplier":factor,"forecast_startup_seconds":10,
            "aggregate_results":reports,"receipt":receipt}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--binary",type=Path,required=True)
    parser.add_argument("--source-commit")
    parser.add_argument("--smoke",action="store_true")
    args=parser.parse_args()
    report={"gate_type":"EXACT_CHECKER_CORRECTNESS","blind_recovery_certified":False,
            "synthetic_only":True,"source_commit":args.source_commit}
    exit_code=0
    try:
        if args.smoke:
            report["sources"]={p.name:run.sha_file(p) for p in HERE.glob("*.py")}
        else:
            if not args.source_commit:
                raise ValueError("formal validation requires published source commit")
            report["sources"]=run.verify_protocol(HERE.parent,args.source_commit)
        report["build"]=run.build(HERE/"checker93.cpp",args.binary)
        report["scope"]=scope93.account()
        report["worked_example"]=worked_example(args.binary)
        report["toy_oracle"]=toy_gate(args.binary,args.smoke)
        report["boundary_plants"]=plant_gate(args.binary,args.smoke)
        report["adversarial"]=adversarial_gate(args.binary)
        report["benchmark"]=benchmark(args.binary,args.smoke)
        report["status"]="COMPLETE"
        report["gate_verdict"]="DEVELOPMENT_ONLY" if args.smoke else "GO"
    except AssertionError as error:
        report.update(status="COMPLETE",gate_verdict="NO_GO",failure=str(error))
    except Exception as error:
        report.update(status="INCOMPLETE",gate_verdict="INCOMPLETE",failure=type(error).__name__+": "+str(error))
        exit_code=2
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ("status","gate_type","gate_verdict")}))
    raise SystemExit(exit_code)


if __name__=="__main__":
    main()
