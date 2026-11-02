#!/usr/bin/env python3
"""R58B SEPARATE AFTER-FREEZE ONLY: compare immutable original K4 outputs against
known public plaintext/offsets. No ranking, rescoring, key selection or re-runs.
"""
import hashlib,json,sys
from pathlib import Path

KNOWN={21+i:ch for i,ch in enumerate("EASTNORTHEAST")}
KNOWN.update({63+i:ch for i,ch in enumerate("BERLINCLOCK")})
assert len(KNOWN)==24
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    if len(sys.argv)!=5:
        raise SystemExit("check_clues.py FROZEN_K4_RESULTS MANIFEST FORWARD_AUDIT AFTER_REVEAL_REPORT")
    _,results,manifest,audit,out=sys.argv
    assert not Path(out).exists()
    m=json.loads(Path(manifest).read_text())
    a=json.loads(Path(audit).read_text())
    assert m["status"]=="FROZEN_BEFORE_ANY_K4_CLUE" and m["phase"]=="target"
    assert m["output_sha256"]==sha(results)==a["raw_output_sha256"]
    assert a["verified_forward_witnesses"]==808 and a["all_forward_witnesses_valid"]
    lines=Path(results).read_text().splitlines()
    assert len(lines)==101
    k4=json.loads(lines[0])
    assert k4["id"]=="K4" and len(k4["candidates"])==8
    result=[]
    for rank,c in enumerate(k4["candidates"],1):
        p=c["plaintext"]
        hit=sum(p[pos]==ch for pos,ch in KNOWN.items())
        result.append({
          "blind_rank":rank,
          "frozen_method":c["family"],
          "frozen_key":c["key"],
          "frozen_route":c["route"],
          "frozen_plaintext":p,
          "frozen_generic_quad_score":c["score"],
          "matches_known_24":hit,
          "matches_all_known_24":hit==24
        })
    outdata={
        "classification":"R58B_POST_REMOTE_FREEZE_ONLY_PUBLIC_K4_LETTER_COMPARISON",
        "raw_output_sha256":m["output_sha256"],
        "blind_declared_detected_family":k4["detected_family"],
        "blind_abstained":k4["detected_family"]=="ABSTAIN",
        "top_rank_known_24":result[0]["matches_known_24"],
        "best_of_eight_known_24":max(x["matches_known_24"] for x in result),
        "all_24_matches":sum(x["matches_all_known_24"] for x in result),
        "candidates_in_original_frozen_order":result,
        "note":"These confirmed letters were never available to blind solver; comparing outputs does not authorize a new ranking or key search."
    }
    with Path(out).open("x",encoding="ascii") as f:
        json.dump(outdata,f,indent=2,sort_keys=True);f.write(chr(10))
    print("R58B original known-letter check AFTER full remote freeze:",
          result[0]["matches_known_24"],"/24 top, best",
          outdata["best_of_eight_known_24"],"/24, full",
          outdata["all_24_matches"])
if __name__=="__main__":main()
