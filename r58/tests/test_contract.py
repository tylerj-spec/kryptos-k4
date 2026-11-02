#!/usr/bin/env python3
"""R58 unit tests independent of sealed holdouts and K4 clue evaluation."""
from pathlib import Path
import importlib.util, json, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[2]
code=(ROOT/"r58/blind/solve.py").read_text(encoding="utf-8").upper()
for banned in ("EASTNORTHEAST","BERLINCLOCK","CRIB_MASK",
               "KEY_ORACLE","AFTER_REVEAL","R52","PLAIN_TEXT_K4",
               "PUBLISHED_POSITION","KNOWN_OFFSETS"):
    assert banned not in code,("forbidden K4 clue dependency",banned)
spec=importlib.util.spec_from_file_location("r58blind",ROOT/"r58/blind/solve.py")
blind=importlib.util.module_from_spec(spec)
spec.loader.exec_module(blind)
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ";N=97
words=ROOT/"k4kit/data/word_model_orth.tsv"
quad=ROOT/"k4kit/data/quad_log10.f32"
routes=blind.physical_routes()
keys=blind.keys_from_model(words)
assert len(routes)==6 and len(keys)>=64
assert all(sorted(v)==list(range(N)) for v in routes.values())

def encode_v(p,key):
    A=blind.A
    return "".join(A[(A.index(c)+A.index(key[i%len(key)]))%26] for i,c in enumerate(p))
def encode_t(p,perm):
    return "".join(p[i] for i in perm)
def encode(p,cls,key,route):
    if cls=="V":return encode_v(p,key)
    if cls=="T":return encode_t(p,routes[route])
    if cls=="VT":return encode_t(encode_v(p,key),routes[route])
    if cls=="TV":return encode_v(encode_t(p,routes[route]),key)
    raise ValueError(cls)

plain=("THEWEATHERWASCLEARANDTHEGUIDEWALKEDSLOWLYACROSSTHE"
       "MOUNTAINBRIDGEWHILETHEOTHERSSTUDIEDTHEOLDSTONEWALLS")[:97]
assert len(plain)==97
for cls,key,route in (("V","KRYPTOS",None),
                      ("T",None,"COL_LT"),
                      ("VT","PALIMPSEST","COL_RB"),
                      ("TV","ABSCISSA","SNAKE_L")):
    ciphertext=encode(plain,cls,key,route)
    if cls=="V":
        recovered=blind.poly_decrypt(ciphertext,
                       [blind.A_INDEX[key[i%len(key)]] for i in range(97)])
    elif cls=="T":
        recovered=blind.unroute(ciphertext,routes[route])
    elif cls=="VT":
        inter=blind.unroute(ciphertext,routes[route])
        recovered=blind.poly_decrypt(inter,
                       [blind.A_INDEX[key[i%len(key)]] for i in range(97)])
    else:
        inter=blind.poly_decrypt(ciphertext,
                       [blind.A_INDEX[key[i%len(key)]] for i in range(97)])
        recovered=blind.unroute(inter,routes[route])
    assert recovered==plain,("round-trip failure",cls)

quad_model=blind.scores_model(quad)
data=blind.solve_one("CONTROL_00",encode(plain,"VT","PALIMPSEST","COL_RB"),
                     keys,routes,quad_model)
assert data["searched"]==len(keys)*13+6
assert len(data["candidates"])==8
assert data["detected_family"] in ("V","T","VT","TV","ABSTAIN")
ciphertext=encode(plain,"VT","PALIMPSEST","COL_RB")
for c in data["candidates"]:
    assert len(c["plaintext"])==97 and all(x in AZ for x in c["plaintext"])
    assert encode(c["plaintext"],c["family"],c["key"],c["route"])==ciphertext

with tempfile.TemporaryDirectory() as root:
    root=Path(root);input_file=root/"in.tsv";output_file=root/"out.jsonl"
    input_file.write_text("CONTROL_00"+chr(9)+ciphertext+chr(10))
    cmd=[sys.executable,"-I","-B",str(ROOT/"r58/blind/solve.py"),
         str(input_file),str(words),str(quad),str(output_file)]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
    assert p.returncode==0,p.stderr
    assert len(output_file.read_text().splitlines())==1
    repeat=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
    assert repeat.returncode!=0,"write-once output contract violated"
    for malformed in (ciphertext.lower(),ciphertext[:-1],ciphertext+"X"):
        input_file.write_text("CONTROL_00"+chr(9)+malformed+chr(10))
        output_file.unlink()
        rerun=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
        assert rerun.returncode!=0,("accepted malformed ciphertext",malformed)
        assert output_file.exists()  # the script can create a partial file, but exits nonzero

print("R58 CONTRACT PASSED: physical route and V/T/VT/TV round trips, 97-letter validation, clues absent, no overwrite")
