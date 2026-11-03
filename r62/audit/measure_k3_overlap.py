#!/usr/bin/env python3
"""Independent exact-substring audit: Kryptos K3 source overlap in R59 training.
R59 generic language model explicitly includes Carter & Mace 1923 text.
NO original K4 plaintext, K4 known public words or offsets are used.
"""
import hashlib,json,sys
from pathlib import Path
def clean(s):return "".join(c for c in s.upper() if "A"<=c<="Z")
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=4:
        raise SystemExit("measure_k3_overlap.py K1K3.txt CARTER_AZ.txt OUTPUT.json")
    _,kpath,cpath,out=sys.argv
    assert not Path(out).exists()
    alltext=clean(Path(kpath).read_text(encoding="utf-8"))
    carter=clean(Path(cpath).read_text(encoding="utf-8"))
    assert len(alltext)>=769 and len(carter)>143000
    k3=alltext[433:769]
    assert len(k3)==336
    region=carter[137000:143000]
    marked=set()
    best={"length":0,"k3_start":None,"carter_az_start":None,"fragment":""}
    # A K3 position counts only if in an EXACT match of >=12 adjacent
    # unspaced letters in the documented Carter source neighborhood.
    for i in range(len(k3)-11):
        n=12
        if region.find(k3[i:i+n])<0:continue
        while i+n<len(k3) and region.find(k3[i:i+n+1])>=0:
            n+=1
        for j in range(n):marked.add(i+j)
        if n>best["length"]:
            best={"length":n,"k3_start":i,
                  "carter_az_start":137000+region.find(k3[i:i+n]),
                  "fragment":k3[i:i+n]}
    assert len(marked)==291 and best["length"]==64 and best["k3_start"]==22
    result={
      "classification":"R62_K3_PRETRAINED_CORPUS_OVERLAP_NOT_K4_DECRYPTION",
      "K3_unduplicated_letters":336,
      "first_k3_start_in_k1k3_file":433,
      "first_k3_end_exclusive":769,
      "carter_clean_letters_compared_start":137000,
      "carter_clean_letters_compared_end_exclusive":143000,
      "criterion":"K3 character position belongs to >=1 exact contiguous >=12-character Carter-source match",
      "K3_positions_in_criterion":len(marked),
      "K3_fraction_covered":len(marked)/len(k3),
      "longest_exact_Carter_training_match":best,
      "source_K1K3_sha256":sha(kpath),
      "source_Carter_sha256":sha(cpath),
      "confounding":"Carter & Mace 1923 is in R59 6-gram training corpus; K3-derived controls are not clean unseen writing; even K3's imperfect transcription has extensive verbatim 12+grams",
      "limitations":"This only measures one 6000-letter Carter region and first unduplicated K3. It does not assert that all of K3 or any of K4 is in the corpus."
    }
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    with Path(out).open("x",encoding="ascii") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("K3 contamination:",len(marked),"/336 chars in exact Carter matches >=12, longest",best["length"],
          "source hash K3",result["source_K1K3_sha256"])
if __name__=="__main__":main()
