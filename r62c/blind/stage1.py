#!/usr/bin/env python3
"""R62C blind stage-one-only R61 wrapper, faithfully using frozen R59 solver.
Inputs original K4 ciphertext and shuffled nulls ONLY; no published K4 plaintext.
Saves full 10 routes x (best, per_convention, top-8) 97-letter plaintext/key pairs.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
AZ=set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
N=97
NCASES=321
NSHARDS=12
PARAMS=["30000","2000","1","AZ_VIG,AZ_BEAU,KRY_VIG,KRY_BEAU","0","20000"]
def load_routes(path):
    rows=[]
    for line in Path(path).read_text(encoding="ascii").splitlines():
        if not line.strip():continue
        name,order,indices=line.split()
        assert order=="S_then_T"
        perm=tuple(int(x) for x in indices.split(","))
        assert len(perm)==N and sorted(perm)==list(range(N))
        rows.append((name,perm))
    assert len(rows)==10 and len({r[0] for r in rows})==10
    assert sum(n.startswith("COL_") or n.startswith("SNAKE_") for n,p in rows)==6
    return rows

def route_for(base,shift):
    assert shift in range(21)
    out=[]
    for name,perm in base:
        if name.startswith(("COL_","SNAKE_")):
            changed=tuple((j+shift)%N for j in perm)
        else:
            changed=perm
        assert len(changed)==N and sorted(changed)==list(range(N))
        out.append((name,changed))
    return out

def undo(ciphertext,perm):
    buf=[""]*N
    for dest,source in enumerate(perm):
        buf[source]=ciphertext[dest]
    return "".join(buf)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if len(sys.argv)!=10:
        raise SystemExit("stage1.py ALL_321.tsv SHARD_ID ROUTES SOLVER_BINARY LM WORDMODEL OUT_RAW_JSONL WORKDIR OUT_LOG")
    _,inp,shard,routes,solver,lm,word,out,work,log=sys.argv
    shard=int(shard);assert 0<=shard<NSHARDS
    inp,work,out,log=map(Path,(inp,work,out,log))
    assert not out.exists()
    work.mkdir(parents=True,exist_ok=True)
    assert not (work/"ROUTES_INPUT.tsv").exists() and not (work/"ROUTES_OUTPUT.jsonl").exists()
    allrows=inp.read_text(encoding="ascii").splitlines()
    assert allrows[0]=="id\tciphertext\tshift" and len(allrows)==NCASES+1
    cases=[]
    for j,line in enumerate(allrows[1:]):
        fields=line.split("\t")
        assert len(fields)==3 and fields[0]==f"CASE_{j:03d}"
        name,ct,shift=fields[0],fields[1],int(fields[2])
        assert len(ct)==N and set(ct)<=AZ
        assert shift==(j if j<=20 else 0)
        if j%NSHARDS==shard:cases.append((name,ct,shift))
    base=load_routes(routes)
    prepared=[]
    parts=[]
    for ident,ct,shift in cases:
        perms=route_for(base,shift)
        for ridx,(name,perm) in enumerate(perms):
            tag=f"{ident}__{ridx}"
            prepared.append((ident,ct,shift,ridx,name,perm,tag))
            parts.append(f"{tag}\t{undo(ct,perm)}")
    tsv=work/"ROUTES_INPUT.tsv";data=work/"ROUTES_OUTPUT.jsonl"
    tsv.write_text("id\tciphertext\n"+"\n".join(parts)+"\n",encoding="ascii")
    with log.open("x",encoding="utf-8") as lg:
        run=subprocess.run([str(Path(solver).resolve()),str(Path(lm).resolve()),
                            str(Path(word).resolve()),str(tsv.resolve()),str(data.resolve())]
                           +PARAMS,stdout=lg,stderr=lg,check=False)
    if run.returncode:
        raise RuntimeError(f"unchanged R59 stage1 solver failed, shard {shard}; log={log}; exit={run.returncode}")
    found=[json.loads(l) for l in data.read_text(encoding="ascii").splitlines() if l]
    assert len(found)==len(prepared)==len(cases)*10
    ready={}
    for (ident,ct,shift,idx,name,perm,tag),item in zip(prepared,found):
        assert item["id"]==tag and item["best"]==item["per_convention"][0]
        assert len(item["per_convention"])==4 and len(item["top"])==8
        assert all(len(c["plaintext"])==len(c["key"])==N
                   for c in [item["best"]]+item["per_convention"]+item["top"])
        ready.setdefault(ident,{"id":ident,"ciphertext":ct,"route_shift":shift,
                                "model":"R61_STAGE1_ONLY_30000_NO_POLISH",
                                "routes":[]})["routes"].append({
              "name":name,"permutation":perm,"original_route_index":idx,"solver_record":item})
    assert len(ready)==len(cases)
    with out.open("x",encoding="ascii") as f:
        for ident,ct,shift in cases:
            row=ready[ident]
            assert len(row["routes"])==10
            f.write(json.dumps(row,separators=(",",":"),sort_keys=True)+"\n")
    report={
      "classification":"R62C_CIPHERTEXT_ONLY_STAGE1_SHARD",
      "shard":shard,"cases":len(cases),"full_candidate_pairs":len(cases)*10*13,
      "input_sha256":sha(inp),"routes_sha256":sha(routes),
      "solver_binary_sha256":sha(solver),"lm_sha256":sha(lm),
      "word_model_sha256":sha(word),"solver_params":PARAMS,
      "shard_raw_sha256":sha(out),"source_sha256":sha(__file__),
      "original_K4_published_plaintext_loaded":False
    }
    with out.with_suffix(".manifest.json").open("x",encoding="ascii") as f:
        json.dump(report,f,sort_keys=True,indent=2);f.write("\n")
    print("R62C blind stage1",shard,"cases",len(cases),"full candidate pairs",len(cases)*130,
          "SHA",report["shard_raw_sha256"])
if __name__=="__main__":main()
