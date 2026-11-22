#!/usr/bin/env python3
"""Convert public supplied-structure synthetic records to archived R68 rows.
Reads only public ciphertext/metadata, never source books or private truth.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reference as R

rows = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line]
assert 0 < len(rows) <= 240 and len({r["id"] for r in rows}) == len(rows)
with Path(sys.argv[2]).open("x") as out:
    for r in rows:
        assert set(r) == {"id", "arm", "ciphertext", "lag", "convention", "path", "path_index", "permutation", "model"}
        assert r["arm"] == "PTAK_R68" and len(r["ciphertext"]) == 97
        assert set(r["ciphertext"]) <= set(R.AZ) and sorted(r["permutation"]) == list(range(97))
        assert 13 <= r["lag"] <= 24
        rid = f'{r["id"]}__{r["path_index"]}__{r["model"]}'
        y = R.unpermute(r["ciphertext"], r["permutation"])
        layout = "I" if r["model"] == "M1" else ",".join(str(x) for x in r["permutation"])
        a, b, op = r["convention"]
        conv = f"{a}/{b}_{op}"
        out.write(f'{rid}\t{y}\t{layout}\t{conv}\t{r["lag"]}\n')
