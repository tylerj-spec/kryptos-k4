#!/usr/bin/env python3
"""R62C ciphertext-only original K4/300 shuffles and 21 route-family inputs.
No published plaintext words/positions, no candidate plaintext and no key source.
Exactly canonical 97-letter ciphertext, strict byte hash with newline.
"""
import hashlib,random,sys
from pathlib import Path
N=97
SEED=620640
SHA="2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
AZ=set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
def main():
    if len(sys.argv)!=3:raise SystemExit("prepare.py CANONICAL_K4_CIPHERTEXT OUT.tsv")
    path,target=map(Path,sys.argv[1:])
    assert not target.exists()
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SHA
    ct=raw.decode("ascii").strip()
    assert len(ct)==N and set(ct)<=AZ
    rows=["id\tciphertext\tshift"]
    for s in range(21):
        rows.append(f"CASE_{s:03d}\t{ct}\t{s}")
    rng=random.Random(SEED)
    seen={ct}
    for j in range(300):
        while True:
            arr=list(ct)
            rng.shuffle(arr)
            null="".join(arr)
            if null not in seen:break
        seen.add(null)
        assert sorted(null)==sorted(ct)
        rows.append(f"CASE_{j+21:03d}\t{null}\t0")
    assert len(rows)==322
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text("\n".join(rows)+"\n",encoding="ascii")
    print(f"R62C original 21 fixed route families and 300 fresh shuffle nulls, seed {SEED}")
if __name__=="__main__":main()
