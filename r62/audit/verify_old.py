#!/usr/bin/env python3
"""R62 A: independent original R59/R61 frozen-hash, forward-witness and gate audit.
NO published K4 plaintext letters or offsets. Separate postfreeze checker owns those.
Reads no original K4 unknown plaintext. Checks old frozen outputs, never reruns them.
"""
import hashlib,json,math,statistics,subprocess,sys
from pathlib import Path
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ"
ROOT=Path(__file__).resolve().parents[2]
SPECS=[
 ("R59_PLANTS","r59/holdout/plants_run/FROZEN.sha256","r59/holdout/blind.tsv","r59/holdout/plants_run/RESULTS.jsonl","R59"),
 ("R59_NULLS","r59/holdout/nulls_run/FROZEN.sha256","r59/holdout/nulls.tsv","r59/holdout/nulls_run/RESULTS.jsonl","R59"),
 ("R59_K4","r59/k4/run/FROZEN.sha256","r59/k4/TARGET.tsv","r59/k4/run/RESULTS.jsonl","R59"),
 ("R61_HOLDOUT","r61/holdout/run/FROZEN.sha256","r61/holdout/combined.tsv","r61/holdout/run/RESULTS.jsonl","R61"),
 ("R61_K4","r61/k4/run/FROZEN.sha256","r61/k4/TARGET.tsv","r61/k4/run/RESULTS.jsonl","R61"),
]
FILE_ROLES={
 "solver_source":"r59/blind/rk_solve.cpp","word_model":"k4kit/data/word_model_orth.tsv",
 "routes":"r61/routes.txt"
}
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def encrypt(plain,key,conv,route=None):
    assert len(plain)==len(key)==97
    alpha,formula=conv.split("_")
    letters=AZ if alpha=="AZ" else KRY
    assert len(letters)==26 and sorted(letters)==sorted(AZ)
    d={ch:i for i,ch in enumerate(letters)}
    intermediate="".join(letters[(d[p]+d[k])%26] if formula=="VIG" else
                         letters[(d[k]-d[p])%26] if formula=="BEAU" else
                         letters[(d[p]-d[k])%26] for p,k in zip(plain,key))
    if route is None:return intermediate
    order=PERMS[route]
    return "".join(intermediate[j] for j in order)

PERMS={}
for line in (ROOT/"r61/routes.txt").read_text().splitlines():
    if not line.strip():continue
    name,direction,chars=line.split()
    assert direction=="S_then_T"
    p=[int(x) for x in chars.split(",")]
    assert len(p)==97 and sorted(p)==list(range(97))
    PERMS[name]=p
assert len(PERMS)==10

def subprocess_ok(args):
    return subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True).returncode==0

def git_checks():
    # The freeze commit must CONTAIN the raw results at the designated path.
    chains=[
        ("R59 prereg, holdout, gate","f1848ad","f3f9e3f","e62da2e"),
        ("R59 holdout gate then K4 freeze","e62da2e","c59703c",None),
        ("R61 prereg, holdout, gate","5b51a00","e6b6325","3178f50"),
        ("R61 holdout gate then K4 freeze","3178f50","4276033",None)
    ]
    out=[]
    for desc,a,b,c in chains:
        ab=subprocess_ok(["git","merge-base","--is-ancestor",a,b])
        bc=True if c is None else subprocess_ok(["git","merge-base","--is-ancestor",b,c])
        out.append({"chain":desc,"precedes_freeze":ab,"freeze_precedes_gate":bc})
    for rev,paths in (
      ("f3f9e3f",["r59/holdout/plants_run/RESULTS.jsonl","r59/holdout/nulls_run/RESULTS.jsonl"]),
      ("c59703c",["r59/k4/run/RESULTS.jsonl"]),
      ("e6b6325",["r61/holdout/run/RESULTS.jsonl"]),
      ("4276033",["r61/k4/run/RESULTS.jsonl"])
    ):
        for path in paths:
            found=subprocess_ok(["git","cat-file","-e",f"{rev}:{path}"])
            out.append({"freeze_commit":rev,"path":path,"contained_in_freeze_commit":found})
    for freeze,loc in (("c59703c","r59/k4/REVEAL.json"),("4276033","r61/k4/REVEAL.json")):
        s=subprocess.run(["git","log","--follow","--format=%H","--",loc],
                         cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip().splitlines()
        oldest=s[-1] if s else None
        anc=bool(oldest and subprocess_ok(["git","merge-base","--is-ancestor",freeze,oldest]))
        out.append({"frozen_before_reveal":anc,"freeze":freeze,
                    "original_reveal_commit":oldest,"reveal_file":loc})
    return out

def manifest(spec,model_path,bin_path):
    name,manifest_path,inp,raw,kind=spec
    read=[]
    names={
      "input":inp,"results":raw,"solver_source":"r59/blind/rk_solve.cpp",
      "solver_binary":bin_path,"language_model":model_path,
      "word_model":"k4kit/data/word_model_orth.tsv",
      "runner":"r59/blind/run.py" if kind=="R59" else "r61/blind/run.py",
      "routes":"r61/routes.txt",
      "protocol":"r59/PREREGISTRATION.md" if kind=="R59" else "r61/PREREGISTRATION.md"}
    for l in (ROOT/manifest_path).read_text().splitlines():
        sha,lab,basename=l.split()
        path=names[lab]
        if path is None:
            read.append({"label":lab,"expected_sha256":sha,"status":"UNVERIFIED_NOT_AVAILABLE_IN_GIT"})
        else:
            actual=h(ROOT/path)
            read.append({"label":lab,"expected_sha256":sha,
                         "actual_sha256":actual,"status":"MATCH" if actual==sha else "MISMATCH"})
    assert len(read) in (8,9)
    return {"name":name,"manifest":manifest_path,"entries":read,
            "mismatch_labels":[a["label"] for a in read if a["status"]=="MISMATCH"],
            "unavailable_labels":[a["label"] for a in read if a["status"].startswith("UNVERIFIED")]}

def load(tsv,outputs):
    text=(ROOT/tsv).read_text().splitlines()
    assert text[0]=="id\tciphertext"
    inputs=dict(x.split("\t") for x in text[1:] if x)
    data=[json.loads(x) for x in (ROOT/outputs).read_text().splitlines() if x]
    assert len(data)==len(inputs) and set(inputs)=={x["id"] for x in data}
    return inputs,data

def witnesses(case):
    name,manifestpath,inp,raw,kind=case
    cts,rows=load(inp,raw)
    total=0
    invalid=[]
    for row in rows:
        ct=cts[row["id"]]
        if kind=="R59":
            assert row["best"]==row["per_convention"][0]
            candidates=[row["best"]]+row["per_convention"]+row["top"]
            assert len(candidates)==13
            for c in candidates:
                total+=1
                if len(c["plaintext"])!=97 or len(c["key"])!=97 or encrypt(c["plaintext"],c["key"],c["convention"])!=ct:
                    invalid.append([row["id"],c["convention"]])
        else:
            assert row["best"]==row["stage2"][0]
            assert len(row["stage2"])==2 and len(row["stage1"])==10
            for c in row["stage2"]:
                total+=1
                if len(c["plaintext"])!=97 or len(c["key"])!=97 or encrypt(c["plaintext"],c["key"],c["convention"],c["route"])!=ct:
                    invalid.append([row["id"],c["convention"],c["route"]])
    return {"case":name,"original_rows":len(rows),"complete_fulltext_witnesses_checked":total,
            "failed_witnesses":invalid,"all_valid":not invalid}

def holdout_gates():
    res={}
    for tag,ptpath,ptout,npath,nout,truthpath,oldreport in (
        ("R59","r59/holdout/blind.tsv","r59/holdout/plants_run/RESULTS.jsonl",
          "r59/holdout/nulls.tsv","r59/holdout/nulls_run/RESULTS.jsonl",
          "r59/holdout/sealed_truth.json","r59/holdout/GATE_REPORT.json"),
        ("R61","r61/holdout/blind.tsv","r61/holdout/run/RESULTS.jsonl",
          "r61/holdout/nulls.tsv","r61/holdout/run/RESULTS.jsonl",
          "r61/holdout/sealed_truth.json","r61/holdout/GATE_REPORT.json")
    ):
        _,rows=load(ptpath,ptout) if tag=="R59" else load("r61/holdout/combined.tsv",ptout)
        plants=[x for x in rows if x["id"].startswith("HOLD_")]
        nulls=[x for x in rows if x["id"].startswith("NULL_")]
        if tag=="R59":
            _,nrows=load(npath,nout);nulls=nrows
        original=json.loads((ROOT/oldreport).read_text())
        truth=json.loads((ROOT/truthpath).read_text())
        assert len(plants)==len(nulls)==20
        nvals=sorted(x["best"]["total"] for x in nulls);nmax=max(nvals)
        counts={"detected":0,"convention_ok":0,"pair_correct_ge_60":0}
        if tag=="R61":counts["route_ok"]=0
        pair_correct=[]
        for x in plants:
            b=x["best"];t=truth[x["id"]]
            p=sum({a,c}=={d,e} for a,c,d,e in zip(b["plaintext"],b["key"],t["plaintext"],t["key"]))
            pair_correct.append(p)
            counts["detected"]+=b["total"]>nmax
            counts["pair_correct_ge_60"]+=p>=60
            counts["convention_ok"]+=b["convention"].replace("VARB","BEAU")==t["convention"].replace("VARB","BEAU")
            if tag=="R61":counts["route_ok"]+=b["route"]==t["route"]
        bar={"detected":16,"convention_ok":16,"pair_correct_ge_60":12} if tag=="R59" else {
            "detected":12,"route_ok":12,"convention_ok":14,"pair_correct_ge_60":8}
        passed=all(counts[k]>=v for k,v in bar.items())
        agree=all(counts[k]==original[k] for k in counts)
        agree=agree and original["gate_passed"]==passed and nvals==original["null_totals"]
        agree=agree and abs(nmax-original["null_max_total"])<1e-8
        res[tag]={"recomputed_counts":counts,"recomputed_gate_passed":passed,
                  "original_gate_identical":agree,"recomputed_null_max":nmax,
                  "recomputed_median_pair_correct":sorted(pair_correct)[10]}
        assert res[tag]["recomputed_median_pair_correct"]==original["median_pair_correct"]
    return res

def main():
    if len(sys.argv)!=4:raise SystemExit("verify_old.py REBUILT_MODEL_PATH-or-NONE REBUILT_SOLVER_PATH-or-NONE OUT")
    model,solver,out=sys.argv[1:]
    assert not Path(out).exists()
    model=None if model=="NONE" else model
    solver=None if solver=="NONE" else solver
    checks=git_checks()
    frozen=[manifest(s,model,solver) for s in SPECS]
    witnesses_all=[witnesses(s) for s in SPECS]
    gates=holdout_gates()
    report={"classification":"R62_INDEPENDENT_OLD_R59_R61_NO_PUBLISHED_K4_LETTERS",
            "commit_ancestry_and_freeze_tree":checks,"manifests":frozen,
            "forward_witnesses":witnesses_all,"recomputed_hidden_control_gates":gates,
            "all_historical_freeze_checks_pass":all(
                  x.get("precedes_freeze",True) and x.get("freeze_precedes_gate",True)
                  and x.get("contained_in_freeze_commit",True)
                  and x.get("frozen_before_reveal",True) for x in checks),
            "source_and_frozen_raw_byte_hashes_valid":all(
                  all(entry["status"]=="MATCH" for entry in m["entries"]
                      if entry["label"]!="solver_binary") for m in frozen),
            "historical_solver_binary_byte_identical_to_rebuild":all(
                  next(entry for entry in m["entries"] if entry["label"]=="solver_binary")["status"]=="MATCH"
                  for m in frozen),
            "historical_solver_binary_rebuild_discrepancy":sorted(set(
                  (entry["expected_sha256"],entry.get("actual_sha256"))
                  for m in frozen for entry in m["entries"]
                  if entry["label"]=="solver_binary" and entry["status"]!="MATCH")),
            "all_available_source_roles_verified":all(
                  not s["unavailable_labels"] for s in frozen),
            "all_original_forward_outputs_independently_valid":all(
                  x["all_valid"] for x in witnesses_all),
            "historical_control_gates_recomputed_identically":all(
                  g["original_gate_identical"] for g in gates.values()),
            "limitations":[
               "The rebuilt LM matches its original hash; the rebuilt solver binary does not match the historical compiler-dependent binary SHA. Preserve this discrepancy; original solver binary not committed, compiler flags/version not independently authenticated.",
               "K3 raw plaintext overlaps Carter & Mace 1923 source used in R59 language-model training",
               "No new original K4 candidate or method is generated by this historical audit"
            ]}
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    with Path(out).open("x") as f:json.dump(report,f,indent=2,sort_keys=True);f.write("\n")
    print("R62 audit:",{k:report[k] for k in report if k.startswith(("all_","source_","historical_"))})
    print("Witness counts",[(x["case"],x["complete_fulltext_witnesses_checked"]) for x in witnesses_all])
    if not (report["all_historical_freeze_checks_pass"] and
            report["source_and_frozen_raw_byte_hashes_valid"] and
            report["all_original_forward_outputs_independently_valid"] and
            report["historical_control_gates_recomputed_identically"]):
        raise SystemExit(2)
if __name__=="__main__":main()
