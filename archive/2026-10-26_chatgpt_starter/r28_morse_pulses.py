#!/usr/bin/env python3
"""R28 K0 dot/dash keystream bounded test (transcription-dependent).
The dot/dash source is RE-ENCODED from the photo-derived plaintext line readings,
not independently measured from the photos. Intercharacter/word gaps omitted.
"""
import sys,random,json,time,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'claude'/'r26'))
from r28_morse_experiment import K4,ANCH,create_streams,AZ,KRY,fixed_one,possible,checks,positives
from r27_routes import routes,setup
M={'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..'}
ROUTE_IDXS=[None,0,1,2,3]
MAPS={'binary01':{'.':0,'-':1},'timing13':{'.':1,'-':3}}
D=create_streams()

def pulse_string(s):return ''.join(M[ch] for ch in s)

def scan(dots,ct=K4,details=False):
 counts={'one_free':0,'two_free':0};passing=[]
 for r in ROUTE_IDXS:
  for order in (['identity'] if r is None else ['S_then_T','T_then_S']):
   ci,an=(ct,ANCH) if r is None else setup(ct,routes()[r][1],order)
   for rev in [False,True]:
    p=dots[::-1] if rev else dots
    for typ,map01 in MAPS.items():
     x=[map01[ch] for ch in p]
     for start in range(len(x)-96):
      k=x[start:start+97]
      for pa,ca,description in [(AZ,None,'PA AZ'),(KRY,None,'PA KRY'),(None,AZ,'CA AZ'),(None,KRY,'CA KRY')]:
       for sign in (1,-1):
        if fixed_one(k,ci,an,pa,ca,sign):
         counts['one_free']+=1
         if details:passing.append((description,r,order,rev,typ,start,sign,checks(k,ci,an)))
      if possible(k,ct=ci,anch=an):
       counts['two_free']+=1
       if details:passing.append(('both free',r,order,rev,typ,start,1,checks(k,ci,an)))
 return counts,passing

def planted(seed=2838,n=200):
 rng=random.Random(seed);pulses=[pulse_string(s) for s in D.values()]
 for ii in range(n):
  source=rng.choice(pulses);source=source if rng.randrange(2) else source[::-1]
  t=rng.choice(list(MAPS.values()));numbers=[t[x] for x in source]
  k=numbers[rng.randrange(len(numbers)-96):];k=k[:97]
  pa=rng.choice([AZ,KRY]);ca=list(AZ);rng.shuffle(ca);ca=''.join(ca)
  sign=rng.choice([1,-1]);plain=[rng.choice(AZ) for _ in range(97)]
  for j,ch in ANCH.items():plain[j]=ch
  r=rng.choice(ROUTE_IDXS);op='identity' if r is None else rng.choice(['S_then_T','T_then_S'])
  if op=='identity':ct=''.join(ca[(pa.index(plain[i])+sign*k[i])%26] for i in range(97));ci,an=ct,ANCH
  elif op=='S_then_T':
   inter=''.join(ca[(pa.index(plain[i])+sign*k[i])%26] for i in range(97));ct=''.join(inter[i] for i in routes()[r][1]);ci,an=setup(ct,routes()[r][1],op)
  else:
   perm=routes()[r][1];ct=''.join(ca[(pa.index(plain[perm[i]])+sign*k[i])%26] for i in range(97));ci,an=setup(ct,perm,op)
  assert fixed_one(k,ci,an,pa,None,sign)
 return n

if __name__=='__main__':
 st=time.time();print('positive',planted(),flush=True)
 observed={};nulls={};fixedseed=282829; rng=random.Random(fixedseed)
 for name,s in D.items():
  dots=pulse_string(s);res,pas=scan(dots,details=True);observed[name]={'morse_len':len(dots),'counts':res,'passing':pas};print('obs',name,'pulse_len',len(dots),'res',res,flush=True)
  controls=[]
  for j in range(40):
   shuffled=list(dots);rng.shuffle(shuffled);r,_=scan(''.join(shuffled));controls.append(r)
  nulls[name]=controls
  for mod in ['one_free','two_free']:
   hits=sum(c[mod]>=res[mod] for c in controls)
   print('null',name,mod,'mean',sum(c[mod] for c in controls)/len(controls),'ge',hits,'p',(hits+1)/(len(controls)+1),flush=True)
 x={'description':'Re-encoded Morse mark stream without gaps; 2 mapping conventions, K0 3 unverified concatenation orders; 97 pulse windows; 4 K3-neighborhood routes plus identity; both orders; +/- signs for one-free; 40 same-inventory mark shuffles per order','observed':observed,'nulls':nulls,'positive':200,'seed':fixedseed,'elapsed_s':round(time.time()-st,2)}
 path=ROOT/'r28_results'/'R28_MORSE_PULSES.json';path.write_text(json.dumps(x,indent=2)+'\n');print('FINAL',x['elapsed_s'],flush=True)
