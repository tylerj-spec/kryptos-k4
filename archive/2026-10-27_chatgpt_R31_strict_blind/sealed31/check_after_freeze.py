#!/usr/bin/env python3
"""R31 reveal-stage ONLY: checks frozen blind output against K4 known cribs.
This code is never imported by the blind decrypter or its input-preparation step.
"""
import csv,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BLIND=ROOT/'blind31'
AZ='ABCDEFGHIJKLMNOPQRSTUVWXYZ';KRY='KRYPTOSABCDEFGHIJLMNQUVWXZ'
CT='OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR'
CRIBS={**{i+21:c for i,c in enumerate('EASTNORTHEAST')},**{i+63:c for i,c in enumerate('BERLINCLOCK')}}
assert len(CT)==97 and len(CRIBS)==24
FROZEN={Path(x.split()[1]).name:x.split()[0] for x in (BLIND/'FROZEN_BEFORE_CHECK.sha256').read_text().splitlines()}

def key_g5(primer):
    k=[int(c) for c in f'{primer:05d}']
    while len(k)<97:k.append((k[-5]+k[-4])%10)
    return k[:97]

text=(BLIND/'carter_az.txt').read_text()

def encrypted(pt,setting,offset):
    parts=dict(x.split('=',1) for x in setting.split('/') if '=' in x)
    pa=AZ if parts['PA']=='AZ' else KRY; ca=AZ if parts['CA']=='AZ' else KRY;op=parts['OP']
    if setting.startswith('G5/'):
        key=key_g5(int(parts['PRIMER']))
    else:
        s=text if parts['DIR']=='FORWARD' else text[::-1]
        numeric=AZ if parts['KEYNUM']=='AZ' else KRY
        key=[numeric.index(c) for c in s[offset:offset+97]]
    assert len(key)==97
    out=[]
    for ch,k in zip(pt,key):
        p=pa.index(ch)
        rank=(p+k)%26 if op=='VIG' else ((k-p)%26 if op=='BEAU' else (p-k)%26)
        out.append(ca[rank])
    return ''.join(out)

def main():
    summary=[]
    for filename in ('K4_G5_BLIND.tsv','K4_CARTER_BLIND.tsv'):
        f=BLIND/filename
        assert hashlib.sha256(f.read_bytes()).hexdigest()==FROZEN[f.name],'blind output changed after freeze'
        rows=list(csv.DictReader(f.open(),delimiter='\t'))
        for r in rows:
            s=r['plaintext']; assert len(s)==97
            assert encrypted(s,r['setting'],int(r['offset']))==CT,'forward encryption failed'
            r['anchor_matches']=sum(s[i]==v for i,v in CRIBS.items())
            r['east_section']=s[21:34]
            r['berlin_section']=s[63:74]
            r['all24']=r['anchor_matches']==24
        h=sorted(rows,key=lambda x:-x['anchor_matches'])
        summary.append({'family':filename,'settings_in_full_blind_scan':1200000 if 'G5' in filename else 13575744,
          'top100_correct_all24':sum(x['all24'] for x in rows),
          'top100_max_crib_matches':max(x['anchor_matches'] for x in rows),
          'best_quad':{k:rows[0][k] for k in ('score_quad','setting','plaintext','anchor_matches','east_section','berlin_section')},
          'strongest_crib_retrospective':[{k:x[k] for k in ('rank','score_quad','plaintext','anchor_matches','east_section','berlin_section')}for x in h[:5]]})
        (ROOT/'sealed31'/f'{filename}.retrospective.json').write_text(json.dumps(rows,indent=2))
    (ROOT/'sealed31'/'BLIND_CHECK_REPORT.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
