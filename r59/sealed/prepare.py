#!/usr/bin/env python3
"""R59 SEALED fixture generator. Must NEVER be available to blind statistic scanner.
Generates simulated random pads, repeated short masks, and independently sourced
book-running keys, hiding *both* messages and generating class.
"""
from pathlib import Path
import hashlib
import json
import random
import sys

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N = 97
SEED = 590059
K4_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
BLOBS = {
    "wells": "419c78ce03f41984ef14913739b48d9332bd2801",
    "sherlock": "ea9235417718bb0a438795c1dd7cbf65472b40fb",
}

def git_blob_sha(raw):
    prefix = b"blob " + str(len(raw)).encode("ascii") + bytes((0,))
    return hashlib.sha1(prefix + raw).hexdigest()

def body_text(name, path):
    data = Path(path).read_bytes()
    got = git_blob_sha(data)
    assert got == BLOBS[name], ("literary corpus not at pinned Git blob",name,got)
    t = data.decode("utf-8",errors="replace")
    central = t[len(t)//10:9*len(t)//10].upper()
    t = "".join(c for c in central if c in AZ)
    assert len(t) >= 45*200, ("corpus too short",name)
    return t

def sample_windows(books,rng):
    passages=[]
    for name in ("wells","sherlock"):
        letters=books[name]
        span=len(letters)//45
        assert span >= 140
        for i in range(45):
            start=i*span+rng.randrange(span-N)
            sample=letters[start:start+N]
            assert len(sample)==N
            passages.append({"plaintext":sample,"source":name,"source_bin":i,
                             "source_start":start})
    assert len(passages)==90
    assert len({p["plaintext"] for p in passages})==90
    rng.shuffle(passages)
    return passages

def forward(p,key):
    assert len(p)==len(key)==N
    return "".join(chr(65+(ord(x)+ord(k)-130)%26) for x,k in zip(p,key))

def prepare(wells,sherlock,canonical,inp,truth):
    rng=random.Random(SEED)
    books={"wells":body_text("wells",wells),
           "sherlock":body_text("sherlock",sherlock)}
    passages=sample_windows(books,rng)
    kinds=["SIMULATED_UNIFORM_PAD"]*30+["PERIODIC_MASK"]*30+["BOOK_RUNNING_KEY"]*30
    rng.shuffle(kinds)
    raw=Path(canonical).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==K4_SHA
    k4=raw.decode("ascii").strip()
    assert len(k4)==N and set(k4)<=set(AZ)
    lines=[]
    true={}
    for i,(context,kind) in enumerate(zip(passages,kinds)):
        p=context["plaintext"]
        meta={}
        if kind=="SIMULATED_UNIFORM_PAD":
            # This is a reproducible pseudo-uniform toy, NOT a secure true OTP.
            key="".join(AZ[rng.randrange(26)] for _ in range(N))
        elif kind=="PERIODIC_MASK":
            period=rng.randrange(3,7)
            shortkey="".join(AZ[rng.randrange(26)] for _ in range(period))
            key=(shortkey*((N+period-1)//period))[:N]
            meta={"short_period":period,"short_key":shortkey}
        elif kind=="BOOK_RUNNING_KEY":
            other="sherlock" if context["source"]=="wells" else "wells"
            text=books[other]
            offset=rng.randrange(0,len(text)-N+1)
            key=text[offset:offset+N]
            meta={"key_source":other,"key_start":offset}
        else:
            raise ValueError(kind)
        ct=forward(p,key)
        assert len(ct)==97 and set(ct)<=set(AZ)
        lab=f"CASE_{i:03d}"
        lines.append(lab+chr(9)+ct+chr(10))
        true[lab]={"family":kind,"plaintext":p,"full_key":key,
                   "book":context["source"],"window":context["source_bin"],
                   "start":context["source_start"],"details":meta}
    assert len(lines)==90 and all(kinds.count(c)==30 for c in set(kinds))
    lines.append("K4"+chr(9)+k4+chr(10))
    input_file=Path(inp);truth_file=Path(truth)
    assert input_file.resolve()!=truth_file.resolve()
    for f in (input_file,truth_file):
        f.parent.mkdir(parents=True,exist_ok=True)
    with input_file.open("x",encoding="ascii") as f:f.write("".join(lines))
    with truth_file.open("x",encoding="utf-8") as f:
        json.dump(true,f,indent=2,sort_keys=True);f.write(chr(10))
    print("R59 sealed: 90 mixed/opaque ciphertext controls + unchanged K4; true keys withheld.")

if __name__=="__main__":
    if len(sys.argv)!=6:
        raise SystemExit("prepare.py PINNED_WELLS PINNED_SHERLOCK ORIGINAL_K4 INPUT.tsv TRUTH.json")
    prepare(*sys.argv[1:])
