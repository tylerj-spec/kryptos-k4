#!/usr/bin/env python3
"""R81a post-freeze POWER CONTROL for validate81.py (added after the K4 validator returned 0 everywhere; synthetic only,
no K4 ciphertext is used). It shows that the check can say yes:
  plant     a random setting of each of the eight families (keyword 2..12) encrypts a random-letter plaintext that
            carries the published words at their positions; the planted setting (everything but the key letters, which
            the published letters pin only at their own slots) must be flagged as EXACT;
  one-off   the same, but one published position holds a different letter (G6); the planted setting must be flagged by
            DROP-ONE with that position set aside (or stay exact, if no other published letter shares its slot).
Nothing here changes the frozen K4 outcome or any pre-registered rule.
Usage: control_validate81.py OUT.json [TRIALS=3]"""
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate81 as V  # noqa: E402

SEED = 810500


def bare(st):
    return {k: v for k, v in st.items() if k != "key"}


def found(mod, fam, ct, st, pos_dropped=None):
    n, ex, drop, flagged = V.check_family(mod, fam, ct, True)
    want = bare(st)
    hit = None
    for f in flagged:
        s = mod.setting(f["chunk_info"], f["row"], np.zeros(f["m"], dtype=np.int64))
        if bare(s) == want:
            hit = f
            break
    return {"settings": n, "exact": ex, "drop_one": int(drop.sum()), "planted_flagged": hit is not None,
            "planted_dropped": hit["dropped"] if hit else None,
            "ok": hit is not None and (pos_dropped is None and not hit["dropped"]
                                       or pos_dropped is not None and (hit["dropped"] == [] or pos_dropped in hit["dropped"]))}


def main():
    outp = sys.argv[1]
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    rng = random.Random(SEED)
    rows, allok = [], True
    for tag, mod, fams in V.FAMSETS:
        for fam in fams:
            for t in range(trials):
                st = mod.random_setting(rng, fam, 2, 12)
                pt = [chr(65 + rng.randrange(26)) for _ in range(97)]
                for p, w in zip(V.POS, V.WANT):
                    pt[p] = chr(65 + int(w))
                ct = mod.encrypt("".join(pt), st)
                assert mod.decrypt(ct, st) == "".join(pt)
                r_plant = found(mod, fam, ct, st)
                a = rng.randrange(len(V.POS))
                p = int(V.POS[a])
                pt2 = list(pt)
                pt2[p] = chr(65 + (int(V.WANT[a]) + 1 + rng.randrange(25)) % 26)
                ct2 = mod.encrypt("".join(pt2), st)
                r_off = found(mod, fam, ct2, st, p)
                ok = r_plant["ok"] and r_off["ok"]
                allok &= ok
                rows.append({"family": f"{tag}:{fam}", "m": st.get("m"), "setting": bare(st), "plant": r_plant,
                             "one_off_position": p, "one_off": r_off, "ok": ok})
                print(f"{tag}:{fam} m={st.get('m')} plant {r_plant['planted_flagged']} "
                      f"(exact {r_plant['exact']}) one-off@{p} {r_off['planted_flagged']} {r_off['planted_dropped']} "
                      f"(exact {r_off['exact']}, drop {r_off['drop_one']}) {'OK' if ok else 'FAIL'}", flush=True)
    Path(outp).write_text(json.dumps({"label": "post-freeze power control for validate81 (synthetic only)",
                                      "seed": SEED, "all_ok": allok, "rows": rows}, indent=1, default=str) + "\n")
    print("ALL OK" if allok else "SOME FAILED")


if __name__ == "__main__":
    main()
