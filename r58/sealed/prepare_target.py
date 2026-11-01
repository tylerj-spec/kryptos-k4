#!/usr/bin/env python3
"""R58B original ciphertext+100 frequency-preserving nulls. No K4 plaintext used."""
import hashlib,random,sys
from pathlib import Path

CANONICAL_SHA="2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def main():
    if len(sys.argv)!=3:raise SystemExit("prepare_target.py CANONICAL_K4_SOURCE OUTPUT.tsv")
    _,source,target=sys.argv
    assert not Path(target).exists(),"no overwrite"
    raw=Path(source).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==CANONICAL_SHA
    ct=raw.decode("ascii").strip()
    assert len(ct)==97 and set(ct)<=set(AZ)
    rng=random.Random(580070)
    seen={ct}
    rows=["K4"+chr(9)+ct+chr(10)]
    for i in range(100):
        for attempts in range(50):
            lst=list(ct);rng.shuffle(lst);null="".join(lst)
            if null not in seen:break
        assert null not in seen and sorted(null)==sorted(ct)
        seen.add(null)
        rows.append(f"NULL_{i:03d}"+chr(9)+null+chr(10))
    assert len(rows)==101
    Path(target).parent.mkdir(parents=True,exist_ok=True)
    with Path(target).open("x",encoding="ascii") as f:f.write("".join(rows))
    print("R58B prepared original 97-letter ciphertext and 100 fixed unranked nulls. No clue words processed.")
if __name__=="__main__":main()
