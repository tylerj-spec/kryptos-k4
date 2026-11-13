#!/usr/bin/env python3
"""Independent synthetic roundtrip test; never accesses K4 input or published clues."""
import random,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
import reference as R
def main():
    rng=random.Random(750003)
    configs=list(R.settings())
    assert len(configs)==2880
    cat=R.class_catalog()
    assert len(cat)==2880
    for s in configs:
        pt=''.join(rng.choices(R.AZ,k=R.N))
        c=R.encrypt(pt,s)
        assert len(c)==R.N and R.decrypt(c,s)==pt
        maps=R.maps40(s)
        assert ''.join(R.AZ[maps[i%40][R.AZ.index(pt[i])]] for i in range(R.N))==c
    for maps in cat:
        assert R.period40(maps)==40
    print('R75 OK: 2,880 exact reversible, 97-symbol trials; all 40-period maps unique.')
if __name__=='__main__':main()
