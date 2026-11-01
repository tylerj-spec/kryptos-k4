#!/usr/bin/env python3
"""R55 AFTER-REMOTE-FREEZE ONLY: known K4 letters are read *here* and nowhere in blind code.
Must run in a separate Actions job after the remote Git freeze and forward audit pass.
"""
import hashlib
import json
import sys
from pathlib import Path

KNOWN = {21+i:ch for i,ch in enumerate("EASTNORTHEAST")}
KNOWN.update({63+i:ch for i,ch in enumerate("BERLINCLOCK")})
assert len(KNOWN) == 24
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if len(sys.argv) != 5:
        raise SystemExit("check_clues.py FROZEN_RESULTS.jsonl MANIFEST.json VERIFIED_AUDIT.json OUT.json")
    _,results,manifest,forward,out = sys.argv
    if Path(out).exists(): raise FileExistsError("no overwrite of revealed result")
    m=json.loads(Path(manifest).read_text())
    audit=json.loads(Path(forward).read_text())
    assert m["status"]=="FROZEN_NO_REVEAL" and m["phase"]=="target"
    assert sha(results)==m["output_sha256"]
    assert audit["raw_output_sha256"]==m["output_sha256"]
    assert audit["all_forward_witnesses_valid"] is True and audit["verified_witnesses"]==156
    data=[json.loads(s) for s in Path(results).read_text().splitlines()]
    assert len(data)==13 and data[0]["id"]=="K4"
    candidates=[]
    for j,x in enumerate(data[0]["candidates"],1):
        p=x["plaintext"]
        agreement=sum(p[i]==ch for i,ch in KNOWN.items())
        candidates.append({
            "rank_blind_frozen":j,
            "known_letter_agreement_of_24":agreement,
            "all_24_known_letters":agreement==24,
            "parameters":{k:x[k] for k in ("method","mode","lag","multiplier","sign","offset","step")},
            "score_blind_frozen":x["score"],
            "full_raw_plaintext":p,
        })
    report={
        "classification":"POSTFREEZE_K4_KNOWN_LETTER_COMPARISON_NOT_A_SOLVE",
        "frozen_raw_output_sha256":m["output_sha256"],
        "original_ciphertext_unchanged":True,
        "no_clue_in_candidate_selection":True,
        "total_candidates":len(candidates),
        "best_agreement_any_frozen_candidate":max(c["known_letter_agreement_of_24"] for c in candidates),
        "full_24_agreement":sum(c["all_24_known_letters"] for c in candidates),
        "blind_top1_agreement":candidates[0]["known_letter_agreement_of_24"],
        "candidates_in_original_blind_order":candidates,
        "warning":"An output contradicting known letters is rejected as a K4 solution. No model or key tuning from this evaluation.",
    }
    with Path(out).open("x",encoding="ascii") as f:
        f.write(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("R55 AFTER REVEAL: top1",report["blind_top1_agreement"],
          "of 24; best of 12",report["best_agreement_any_frozen_candidate"],
          "full matches",report["full_24_agreement"])

if __name__=="__main__":
    main()
