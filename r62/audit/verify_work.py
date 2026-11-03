#!/usr/bin/env python3
"""R62A+ independent full R59 shard and R61 stage1/stage2 WORK-file witnesses.
Independent encryption from scratch, never imports R59/R61 enc/solvers.
No original K4 plaintext words/positions; runs against all OLD frozen work.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
N=97
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ"

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def enc_simple(p,k,convention):
    assert len(p)==len(k)==N
    name,method=convention.split("_")
    alpha=AZ if name=="AZ" else KRY
    index={c:i for i,c in enumerate(alpha)}
    out=[]
    for x,y in zip(p,k):
        i,j=index[x],index[y]
        if method=="VIG":value=(i+j)%26
        elif method=="BEAU":value=(j-i)%26
        else:raise ValueError(convention)
        out.append(alpha[value])
    return "".join(out)

def original_routes():
    d=[]
    for line in (ROOT/"r61/routes.txt").read_text().splitlines():
        if not line.strip():continue
        name,order,chars=line.split()
        assert order=="S_then_T"
        p=tuple(int(q) for q in chars.split(","))
        assert len(p)==97 and sorted(p)==list(range(N))
        d.append((name,p))
    assert len(d)==10
    return d

def reverse(original,perm):
    out=[""]*N
    for i,j in enumerate(perm):out[j]=original[i]
    return "".join(out)

def source_frozen(commit,prefix,expected):
    z=subprocess.run(["git","ls-tree","-r","--name-only",commit,prefix],
                     cwd=ROOT,capture_output=True,text=True,check=True)
    listed=set(z.stdout.splitlines())
    assert listed==set(expected),(prefix,"work files differ from freeze commit",len(listed),len(expected))
    return len(listed)

def old_input(path):
    txt=(ROOT/path).read_text().splitlines()
    assert txt[0]=="id\tciphertext"
    rows=dict(s.split("\t") for s in txt[1:])
    assert len(rows)==len(txt)-1
    return rows

def check_candidate(candidate,ct):
    p,k=candidate["plaintext"],candidate["key"]
    assert len(p)==len(k)==N and set(p)<=set(AZ) and set(k)<=set(AZ)
    assert enc_simple(p,k,candidate["convention"])==ct
    return 1

def case_records_from_work(dir_path):
    directory=ROOT/dir_path
    files=list(directory.glob("*.result.json"))
    assert files
    return sorted(files)

def audit_r61(workdir,input_tsv,results,freeze_commit):
    root=ROOT/workdir
    inputs=old_input(input_tsv)
    master={json.loads(l)["id"]:json.loads(l) for l in (ROOT/results).read_text().splitlines() if l}
    assert len(master)==len(inputs)
    routes=original_routes()
    names=[x[0] for x in routes]
    cases=case_records_from_work(workdir)
    assert len(cases)==len(inputs)
    full=0
    meta=[]
    r1=0;r2=0
    original_results=0
    for file in cases:
        name=file.name.split(".result.json")[0]
        assert name in inputs and name in master
        obj=json.loads(file.read_text())
        assert obj["id"]==name and obj["ct"]==inputs[name]
        assert obj["result"]==master[name]
        original_results+=1
        for part in ("s1","s2"):
            tsv=root/f"{name}.{part}.tsv"
            raw=root/f"{name}.{part}.jsonl"
            assert tsv.is_file() and raw.is_file()
            ins={}
            for row in tsv.read_text().splitlines():
                tag,ct=row.split("\t")
                assert tag not in ins and len(ct)==97
                ins[tag]=ct
            rows=[json.loads(t) for t in raw.read_text().splitlines() if t]
            expected=10 if part=="s1" else 2
            assert len(ins)==len(rows)==expected
            if part=="s1":r1+=len(rows)
            else:r2+=len(rows)
            for record in rows:
                tag=record["id"]
                assert tag in ins
                assert tag.startswith(f"{name}__")
                idx=int(tag.rsplit("__",1)[1])
                assert 0<=idx<10
                route,perm=routes[idx]
                target=reverse(inputs[name],perm)
                assert target==ins[tag],("stage route ciphertext mismatch",tag)
                assert record["best"]==record["per_convention"][0]
                assert len(record["per_convention"])==4 and len(record["top"])==8
                for c in [record["best"]]+record["per_convention"]+record["top"]:
                    full+=check_candidate(c,target)
                    z=enc_simple(c["plaintext"],c["key"],c["convention"])
                    assert "".join(z[j] for j in perm)==inputs[name],("stage reencrypt original failed",tag)
                if part=="s1":
                    selected=next(x for x in master[name]["stage1"] if x["route"]==route)
                    assert selected["convention"]==record["best"]["convention"]
                    assert selected["total"]==record["best"]["total"]
                else:
                    selected=next(x for x in master[name]["stage2"] if x["route"]==route)
                    assert selected["convention"]==record["best"]["convention"]
                    assert selected["total"]==record["best"]["total"]
                    assert selected["plaintext"]==record["best"]["plaintext"]
                    assert selected["key"]==record["best"]["key"]
        meta.append(name)
    # All old work files (including logs and source ciphertexts) were present at historic frozen commit.
    expected_files=[str(x.relative_to(ROOT)) for x in root.iterdir() if x.is_file()]
    assert len(expected_files)==len(cases)*7
    tree_items=source_frozen(freeze_commit,workdir,expected_files)
    assert r1==len(cases)*10 and r2==len(cases)*2 and full==(r1+r2)*13
    return {"cases":len(cases),"original_results_exact":original_results,
            "full_stage1_records":r1,"full_stage2_records":r2,
            "independent_full_forward_witnesses":full,
            "all_97_letter_input_routes_invert_exactly":True,
            "all_original_case_ciphertexts_reencrypt_exactly":True,
            "old_freeze_tree_contains_all_work_files":True,
            "old_freeze_work_files_count":tree_items,
            "old_work_dir":workdir}

def audit_r59_log_shards(base,input_path,results,freeze_commit):
    prefix=ROOT/base
    original_rows=[json.loads(l) for l in (ROOT/results).read_text().splitlines()]
    ref={x["id"]:x for x in original_rows}
    inputs=old_input(input_path)
    assert len(ref)==len(inputs)
    shards=sorted((prefix/"logs").glob("shard_*.jsonl"))
    assert len(shards)==4
    seen=set()
    full=0
    for path in shards:
        for line in path.read_text().splitlines():
            if not line.strip():continue
            row=json.loads(line)
            ident=row["id"]
            assert ident in ref and ident not in seen and row==ref[ident]
            seen.add(ident)
            assert len(row["per_convention"])==4 and len(row["top"])==8
            for c in [row["best"]]+row["per_convention"]+row["top"]:
                full+=check_candidate(c,inputs[ident])
    assert seen==set(ref) and full==len(ref)*13
    # Prove raw work logs were present in actual original freeze commit.
    logs=list((prefix/"logs").iterdir())
    tree=source_frozen(freeze_commit,base+"/logs",[str(p.relative_to(ROOT)) for p in logs if p.is_file()])
    return {"prefix":base,"original_rows":len(ref),
            "duplicate_raw_work_witnesses_verified":full,
            "shard_logs_original_freeze_tree_count":tree,"all_shard_json_identical_to_master":True}

def main():
    if len(sys.argv)!=2:raise SystemExit("verify_work.py OUTPUT.json")
    out=Path(sys.argv[1]);assert not out.exists()
    a=audit_r61("r61/holdout/run/work","r61/holdout/combined.tsv",
                 "r61/holdout/run/RESULTS.jsonl","e6b6325")
    b=audit_r61("r61/k4/run/work","r61/k4/TARGET.tsv",
                 "r61/k4/run/RESULTS.jsonl","4276033")
    r59=[
       audit_r59_log_shards("r59/holdout/plants_run","r59/holdout/blind.tsv",
          "r59/holdout/plants_run/RESULTS.jsonl","f3f9e3f"),
       audit_r59_log_shards("r59/holdout/nulls_run","r59/holdout/nulls.tsv",
          "r59/holdout/nulls_run/RESULTS.jsonl","f3f9e3f"),
       audit_r59_log_shards("r59/k4/run","r59/k4/TARGET.tsv",
          "r59/k4/run/RESULTS.jsonl","c59703c")
    ]
    result={
      "classification":"R62_HISTORICAL_ALL_STAGE_WORK_FILES_INDEPENDENT_FORWARD_REENCRYPTION",
      "status":"PASS",
      "R61_HOLDOUT":a,"R61_K4_AND_100_NULLS":b,
      "R59_DUPLICATE_RAW_LOG_SHARDS":r59,
      "independent_R61_complete_stage1_stage2_forward_witnesses":a["independent_full_forward_witnesses"]+b["independent_full_forward_witnesses"],
      "independent_R59_duplicate_raw_shard_witnesses":sum(x["duplicate_raw_work_witnesses_verified"] for x in r59),
      "original_K4_new_solver_run":False,
      "published_K4_plaintext_read":False,
      "all_frozen_sources_present_in_historical_freeze_trees":True,
      "limits":[
         "Same frozen outputs recur in multiple stage and summary files; witness counts are not unique candidate plaintexts",
         "A valid re-encryption witness confirms arithmetic, not a K4 key or cipher-family recovery",
         "K3 contains training text from Howard Carter and A. C. Mace's 1923 account",
         "This expands prior 2115 summary-level witness audit to the complete intermediate work-file outputs"
      ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x") as f:json.dump(result,f,sort_keys=True,indent=2);f.write("\n")
    print("R62 all old work audited",
          result["independent_R61_complete_stage1_stage2_forward_witnesses"],
          "R61 stage witnesses and",
          result["independent_R59_duplicate_raw_shard_witnesses"],
          "R59 raw shard duplicates; all match")
if __name__=="__main__":main()
