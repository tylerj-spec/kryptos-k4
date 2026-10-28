#!/usr/bin/env python3
"""Preselected K3-neighborhood route × nonrepeating Gromark sweep.
See protocols/R27_ROUTE_PREREGISTRATION.md. Executes without numpy and with no solver.
"""
import csv,json,random,statistics,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'claude'/'r26'))
from key_oracle import K4, ANCH, possible, checks
N=97
PAIRS=[(24,8),(23,8),(25,8),(24,7),(24,9)]
RNG_SEED=270051
NULL_SAMPLES=20
NULL_PRIMERS=2500

def rotperm(n,w,cw):
 rows=[list(range(i,min(i+w,n))) for i in range(0,n,w)]
 out=[]
 for c in range(w):
  cc=c if cw else w-1-c
  for r in (range(len(rows)-1,-1,-1) if cw else range(len(rows))):
   if cc < len(rows[r]):out.append(rows[r][cc])
 assert sorted(out)==list(range(n))
 return out

def routes():
 out=[];seen=set()
 for w1,w2 in PAIRS:
  for cw in [True,False]:
   p1=rotperm(N,w1,cw);p2=rotperm(N,w2,cw);p=[p1[i] for i in p2]
   inv=[0]*N
   for j,i in enumerate(p):inv[i]=j
   for kind,pp in [('fwd',p),('inv',inv)]:
    t=tuple(pp)
    if t not in seen:
     seen.add(t);out.append((f'R{w1}x{w2}/'+('CW' if cw else 'CCW')+'/'+kind,pp))
 return out

def gkey(pr):
 a=list(map(int,f'{pr:05d}'))
 while len(a)<N:a.append((a[-5]+a[-4])%10)
 return a

def setup(ct,perm,order):
 if order=='S_then_T':
  # External ciphertext CT[j] = intermediate[perm[j]]
  inv=[0]*N
  for j,i in enumerate(perm):inv[i]=j
  return ''.join(ct[inv[i]] for i in range(N)), ANCH
 if order=='T_then_S':
  # Intermediate X[j] = P[perm[j]], and CT[j] substitutes X[j].
  return ct,{j:ANCH[i] for j,i in enumerate(perm) if i in ANCH}
 raise AssertionError(order)

def planted():
 rng=random.Random(RNG_SEED+1);tested=0
 for name,perm in routes():
  for order in ('S_then_T','T_then_S'):
   for _ in range(10):
    pa=list(range(26));ca=list(range(26));rng.shuffle(pa);rng.shuffle(ca)
    k=gkey(rng.randrange(100000))
    p=[rng.randrange(26) for _ in range(N)]
    for i,ch in ANCH.items():p[i]=ord(ch)-65
    if order=='S_then_T':
     intermediate=''.join(chr(65+ca[(pa[p[i]]+k[i])%26]) for i in range(N))
     ct=''.join(intermediate[i] for i in perm)
    else:
     t=[p[i] for i in perm]
     ct=''.join(chr(65+ca[(pa[t[j]]+k[j])%26]) for j in range(N))
    intermediate,anch=setup(ct,perm,order)
    assert possible(k,ct=intermediate,anch=anch)
    # Re-encrypt is deterministic by the exact formula above; inverse exact.
    if order=='S_then_T':assert ''.join(ct[perm.index(i)] for i in range(N))==intermediate
    tested+=1
 return tested

def score_ct(ct,lim,do_catalog):
 counts=[];catalog=[]
 for name,perm in routes():
  for order in ('S_then_T','T_then_S'):
   ci,an=setup(ct,perm,order)
   count=0
   for primer in range(lim):
    k=gkey(primer)
    if possible(k,ct=ci,anch=an):
     count+=1
     if do_catalog:
      catalog.append(dict(route=name,order=order,primer=f'{primer:05d}',checks=checks(k,ct=ci,anch=an)))
   counts.append(dict(route=name,order=order,primers=lim,passing=count))
 return counts,catalog

if __name__=='__main__':
 out=ROOT/'results';out.mkdir(exist_ok=True)
 print('ROUTES',len(routes()),flush=True)
 npos=planted();print('PLANTED',npos,flush=True)
 t=time.time()
 full,cat=score_ct(K4,100000,True)
 print('FULL',sum(x['passing'] for x in full),'TIME',round(time.time()-t,1),flush=True)
 with (out/'R27_ROUTE_PASSES.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['route','order','primer','checks']);w.writeheader();w.writerows(cat)
 sub,_=score_ct(K4,NULL_PRIMERS,False)
 observed=sum(x['passing'] for x in sub)
 rng=random.Random(RNG_SEED);null=[]
 for i in range(NULL_SAMPLES):
  s=list(K4);rng.shuffle(s)
  counts,_=score_ct(''.join(s),NULL_PRIMERS,False)
  n=sum(x['passing'] for x in counts)
  null.append(n)
  print('NULL',i+1,n,flush=True)
 dat={'routes':len(routes()),'orders':2,'primers_full':100000,'planted_positive':npos,'full_total':sum(x['passing'] for x in full),'full_counts':full,'null_primers':NULL_PRIMERS,'observed_subset':observed,'null_counts':null,'p_empirical':(1+sum(v>=observed for v in null))/(1+len(null)),'seed':RNG_SEED,'note':'These counts alone do not imply coherent plaintext; expected hundreds of chance fits across route space.'}
 (out/'R27_ROUTE_RESULTS.json').write_text(json.dumps(dat,indent=2)+'\n')
 print('SUBSET',observed,'NULL',null,'p',dat['p_empirical'],flush=True)
