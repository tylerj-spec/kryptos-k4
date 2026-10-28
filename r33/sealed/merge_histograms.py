#!/usr/bin/env python3
"""Postfreeze summary of C++ whole-family clue-check histograms."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
reports={}
for fam, expected in [('G5',192*100000*12),('CARTER',24*(282924-96)*4*12)]:
    hist=[0]*25;best=0; examples=[]; totals=[]
    for i in range(4):
        lines=(root/'results'/f'whole_{fam.lower()}_{i}.txt').read_text().splitlines()
        assert lines[0].startswith('BEST\t')
        b=int(lines[0].split('\t')[1]);n=lines[0].split('\t')[2]
        if b>best:best=b;examples=[n]
        elif b==best:examples.append(n)
        row=next(l for l in lines if l.startswith('HIST\t'))
        hs=[int(q) for q in row.split('\t')[1:]]
        assert len(hs)==25
        hist=[a+b for a,b in zip(hist,hs)]
        totals.append(sum(hs))
    assert sum(hist)==expected,(fam,sum(hist),expected)
    reports[fam]={'settings':expected,'max_clue_match':best,'full24':hist[24],'histogram':hist,'best_settings':examples,'sum_per_partition':totals}
for fn in ('routes_g5.txt','routes_carter.txt'):
    rows=(root/'runs'/fn).read_text().splitlines()
    perms=[tuple(map(int,x.split()[2].split(','))) for x in rows]
    reports[fn]={'route_order_settings':len(rows),'distinct_permutations':len(set(perms))}
(root/'results/WHOLE_FAMILY_POSTFREEZE.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps({f:{k:v for k,v in d.items() if k in ('settings','max_clue_match','full24','route_order_settings','distinct_permutations')} for f,d in reports.items()},indent=2))
