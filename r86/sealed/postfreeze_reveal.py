#!/usr/bin/env python3
"""Post-FREEZE ONLY: uses published K4 plaintext after independent GitHub SHA freeze.
Do not import or call this from any candidate generator. Reads frozen 97-letter
candidates and scores their alignment to public K4 clues; cannot fit keys.
"""
import csv,json,hashlib,pathlib
ROOT=pathlib.Path('/mnt/data/k4_r85')
FROZEN_COMMIT='26dee4e72524f3ad74248a3163bffebb6bb27645'
ROWS=ROOT/'git_frozen/run/RESULTS.tsv'
EXPECTED_SHA='5460f72117b585ec0f35dc07910a2024f26af9521129a55f8116747faca875b5'
assert hashlib.sha256(ROWS.read_bytes()).hexdigest()==EXPECTED_SHA
known={}
for pos,seq in [(22,'EASTNORTHEAST'),(64,'BERLINCLOCK')]:
 for j,c in enumerate(seq):
  assert pos+j not in known
  known[pos+j]=c
assert len(known)==24
candidates=[v for v in csv.DictReader(ROWS.open(),delimiter='\t') if v['ID']=='K4']
assert len(candidates)==6 and all(len(x['PLAINTEXT'])==97 for x in candidates)
results=[]
for x in candidates:
 plain=x['PLAINTEXT']
 wrong=[{'position':p,'expected':c,'observed':plain[p-1]} for p,c in known.items() if plain[p-1]!=c]
 results.append({'rank':int(x['RANK']),'n':int(x['N']),'d':int(x['D']),'raw_score':float(x['SCORE']),'matched_known_24':24-len(wrong),'mismatched_positions':[w['position'] for w in wrong],'frozen_plaintext_sha256':hashlib.sha256(plain.encode()).hexdigest(),'decodes_fully':not wrong})
out={'freeze_git_commit':FROZEN_COMMIT,'frozen_outputs_sha256':EXPECTED_SHA,'mode':'POSTFREEZE_VALIDATION_ONLY','candidate_count':6,'verified_plaintext_positions':24,'best_known_match':max(v['matched_known_24'] for v in results),'any_consistent_with_all_24':any(v['decodes_fully'] for v in results),'results':results,'not_allowed_to_feed_generator':True}
p=ROOT/'POSTFREEZE_REVEAL.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
