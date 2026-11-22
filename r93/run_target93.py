#!/usr/bin/env python3
"""R93 registered CRIB_ASSISTED aggregate audit. Use only after published GO.

No reference decoder or cipher solver is imported. The only target output is
aggregate compatibility counts and reproducibility metadata. Run through the
aggregate resource wrapper, then publish a freeze before interpreting counts.
"""
import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import random
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import runner93 as run

PREREG_COMMIT="567f418961cc18847207008468679115074f4c93"
PREREG_SHA="8fe62792c91e7b58706effd2bc1c951c730fa232dbf628f9f183eb0af23fe941"
CIPHERTEXT_FILE_SHA="2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CLUE_SOURCE_SHA="63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"


def committed_bytes(commit,name):
    if not re.fullmatch(r"[0-9a-f]{40}",commit):
        raise ValueError("full immutable commit SHA required")
    subprocess.run(["git","merge-base","--is-ancestor",commit,"HEAD"],cwd=ROOT,check=True)
    return subprocess.check_output(["git","show",f"{commit}:{name}"],cwd=ROOT)


def validate_prerequisites(source_commit,gate_commit):
    qa=json.loads((HERE/"QA_MANIFEST.json").read_text())
    checks=(qa.get("schema")=="k4-qa-v2",qa.get("mode")=="crib_assisted",
            qa.get("gate_type")=="EXACT_CHECKER_CORRECTNESS",
            qa.get("blind_recovery_certified") is False,qa.get("gate_verdict")=="GO",
            qa.get("preregistration_commit")==PREREG_COMMIT,
            qa.get("preregistration_sha256")==PREREG_SHA,
            qa.get("synthetic_gate_path")=="r93/holdout/CHECKER_GATE.json")
    if not all(checks):
        raise ValueError("QA does not authorize the registered exact-only gate")
    budget=qa["resource_budget"]
    if (budget["max_wall_seconds"],budget["max_cpu_seconds"],budget["max_ram_mb"],
        budget["max_candidates"],budget["max_retries"],budget["max_decoded_candidates"],
        budget["max_surviving_setting_outputs"],budget["max_aggregate_records"]) != (1800,1200,512,1,0,0,0,201):
        raise ValueError("target budget differs from registration")
    if run.sha_bytes(committed_bytes(PREREG_COMMIT,"r93/PREREGISTRATION.md"))!=PREREG_SHA:
        raise ValueError("preregistration commit/hash mismatch")
    sources=run.verify_protocol(ROOT,source_commit)
    gate_path="r93/holdout/CHECKER_GATE.json"
    gate_data=committed_bytes(gate_commit,gate_path)
    if gate_data!=(ROOT/gate_path).read_bytes():
        raise ValueError("gate bytes differ from published gate commit")
    gate=json.loads(gate_data)
    if (gate.get("gate_verdict")!="GO" or gate.get("status")!="COMPLETE"
        or gate.get("gate_type")!="EXACT_CHECKER_CORRECTNESS"
        or gate.get("blind_recovery_certified") is not False
        or gate.get("source_commit")!=source_commit or gate.get("sources")!=sources):
        raise ValueError("gate is incomplete, failed, or covers different source")
    resource_path="r93/holdout/VALIDATION_RESOURCE.json"
    resource_data=committed_bytes(gate_commit,resource_path)
    if resource_data!=(ROOT/resource_path).read_bytes():
        raise ValueError("gate resource bytes differ from published commit")
    resource=json.loads(resource_data)
    if (resource["status"]!="COMPLETE" or resource["exit_code"]!=0
        or resource["wall_seconds"]>180 or resource["cpu_seconds"]>120
        or resource["max_rss_mb"]>512):
        raise ValueError("gate did not complete within its registered resource cap")
    manifest_path="r93/holdout/GATE_FROZEN.sha256"
    frozen=committed_bytes(gate_commit,manifest_path)
    if frozen!=(ROOT/manifest_path).read_bytes():
        raise ValueError("gate freeze manifest changed")
    covered=set()
    for line in frozen.decode().splitlines():
        expected,name=line.split(maxsplit=1)
        if name in covered or run.sha_file(ROOT/name)!=expected:
            raise ValueError("gate freeze hash mismatch or duplicate")
        if run.sha_bytes(committed_bytes(gate_commit,name))!=expected:
            raise ValueError("gate artifact absent or changed at gate commit")
        covered.add(name)
    if not {gate_path,resource_path,"r93/PROTOCOL.sha256"}<=covered:
        raise ValueError("incomplete gate freeze membership")
    if source_commit==gate_commit or PREREG_COMMIT in (source_commit,gate_commit):
        raise ValueError("preregistration, source and gate must be separate commits")
    subprocess.run(["git","merge-base","--is-ancestor",PREREG_COMMIT,source_commit],cwd=ROOT,check=True)
    subprocess.run(["git","merge-base","--is-ancestor",source_commit,gate_commit],cwd=ROOT,check=True)
    return {"preregistration_commit":PREREG_COMMIT,"preregistration_sha256":PREREG_SHA,
            "source_commit":source_commit,"gate_commit":gate_commit,"source_sha256":sources,
            "gate_sha256":run.sha_bytes(gate_data),"gate_resource_sha256":run.sha_bytes(resource_data)}


def observations():
    path=ROOT/"r73/sealed/reveal_k4.py"
    if run.sha_file(path)!=CLUE_SOURCE_SHA:
        raise ValueError("published observation source changed")
    module=ast.parse(path.read_text())
    found=[]
    for node in module.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="CLUES" for t in node.targets):
            found.append(ast.literal_eval(node.value))
    if len(found)!=1:
        raise ValueError("expected one literal CLUES assignment")
    positions=[]; letters=[]
    for start,text in found[0]:
        for offset,letter in enumerate(text):
            positions.append(start+offset);letters.append(letter)
    if (len(positions)!=24 or len(set(positions))!=24 or any(p<0 or p>=97 for p in positions)
        or any(c not in run.AZ for c in letters)):
        raise ValueError("invalid observation domain")
    return positions,"".join(letters)


def target_inputs():
    original=(ROOT/"r39/ic_gate/k4_ciphertext.txt").read_bytes()
    if run.sha_bytes(original)!=CIPHERTEXT_FILE_SHA:
        raise ValueError("canonical ciphertext source hash mismatch")
    ciphertext=original.decode("ascii").strip()
    if len(ciphertext)!=97 or any(c not in run.AZ for c in ciphertext):
        raise ValueError("invalid canonical ciphertext length/alphabet")
    rng=random.Random(930400)
    inputs=[("K4",ciphertext)]
    seen={ciphertext}
    draws=0
    while len(inputs)<201 and draws<10000:
        letters=list(ciphertext);rng.shuffle(letters);draws+=1
        shuffled="".join(letters)
        if shuffled in seen:
            continue
        seen.add(shuffled)
        inputs.append((f"SHUF_{len(inputs)-1:03d}",shuffled))
    if len(inputs)!=201:
        raise RuntimeError("shuffle draw cap exhausted")
    if any(Counter(ct)!=Counter(ciphertext) for _,ct in inputs):
        raise RuntimeError("shuffle frequency mismatch")
    return inputs,draws


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-commit",required=True)
    parser.add_argument("--gate-commit",required=True)
    parser.add_argument("--out-dir",type=Path,required=True)
    parser.add_argument("--binary",type=Path,required=True)
    args=parser.parse_args()
    if args.out_dir.exists():
        raise ValueError("output directory already exists; no overwrite or automatic retry")
    receipt=validate_prerequisites(args.source_commit,args.gate_commit)
    # All prospective prerequisites are checked before either target input or
    # the published observation literal is read.
    positions,letters=observations()
    inputs,draws=target_inputs()
    args.out_dir.mkdir(parents=True)
    incoming="id\tciphertext\n"+"".join(f"{rid}\t{ct}\n" for rid,ct in inputs)
    (args.out_dir/"INPUTS.tsv").write_text(incoming)
    receipt["input_sha256"]=run.sha_file(args.out_dir/"INPUTS.tsv")
    receipt["canonical_ciphertext_file_sha256"]=CIPHERTEXT_FILE_SHA
    receipt["observation_source_sha256"]=CLUE_SOURCE_SHA
    receipt["shuffle_seed"]=930400
    receipt["shuffle_draws"]=draws
    receipt["build"]=run.build(HERE/"checker93.cpp",args.binary)
    results,stream=run.scan(args.binary,inputs,positions,letters)
    if len(results)!=201 or set(results)!={rid for rid,_ in inputs}:
        raise RuntimeError("aggregate result membership mismatch")
    report={"status":"COMPLETE","mode":"CRIB_ASSISTED_AGGREGATE_ONLY",
            "interpretive_verdict_deferred_until_published_freeze":True,
            "gate_type":"EXACT_CHECKER_CORRECTNESS","blind_recovery_certified":False,
            "inputs":results,"settings_per_input":145728,"input_count":201,
            "base_setting_input_calls":145728*201,
            "logical_exact_or_one_deletion_tests":145728*201*25,
            "observations":24,"count_arithmetic":"Python int","kernel_stream":stream,
            "decoded_plaintexts":0,"wiring_completions":0,"published_surviving_settings":0,
            "candidate_or_strength_ranking":False}
    (args.out_dir/"AGGREGATES.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    (args.out_dir/"SOURCE_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"COMPLETE","inputs":201,"settings_per_input":145728,
                      "interpretation":"WAIT_FOR_PUBLISHED_OUTPUT_FREEZE"}))


if __name__=="__main__":
    main()
