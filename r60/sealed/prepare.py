#!/usr/bin/env python3
"""R60 sealed fixture construction for semantic covertext.
The ciphertext-only solver must NOT see this source, plaintexts, keys,
family labels, or private meaning assignments.
"""
from pathlib import Path
import hashlib
import json
import math
import random
import sys

N=97
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEY_NAMES=("KRYPTOS","PALIMPSEST","ABSCISSA")
A="".join(dict.fromkeys("KRYPTOS"+AZ))
INDEX={c:i for i,c in enumerate(A)}
assert len(A)==26

# Independent ordinary English passages containing their preselected coverword.
# These are synthetic, not proposed K4 plaintexts, keywords, or crib material.
PASSAGES=(
("CAKE","The gardener promised the cake would be ready before sunset and asked everyone to gather by the north gate after the morning service ended."),
("APPLE","The courier carried a green apple past the front desk while the guard checked the roster and locked the storage room for the evening."),
("RIVER","A fisherman crossed the shallow river at dawn and quietly returned the wooden paddle to its proper place near the village cottage."),
("BRIDGE","The travelers followed the stone bridge into town and stopped beside the public fountain to review the map before continuing west."),
("GARDEN","A small garden behind the library had been neglected for years until a group of neighbors agreed to restore the pathways and benches."),
("LANTERN","The old lantern flickered near the entrance while the caretaker inspected the shutters and prepared the upstairs rooms for guests."),
("WINDOW","The child looked through the window toward the orchard and watched the distant clouds drift slowly above the green hills."),
("MARKET","At the market several merchants arranged fresh bread and fruit beneath the awnings and welcomed visitors arriving at daybreak."),
("CLOCK","The clock beside the staircase stopped at midnight and the watchmaker returned at dawn to investigate the missing brass spring."),
("HORSE","The horse moved quietly through the meadow as the traveler secured his saddle and checked the narrow trail toward the village."),
("TRAIN","A passenger left the train just before noon and carried a small leather case through the station toward the busy public square."),
("FLOWER","A bright flower grew beside the old wooden fence where the gardener had planted several seeds during the previous spring."),
("BOOK","The librarian placed the book inside a glass cabinet after discovering a handwritten note tucked beneath the back cover."),
("TABLE","The carpenter moved the heavy table toward the northern wall and examined its carved legs for signs of damage or repair."),
("BOTTLE","A glass bottle rested near the kitchen sink while the cook prepared a simple meal for the visitors arriving later that night."),
("LETTER","The messenger folded the letter carefully and placed it in a sealed envelope before handing it to the waiting driver."),
("HARBOR","The harbor was quiet in the early morning as the sailors untied their ropes and prepared the small fishing boats for departure."),
("FOREST","A narrow path through the forest led to an abandoned cottage hidden beneath the tall trees near a quiet mountain stream."),
("CANDLE","The candle burned beside the desk while the historian studied several faded photographs and copied notes into a journal."),
("FARM","The farm remained peaceful throughout the afternoon as the workers collected tools and brought the horses back to the barn."),
)

def clean(s):
    return "".join(ch for ch in s.upper() if ch in AZ)

def keys_from_generic_model(path):
    words=[]
    for line in Path(path).open(encoding="utf-8"):
        cols=line.split()
        if len(cols)<2:continue
        w=cols[0]
        if not (w.isascii() and w.isalpha() and w.isupper() and 5<=len(w)<=10):
            continue
        try:val=float(cols[1])
        except ValueError:continue
        if math.isfinite(val):words.append((-val,w))
    words.sort()
    picked=set()
    for _,w in words:
        picked.add(w)
        if len(picked)==64:break
    assert len(picked)==64
    return tuple(sorted(picked.union(KEY_NAMES)))

def route_permutations():
    sites=[(0,c) for c in range(27,31)]+[
        (r,c) for r in (1,2,3) for c in range(31)
    ]
    assert len(sites)==N
    loc={cell:i for i,cell in enumerate(sites)}
    mapping={}
    for cd in ("L","R"):
        for rd in ("T","B"):
            cols=range(31) if cd=="L" else range(30,-1,-1)
            rows=range(4) if rd=="T" else range(3,-1,-1)
            mapping["COL_"+cd+rd]=tuple(loc[(r,c)] for c in cols
                                      for r in rows if (r,c) in loc)
    for start in ("L","R"):
        order=[]
        for r in range(4):
            row=[loc[cell] for cell in sites if cell[0]==r]
            reverse=(r%2==1)==(start=="L")
            order.extend(row[::-1] if reverse else row)
        mapping["SNAKE_"+start]=tuple(order)
    assert len(mapping)==6
    assert all(sorted(perm)==list(range(N)) for perm in mapping.values())
    return mapping

def add_tableau(plain,key):
    return "".join(A[(INDEX[ch]+INDEX[key[i%len(key)]])%26]
                   for i,ch in enumerate(plain))

def permute(plain,order):
    return "".join(plain[i] for i in order)

def encrypt(plain,family,key,route,routes,private_meaning):
    # The semantic meaning deliberately does NOT enter cryptographic arithmetic.
    # That is the exact distinction being tested, NOT a claim about actual K4.
    assert private_meaning and len(plain)==97
    if family=="V":return add_tableau(plain,key)
    if family=="T":return permute(plain,routes[route])
    if family=="VT":return permute(add_tableau(plain,key),routes[route])
    if family=="TV":return add_tableau(permute(plain,routes[route]),key)
    raise ValueError("invalid tested family")

def write_new(path,body):
    dest=Path(path)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as stream:stream.write(body)

def main():
    if len(sys.argv)!=4:
        raise SystemExit("prepare.py GENERIC_WORDS.tsv CIPHERTEXT_ONLY.tsv SEALED_TRUTH.json")
    _,wordfile,inputfile,truthfile=sys.argv
    assert Path(inputfile).resolve()!=Path(truthfile).resolve()
    rng=random.Random(600060)
    nullrng=random.Random(600061)
    keys=keys_from_generic_model(wordfile)
    routes=route_permutations()
    family_schedule=list("V"*5+"T"*5)+["VT"]*5+["TV"]*5
    rng.shuffle(family_schedule)
    items=[]
    for i,((word,body),family) in enumerate(zip(PASSAGES,family_schedule)):
        p=clean(body)[:N]
        assert len(p)==N and word in p,("fixture coverword missing",word)
        key=rng.choice(keys) if family in ("V","VT","TV") else None
        route=rng.choice(sorted(routes)) if family in ("T","VT","TV") else None
        meaning_a=f"{word} denotes rendezvous location {i:02d} at 0500"
        meaning_b=f"{word} denotes transfer order {i:02d} at 2300"
        assert meaning_a!=meaning_b
        a=encrypt(p,family,key,route,routes,meaning_a)
        b=encrypt(p,family,key,route,routes,meaning_b)
        assert a==b,("semantics leaked into ciphertext",word)
        items.append({
            "cipher":a,"family":family,"plaintext":p,"key":key,"route":route,
            "coverword":word,"meaning_a":meaning_a,"meaning_b":meaning_b,
            "source_index":i
        })
    assert len(items)==20
    for i in range(20):
        c="".join(AZ[nullrng.randrange(26)] for _ in range(N))
        items.append({"cipher":c,"family":"UNIFORM_NULL",
                      "plaintext":None,"key":None,"route":None,
                      "coverword":None,"meaning_a":None,"meaning_b":None,
                      "source_index":None})
    rng.shuffle(items)  # IDs are NOT correlated with generating family.
    assert len(items)==40
    rows=[]
    truth={}
    for i,d in enumerate(items):
        ident=f"CASE_{i:03d}"
        rows.append(ident+chr(9)+d.pop("cipher")+chr(10))
        truth[ident]=d
    assert {x:sum(v["family"]==x for v in truth.values()) for x in
            ("V","T","VT","TV","UNIFORM_NULL")}=={
            "V":5,"T":5,"VT":5,"TV":5,"UNIFORM_NULL":20}
    write_new(inputfile,"".join(rows))
    write_new(truthfile,json.dumps(truth,indent=2,sort_keys=True)+chr(10))
    print("R60: 40 opaque hidden-family ciphertexts; 20 semantic codebook pairs sealed")
if __name__=="__main__":
    main()
