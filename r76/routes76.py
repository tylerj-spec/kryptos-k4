"""R76 route sets (no K4 data). A route is a permutation p of 0..96 with out[j] = in[p[j]].
  sheet36   R72's 9 two-turn orderings of a 98-cell sheet (r72/data/SHEET98_ORDERINGS.tsv), extra cell first or
            last (r72/novelty.py drop_cell), and the inverse of each;
  rot2      K3-style double rotations R{w1}x{w2}, w1, w2 in 2..48, same direction (CW/CCW) or mixed, fwd and inv
            (strictblind/blind/routes.py rotation, mixed_rotation);
  rot1      single quarter turns, width 2..48, CW/CCW, and inverses (routes.rot);
  colall    complete columnar transpositions with EVERY column order, widths 2-7, 16 fill/read variants, and inverses
            (routes.columnar with a numeric key);
  r61       the 14 directed R61 routes (r74/sandwich.py load_routes; includes COL_LT and SNAKE_L).
Duplicates across sets are merged (first name kept). identity is reported separately as a control."""
import importlib.util
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
N = 97


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


SB = _load("r76_sb_routes", ROOT / "strictblind/blind/routes.py")
NOV = _load("r76_r72_novelty", ROOT / "r72/novelty.py")
SW = _load("r76_r74_sandwich", ROOT / "r74/sandwich.py")


def inv(p):
    q = [0] * len(p)
    for j, i in enumerate(p):
        q[i] = j
    return q


def sheet36():
    out = []
    for line in (ROOT / "r72/data/SHEET98_ORDERINGS.tsv").read_text().splitlines()[1:]:
        k, _, order = line.split("\t")
        o98 = [int(x) for x in order.split(",")]
        for cell in (0, 97):
            p = NOV.drop_cell(o98, cell)
            assert sorted(p) == list(range(N))
            out.append((f"S98x{k}/drop{cell}/fwd", p))
            out.append((f"S98x{k}/drop{cell}/inv", inv(p)))
    return out


def rot2():
    out = []
    for w1 in range(2, 49):
        for w2 in range(2, 49):
            for d in ("CW", "CCW"):
                for k in ("fwd", "inv"):
                    out.append((f"R{w1}x{w2}/{d}/{k}", SB.rotation(f"R{w1}x{w2}/{d}/{k}")))
            for d in ("CW-CCW", "CCW-CW"):
                for k in ("fwd", "inv"):
                    out.append((f"R{w1}x{w2}/{d}/{k}", SB.mixed_rotation(f"R{w1}x{w2}/{d}/{k}")))
    return out


def rot1():
    out = []
    for w in range(2, 49):
        for cw in (True, False):
            p = SB.rot(N, w, cw)
            out.append((f"T{w}/{'CW' if cw else 'CCW'}/fwd", p))
            out.append((f"T{w}/{'CW' if cw else 'CCW'}/inv", inv(p)))
    return out


def colall():
    out = []
    for w in range(2, 8):
        for key in itertools.permutations(range(w)):
            for rf, sn, rs, rr in itertools.product((0, 1), repeat=4):
                p = SB.columnar(key, rf, sn, rs, rr)
                tag = "".join(map(str, key))
                out.append((f"C{w}:{tag}/F{rf}S{sn}O{rs}V{rr}/fwd", p))
                out.append((f"C{w}:{tag}/F{rf}S{sn}O{rs}V{rr}/inv", inv(p)))
    return out


def r61():
    return [(n, list(p)) for n, p in SW.load_routes().items()]


def merged(sets):
    out, seen = [], {tuple(range(N))}
    for name in sets:
        for rn, p in {"sheet36": sheet36, "rot2": rot2, "rot1": rot1, "colall": colall, "r61": r61}[name]():
            t = tuple(p)
            if t not in seen:
                seen.add(t)
                out.append((f"{name}:{rn}", t))
    return out
