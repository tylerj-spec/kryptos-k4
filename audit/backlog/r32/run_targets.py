#!/usr/bin/env python3
"""Post-freeze historical audit only. Must run through run_bounded_agg.py.

No candidate ranking or plaintext output. R32 counts fixed-setting constraints;
R41 counts partial bijections without completing an alphabet. Sources and plans
must exist in the supplied published commits before the target is read.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('independent_history_helpers',HERE/'check_replay.py')
H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
ANCHORS={21+i:c for i,c in enumerate('EASTNORTHEAST')}|{63+i:c for i,c in enumerate('BERLINCLOCK')}
CAS=('AZ','KRY','PALP','ABSP','ACAKRY','ACAPAL','ACAABS')
EXPECTED_SOURCES={'CARTER':'6761a5075869325f708e1d81f8bd0efeeab5aaaad43206e1551ed53243f13ee0',
                  'K1K3':'bb6b5b03500084ccd45bd93ab7a63ab986026e83e6a84aa2b93cb8824d3281b5'}
K4_RAW_SHA256='2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3'


def pinned(path,commit):
    raw=subprocess.check_output(['git','show',f'{commit}:{path.relative_to(ROOT)}'],cwd=ROOT)
    assert hashlib.sha256(raw).hexdigest()==H.sha(path),f'unpublished source change: {path}'


def clean(path):
    return ''.join(c for c in path.read_text().upper() if 'A'<=c<='Z')


def header(path):
    ans={}
    for line in path.read_text().splitlines():
        if line.startswith('# '):
            k,v=line[2:].split('\t',1)
            if k!='min_setting':ans[k]=int(v)
    return ans


def key_index(family,label,source):
    fields=label.split('/')
    if family in ('G5','C6'):
        return int(fields[-1].removeprefix('primer'))
    direction,num,offset=fields[-3:]
    return ((direction=='rev')*2+(num=='KRY'))*(len(source)-96)+int(offset.removeprefix('off'))


def fixed_witness(ct,setting,sources,sets):
    fam,name,order,keylabel,pa,ca,op=setting.split('|')
    route=next(r for r in sets['r32_f1']+sets['r32_f2'] if r[:2]==(name,order))
    index=key_index(fam,keylabel,sources.get(fam,''));key=H.key_at(fam,index,sources.get(fam,''))
    p_al=H.ALPH[int(pa=='PA=KRY')];c_al=H.ALPH[int(ca=='CA=KRY')];operation=int(op.removeprefix('OP='));q=H.inverse(route[2])
    correct=0
    for pos,want in ANCHORS.items():
        at=pos if order=='ID' else q[pos];ki=at if order=='T_then_S' else pos
        c,p=c_al.index(ct[at]),p_al.index(want)
        needed=(c-p if operation==0 else c+p if operation==1 else p-c)%26
        correct+=key[ki]==needed
    return correct


def run32(a,sets,sources,report):
    prior=json.loads((ROOT/'k4kit/r32/runs/WHOLE_FAMILY.json').read_text())
    ctpath=ROOT/'k4kit/r32/runs/k4_ciphertext.txt';assert H.sha(ctpath)==K4_RAW_SHA256;ct=clean(ctpath)
    want=''.join(ANCHORS.get(i,'?') for i in range(97))
    report['input_sha256']={str(ctpath.relative_to(ROOT)):H.sha(ctpath)}
    report['archive_sha256']=H.sha(ROOT/'k4kit/r32/runs/WHOLE_FAMILY.json')
    report['full_histogram_prior_available']=False
    report['jobs']={};report['status']='RUNNING'
    for tag,family,routekey in (('F1_CARTER','CARTER','r32_f1'),('F1_K1K3','K1K3','r32_f1'),('F1_G5','G5','r32_f1'),('F1_C6','C6','r32_f1'),('F2_G5','G5','r32_f2')):
        with tempfile.TemporaryDirectory(prefix='kryptos_R32_audit_') as td:
            result=H.kernel(a.binary,Path(td),32,family,ct,want,sets[routekey],sources.get(family,''),tag=tag)
        expected_keys=(100000 if family=='G5' else 1000000 if family=='C6' else 4*(len(sources[family])-96))
        hist=result['histogram'];maximum=max(i for i,n in enumerate(hist) if n)
        computed={'settings':int(len(sets[routekey]))*int(expected_keys)*12,'max':maximum,'full24':int(hist[24]),
                  'count_ge':{str(i):sum(hist[i:]) for i in range(8,13)},'histogram':hist,
                  'archived_max_witness_matches':fixed_witness(ct,prior[tag]['best_setting'],sources,sets),
                  'kernel_wall_seconds':result['wall_seconds']}
        computed['matches_archive']=(computed['settings']==prior[tag]['settings']==sum(hist)==result['settings'] and
             computed['max']==prior[tag]['max']==computed['archived_max_witness_matches'] and
             computed['full24']==len(prior[tag]['full24']) and computed['count_ge']==prior[tag]['count_ge'])
        report['jobs'][tag]=computed;a.out.write_text(json.dumps(report,indent=2)+'\n')
        if not computed['matches_archive'] or computed['full24']:
            report['status']='STOP_MISMATCH_OR_SURVIVOR';a.out.write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(3)
    report['total_settings']=sum(j['settings'] for j in report['jobs'].values())
    report['status']='COMPLETE_FULL_RECOUNT_ALL_RETAINED_STATISTICS_AGREE'
    report['scope_limit']='New full histograms; original bins0-7 were not retained. No language or posterior probability inference.'


def run41(a,sets,sources,report):
    exp=ROOT/'r41/x1_route_pafree';truth=json.loads((ROOT/'r41/sealed/truth.json').read_text())
    report['input_sha256']={};report['archive_sha256']={};report['jobs']={};report['plants_verified']=[];report['status']='RUNNING'
    for tag in ['K4','NULL_00','NULL_01']+sorted(truth):
        ctp=exp/f'{tag}_ct.txt'
        if tag=='K4':assert H.sha(ctp)==K4_RAW_SHA256
        ct=clean(ctp);report['input_sha256'][str(ctp.relative_to(ROOT))]=H.sha(ctp)
        if tag in truth:
            t=truth[tag];want=''.join(t['plaintext'][i] if i in ANCHORS else '?' for i in range(97))
            route=(t['route'],'S_then_T',t['perm']);op=('VIG','BEAU','VARB').index(t['op'])
            assert H.encrypt(t['plaintext'],t['key'],t['pa'],H.ALPH[CAS.index(t['ca'])],op,route)==ct
            assert H.free_feasible(ct,want,t['key'],H.ALPH[CAS.index(t['ca'])],int(t['op']=='VARB'),route)
            report['plants_verified'].append(tag)
        else:want=''.join(ANCHORS.get(i,'?') for i in range(97))
        report['jobs'][tag]={}
        for part,families in (('A',('G5','C6','CARTER','K1K3')),('B',('G5','K1K3'))):
            rows=sets['r41_'+part];prior_path=exp/'out'/f'WF_{tag}_{part}.tsv';previous=header(prior_path)
            report['archive_sha256'][str(prior_path.relative_to(ROOT))]=H.sha(prior_path)
            detail={};total=consistent=0
            for fam in families:
                with tempfile.TemporaryDirectory(prefix='kryptos_R41_audit_') as td:
                    result=H.kernel(a.binary,Path(td),41,fam,ct,want,rows,sources.get(fam,''),tag=tag+'_'+part+'_'+fam)
                expected_keys=(100000 if fam=='G5' else 1000000 if fam=='C6' else 4*(len(sources[fam])-96))
                expected=int(expected_keys)*int(len(rows))*14
                assert result['settings']==expected
                total+=expected;consistent+=result['consistent']
                detail[fam]={k:result[k] for k in ('keys','settings','consistent','index_hits','wall_seconds')}
            result={'settings':total,'consistent':consistent,'families':detail,
                    'matches_archive':total==previous['settings'] and consistent==previous['consistent_settings(V=0)']}
            report['jobs'][tag][part]=result;a.out.write_text(json.dumps(report,indent=2)+'\n')
            if not result['matches_archive'] or (tag=='K4' and consistent):
                report['status']='STOP_MISMATCH_OR_TARGET_SURVIVOR';a.out.write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(3)
    report['total_labeled_settings']=sum(v['settings'] for r in report['jobs'].values() for v in r.values())
    report['status']='COMPLETE_FULL_FEASIBILITY_COUNTS_AGREE'
    report['scope_limit']='Complete algebraic feasibility join; not the historical full violation histogram or positive minimum-V statistic.'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--round',choices=['32','41'],required=True);ap.add_argument('--binary',type=Path,required=True)
    ap.add_argument('--carter',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--plan-commit',required=True);ap.add_argument('--code-commit',required=True);a=ap.parse_args()
    plan=HERE/'PLAN.md' if a.round=='32' else ROOT/'r41/audit/backlog_closeout/PLAN.md'
    for f in (plan,plan.parent/'BUDGET.json',HERE/'replay_kernel.cpp',HERE/'check_replay.py',HERE/'SYNTHETIC.json'):
        pinned(f,a.plan_commit)
    for f in (Path(__file__).resolve(),HERE/'ARCHIVE_FORMAT_AMENDMENT.md'):
        pinned(f,a.code_commit)
    tests=json.loads((HERE/'SYNTHETIC.json').read_text())
    assert tests['pretarget_decision']['R'+a.round]==('FULL' if a.round=='32' else 'FULL_FEASIBILITY')
    assert tests['source_sha256']=={'kernel':H.sha(HERE/'replay_kernel.cpp'),'checker':H.sha(HERE/'check_replay.py')}
    inputs={'CARTER':a.carter,'K1K3':ROOT/'k4kit/data/k1k3_plaintext.txt'}
    for family,p in inputs.items():assert H.sha(p)==EXPECTED_SOURCES[family]
    # A clean rebuild of the pinned source makes the executable provenance explicit.
    subprocess.run(['g++','-O3','-std=c++17','-march=native',str(HERE/'replay_kernel.cpp'),'-o',str(a.binary)],check=True)
    report={'round':a.round,'reviewer':'ChatGPT','mode':'POSTFREEZE_CRIB_ASSISTED_EXCLUSION_AUDIT',
            'plan_commit':a.plan_commit,'code_commit':a.code_commit,'plan_sha256':H.sha(plan),
            'source_sha256':{str(f.relative_to(ROOT)):H.sha(f) for f in (HERE/'replay_kernel.cpp',HERE/'check_replay.py',Path(__file__).resolve())},
            'key_source_sha256':EXPECTED_SOURCES,'binary_sha256':H.sha(a.binary),'synthetic_sha256':H.sha(HERE/'SYNTHETIC.json')}
    sets=H.route_sets();report['independent_route_sha256']={k:hashlib.sha256(''.join(f'{n} {o} {",".join(map(str,p))}\n' for n,o,p in rows).encode()).hexdigest() for k,rows in sets.items()}
    sources={k:clean(p) for k,p in inputs.items()}
    (run32 if a.round=='32' else run41)(a,sets,sources,report)
    a.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'round':a.round,'status':report['status'],'settings':report.get('total_settings',report.get('total_labeled_settings'))}))


if __name__=='__main__':main()
