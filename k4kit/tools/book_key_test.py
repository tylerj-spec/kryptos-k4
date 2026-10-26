#!/usr/bin/env python3
"""Outputs go to the current directory. Running-key test of a whole book against K4 (Claude R29; written for Carter & Mace 1923 vol. I, ledger L101).
python3 -I book_key_test.py BOOK.txt [--anchor-phrase PHRASE] [--search N]

- Text normalisation: letters A-Z only (hyphens, punctuation, digits and spaces dropped). Lines that look like running
  heads (all capitals, under 60 characters, repeated 5+ times) are removed first; the count is reported.
- Oracle (key_oracle.possible, both alphabets free; sign de-duplicated per L92): every 97-letter window, forward and
  reversed text, key letters numbered A-Z or KRYPTOS.
- Null: the same scan on 20 letter-shuffled copies of the book (same letter counts), giving the pass count expected
  for this book's letters by chance.
- --anchor-phrase: also report the window offsets nearest the K3 source passage (e.g. "CANYOUSEEANYTHING").
- --search N: run solver_s2k (64 x 40,000) on the first N passes ranked by closeness to the anchor phrase (or by
  offset), plus 20 random oracle-passing keys as a wrong-key calibration. Candidate rule as R28C: W > -114.9 and
  the text replicates with new seeds."""
import collections
import json
import random
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from k4common import ANCH, AZ, BIN, DATA, K4, KRY, MASK  # noqa: E402
from key_oracle import possible  # noqa: E402
args = sys.argv[1:]
book = Path(args[0])
phrase = args[args.index("--anchor-phrase") + 1] if "--anchor-phrase" in args else None
nsearch = int(args[args.index("--search") + 1]) if "--search" in args else 0

raw = book.read_text(errors="replace").splitlines()
heads = collections.Counter(ln.strip() for ln in raw if ln.strip() and ln.strip().upper() == ln.strip()
                            and len(ln.strip()) < 60 and re.search("[A-Z]", ln))
drop = {h for h, n in heads.items() if n >= 5}
text = re.sub("[^A-Z]", "", "\n".join(ln for ln in raw if ln.strip() not in drop).upper())
print(f"book: {book.name}; {len(text):,} letters after removing {len(drop)} repeated running heads")


def scan(s, keep=False):
    found, n = [], 0
    for direction, ss in (("fwd", s), ("rev", s[::-1])):
        for numname, alpha in (("AZ", AZ), ("KRY", KRY)):
            v = [alpha.index(c) for c in ss]
            for off in range(len(v) - 96):
                n += 1
                k = v[off:off + 97]
                if possible(k):
                    found.append((direction, numname, off, k) if keep else None)
    return n, found


n, hits = scan(text, keep=True)
rng = random.Random(2828)
null = []
for _ in range(20):
    sh = list(text)
    rng.shuffle(sh)
    null.append(len(scan("".join(sh))[1]))
null.sort()
print(f"oracle: {len(hits)} passes in {n:,} windows; 20 letter-shuffled copies: median {null[10]}, max {null[-1]} "
      f"-> {sum(x >= len(hits) for x in null)}/20 reach the book's count")
pos = text.find(phrase) if phrase else -1
if phrase:
    print(f"anchor phrase {'found at letter ' + str(pos) if pos >= 0 else 'NOT found'}")


def dist(h):
    d, _, off, _ = h
    start = off if d == "fwd" else len(text) - 97 - off
    return abs(start - pos) if pos >= 0 else start


hits.sort(key=dist)
json.dump([dict(direction=d, numbering=a, offset=o, near_phrase=dist((d, a, o, k))) for d, a, o, k in hits],
          open(Path.cwd() / (book.stem + ".oracle_passes.json"), "w"), indent=1)
if nsearch:
    lines = [(f"BOOK:{d}/{a}/off{o}", k) for d, a, o, k in hits[:nsearch]]
    c = 0
    while c < 20:
        k = [rng.randrange(26) for _ in range(97)]
        if possible(k):
            lines.append((f"NULL:{c}", k))
            c += 1
    out = [f"{lab} {''.join(chr(65 + x) for x in k)} {K4} {MASK} {random.Random(lab).randrange(1, 2 ** 63)}" for lab, k in lines]
    Path("book_in.txt").write_text("\n".join(x + " -" for x in out) + "\n")
    subprocess.run([str(BIN / "solver_s2kp"), str(DATA / "word_model_orth.tsv"), str(DATA / "quad_log10.f32"),
                    "book_in.txt", "book_out.jsonl", "64", "40000", "0.05", "0"], check=True)
    best = {}
    for ln in open("book_out.jsonl"):
        r = json.loads(ln)
        if r["id"] not in best or r["W"] > best[r["id"]]["W"]:
            best[r["id"]] = r
    nb = max(r["W"] for k, r in best.items() if k.startswith("NULL"))
    print(f"wrong-key calibration best W {nb:.2f}; book passes (best 10):")
    for r in sorted((r for k, r in best.items() if k.startswith("BOOK")), key=lambda r: -r["W"])[:10]:
        print(f"   {r['W']:8.2f} {r['id']} {r['plaintext']}" + ("   <-- above -114.9: replicate" if r["W"] > -114.9 else ""))
