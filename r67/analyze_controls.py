#!/usr/bin/env python3
"""R67 post-freeze, ciphertext-only control calibration report.

Usage: python3 r67/analyze_controls.py R67_OUTPUT_DIR R65_CONTROLS_RESULTS.jsonl OUTPUT.json
Run only AFTER R65 raw outputs and checksums are pushed/frozen. No published
K4 plaintext, published-letter offsets, or candidate plaintext is ever read.
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def summary(items, threshold):
    n = len(items)
    above = sum(x['gap'] >= threshold for x in items)
    joint = sum(x['gap'] >= threshold and x['best_route'] == 'SNAKE_L' for x in items)
    gaps = sorted(x['gap'] for x in items)
    return {'n': n, 'ge_k4_gap': above, 'empirical_p': (above + 1) / (n + 1),
            'joint_ge_k4_and_snake': joint,
            'joint_descriptive_rate': joint / n if n else None,
            'gap_median': gaps[n // 2] if n else None,
            'gap_max': gaps[-1] if n else None}


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    outdir, results_file, report_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    if report_path.exists():
        raise SystemExit('Refusing to overwrite existing report')
    manifest = json.loads((outdir / 'MANIFEST.json').read_text())
    truth_file, blind_file = outdir / 'SEALED_TRUTH.json', outdir / 'BLIND.tsv'
    if sha(truth_file) != manifest['truth_sha256'] or sha(blind_file) != manifest['blind_sha256']:
        raise SystemExit('Control inputs changed after preparation')
    truth = json.loads(truth_file.read_text())
    blind = dict(l.split('\t') for l in blind_file.read_text().splitlines()[1:] if l)
    if len(blind) != 216 or len(truth) != 216 or len(set(blind)) != len(truth):
        raise SystemExit('Expected 192 nuisance + 24 positive controls, no duplicate ids')
    for t in truth:
        if blind.get(t['id']) != t['ciphertext']:
            raise SystemExit('Control ciphertext/truth mismatch')
    result_rows = read_jsonl(results_file)
    res = {x['id']: x for x in result_rows}
    if len(res) != len(result_rows) or set(res) != set(blind):
        raise SystemExit('Incomplete or duplicate R65 stage-1 results')
    for r in result_rows:
        if len(r['stage1']) != 10 or len(set(x['route'] for x in r['stage1'])) != 10:
            raise SystemExit('Incomplete 10-route search for ' + r['id'])
        ranked = sorted(r['stage1'], key=lambda x: -x['total'])
        if abs((ranked[0]['total'] - ranked[1]['total']) - r['gap']) > 1e-5:
            raise SystemExit('Route gap mismatch ' + r['id'])
        if ranked[0]['route'] != r['best_route']:
            raise SystemExit('Top route mismatch ' + r['id'])
    k4 = json.loads((ROOT / 'r65/k4/EVALUATION.json').read_text())
    target_gap = k4['k4_gap_rerun']
    if abs(target_gap - 28.4979) > 0.001 or k4['k4_best_route_rerun'] != 'SNAKE_L':
        raise SystemExit('R65 target statistic changed')
    buckets = defaultdict(list)
    positive = []
    for t in truth:
        row = res[t['id']]
        if t['family'] == 'POS_GERMAN':
            positive.append((t, row))
        else:
            buckets[t['family']].append(row)
    required = {'OTP', 'PERIODIC_VIG', 'QUAG_III', 'PLAINTEXT_AUTOKEY',
                'QUAG_III_ROUTE', 'HOMOPHONIC_ROUTE'}
    if set(buckets) != required or any(len(x) != 32 for x in buckets.values()):
        raise SystemExit('Unbalanced nuisance families')
    if len(positive) != 24:
        raise SystemExit('Incorrect positive-control count')
    nuisance = [x for rows in buckets.values() for x in rows]
    pos_stats = {'n': len(positive),
                 'correct_route': sum(t['route'] == r['best_route'] for t, r in positive),
                 'gap_ge_k4': sum(r['gap'] >= target_gap for _, r in positive),
                 'correct_route_and_gap_ge_k4': sum(
                    t['route'] == r['best_route'] and r['gap'] >= target_gap
                    for t, r in positive),
                 'snake_correct': sum(t['route'] == r['best_route'] for t, r in positive
                                      if t['route'] == 'SNAKE_L'),
                 'snake_count': sum(t['route'] == 'SNAKE_L' for t, _ in positive)}
    report = {'experiment': 'R67 (cipher-control calibration, not a K4 solve)',
              'k4_gap': target_gap, 'k4_best_route': 'SNAKE_L',
              'nuisance_pooled': summary(nuisance, target_gap),
              'nuisance_by_family': {family: summary(rows, target_gap)
                                    for family, rows in sorted(buckets.items())},
              'positive_controls': pos_stats,
              'control_blind_sha256': manifest['blind_sha256'],
              'control_truth_sha256': manifest['truth_sha256'],
              'results_sha256': sha(results_file),
              'interpretation': 'DESCRIPTIVE ONLY: R65 route-gap statistic was chosen after '
                                'inspecting K4. Low structured-control rate neither proves '
                                'SNAKE_L nor decrypts K4. Compare matched IC and power. '
                                'No K4 published clues evaluated.'}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
