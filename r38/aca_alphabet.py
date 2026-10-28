#!/usr/bin/env python3
"""ACA transposition-block keyed alphabet; derived from the ACA GROMARK specification.

The keyword's unique letters fill the top row. Remaining A-Z letters
fill the block row-wise. Read each column top-to-bottom in alphabetical
order of its heading; ties left to right.
This is NOT the same as a keyword-prefixed mixed alphabet.
"""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def aca_alphabet(keyword):
    key = "".join(dict.fromkeys(ch for ch in keyword.upper() if ch in AZ))
    if not key:
        raise ValueError("keyword must contain at least one A-Z letter")
    block = key + "".join(c for c in AZ if c not in key)
    result = "".join("".join(block[j] for j in range(i, len(block), len(key)))
                     for i in sorted(range(len(key)), key=lambda i: (key[i], i)))
    assert len(result) == 26 and set(result) == set(AZ)
    return result


if __name__ == "__main__":
    for k in ("ENIGMA", "KRYPTOS", "PALIMPSEST", "ABSCISSA"):
        print(k, aca_alphabet(k))
