#!/usr/bin/env python3
"""Freeze R59 entire ciphertext-only output and provenance hashes BEFORE sealed class/key reveal.
Does not read ANY known K4 plaintext, anchors, clue offsets, guessed full plaintext, or
the synthetic control truth.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    if len(sys.argv)!=8:
        raise SystemExit("freeze.py INPUT RESULTS BLIND_SOURCE MONOGRAM_MODEL PROTOCOL SEALED_GENERATOR MANIFEST")
    _,inputs,results,source,prior,protocol,prep,out=sys.argv
    path=Path(out)
    assert not path.exists(),"refuse overwrite"
    inp=Path(inputs).read_text(encoding="ascii").splitlines()
    raw=Path(results).read_text(encoding="ascii").splitlines()
    assert len(inp)==len(raw)==91
    fields_expected=("abs_IC_deviation_from_uniform",
                     "max_pooled_periodic_IC_m2_to12",
                     "max_lag_equality_z_lag1_to24",
                     "max_column_best_shift_log_likelihood_m2_to12")
    for i,(a,b) in enumerate(zip(inp,raw)):
        ident,ct=a.split(chr(9))
        expected=f"CASE_{i:03d}" if i<90 else "K4"
        assert ident==expected and len(ct)==97 and set(ct)<=set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        obj=json.loads(b)
        assert obj["id"]==ident and obj["n"]==97
        assert obj["null_cohort_size"]==obj["omnibus_cohort_size"]==4000
        assert obj["feature_names"]==list(fields_expected)
        assert len(obj["feature_values"])==len(obj["feature_upper_tail_p_values"])==4
        assert all(math.isfinite(x) for x in obj["feature_values"])
        assert all(0<x<=1 for x in obj["feature_upper_tail_p_values"])
        assert 0<obj["familywise_uniform_null_p"]<=1
        assert obj["departure_flag"]==(obj["familywise_uniform_null_p"]<=0.01)
        assert obj["conclusion"]=="STATISTICAL_NONUNIFORMITY_ONLY_NO_DECRYPTION"
        assert "plaintext" not in b.lower() and "key" not in b.lower()
    data={
      "phase":"controls_plus_K4","classification":"R59_STRICT_CIPHERTEXT_ONLY",
      "status":"FROZEN_BEFORE_ANY_SEALED_TRUE_FAMILY_OR_KEY",
      "input_sha256":sha(inputs),"output_sha256":sha(results),
      "blind_source_sha256":sha(source),"monogram_prior_sha256":sha(prior),
      "protocol_sha256":sha(protocol),"sealed_generator_sha256":sha(prep),
      "records":91,"uniform_calibration_size":4000,
      "omnibus_calibration_size":4000,"feature_families":4,
      "no_candidate_plaintext_generated":True,
      "no_K4_known_letters_or_positions_supplied":True
    }
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="ascii") as f:
        json.dump(data,f,indent=2,sort_keys=True);f.write(chr(10))
    print("R59 frozen SHA256",data["output_sha256"],"91 ciphertext-only fingerprints")

if __name__=="__main__":main()
