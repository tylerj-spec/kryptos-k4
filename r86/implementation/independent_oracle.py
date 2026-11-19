#!/usr/bin/env python3
"""Independent standard-library forward checker, separate from C++ rotor solver.
No published K4 letters or positions are used or imported.
"""
import csv,hashlib,json,random,sys,pathlib
P=pathlib.Path(__file__).resolve().parent
A='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
def inverse_wiring(w):
    assert len(w)==26 and set(w)==set(A)
    return ''.join(A[w.index(ch)] for ch in A) # input-to-output mapping

def encipher(plaintext, inverse, n, d):
    forward=inverse_wiring(inverse)
    assert len(plaintext)==97 and 1<=n<=96 and d in (-1,1)
    out=[]
    for pos, symbol in enumerate(plaintext):
        contact=(A.index(symbol)+d*(pos//n))%26
        out.append(A[(A.index(forward[contact])-d*(pos//n))%26])
    return ''.join(out)

def decode(ciphertext, inverse, n, d):
    assert len(ciphertext)==97
    return ''.join(A[(A.index(inverse[(A.index(c)+d*(i//n))%26])-d*(i//n))%26] for i,c in enumerate(ciphertext))

def test_oracle():
    r=random.Random(456123)
    for n in [1,2,3,4,26,27,96]:
        for d in [-1,1]:
            for i in range(20):
                inverse=''.join(r.sample(A,26));p=''.join(r.choices(A,k=97))
                c=encipher(p,inverse,n,d)
                assert decode(c,inverse,n,d)==p
                j=r.randrange(97);p_bad=p[:j]+A[(A.index(p[j])+1)%26]+p[j+1:]
                assert encipher(p_bad,inverse,n,d)!=c
                c_bad=c[:j]+A[(A.index(c[j])+1)%26]+c[j+1:]
                assert decode(c_bad,inverse,n,d)!=p
    return True

def check_records(input_tsv, output_tsv, outfile):
    targets={id:ct for id,ct in csv.reader(open(input_tsv),delimiter='\t')}
    checks=[]
    for row in csv.DictReader(open(output_tsv),delimiter='\t'):
        ct=targets[row['ID']];text=row['PLAINTEXT'];w=row['INVW'];n=int(row['N']);d=int(row['D'])
        ok=(len(text)==97 and set(text)<=set(A) and len(w)==26 and set(w)==set(A) and encipher(text,w,n,d)==ct and decode(ct,w,n,d)==text)
        checks.append({'id':row['ID'],'rank':int(row['RANK']),'ok':ok})
        if not ok:raise AssertionError(f'bad independent witness {row}')
    assert all(len([x for x in checks if x['id']==id])==6 for id in targets)
    o={'oracle_97_random_tests':280,'all_witnesses_valid':all(c['ok'] for c in checks),'witness_count':len(checks),'inputs_sha256':hashlib.sha256(open(input_tsv,'rb').read()).hexdigest(),'outputs_sha256':hashlib.sha256(open(output_tsv,'rb').read()).hexdigest()}
    open(outfile,'w').write(json.dumps(o,indent=2))
    return o
if __name__=='__main__':
    test_oracle();print(check_records(*sys.argv[1:]))
