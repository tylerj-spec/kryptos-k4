#!/usr/bin/env python3
"""R58 sealed generator. NOT MOUNTED in the ciphertext-only solver environment.

Reads two verifiably pinned US-public-domain English books, then writes 120 shuffled,
opaque 97-letter ciphertext controls and separate secret family/key/plaintext truth.
Independent forward encryption implementation; no imported blind solver.
"""
import hashlib
import json
import math
import random
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N = 97
SEED = 580058
A = "".join(dict.fromkeys("KRYPTOS" + AZ))
INDEX = {ch:i for i,ch in enumerate(A)}
BOOK_BLOBS = {
 "alice": "0f25e9af379233267a09623e0c650472f9e463ea",
 "pride": "20c3737a33af2501e4c0597285ad630ef42e8e46",
}
SPECIAL_KEYS = ("KRYPTOS", "PALIMPSEST", "ABSCISSA")

def read_book(name, path):
    content = Path(path).read_bytes()
    expected = BOOK_BLOBS[name]
    actual = hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + bytes((0,)) + content).hexdigest()
    assert actual == expected, ("public-domain source changed",name,actual)
    text = content.decode("utf-8",errors="replace")
    # Source headers, transcribers and licenses are rejected by keeping only the central 80%.
    body = text[len(text)//10:len(text)*9//10].upper()
    clean = "".join(c for c in body if c in AZ)
    assert len(clean) >= 60*250
    return clean

def texts(alice_path, pride_path):
    rng = random.Random(SEED)
    out = []
    for name, path in (("alice",alice_path),("pride",pride_path)):
        letters = read_book(name,path)
        span = len(letters)//60
        assert span >= 250
        for i in range(60):
            start = i*span + rng.randrange(span-N)
            out.append((letters[start:start+N],name,i))
    assert len(out) == 120 and len({t for t,_,_ in out}) == 120
    rng.shuffle(out)
    return out

def read_keywords(words_path):
    scores=[]
    for line in Path(words_path).open(encoding="utf-8"):
        x=line.split()
        if len(x)<2:continue
        w=x[0]
        if not w.isascii() or not w.isupper() or not w.isalpha() or not 5<=len(w)<=10:continue
        try:v=float(x[1])
        except ValueError:continue
        if math.isfinite(v):scores.append((-v,w))
    scores.sort()
    selected=[];seen=set()
    for _,w in scores:
        if w not in seen:
            seen.add(w);selected.append(w)
        if len(selected)==64:break
    assert len(selected)==64
    return sorted(set(selected).union(SPECIAL_KEYS))

def routes():
    sites=[(0,j) for j in range(27,31)]+[(r,c) for r in (1,2,3) for c in range(31)]
    ids={p:i for i,p in enumerate(sites)}
    out={}
    for col in ("L","R"):
        for row in ("T","B"):
            cs=range(31) if col=="L" else range(30,-1,-1)
            rs=range(4) if row=="T" else range(3,-1,-1)
            out["COL_"+col+row]=tuple(ids[(r,c)] for c in cs for r in rs if (r,c) in ids)
    for start in ("L","R"):
        order=[]
        for r in range(4):
            cells=[z for z in sites if z[0]==r]
            rev=(r%2==1)==(start=="L")
            order += cells[::-1] if rev else cells
        out["SNAKE_"+start]=tuple(ids[z] for z in order)
    assert len(out)==6 and all(sorted(v)==list(range(N)) for v in out.values())
    return out

def substitution(p,key):
    shifts=[INDEX[key[i%len(key)]] for i in range(N)]
    return "".join(A[(INDEX[ch]+shifts[i])%26] for i,ch in enumerate(p))

def route_write(text,permutation):
    return "".join(text[i] for i in permutation)

def hill(p,key):
    a,b,c,d=key
    out=[]
    for i in range(0,96,2):
        x=ord(p[i])-65; y=ord(p[i+1])-65
        out += [chr(65+(a*x+b*y)%26),chr(65+(c*x+d*y)%26)]
    out.append(chr(65+(a*(ord(p[-1])-65)+23*b)%26))
    return "".join(out)

def create(book_a,book_b,words_path,controls_path,truth_path):
    inp=Path(controls_path); secret=Path(truth_path)
    assert inp.resolve()!=secret.resolve()
    rng=random.Random(SEED)
    windows=texts(book_a,book_b)
    keys=read_keywords(words_path)
    perms=routes()
    kinds=["V"]*20+["T"]*20+["VT"]*20+["TV"]*20+["HILL"]*20+["SHUFFLE"]*20
    rng.shuffle(kinds)
    lines=[]
    secret_info={}
    for i,((plain,book,book_bin),family) in enumerate(zip(windows,kinds)):
        key=rng.choice(keys) if family in ("V","VT","TV") else None
        route=rng.choice(sorted(perms)) if family in ("T","VT","TV") else None
        if family=="V": ct=substitution(plain,key)
        elif family=="T":ct=route_write(plain,perms[route])
        elif family=="VT":ct=route_write(substitution(plain,key),perms[route])
        elif family=="TV":ct=substitution(route_write(plain,perms[route]),key)
        elif family=="HILL":
            while True:
                matrix=tuple(rng.randrange(26) for _ in range(4))
                a,b,c,d=matrix
                if math.gcd(a,26)==math.gcd((a*d-b*c)%26,26)==1:break
            ct=hill(plain,matrix)
        else:
            perm=list(range(N));rng.shuffle(perm)
            ct=route_write(plain,perm)
        assert len(ct)==97
        ident=f"CASE_{i:03d}"
        lines.append(ident + chr(9) + ct + chr(10))
        secret_info[ident]={"family":family,"plaintext":plain,"key":key,"route":route,
                            "book":book,"source_bin":book_bin}
        if family=="HILL":secret_info[ident]["matrix"]=matrix
        if family=="SHUFFLE":secret_info[ident]["full_permutation"]=perm
    assert len(secret_info)==120 and all(kinds.count(k)==20 for k in set(kinds))
    for filename in (inp,secret):
        filename.parent.mkdir(parents=True,exist_ok=True)
    with inp.open("x",encoding="ascii") as f:f.write("".join(lines))
    with secret.open("x",encoding="utf-8") as f:
        json.dump(secret_info,f,sort_keys=True,indent=2)
        f.write(chr(10))
    print("R58 sealed controls generated: 120 hidden family+key texts, 20 per group, 2 pinned books")
if __name__=="__main__":
    if len(sys.argv)!=6:
        raise SystemExit("prepare.py ALICE_PUBLIC_DOMAIN.txt PRIDE_PUBLIC_DOMAIN.txt generic_words.tsv INPUT.tsv TRUTH.json")
    create(*sys.argv[1:])
