#!/usr/bin/env python3
"""R57 isolated published-letter check AFTER remote-freeze and forward-witness audit."""
import hashlib,json,sys
from pathlib import Path
KNOWN={21+i:x for i,x in enumerate("EASTNORTHEAST")}
KNOWN.update({63+i:x for i,x in enumerate("BERLINCLOCK")})
assert len(KNOWN)==24
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=5:raise SystemExit("reveal.py FROZEN_RESULTS MANIFEST FORWARD_AUDIT OUT")
    _,results,manifest,audit,out=sys.argv
    assert not Path(out).exists()
    m=json.loads(Path(manifest).read_text())
    a=json.loads(Path(audit).read_text())
    assert m["status"]=="FROZEN_WITHOUT_TRUTH" and m["phase"]=="target"
    assert m["output_sha256"]==sha(results)==a["raw_output_sha256"]
    assert a["all_forward_witnesses_valid"] and a["verified_witnesses"]==156
    rows=[json.loads(line) for line in Path(results).read_text().splitlines()]
    assert len(rows)==13 and rows[0]["id"]=="K4"
    entries=[]
    for i,c in enumerate(rows[0]["candidates"],1):
        p=c["plaintext"]
        agree=sum(p[j]==x for j,x in KNOWN.items())
        entries.append({"blind_rank":i,"matches_of_24":agree,
                        "passes_all_24":agree==24,"raw_97_letter_plaintext":p,
                        "frozen_language_score":c["score"],
                        "matrix":[c[z] for z in ("a","b","c","d")]})
    report={"classification":"R57_AFTER_REMOTE_FREEZE_K4_CLUE_REJECT_ONLY",
            "raw_output_sha256":m["output_sha256"],
            "blind_top1_matches":entries[0]["matches_of_24"],
            "best_of_twelve_matches":max(e["matches_of_24"] for e in entries),
            "full_24_matches":sum(e["passes_all_24"] for e in entries),
            "candidates_original_blind_order":entries,
            "note":"Never re-ranked or altered candidate generation with published plaintext"}
    with Path(out).open("x",encoding="ascii") as f:f.write(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("R57 postfreeze: top",report["blind_top1_matches"],"/24, best",
          report["best_of_twelve_matches"],"/24; full",report["full_24_matches"])
if __name__=="__main__":main()
