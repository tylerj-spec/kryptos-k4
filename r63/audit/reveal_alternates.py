#!/usr/bin/env python3
"""R63 SEALED, optional exploratory check of previously frozen raw candidates.

NEVER run before a verified remote Git freeze of WORK_FREEZE.sha256 and every
referenced raw work/ file. This is a secondary look, NOT a preregistered R63
SIGNAL and NOT a new search/generator. It cannot feed results to the solver.
The only source of known K4 plaintext is r63/sealed/reveal_k4.py, dynamically
loaded strictly after the independent freeze audit has passed.

Invocation uses the same source/file arguments as verify_frozen.py plus
--remote-freeze-commit (the operator must independently verify the pushed
commit and record its URL before invoking this postfreeze check).
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # also works under python3 -I (no script dir on sys.path)
from verify_frozen import audit, parse_jsonl, MODES  # noqa: E402


def examine(frozen, hit_checker):
    found = {}
    for mode in MODES:
        chunk = parse_jsonl(frozen / 'work' / f'{mode}_000.jsonl')
        assert chunk and chunk[0]['id'] == 'K4', 'K4 must be in the first work chunk'
        r = chunk[0]
        candidates = [r['best']] + r['per_convention'] + r['top']
        unique = {}
        for b in candidates:
            key = (b['convention'], b['plaintext'], b['key'])
            unique[key] = b
        high = []
        exact = []
        for b in unique.values():
            n = hit_checker(b['plaintext'])
            if n >= 10:
                high.append({'clue_hits': n, **b})
            if n == 24:
                exact.append({'clue_hits': n, **b})
        found[mode] = {
            'frozen_k4_alternative_count': len(unique),
            'postfreeze_candidates_at_least_10_of_24': len(high),
            'postfreeze_candidates_24_of_24': len(exact),
            'candidate_details_at_least_10_of_24': high,
        }
    return found


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('input', 'frozen', 'root', 'solver-binary', 'english-lm', 'keydir'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--expected-nulls', type=int, default=100)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--remote-freeze-commit', required=True,
                   help='Full verified remote Git SHA covering WORK_FREEZE and every raw chunk; independently verify first')
    args = p.parse_args()
    if not (len(args.remote_freeze_commit) == 40 and
            all(c in '0123456789abcdef' for c in args.remote_freeze_commit.lower())):
        p.error('remote-freeze-commit must be a full 40-character Git SHA')
    # No clue import until AFTER the complete source, data, raw alt, and witness audit.
    report = audit(args)
    spec = importlib.util.spec_from_file_location('r63_sealed_checker',
                                                    args.root / 'r63/sealed/reveal_k4.py')
    if not spec or not spec.loader:
        p.error('cannot load sealed R63 check')
    sealed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sealed)
    results = {
        'kind': 'R63 SECONDARY postfreeze alternative-check (not preregistered SIGNAL)',
        'independently_supplied_remote_freeze_sha': args.remote_freeze_commit,
        'remote_git_freeze_verified_by_this_script': False,
        'audit_work_seal_sha256': report['work_seal']['work_seal_sha256'],
        'full_witnesses_checked_before_clues': report['full_length_forward_witnesses_passed'] + report['raw_best_and_alternative_witnesses_passed'],
        'models': examine(args.frozen, sealed.hits),
        'caveat': 'These are pre-existing generated alternatives, screened after a remote freeze. Do not refit keys or revise the original preregistered R63 primary decision based on this check.',
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()