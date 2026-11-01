#!/usr/bin/env python3
"""R55 sealed reviewer of REMOTE-FROZEN blind results. NO PUBLIC K4 CLUES HERE.
Controls truth (if supplied) is evaluated ONLY after remote ciphertext-only results freeze.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALLOWED_MULT = {1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25}
N = 97
K4_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_and_verify(kind, inp, results, manifest_path, source, quad, protocol):
    meta = json.loads(Path(manifest_path).read_text())
    assert meta["status"] == "FROZEN_NO_REVEAL" and meta["phase"] == kind
    for filepath, field in (
        (inp,"input_sha256"), (results,"output_sha256"),
        (source,"blind_source_sha256"), (quad,"quad_model_sha256"),
        (protocol,"protocol_sha256")
    ):
        assert sha(filepath) == meta[field], ("FROZEN DATA OR SOURCE MISMATCH", filepath)
    source_inputs = {}
    for row in Path(inp).read_text().splitlines():
        fields = row.split("\t")
        assert len(fields) == 2
        lab, ct = fields
        assert lab not in source_inputs and len(ct) == N and set(ct) <= set(AZ)
        source_inputs[lab] = ct
    assert len(source_inputs) == (20 if kind == "controls" else 13)
    if kind == "target":
        assert list(source_inputs)[0] == "K4"
        assert list(source_inputs)[1:] == [f"NULL_{i:02d}" for i in range(12)]
        assert source_inputs["K4"] == (
            "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        )
        # The canonical byte-for-byte source SHA is additionally checked in prepare.py.
        for n, t in list(source_inputs.items())[1:]:
            assert sorted(t) == sorted(source_inputs["K4"]), n
    else:
        assert list(source_inputs) == [f"PLANT_{i:02d}" for i in range(20)]
    frozen = {}
    total = 0
    for line in Path(results).read_text().splitlines():
        rec = json.loads(line)
        assert set(rec) == {"id", "tested", "candidates"}
        lab = rec["id"]
        assert lab in source_inputs and lab not in frozen
        assert rec["tested"] == 29952 and len(rec["candidates"]) == 12
        ct = source_inputs[lab]
        best_score = float("inf")
        signatures = set()
        for x in rec["candidates"]:
            assert set(x) == {"method","mode","lag","multiplier","sign","offset","step","score","plaintext"}
            assert x["method"] == "affine_feedback"
            assert x["mode"] in ("plaintext", "ciphertext")
            assert type(x["lag"]) is int and 1 <= x["lag"] <= 8
            assert type(x["multiplier"]) is int and x["multiplier"] in ALLOWED_MULT
            assert type(x["sign"]) is int and x["sign"] in (-1, 1)
            assert type(x["offset"]) is int and 0 <= x["offset"] <= 25
            assert type(x["step"]) is int and x["step"] in (-1, 0, 1)
            assert type(x["score"]) in (float, int) and math.isfinite(x["score"])
            assert x["score"] <= best_score + 1e-7
            best_score = x["score"]
            p = x["plaintext"]
            assert type(p) is str and len(p) == N and set(p) <= set(AZ)
            sig = tuple(x[t] for t in ("mode","lag","multiplier","sign","offset","step"))
            assert sig not in signatures
            signatures.add(sig)
            plain = [ord(ch)-65 for ch in p]
            cipher = []
            for i,v in enumerate(plain):
                f = (plain[i-x["lag"]] if x["mode"]=="plaintext"
                     else cipher[i-x["lag"]]) if i>=x["lag"] else 0
                cipher.append((x["multiplier"]*v + x["offset"]
                               + x["step"]*i + x["sign"]*f) % 26)
            assert "".join(chr(65+v) for v in cipher) == ct, ("WITNESS FAILURE",lab,sig)
            total += 1
        frozen[lab] = rec
    assert frozen.keys() == source_inputs.keys()
    return frozen, total, meta

def main():
    if len(sys.argv) not in (9,10):
        raise SystemExit("verify_frozen.py controls|target INPUT RESULTS MANIFEST SOLVER QUAD PROTOCOL OUT [TRUTH]")
    _, kind, inp, result, manifest, solver, quad, protocol, outfile, *extras = sys.argv
    assert kind in ("controls","target")
    assert (kind=="controls" and len(extras)==1) or (kind=="target" and not extras)
    if Path(outfile).exists():
        raise FileExistsError("will not overwrite sealed evaluation")
    rows, witnesses, meta = read_and_verify(kind, inp, result, manifest, solver, quad, protocol)
    report = {
        "phase": kind,
        "classification": "POST_REMOTE_FREEZE_CONTROL_GATE" if kind=="controls" else "POST_REMOTE_FREEZE_FORWARD_AUDIT_NO_K4_CLUES",
        "raw_output_sha256": meta["output_sha256"],
        "all_forward_witnesses_valid": True,
        "verified_witnesses": witnesses,
        "inputs": len(rows),
        "candidates_per_input": 12,
    }
    if kind == "controls":
        truth = json.loads(Path(extras[0]).read_text())
        assert truth.keys() == rows.keys()
        exact = 0
        true_param_top1 = 0
        for lab,row in rows.items():
            t = truth[lab]
            c = row["candidates"][0]
            exact += c["plaintext"] == t["plaintext"]
            true_param_top1 += all(c[x] == t[x] for x in (
                "mode","lag","multiplier","sign","offset","step"
            ))
        report["top1_exact_plaintext"] = exact
        report["top1_true_settings"] = true_param_top1
        report["required_exact"] = 16
        report["gate_passed"] = exact >= 16
        report["warning"] = "Synthetic same-family test, not evidence that K4 uses the model"
    else:
        best = rows["K4"]["candidates"][0]["score"]
        null_scores = [rows[f"NULL_{i:02d}"]["candidates"][0]["score"] for i in range(12)]
        exceed = sum(s >= best for s in null_scores)
        report["k4_top1_score"] = best
        report["null_top1_scores"] = null_scores
        report["k4_score_empirical_upper_tail_13"] = (exceed+1)/13
        report["warning"] = "Only 12 shuffles; the language score is not a K4 decryption or confirmed method."
    Path(outfile).parent.mkdir(parents=True, exist_ok=True)
    with Path(outfile).open("x",encoding="ascii") as f:
        f.write(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print("R55",kind,"verified",witnesses,"forward witnesses",
          "top1 exact" if kind=="controls" else "no clue validation performed",
          report.get("top1_exact_plaintext",""))
    if kind=="controls" and not report["gate_passed"]:
        print("R55 RESEARCH GATE FAILED; original K4 must NOT be run under this protocol.",file=sys.stderr)
        sys.exit(2)

if __name__=="__main__":
    main()
