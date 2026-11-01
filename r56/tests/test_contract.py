#!/usr/bin/env python3
"""R56 method validation and blind-source firewall, independent from sealed K4 evaluator."""
from pathlib import Path
import json,subprocess,sys,tempfile

AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ROOT=Path(__file__).resolve().parents[2]
SRC=(ROOT/"r56/blind/solve.cpp").read_text().upper()
assert not any(w in SRC for w in (
    "EASTNORTHEAST","BERLINCLOCK","NORTHEAST","KEY_ORACLE",
    "REFERENCE_MESSAGES","CRIB_MASK","SECRET_PLAINTEXT",
    "K4_CIPHERTEXT","CLUE_POSITION","ANCHORED_POSITION",
    "R55/FROZEN","R52/EDUCATED"
)), "blind source has K4-known-plaintext dependencies"
assert "CONSTEXPR INT TOP=12" in SRC
assert "CONSTEXPR INT N=97" in SRC

def rotate(s,k):
    k%=26
    return s[k:]+s[:k]
def encrypt(plain,left,right):
    out=[]
    for char in plain:
        j=right.index(char)
        out.append(left[j])
        left=rotate(left,j)
        l=left[1]
        left=left[:1]+left[2:14]+l+left[14:]
        right=rotate(right,j+1)
        r=right[2]
        right=right[:2]+right[3:14]+r+right[14:]
    return "".join(out)

# Third-party published Chaocipher reference vector: this does NOT concern K4.
L="HXUCZVAMDSLKPEFJRIGTWOBNYQ"
R="PTLNBQDEOYSFAVZKGJRIHWXUMC"
phrase="WELLDONEISBETTERTHANWELLSAID"
expected="OAHQHCNYNXTSZJRRHJBYHQKSOUJY"
assert encrypt(phrase,L,R)==expected, "Chaocipher algorithm must match published reference"

if len(sys.argv)!=4:
    raise SystemExit("test_contract.py BLIND_BINARY GENERIC_WORDS.tsv GENERIC_QUAD.f32")
binary,words,quad=sys.argv[1:]
p=(phrase*4)[:97]
assert len(p)==97
ct=encrypt(p,L,R)
with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp);inp=d/"cipher.tsv";out=d/"result.jsonl"
    inp.write_text("SYNTHETIC_00\t"+ct+"\n")
    run=subprocess.run([binary,str(inp),words,quad,str(out)],
                       text=True,capture_output=True,timeout=90)
    assert run.returncode==0,run.stderr
    row=json.loads(out.read_text().strip())
    assert row["id"]=="SYNTHETIC_00" and len(row["candidates"])==12
    assert row["searched"]==52*row["keyword_alphabets"] and row["keyword_alphabets"]>0
    for c in row["candidates"]:
        k=c["keyword_alphabet"]
        assert len(k)==26 and set(k)==set(AZ)
        left=k if c["keyword_side"]=="left" else AZ
        right=k if c["keyword_side"]=="right" else AZ
        right=rotate(right,c["right_initial_phase"])
        assert encrypt(c["plaintext"],left,right)==ct, "candidate does not independently re-encrypt"
    run=subprocess.run([binary,str(inp),words,quad,str(out)],capture_output=True)
    assert run.returncode!=0, "solver overwrote previous output"
    for invalid in [
        "SYNTHETIC_00\t"+ct+"\tK4_MASK\n",
        "SYNTHETIC_00\t"+ct[:-1]+"\n",
        "SYNTHETIC_00\t"+ct.lower()+"\n",
        "SYNTHETIC_00\t"+ct+" \n",
    ]:
        inp.write_text(invalid)
        out.unlink()
        run=subprocess.run([binary,str(inp),words,quad,str(out)],capture_output=True,timeout=90)
        assert run.returncode!=0, "malformed or extra-field input accepted"
print("R56 SOURCE CONTRACT PASS: no K4 plaintext; canonical Chaocipher vector; independent forward witnesses; write-once; input strict")
