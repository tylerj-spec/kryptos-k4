#!/usr/bin/env python3
"""R67 POST-FREEZE synthetic-truth descriptive evaluator (no K4 known letters).

Usage:
  python3 r67/analyze_controls.py CONTROL_DIR RUN_DIR/RESULTS.jsonl REPORT.json

Requires CONTROL_DIR/VERIFY.json with status PASSED, produced only AFTER all
raw blind outputs are committed/pushed and integrity-verified. Hash and frozen
result gates are checked BEFORE SEALED_TRUTH.json is read. Descriptive only.
"""
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ('OTP', 'PERIODIC_VIG', 'QUAG_III', 'PLAINTEXT_AUTOKEY',
            'QUAG_III_ROUTE', 'HOMOPHONIC_ROUTE')
ROUTES = {l.split()[0] for l in (ROOT / 'r61/routes.txt').read_text().splitlines()}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jsonl(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def parse_frozen(path):
    pairs = {}
    for line in path.read_text().splitlines():
        h, role, name = line.split('  ', 2)
        if (role, name) in pairs:
            raise ValueError('duplicate freeze entry')
        pairs[(role, name)] = h
    return pairs


def describe(values):
    values = sorted(values)
    return {'n': len(values), 'min': values[0], 'median': statistics.median(values),
            'max': values[-1]} if values else {'n': 0}


def metrics(rows, threshold):
    gaps = [r['gap'] for r in rows]
    best = [r['stage1'][0]['total'] for r in rows]
    second = [r['stage1'][1]['total'] for r in rows]
    left_right = [next(x['total'] for x in r['stage1'] if x['route'] == 'SNAKE_L') -
                  next(x['total'] for x in r['stage1'] if x['route'] == 'SNAKE_R')
                  for r in rows]
    ge = sum(g >= threshold for g in gaps)
    snake = sum(r['best_route'] == 'SNAKE_L' for r in rows)
    joint = sum(r['best_route'] == 'SNAKE_L' and r['gap'] >= threshold for r in rows)
    return {'n': len(rows), 'gaps_ge_k4': ge,
            'descriptive_smoothed_tail': (ge + 1) / (len(rows) + 1),
            'snake_l_best_count': snake,
            'snake_l_best_fraction': snake / len(rows),
            'snake_l_best_and_large_gap_count': joint,
            'gap': describe(gaps),
            'best_route_total': describe(best),
            'second_best_route_total': describe(second),
            'snake_l_minus_snake_r': describe(left_right),
            'route_histogram': dict(sorted(Counter(r['best_route'] for r in rows).items()))}


def params_distribution(truth):
    out = {}
    for family in FAMILIES:
        subset = [t for t in truth if t['family'] == family]
        samples = {}
        if family in ('PERIODIC_VIG', 'QUAG_III', 'QUAG_III_ROUTE'):
            samples['key_period'] = dict(sorted(Counter(len(t['key']) for t in subset).items()))
        elif family == 'PLAINTEXT_AUTOKEY':
            samples['autokey_lag'] = dict(sorted(Counter(t['lag'] for t in subset).items()))
        elif family == 'HOMOPHONIC_ROUTE':
            samples['used_homophone_symbols'] = dict(sorted(Counter(
                sum(len(x) for x in t['homophones'].values()) for t in subset).items()))
            samples['max_per_plain_letter'] = dict(sorted(Counter(
                max(map(len, t['homophones'].values())) for t in subset).items()))
        if family.endswith('_ROUTE'):
            samples['true_route'] = dict(sorted(Counter(t['route'] for t in subset).items()))
        out[family] = samples
    return out


def pos_summary(pairs, threshold):
    n = len(pairs)
    return {'n': n,
            'correct_route': sum(t['route'] == r['best_route'] for t, r in pairs),
            'gap_ge_k4': sum(r['gap'] >= threshold for t, r in pairs),
            'joint_correct_and_gap_ge_k4': sum(
                t['route'] == r['best_route'] and r['gap'] >= threshold for t, r in pairs),
            'gap': describe([r['gap'] for _, r in pairs]),
            'best_route_total': describe([r['stage1'][0]['total'] for _, r in pairs])}


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    ctrl, results, report_path = map(Path, sys.argv[1:])
    if report_path.exists():
        raise SystemExit('refusing to overwrite evaluation report')
    if not results.is_file():
        raise SystemExit('missing run results')
    verify = json.loads((ctrl / 'VERIFY.json').read_text())
    manifest = json.loads((ctrl / 'MANIFEST.json').read_text())
    pinned_prereg = (ROOT / 'r67/PREREGISTRATION.sha256').read_text().split()[0]
    if (verify.get('status') != 'PASSED'
            or verify.get('preregistration_sha256') != pinned_prereg
            or manifest.get('preregistration_sha256') != pinned_prereg
            or sha(ROOT / 'r67/PREREGISTRATION.md') != pinned_prereg):
        raise SystemExit('INVALID: pre-reveal audit or frozen preregistration gate failed')
    if (verify['results_sha256'] != sha(results)
            or verify['input_sha256'] != sha(ctrl / 'BLIND.tsv')):
        raise SystemExit('INVALID: verification hashes differ from current inputs/results')
    frozen = parse_frozen(results.parent / 'FROZEN.sha256')
    entries = [v for (role, name), v in frozen.items() if role == 'results']
    if len(entries) != 1 or entries[0] != sha(results):
        raise SystemExit('INVALID: RESULTS.jsonl differs from frozen hash')
    if (verify['freeze_manifest_sha256'] != sha(results.parent / 'FROZEN.sha256')
            or verify['work_manifest_sha256'] != sha(results.parent / 'WORK.sha256')):
        raise SystemExit('INVALID: frozen raw witness manifests changed after verification')
    if manifest.get('blind_sha256') != sha(ctrl / 'BLIND.tsv'):
        raise SystemExit('INVALID: control ciphertext changed')
    # NO sealed synthetic plaintext/key is opened above this line.
    truth_path = ctrl / 'SEALED_TRUTH.json'
    if sha(truth_path) != manifest['truth_sha256']:
        raise SystemExit('INVALID: sealed synthetic truth changed')
    truth = json.loads(truth_path.read_text())
    blind_rows = (ctrl / 'BLIND.tsv').read_text().splitlines()
    blind = dict(l.split('\t') for l in blind_rows[1:])
    if (blind_rows[0] != 'id\tciphertext' or len(blind_rows) != 217
            or len(blind) != 216 or len(truth) != 216):
        raise SystemExit('INVALID: 216 unique control ciphertexts required')
    for t in truth:
        if blind.get(t['id']) != t['ciphertext']:
            raise SystemExit('INVALID: sealed/blind control disagreement')
    rows = jsonl(results)
    res = {r['id']: r for r in rows}
    if len(res) != 216 or len(rows) != 216 or set(res) != set(blind):
        raise SystemExit('INVALID: result IDs incomplete or duplicated')
    for r in rows:
        stage = r['stage1']
        if len(stage) != 10 or set(x['route'] for x in stage) != ROUTES:
            raise SystemExit('INVALID: missing or duplicated route score')
        ordered = sorted(stage, key=lambda x: (-x['total'], next(
            i for i, name in enumerate((l.split()[0] for l in
              (ROOT / 'r61/routes.txt').read_text().splitlines())) if name == x['route'])))
        if (r['best_route'] != ordered[0]['route']
                or abs(r['gap'] - (ordered[0]['total'] - ordered[1]['total'])) > 1e-5):
            raise SystemExit('INVALID: inconsistent scores/gap')
        r['stage1'] = ordered
    k4 = json.loads((ROOT / 'r65/k4/EVALUATION.json').read_text())
    k4_gap = k4['k4_gap_rerun']
    if abs(k4_gap - 28.4979) > 0.001 or k4['k4_best_route_rerun'] != 'SNAKE_L':
        raise SystemExit('INVALID: R65 comparison changed')
    buckets = defaultdict(list)
    positives = []
    for t in truth:
        row = res[t['id']]
        if t['family'] == 'POS_GERMAN':
            positives.append((t, row))
        else:
            buckets[t['family']].append(row)
    if (set(buckets) != set(FAMILIES)
            or any(len(buckets[family]) != 32 for family in FAMILIES)
            or len(positives) != 24
            or sum(t['route'] == 'SNAKE_L' for t, _ in positives) != 12):
        raise SystemExit('INVALID: unbalanced or missing controls')
    nuisance = [r for family in FAMILIES for r in buckets[family]]
    pos_snake = [p for p in positives if p[0]['route'] == 'SNAKE_L']
    pos_other = [p for p in positives if p[0]['route'] != 'SNAKE_L']
    # K4's existing R65 frozen route components, no new solve or clue.
    old = next(x for x in jsonl(ROOT / 'r65/k4/run/RESULTS.jsonl') if x['id'] == 'K4')
    oldstage = {r['route']: r['total'] for r in old['stage1']}
    context = {'gap': k4_gap, 'best_route': k4['k4_best_route_rerun'],
               'best_total': old['stage1'][0]['total'],
               'second_total': old['stage1'][1]['total'],
               'snake_l_minus_snake_r': oldstage['SNAKE_L'] - oldstage['SNAKE_R']}
    if abs(context['best_total'] - context['second_total'] - k4_gap) > 0.001:
        raise SystemExit('INVALID: R65 frozen stage-1 mismatch')
    attempts = manifest['family_counts']
    if any(attempts[f]['accepted'] != 32 for f in FAMILIES):
        raise SystemExit('INVALID: family acceptance counts')
    report = {
        'experiment': 'R67 (post-selection descriptive cipher controls, NOT a K4 solve)',
        'comparison_k4_r65_stage1': context,
        'nuisance_pooled': metrics(nuisance, k4_gap),
        'nuisance_by_family': {family: metrics(buckets[family], k4_gap) for family in FAMILIES},
        'nuisance_accepted_attempts': attempts,
        'accepted_parameter_distributions': params_distribution(truth),
        'positive_controls': {
            'all': pos_summary(positives, k4_gap),
            'true_snake_l': pos_summary(pos_snake, k4_gap),
            'other_routes': pos_summary(pos_other, k4_gap),
        },
        'provenance': {'control_blind_sha256': manifest['blind_sha256'],
                       'sealed_truth_sha256': manifest['truth_sha256'],
                       'source_manifest_sha256': manifest['source_manifest_sha256'],
                       'preregistration_sha256': pinned_prereg,
                       'verification_sha256': sha(ctrl / 'VERIFY.json'),
                       'raw_results_sha256': sha(results)},
        'limitations': ('R65 gap and SNAKE_L were selected after inspecting K4. '
                        'A matching IC/letter-coverage filter selects parameter tails. '
                        'No unmatched companion controls or carved-order identity solves '
                        'are included; SNAKE_L-SNAKE_R and best/second totals cost no '
                        'additional solver runs. Low rates do not prove a K4 method. '
                        'R65b rejects the specific German-key explanation with high '
                        'statistical power, not as a mathematical exclusion.')
    }
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
