#!/usr/bin/env python3
"""Run the hash-pinned pilot in a reduced allowlisted sandbox with budget and complete resource record.
No released K4 plaintext or crib positions are read by this script.
"""
import csv,hashlib,json,os,pathlib,resource,shutil,signal,subprocess,sys,time
ROOT=pathlib.Path('/mnt/data/k4_r85')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=4:raise SystemExit('usage: run_local_bounded.py LABEL TARGET_PATH BUDGET_SECONDS')
    tag=sys.argv[1];inputpath=pathlib.Path(sys.argv[2]);limit=int(sys.argv[3]);assert 0<limit<=3600
    expected={id:ct for id,ct in csv.reader(inputpath.open(),delimiter='\t')}
    assert len(expected) in (20,101) and all(len(x)==97 and x.isalpha() and x.isupper() for x in expected.values())
    sb=ROOT/f'isolated_{tag}';sb.mkdir(exist_ok=False)
    for name in ('rotor','gram2.bin','gram3.bin','gram4.bin','generic_words.txt'):
        shutil.copy2(ROOT/name,sb/name)
    shutil.copy2(inputpath,sb/'INPUT.tsv')
    output=sb/'RESULTS.tsv'; outlog=sb/'STDERR.log';log=sb/'RESOURCE_LOG.json'
    def restrict():
        resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    cmd=[str(sb/'rotor'),str(sb/'INPUT.tsv'),str(output),str(sb),'1','4','80','16000','8600']
    start=time.monotonic();state='INCOMPLETE';err='';ret=None
    with outlog.open('wb') as ferr:
        pr=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=ferr,cwd=sb,preexec_fn=restrict,start_new_session=True)
        try:ret=pr.wait(timeout=limit)
        except subprocess.TimeoutExpired:
            os.killpg(pr.pid,signal.SIGKILL);ret=pr.wait();err='WALL_TIME_LIMIT_EXCEEDED'
    elapsed=time.monotonic()-start
    try:
        rows=list(csv.DictReader(output.open(),delimiter='\t'))
        complete=len(rows)==6*len(expected) and all(len(x['PLAINTEXT'])==97 and x['ID'] in expected and len(x['INVW'])==26 for x in rows)
    except Exception as e:complete=False;rows=[];err+=' '+str(e)
    if ret==0 and complete and not err:state='COMPLETE'
    result={'state':state,'tag':tag,'returncode':ret,'error':err,'duration_seconds':round(elapsed,4),'memory_limit_mb':1024,'wall_budget_seconds':limit,'target_count':len(expected),'candidate_count':len(rows),'expected_candidates':6*len(expected),'target_sha256':sha(inputpath),'solver_sha256':sha(sb/'rotor'),'stdout_data_sha256':sha(output) if output.exists() else None,'parent_pid':os.getpid()}
    log.write_text(json.dumps(result,indent=2)+'\n')
    print(result,flush=True)
    return 0 if state=='COMPLETE' else 1
if __name__=='__main__':raise SystemExit(main())
