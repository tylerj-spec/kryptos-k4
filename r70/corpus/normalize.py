#!/usr/bin/env python3
"""R70 deterministic normalisation (fixed before any K4 run; no discretionary cleanup):
  UTF-8 decode -> Unicode NFKD -> uppercase -> keep only A-Z (everything else, including digits, punctuation, spaces,
  combining marks and letters NFKD leaves outside A-Z, is deleted). The whole OCR file is kept: front matter,
  advertisements, headers, index and OCR noise stay in the stream, in file order. One line per source.
Usage: python3 -I normalize.py RAW_DIR NORM_DIR   (RAW_DIR from fetch_sources.py; writes NORM_DIR/<KEY>.txt and
       NORM_DIR/MANIFEST.json with raw and normalised sha256 and letter counts)"""
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

KEYS = ("BERLIN_1912", "EGYPT_1908", "MURRAY_1907", "COOK_1876", "BUDGE_1898")


def norm(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text).upper() if "A" <= c <= "Z")


def main():
    raw, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    src = json.loads((raw / "SOURCES.json").read_text())
    man = {}
    for k in KEYS:
        b = (raw / f"{k}.djvu.txt").read_bytes()
        if hashlib.sha256(b).hexdigest() != src[k]["sha256"]:
            raise SystemExit(f"raw sha256 mismatch {k}")
        s = norm(b.decode("utf-8"))
        (out / f"{k}.txt").write_text(s + "\n")
        man[k] = {"raw_sha256": src[k]["sha256"], "raw_sha1": src[k]["sha1"], "item": src[k]["item"],
                  "norm_sha256": hashlib.sha256((s + "\n").encode()).hexdigest(), "letters": len(s)}
        print(k, len(s), man[k]["norm_sha256"])
    (out / "MANIFEST.json").write_text(json.dumps(man, indent=1) + "\n")


if __name__ == "__main__":
    main()
