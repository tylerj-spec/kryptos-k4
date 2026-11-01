#!/usr/bin/env python3
"""R56 sealed synthetic encryptor, independent of C++ decryptor. Never mounted with solver."""
from pathlib import Path
import hashlib,json,random,sys
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N=97
SOURCE_SHA="2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
PASSAGES=(
    "The traveler unfolded his notebook beside the lantern and carefully drew a map showing the narrow bridges that crossed the river beyond the village.",
    "Long before the opening ceremony the musicians gathered inside the empty hall and tuned their instruments while waiting for the conductor to arrive.",
    "The lighthouse keeper polished the windows on the upper floor before checking the weather charts and securing the heavy wooden door against the wind.",
    "Each spring the botanist returned to the mountain valley to observe the wildflowers that grew in the sheltered meadows beside the melting snow.",
    "A small fishing boat passed beneath the old stone archway at sunrise while the harbor workers prepared the market stalls for another busy morning.",
    "After examining the faded letters the researcher carefully copied every visible mark onto fresh paper and sealed the documents inside a protective case.",
    "The architect placed a collection of wooden models across the long table and explained how each structure would admit sunlight through its upper windows.",
    "A distant train sounded its whistle while the station attendant checked the departure board and carried the final parcels toward the waiting passenger cars.",
    "The carpenter carried a heavy chest into the workshop and began repairing the brass hinges that held the lid in place after many years of use.",
    "In the museum courtyard several visitors gathered around a large stone fountain and listened as a guide described the history of the surrounding buildings.",
    "Before the morning clouds disappeared the farmers walked through their fields and inspected the rows of young plants for evidence of damage from heavy rain.",
    "The writer spent the afternoon sorting old correspondence and arranging the envelopes by date before beginning the long task of transcribing their contents.",
    "Three hikers followed a narrow trail across the hillside until they reached a wooden observation platform overlooking the valley and distant river.",
    "The school caretaker opened the front doors at dawn and walked through each corridor checking the lights and windows before the first students arrived.",
    "With a steady hand the artist traced a delicate pattern onto the wooden panel and began filling each shape with carefully mixed shades of blue paint.",
    "The expedition carried several crates of supplies across the rocky shoreline before setting up a temporary shelter beneath the cliffs overlooking the sea.",
    "A gentle breeze moved through the orchard as the family collected ripe apples in baskets and carried them back to the small farmhouse near the stream.",
    "During the evening rehearsal the theater director watched every movement from the balcony and quietly recorded suggestions for the following performance.",
    "The young mechanic spent hours examining the broken clockwork and eventually discovered a worn metal spring hidden beneath the lower wooden cover.",
    "The librarian opened a dusty cabinet and discovered an old catalogue containing handwritten descriptions of books that had been missing for many years.",
)
def clean(s):
    return "".join(ch for ch in s.upper() if ch in AZ)
def word_alphas(file):
    ws=[]
    with open(file,encoding="ascii") as f:
        for line in f:
            parts=line.split()
            if len(parts)!=3:continue
            w,score,_=parts
            if w.isupper() and w.isalpha() and 5<=len(w)<=10:
                q=float(score)
                if q>-1e90 and q!=float("inf") and q!=float("-inf"):ws.append((-q,w))
    ws.sort()
    assert len(ws)>=1024
    words=[w for _,w in ws[:1024]]
    alphas=set()
    for w in words:
        a=""
        for c in w+AZ:
            if c not in a:a+=c
        assert len(a)==26 and sorted(a)==sorted(AZ)
        alphas.add(a)
    return sorted(alphas)
def rotate(a,n):
    n%=26
    return a[n:]+a[:n]
def encrypt(plain,alpha,side,phase):
    left=alpha if side=="left" else AZ
    right=alpha if side=="right" else AZ
    right=rotate(right,phase)
    out=[]
    for char in plain:
        j=right.index(char)
        out.append(left[j])
        left=rotate(left,j)
        lc=left[1]
        left=left[:1]+left[2:14]+lc+left[14:]
        right=rotate(right,j+1)
        rc=right[2]
        right=right[:2]+right[3:14]+rc+right[14:]
    return "".join(out)
def write_new(path,txt):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="ascii") as f:f.write(txt)
def controls(wordpath,inputpath,truthpath):
    assert len(PASSAGES)==20
    a=word_alphas(wordpath)
    rnd=random.Random(560056)
    lines=[]
    truth={}
    for i,passage in enumerate(PASSAGES):
        original=clean(passage)[:97]
        assert len(original)==97
        side=rnd.choice(("left","right"))
        keyword_alpha=rnd.choice(a)
        phase=rnd.randrange(26)
        ct=encrypt(original,keyword_alpha,side,phase)
        lab=f"PLANT_{i:02d}"
        lines.append(f"{lab}\t{ct}\n")
        truth[lab]={"plaintext":original,"keyword_side":side,
                    "keyword_alphabet":keyword_alpha,"right_initial_phase":phase}
    write_new(inputpath,"".join(lines))
    write_new(truthpath,json.dumps(truth,sort_keys=True,indent=2)+"\n")
    print("R56 generated 20 fresh sealed ciphertext-only synthetic controls")
def target(cipherpath,inputpath):
    raw=Path(cipherpath).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    original=raw.decode("ascii").strip()
    assert len(original)==97 and all(ch in AZ for ch in original)
    rnd=random.Random(560070)
    seen={original}
    lines=[f"K4\t{original}\n"]
    for i in range(12):
        letters=list(original)
        rnd.shuffle(letters)
        x="".join(letters)
        assert x not in seen and sorted(x)==sorted(original)
        seen.add(x)
        lines.append(f"NULL_{i:02d}\t{x}\n")
    write_new(inputpath,"".join(lines))
    print("R56 original ciphertext and frequency-preserving nulls prepared with no clues")
if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="controls":
        controls(sys.argv[2],sys.argv[3],sys.argv[4])
    elif len(sys.argv)==4 and sys.argv[1]=="target":
        target(sys.argv[2],sys.argv[3])
    else:raise SystemExit("usage prepare.py controls WORDS.tsv INPUT.tsv TRUTH.json | target K4.txt INPUT.tsv")
