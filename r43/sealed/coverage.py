#!/usr/bin/env python3
"""Sealed-only vocabulary coverage diagnostic for development fixtures (not solver input)."""
import json
import sys
from pathlib import Path

truth = json.loads(Path(sys.argv[1]).read_text())
model = Path(sys.argv[2])
ranked = {}
for line in model.read_text().splitlines():
    parts=line.split()
    if len(parts)!=3:
        continue
    w,raw,_=parts
    try:
        score=float(raw)
    except ValueError:
        continue
    if score < -1e50 or not (w.isalpha() and w.isupper()):
        continue
    ranked.setdefault(len(w), []).append((score,w))
sets={}
for cap in (64,128,256,512,1024,2048):
    sets[cap]={n:set(w for score,w in sorted(ws,reverse=True)[:cap]) for n,ws in ranked.items()}
for label,v in list(truth.items())[:5]:
    words=[];total=0
    for t in v["source_sentence"].upper().split():
        clean="".join(c for c in t if "A"<=c<="Z")
        left=97-total
        if left<=0: break
        words.append((clean[:left],len(clean)<=left))
        total+=min(len(clean),left)
    print(label,"words",len(words),
          "tail",words[-1],
          "caps",[(cap,sum(full and w in sets[cap].get(len(w),set()) for w,full in words),
                    "/",sum(full for _,full in words)) for cap in sets])
