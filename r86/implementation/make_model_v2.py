#!/usr/bin/env python3
import bz2,html,hashlib,math,re,struct,json,pathlib
P=pathlib.Path('/mnt/data/k4_r85'); base=pathlib.Path('/opt/pyvenv/lib/python3.13/site-packages/gensim/test/test_data'); wiki=base/'enwiki-latest-pages-articles1.xml-p000000010p000030302-shortened.bz2'
paths=[base/'lee.cor',base/'lee_background.cor',wiki]
raw='\n'.join(p.read_text(errors='replace') for p in paths[:-1]); source=bz2.open(wiki,'rt',errors='replace').read()
articles=re.findall(r'<text[^>]*>(.*?)</text>',source,flags=re.S)
texts=[]
for txt in articles:
 txt=html.unescape(txt)
 if txt.lstrip().upper().startswith('#REDIRECT'):continue
 txt=re.sub(r'(?is)<ref\b[^>]*>.*?</ref>',' ',txt)
 txt=re.sub(r'(?is)\{\{.*?\}\}',' ',txt)
 txt=re.sub(r'(?is)\[\[(?:[^\]|]+\|)?([^\]|]+)\]\]',r'\1',txt)
 txt=re.sub(r'(?is)\[[^\s\]]+\s+([^\]]+)\]',r'\1',txt)
 txt=re.sub(r'(?is)<[^>]*>',' ',txt)
 txt=re.sub(r'(?im)^\s*[|!;=\*#].*$', ' ',txt)
 texts.append(txt)
raw+='\n'+'\n'.join(texts)
train=''.join(re.findall('[a-z]+',raw.lower())).upper(); print('wiki articles:',len(articles),'model chars',len(train))
for k in (2,3,4):
 N=26**k;cnt=[0]*N; idx=0
 for i,c in enumerate(train):
  idx=(idx*26+ord(c)-65)%N
  if i>=k-1:cnt[idx]+=1
 alpha={2:1.,3:.5,4:.05}[k]
 total=sum(cnt)+alpha*N
 values=[math.log((v+alpha)/total) for v in cnt]
 (P/f'gram{k}.bin').write_bytes(struct.pack(f'<{N}f',*values))
 print(k, 'seen',sum(v>0 for v in cnt),'sha',hashlib.sha256((P/f'gram{k}.bin').read_bytes()).hexdigest())
model=json.loads((P/'model_manifest.json').read_text());model['training']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths];model['gram_bins']={str(k):hashlib.sha256((P/f'gram{k}.bin').read_bytes()).hexdigest() for k in (2,3,4)};model['training_extractor_sha256']=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
(P/'model_manifest.json').write_text(json.dumps(model,indent=2))
