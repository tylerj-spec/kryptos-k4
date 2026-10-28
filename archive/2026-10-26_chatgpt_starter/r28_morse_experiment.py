#!/usr/bin/env python3
"""K4 R28: documented Morse characters, limited documented/proxy orders.
No claim these orderings are an authenticated spatial coordinate survey.
No plaintext-fitting; run oracle at 24 anchor letters. Python 3 standard library.
"""
import sys,json,random,csv,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'claude'/'r26'))
from key_oracle import K4,ANCH,possible,checks
from r27_routes import routes,setup
AZ='ABCDEFGHIJKLMNOPQRSTUVWXYZ'; KRY='KRYPTOSABCDEFGHIJLMNQUVWXZ'
# Literal conservative reading reconstructed from the 1999 photos as annotated at
# https://rumkin.com/reference/kryptos/k0/
# Distinct 'E' signals retained. The isolated 1-letter Morse E is a meaningful separator.
PANELS={
 'V':'EEVIRTUALLYEEEEE EEEINVISIBLE',  # see below explicitly corrected: line1 EEVIRTUALLYE; line2 EEEEEINVISIBLE
 'S':'EESHADOWEEFORCESEEEEE',
 'L':'LUCIDEEEMEMORYE',
 'R':'RQ',
 'O':'SOS',
 'D':'EDIGETALEEEINTERPRETATI',
 'P':'TISYOURPOSITIONE',
}
PANELS['V']='EEVIRTUALLYE'+'EEEEEINVISIBLE'
PANELS={k:''.join(c for c in v if c in AZ) for k,v in PANELS.items()}
ORDERS={
 'slab_first_documented':'VSLRODP',    # reference page groups first slab then compass slab
 'compass_slab_first':'DPVSLRO',
 'photographic_page_order':'ORLSPDV',  # order as listed in photo notes, NOT physical traversal
}
# Include separator-less aggregate as sensitivity check only if <97 letters; cyclic repeat explicitly marked.

def create_streams():
 d={}
 for name,order in ORDERS.items():
  s=''.join(PANELS[x] for x in order)
  assert len(s)>=97, (name,len(s))
  d[name]=s
 return d

def fixed_one(k,ct,anchor,pa=None,ca=None,sign=1):
 """Exact necessary and sufficient 24-cr ib condition for one fixed alpha and one arbitrary alpha.
    Numeric coordinate P=PA.index(plaintext char), C=CA.index(cipher char), C=P+k.
 """
 assert (pa is None)!=(ca is None)
 assigned={};rev={}
 for i,p in anchor.items():
  c=ct[i]
  if pa is not None:
   x=(pa.index(p)+sign*k[i])%26
   label=c
  else:
   x=(ca.index(c)-sign*k[i])%26
   label=p
  if label in assigned and assigned[label]!=x:return False
  if x in rev and rev[x]!=label:return False
  assigned[label]=x;rev[x]=label
 return True

def fixed_both(k,ct,anchor,pa,ca):
 return all((pa.index(p)+k[i])%26==ca.index(ct[i]) for i,p in anchor.items())

def transformations(ct,routeidx,order):
 if routeidx is None:return ct,ANCH
 return setup(ct,routes()[routeidx][1],order)

def scan(ct,source,route_indices, include_all_free=False):
 out=[]; counts={};n=0
 for r in route_indices:
  for op in (['identity'] if r is None else ['S_then_T','T_then_S']):
   ci,an= (ct,ANCH) if r is None else transformations(ct,r,op)
   for orientation in ('FWD','REV'):
    s=source if orientation=='FWD' else source[::-1]
    for a in ('AZ','KRY'):
     alpha=AZ if a=='AZ' else KRY
     digits=[alpha.index(c) for c in s]
     for offset in range(len(s)-96):
      key=digits[offset:offset+97]
      configurations=(('PA=AZ,CA=free',AZ,None),('PA=KRY,CA=free',KRY,None),('PA=free,CA=AZ',None,AZ),('PA=free,CA=KRY',None,KRY))
      for m,pa,ca in configurations:
       for sign in (1,-1):
        n+=1
        if fixed_one(key,ci,an,pa,ca,sign):
         row={'source_name':source,'route':'identity' if r is None else routes()[r][0], 'order':op,'reading':orientation,'key_numeration':a,'offset':offset,'model':m,'sign':sign,'n_independent_checks':checks(key,ci,an)}
         out.append(row)
      if include_all_free:
       n+=1
       if possible(key,ct=ci,anch=an):
        out.append({'source_name':source,'route':'identity' if r is None else routes()[r][0], 'order':op,'reading':orientation,'key_numeration':a,'offset':offset,'model':'PA=free,CA=free','sign':1,'n_independent_checks':checks(key,ci,an)})
 return out,n


def positives(seed=282806,n=200):
 rng=random.Random(seed)
 streams=list(create_streams().values());rc=routes()
 for m in range(n):
  s=rng.choice(streams);dir=rng.choice([True,False]);s=s[::-1] if dir else s
  a=rng.choice([AZ,KRY]);off=rng.randrange(len(s)-96)
  k=[a.index(x) for x in s[off:off+97]]
  sign=rng.choice([1,-1])
  pa=rng.choice([AZ,KRY]);ca=list(AZ);rng.shuffle(ca);ca=''.join(ca)
  pt=[rng.choice(AZ) for _ in range(97)]
  for i,p in ANCH.items():pt[i]=p
  r=rng.choice([None,0,1,2,3]);op=rng.choice(['S_then_T','T_then_S']) if r is not None else 'identity'
  if op=='S_then_T':
   inter=''.join(ca[(pa.index(pt[i])+sign*k[i])%26] for i in range(97));ct=''.join(inter[i] for i in rc[r][1]);ci,an=transformations(ct,r,op)
  elif op=='T_then_S':
   t=[pt[i] for i in rc[r][1]];ct=''.join(ca[(pa.index(x)+sign*k[i])%26] for i,x in enumerate(t));ci,an=transformations(ct,r,op)
  else:
   ct=''.join(ca[(pa.index(pt[i])+sign*k[i])%26] for i in range(97));ci,an=ct,ANCH
  assert fixed_one(k,ci,an,pa,None,sign),('positive_failed',m,r,op)
 return n

if __name__=='__main__':
 t=time.time();d=create_streams();out=ROOT/'r28_results';out.mkdir(exist_ok=True)
 print('PANELS', {k:len(v) for k,v in PANELS.items()},'STREAMS', {k:len(v) for k,v in d.items()}, flush=True)
 p=positives();print('POSITIVES',p,flush=True)
 obs=[]
 # R27 earlier 20 route templates; freeze first four (24x8 and 23x8, no search by outcomes)
 route_indices=[None,0,1,2,3]
 for key,stream in d.items():
  rows,n=scan(K4,stream,route_indices,True)
  for row in rows:row['stream_id']=key;row['source_name']=key
  obs.extend(rows)
  print('OBS',key,n,'fits',len(rows),'fixed_one',sum(row['model']!='PA=free,CA=free' for row in rows),flush=True)
 with (out/'r28_morse_passes.csv').open('w',newline='') as f:
  field=['stream_id','source_name','route','order','reading','key_numeration','offset','model','sign','n_independent_checks'];w=csv.DictWriter(f,fieldnames=field);w.writeheader();w.writerows(obs)
 # control on EXACT same families and number of comparisons; shuffled Morse key stream preserves K0 letter counts
 rng=random.Random(280028)
 null=[]
 for iteration in range(80):
  counts=[]
  for name,stream in d.items():
   x=list(stream);rng.shuffle(x);rows,n=scan(K4,''.join(x),route_indices,True)
   counts.append({'one_free':sum(v['model']!='PA=free,CA=free' for v in rows),'two_free':sum(v['model']=='PA=free,CA=free' for v in rows)})
  null.append(counts)
  if (iteration+1)%10==0:print('NULL',iteration+1,counts,'elapsed',round(time.time()-t,1),flush=True)
 sums={}
 for j,key in enumerate(d):
  observed=sum(x['stream_id']==key and x['model']!='PA=free,CA=free' for x in obs)
  controls=[x[j]['one_free'] for x in null]
  obs_two=sum(x['stream_id']==key and x['model']=='PA=free,CA=free' for x in obs)
  controls_two=[x[j]['two_free'] for x in null]
  sums[key]={'len':len(d[key]),'sha256':hashlib.sha256(d[key].encode()).hexdigest(),'obs_one_free':observed,'null_one_free_mean':sum(controls)/len(controls),'null_one_free_ge':sum(x>=observed for x in controls),'null_one_free_p':(sum(x>=observed for x in controls)+1)/(len(controls)+1),'obs_two_free':obs_two,'null_two_free_mean':sum(controls_two)/len(controls_two),'null_two_free_ge':sum(x>=obs_two for x in controls_two),'null_two_free_p':(sum(x>=obs_two for x in controls_two)+1)/(len(controls_two)+1),'null_two_free_max':max(controls_two)}
 result={'protocol':'R28 K0 physical photo transcriptions with uncertain group order; 3 fixed proxy full-stream orders; identity + four frozen 24x8/23x8 routes, both operation orders, forward/reverse, A-Z and KRY numbering; 1 free alphabet or 2 free','panel_strings':PANELS,'streams':d,'summary':sums,'null_counts':null,'positive_controls':p,'n_fits_all':len(obs),'one_free_fits':sum(x['model']!='PA=free,CA=free' for x in obs),'two_free_fits':sum(x['model']=='PA=free,CA=free' for x in obs),'remaining_caveats':['source order is uncertain: tested proxy orderings are not verified compass layout','one-free exact result is limited to tested routes, source transcription and numbered 97 windows','two-free flexible matches do not predict letters outside cribs','slab transcription from photos may include gaps/uncertain Morse marks']}
 (out/'R28_MORSE_TEST.json').write_text(json.dumps(result,indent=2)+'\n')
 print('SUMMARY',json.dumps(sums,indent=2),'total',len(obs),'time',round(time.time()-t,1),flush=True)
