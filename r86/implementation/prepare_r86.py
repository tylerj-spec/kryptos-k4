#!/usr/bin/env python3
"""Generate distinct fresh R86 development, gate, and wrong-family-negative data.
Input corpus independently held out from LM training. Does not read K4.
"""
import pathlib,re,random,json,hashlib
P=pathlib.Path('/mnt/data/k4_r85');source=pathlib.Path('/opt/pyvenv/lib/python3.13/site-packages/gensim/test/test_data/pang_lee_polarity.cor')
raw=[]
for line in source.read_text(errors='replace').splitlines():
 s=re.sub(r'^__label__\w+\s*','',line)
 s=''.join(re.findall('[a-z]+',s.lower())).upper()
 if 97<=len(s)<=900:raw.append(s)
random.Random(8519).shuffle(raw)
assert len(raw)>=81
A='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
def encrypt(p,w,n,d):
 result=[]
 for i,c in enumerate(p):
  v=(A.index(c)+d*(i//n))%26
  result.append(A[(w[v]-d*(i//n))%26])
 return ''.join(result)
classes=[(n,d) for n in (1,2,3,4) for d in (-1,1)]*2+[(1,1),(2,-1),(3,1),(4,-1)]
random.Random(860019).shuffle(classes)
items=[]
for i in range(30,60):
 p=raw[i][:97];r=random.Random(86000031+i*29);w=list(range(26));r.shuffle(w)
 if i<40: n,d=r.choice(classes)
 else: n,d=classes[i-40]
 ct=encrypt(p,w,n,d)
 items.append({'id':f'R86_{i+1:03d}','ciphertext':ct,'truth':p,'wiring':w,'n':n,'d':d})
for start,stop,prefix in [(0,10,'dev86'),(10,30,'gate86')]:
 these=items[start:stop]
 (P/f'{prefix}_input.tsv').write_text(''.join(x['id']+'\t'+x['ciphertext']+'\n' for x in these))
 (P/f'{prefix}_truth.json').write_text(json.dumps(these,indent=2))
# Independent wrong-family controls: 10 Vigenere with long random keys, 10 independent random permutations of another heldout line.
neg=[]
for j in range(20):
 i=60+j;p=raw[i][:97];r=random.Random(860100+j*119)
 if j<10:
  k=[r.randrange(26) for _ in range(11+j)]
  c=''.join(A[(A.index(v)+k[z%len(k)])%26] for z,v in enumerate(p))
  mode='long-key Vigenere'
 else:
  c=''.join(r.sample(p,len(p)))
  mode='shuffled English'
 neg.append({'id':f'NEG86_{j+1:03d}','ciphertext':c,'true_family':mode})
(P/'neg86_input.tsv').write_text(''.join(x['id']+'\t'+x['ciphertext']+'\n' for x in neg))
(P/'neg86_metadata.json').write_text(json.dumps(neg,indent=2))
print('dev SHA',hashlib.sha256((P/'dev86_input.tsv').read_bytes()).hexdigest())
print('gate SHA',hashlib.sha256((P/'gate86_input.tsv').read_bytes()).hexdigest())
print('negative SHA',hashlib.sha256((P/'neg86_input.tsv').read_bytes()).hexdigest())
print('corpus SHA',hashlib.sha256(source.read_bytes()).hexdigest())
