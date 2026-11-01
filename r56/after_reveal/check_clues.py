#!/usr/bin/env python3
"""R56 ONLY AFTER REMOTE FREEZE + SEPARATE FORWARD WITNESSES:
compare original fixed outputs to published K4 letters; NEVER rerank or tune.
"""
import json,hashlib,sys
from pathlib import Path
KNOWN={21+i:c for i,c in enumerate("EASTNORTHEAST")}
KNOWN.update({63+i:c for i,c in enumerate("BERLINCLOCK")})
assert len(KNOWN)==24
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=5:
        raise SystemExit("reveal.py TARGET_RESULTS MANIFEST AUDIT OUTPUT")
    _,results,manifest,audit,out=sys.argv
    assert not Path(out).exists()
    m=json.loads(Path(manifest).read_text())
    a=json.loads(Path(audit).read_text())
    assert m["phase"]=="target" and m["status"]=="FROZEN_NO_EVALUATION"
    assert sha(results)==m["output_sha256"]==a["raw_output_sha256"]
    assert a["all_forward_witnesses_valid"] and a["verified_witnesses"]==156
    rows=[json.loads(s) for s in Path(results).read_text().splitlines()]
    assert len(rows)==13 and rows[0]["id"]=="K4"
    raw=[]
    for rank,c in enumerate(rows[0]["candidates"],1):
        p=c["plaintext"]
        hit=sum(p[j]==v for j,v in KNOWN.items())
        raw.append({"blind_rank":rank,"published_matches_of_24":hit,
                    "pass_all_24":hit==24,"raw_97_letter_plaintext":p,
                    "frozen_score":c["score"],"keyword_alphabet":c["keyword_alphabet"],
                    "keyword_side":c["keyword_side"],
                    "right_initial_phase":c["right_initial_phase"]})
    report={"classification":"R56_POSTFREEZE_K4_KNOWN_LETTER_EVALUATION_NOT_A_SOLUTION",
            "original_order_kept":True,
            "frozen_raw_output_sha256":m["output_sha256"],
            "top1_matches":raw[0]["published_matches_of_24"],
            "best_of_twelve_matches":max(x["published_matches_of_24"] for x in raw),
            "full_24_matches":sum(x["pass_all_24"] for x in raw),
            "raw_candidates_original_frozen_order":raw,
            "rule":"known plaintext never enters blind solver or key search"}
    with Path(out).open("x",encoding="ascii") as f:f.write(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("R56 K4 postfreeze top1",report["top1_matches"],"/24; best",
          report["best_of_twelve_matches"],"/24, full",report["full_24_matches"])
if __name__=="__main__":main()
