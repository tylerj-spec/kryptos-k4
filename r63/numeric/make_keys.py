#!/usr/bin/env python3
"""R63 part C: numeric key streams for the strictblind harness (TEXT keys; digit d -> letter chr(65+d), so with A-Z
numbering the shift is the digit itself). No K4 data.
  PI, E, SQRT2, PHI : the first 10,000 digits (integer digit included), exact integer arithmetic;
  K2COORD           : K2's coordinates 38 57 6.5 N, 77 8 44 W -> "38576577844", repeated to 2,000 digits;
  DATES             : 19901103 (dedication), 19891109 (Berlin Wall), 19860000-style "1986" (Egypt trip) -> each repeated
                      to 2,000 digits.
Usage: make_keys.py OUT_DIR"""
import sys
from math import isqrt
from pathlib import Path

N = 10000
sys.set_int_max_str_digits(100000)


def pi_digits(n):
    def arctan_inv(x, unity):
        s = t = unity // x; x2, k, sign = x * x, 3, -1
        while t:
            t //= x2; s += sign * (t // k); sign, k = -sign, k + 2
        return s
    u = 10 ** (n + 10)
    return str(4 * (4 * arctan_inv(5, u) - arctan_inv(239, u)))[:n]


def e_digits(n):
    u = 10 ** (n + 10); s, t, k = 0, u, 0
    while t:
        s += t; k += 1; t //= k
    return str(s)[:n]


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    streams = {"PI": pi_digits(N), "E": e_digits(N), "SQRT2": str(isqrt(2 * 10 ** (2 * (N - 1))))[:N],
               "PHI": str((10 ** (N - 1) + isqrt(5 * 10 ** (2 * (N - 1)))) // 2)[:N]}
    for name, rep in (("K2COORD", "38576577844"), ("DATE19901103", "19901103"), ("DATE19891109", "19891109"), ("DATE1986", "1986")):
        streams[name] = (rep * (2000 // len(rep) + 1))[:2000]
    assert streams["PI"].startswith("31415926535") and streams["E"].startswith("27182818284")
    assert streams["SQRT2"].startswith("14142135623") and streams["PHI"].startswith("16180339887")
    for name, d in streams.items():
        (out / f"key_{name}.txt").write_text("".join(chr(65 + int(c)) for c in d) + "\n")
    print({k: len(v) for k, v in streams.items()})


if __name__ == "__main__":
    main()
