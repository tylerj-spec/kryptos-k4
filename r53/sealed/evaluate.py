#!/usr/bin/env python3
"""SEALED: AFTER a blind-output commit, check hash, forward crypto, then K4 clues.

This code is deliberately outside r53/blind and is never mounted into the
blind runtime. It MUST run only after the blind output was committed/frozen.
"""
import hashlib
import json
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Public K4 facts are SEALED and only evaluated AFTER raw output freeze.
CONFIRMED = dict((21 + i, ch) for i, ch in enumerate("EASTNORTHEAST"))
CONFIRMED.update((63 + i, ch) for i, ch in enumerate("BERLINCLOCK"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def encode_caesar(plaintext, shift):
    return "".join(AZ[(AZ.index(ch) + shift) % 26] for ch in plaintext)


def main():
    if len(sys.argv) != 6:
        raise SystemExit(
            "usage: evaluate.py FROZEN_INPUT.ndjson FROZEN_OUTPUT.ndjson "
            "MANIFEST.json BLIND_SOURCE.py REPORT.json"
        )
    input_file, output_file, manifest_file, blind_file, report_file = map(Path, sys.argv[1:])
    if report_file.exists():
        raise FileExistsError("will not overwrite evaluation")
    assert manifest_file.is_file(), "freeze manifest missing"
    manifest = json.loads(manifest_file.read_text())
    assert manifest["status"] == "BLIND_FROZEN_NO_VALIDATION_YET"
    assert manifest["input_sha256"] == sha(input_file)
    assert manifest["candidates_sha256"] == sha(output_file)
    assert manifest["solver_sha256"] == sha(blind_file)
    original = {}
    for line in input_file.read_text().splitlines():
        x = json.loads(line)
        assert set(x) == {"ciphertext", "id"}
        assert x["id"] not in original
        assert len(x["ciphertext"]) == 97
        original[x["id"]] = x["ciphertext"]
    frozen = {}
    for line in output_file.read_text().splitlines():
        row = json.loads(line)
        assert set(row) == {"id", "ciphertext_sha256", "candidates"}
        identifier = row["id"]
        assert identifier in original and identifier not in frozen
        assert row["ciphertext_sha256"] == hashlib.sha256(
            original[identifier].encode("ascii")
        ).hexdigest()
        results = row["candidates"]
        assert len(results) == 26
        keys = set()
        for x in results:
            assert set(x) == {"algorithm", "key", "plaintext", "language_score"}
            assert x["algorithm"] == "caesar_az_smoke_only"
            assert isinstance(x["key"], int) and not isinstance(x["key"], bool)
            assert x["key"] in range(26)
            assert x["key"] not in keys
            keys.add(x["key"])
            assert len(x["plaintext"]) == 97 and set(x["plaintext"]) <= set(AZ)
            assert encode_caesar(x["plaintext"], x["key"]) == original[identifier], (
                "independent forward encryption witness failed"
            )
        assert keys == set(range(26))
        frozen[identifier] = row
    assert frozen.keys() == original.keys() and "K4" in frozen

    # Only NOW, after verifying the immutable output hash + every independent
    # forward encryption witness, consult K4's confirmed words/positions.
    k4_row = frozen["K4"]
    clue_passes = []
    for i, x in enumerate(k4_row["candidates"]):
        agreement = sum(x["plaintext"][j] == ch for j, ch in CONFIRMED.items())
        if agreement == len(CONFIRMED):
            clue_passes.append({"rank": i + 1, "key": x["key"]})
    assert len(clue_passes) == 0, (
        "Unexpected K4 clue match in Caesar smoke; scientifically investigate!"
    )

    report = {
        "classification": "HARD_BLIND_CAESAR_SMOKE_NOT_A_K4_SOLUTION",
        "frozen_raw_sha256": manifest["candidates_sha256"],
        "forward_encryption_valid": True,
        "ciphertexts": len(frozen),
        "candidates_per_ciphertext": 26,
        "synthetic_control_count": len(frozen) - 1,
        "k4_caesar_candidates_matching_all_published_letters": clue_passes,
        "k4_top1_known_letter_count_after_freeze": sum(
            k4_row["candidates"][0]["plaintext"][j] == ch
            for j, ch in CONFIRMED.items()
        ),
        "warning": "Clue validation ran only AFTER raw ciphertext-only candidates were frozen. "
                   "No K4 plaintext recovery is claimed. Synthetic smoke controls are not "
                   "a genuine hidden-key unknown-cipher benchmark."
    }
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("R53 sealed evaluation PASS: frozen hash verified, all 26 keys forward encrypted, "
          "Caesar smoke K4 full published-clue matches = 0")


if __name__ == "__main__":
    main()
