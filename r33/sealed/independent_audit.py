#!/usr/bin/env python3
"""Post-freeze INDEPENDENT audit of R32 and R33 result rows.

No imports from blind encrypt/decrypt code. Reads the known clues only after
SHA-256 verification; never modifies or scores any candidate in the search.
"""
from pathlib import Path
import argparse, array, csv, hashlib, json, re

AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
KRY = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'
N=97
CLUES = {**{i+21:c for i,c in enumerate('EASTNORTHEAST')}, **{i+63:c for i,c in enumerate('BERLINCLOCK')}}
assert len(CLUES)==24


def sha_verify(base, filename):
    for line in (base / filename).read_text().splitlines():
        hash_, path = line.split(maxsplit=1)
        got = hashlib.sha256((base / path.strip()).read_bytes()).hexdigest()
        if got != hash_:
            raise ValueError(f'FAIL SHA256 {filename} {path}')


def make_key(fam, spec, carter, k1k3):
    if fam in ('CARTER','K1K3'):
        direction, numbering, offset = spec.split('/')
        source = carter if fam == 'CARTER' else k1k3
        if direction == 'rev':
            source=source[::-1]
        abc=AZ if numbering=='AZ' else KRY
        word=source[int(offset[3:]):int(offset[3:])+N]
        if len(word)!=N:
            raise AssertionError('short source key')
        return [abc.index(ch) for ch in word]
    m = re.fullmatch(r'primer(\d{5,6})',spec)
    if not m:
        raise ValueError(spec)
    digits = [int(c) for c in m.group(1)]
    b = len(digits)
    while len(digits)<N:
        digits.append((digits[-b]+digits[-b+1]) % 10)
    return digits


def independent_encrypt(plain, perm, order, key, pa, ca, op):
    out=[]
    for j in range(N):
        t = j if order=='ID' else perm[j]
        kk = key[j] if order=='T_then_S' else key[t]
        x = pa.index(plain[t])
        q = (x + kk) % 26 if op=='VIG' else (kk - x) % 26 if op=='BEAU' else (x-kk) % 26
        out.append(ca[q])
    return ''.join(out)


def read_routes(file):
    out = {}
    for line in file.read_text().splitlines():
        name,order,ps = line.split()
        p=tuple(map(int,ps.split(',')))
        assert len(p)==N and len(set(p))==N and min(p)==0 and max(p)==N-1
        assert (name,order) not in out
        out[name,order]=p
    return out


def scan_rows(root, tags, routes_for, carter, k1k3, q):
    report={}
    for tag in tags:
        rows=list(csv.DictReader((root / f'{tag}.tsv').open(), delimiter='\t'))
        assert len(rows)==100
        filect = next((root / s for s in ('k4_ciphertext.txt', 'PLANT_G5.txt', 'PLANT_CARTER.txt') if s.startswith('k4') and tag.startswith('K4')), None)
        if not tag.startswith('K4'):
            if root.name=='runs' and (root/'plant_f1_0_ct.txt').exists():
                i=int(tag.rsplit('_',1)[1]); filect=root / f'plant_f{1 if i<6 else 2}_{i}_ct.txt'
            else: filect=root / f'{tag}.txt'
        ct=filect.read_text().strip()
        assert len(ct)==N
        allok=True; scoreok=True; matches=[]
        for row in rows:
            fields=row['setting'].split('|')
            assert len(fields)==7,(tag,fields)
            fam,name,order,spec,pas,cas,ops=fields
            key=make_key(fam,spec,carter,k1k3)
            perm=routes_for(tag)[name,order]
            p=row['plaintext']
            assert len(p)==N and p.isupper() and p.isalpha()
            enc=independent_encrypt(p,perm,order,key, AZ if pas=='PA=AZ' else KRY, AZ if cas=='CA=AZ' else KRY,ops[3:])
            allok &= enc==ct
            iv=[ord(c)-65 for c in p]
            score=sum(q[(((iv[i-3]*26+iv[i-2])*26+iv[i-1])*26+iv[i])] for i in range(3,N))
            scoreok &= abs(score-float(row['score']))<.00001
            matches.append(sum(p[i]==c for i,c in CLUES.items()))
        assert allok and scoreok, (tag,allok,scoreok)
        report[tag]={'rows':len(rows),'independent_forward_ok':allok,'independent_score_ok':scoreok,'max_known_letters_in_saved_rows':max(matches),'number_24':sum(c==24 for c in matches),'top_plaintext':rows[0]['plaintext'],'top_score':float(rows[0]['score'])}
    return report


def main():
    a=argparse.ArgumentParser(); a.add_argument('--r32',type=Path,required=True); a.add_argument('--r33',type=Path,required=True); a.add_argument('--data',type=Path,required=True); opts=a.parse_args()
    r32=opts.r32/'r32'; r33=opts.r33
    sha_verify(r32,'PROTOCOL.sha256')
    sha_verify(r32/'runs','FROZEN.sha256')
    sha_verify(r33,'PROTOCOL.sha256')
    sha_verify(r33/'runs','FROZEN.sha256')
    carter=(r33/'runs/carter_az.txt').read_text().strip()
    k1k3=''.join(c for c in (opts.data/'k1k3_plaintext.txt').read_text() if 'A'<=c<='Z')
    fromarray=array.array('f'); fromarray.frombytes((r33/'data/quad_log10.f32').read_bytes()); assert len(fromarray)==26**4
    old1=read_routes(r32/'runs/routes_f1.txt');old2=read_routes(r32/'runs/routes_f2.txt')
    newg=read_routes(r33/'runs/routes_g5.txt');newc=read_routes(r33/'runs/routes_carter.txt')
    t32=['K4_F1_CARTER','K4_F1_K1K3','K4_F1_G5','K4_F1_C6','K4_F2_G5']
    p32=[f'PLANT_F1_{i}' for i in range(6)]+['PLANT_F2_6']
    rep32=scan_rows(r32/'runs',t32+p32, lambda tag: old2 if tag.endswith('F2_G5') or tag.startswith('PLANT_F2') else old1,carter,k1k3,fromarray)
    t33=['K4_G5','K4_CARTER','PLANT_G5','PLANT_CARTER']
    rep33=scan_rows(r33/'runs',t33, lambda tag: newc if 'CARTER' in tag else newg,carter,k1k3,fromarray)
    # Plant correctness is revealed only after the frozen SHA validation.
    plants32=json.loads((r32/'sealed/plants_truth.json').read_text())
    for info in plants32:
        i=info['plant']; tag=f'PLANT_F{1 if i<6 else 2}_{i}'
        rows=list(csv.DictReader((r32/'runs'/(tag+'.tsv')).open(), delimiter='\t'))
        rep32[tag]['truth_rank']=next((int(row['rank']) for row in rows if row['plaintext']==info['plaintext']),None)
        rep32[tag]['top_is_truth']=rows[0]['plaintext']==info['plaintext']
        assert rep32[tag]['truth_rank']==1,tag
    plants=json.loads((r33/'sealed/TRUTHS_SEALED.json').read_text())
    for p in plants:
        rows=list(csv.DictReader((r33/'runs'/(p['tag']+'.tsv')).open(),delimiter='\t'))
        rep33[p['tag']]['truth_rank']=next((int(r['rank']) for r in rows if r['plaintext']==p['plain']),None)
        rep33[p['tag']]['top_is_truth']=rows[0]['plaintext']==p['plain']
    assert all(rep33[p['tag']]['truth_rank']==1 for p in plants)
    out={'r32':rep32,'r33':rep33,'r32_saved_k4_rows_verified':500,'r32_saved_plants_verified':700,'r33_rows_verified':400,'frozen_sha_verified':True}
    dst=r33/'results/INDEPENDENT_AUDIT.json'
    dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:{z:{s:v for s,v in d.items() if s in ('top_score','max_known_letters_in_saved_rows','number_24','truth_rank','top_is_truth')} for z,d in ob.items()} for k,ob in [('r32',rep32),('r33',rep33)]},indent=2))

if __name__=='__main__':main()
