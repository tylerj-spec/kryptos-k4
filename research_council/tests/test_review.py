#!/usr/bin/env python3
"""Run: python3 -I research_council/tests/test_review.py (no network or LLM)."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'review.py'
BRIEF = ROOT / 'briefs' / 'r75.json'


def run(*args, ok=True):
    p = subprocess.run([sys.executable, '-I', str(CLI), *map(str, args)], text=True, capture_output=True)
    if ok and p.returncode:
        raise AssertionError(p.stderr + p.stdout)
    if not ok and p.returncode == 0:
        raise AssertionError('expected failure but succeeded')
    return p


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = root / 'run'
        run('prepare', '--brief', BRIEF, '--out', d)
        assert all((d / 'phase1' / (seat + '.md')).exists() for seat in ('alpha','beta','gamma'))
        manifest = json.loads((d / 'manifest.json').read_text())
        assert len(manifest['files']) == 4
        assert manifest['seats'] == {}
        run('prepare', '--brief', BRIEF, '--out', d, ok=False)
        roster = root / 'roster.json'
        roster.write_text(json.dumps({'alpha':{'family':'anthropic','model':'model-one'},'beta':{'family':'openai','model':'model-two'},'gamma':{'family':'google','model':'model-three'}}))
        reps = []
        for i, seat in enumerate(('alpha','beta','gamma')):
            p = root / (seat + '.md')
            p.write_text('Reviewer ' + seat + ': ' + ('This assessment is an independently written synthetic test fixture. ' * (3+i)))
            reps.extend(['--'+seat,p])
        run('triage','--out',d,'--roster',roster,*reps)
        t=(d/'phase2'/'triage.md').read_text()
        assert t.find('Reviewer beta') < t.find('Reviewer gamma') < t.find('Reviewer alpha')
        assert 'model-one' not in t and 'model-two' not in t
        run('attack','--out',d,'--leader','B','--consensus','partial')
        assert (d/'phase3'/'attack_A.md').exists() and (d/'phase3'/'attack_C.md').exists()
        assert not (d/'phase3'/'attack_B.md').exists()
        p1,p2=root/'attack_a.md',root/'attack_c.md'
        p1.write_text('Synthetic adversarial critique A: a mathematical equivalence audit must be checked independently.')
        p2.write_text('Synthetic adversarial critique C: the false-positive rate must be calibrated on matched nulls.')
        run('verdict','--out',d,'--attack-a',p1,'--attack-c',p2)
        assert (d/'phase4'/'verdict.md').exists()
        run('verdict','--out',d,'--attack-a',p1,'--attack-c',p2,ok=False)
        assert len(json.loads((d/'manifest.json').read_text())['files']) == 13
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        b=json.loads(BRIEF.read_text())
        b['sources'].append('r53/BLIND_RULES.md')
        invalid=root/'invalid.json'; invalid.write_text(json.dumps(b))
        run('prepare','--brief',invalid,'--out',root/'bad',ok=False)
        b=json.loads(BRIEF.read_text()); b['facts'].append({'claim':'secret','basis':'hypothesis','source':'none','known_plaintext':'hidden'})
        invalid.write_text(json.dumps(b))
        run('prepare','--brief',invalid,'--out',root/'bad2',ok=False)
        run('prepare','--brief',BRIEF,'--out',root/'run')
        (root/'run'/'phase1'/'alpha.md').write_text('tampered')
        roster=root/'roster.json';roster.write_text(json.dumps({'alpha':{'family':'anthropic','model':'x'},'beta':{'family':'openai','model':'y'},'gamma':{'family':'google','model':'z'}}))
        for s in ('alpha','beta','gamma'):
            (root/(s+'.md')).write_text('A genuine independent response would be provided by a model provider. '*3 + s)
        args=['triage','--out',root/'run','--roster',roster]
        for s in ('alpha','beta','gamma'):
            args.extend(['--'+s,root/(s+'.md')])
        run(*args,ok=False)
        # Even without file tampering, a three-seat roster cannot claim diversity
        # when two seats use the same family (model identities remain self-reported).
        run('prepare','--brief',BRIEF,'--out',root/'fresh')
        roster.write_text(json.dumps({'alpha':{'family':'anthropic','model':'x'},'beta':{'family':'anthropic','model':'y'},'gamma':{'family':'google','model':'z'}}))
        args2=['triage','--out',root/'fresh','--roster',roster]
        for s in ('alpha','beta','gamma'):
            args2.extend(['--'+s,root/(s+'.md')])
        run(*args2,ok=False)
    print('PASS: offline review-workflow tests: independent prompts, anonymous triage, attack/verdict, hash freeze, no overwrite, source whitelist, forbidden structured fields, tamper rejection and distinct family check. All external reviews are MOCK fixtures.')

if __name__=='__main__':
    main()
