#!/usr/bin/env python3
"""R60 source/roundtrip contract, uses no original K4 plaintext or clue offsets."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
solve_source=(ROOT/"r58/blind/solve.py").read_text()
for banned in ("EASTNORTHEAST","BERLINCLOCK","KNOWN_K4","CLUE_POSITION",
               "r60/sealed","r58/frozen/K4","R52_SURVIVOR"):
    assert banned not in solve_source,("ciphertext-only source contains a clue",banned)

spec=importlib.util.spec_from_file_location("R60_sealed_fixture",ROOT/"r60/sealed/prepare.py")
fixture=importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)

assert len(fixture.PASSAGES)==20
texts=[fixture.clean(t)[:97] for w,t in fixture.PASSAGES]
assert all(len(x)==97 and w in x for x,(w,t) in zip(texts,fixture.PASSAGES))
assert len(set(texts))==20
routes=fixture.route_permutations()
assert len(routes)==6
for name,p in routes.items():
    assert len(p)==97 and sorted(p)==list(range(97))
A=fixture.A
assert len(A)==26 and set(A)==set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
for family,key,route in (
    ("V","KRYPTOS",None),
    ("T",None,"SNAKE_R"),
    ("VT","PALIMPSEST","COL_RB"),
    ("TV","ABSCISSA","COL_LT")
):
    p=texts[0]
    a=fixture.encrypt(p,family,key,route,routes,"CAKE MEANS MEETING TOMORROW")
    b=fixture.encrypt(p,family,key,route,routes,"CAKE MEANS DELIVERED PACKAGE")
    assert a==b and len(a)==97
    assert set(a)<=set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
print("R60 contract passed: 20 distinct ordinary English covertexts, six reversible physical routes, and 4 independent dual-meaning ciphertext equalities")
