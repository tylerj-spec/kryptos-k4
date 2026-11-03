#!/usr/bin/env python3
"""R62 OLD R59/R61 published-letter audit strictly AFTER verifying the historical remote freezes.
Never supplies known K4 letters or positions to a cipher solver, scorer, generator or reranker.
Reads ONLY already frozen 97-letter raw outputs from historical rounds.
"""
import json,sys,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
KNOWN={21+i:x for i,x in enumerate("EASTNORTHEAST")}
KNOWN.update({63+i:x for i,x in enumerate("BERLINCLOCK")})
assert len(KNOWN)==24
def load(path):
    return [json.loads(l) for l in (ROOT/path).read_text().splitlines() if l.strip()]
def hits(p):
    assert len(p)==97
    return sum(p[i]==c for i,c in KNOWN.items())
def main():
    if len(sys.argv)!=3:raise SystemExit("afterfreeze_old.py VERIFIED_PRE_REPORT OUT")
    prev,out=sys.argv[1:]
    assert not Path(out).exists()
    audit=json.loads(Path(prev).read_text())
    assert audit["all_historical_freeze_checks_pass"]
    assert audit["all_original_forward_outputs_independently_valid"]
    assert audit["historical_control_gates_recomputed_identically"]
    # The source/input/results SHA256 entries must match even if a rebuilt compiler produced
    # different binary bytes; a missing or differing historical binary is recorded separately.
    for m in audit["manifests"]:
        for entry in m["entries"]:
            if entry["label"] not in ("language_model","solver_binary"):
                assert entry["status"]=="MATCH",(m["name"],entry)
    expected59=json.loads((ROOT/"r59/k4/REVEAL.json").read_text())
    expected61=json.loads((ROOT/"r61/k4/REVEAL.json").read_text())
    r59=load("r59/k4/run/RESULTS.jsonl")
    r61=load("r61/k4/run/RESULTS.jsonl")
    assert len(r59)==len(r61)==101 and r59[0]["id"]==r61[0]["id"]=="K4"
    a,b=r59[0]["best"],r61[0]["best"]
    n59=sum(x["best"]["total"]>=a["total"] for x in r59[1:])
    n61=sum(x["best"]["total"]>=b["total"] for x in r61[1:])
    vals59=sorted(x["best"]["total"] for x in r59[1:])
    vals61=sorted(x["best"]["total"] for x in r61[1:])
    gap=lambda row:row["stage1"][0]["total"]-row["stage1"][1]["total"]
    origgap=gap(r61[0])
    gnulls=sorted(gap(x) for x in r61[1:])
    data={
      "classification":"R62_AFTER_HISTORICAL_REMOTE_FREEZE_ONLY_NO_SOLVER_REUSE",
      "R59":{
        "K4_score":a["total"],"nulls_at_or_above":n59,
        "empirical_plus_one_rank":(n59+1)/101,
        "K4_best_public_hits":[hits(a["plaintext"]),hits(a["key"])],
        "top8_public_hits":[[hits(x["plaintext"]),hits(x["key"])] for x in r59[0]["top"]],
        "null_median":statistics.median(vals59),"null_max":max(vals59),
        "old_report_reproduced":(
           n59==expected59["nulls_at_or_above_k4"] and
           vals59==expected59["null_totals_sorted"] and
           [hits(a["plaintext"]),hits(a["key"])]==[
             expected59["k4_best_clue_hits"]["plaintext_stream"],
             expected59["k4_best_clue_hits"]["key_stream"]])
      },
      "R61":{
        "K4_score":b["total"],"nulls_at_or_above":n61,
        "empirical_plus_one_rank":(n61+1)/101,
        "K4_best_public_hits":[hits(b["plaintext"]),hits(b["key"])],
        "null_median":statistics.median(vals61),"null_max":max(vals61),
        "stage1_route_gap":origgap,"stage1_null_gap_max":max(gnulls),
        "stage1_null_gaps_at_or_above_original":sum(v>=origgap for v in gnulls),
        "stage1_null_gap_median":statistics.median(gnulls),
        "old_report_reproduced":(
           n61==expected61["nulls_at_or_above_k4"] and
           vals61==expected61["null_totals_sorted"] and
           [hits(b["plaintext"]),hits(b["key"])]==[
             expected61["k4_best_clue_hits"]["text_A"],
             expected61["k4_best_clue_hits"]["text_B"]] and
           r61[0]["stage1"]==expected61["k4_stage1"])
      },
      "interpretation":"K4 output fixed before published-letter comparison. 21.2131 stage-one gap was posthoc selected, cannot be assigned 1/101 significance without new look-elsewhere calibration.",
      "limitations":["No new K4 run","No original K4 key or method recovered",
        "Separate frozen R59 and R61 old outputs only",
        "Retrospective stage-1 gap statistic is posthoc and uncorrected"]
    }
    with Path(out).open("x") as f:json.dump(data,f,sort_keys=True,indent=2);f.write("\n")
    print("R62 independent original reveal:",{r:data[r] for r in ("R59","R61")})
    if not(data["R59"]["old_report_reproduced"] and data["R61"]["old_report_reproduced"]):raise SystemExit(2)
if __name__=="__main__":main()
