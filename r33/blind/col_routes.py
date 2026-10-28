#!/usr/bin/env python3
"""Crib-free keyed irregular-columnar permutation enumerator for Round 33.

Each line: name, S_then_T|T_then_S, permutation CT[j]=X[perm[j]].
The three keywords are sourced from earlier Kryptos sections; no K4 plaintext clues.
"""
from pathlib import Path

N = 97
WORDS = ('KRYPTOS', 'PALIMPSEST', 'ABSCISSA')


def invert(p):
    q = [0] * len(p)
    for j, v in enumerate(p):
        q[v] = j
    return q


def columnar(key, revfill=False, snake=False, revsort=False, revread=False):
    w = len(key)
    grid = {}
    for j in range(N):
        row, col = divmod(j, w)
        if snake and row % 2:
            col = w - 1 - col
        if revfill:
            col = w - 1 - col
        grid[row, col] = j
    ordered_columns = sorted(range(w), key=lambda c: (key[c], c))
    if revsort:
        ordered_columns.reverse()
    rows = (N + w - 1) // w
    p = []
    for c in ordered_columns:
        for r in (range(rows - 1, -1, -1) if revread else range(rows)):
            if (r, c) in grid:
                p.append(grid[r, c])
    assert len(p) == N and sorted(p) == list(range(N))
    return p


def variants(key):
    for revfill in (0, 1):
        for snake in (0, 1):
            for revsort in (0, 1):
                for revread in (0, 1):
                    p = columnar(key, revfill, snake, revsort, revread)
                    attrs = f'F{revfill}S{snake}O{revsort}V{revread}'
                    for inv in (0, 1):
                        yield key + '/' + attrs + ('/INV' if inv else '/FWD'), invert(p) if inv else p


def write(file, which):
    entries = []
    # F1 all variants, F2 canonical four per keyword (not selected from ciphertext)
    for key in WORDS:
        for name, p in variants(key):
            if which == 'CARTER':
                # freeze only 4 canonical physical column-read conventions per word
                # forward fill, non-snake; asc/desc sort, top/bottom read; forward orientation
                if not any(name.endswith('/' + x + '/FWD') for x in ('F0S0O0V0', 'F0S0O1V0', 'F0S0O0V1', 'F0S0O1V1')):
                    continue
            for order in ('S_then_T', 'T_then_S'):
                entries.append((name, order, p))
    with file.open('w') as f:
        for name, order, p in entries:
            f.write(name + ' ' + order + ' ' + ','.join(str(x) for x in p) + '\n')
    return len(entries)


if __name__ == '__main__':
    out = Path(__file__).resolve().parent.parent / 'runs'
    out.mkdir(exist_ok=True)
    print('G5', write(out / 'routes_g5.txt', 'G5'))
    print('CARTER', write(out / 'routes_carter.txt', 'CARTER'))
