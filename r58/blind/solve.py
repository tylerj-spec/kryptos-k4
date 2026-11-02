#!/usr/bin/env python3
"""R58 ciphertext-only full-sequence process+key identifier.
No K4 clues, known plaintext, clue positions, true control labels, or sealed data.
Inputs: exactly ID<TAB>97-uppercase-ciphertext, generic word TSV, generic quadgram model.
"""
from array import array
from pathlib import Path
import json, math, sys

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N = 97
TOP = 8
SCORE_THRESHOLD = -525.0
MARGIN_THRESHOLD = 10.0
EXTRA_KEYS = ("KRYPTOS", "PALIMPSEST", "ABSCISSA")
A = "".join(dict.fromkeys("KRYPTOS" + AZ))
assert len(A) == 26 and set(A) == set(AZ)
A_INDEX = {c: i for i, c in enumerate(A)}
QCOUNT = 26**4

def keys_from_model(filepath):
    data = []
    for line in Path(filepath).open(encoding="utf-8"):
        parts = line.split()
        if len(parts) < 2:
            continue
        w = parts[0]
        if not 5 <= len(w) <= 10 or not w.isascii() or not w.isalpha() or not w.isupper():
            continue
        try:
            val = float(parts[1])
        except ValueError:
            continue
        if math.isfinite(val):
            data.append((-val, w))
    data.sort()
    unique = []
    seen = set()
    for _, word in data:
        if word not in seen:
            unique.append(word)
            seen.add(word)
        if len(unique) == 64:
            break
    if len(unique) != 64:
        raise ValueError("not enough generic key words")
    return tuple(sorted(set(unique).union(EXTRA_KEYS)))

def physical_routes():
    sites = [(0, c) for c in range(27, 31)] + [
        (r, c) for r in (1, 2, 3) for c in range(31)
    ]
    assert len(sites) == N and len(set(sites)) == N
    indices = {cell: i for i, cell in enumerate(sites)}
    mapping = {}
    for cd in ("L", "R"):
        for rd in ("T", "B"):
            cs = range(31) if cd == "L" else range(30, -1, -1)
            rs = range(4) if rd == "T" else range(3, -1, -1)
            seq = [(r, c) for c in cs for r in rs if (r, c) in indices]
            mapping["COL_" + cd + rd] = tuple(indices[c] for c in seq)
    for start in ("L", "R"):
        seq = []
        for r in range(4):
            row = [x for x in sites if x[0] == r]
            reverse = (r % 2 == 1) == (start == "L")
            seq += row[::-1] if reverse else row
        mapping["SNAKE_" + start] = tuple(indices[c] for c in seq)
    assert len(mapping) == 6
    assert all(sorted(v) == list(range(N)) for v in mapping.values())
    return mapping

def poly_decrypt(ct, shift):
    return "".join(A[(A_INDEX[ch] - shift[i]) % 26] for i, ch in enumerate(ct))

def unroute(ct, perm):
    buf = [""] * N
    for i, source_idx in enumerate(perm):
        buf[source_idx] = ct[i]
    return "".join(buf)

def score_text(p, Q):
    vals = [ord(ch)-65 for ch in p]
    z = 0.0
    for i in range(N-3):
        a = ((vals[i]*26 + vals[i+1])*26 + vals[i+2])*26 + vals[i+3]
        z += Q[a]
    if not math.isfinite(z):
        raise ValueError("nonfinite model score")
    return z

def scores_model(path):
    data = Path(path).read_bytes()
    if len(data) != QCOUNT * 4:
        raise ValueError("quadgram model bytes mismatch")
    q = array("f")
    q.frombytes(data)
    if sys.byteorder != "little":
        q.byteswap()
    return q

def solve_one(id_, cipher, keys, routes, model):
    if not 1 <= len(id_) <= 32 or any(c not in AZ + "0123456789_" for c in id_):
        raise ValueError("bad opaque record ID")
    if len(cipher) != N or any(c not in AZ for c in cipher):
        raise ValueError("exactly 97 uppercase ciphertext letters required")
    shifts = {key: tuple(A_INDEX[key[i % len(key)]] for i in range(N)) for key in keys}
    all_candidates = []
    def record(label, word, route, p, mid):
        all_candidates.append((score_text(p, model), label, word, route, p, mid))
    for key in keys:
        record("V", key, "", poly_decrypt(cipher, shifts[key]), None)
    for route, perm in routes.items():
        record("T", "", route, unroute(cipher, perm), None)
    for route, perm in routes.items():
        inter = unroute(cipher, perm)
        for key in keys:
            record("VT", key, route, poly_decrypt(inter, shifts[key]), inter)
            other = poly_decrypt(cipher, shifts[key])
            record("TV", key, route, unroute(other, perm), other)
    expected = len(keys)*(1+2*len(routes)) + len(routes)
    if len(all_candidates) != expected:
        raise ValueError("method/key configurations not fully searched")
    all_candidates.sort(key=lambda x:(-x[0],x[1],x[2],x[3],x[4]))
    ranked = []
    for score, label, word, route, plain, mid in all_candidates[:TOP]:
        ranked.append({
            "family":label, "key":word or None, "route":route or None,
            "score":round(score, 8), "plaintext":plain,
            "first_reversed_intermediate":mid
        })
    best = all_candidates[0]
    runner = next((z for z in all_candidates[1:] if z[4] != best[4]), None)
    gap = max(0.0, best[0]-runner[0]) if runner else 0
    equiv_classes = {z[1] for z in all_candidates if z[4] == best[4]}
    found = best[0] >= SCORE_THRESHOLD and gap >= MARGIN_THRESHOLD and len(equiv_classes) == 1
    return {
        "id":id_, "searched":expected, "key_count":len(keys), "route_count":len(routes),
        "detected_family":best[1] if found else "ABSTAIN",
        "confidence_reason":"full_text_score_and_margin_passed" if found else (
            "observationally_aliased" if len(equiv_classes) > 1 else
            "insufficient_english_score_or_margin"
        ),
        "best_score":round(best[0], 8), "next_distinct_margin":round(gap, 8),
        "candidates":ranked
    }

def main():
    if len(sys.argv) != 5:
        raise ValueError("usage: solve.py ciphertext_only.tsv word_model.tsv quad.f32 OUTPUT.jsonl")
    input_path, wordfile, quadfile, outfile = sys.argv[1:]
    if Path(outfile).exists():
        raise FileExistsError("do not overwrite blind candidate outputs")
    keys = keys_from_model(wordfile)
    routes = physical_routes()
    model = scores_model(quadfile)
    records = []
    for line in Path(input_path).read_text(encoding="ascii").splitlines():
        fields = line.split("\t")
        if len(fields) != 2:
            raise ValueError("blind input requires exactly two TSV columns")
        records.append((fields[0], fields[1]))
    if not 1 <= len(records) <= 150 or len(set(i for i,_ in records)) != len(records):
        raise ValueError("zero, too many or duplicate blind records")
    with Path(outfile).open("x", encoding="ascii") as f:
        for i,(label,cipher) in enumerate(records):
            row = solve_one(label,cipher,keys,routes,model)
            f.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n")
            if (i+1)%20 == 0:
                print("R58 ciphertext-only complete:",i+1,"/",len(records),file=sys.stderr)
    print("R58 blind complete",len(records),"records,",
          len(keys)*(1+2*len(routes))+len(routes),"searches/record")
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("R58 BLIND FAILURE:",type(e).__name__,str(e),file=sys.stderr)
        sys.exit(1)
