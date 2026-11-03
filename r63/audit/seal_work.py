#!/usr/bin/env python3
"""Freeze R63 raw per-convention/top alternatives BEFORE any K4 clue check.

Run after the blind solver completes, but BEFORE posting results or invoking
r63/sealed/reveal_k4.py. This operation reads no K4 known plaintext.
The resulting WORK_FREEZE.sha256 AND all the listed raw work files must be
committed and successfully pushed to remote Git before any postfreeze reveal.

python3 r63/audit/seal_work.py /path/to/R63_FROZEN_DIR [--expected-nulls 100]
"""
import argparse
import hashlib
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('frozen', type=Path)
    p.add_argument('--expected-nulls', type=int, default=100)
    a = p.parse_args()
    if a.expected_nulls < 1:
        p.error('expected-nulls must be >= 1')
    work = a.frozen / 'work'
    n = (a.expected_nulls + 1 + 2) // 3  # pre-registered chunks of 3
    expected = [work / f'{mode}_{j:03d}.{ext}'
                for mode in ('CLOCK', 'GERMAN')
                for j in range(n) for ext in ('tsv', 'jsonl')]
    found = set(work.glob('*.jsonl')) | set(work.glob('*.tsv'))
    if set(expected) != found:
        p.error(f'work file mismatch: missing={sorted(set(expected)-found)}, extra={sorted(found-set(expected))}')
    files = [a.frozen / 'RESULTS.jsonl', a.frozen / 'FROZEN.sha256'] + expected
    for path in files:
        if not path.is_file() or path.stat().st_size == 0:
            p.error(f'missing or empty file: {path}')
    output = a.frozen / 'WORK_FREEZE.sha256'
    if output.exists():
        p.error(f'refusing to overwrite: {output}')
    output.write_text(''.join(f'{sha(path)}  {path.relative_to(a.frozen).as_posix()}\n'
                              for path in files), encoding='utf-8')
    print(f'WORK_FREEZE.sha256 created: {len(files)} entries; sha256={sha(output)}')
    print('NOT REMOTELY FROZEN YET. Push this manifest AND all listed files to remote Git before any clue check.')


if __name__ == '__main__':
    main()