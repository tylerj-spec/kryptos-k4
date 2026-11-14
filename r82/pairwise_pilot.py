#!/usr/bin/env python3
"""R82 candidate pairwise-factor solver: SYNTHETIC ONLY, no K4 inputs.

Demonstrates that a one-key two-stage tableau cipher yields a discrete
pairwise Markov random field of key letters. Uses deliberately simplified,
INDEPENDENT English letter-frequency controls (NOT natural English).
No published K4 plaintext, K4 ciphertext, R81a targets, or secret keys
are imported. This is an engineering pilot, not an R80/R82 holdout gate.

Run: python3 -m pip install numpy
     python3 -I r82/pairwise_pilot.py
"""
from pathlib import Path
import json
import time
import numpy as np

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "".join(dict.fromkeys("KRYPTOS" + AZ))
FREQ = np.array([8.2,1.5,2.8,4.3,12.7,2.2,2.0,6.1,7.0,.15,.77,4.0,2.4,6.7,7.5,1.9,.095,6.0,6.3,9.1,2.8,.98,2.4,.15,2.0,.074],float)
FREQ /= FREQ.sum()
LOG_F = np.log(FREQ)
RNG = np.random.default_rng(8223)

# C=AZ[(IDX[AZ][KRY[(P+key[r])%26]]+key[s])%26].
# DECODE[c, a, b] = (KRY.index(AZ[(c-b)%26])-a)%26.
DECODE = np.zeros((26,26,26), np.uint8)
for c in range(26):
    for a in range(26):
        for b in range(26):
            DECODE[c,a,b] = (KRY.index(AZ[(c-b)%26])-a)%26


def sample(m, w, n=97):
    p = RNG.choice(26, n, p=FREQ)
    key = RNG.integers(26, size=m)
    cipher = np.array([
        (AZ.index(KRY[(int(p[i])+int(key[i%m]))%26]) +
         int(key[(i+i//w)%m])) % 26 for i in range(n)], int)
    return p,key,cipher


def factors(cipher, m, w):
    """Pairwise potential log P(C|key) with iid English source.

    For position i, only key letters r=i%m and
    s=(i+floor(i/w))%m matter. Hence factor graph has at most
    m variables of 26 values each, not two independent key arrays.
    """
    unary = np.zeros((m,26),float)
    edges = {}
    for i,c in enumerate(cipher):
        r, s = i%m, (i+i//w)%m
        mat = LOG_F[DECODE[int(c)]]
        if r == s:
            unary[r] += np.diag(mat)
        else:
            if r < s:
                pair,table = (r,s),mat
            else:
                pair,table = (s,r),mat.T
            if pair not in edges:
                edges[pair] = np.zeros((26,26),float)
            edges[pair] += table
    return unary, edges


def objective(unary, edges, key):
    return float(sum(unary[i,int(key[i])] for i in range(len(key))) +
                 sum(mat[int(key[i]),int(key[j])]
                     for (i,j),mat in edges.items()))


def solve(unary, edges, restarts=12, steps=100):
    """Anneal one key-variable at a time; local exact key-factor updates.

    This is a simple baseline, not an optimal inference algorithm.
    """
    m=len(unary)
    graph=[[] for _ in range(m)]
    for (i,j),mat in edges.items():
        graph[i].append((j,mat,True))
        graph[j].append((i,mat,False))
    best=-float("inf"); bestkey=None
    for _ in range(restarts):
        key=RNG.integers(26,size=m)
        for t in range(steps):
            r=int(RNG.integers(m))
            scores=unary[r].copy()
            for j,mat,first in graph[r]:
                scores+=(mat[:,int(key[j])] if first else mat[int(key[j]),:])
            temp=1.7*(1-t/steps)**1.4+.06
            scores=scores/temp
            scores-=max(scores)
            prob=np.exp(scores);prob/=sum(prob)
            key[r]=int(RNG.choice(26,p=prob))
        for _ in range(7):
            changed=False
            for r in RNG.permutation(m):
                scores=unary[r].copy()
                for j,mat,first in graph[r]:
                    scores+=(mat[:,int(key[j])] if first else mat[int(key[j]),:])
                new=int(scores.argmax())
                changed=changed or new!=key[r]
                key[r]=new
            if not changed:break
        val=objective(unary,edges,key)
        if val>best:
            best,bestkey=val,key.copy()
    return bestkey,best


def run():
    results=[]
    for m,w in [(4,4),(5,5),(7,7),(9,9),(9,11),(9,31),(5,31),(12,31)]:
        keys=0; rights=[]; truth_ge=0
        for _ in range(16):
            pt,truth,ct=sample(m,w)
            unary,edges=factors(ct,m,w)
            guess,score=solve(unary,edges)
            recovered=np.array([
                DECODE[int(ct[i]),int(guess[i%m]),
                       int(guess[(i+i//w)%m])] for i in range(len(ct))])
            assert len(recovered)==97
            rights.append(int((recovered==pt).sum()))
            keys+=int(np.array_equal(guess,truth))
            truth_ge+=int(objective(unary,edges,truth)>=score-1e-4)
        results.append(dict(m=m,w=w,plants=16,exact_key=keys,
                            exact_full_plaintext=sum(x==97 for x in rights),
                            mean_plaintext_letters=sum(rights)/len(rights),
                            min_plaintext_letters=min(rights),
                            true_iid_unigram_score_ge_solver=truth_ge))
    return {"label":"R82 exploratory simulated i.i.d. English letters only: NOT a natural-language blind gate",
            "seed":8223,"n":97,"model":"two tableau stages, one shared unknown key, rotated stage-2 slot",
            "alphabets":"AZ->KRY then AZ->AZ", "solver":"12 annealing restarts, 100 moves each + local optimization",
            "results":results}


if __name__=="__main__":
    report=run()
    print(json.dumps(report,indent=2))
