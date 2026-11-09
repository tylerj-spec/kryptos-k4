#!/usr/bin/env python3
"""R75 algebraic novelty audit (no K4 data/known letters).
Run: python3 -I r75/audit.py [output.json]
"""
import json, random, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import reference as R

def main():
    rng=random.Random(750001)
    raw=list(R.settings())
    classes=R.class_catalog()
    assert len(raw)==2880
    assert len(classes)==2880
    assert len(set(R.KRY))==26
    for an,a in R.ALPHABETS.items():
        for op in R.OPS:
            for key in R.KEYS:
                for phase in (0,len(key)-1):
                    pt=''.join(rng.choices(R.AZ,k=R.N))
                    assert R.unstage(R.stage(pt,key,phase,op,a),key,phase,op,a)==pt
    for s in raw:
        pt=''.join(rng.choices(R.AZ,k=R.N))
        ct=R.encrypt(pt,s)
        assert R.decrypt(ct,s)==pt,('roundtrip',s)
        m=R.maps40(s)
        assert ''.join(R.AZ[m[j%40][R.AZ.index(pt[j])]] for j in range(R.N))==ct
    # Compare each of the 40 positional substitution maps to all
    # fixed single-stage 26-shift Quagmire/Vig/Beau/VBeau settings across
    # AZ, KRYPTOS, PALIMPSEST and ABSCISSA keyword-derived alphabets.
    R.ALPHABETS['PAL']=''.join(dict.fromkeys('PALIMPSEST'+R.AZ))
    R.ALPHABETS['ABS']=''.join(dict.fromkeys('ABSCISSA'+R.AZ))
    ones=R.single_stage_maps(('AZ','KRY','PAL','ABS'))
    matches=sum(all(slot in ones for slot in m) for m in classes)
    counts=dict(sorted(Counter(R.period40(x) for x in classes).items()))
    report={
      'scope':'two distinct AZ/KRY same-alphabet stages; 10x8 keyword periods',
      'original_K4_ciphertext_used':False,'public_K4_plaintext_used':False,
      'raw_settings':len(raw),'distinct_full_40_maps':len(classes),
      'reversible_explicit_97_letter_trials':len(raw),
      'period_counts':counts,
      'all_40_slots_equivalent_to_prior_fixed_single_stage_tableaux':matches,
      'prior_fixed_single_stage_slot_maps':len(ones),
      'equivalence_check_limit':'No global proof against arbitrary period-40 26! per-slot alphabets (L21).'
    }
    print(json.dumps(report,indent=2))
    if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
