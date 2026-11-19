#!/usr/bin/env python3
"""Self-contained language model and fixed heldout data for an R85 rotor pilot.
Models train on local Gensim Lee news corpora, not K4 or published clues.
20 gate English messages are disjoint from training (Pang Lee review corpus).
All sources are from installed Gensim test data, hashes recorded.
"""
import hashlib,json,math,re,struct,random,pathlib
P=pathlib.Path('/mnt/data/k4_r85'); base=pathlib.Path('/opt/pyvenv/lib/python3.13/site-packages/gensim/test/test_data');P.mkdir(exist_ok=True)
train_paths=[base/'lee.cor',base/'lee_background.cor']
h=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
train=''.join(re.findall('[a-z]+', '\n'.join(p.read_text(errors='replace') for p in train_paths).lower())).upper()
print('training chars',len(train))
for k in (2,3,4):
 N=26**k;cnt=[0]*N; idx=0; powx=26**(k-1)
 for i,c in enumerate(train):
  v=ord(c)-65
  idx=(idx*26+v)%N
  if i>=k-1:cnt[idx]+=1
 alpha={2:0.5,3:0.1,4:0.02}[k]
 total=sum(cnt)+alpha*N
 values=[math.log((v+alpha)/total) for v in cnt]
 (P/f'gram{k}.bin').write_bytes(struct.pack(f'<{N}f',*values))
 print(k,'counts',sum(v>0 for v in cnt),'model sha256',h(P/f'gram{k}.bin'))
words=[]
for line in (base/'pang_lee_polarity.cor').read_text(errors='replace').splitlines():
  s=re.sub(r'^__label__\w+\s*','',line)
  s=''.join(re.findall('[a-z]+',s.lower())).upper()
  if 97<=len(s)<=900:words.append(s)
print('heldout candidate lines',len(words))
random.Random(8519).shuffle(words)
holdout=words[:30]
# Fixed family with one unknown wiring, AZ contact alphabets, d in +/-1, n in [1..4]
def encrypt(plain, wiring, n, d):
 out=[]
 for i,letter in enumerate(plain):
  sh=(d*(i//n))%26
  x=(ord(letter)-65+sh)%26
  y=(wiring[x]-sh)%26
  out.append(chr(y+65))
 return ''.join(out)
classes=[(n,d) for n in (1,2,3,4) for d in (-1,1)]*2+[(1,1),(2,-1),(3,1),(4,-1)]
random.Random(8519).shuffle(classes)
entries=[]
for i,s in enumerate(holdout):
 r=random.Random(1000003+i*19)
 wiring=list(range(26));r.shuffle(wiring)
 n,d=classes[i] if i<20 else (r.choice([1,2,3,4]),r.choice([-1,1]))
 entries.append({'id':f'G{i+1:02d}','ciphertext':encrypt(s[:97],wiring,n,d), 'truth':s[:97],'wiring':wiring,'n':n,'d':d,'source':'pang_lee_polarity.cor'})
(P/'gate_inputs.tsv').write_text(''.join(x['id']+'\t'+x['ciphertext']+'\n' for x in entries[:20]))
(P/'gate_truth.json').write_text(json.dumps(entries[:20],indent=2))
(P/'dev_inputs.tsv').write_text(''.join(x['id']+'\t'+x['ciphertext']+'\n' for x in entries[20:]))
(P/'dev_truth.json').write_text(json.dumps(entries[20:],indent=2))
# K4 is not placed in any gate files, project solver remains blind to its clues.
(P/'model_manifest.json').write_text(json.dumps({'training':[{'path':str(p),'sha256':h(p)} for p in train_paths], 'heldout_source_sha256':h(base/'pang_lee_polarity.cor'), 'gram_bins':{str(k):h(P/f'gram{k}.bin') for k in (2,3,4)},'generator_sha256':h(pathlib.Path(__file__)),'seed':8519},indent=2))
