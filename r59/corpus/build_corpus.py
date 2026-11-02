#!/usr/bin/env python3
"""R59 corpus builder (generic English; no K4 data). Verifies the pinned public-domain books, strips the Project
Gutenberg header/footer, keeps letters A-Z only, and writes one letters file per role.

Usage:
  python3 -I r59/corpus/build_corpus.py fetch RAW_DIR          # download the pinned books (raw.githubusercontent.com)
  python3 -I r59/corpus/build_corpus.py build RAW_DIR OUT_DIR [NLTK_DIR]
        # verify sha256, clean, write OUT_DIR/{train,dev_pt,dev_key,hold_pt,hold_key}.txt; NLTK_DIR holds the
        # brown/webtext/inaugural/state_union/gutenberg zips (extra training text only)
Roles never overlap:
  train    : 14 novels + Carter & Mace 1923 vol. I (r34/carter_az.txt) + NLTK Brown/webtext/inaugural/state_union/
             gutenberg extras -> language model only
  dev_pt / dev_key   : development plaintext / running-key sources (solver tuning)
  hold_pt / hold_key : sealed holdout sources (used only by r59/sealed/make_holdout.py after registration)
Raw books are downloaded data: keep RAW_DIR separate from code and run this script with python3 -I."""
import hashlib
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://raw.githubusercontent.com/GITenberg/{repo}/master/{file}"
# repo, file, sha256 of the downloaded bytes, role
BOOKS = [
    ("Moby-Dick--Or-The-Whale_2701", "2701-0.txt", "baf9b04fcf6e0008f30eaaa6697277751448c1070b20175e0082f28cbb161fd3", "train"),
    ("A-Tale-of-Two-Cities_98", "98-0.txt", "2fcfa071498b30724bd1bd714ba89e38477d632b86d74e87559f6259d3917e36", "train"),
    ("The-Adventures-of-Sherlock-Holmes_1661", "1661.txt", "2a0ce5568625a304f54fbb6bfdeeadf527a1437254b5f0e06b5a9e233d4784a2", "train"),
    ("Great-Expectations_1400", "1400-0.txt", "b58ce42c630e06314f2442d5937fa8a8556b6e3c5c16f4713c7332a4bb50b420", "train"),
    ("Dracula_345", "345.txt", "c802711470ddb2aaca81432fc101ed29c154e7c3d32df4172478695c33f68eae", "train"),
    ("Adventures-of-Huckleberry-Finn_76", "76-0.txt", "cd9931183257a850178225bd5e25e4f2df0cbac544dfe9a49cd0ea5a210c24d9", "train"),
    ("Jane-Eyre_1260", "1260.txt", "bc74b04ec70c9283323f5043f3305c4b08e70650a96ca5a9e1c5e5c5b4c0aa9a", "train"),
    ("Emma_158", "158-0.txt", "89b601ce13c21eca31766bdd1a554842fc9ecb7d3638cc769f41712a523e24cf", "train"),
    ("Little-Women_514", "514.txt", "b20d98130841548c2137476e18fb1fe3bc7d666202985cafa09b5e02e54f7d7f", "train"),
    ("Wuthering-Heights_768", "768.txt", "2ff1cd2fa12ecff82da679e889ca7645e132e7bcfd55768ea42a955abe12c1e1", "train"),
    ("Sense-and-Sensibility_161", "161.txt", "9109bd8aabe8f36d0814bd6f5afad1e278b1369d66c0d3846667f0659e119d27", "train"),
    ("Alice-s-Adventures-in-Wonderland_11", "11-0.txt", "49a0b2726606e1290ac03a63978fa1dd1bd38a8d805704d98265f393533ea094", "train"),
    ("Pride-and-Prejudice_1342", "1342-0.txt", "48e0522844402a86a3ea98f0947ba85ea54838db3c59022299298ed968a5a163", "train"),
    ("Frankenstein_84", "84-0.txt", "c29a4f56dd91aa894a3f17d5f96b356ccb499e3e2c5a27964de911845e39efab", "train"),
    ("The-Adventures-of-Tom-Sawyer_74", "74-0.txt", "b1cd5782db259c00bc1a8fbb58238f285e40828cc858c1343f74a0a75157cc91", "dev_pt"),
    ("The-Picture-of-Dorian-Gray_174", "174.txt", "0c9a2cbf188ca6534c60381b764ac37bf4594b16971aea5cc8263e83b9ce9a05", "dev_key"),
    ("The-War-of-the-Worlds_36", "36-0.txt", "0c9bea907452abd6e9a31d9152188ef5007f0e2d3e4a52d7a6a627a37616249f", "hold_pt"),
    ("Treasure-Island_120", "120-0.txt", "0fee2fef1b2ffde22e2c962bd8bc2b75ea1ae9b02b3fe85ef08d44f4cc1bb2de", "hold_pt"),
    ("Heart-of-Darkness_219", "219-0.txt", "b5aad152564fa9bdd92d71434134a26fbc3146afdeabd6cc7a09e723dfb0a414", "hold_key"),
    ("The-Time-Machine_35", "35-0.txt", "0eb70818a4c7e2e04f91be807bad37ca5c1475cd51cec2a7b620c4db2b595ce4", "hold_key"),
]
CARTER = ROOT / "r34/carter_az.txt"
# Extra TRAINING text (modern American English and more prose), read directly from the NLTK data zips
# (https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/<name>.zip).
NLTK_URL = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/{name}.zip"
NLTK = {
    "brown": "9b275f9b3b95d7bd66ccfb7cd259f445a13bbe5d1f4107aba09fd3e8364bafa6",       # 1961 American English, tagged
    "webtext": "9e32dbae4879464b8f420a0dc721855bb26167b720d7695588d2ca2aeadf501a",
    "inaugural": "b3b2cb7bd82697b58ff79c75af20ab963810d191a8c3d1f7c240f98e5d27a895",
    "state_union": "366c1dc82b2abf896f42b2ec50ba802a0141a29f75d29ca48a7a243ce5bfbe8d",
    "gutenberg": "2d3c3ab548c653944310f37f536443ec85d0a0ad855fcae217a0c9efdce2d611",
}
# NLTK gutenberg files already present above (as full books) are skipped to avoid double weight.
NLTK_SKIP = {"austen-emma.txt", "austen-sense.txt", "carroll-alice.txt", "melville-moby_dick.txt"}
START = re.compile(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG")
END = re.compile(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG")


def body_letters(raw):
    lines = raw.decode("utf-8", errors="replace").splitlines()
    s = next(i for i, l in enumerate(lines) if START.search(l))
    e = next(i for i, l in enumerate(lines) if END.search(l))
    assert s < e
    return "".join(c for c in "\n".join(lines[s + 1:e]).upper() if "A" <= c <= "Z")


def main():
    mode, raw_dir = sys.argv[1], Path(sys.argv[2])
    if mode == "fetch":
        raw_dir.mkdir(parents=True, exist_ok=True)
        for repo, f, h, _ in BOOKS:
            p = raw_dir / f"{repo}.txt"
            if not p.exists():
                with urllib.request.urlopen(BASE.format(repo=repo, file=f), timeout=60) as r:
                    p.write_bytes(r.read())
            print(repo, "ok" if hashlib.sha256(p.read_bytes()).hexdigest() == h else "HASH MISMATCH")
        return
    out = Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    roles = {}
    for repo, _, h, role in BOOKS:
        raw = (raw_dir / f"{repo}.txt").read_bytes()
        if hashlib.sha256(raw).hexdigest() != h:
            raise SystemExit(f"hash mismatch: {repo}")
        roles.setdefault(role, []).append((repo, body_letters(raw)))
    roles["train"].append(("Carter_Mace_1923_vol1", "".join(c for c in CARTER.read_text() if "A" <= c <= "Z")))
    if len(sys.argv) > 4:   # NLTK_DIR holding the five zips
        import zipfile
        nd = Path(sys.argv[4])
        for name, h in NLTK.items():
            zb = (nd / f"{name}.zip").read_bytes()
            if hashlib.sha256(zb).hexdigest() != h:
                raise SystemExit(f"hash mismatch: {name}.zip")
            import io
            z = zipfile.ZipFile(io.BytesIO(zb))
            parts = []
            for m in sorted(z.namelist()):
                base = m.rsplit("/", 1)[-1]
                if m.endswith("/") or base in ("README", "CONTENTS", "cats.txt", "cats.csv") or base in NLTK_SKIP:
                    continue
                txt = z.read(m).decode("latin-1")
                if name == "brown":   # "word/tag" tokens -> word
                    txt = " ".join(tok.rsplit("/", 1)[0] for tok in txt.split())
                parts.append("".join(c for c in txt.upper() if "A" <= c <= "Z"))
            roles["train"].append((f"nltk_{name}", "".join(parts)))
    for role, items in roles.items():
        # books joined with a 'separator' of nothing: n-gram counts across a join are negligible (< 20 of ~8M)
        text = "".join(t for _, t in items)
        (out / f"{role}.txt").write_text(text + "\n")
        print(role, len(text), [(r, len(t)) for r, t in items])


if __name__ == "__main__":
    main()
