#!/usr/bin/env python3
"""Read-only replay of R89's frozen evidence; this is an audit, not a new search.

Run this program through audit/run_bounded.py. Outputs go only to a new directory.
The original language-model binary is not supplied, so neither the original blind
search nor its letter scores are represented as freshly reproduced here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report = {'mode': 'FROZEN_RESULT_REPLAY', 'new_blind_search': False,
              'language_model_scores_recomputed': False, 'checks': [], 'commands': []}

    def check(name, ok, **detail):
        report['checks'].append({'name': name, 'passed': bool(ok), **detail})
        if not ok:
            (out / 'REPLAY_SUMMARY.json').write_text(json.dumps(report, indent=2) + '\n')
            raise AssertionError(name)

    manifests = ['r89/PROTOCOL.sha256', 'r89/holdout/GATE_FROZEN.sha256', 'r89/k4/FROZEN.sha256']
    for rel in manifests:
        rows = []
        for line in (root / rel).read_text().splitlines():
            if not line.strip():
                continue
            expected, path = line.split()[0], line.split()[-1]
            p = root / path
            rows.append({'path': path, 'present': p.is_file(),
                         'matches': p.is_file() and sha(p) == expected})
        check(rel, all(x['matches'] for x in rows), entries=len(rows), files=rows)

    wanted = (root / 'r89/holdout/TRUTH_SHA256').read_text().split()[0]
    check('sealed_truth_digest', sha(root / 'r89/holdout/TRUTH.json') == wanted)
    rows = [line.split('\t') for line in (root / 'r89/k4/TARGET.tsv').read_text().splitlines()[1:] if line]
    inputs = dict(rows)
    k4 = inputs['K4']
    expected_ids = {'K4'} | {f'NULL_{i:03d}' for i in range(200)}
    source = (root / 'r39/ic_gate/k4_ciphertext.txt').read_text().strip()
    check('target_integrity', len(rows) == len(inputs) == 201 and set(inputs) == expected_ids
          and k4 == source and all(len(ct) == 97 and sorted(ct) == sorted(k4) for ct in inputs.values()),
          rows=len(rows), nulls=len(rows)-1)

    def run(label, command, expected=None, produced=None, timeout=600):
        started = time.monotonic()
        result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=timeout,
                                env={**os.environ, 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'})
        (out / f'{label}.log').write_text(result.stdout + result.stderr)
        record = {'label': label, 'returncode': result.returncode,
                  'wall_seconds': round(time.monotonic() - started, 3)}
        if expected:
            record['matches_frozen_bytes'] = produced.is_file() and produced.read_bytes() == (root / expected).read_bytes()
        report['commands'].append(record)
        check(label, result.returncode == 0 and (not expected or record['matches_frozen_bytes']))
        print(label + ': PASS', flush=True)

    py = sys.executable
    run('unit_tests', [py, '-I', 'r89/tests/test_r89.py'])
    for label, inp in [('gate', 'holdout/BLIND.tsv'), ('k4', 'k4/TARGET.tsv')]:
        run('witness_' + label, [py, '-I', 'r89/sealed/witness89.py', 'r89/' + inp,
                                'r89/' + ('holdout' if label == 'gate' else 'k4') + '/run/RESULTS.jsonl',
                                str(out / ('WITNESS_' + label + '.json'))],
            'r89/' + ('holdout' if label == 'gate' else 'k4') + '/run/WITNESS.json',
            out / ('WITNESS_' + label + '.json'))
    run('gate', [py, '-I', 'r89/sealed/gate89.py', 'r89/holdout', 'r89/holdout/TRUTH.json', str(out / 'GATE.json')],
        'r89/holdout/GATE.json', out / 'GATE.json')
    run('evaluation', [py, '-I', 'r89/sealed/evaluate89.py', 'r89/k4/TARGET.tsv', 'r89/k4/run/RESULTS.jsonl',
                       'r89/k4/run/WITNESS.json', 'r89/k4/FROZEN.sha256', str(out / 'EVALUATION.json')],
        'r89/k4/EVALUATION.json', out / 'EVALUATION.json')
    run('exact', [py, '-I', 'r89/sealed/exact89.py', 'r89/k4/TARGET.tsv', 'F26L,RCT', str(out / 'EXACT.json')],
        'r89/k4/EXACT.json', out / 'EXACT.json')
    report['passed'] = all(c['passed'] for c in report['checks'])
    (out / 'REPLAY_SUMMARY.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Frozen-result replay: PASS; original blind search and letter scores not rerun.', flush=True)


if __name__ == '__main__':
    main()
