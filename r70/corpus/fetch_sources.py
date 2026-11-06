#!/usr/bin/env python3
"""R70 source acquisition. Downloads the archive.org OCR text (_djvu.txt) of each pinned scan through the
https://archive.org/stream/<item>/<file> page (the only archive.org host this environment allows), extracts the <pre>
block, and accepts it only if its SHA-1 equals the SHA-1 that archive.org's own metadata lists for that file (pinned
below), i.e. the bytes are exactly archive.org's file. Then writes RAW/<KEY>.djvu.txt and RAW/SOURCES.json
(item, file, sha1, sha256, bytes, retrieval time). Never invents a checksum: a mismatch is an error.
Usage: python3 -I fetch_sources.py RAW_DIR"""
import hashlib
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

# key: (archive.org item, OCR file, SHA-1 from https://archive.org/metadata/<item>, bibliographic record)
SOURCES = {
    "BERLIN_1912": ("berlinitsenviron00karl", "berlinitsenviron00karl_djvu.txt",
                    "60695e5b6a42bbf271eb54b9bb6822691c76c319",
                    "Karl Baedeker, Berlin and Its Environs: Handbook for Travellers, 5th English ed., Leipzig 1912"),
    "EGYPT_1908": ("00491772.5459.emory.edu", "00491772_5459_djvu.txt",
                   "05d0acc26ceed2417373ea5427725a87c1d93628",
                   "Karl Baedeker, Egypt and the Sudan: Handbook for Travellers, 6th ed., Leipzig 1908 (Emory scan)"),
    "MURRAY_1907": ("handbookforegyp00hallgoog", "handbookforegyp00hallgoog_djvu.txt",
                    "5b02a6ef23129c27c196d2f3481661bc833045cd",
                    "Handbook for Egypt and the Sudan (Murray's handbooks), London: Edward Stanford 1907 (Google scan)"),
    "COOK_1876": ("cookstouristsha07ltdgoog", "cookstouristsha07ltdgoog_djvu.txt",
                  "e83ff7f676cd95d4dc5bf6429c1d32b7ee341220",
                  "Cook's Tourists' Handbook for Egypt, the Nile, and the Desert, London 1876 (Google scan); "
                  "substitute: the 1897 edition is only on Google Books, which this environment cannot reach"),
    "BUDGE_1898": ("bookdeadanengli00budggoog", "bookdeadanengli00budggoog_djvu.txt",
                   "06eb6e349ef0a157079c73dd2ebe5f08c1ea76e1",
                   "E. A. Wallis Budge, The Book of the Dead: An English Translation of the Chapters, Hymns, etc., "
                   "of the Theban Recension, London: Kegan Paul 1898 (Google scan); substitute: the only full 1895 "
                   "Papyrus of Ani text on archive.org is an access-restricted 1967 reprint"),
}


def fetch(item, fname):
    url = f"https://archive.org/stream/{item}/{fname}"
    req = urllib.request.Request(url, headers={"User-Agent": "kryptos-k4-research/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        page = r.read().decode("utf-8")
    m = re.search(r"<pre[^>]*>(.*?)</pre>", page, re.S)
    if not m:
        raise SystemExit(f"no <pre> block: {url}")
    return url, html.unescape(m.group(1)).encode("utf-8")


def main():
    raw = Path(sys.argv[1])
    raw.mkdir(parents=True, exist_ok=True)
    rec = {}
    for key, (item, fname, sha1, bib) in SOURCES.items():
        url, b = fetch(item, fname)
        if hashlib.sha1(b).hexdigest() != sha1:
            raise SystemExit(f"{key}: sha1 mismatch against archive.org metadata ({hashlib.sha1(b).hexdigest()})")
        (raw / f"{key}.djvu.txt").write_bytes(b)
        rec[key] = {"item": item, "file": fname, "url": url, "metadata": f"https://archive.org/metadata/{item}",
                    "sha1": sha1, "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b), "bibliographic": bib,
                    "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        print(key, len(b), "bytes, sha1 matches archive.org metadata")
    (raw / "SOURCES.json").write_text(json.dumps(rec, indent=1) + "\n")


if __name__ == "__main__":
    main()
