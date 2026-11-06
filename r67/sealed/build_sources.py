#!/usr/bin/env python3
"""Build exactly pinned R67 source streams from original public-domain archives.

Usage: python3 r67/sealed/build_sources.py BOOK_DIR EUROPARL_ZIP OUTDIR
BOOK_DIR must contain 215-0.txt and 2852-0.txt as pinned below.
EUROPARL_ZIP is NLTK europarl_raw.zip pinned by r63/corpus/build_keys.py.
No download, model fitting, K4 plaintext or candidate generation occurs here.
"""
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

BOOKS = (
    ("The Call of the Wild", "215-0.txt",
     "7b3e855dbc4e9833b0281a0bc1d527379d85c14f8dfb389ef916022d6e4d888c"),
    ("The Hound of the Baskervilles", "2852-0.txt",
     "c8a61868388cafca2c76d1d82ee610d24b2bb09913ba6da936c4aca94eb1d1e4"),
)
EUROPARL_SHA256 = "ad553e177baac263840c10980e6f3e76d5d15f7f7a078bd98520b36edb69b27c"
START = re.compile(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG", re.I)
END = re.compile(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", re.I)
AZ = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, expected):
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise SystemExit("source hash mismatch: " + str(path))
    return raw


def text_body(raw):
    lines = raw.decode("utf-8").lstrip("\ufeff").splitlines()
    begin = next((i for i, s in enumerate(lines) if START.search(s)), None)
    end = next((i for i, s in enumerate(lines) if END.search(s)), None)
    if begin is None or end is None or begin >= end:
        raise SystemExit("Gutenberg body markers not found")
    return "\n".join(lines[begin+1:end])


def en_az(text):
    return "".join(c for c in text.upper() if c in AZ)


def de_az(text):
    # Exact R63 G-DE1 transliteration before A-Z filtering.
    s = text.upper().replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE").replace("ß", "SS")
    return "".join(c for c in s if c in AZ)


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    book_dir, europarl, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    if out.exists():
        raise SystemExit("refusing to overwrite source directory")
    en_sections = []
    raw_records = []
    for title, name, expected in BOOKS:
        raw = checked(book_dir / name, expected)
        en_sections.append(en_az(text_body(raw)))
        raw_records.append({"title": title, "filename": name, "sha256": expected,
                            "origin": "GITenberg raw text pinned by r64/corpus/build_sources.py"})
    zbytes = checked(europarl, EUROPARL_SHA256)
    archive = zipfile.ZipFile(io.BytesIO(zbytes))
    members = sorted(m for m in archive.namelist()
                     if m.startswith("europarl_raw/german/") and not m.endswith("/"))
    if len(members) != 10:
        raise SystemExit("expected exactly 10 German Europarl files")
    german = de_az(archive.read(members[9]).decode("utf-8"))
    english = "".join(en_sections)
    out.mkdir(parents=True)
    contents = {"hold_pt.txt": english + "\n", "de_hold.txt": german + "\n"}
    normalized = {}
    for name, val in contents.items():
        dest = out / name
        dest.write_bytes(val.encode("ascii"))
        normalized[name] = {"sha256": sha(dest.read_bytes()), "letters": len(val.strip()),
                            "role": "out_of_training"}
    manifest = {
        "experiment": "R67",
        "english_books": raw_records,
        "german_archive_sha256": EUROPARL_SHA256,
        "german_member": members[9],
        "german_training_split": "sorted members 0-7 train, 8 dev, 9 holdout",
        "english_training_split": "R64 new holdout books, not R59 training/NTLK texts",
        "normalization": {"English": "r64/corpus/build_sources.py uppercase and A-Z only",
                          "German": "r63/corpus/build_keys.py G-DE1"},
        "normalized": normalized,
        "builder_sha256": sha(Path(__file__).read_bytes()),
    }
    (out / "SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("R67 sources verified: English", len(english), "German", len(german))
    print(json.dumps(normalized, indent=2))


if __name__ == "__main__":
    main()
