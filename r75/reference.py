"""R75 candidate: two DIFFERENT same-alphabet Quagmire-III tableau stages.

No K4 ciphertext or known K4 plaintext in this source.
This is a hypothetical extension, not an established Sanborn construction.
Stage 1 and stage 2 each use a different AZ/KRY alphabet.
"""
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPHABETS = {"AZ": AZ, "KRY": KRY}
KEYS = ("PALIMPSEST", "ABSCISSA")
OPS = {"VIG": (1, 1), "BEAU": (-1, 1), "VARB": (1, -1)}
N = 97
assert len(set(KRY)) == 26

@dataclass(frozen=True)
class Setting:
    a1: str
    a2: str
    k1: str
    k2: str
    phase1: int
    phase2: int
    op1: str
    op2: str

def settings():
    for alphas in (("AZ","KRY"),("KRY","AZ")):
        for keys in (KEYS, KEYS[::-1]):
            for p1 in range(len(keys[0])):
                for p2 in range(len(keys[1])):
                    for ops in product(OPS, repeat=2):
                        yield Setting(*alphas, *keys, p1, p2, *ops)

def stage(x, keyword, phase, op, alphabet):
    idx = {ch:i for i,ch in enumerate(alphabet)}
    s,t = OPS[op]
    return "".join(alphabet[(s*idx[ch]+t*idx[keyword[(i+phase)%len(keyword)]])%26]
                   for i,ch in enumerate(x))

def unstage(x, keyword, phase, op, alphabet):
    idx = {ch:i for i,ch in enumerate(alphabet)}
    s,t = OPS[op]
    return "".join(alphabet[(s*(idx[ch]-t*idx[keyword[(i+phase)%len(keyword)]]))%26]
                   for i,ch in enumerate(x))

def encrypt(pt, setting):
    return stage(stage(pt,setting.k1,setting.phase1,setting.op1,ALPHABETS[setting.a1]),
                 setting.k2,setting.phase2,setting.op2,ALPHABETS[setting.a2])

def decrypt(ct, setting):
    return unstage(unstage(ct,setting.k2,setting.phase2,setting.op2,ALPHABETS[setting.a2]),
                   setting.k1,setting.phase1,setting.op1,ALPHABETS[setting.a1])

@lru_cache(maxsize=4096)
def maps40(s):
    # One 26-letter substitution permutation at each of the 40 phases.
    result = []
    idx1 = {ch:i for i,ch in enumerate(ALPHABETS[s.a1])}
    idx2 = {ch:i for i,ch in enumerate(ALPHABETS[s.a2])}
    A1, A2 = ALPHABETS[s.a1], ALPHABETS[s.a2]
    sa,ta = OPS[s.op1]
    sb,tb = OPS[s.op2]
    for i in range(40):
        kv1=idx1[s.k1[(i+s.phase1)%len(s.k1)]]
        kv2=idx2[s.k2[(i+s.phase2)%len(s.k2)]]
        row=[]
        for p in AZ:
            x=A1[(sa*idx1[p]+ta*kv1)%26]
            c=A2[(sb*idx2[x]+tb*kv2)%26]
            row.append(AZ.index(c))
        result.append(bytes(row))
    return tuple(result)

def period40(m):
    return next(i for i in (1,2,4,5,8,10,20,40)
                if all(m[j]==m[j%i] for j in range(40)))

def single_stage_maps(alphabet_names=("AZ","KRY")):
    # Exhaustively enumerate all 26 shifts for fixed PA/CA combinations.
    found={}
    for pa in alphabet_names:
        for ca in alphabet_names:
            P,C=ALPHABETS[pa],ALPHABETS[ca]
            idx={ch:i for i,ch in enumerate(P)}
            for op,(sgn,t) in OPS.items():
                for k in range(26):
                    m=bytes(AZ.index(C[(sgn*idx[x]+t*k)%26]) for x in AZ)
                    found.setdefault(m,[]).append((pa,ca,op,k))
    return found

def class_catalog():
    unique={}
    for s in settings():
        unique.setdefault(maps40(s),[]).append(s)
    return unique

if __name__ == "__main__":
    from collections import Counter
    classes=class_catalog()
    print({"raw":len(list(settings())),"unique":len(classes),
           "periods":dict(Counter(period40(x) for x in classes))})
