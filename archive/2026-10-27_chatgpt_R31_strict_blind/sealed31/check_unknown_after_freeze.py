from pathlib import Path
import json,hashlib
from collections import defaultdict
root=Path(__file__).resolve().parents[1];blind=root/'blind31'
p=blind/'UNKNOWN_BLIND_ALL_OUTPUTS.jsonl'
want=(blind/'UNKNOWN_OUTPUT_FROZEN_BEFORE_CHECK.sha256').read_text().split()[0]
assert hashlib.sha256(p.read_bytes()).hexdigest()==want,'output changed after freeze'
rows=[json.loads(line)for line in p.read_text().splitlines()]
byid=defaultdict(list)
for r in rows:byid[r['id']].append(r)
inputs={l.split()[0]:l.split() for l in (blind/'UNKNOWN_BLIND_ALL_INPUTS.txt').read_text().splitlines()}
P={d['id']:d for d in json.loads((root/'sealed31/unknown_plants_ground_truth.json').read_text())}
CRIBS={**{i+21:c for i,c in enumerate('EASTNORTHEAST')},**{i+63:c for i,c in enumerate('BERLINCLOCK')}}
A='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
results=[]
for lab,rs in byid.items():
    t=inputs[lab]; key=[ord(v)-65 for v in t[1]]; cipher=t[2]
    for r in rs:
        plain=r['plaintext'];pa=r['plaintext_alphabet'];ca=r['ciphertext_alphabet']
        assert len(plain)==97 and len(pa)==len(ca)==26
        assert set(pa)==set(ca)==set(A)
        ct=''.join(ca[(pa.index(v)+k)%26]for v,k in zip(plain,key))
        assert ct==cipher,(lab,'re-encryption fails')
    best=max(rs,key=lambda x:x['W'])
    x={'id':lab,'score':best['W'],'plaintext':best['plaintext'],'kind':'PLANTED' if lab in P else 'K4', 'blind_input_mask_all_unknown':t[3]=='?'*97}
    if lab in P:
        x['wrong_letters']=sum(i!=j for i,j in zip(best['plaintext'],P[lab]['true_plaintext']))
        x['readable_within_5']=x['wrong_letters']<=5
    else:
        x['known_anchor_matches_after_freeze']=sum(best['plaintext'][i]==v for i,v in CRIBS.items())
        x['known_east_segment']=best['plaintext'][21:34]
        x['known_berlin_segment']=best['plaintext'][63:74]
    results.append(x)
print(json.dumps(results,indent=2))
(root/'sealed31/UNKNOWN_BLIND_AFTER_CHECK.json').write_text(json.dumps(results,indent=2))
