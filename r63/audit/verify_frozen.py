#!/usr/bin/env python3
"""Independent R63 K4 A/B post-freeze audit, with no published plaintext clues.

Read-only for the input, solver artifacts, and freeze directory. Requires a
separately verified remote Git freeze BEFORE running or reporting a result.
This script does not check known plaintext, select candidates, or run a solver.

Example (from the historical source tree, checked out at its freeze commit):
 python3 r63/audit/verify_frozen.py \
   --input /path/TARGET.tsv --frozen /path/FROZEN_DIR \
   --root /path/kryptos-k4 --solver-binary /path/rk2_solve \
   --english-lm /path/lm6_en.bin --keydir /path/model_dir \
   --report /path/OUTSIDE_FREEZE/audit.json
"""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path

AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
KRY = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'
MODES = ('CLOCK', 'GERMAN')
CONVS = {f'{x}_{op}' for x in ('AZ', 'KRY') for op in ('VIG', 'BEAU', 'VARB')}
KEY_FILES = ('lm6_clock.bin', 'clock_words.tsv', 'lm6_de.bin', 'de_words.tsv')


class AuditError(Exception):
    pass


def need(ok, message):
    if not ok:
        raise AuditError(message)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def parse_tsv(path):
    lines = path.read_text(encoding='utf-8').splitlines()
    need(lines and lines[0] == 'id\tciphertext', f'{path}: unexpected TSV header')
    out = []
    seen = set()
    for line_no, line in enumerate(lines[1:], 2):
        parts = line.split('\t')
        need(len(parts) == 2, f'{path}:{line_no}: invalid TSV row')
        ident, ct = parts
        need(ident not in seen, f'{path}: duplicate id {ident}')
        need(ident and len(ct) == 97 and set(ct) <= set(AZ),
             f'{path}:{line_no}: ciphertext must contain 97 A-Z letters')
        seen.add(ident)
        out.append((ident, ct))
    return out


def parse_jsonl(path):
    rows = []
    for ln, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except (ValueError, TypeError) as e:
                raise AuditError(f'{path}:{ln}: invalid JSON: {e}') from e
    return rows


def encode(p, k, conv):
    name, op = conv.split('_')
    alpha = AZ if name == 'AZ' else KRY
    tab = {ch: i for i, ch in enumerate(alpha)}
    out = []
    for a, b in zip(p, k):
        x, y = tab[a], tab[b]
        z = (x + y) if op == 'VIG' else ((y - x) if op == 'BEAU' else (x - y))
        out.append(alpha[z % 26])
    return ''.join(out)


def check_best(best, ct, label):
    need(isinstance(best, dict), f'{label}: missing best candidate')
    conv = best.get('convention')
    need(conv in CONVS, f'{label}: unexpected convention {conv}')
    for name in ('plaintext', 'key'):
        value = best.get(name)
        need(isinstance(value, str) and len(value) == 97 and set(value) <= set(AZ),
             f'{label}: invalid 97-character {name}')
    for name in ('total', 'lm', 'word'):
        value = best.get(name)
        need(type(value) in (float, int) and math.isfinite(value),
             f'{label}: invalid numeric {name}')
    need(encode(best['plaintext'], best['key'], conv) == ct,
         f'{label}: forward-encryption witness FAILED')


def verify_manifest(args):
    root, frozen, keydir = args.root, args.frozen, args.keydir
    resolved = [
        ('input', args.input),
        ('results', frozen / 'RESULTS.jsonl'),
        ('solver_source', root / 'r63/blind/rk2_solve.cpp'),
        ('solver_binary', args.solver_binary),
        ('english_lm', args.english_lm),
        ('english_words', root / 'k4kit/data/word_model_orth.tsv'),
    ]
    resolved += [('key_model', keydir / f) for f in KEY_FILES]
    resolved += [('runner', root / 'r63/blind/run.py'),
                 ('protocol', root / 'r63/PREREGISTRATION.md')]
    expected = {(label, path.name): path for label, path in resolved}
    need(len(expected) == len(resolved), 'ambiguous source manifest basenames')
    manifest = frozen / 'FROZEN.sha256'
    entries = {}
    for ln, line in enumerate(manifest.read_text(encoding='utf-8').splitlines(), 1):
        parts = line.split('  ')
        need(len(parts) == 3, f'manifest line {ln}: malformed entry')
        digest, label, basename = parts
        need(len(digest) == 64 and all(c in '0123456789abcdef' for c in digest),
             f'manifest line {ln}: invalid SHA-256')
        key = (label, basename)
        need(key not in entries, f'manifest line {ln}: duplicate entry {key}')
        entries[key] = digest
    need(set(entries) == set(expected),
         f'manifest entry mismatch: missing={sorted(set(expected)-set(entries))}, '
         f'extra={sorted(set(entries)-set(expected))}')
    for key, path in expected.items():
        need(path.is_file(), f'missing source file: {path}')
        need(sha(path) == entries[key], f'SHA-256 mismatch: {key} at {path}')
    return {'entries_verified': len(entries), 'manifest_sha256': sha(manifest),
            'raw_results_sha256': sha(frozen / 'RESULTS.jsonl'),
            'protocol_sha256': entries[('protocol', 'PREREGISTRATION.md')]}


def verify_work_seal(frozen, required_files):
    """Require a pre-reveal hash commitment to every raw alternative file."""
    path = frozen / 'WORK_FREEZE.sha256'
    need(path.is_file(), 'WORK_FREEZE.sha256 missing: raw alternatives are NOT frozen')
    expected = {rel: file for rel, file in required_files}
    actual = {}
    for ln, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        parts = line.split('  ')
        need(len(parts) == 2, f'WORK_FREEZE line {ln}: malformed entry')
        digest, name = parts
        need(len(digest) == 64 and all(c in '0123456789abcdef' for c in digest),
             f'WORK_FREEZE line {ln}: invalid digest')
        need(name not in actual, f'WORK_FREEZE line {ln}: duplicate entry')
        actual[name] = digest
    need(set(actual) == set(expected),
         f'WORK_FREEZE missing/extra files: {sorted(set(expected)-set(actual))}, '
         f'{sorted(set(actual)-set(expected))}')
    for name, file in expected.items():
        need(file.is_file(), f'WORK_FREEZE missing file: {name}')
        need(sha(file) == actual[name], f'WORK_FREEZE SHA-256 mismatch: {name}')
    return {'entries_verified': len(expected), 'work_seal_sha256': sha(path)}


def audit(args):
    need(args.expected_nulls >= 1, 'expected_nulls must be >= 1')
    paths = [args.input, args.frozen, args.root, args.solver_binary,
             args.english_lm, args.keydir]
    for path in paths:
        need(path.exists(), f'path not found: {path}')
    if args.report:
        need(args.report.resolve() != (args.frozen / 'RESULTS.jsonl').resolve(),
             'report cannot overwrite frozen results')
        need(args.frozen.resolve() not in args.report.resolve().parents,
             'report must be outside the frozen directory')
    manifest_info = verify_manifest(args)
    target = parse_tsv(args.input)
    want_ids = ['K4'] + [f'NULL_{j:03d}' for j in range(args.expected_nulls)]
    need([ident for ident, _ in target] == want_ids,
         f'target ids/order mismatch: expected K4 plus {args.expected_nulls} NULL_XXX')
    ct_original = (args.root / 'r39/ic_gate/k4_ciphertext.txt').read_text().strip()
    need(target[0][1] == ct_original, 'K4 ciphertext differs from source')
    # The nulls must preserve exactly the original ciphertext's letter counts.
    original_hist = collections.Counter(ct_original)
    null_cts = [ct for _, ct in target[1:]]
    need(len(set(null_cts)) == len(null_cts), 'duplicate null ciphertexts')
    for j, ct in enumerate(null_cts):
        need(ct != ct_original and collections.Counter(ct) == original_hist,
             f'NULL_{j:03d}: not a distinct letter-count-preserving shuffle')

    raw = parse_jsonl(args.frozen / 'RESULTS.jsonl')
    need(len(raw) == len(target), 'merged results row count mismatch')
    need([r.get('id') for r in raw] == want_ids, 'merged results IDs/order mismatch')
    cts = dict(target)
    for r in raw:
        ident = r['id']
        models = r.get('models')
        need(isinstance(models, dict) and set(models) == set(MODES),
             f'{ident}: missing/extra models')
        for model in MODES:
            check_best(models[model], cts[ident], f'{ident}/{model}')

    # A resume cache with only the right row count can silently contain data
    # from a different input. Verify *every* cached plaintext and ciphertext
    # against both the current input and final merged output.
    work = args.frozen / 'work'
    need(work.is_dir(), 'work/ chunk directory missing')
    nchunks = (len(target) + 2) // 3  # pre-registered CHUNK=3
    total_chunks = 0
    verified_raw_candidates = 0
    per_model_unique_k4 = {mode: set() for mode in MODES}
    work_files = [('RESULTS.jsonl', args.frozen / 'RESULTS.jsonl'),
                  ('FROZEN.sha256', args.frozen / 'FROZEN.sha256')]
    for mode in MODES:
        for j in range(nchunks):
            for ext in ('tsv', 'jsonl'):
                rel = f'work/{mode}_{j:03d}.{ext}'
                work_files.append((rel, work / f'{mode}_{j:03d}.{ext}'))
    seal_info = verify_work_seal(args.frozen, work_files)
    for model in MODES:
        expected_names = {f'{model}_{j:03d}.{ext}'
                          for j in range(nchunks) for ext in ('tsv', 'jsonl')}
        existing = {p.name for p in work.glob(f'{model}_*.tsv')}
        existing |= {p.name for p in work.glob(f'{model}_*.jsonl')}
        need(existing == expected_names,
             f'{model}: missing or unexpected work chunk files: '
             f'{sorted(expected_names-existing)}, {sorted(existing-expected_names)}')
        for j in range(nchunks):
            group = target[j * 3:(j + 1) * 3]
            stem = f'{model}_{j:03d}'
            chunk_input = work / (stem + '.tsv')
            expected_text = ''.join(f'{ident}\t{ct}\n' for ident, ct in group)
            need(chunk_input.read_text(encoding='utf-8') == expected_text,
                 f'{stem}: stale or incorrect cached ciphertext input')
            chunk_output = parse_jsonl(work / (stem + '.jsonl'))
            need([r.get('id') for r in chunk_output] == [ident for ident, _ in group],
                 f'{stem}: cached output ids/order mismatch')
            for row in chunk_output:
                ident = row['id']
                need('best' in row, f'{stem}/{ident}: missing best candidate')
                check_best(row['best'], cts[ident], f'{stem}/{ident}')
                merged = raw[want_ids.index(ident)]['models'][model]
                need(row['best'] == merged,
                     f'{stem}/{ident}: cached best differs from frozen merged result')
                per_conv = row.get('per_convention')
                top = row.get('top')
                need(isinstance(per_conv, list) and len(per_conv) == 6 and
                     {b.get('convention') for b in per_conv} == CONVS,
                     f'{stem}/{ident}: incomplete six-convention alternative set')
                need(isinstance(top, list) and len(top) == 8,
                     f'{stem}/{ident}: incomplete top-eight alternative set')
                for kind, array in (('best', [row['best']]),
                                    ('per_convention', per_conv), ('top', top)):
                    for pos, item in enumerate(array):
                        check_best(item, cts[ident], f'{stem}/{ident}/{kind}[{pos}]')
                        verified_raw_candidates += 1
                        if ident == 'K4':
                            per_model_unique_k4[model].add((item['convention'],
                                                             item['plaintext'], item['key']))
            total_chunks += 1

    empirical = {}
    for model in MODES:
        top = raw[0]['models'][model]['total']
        null_scores = [r['models'][model]['total'] for r in raw[1:]]
        ties_or_better = sum(s >= top for s in null_scores)
        empirical[model] = {
            'k4_total': top, 'nulls': args.expected_nulls,
            'nulls_at_or_above': ties_or_better,
            'plus_one_rank_p': (ties_or_better + 1) / (args.expected_nulls + 1),
            'strictly_above_all_nulls': ties_or_better == 0,
        }
    pmin = min(o['plus_one_rank_p'] for o in empirical.values())
    return {
        'kind': 'R63 read-only postfreeze cryptographic and source audit',
        'verified_remote_git_freeze': False,
        'remote_git_freeze_caveat': 'Separately verify a successful remote Git freeze commit before any reveal or claim.',
        'known_k4_plaintext_used': False,
        'rows_verified': len(raw), 'full_length_forward_witnesses_passed': len(raw) * len(MODES),
        'cached_chunks_verified': total_chunks, 'manifest': manifest_info,
        'work_seal': seal_info,
        'raw_best_and_alternative_witnesses_passed': verified_raw_candidates,
        'unique_frozen_k4_candidates_by_model': {
            mode: len(per_model_unique_k4[mode]) for mode in MODES},
        'per_model_rank_only': empirical,
        'familywise_bonferroni_upper_bound': min(1., 2 * pmin),
        'interpretation_caveat': 'Ranks require exchangeable shuffled nulls; familywise bound covers only two fixed models. No plaintext validation or correct-key claim.',
        'work_hash_caveat': 'WORK_FREEZE.sha256 commits to raw alternatives locally. The remote Git commit must contain the manifest and ALL listed work/ files; verify remote provenance separately.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('input', 'frozen', 'root', 'solver-binary', 'english-lm', 'keydir'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--expected-nulls', type=int, default=100)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        result = audit(args)
        if args.report:
            args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(json.dumps(result, indent=2, sort_keys=True))
    except (AuditError, ValueError, OSError, KeyError) as e:
        parser.exit(1, f'R63 INDEPENDENT AUDIT FAILED: {e}\n')


if __name__ == '__main__':
    main()