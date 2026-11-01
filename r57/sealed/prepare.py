#!/usr/bin/env python3
"""R57 independent encrypted synthetic controls; never mounted in blind solver."""
from pathlib import Path
import hashlib,json,math,random,sys

AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N=97
SHA="2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
PASSAGES=(
 "The astronomer carefully adjusted the telescope and recorded the faint glow of a distant planet as the evening clouds drifted slowly over the observatory.",
 "Every visitor entering the old fortress followed a narrow staircase toward the upper chamber where faded murals covered the walls above the stone doorway.",
 "In a quiet studio the violin maker selected a strip of seasoned wood and shaped the curved bridge that would support the instrument strings.",
 "The small coastal village prepared for the annual festival by hanging bright banners across the streets and arranging wooden benches beside the harbor.",
 "Before leaving the camp the expedition leader checked the supply records and marked the next destination on a folded map beneath the lantern.",
 "The music teacher paused between rehearsals to explain how the rhythm changed when the melody shifted from one instrument to another across the orchestra.",
 "After a long journey the postal courier reached the mountain inn and delivered a packet of letters wrapped carefully in brown paper.",
 "The harbor pilot studied the current and guided the cargo vessel through a narrow channel bordered by rocks and shifting sandbanks.",
 "While the baker waited for the bread to rise the apprentice arranged rows of pastries on wooden trays and cleaned the flour from the workbench.",
 "Two naturalists collected samples near the marsh and carefully noted the colors and shapes of the insects discovered beneath fallen leaves.",
 "The village carpenter restored an antique chest using simple hand tools and polished the worn hinges until their brass surfaces began to shine.",
 "An unexpected rainfall forced the visiting scholars to gather beneath the library arcade where they continued discussing their latest discoveries.",
 "The old clock tower stood above a busy market square as merchants opened their stalls and greeted familiar customers arriving before dawn.",
 "Every evening the caretaker inspected the greenhouse windows and checked the temperature before securing the gate beside the quiet orchard.",
 "The students spent the afternoon measuring the length of the old stone bridge and sketching its arches in their notebooks for the history project.",
 "At the riverside workshop a mechanic examined a collection of tiny gears and searched for the missing spring that controlled the brass instrument.",
 "The traveler rested beside a small fountain and watched a procession of horses pass slowly through the ancient gate toward the central courtyard.",
 "In the attic an art collector discovered several forgotten canvases hidden behind wooden crates and carefully removed the dust from each frame.",
 "The mountaineer followed the ridge as far as the wooded pass before stopping to study the distant peaks outlined against the pale morning sky.",
 "A small crowd gathered in the town hall to hear the explorer describe unusual landscapes and the people encountered during a long voyage.",
)
def clean(s):return "".join(c for c in s.upper() if c in AZ)
def keys():
    return [(a,b,c,d) for a in range(26) if math.gcd(a,26)==1
            for b in range(26) for c in range(26) for d in range(26)
            if math.gcd((a*d-b*c)%26,26)==1]
def forward(p,a,b,c,d):
    assert len(p)==97
    out=[]
    for i in range(0,96,2):
        x=ord(p[i])-65;y=ord(p[i+1])-65
        out.append(chr(65+(a*x+b*y)%26))
        out.append(chr(65+(c*x+d*y)%26))
    out.append(chr(65+(a*(ord(p[96])-65)+b*23)%26))
    return "".join(out)
def write_new(p,txt):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("x",encoding="ascii") as f:f.write(txt)
def controls(inp,truth):
    assert len(PASSAGES)==20
    candidate_keys=keys()
    assert len(candidate_keys)==97344
    rng=random.Random(570057)
    rows=[];known={}
    for i,msg in enumerate(PASSAGES):
        plain=clean(msg)[:N]
        assert len(plain)==97
        k=rng.choice(candidate_keys)
        ciphertext=forward(plain,*k)
        lab=f"PLANT_{i:02d}"
        rows.append(f"{lab}\t{ciphertext}\n")
        known[lab]={"plaintext":plain,"a":k[0],"b":k[1],"c":k[2],"d":k[3]}
    write_new(inp,"".join(rows))
    write_new(truth,json.dumps(known,sort_keys=True,indent=2)+"\n")
    print("R57: 20 fresh 97-letter synthetic ciphertexts; keys hidden")
def target(original_file,inp):
    blob=Path(original_file).read_bytes()
    assert hashlib.sha256(blob).hexdigest()==SHA
    original=blob.decode("ascii").strip()
    assert len(original)==97 and all(ch in AZ for ch in original)
    rng=random.Random(570070)
    seen={original};rows=[f"K4\t{original}\n"]
    for i in range(12):
        v=list(original);rng.shuffle(v);s="".join(v)
        assert s not in seen and sorted(s)==sorted(original)
        seen.add(s);rows.append(f"NULL_{i:02d}\t{s}\n")
    write_new(inp,"".join(rows))
    print("R57 original ciphertext plus 12 nulls isolated")
if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="controls":controls(sys.argv[2],sys.argv[3])
    elif len(sys.argv)==4 and sys.argv[1]=="target":target(sys.argv[2],sys.argv[3])
    else:raise SystemExit("usage prepare.py controls IN.tsv TRUTH.json | target CANONICAL K4_INPUT.tsv")
