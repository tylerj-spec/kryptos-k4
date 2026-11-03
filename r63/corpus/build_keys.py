#!/usr/bin/env python3
"""R63 key models (generic; no K4 data). Two non-English key sources for the running-key solver:
  CLOCK  : any sequence of World Clock (Weltzeituhr, Alexanderplatz) city names, any order, repeats allowed.
           Vocabulary = every name in the photo-derived R23/R49 chart (r49/prior_photo_360_chart.json, all eras), letters
           only (spaces/hyphens removed, U-umlaut -> UE), plus declared additions: ROM (missed by the 4-letter
           extraction), MEXIKOSTADT (press-reported later form), BRUSSEL (umlaut dropped), WELTZEITUHR, URANIA,
           ALEXANDERPLATZ. Written to r63/data/clock_names.txt.
  GERMAN : modern German prose (NLTK europarl_raw, German part; ae/oe/ue/ss transliteration).
Usage: build_keys.py clock OUT_DIR                      -> clock_names.txt (committed copy in r63/data), clock_train.txt,
                                                           clock_words.tsv
       build_keys.py german EUROPARL_ZIP OUT_DIR        -> de_train.txt (files 1-8), de_dev.txt (file 9),
                                                           de_hold.txt (file 10), de_words.tsv (training words)
Word files use the ORTH layout: WORD log10p -1e+100."""
import hashlib
import io
import json
import math
import random
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EUROPARL_SHA256 = "ad553e177baac263840c10980e6f3e76d5d15f7f7a078bd98520b36edb69b27c"
ADD = ["ROM", "MEXIKOSTADT", "BRUSSEL", "WELTZEITUHR", "URANIA", "ALEXANDERPLATZ"]


def az(s):
    s = s.upper().replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE").replace("ß", "SS")
    return "".join(c for c in s if "A" <= c <= "Z")


def clock_names():
    d = json.loads((ROOT / "r49/prior_photo_360_chart.json").read_text())
    names = set()
    for f in d["faces"]:
        for cell in (f["upper_original_chart_cell"], f["lower_original_chart_cell"]):
            for m in re.findall(r"[A-ZÄÖÜ][A-ZÄÖÜ\- ]{2,}[A-ZÄÖÜ]", cell):
                for part in m.split(","):
                    if part.strip():
                        names.add(az(part))
    names |= set(ADD)
    return sorted(names)


def main():
    mode = sys.argv[1]
    if mode == "clock":
        out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
        names = clock_names()
        (out / "clock_names.txt").write_text("\n".join(names) + "\n")
        rng = random.Random(63000)
        parts, n = [], 0
        while n < 5_000_000:
            w = names[rng.randrange(len(names))]
            parts.append(w); n += len(w)
        (out / "clock_train.txt").write_text("".join(parts) + "\n")
        lp = math.log10(1 / len(names))
        (out / "clock_words.tsv").write_text("".join(f"{w} {lp:.6f} -1e+100\n" for w in names))
        print(f"clock: {len(names)} names; synthetic training text {n} letters")
    elif mode == "german":
        zb = Path(sys.argv[2]).read_bytes()
        if hashlib.sha256(zb).hexdigest() != EUROPARL_SHA256:
            raise SystemExit("europarl_raw.zip hash mismatch")
        out = Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(zb))
        files = sorted(m for m in z.namelist() if m.startswith("europarl_raw/german/") and not m.endswith("/"))
        assert len(files) == 10
        texts = [z.read(m).decode("utf-8") for m in files]
        roles = {"de_train": texts[:8], "de_dev": texts[8:9], "de_hold": texts[9:10]}
        for role, ts in roles.items():
            letters = "".join(az(t) for t in ts)
            (out / f"{role}.txt").write_text(letters + "\n")
            print(role, len(letters))
        cnt = Counter(w for t in roles["de_train"] for w in (az(x) for x in re.split(r"[^A-Za-zÄÖÜäöüß]+", t)) if w)
        tot = sum(cnt.values())
        (out / "de_words.tsv").write_text("".join(f"{w} {math.log10(c / tot):.6f} -1e+100\n"
                                                 for w, c in cnt.most_common(60000) if len(w) <= 24))
        print("german words", min(60000, len(cnt)), "of", len(cnt))


if __name__ == "__main__":
    main()
