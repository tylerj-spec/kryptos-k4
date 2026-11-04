#!/usr/bin/env python3
"""R67 pre-reveal verifier: hashes, full 97-letter witnesses, forward encryption.

Usage: python3 r67/verify_controls.py BLIND.tsv RUN_DIR REPORT.json
This verifier NEVER reads SEALED_TRUTH.json or published K4 plaintext.
It must be run after the blind outputs are frozen and before synthetic truth opens.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'r64/sealed'))
from common import forward, routes  # noqa: E402


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    inp, run, report = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    if report.exists():
        raise SystemExit('Refusing to overwrite report')
    problems = []
    if not (run / 'FROZEN.sha256').exists() or not (run / 'WORK.sha256').exists():
        raise SystemExit('Missing frozen manifests')
    frozen = (run / 'FROZEN.sha256').read_text().splitlines()
    required = {'input', 'results', 'solver_source', 'solver_binary', 'english_lm',
                'english_words', 'routes', 'key_model', 'runner', 'r64_runner', 'protocol'}
    found = set()
    for line in frozen:
        try:
            h, lab, name = line.split('  ')
        except ValueError:
            problems.append('invalid manifest line: ' + line[:80])
            continue
        found.add(lab)
        if lab in {'input', 'results'}:
            path = inp if lab == 'input' else run / 'RESULTS.jsonl'
            if digest(path) != h:
                problems.append('freeze SHA mismatch ' + lab)
        elif lab == 'routes':
            if digest(ROOT / 'r61/routes.txt') != h:
                problems.append('routes SHA mismatch')
        elif lab == 'runner':
            if digest(ROOT / 'r65/blind/run.py') != h:
                problems.append('R65 runner SHA mismatch')
        elif lab == 'r64_runner':
            if digest(ROOT / 'r64/blind/run.py') != h:
                problems.append('R64 runner SHA mismatch')
        elif lab == 'solver_source':
            if digest(ROOT / 'r63/blind/rk2_solve.cpp') != h:
                problems.append('solver source SHA mismatch')
        elif lab == 'english_words':
            if digest(ROOT / 'k4kit/data/word_model_orth.tsv') != h:
                problems.append('word-model SHA mismatch')
        elif lab == 'protocol':
            if digest(ROOT / 'r65/PREREGISTRATION.md') != h:
                problems.append('R65 protocol SHA mismatch')
    if not required.issubset(found):
        problems.append('missing freeze-manifest labels: ' + ','.join(sorted(required - found)))
    listed = set()
    for line in (run / 'WORK.sha256').read_text().splitlines():
        try:
            h, name = line.split('  ')
        except ValueError:
            problems.append('invalid work manifest line')
            continue
        listed.add(name)
        f = run / 'work' / name
        if not f.exists() or digest(f) != h:
            problems.append('work SHA mismatch ' + name)
    actual = {p.name for p in (run / 'work').iterdir() if p.is_file()}
    if actual != listed:
        problems.append('extra/missing work files')
    R = routes()
    names = list(R)
    if len(names) != 10:
        problems.append('frozen routes changed count')
    cts = dict(l.split('\t') for l in inp.read_text().splitlines()[1:] if l)
    if len(cts) != 216:
        problems.append('expected exactly 216 controls')
    if any(len(v) != 97 or not v.isupper() for v in cts.values()):
        problems.append('malformed ciphertext')
    rows = [json.loads(l) for l in (run / 'RESULTS.jsonl').read_text().splitlines() if l.strip()]
    by_id = {r['id']: r for r in rows}
    if len(by_id) != len(rows) or set(by_id) != set(cts):
        problems.append('result IDs incomplete or duplicated')
    count = 0
    for rid in cts:
        jf = run / 'work' / (rid + '.s1.jsonl')
        if not jf.exists():
            problems.append('missing raw solver outputs ' + rid)
            continue
        workrows = [json.loads(l) for l in jf.read_text().splitlines() if l.strip()]
        if len(workrows) != 10:
            problems.append('missing route output ' + rid)
        route_indices = []
        for r in workrows:
            try:
                idx = int(r['id'].rsplit('__', 1)[1])
                route_indices.append(idx)
                rn = names[idx]
                for witness in [r['best']] + r['per_convention'] + r['top']:
                    count += 1
                    if len(witness['plaintext']) != 97 or len(witness['key']) != 97:
                        problems.append('incomplete 97-letter witness ' + rid + ' ' + rn)
                    elif forward(witness['plaintext'], witness['key'],
                                 witness['convention'], R[rn]) != cts[rid]:
                        problems.append('not independently re-encryptable ' + rid + ' ' + rn)
            except (KeyError, ValueError, IndexError, TypeError) as e:
                problems.append('malformed witness ' + rid + ': ' + str(e))
        if sorted(route_indices) != list(range(10)):
            problems.append('missing/duplicate route in ' + rid)
    status = 'PASSED' if not problems else 'INVALID'
    output = {'status': status, 'controls': len(cts), 'witnesses_checked': count,
              'problem_count': len(problems), 'problems': problems,
              'input_sha256': digest(inp),
              'results_sha256': digest(run / 'RESULTS.jsonl'),
              'work_manifest_sha256': digest(run / 'WORK.sha256'),
              'freeze_manifest_sha256': digest(run / 'FROZEN.sha256')}
    report.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: v for k, v in output.items() if k != 'problems'}, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
