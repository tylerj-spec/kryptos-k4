#!/usr/bin/env python3
"""R62 PREDECLARED sealed 40+40 Sanborn-style text power benchmark.
Generator, plaintext, source offsets, keys and truth are NEVER mounted with the R59 solver.
No original K4 ciphertext or published K4 plaintext letters/positions are used.
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
N = 97
OZ_BLOB = "4d978dfeb6b30ead21f73beca1eb51d8cb9686cc"
OZ_COMMIT = "d19a4315b7c6f4471de8840a1a81609b34841dff"

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def git_blob_id(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def clean(t):
    return "".join(x for x in t.upper() if x in AZ)

def load_oz(path):
    b = Path(path).read_bytes()
    assert git_blob_id(b) == OZ_BLOB, "Pinned independent key book changed"
    raw = b.decode("utf-8", "replace")
    a = re.search(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*\*\*\*", raw, re.I)
    z = re.search(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*\*\*\*", raw, re.I)
    assert a and z and a.end() < z.start()
    body = clean(raw[a.end():z.start()])
    assert len(body) > 10000
    return body

def encrypt(plain, key, convention):
    alph, kind = convention.split("_")
    chars = AZ if alph == "AZ" else KRY
    idx = {c:i for i,c in enumerate(chars)}
    if kind == "VIG": return "".join(chars[(idx[p]+idx[k]) % 26] for p,k in zip(plain,key))
    if kind == "BEAU": return "".join(chars[(idx[k]-idx[p]) % 26] for p,k in zip(plain,key))
    raise ValueError(convention)

def make(k1_path,modern_path,oz_path,input_path,truth_path,provenance_path):
    inp, secret, prov = map(Path,(input_path,truth_path,provenance_path))
    for f in (inp,secret,prov):
        assert not f.exists() and all(f.resolve()!=t.resolve() for t in (inp,secret,prov) if f!=t)
        f.parent.mkdir(parents=True,exist_ok=True)
    s=Path(k1_path).read_text().strip()
    assert len(s)>=769 and set(s)<=set(AZ)
    texts=[]
    for name,section,count in (("K1_K2",s[:433],12),("K3_FIRST_ONLY",s[433:769],8)):
        offsets=[j*(len(section)-N)//(count-1) for j in range(count)]
        assert len(set(offsets))==count
        for ix,o in enumerate(offsets):
            texts.append({"cohort":"SANBORN","subgroup":name,"sub_index":ix,
                          "source_offset":o+(433 if name=="K3_FIRST_ONLY" else 0),
                          "plaintext":section[o:o+N]})
    lines=[l.strip() for l in Path(modern_path).read_text().splitlines()
           if l.strip() and not l.lstrip().startswith("#")]
    assert len(lines)==20
    for j,line in enumerate(lines):
        t=clean(line)
        assert len(t)>=N
        texts.append({"cohort":"MODERN","subgroup":"MODERN_UNIQUE","sub_index":j,
                      "source_offset":0,"plaintext":t[:N]})
    assert len(texts)==40 and all(len(x["plaintext"])==97 for x in texts)
    assert len({x["plaintext"] for x in texts})==40
    book=load_oz(oz_path)
    randkey=random.Random(620621)
    width=len(book)//40
    assert width>97
    keys=[]
    for i in range(40):
        ko=i*width+randkey.randrange(width-N)
        keys.append((ko,book[ko:ko+N]))
    assert len({k for _,k in keys})==40
    rng=random.Random(620622)
    rng.shuffle(texts)
    conventions=("AZ_VIG","AZ_BEAU","KRY_VIG","KRY_BEAU")
    plants=[]
    for ix,row in enumerate(texts):
        off,key=keys[ix]
        convention=rng.choice(conventions)
        ct=encrypt(row["plaintext"],key,convention)
        assert len(ct)==N and set(ct)<=set(AZ)
        plants.append({**row,"source_index":ix,"key_offset":off,"key":key,
                       "convention":convention,"ciphertext":ct,"role":"plant",
                       "plant_slot":ix})
    allrows=plants[:]
    randnull=random.Random(620623)
    for x in plants:
        letters=list(x["ciphertext"])
        randnull.shuffle(letters)
        c="".join(letters)
        assert len(c)==N and sorted(c)==sorted(x["ciphertext"]) and c!=x["ciphertext"]
        allrows.append({"role":"shuffle","ciphertext":c,
                        "plant_slot":x["plant_slot"],"cohort":x["cohort"],
                        "subgroup":x["subgroup"],"source_index":x["source_index"]})
    assert len(allrows)==80
    random.Random(620624).shuffle(allrows)
    with inp.open("x",encoding="ascii") as f:
        f.write("id\tciphertext\n")
        for j,row in enumerate(allrows):
            f.write(f"CASE_{j:03d}\t{row['ciphertext']}\n")
    truth={f"CASE_{j:03d}":row for j,row in enumerate(allrows)}
    with secret.open("x",encoding="ascii") as f:
        json.dump(truth,f,sort_keys=True,indent=2);f.write("\n")
    with prov.open("x",encoding="ascii") as f:
        json.dump({"classification":"R62_SEALED_PREPARED_NEVER_MOUNTED",
                   "input_sha256":sha(inp),"truth_sha256":sha(secret),
                   "modern_sha256":sha(modern_path),"k1k3_sha256":sha(k1_path),
                   "oz_sha256":sha(oz_path),"oz_blob":OZ_BLOB,"oz_commit":OZ_COMMIT,
                   "raw_cases":80,"plants":40,"nulls":40,"key_strata":40,
                   "sanborn":{"K1_K2":12,"K3":8},"modern":20,
                   "seeds":[620621,620622,620623,620624]},f,indent=2,sort_keys=True)
        f.write("\n")
    print("R62 sealed: 20 Sanborn text, 20 distinct modern text, 40 unseen English book keys, 40 shuffled nulls; opaque rows")
if __name__=="__main__":
    if len(sys.argv)!=7:raise SystemExit("prepare_controls.py K1K3 MODERN OZ INPUT SEALED_TRUTH SEALED_PROVENANCE")
    make(*sys.argv[1:])
