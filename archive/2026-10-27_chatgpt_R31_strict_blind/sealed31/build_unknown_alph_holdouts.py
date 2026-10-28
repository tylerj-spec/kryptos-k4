from pathlib import Path
import random,json
root=Path(__file__).resolve().parents[1];AZ='ABCDEFGHIJKLMNOPQRSTUVWXYZ';KRY='KRYPTOSABCDEFGHIJLMNQUVWXZ'
src=(root/'blind31/carter_az.txt').read_text()
P=json.loads((root/'sealed31/reference_messages.json').read_text())['calibration'][:8]
rng=random.Random(310031)
def chain(primer):
 k=[int(x)for x in f'{primer:05d}']
 while len(k)<97:k.append((k[-5]+k[-4])%10)
 return k[:97]
rows=[]
for i,p in enumerate(P):
 assert len(p)==97
 if i<4:
  primer=rng.randrange(100000); k=chain(primer);meta={'family':'G5','primer':primer}
 else:
  off=rng.randrange(len(src)-96);dire=rng.randrange(2);num=rng.randrange(2)
  s=src[::-1] if dire else src
  a=KRY if num else AZ
  k=[a.index(x)for x in s[off:off+97]]; meta={'family':'CARTER','offset':off,'reverse':dire,'num':num}
 pa=list(AZ);ca=list(AZ);rng.shuffle(pa);rng.shuffle(ca)
 ct=''.join(ca[(pa.index(x)+kk)%26] for x,kk in zip(p,k))
 label=f'PLANTUNKNOWN_{i:02d}';key=''.join(chr(65+n)for n in k)
 rows.append({'id':label,'true_plaintext':p,'ciphertext':ct,'key':key,'metadata':meta,'pa':''.join(pa),'ca':''.join(ca)})
(root/'sealed31/unknown_plants_ground_truth.json').write_text(json.dumps(rows,indent=2))
with (root/'blind31/unknown_plants_inputs.txt').open('w') as f:
 for x in rows:f.write(f"{x['id']} {x['key']} {x['ciphertext']} {'?'*97} {310031000 + int(x['id'][-2:])} -\n")
print('Wrote',len(rows),'sealed unknown-alphabet plants')
