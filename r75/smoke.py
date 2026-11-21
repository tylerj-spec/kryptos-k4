#!/usr/bin/env python3
"""R75 local synthetic-only smoke pilot. NOT a locked cryptanalytic gate.

Uses Python's bundled pydoc topics (technical prose, NOT representative
historical literary English) and a disposable trigram/quadgram scorer. This
script NEVER opens K4 ciphertext, known clues, or repo scorer data.
Run: OPENBLAS_NUM_THREADS=1 python3 -I r75/smoke.py [out.json]
"""
import json, random, sys, hashlib
from pathlib import Path
from collections import Counter
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import reference as R

def norm(s):
    return ''.join(c for c in s.upper() if 'A'<=c<='Z')

def model_train(texts):
    result={}
    for n in (3,4):
        counts=np.zeros(26**n,dtype=np.int64)
        for text in texts:
            a=np.frombuffer(norm(text).encode('ascii'),dtype=np.uint8).astype(np.int16)-65
            if len(a)<n:continue
            codes=a[:len(a)-n+1].astype(np.int64)
            for j in range(1,n):
                codes=26*codes+a[j:len(a)-n+1+j]
            np.add.at(counts,codes,1)
        pseudo=0.03
        result[n]=np.log10((counts+pseudo)/(counts.sum()+pseudo*26**n)).astype(np.float32)
    return result

def scanner_init():
    cfg=list(R.settings())
    assert len(cfg)==2880
    inv=np.empty((len(cfg),40,26),dtype=np.uint8)
    for row,s in enumerate(cfg):
        for pos,m in enumerate(R.maps40(s)):
            for inp,code in enumerate(m):inv[row,pos,code]=inp
    return cfg,inv

def decode(ct,labels,inv,model):
    c=np.frombuffer(ct.encode('ascii'),dtype=np.uint8).astype(np.int16)-65
    pt=inv[:,np.arange(97)%40,c].astype(np.int32)
    score=np.zeros(len(labels),dtype=np.float64)
    for n,w in ((3,.32),(4,.68)):
        x=pt[:,:98-n].copy()
        for j in range(1,n):x=26*x+pt[:,j:98-n+j]
        score+=w*model[n][x].mean(axis=1)
    best=int(np.argmax(score))
    return {'setting_index':best,'plaintext':''.join(R.AZ[x] for x in pt[best]),
            'score':float(score[best])}

def examples(texts,labels,num,seed):
    rng=random.Random(seed)
    windows=[]
    for topic,text in texts:
        txt=norm(text)
        for i in range(0,len(txt)-97,127):
            windows.append((topic,txt[i:i+97]))
    rng.shuffle(windows)
    if len(windows)<num:raise ValueError('insufficient technical-prose windows')
    out=[]
    for i,(topic,pt) in enumerate(windows[:num]):
        idx=rng.randrange(len(labels))
        out.append({'id':f'P{i:03}','ct':R.encrypt(pt,labels[idx]),
                    'pt':pt,'setting':idx,'topic':topic})
    return out

def negatives(pos,num,seed):
    rng=random.Random(seed)
    out=[]
    for i in range(num):
        original=pos[i%len(pos)]['pt']
        t=i%4
        if t==0: ct=''.join(rng.choices(R.AZ,k=97))
        elif t==1:
            a=list(original);rng.shuffle(a);ct=''.join(a)
        elif t==2:
            key=''.join(rng.choices(R.AZ,k=7))
            ct=''.join(R.AZ[(ord(ch)-65+ord(key[j%7])-65)%26]
                       for j,ch in enumerate(original))
        else:
            alpha=list(R.AZ);rng.shuffle(alpha)
            sub=dict(zip(R.AZ,alpha))
            ct=''.join(sub[c] for c in original)
        out.append({'id':f'N{i:03}','ct':ct,'type':t})
    return out

def main():
    import pydoc_data.topics as doc
    topics=sorted((k,v) for k,v in doc.topics.items() if len(norm(v))>1500)
    rng=random.Random(750010);rng.shuffle(topics)
    train=topics[:int(.65*len(topics))]
    dev=topics[int(.65*len(topics)):int(.8*len(topics))]
    unseen=topics[int(.8*len(topics)):]
    lm=model_train([v for _,v in train])
    labels,inv=scanner_init()
    development=examples(dev,labels,20,750011)
    dn=negatives(development,40,750012)
    dpos=[decode(v['ct'],labels,inv,lm) for v in development]
    dneg=[decode(v['ct'],labels,inv,lm) for v in dn]
    dmin=min(x['score'] for x in dpos)
    dmax=max(x['score'] for x in dneg)
    cut=(dmin+dmax)/2 if dmin>dmax else None
    hold=examples(unseen,labels,60,750021)
    hn=negatives(hold,120,750022)
    hpos=[decode(v['ct'],labels,inv,lm) for v in hold]
    hneg=[decode(v['ct'],labels,inv,lm) for v in hn]
    result={'purpose':'SMOKE ONLY: not sealed, not historical English',
            'K4_ciphertext_used':False,'K4_plaintext_clues_used':False,
            'model':'pydoc technical-prose trigram+quadgram',
            'python_version':sys.version.split()[0],
            'topic_groups':[len(train),len(dev),len(unseen)],
            'settings':len(labels),'development_min_positive_score':dmin,
            'development_max_negative_score':dmax,'development_cut':cut,
            'unseen_true_count':len(hold),
            'unseen_exact_plaintext_and_setting':sum(x['plaintext']==a['pt'] and x['setting_index']==a['setting'] for a,x in zip(hold,hpos)),
            'unseen_negative_count':len(hn),
            'unseen_false_confident':None if cut is None else sum(x['score']>=cut for x in hneg),
            'unseen_positive_confident':None if cut is None else sum(x['score']>=cut for x in hpos),
            'unseen_min_positive':min(x['score'] for x in hpos),
            'unseen_max_negative':max(x['score'] for x in hneg)}
    print(json.dumps(result,indent=2))
    if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
