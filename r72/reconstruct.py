#!/usr/bin/env python3
"""R72 reconstruction of Sanborn's documented sheet operations (no K4 decryption; no published K4 letters).
  A. K3 positive control: the worksheets show the plaintext written in rows of 42 (a 42-wide x 8-high sheet), turned a
     quarter turn, written in rows of 14 (a 14-wide x 24-high sheet) and turned again. Verify that this reproduces all
     336 K3 ciphertext letters from the K3 plaintext, list every width pair that gives the same result, and write the
     exact index map with both sheets' cell coordinates.
  B. Lemma: one quarter turn of a sheet of n = h x w cells (write rows of width w, read columns) is a decimation of
     1-based positions modulo n + 1: anticlockwise j -> w*j, clockwise j -> -w*j. Two turns multiply. Checked for every
     whole-grid sheet of 336 and of 98 cells.
  C. Fabrication: K3 (336) + separator (1) + K4 (97) = 434 = 14 x 31 places K4 at row 11 col 27 onward: 4 + 31+31+31.
  D. The same documented procedure on a K4-sized whole sheet: 97 is prime, so no whole sheet holds K4 alone; with one
     extra cell (the carved separator, or a blank) the sheet is 98 = 14 x 7 = 2 x 49 (14 rows, as K3's 14 x 24 sheet).
     List every distinct double-turn ordering of a 98-cell sheet. Definitions only; nothing is applied to K4 here.
Usage: python3 -I r72/reconstruct.py   (writes r72/data/K3_INDEX_MAP.tsv and r72/data/SHEET98_ORDERINGS.tsv)"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
K123_CT = ROOT / "archive/2026-10-27_solver_and_carter_excerpts/source_excerpts/cia_k1k3_cipher_drop_q.txt"
K123_PT = ROOT / "k4kit/data/k1k3_plaintext.txt"
K4_CT = ROOT / "r39/ic_gate/k4_ciphertext.txt"
K4_SHA256 = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"


def turn(n, w, clockwise):
    """Write positions 0..n-1 in rows of width w; read columns (clockwise: bottom to top, left to right;
    anticlockwise: top to bottom, right to left). Returns out with out[j] = input index at output position j."""
    rows = [list(range(i, min(i + w, n))) for i in range(0, n, w)]
    out = []
    for c in range(w):
        cc = c if clockwise else w - 1 - c
        for r in (range(len(rows) - 1, -1, -1) if clockwise else range(len(rows))):
            if cc < len(rows[r]):
                out.append(rows[r][cc])
    return out


def compose(p, q):
    """Apply p, then q: out[j] = p[q[j]]."""
    return [p[i] for i in q]


def decimation(perm):
    """k with perm[j] + 1 == k * (j + 1) mod (n + 1) for all j, or None."""
    n, m = len(perm), len(perm) + 1
    ks = [k for k in range(1, m) if all((perm[j] + 1 - k * (j + 1)) % m == 0 for j in range(n))]
    return ks[0] if len(ks) == 1 else None


def main():
    out = {}
    ct3 = K123_CT.read_text().strip()[-336:]
    pt3 = K123_PT.read_text().strip()[-336:]
    assert ct3.startswith("ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIA") and pt3.startswith("SLOWLYDESPARATLY")
    # A. K3
    k3 = compose(turn(336, 42, True), turn(336, 14, True))
    assert "".join(pt3[i] for i in k3) == ct3, "K3 not reproduced"
    pairs = []
    for w1 in range(2, 169):
        for w2 in range(2, 169):
            for cw in (True, False):
                if 336 % w1 == 0 and 336 % w2 == 0 and compose(turn(336, w1, cw), turn(336, w2, cw)) == k3:
                    pairs.append([w1, w2, "CW" if cw else "CCW"])
    out["K3"] = {"reproduced": True, "documented": "rows of 42 (42x8), clockwise turn, rows of 14 (14x24), clockwise turn",
                 "decimation_mod_337": decimation(k3), "inverse_mod_337": pow(decimation(k3), -1, 337),
                 "equivalent_width_pairs": pairs}
    s1 = turn(336, 42, True)
    lines = ["ct_pos\tpt_pos\tletter\tsheet1_row_of_8\tsheet1_col_of_42\tsheet2_row_of_24\tsheet2_col_of_14"]
    for j, i in enumerate(k3):
        mid = s1.index(i)                    # position after the first turn
        lines.append(f"{j}\t{i}\t{pt3[i]}\t{i // 42}\t{i % 42}\t{mid // 14}\t{mid % 14}")
    (ROOT / "r72/data/K3_INDEX_MAP.tsv").write_text("\n".join(lines) + "\n")
    # B. lemma
    lemma = {}
    for n in (336, 98):
        for w in [w for w in range(2, n) if n % w == 0]:
            a, c = decimation(turn(n, w, False)), decimation(turn(n, w, True))
            assert a == w and c == (n + 1 - w), (n, w, a, c)
        lemma[n] = "checked: anticlockwise = x w, clockwise = x (-w) mod n+1, for every whole-grid width"
    out["lemma"] = lemma
    # C. fabrication
    raw = K4_CT.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == K4_SHA256
    k4 = raw.decode().strip()
    cells = ct3 + "?" + k4
    assert len(cells) == 434 == 14 * 31
    rows = [cells[r * 31:(r + 1) * 31] for r in range(14)]
    k4_rows = [len([c for c in range(31) if 337 <= r * 31 + c]) for r in range(14)]
    out["panel_14x31"] = {"K4_start_row_col": divmod(337, 31), "K4_cells_per_row": [x for x in k4_rows if x],
                          "row_11_text": rows[10]}
    assert [x for x in k4_rows if x] == [4, 31, 31, 31]
    # D. 98-cell sheet orderings
    seen = {}
    for w1 in (2, 7, 14, 49):
        for w2 in (2, 7, 14, 49):
            for cw in (True, False):
                p = compose(turn(98, w1, cw), turn(98, w2, cw))
                seen.setdefault(tuple(p), []).append(f"{w1}x{w2}/{'CW' if cw else 'CCW'}")
    rows98 = ["k_mod_99\tsheet_sequences\tordering(out[j] = input index at output position j, 0-based)"]
    ks = []
    for p, names in seen.items():
        k = decimation(list(p))
        ks.append(k)
        rows98.append(f"{k}\t{' '.join(names)}\t{','.join(map(str, p))}")
    (ROOT / "r72/data/SHEET98_ORDERINGS.tsv").write_text("\n".join(rows98) + "\n")
    out["sheet98"] = {"distinct_orderings": len(seen), "k_mod_99": sorted(ks),
                      "note": "every double turn of a 98-cell sheet is 'take every k-th cell mod 99'; inverses included"}
    (ROOT / "r72/data/RECONSTRUCTION.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "K3"} | {"K3": {x: out["K3"][x] for x in
          ("reproduced", "decimation_mod_337", "inverse_mod_337")}, "K3_equivalent_pairs": len(pairs)}, indent=1))


if __name__ == "__main__":
    main()
