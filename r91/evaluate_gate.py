#!/usr/bin/env python3
"""Reveal private synthetic truth only AFTER the complete output freeze is pushed."""
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import reference as R


def equivalent_linked(k1,k2,width):
    if k1 == k2:
        return True
    if len(k1) != len(k2):
        return False
    period = len(k1)*width
    return all(R.linked_encrypt(ch*period,k1,width)==R.linked_encrypt(ch*period,k2,width) for ch in R.AZ)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--round",required=True)
    ap.add_argument("--truth",required=True)
    ap.add_argument("--freeze-commit",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    rnd=Path(a.round).resolve(); repo=rnd.parent
    assert re.fullmatch(r"[0-9a-f]{40}",a.freeze_commit)
    frozen = set()
    for line in (rnd/"holdout/FROZEN.sha256").read_text().splitlines():
        h,p=line.split(maxsplit=1)
        assert hashlib.sha256((repo/p).read_bytes()).hexdigest()==h, p
        frozen.add(p)
    needed = ("holdout/R82_INPUT.jsonl", "holdout/PTAK_INPUT.jsonl", "holdout/TRUTH_SHA256",
              "holdout/run/R82_OUTPUT.jsonl", "holdout/run/PTAK_OUTPUT.jsonl",
              "holdout/run/R82_RESOURCE_LOG.json", "holdout/run/PTAK_RESOURCE_LOG.json",
              "holdout/run/WITNESSES.json", "PROTOCOL.sha256", "QA_MANIFEST.json")
    assert {"r91/" + p for p in needed} <= frozen
    for name in ("R82_RESOURCE_LOG.json", "PTAK_RESOURCE_LOG.json"):
        log = json.loads((rnd/"holdout/run"/name).read_text())
        assert log["status"] == "COMPLETE"
        assert log["wall_seconds"] <= 1800 and log["cpu_seconds"] <= 1800 and log["aggregate_peak_rss_mb"] <= 2048
    witness = json.loads((rnd/"holdout/run/WITNESSES.json").read_text())
    assert witness["all_forward_witnesses_pass"] and witness["r82_witnesses"] == 360 and witness["ptak_witnesses"] == 240
    raw=Path(a.truth).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==(rnd/"holdout/TRUTH_SHA256").read_text().strip()
    truth=json.loads(raw)
    public={}
    for name in ("R82_INPUT.jsonl","PTAK_INPUT.jsonl"):
        for line in (rnd/"holdout"/name).read_text().splitlines():
            r=json.loads(line);assert r["id"] not in public;public[r["id"]]=r
    out={}
    for line in (rnd/"holdout/run/R82_OUTPUT.jsonl").read_text().splitlines():
        r=json.loads(line);assert r["id"] not in out;out[r["id"]]=r
    for line in (rnd/"holdout/run/PTAK_OUTPUT.jsonl").read_text().splitlines():
        r=json.loads(line);rid=r["id"].split("__")[0];b=r["best"]
        assert rid not in out
        out[rid]={"id":rid,"arm":"PTAK_R68","plaintext":b["plaintext"],"key":b["key"],"objective":b["score4"]}
    assert set(out)==set(truth)==set(public) and len(out)==600
    counts={}; records=[]
    routes = [("ID", list(range(97)))]
    for line in (rnd/"routes.txt").read_text().splitlines():
        name, order, nums = line.split()
        assert order == "S_then_T"
        routes.append((name, list(map(int, nums.split(",")))))
    expected_l = {f"m{m}_w{w}" for m in (3,4,5,7,9,12) for w in (m,m+2,31)}
    expected_p = {f"L{lag}" for lag in range(13,25)}
    for rid,t in truth.items():
        b=out[rid];p=public[rid]
        assert t["arm"] == p["arm"] == b["arm"]
        assert len(t["plaintext"]) == 97 and set(t["plaintext"]) <= set(R.AZ)
        assert set(t["key"]) <= set(R.AZ)
        right=sum(x==y for x,y in zip(t["plaintext"],b["plaintext"]))
        assert len(b["plaintext"])==97
        if t["arm"]=="R82_LINKED":
            assert t["m"] == p["m"] and t["w"] == p["w"] and len(t["key"]) == t["m"]
            assert t["stratum"] == f'm{p["m"]}_w{p["w"]}' and t["stratum"] in expected_l
            key_ok=equivalent_linked(t["key"],b["key"],t["w"])
            witness=R.linked_encrypt(b["plaintext"],b["key"],t["w"])==p["ciphertext"]
        else:
            assert t["arm"] == "PTAK_R68"
            assert t["lag"] == p["lag"] and len(t["key"]) == t["lag"]
            assert t["stratum"] == f'L{p["lag"]}' and t["stratum"] in expected_p
            assert all(t[k] == p[k] for k in ("convention", "path", "model"))
            assert routes[p["path_index"]] == (p["path"], p["permutation"])
            key_ok=b["key"]==t["key"]
            witness=R.ptak_encrypt(b["plaintext"],b["key"],p["convention"],p["permutation"],p["model"])==p["ciphertext"]
        assert witness,rid
        c=counts.setdefault(t["arm"],{}).setdefault(t["stratum"],{"n":0,"exact_message_key":0,"plain97":0,"plain95":0,"key_exact":0,"key_equivalent":0})
        c["n"]+=1;c["exact_message_key"]+=int(right==97 and key_ok);c["plain97"]+=int(right==97)
        c["plain95"]+=int(right>=95);c["key_exact"]+=int(b["key"]==t["key"]);c["key_equivalent"]+=int(key_ok)
        records.append({"id":rid,"arm":t["arm"],"stratum":t["stratum"],"correct_letters":right,
                        "key_exact":b["key"]==t["key"],"key_equivalent":key_ok,"genre":t["genre"],"witness":True})
    decisions={}
    assert set(counts) == {"R82_LINKED", "PTAK_R68"}
    assert set(counts["R82_LINKED"]) == expected_l and set(counts["PTAK_R68"]) == expected_p
    for arm,strata in counts.items():
        assert all(c["n"]==20 for c in strata.values())
        failing=[s for s,c in strata.items() if c["exact_message_key"]<18]
        decisions[arm]={"outcome":"SOLVER_NO_POWER" if failing else "SCREEN_PASS_ONLY",
                        "failed_strata":failing,"passing_strata":[s for s in strata if s not in failing],
                        "full_unknown_family_gate":"NOT_ELIGIBLE_FAILURE_OF_MANDATORY_POWER_SCREEN" if failing else "NOT_PERFORMED_SCREEN_ALONE_INSUFFICIENT",
                        "k4_run_allowed":False}
    report={"round":"R91","label":"Preregistered fresh synthetic known-structure power screen; not method recognition",
            "freeze_commit":a.freeze_commit,"decisions":decisions,"strata":counts,"witnesses_passed":600,
            "truth_sha256":hashlib.sha256(raw).hexdigest(),"records":records,
            "scope_limit":"Only the pinned bounded solver attempts; cipher families remain OPEN. No K4 input, output or exclusion.",
            "independent_execution_review":"NONE"}
    Path(a.output).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"decisions":decisions,"strata":counts,"witnesses":600},indent=2),flush=True)


if __name__=="__main__":
    main()
