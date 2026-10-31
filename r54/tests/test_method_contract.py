#!/usr/bin/env python3
"""Test R54 no-crib source contract; optional independently verify report math."""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "r54/blind/method_fingerprint.js"
SOURCE = SCRIPT.read_text()
UP = SOURCE.upper()
BANNED = (
    "EASTNORTHEAST", "BERLINCLOCK", "K4COMMON", "KEY_ORACLE",
    "R52/EDUCATED", "R45/SEALED", "R46/SEALED",
    "SECRET_PLAINTEXT", "CLUE_POSITION", "CRIB_MASK"
)
assert not any(w in UP for w in BANNED), (
    "method classifier must not import confirmed K4 plaintext or derived masks"
)
imports = re.findall(r"""require\(\s*['"]([^'"]+)['"]\s*\)""", SOURCE)
assert set(imports) == {"fs", "crypto"}, imports
assert "http:" not in SOURCE and "https:" not in SOURCE
assert "process.env" not in SOURCE and "child_process" not in SOURCE
assert "eval(" not in SOURCE and "exec(" not in SOURCE
assert "method_fingerprint.js" in SCRIPT.name

if len(sys.argv) == 2:
    report = json.loads(Path(sys.argv[1]).read_text())
    assert report["classification"] == (
        "EXPLORATORY_CIPHERTEXT_ONLY_METHOD_FINGERPRINTS_NO_DECRYPTION"
    )
    assert report["target_letters"] == 97
    assert report["original_ciphertext"]["unique_letters"] == 26
    assert report["original_ciphertext"]["repeated_trigrams"] == []
    assert report["english_reference"]["windows"] == 1009
    assert report["english_reference"]["count_ic_at_or_below_ciphertext"] == 0
    assert report["english_marginal_null"]["replicates"] == 200000
    assert report["shuffled_ciphertext_lag_null"]["replicates"] == 40000
    assert len(report["independent_synthetic_cipher_models"]["by_period"]) == 9
    ct_file = ROOT / "r39/ic_gate/k4_ciphertext.txt"
    actual_sha = hashlib.sha256(ct_file.read_bytes()).hexdigest()
    assert report["ciphertext_sha256"] == actual_sha
    ct = ct_file.read_text().strip()
    counts = Counter(ct)
    n = len(ct)
    ic = sum(v * (v-1) for v in counts.values())/(n*(n-1))
    assert ic == report["original_ciphertext"]["index_of_coincidence"]
    assert report["original_ciphertext"]["letter_counts"] == {
        chr(65+i): counts.get(chr(65+i), 0) for i in range(26)
    }
    assert 0 <= report["shuffled_ciphertext_lag_null"]["familywise_p"] <= 1
    assert report["shuffled_ciphertext_lag_null"]["observed_best_lag"] == 7
    assert report["shuffled_ciphertext_lag_null"]["observed_best_lag_matches"] == 9
    print("R54 CHECK PASS: original ciphertext independent IC/counts, no clue paths, all nulls recorded")
else:
    assert len(sys.argv) == 1
    print("R54 SOURCE FIREWALL PASS: no K4 plaintext imports, only node builtins fs/crypto")
