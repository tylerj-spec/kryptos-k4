#!/usr/bin/env python3
"""Contract & independent reverse/forward witness check on neutral synthetic messages."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PROGRAM=ROOT/"r55/blind/solve.cpp"
SRC=PROGRAM.read_text(encoding="utf-8").upper()
FORBIDDEN=("EASTNORTHEAST","BERLINCLOCK","NORTHEAST","KEY_ORACLE",
           "REFERENCE_MESSAGES","MASK","CLUE","CRIB","TRUTH","SEALED/")
for marker in FORBIDDEN:
    assert marker not in SRC, ("blind source contains prohibited dependency",marker)
assert "NUM_FAMILIES = 29952" in SRC
assert "CONSTEXPR INT TOP = 12" in SRC

if len(sys.argv)!=3:
    raise SystemExit("test_contract.py BINARY QUAD_MODEL")
binary,model=sys.argv[1:]
plaintext=("THEENGINEERSCARRIEDTHEWOODENBOXALONGTHENARROWPATH"
           "WHILETHEGARDENERSWATCHEDTHEMUNDERTHETALLTREESBEFOREMORNING")[:97]
assert len(plaintext)==97
pp=[ord(c)-65 for c in plaintext]
# Deliberately use nontrivial ciphertext-feedback under unknown settings.
c=[]
for i,v in enumerate(pp):
    x=c[i-4] if i>=4 else 0
    c.append((7*v+8+i-x)%26)
ciphertext="".join(chr(65+v) for v in c)

def verify(row,ct):
    assert row["tested"]==29952 and len(row["candidates"])==12
    assert all(len(z["plaintext"])==97 for z in row["candidates"])
    for z in row["candidates"]:
        p=[ord(x)-65 for x in z["plaintext"]]
        c=[]
        for i,x in enumerate(p):
            source=(p[i-z["lag"]] if z["mode"]=="plaintext"
                    else c[i-z["lag"]]) if i>=z["lag"] else 0
            c.append((z["multiplier"]*x+z["offset"]+z["step"]*i+z["sign"]*source)%26)
        assert "".join(chr(65+x) for x in c)==ct

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    inp=root/"input.tsv"
    out=root/"output.jsonl"
    inp.write_text("CONTROL_00\t"+ciphertext+"\n")
    p=subprocess.run([binary,str(inp),model,str(out)],capture_output=True,text=True,timeout=30)
    assert p.returncode==0,p.stderr
    rows=[json.loads(s) for s in out.read_text().splitlines()]
    assert len(rows)==1 and rows[0]["id"]=="CONTROL_00"
    verify(rows[0],ciphertext)
    assert subprocess.run([binary,str(inp),model,str(out)],capture_output=True).returncode!=0, "overwrote frozen result"
    for payload in [
        "CONTROL_00\t"+ciphertext+"\tMASK\n",
        "CONTROL_00\t"+ciphertext.lower()+"\n",
        "CONTROL_00\t"+ciphertext[:-1]+"\n",
        "CONTROL_00\t"+ciphertext+"EXTRA\n",
        "CONTROL_00\t"+ciphertext+" \n",
        "CONTROL_00\t"+ciphertext+"\nCONTROL_01\t"+ciphertext+"\tKEY\n",
    ]:
        inp.write_text(payload)
        out.unlink()
        p=subprocess.run([binary,str(inp),model,str(out)],capture_output=True,text=True,timeout=30)
        assert p.returncode!=0,("accepted malformed input",payload[:45])
print("R55 CONTRACT PASS: exact scope, neutral synthetics reencrypt, output is write-once, metadata rejected")
