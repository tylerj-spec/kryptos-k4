#!/usr/bin/env python3
"""No-K4 synthetic regression tests for the R63 postfreeze auditor."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))

SPEC = importlib.util.spec_from_file_location('verify_frozen', Path(__file__).with_name('verify_frozen.py'))
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        p = Path(self.tmp.name)
        self.root, self.freeze, keydir = p / 'repo', p / 'freeze', p / 'keydir'
        self.root.mkdir()
        self.freeze.mkdir()
        keydir.mkdir()
        for relative in ('r63/blind/rk2_solve.cpp', 'r63/blind/run.py',
                         'r63/PREREGISTRATION.md', 'k4kit/data/word_model_orth.tsv',
                         'r39/ic_gate/k4_ciphertext.txt'):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture: ' + relative + '\n', encoding='utf-8')
        for file in v.KEY_FILES:
            (keydir / file).write_bytes(('fixture: ' + file).encode())
        solver, lm_en = p / 'rk2_solve', p / 'lm6_en.bin'
        solver.write_bytes(b'synthetic solver binary')
        lm_en.write_bytes(b'synthetic English LM')
        self.args = SimpleNamespace(
            input=p / 'TARGET.tsv', frozen=self.freeze, root=self.root,
            solver_binary=solver, english_lm=lm_en, keydir=keydir,
            expected_nulls=2, report=p / 'audit.json')
        pt = ('THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG' * 3)[:97]
        key = ('QWERTYUIOPASDFGHJKLZXCVBNM' * 4)[:97]
        ct = v.encode(pt, key, 'AZ_VIG')
        self.assertEqual(len(ct), 97)
        (self.root / 'r39/ic_gate/k4_ciphertext.txt').write_text(ct + '\n')
        cts = [ct, ct[1:] + ct[:1], ct[2:] + ct[:2]]
        self.ids = ['K4', 'NULL_000', 'NULL_001']
        self.args.input.write_text('id\tciphertext\n' + ''.join(
            f'{ident}\t{c}\n' for ident, c in zip(self.ids, cts)))
        self.rows = []
        self.raw_rows = []
        self.freeze.joinpath('work').mkdir()
        for pos, (ident, c) in enumerate(zip(self.ids, cts)):
            best = {'convention': 'AZ_VIG', 'plaintext': 'A' * 97,
                    'key': c, 'lm': -90., 'word': -8., 'total': -98. - pos}
            self.rows.append({'id': ident, 'models': {'CLOCK': best, 'GERMAN': best}})
            alts = []
            for conv in sorted(v.CONVS):
                alpha, op = conv.split('_')
                x = v.AZ if alpha == 'AZ' else v.KRY
                pa = x.index('A')
                idx = {char: i for i, char in enumerate(x)}
                if op == 'VIG':
                    k = ''.join(x[(idx[ch] - pa) % 26] for ch in c)
                elif op == 'BEAU':
                    k = ''.join(x[(idx[ch] + pa) % 26] for ch in c)
                else:
                    k = ''.join(x[(pa - idx[ch]) % 26] for ch in c)
                alts.append(dict(best, key=k, convention=conv))
            self.raw_rows.append({'id': ident, 'best': best,
                                  'per_convention': alts, 'top': alts + alts[:2]})
        (self.freeze / 'RESULTS.jsonl').write_text(''.join(
            json.dumps(r) + '\n' for r in self.rows))
        for mode in v.MODES:
            (self.freeze / 'work' / f'{mode}_000.tsv').write_text(''.join(
                f'{ident}\t{c}\n' for ident, c in zip(self.ids, cts)))
            (self.freeze / 'work' / f'{mode}_000.jsonl').write_text(''.join(
                json.dumps(r) + '\n' for r in self.raw_rows))
        self.write_manifest()
        self.write_work_seal()

    def tearDown(self):
        self.tmp.cleanup()

    def write_work_seal(self):
        files = [self.freeze / 'RESULTS.jsonl', self.freeze / 'FROZEN.sha256']
        for mode in v.MODES:
            for ext in ('tsv', 'jsonl'):
                files.append(self.freeze / 'work' / f'{mode}_000.{ext}')
        (self.freeze / 'WORK_FREEZE.sha256').write_text(''.join(
            f'{v.sha(path)}  {path.relative_to(self.freeze).as_posix()}\n'
            for path in files))

    def write_manifest(self):
        a = self.args
        files = [
            ('input', a.input), ('results', a.frozen / 'RESULTS.jsonl'),
            ('solver_source', a.root / 'r63/blind/rk2_solve.cpp'),
            ('solver_binary', a.solver_binary), ('english_lm', a.english_lm),
            ('english_words', a.root / 'k4kit/data/word_model_orth.tsv'),
        ] + [('key_model', a.keydir / f) for f in v.KEY_FILES] + [
            ('runner', a.root / 'r63/blind/run.py'),
            ('protocol', a.root / 'r63/PREREGISTRATION.md'),
        ]
        (a.frozen / 'FROZEN.sha256').write_text(''.join(
            f'{v.sha(p)}  {tag}  {p.name}\n' for tag, p in files))

    def test_full_synthetic_freeze_passes(self):
        rep = v.audit(self.args)
        self.assertEqual(rep['rows_verified'], 3)
        self.assertEqual(rep['full_length_forward_witnesses_passed'], 6)
        self.assertEqual(rep['cached_chunks_verified'], 2)
        self.assertEqual(rep['raw_best_and_alternative_witnesses_passed'], 90)
        self.assertEqual(rep['work_seal']['entries_verified'], 6)
        self.assertEqual(rep['manifest']['entries_verified'], 12)
        self.assertFalse(rep['verified_remote_git_freeze'])
        self.assertEqual(rep['per_model_rank_only']['CLOCK']['plus_one_rank_p'], 1/3)

    def test_stale_cache_detected_even_with_valid_frozen_results(self):
        p = self.freeze / 'work/CLOCK_000.tsv'
        p.write_text(p.read_text().replace('NULL_001', 'NULL_999'))
        self.write_work_seal()
        with self.assertRaisesRegex(v.AuditError, 'stale or incorrect'):
            v.audit(self.args)

    def test_edited_solver_is_detected_by_manifest(self):
        p = self.root / 'r63/blind/rk2_solve.cpp'
        p.write_text('malicious/untracked change')
        with self.assertRaisesRegex(v.AuditError, 'SHA-256 mismatch'):
            v.audit(self.args)

    def test_witness_failure_detected_even_if_result_hash_is_updated(self):
        self.rows[0]['models']['CLOCK'] = dict(self.rows[0]['models']['CLOCK'], key='Z' * 97)
        (self.freeze / 'RESULTS.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in self.rows))
        self.write_manifest()
        with self.assertRaisesRegex(v.AuditError, 'witness FAILED'):
            v.audit(self.args)

    def test_missing_chunk_detected(self):
        (self.freeze / 'work/GERMAN_000.jsonl').unlink()
        with self.assertRaisesRegex(v.AuditError, 'WORK_FREEZE missing file'):
            v.audit(self.args)

    def test_alternate_checker_looks_only_at_existing_raw_candidates(self):
        import reveal_alternates
        res = reveal_alternates.examine(self.freeze, lambda s: 24 if s == 'A' * 97 else 0)
        self.assertEqual(res['CLOCK']['frozen_k4_alternative_count'], 6)
        self.assertEqual(res['CLOCK']['postfreeze_candidates_24_of_24'], 6)
        self.assertEqual(res['GERMAN']['postfreeze_candidates_at_least_10_of_24'], 6)

    def test_output_report_cannot_modify_freeze(self):
        self.args.report = self.freeze / 'new_report.json'
        with self.assertRaisesRegex(v.AuditError, 'outside the frozen'):
            v.audit(self.args)


if __name__ == '__main__':
    unittest.main()