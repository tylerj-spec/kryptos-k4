#!/usr/bin/env python3
"""R57 independent Hill known-vector and no-clue blind contract test."""
import json,math,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=(ROOT/"r57/blind/solve.cpp").read_text().upper()
for forbidden in ("EASTNORTHEAST","BERLINCLOCK","NORTHEAST",
                  "KEY_ORACLE","CLUE_POSITION","SECRET_PLAINTEXT",
                  "K4_CIPHERTEXT","R55/FROZEN","R56/FROZEN"):
    assert forbidden not in SOURCE, ("R57 source imported known plaintext",forbidden)
assert "EXPECTED=97344" in SOURCE and "TOP=12" in SOURCE
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def enc(p,a,b,c,d):
    assert len(p)==97 and math.gcd(a,26)==1
    assert math.gcd((a*d-b*c)%26,26)==1
    v=[]
    for i in range(0,96,2):
        x=ord(p[i])-65;y=ord(p[i+1])-65
        v.append(chr(65+(a*x+b*y)%26))
        v.append(chr(65+(c*x+d*y)%26))
    v.append(chr(65+(a*(ord(p[96])-65)+23*b)%26))
    return "".join(v)
# Public, independently checkable Hill digraph example:
# M=[[5,11],[1,22]], "NU" -> "ZL".
assert (5*13+11*20)%26==25 and (1*13+22*20)%26==11
assert math.gcd(5*22-11,26)==1
if len(sys.argv)!=3:
    raise SystemExit("test_contract.py BINARY QUAD.f32")
binary,quad=sys.argv[1:]
msg=("NUNU"+("THEASTRONOMERSWATCHEDTHENIGHTSKY"
           "ANDRECORDEDTHEPOSITIONOFEACHPLANET"))[:97]
msg=(msg*4)[:97]
assert len(msg)==97
ct=enc(msg,5,11,1,22)
with tempfile.TemporaryDirectory() as tmp:
    folder=Path(tmp);incoming=folder/"in.tsv";out=folder/"results.jsonl"
    incoming.write_text("CONTROL_00\t"+ct+"\n")
    x=subprocess.run([binary,str(incoming),quad,str(out)],
                     capture_output=True,text=True,timeout=100)
    assert x.returncode==0,x.stderr
    row=json.loads(out.read_text().strip())
    assert row["searched"]==97344 and len(row["candidates"])==12
    assert row["id"]=="CONTROL_00"
    for c in row["candidates"]:
        assert enc(c["plaintext"],*[c[z] for z in ("a","b","c","d")])==ct
    x=subprocess.run([binary,str(incoming),quad,str(out)],capture_output=True,timeout=100)
    assert x.returncode!=0,"existing output must never be overwritten"
    for bad in (
        "CONTROL_00\t"+ct+"\tEXTRA\n",
        "CONTROL_00\t"+ct[:-1]+"\n",
        "CONTROL_00\t"+ct.lower()+"\n",
        "CONTROL_00\t"+ct+" \n"
    ):
        incoming.write_text(bad);out.unlink()
        x=subprocess.run([binary,str(incoming),quad,str(out)],
                         capture_output=True,timeout=100)
        assert x.returncode!=0, "malformed blind input accepted"
print("R57 HILL CONTRACT PASS: known NU/ZL vector, complete 97344-key search, forward witnesses, two-field inputs")
