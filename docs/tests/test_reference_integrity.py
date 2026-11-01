#!/usr/bin/env python3
"""Read-only documentation integration checks; never used by a blind K4 solver."""
from pathlib import Path
import hashlib, json
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "r39/ic_gate/k4_ciphertext.txt"
assert hashlib.sha256(DATA.read_bytes()).hexdigest() == (
    "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
)
cipher = DATA.read_text().strip()
assert len(cipher) == 97 and set(cipher) <= set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
for round_, expected in (("r55", 29952), ("r56", 51324), ("r57", 97344)):
    base = ROOT / round_ / "frozen"
    for phase, input_name, output_name, manifest_name in (
        ("controls", "CONTROLS_INPUT.tsv", "CONTROLS_RESULTS.jsonl", "CONTROLS_MANIFEST.json"),
        ("target", "K4_INPUT.tsv", "K4_RESULTS.jsonl", "K4_MANIFEST.json"),
    ):
        mf = json.loads((base / manifest_name).read_text())
        raw = (base / output_name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == mf["output_sha256"], (round_, phase)
        rows = [json.loads(line) for line in raw.splitlines()]
        n = 20 if phase == "controls" else 13
        assert len(rows) == n, (round_, phase)
        assert all(len(row["candidates"]) == 12 for row in rows)
        assert all(len(candidate["plaintext"]) == 97
                   for row in rows for candidate in row["candidates"])
        num = rows[0].get("tested", rows[0].get("searched"))
        assert num == expected, (round_, phase, num)
        assert (base / input_name).exists()
    evaluation = json.loads((base / "CONTROLS_EVALUATION.json").read_text())
    assert evaluation["gate_passed"] and evaluation["top1_exact_plaintext"] == 20
    assert evaluation["all_forward_witnesses_valid"]
    assert evaluation["verified_witnesses"] == 240
    audit = json.loads((base / "INDEPENDENT_FORWARD_AUDIT.json").read_text())
    assert audit["all_forward_witnesses_valid"] and audit["verified_witnesses"] == 156
    reveal = json.loads((base / "AFTER_REVEAL_EVALUATION.json").read_text())
    assert reveal["full_24_matches"] == 0
    assert reveal.get("frozen_raw_output_sha256", reveal.get("raw_output_sha256")) == (
        json.loads((base / "K4_MANIFEST.json").read_text())["output_sha256"]
    )
    print(round_, "frozen checks/claims verified (not a K4 solution)")
docs = (ROOT / "docs/CIPHER_TYPES_TESTED.md").read_text()
assert "The same applies after any transposition" not in docs
assert "does NOT extend to substitution" in docs
assert all(x in docs for x in ("R55", "R56", "R57", "two-wheel"))
memo = (ROOT / "docs/R55_R57_METHODOLOGY_AUDIT.md").read_text()
assert "No verified K4 solution" in memo
assert "family" in memo and "out-of-family" in memo
print("Research reference, strict scope and preserved freezes checked")
