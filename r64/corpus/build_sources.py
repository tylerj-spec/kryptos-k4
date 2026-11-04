#!/usr/bin/env python3
"""R64 control sources (generic; no K4 data). Fresh texts for the R64 hidden tests, none of them used by R59/R63:
  English plaintext for the holdout  : The Call of the Wild (PG 215) + The Hound of the Baskervilles (PG 2852)
  German key, literary, OLD spelling : Kafka, Die Verwandlung (PG 22367, 1915)   -> development only
                                       Mann, Der Tod in Venedig (PG 12108, 1912) -> holdout only
  The German books are pre-1996 orthography ("daß") and a different genre from R63's Europarl training text, so they
  test whether R63's GERMAN key model works outside its training domain (ChatGPT dossier, PR #45/#46 request).
  Normalisation: R63's G-DE1 rule (Ä->AE, Ö->OE, Ü->UE, ß->SS, then A-Z only), identical to r63/corpus/build_keys.py.
Also writes the clock RING sequence: the 24 faces of r49/prior_photo_360_chart.json in UTC-offset order, the names of
each face (upper cell then lower cell) in chart order, extracted exactly as r63/corpus/build_keys.py extracts the
vocabulary. A ring-walk key reads this sequence from a start letter, wrapping around (out-of-distribution for the
CLOCK model, which was trained on random name orders).
Usage: build_sources.py fetch RAW_DIR           (downloads; checks sha256)
       build_sources.py build RAW_DIR OUT_DIR   (-> hold_pt.txt, de_lit_dev.txt, de_lit_hold.txt, clock_ring.txt)"""
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r63/corpus"))
from build_keys import az  # noqa: E402  (R63 normalisation, unchanged)

BASE = "https://raw.githubusercontent.com/GITenberg/{repo}/master/{file}"
# repo, file, sha256 of the downloaded bytes, encoding, role
BOOKS = [
    ("The-Call-of-the-Wild_215", "215-0.txt", "7b3e855dbc4e9833b0281a0bc1d527379d85c14f8dfb389ef916022d6e4d888c", "utf-8", "hold_pt"),
    ("The-Hound-of-the-Baskervilles_2852", "2852-0.txt", "c8a61868388cafca2c76d1d82ee610d24b2bb09913ba6da936c4aca94eb1d1e4", "utf-8", "hold_pt"),
    ("Die-Verwandlung_22367", "22367-8.txt", "fe91c871104780ce5a8fe3e12e79b757f6fb5ffa28ed83d6186e618fb3bf344a", "latin-1", "de_lit_dev"),
    ("Der-Tod-in-Venedig_12108", "12108-8.txt", "5543be6892a1a8d4b2c5e944abb5b1ff3cc82c8ecc2e91830ac590583d11a579", "latin-1", "de_lit_hold"),
]
START = re.compile(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG", re.I)
END = re.compile(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", re.I)


def body(raw, enc):
    lines = raw.decode(enc).lstrip("﻿").splitlines()
    s = next(i for i, l in enumerate(lines) if START.search(l))
    e = next(i for i, l in enumerate(lines) if END.search(l))
    assert s < e
    return "\n".join(lines[s + 1:e])


def clock_ring():
    d = json.loads((ROOT / "r49/prior_photo_360_chart.json").read_text())
    names = []
    for f in sorted(d["faces"], key=lambda f: f["utc_offset"]):
        for cell in (f["upper_original_chart_cell"], f["lower_original_chart_cell"]):
            for m in re.findall(r"[A-ZÄÖÜ][A-ZÄÖÜ\- ]{2,}[A-ZÄÖÜ]", cell):
                for part in m.split(","):
                    if part.strip():
                        names.append(az(part))
    vocab = set((ROOT / "r63/data/clock_names.txt").read_text().split())
    assert all(n in vocab for n in names)
    return names


def main():
    mode, raw_dir = sys.argv[1], Path(sys.argv[2])
    if mode == "fetch":
        raw_dir.mkdir(parents=True, exist_ok=True)
        for repo, f, h, _, _ in BOOKS:
            p = raw_dir / f
            if not p.exists():
                with urllib.request.urlopen(BASE.format(repo=repo, file=f), timeout=60) as r:
                    p.write_bytes(r.read())
            print(repo, "ok" if hashlib.sha256(p.read_bytes()).hexdigest() == h else "HASH MISMATCH")
        return
    out = Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    roles = {}
    for repo, f, h, enc, role in BOOKS:
        raw = (raw_dir / f).read_bytes()
        if hashlib.sha256(raw).hexdigest() != h:
            raise SystemExit(f"hash mismatch: {repo}")
        text = body(raw, enc)
        letters = az(text) if role.startswith("de_") else "".join(c for c in text.upper() if "A" <= c <= "Z")
        roles.setdefault(role, []).append(letters)
    for role, parts in roles.items():
        s = "".join(parts)
        (out / f"{role}.txt").write_text(s + "\n")
        print(role, len(s))
    ring = clock_ring()
    (out / "clock_ring.txt").write_text("\n".join(ring) + "\n")
    print("clock ring", len(ring), "names,", sum(map(len, ring)), "letters")


if __name__ == "__main__":
    main()
