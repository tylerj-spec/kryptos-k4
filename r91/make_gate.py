#!/usr/bin/env python3
"""Sealed fresh control generation. Never import this file from candidate code."""
import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference as R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--training", required=True)
    ap.add_argument("--public", required=True)
    ap.add_argument("--private", required=True)
    args = ap.parse_args()
    public, private = Path(args.public), Path(args.private)
    public.mkdir(exist_ok=False, parents=True)
    private.mkdir(exist_ok=False, parents=True)
    spec = json.loads((HERE / "SOURCES.json").read_text())
    source_texts = []
    for source in spec["sources"]:
        raw = (Path(args.sources) / source["file"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source["sha256"]
        lines = raw.decode("utf-8").splitlines()
        start = next(i for i,l in enumerate(lines) if re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG", l))
        end = next(i for i,l in enumerate(lines) if re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", l))
        text = "".join(c for c in "\n".join(lines[start+1:end]).upper() if "A" <= c <= "Z")
        assert len(text) > 30000
        source_texts.append(text)
    training = Path(args.training).read_bytes()
    assert hashlib.sha256(training).hexdigest() == "871627e5fd2f84b4afa976516303098f437b5c339b7297db238fcd1ecb0e0434"
    training = training.decode()
    paths = [("ID", list(range(97)))]
    for line in (HERE / "routes.txt").read_text().splitlines():
        name, order, nums = line.split()
        assert order == "S_then_T"
        paths.append((name, list(map(int, nums.split(",")))))
    convs = [(a,b,op) for a in ("AZ","KRY") for b in ("AZ","KRY") for op in ("VIG","BEAU","VARB")]
    rng = random.Random(912211)
    used = [[] for _ in source_texts]
    plaintexts = set()
    rows_r82, rows_ptak, truth = [], [], {}

    def window(genre):
        text = source_texts[genre]
        for _ in range(100000):
            off = rng.randrange(500, len(text)-97-500)
            if any(abs(off-other)<97 for other in used[genre]):
                continue
            p = text[off:off+97]
            if p in plaintexts or p in training:
                continue
            plaintexts.add(p); used[genre].append(off)
            return p, off
        raise RuntimeError("fresh nonoverlapping source-window budget exhausted")

    def key(length):
        for _ in range(100000):
            k = "".join(rng.choice(R.AZ) for _ in range(length))
            if all(k != (k[:d]*(length//d)) for d in range(1,length) if length%d==0):
                return k
        raise RuntimeError("primitive-key draw budget exhausted")

    cell = 0
    for m in (3,4,5,7,9,12):
        for w in (m,m+2,31):
            for j in range(20):
                genre = (cell+j)%3; p, off = window(genre); k = key(m)
                rid = f"L_{len(rows_r82):03}"
                ct = R.linked_encrypt(p,k,w)
                assert R.linked_decrypt(ct,k,w)==p
                rows_r82.append({"id":rid,"arm":"R82_LINKED","ciphertext":ct,"m":m,"w":w})
                truth[rid] = {"arm":"R82_LINKED","stratum":f"m{m}_w{w}","m":m,"w":w,"plaintext":p,
                              "key":k,"genre":spec["sources"][genre]["genre"],"source_file":spec["sources"][genre]["file"],"offset":off}
            cell += 1
    for lag in range(13,25):
        for j in range(20):
            genre = (lag+j)%3; p, off = window(genre); k = key(lag)
            pi = rng.randrange(len(paths)); name, perm = paths[pi]
            model = "M1" if name == "ID" else rng.choice(("M1","M2"))
            conv = rng.choice(convs); rid = f"P_{len(rows_ptak):03}"
            ct = R.ptak_encrypt(p,k,conv,perm,model)
            assert R.ptak_decrypt(ct,k,conv,perm,model)==p
            rows_ptak.append({"id":rid,"arm":"PTAK_R68","ciphertext":ct,"lag":lag,"convention":conv,
                              "path":name,"path_index":pi,"permutation":perm,"model":model})
            truth[rid] = {"arm":"PTAK_R68","stratum":f"L{lag}","lag":lag,"plaintext":p,"key":k,
                          "convention":conv,"path":name,"model":model,"genre":spec["sources"][genre]["genre"],
                          "source_file":spec["sources"][genre]["file"],"offset":off}
    rng.shuffle(rows_r82); rng.shuffle(rows_ptak)
    for name, rows in (("R82_INPUT.jsonl", rows_r82),("PTAK_INPUT.jsonl",rows_ptak)):
        (public/name).write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in rows))
    truth_bytes = (json.dumps(truth,indent=2,sort_keys=True)+"\n").encode()
    (private/"TRUTH.json").write_bytes(truth_bytes)
    digest = hashlib.sha256(truth_bytes).hexdigest()
    (public/"TRUTH_SHA256").write_text(digest+"\n")
    print(json.dumps({"r82_inputs":len(rows_r82),"ptak_inputs":len(rows_ptak),"truth_sha256":digest,
                      "source_counts":[len(x) for x in used],"training_exact_97_overlap":0,
                      "within_source_window_overlap":0}),flush=True)


if __name__ == "__main__":
    main()
