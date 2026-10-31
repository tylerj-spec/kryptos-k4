#!/usr/bin/env python3
"""A MINIMAL CIPHERTEXT-ONLY DEMONSTRATION, NOT A CLAIM THAT K4 USES CAESAR.

Input NDJSON objects: {"id": "...", "ciphertext": "<97 A-Z characters>"}
Output NDJSON: every tested Caesar shift, unmodified score-based order.

Uses only generic English letter and n-gram frequencies; no clue positions,
known plaintext, candidate templates, external code, or network access.
This is a tiny integration smoke test for the hard blind/reveal firewall.
"""
import hashlib
import json
import math
import sys

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
FREQ = {
    "A": 0.0817, "B": 0.0149, "C": 0.0278, "D": 0.0425, "E": 0.1270,
    "F": 0.0223, "G": 0.0202, "H": 0.0609, "I": 0.0697, "J": 0.0015,
    "K": 0.0077, "L": 0.0403, "M": 0.0241, "N": 0.0675, "O": 0.0751,
    "P": 0.0193, "Q": 0.0010, "R": 0.0599, "S": 0.0633, "T": 0.0906,
    "U": 0.0276, "V": 0.0098, "W": 0.0236, "X": 0.0015, "Y": 0.0197,
    "Z": 0.0007,
}
LOGP = {x: math.log(p) for x, p in FREQ.items()}
COMMON_DIGRAMS = frozenset((
    "TH", "HE", "IN", "ER", "AN", "RE", "ON", "AT", "EN", "ND", "TI", "ES",
    "OR", "TE", "OF", "ED", "IS", "IT", "AL", "AR", "ST", "TO", "NT", "NG",
    "SE", "HA", "AS", "OU", "IO", "LE", "VE", "CO", "ME", "DE", "HI", "RI",
    "RO", "IC", "NE", "EA", "RA", "CE", "LI", "CH", "LL", "BE", "MA", "SI",
))
COMMON_TRIGRAMS = frozenset((
    "THE", "AND", "ING", "HER", "ERE", "ENT", "THA", "NTH", "WAS", "ETH",
    "FOR", "DTH", "HAT", "ION", "TIO", "VER", "TER", "HES", "ATI", "ALL",
    "THI", "HIS", "WIT", "THR", "ATE", "RES", "EST", "NOT", "YOU", "OUT",
))


def decipher(ciphertext: str, shift: int) -> str:
    return "".join(AZ[(AZ.index(char) - shift) % 26] for char in ciphertext)


def language_score(text: str) -> float:
    # Generic English priors, fixed and independent of the K4 known letters.
    score = sum(LOGP[x] for x in text)
    score += 0.65 * sum(text[i:i + 2] in COMMON_DIGRAMS for i in range(len(text) - 1))
    score += 1.15 * sum(text[i:i + 3] in COMMON_TRIGRAMS for i in range(len(text) - 2))
    return score


def solve_one(label: str, ct: str) -> dict:
    if not isinstance(label, str) or not label or len(label) > 90:
        raise ValueError("invalid ID")
    if not isinstance(ct, str) or len(ct) != 97 or not ct.isascii() or any(c not in AZ for c in ct):
        raise ValueError("only original-length A-Z ciphertext inputs allowed")
    candidates = []
    for k in range(26):
        p = decipher(ct, k)
        candidates.append({
            "algorithm": "caesar_az_smoke_only",
            "key": k,
            "plaintext": p,
            "language_score": round(language_score(p), 7),
        })
    candidates.sort(key=lambda x: (-x["language_score"], x["key"]))
    return {
        "id": label,
        "ciphertext_sha256": hashlib.sha256(ct.encode("ascii")).hexdigest(),
        "candidates": candidates,
    }


def main():
    seen = set()
    count = 0
    for lineno, line in enumerate(sys.stdin, 1):
        if not line.strip():
            continue
        x = json.loads(line)
        # A strict two-field input prevents hidden key/mask/answer metadata.
        if not isinstance(x, dict) or set(x) != {"id", "ciphertext"}:
            raise ValueError("blind input must contain only id and ciphertext")
        if x["id"] in seen:
            raise ValueError("duplicate input ID")
        seen.add(x["id"])
        r = solve_one(x["id"], x["ciphertext"])
        print(json.dumps(r, separators=(",", ":"), sort_keys=True), flush=True)
        count += 1
    if count == 0:
        raise ValueError("empty blind ciphertext input")


if __name__ == "__main__":
    main()
