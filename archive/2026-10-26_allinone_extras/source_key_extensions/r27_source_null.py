#!/usr/bin/env python3
"""Frozen letter-count preserving source-key nulls and positive controls for R27.
Run with python -I, shares only historical source text literals with r27_sources.
"""
import json, random, sys
from pathlib import Path
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p))
sys.path.insert(0,str(p/'claude'/'r26'))
from r27_sources import SOURCE_TEXT, AZ, KRY, norm
from key_oracle import possible, K4, ANCH
RNG_SEED=270027
N_NULL=80

def cnt_source(s,ct=K4):
    n=hits=0
    for base in (s,s[::-1]):
        for alphabet in (AZ,KRY):
            arr=[alphabet.index(x) for x in base]
            for i in range(len(arr)-96):
                n+=1
                hits+=bool(possible(arr[i:i+97],ct=ct,sign=1))
    return hits,n

def positives():
    rng=random.Random(270028);tested=0
    for name,raw in SOURCE_TEXT.items():
        s=norm(raw)
        for _ in range(60):
            off=rng.randrange(0,len(s)-96)
            alphkey=rng.choice([AZ,KRY])
            key=[alphkey.index(x) for x in s[off:off+97]]
            ap=list(range(26));ac=list(range(26));rng.shuffle(ap);rng.shuffle(ac)
            pt=[rng.randrange(26) for _ in range(97)]
            for i,ch in ANCH.items():pt[i]=ord(ch)-65
            ct=''.join(chr(65+ac[(ap[u]+key[i])%26]) for i,u in enumerate(pt))
            assert possible(key,ct=ct,sign=1)
            assert possible(key,ct=ct,sign=-1)
            tested+=1
    return tested

if __name__=='__main__':
    pos=positives()
    rng=random.Random(RNG_SEED)
    out=[]
    for name,raw in SOURCE_TEXT.items():
        s=norm(raw)
        observed,n=cnt_source(s)
        vals=[]
        for i in range(N_NULL):
            ss=list(s);rng.shuffle(ss)
            v,nn=cnt_source(''.join(ss))
            assert nn==n
            vals.append(v)
        emp=(1+sum(v>=observed for v in vals))/(N_NULL+1)
        out.append(dict(name=name,trials_unique_sign=n,passes_unique_sign=observed,expected_random=round(0.00047*n,2),nulls=N_NULL,mean_shuffled=round(sum(vals)/N_NULL,3),maximum_shuffled=max(vals),n_null_ge=sum(v>=observed for v in vals),p_empirical=round(emp,5),null_counts=vals))
        print(name,'observed',observed,'null_mean',sum(vals)/N_NULL,'range',min(vals),max(vals),'null_ge',sum(v>=observed for v in vals),'p',emp,flush=True)
    output={'seed':RNG_SEED,'null_controls':N_NULL,'positive_controls':pos,'note':'No pooled p-value: source excerpts correlated; signs equivalent; letters shuffled per source preserving counts.','sources':out}
    outpath=p/'results'/'R27_SOURCE_NULLS.json';outpath.write_text(json.dumps(output,indent=2)+'\n')
    print('POSITIVE',pos)
