#!/usr/bin/env python3
"""Independent review of R89's saved synthetic gate; never reads K4 inputs.

Uses the frozen plaintext, ciphertext and candidate results and their recorded
scores. It does not import the builder's family/gate code, rerun optimization,
or claim to independently recompute scores without the large language model.
"""
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(word):
    return "".join(dict.fromkeys(word + AZ))


CONTACTS = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
FALPH = {name: keyed(name) for name in (
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "NUANCE", "MAGNETIC", "PASSAGE", "CANDLE", "SANBORN",
    "SCHEIDT", "LANGLEY", "WEBSTER", "SHADING", "IQLUSION", "UNDERGRUUND", "DESPARATLY", "LAYERTWO", "INVISIBLE")}
FALPH.update(AZ=AZ, QWERTY="QWERTYUIOPASDFGHJKLZXCVBNM", ALT=AZ[::2] + AZ[1::2])


def encrypt(pt, arm, st):
    if arm in ("F26", "F26L"):
        a, block = FALPH[st["alphabet"]], st["b"]
        text = []
        for start in range(0, len(pt), block):
            plain = pt[start:start + block]
            for k in range(len(plain)):
                row = a.index(plain[(k + st["u"]) % len(plain)]) // 13
                col = a.index(plain[(k + st["v"]) % len(plain)]) % 13
                text.append(a[row * 13 + col])
        outer = st["outer"]
        if outer:
            key = {"PAL": "PALIMPSEST", "ABS": "ABSCISSA"}[outer["key"]]
            a = CONTACTS["KRY"]
            text = [a[(a.index(c) + outer["sign"] * a.index(key[(i + outer["phase"]) % len(key)])) % 26]
                    for i, c in enumerate(text)]
        return "".join(text)
    ein, eout = CONTACTS[st["ein"]], CONTACTS[st["eout"]]
    offset, text = 0, []
    for p in pt:
        c = eout[(st["wiring"][(ein.index(p) + offset) % 26] - offset) % 26]
        text.append(c)
        offset = (offset + st["d"] * (1 + ((AZ.index(c) + st["q"]) % st["m"] == 0))) % 26
    return "".join(text)


def confidence(candidate):
    return candidate["lm_per_letter"] >= -1.30 and candidate["word_per_letter"] >= -2.50


def key_recovery(truth, found):
    """Return full-key equality and message-contact equivalence for RCT.

    Message-contact equivalence is weaker than global cipher equivalence:
    unvisited contacts may have different arbitrary completions.
    """
    if truth["arm"] != found["arm"]:
        return False, False
    actual, got = truth["setting"], found["setting"]
    if truth["arm"] == "F26L":
        return actual == got, actual == got
    if not all(actual[k] == got[k] for k in ("ein", "eout", "d", "m", "q")):
        return False, False
    used, offset = set(), 0
    for p, c in zip(truth["enciphered"], truth["ct"]):
        used.add((CONTACTS[actual["ein"]].index(p) + offset) % 26)
        offset = (offset + actual["d"] * (1 + ((AZ.index(c) + actual["q"]) % actual["m"] == 0))) % 26
    return actual["wiring"] == got["wiring"], all(actual["wiring"][k] == got["wiring"][k] for k in used)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


hold = REPO / "r89/holdout"
truth = json.loads((hold / "TRUTH.json").read_text())
rows = [json.loads(line) for line in (hold / "run/RESULTS.jsonl").read_text().splitlines()]
assert len({r["id"] for r in rows}) == len(rows)
results = {r["id"]: r for r in rows}
cts = dict(line.split("\t") for line in (hold / "BLIND.tsv").read_text().splitlines()[1:])
assert set(truth) == set(results) == set(cts)
assert len(truth) == 255
assert digest(hold / "TRUTH.json") == (hold / "TRUTH_SHA256").read_text().split()[0]
assert all(t["ct"] == cts[rid] and len(t["ct"]) == 97 for rid, t in truth.items())

report = {
    "scope": "Saved synthetic holdout and saved scores only; independent aggregation and reference encryption; no K4 input.",
    "commit": "9e04e4e32eeb7c947e32979dc6663433e358192d",
    "source_sha256": {str(p.relative_to(REPO)): digest(p) for p in (
        hold / "TRUTH.json", hold / "BLIND.tsv", hold / "run/RESULTS.jsonl", hold / "GATE.json")},
    "classes": dict(Counter(t["class"] for t in truth.values())),
    "negative_generators": dict(Counter(t["generator"] for t in truth.values() if t["class"] == "NEG")),
    "arms": {}, "positive_reference_encryptions": 0, "saved_reference_witnesses": 0,
}
negative_ids = [rid for rid, t in truth.items() if t["class"] == "NEG"]
report["negatives_confident_best"] = sum(confidence(results[rid]["best"]) for rid in negative_ids)
report["negatives_confident_any_saved"] = sum(any(confidence(c) for c in results[rid]["top"] +
    list(results[rid]["best_by_arm"].values())) for rid in negative_ids)
report["zero_of_150_iid_binomial_95pct_upper"] = 1 - math.pow(0.05, 1 / 150)
report["binomial_qualification"] = "Illustrative bound assumes independent exchangeable cases; stratified generators and reused source books do not establish that assumption."

for rid, t in truth.items():
    r = results[rid]
    assert r["n_settings"] == {"F26L+F26": 139120, "RCT": 448}
    assert r["best"] == r["top"][0]
    seen = set()
    for candidate in r["top"] + list(r["best_by_arm"].values()):
        identity = json.dumps({k: candidate[k] for k in ("arm", "text", "setting")}, sort_keys=True)
        if identity not in seen:
            seen.add(identity)
            assert len(candidate["text"]) == 97
            assert encrypt(candidate["text"], candidate["arm"], candidate["setting"]) == t["ct"]
            report["saved_reference_witnesses"] += 1
    if t["class"] == "POS":
        assert t["enciphered"] == (t["pt"].translate(str.maketrans("CW", "KV")) if t["masked"] else t["pt"])
        assert encrypt(t["enciphered"], t["arm"], t["setting"]) == t["ct"]
        report["positive_reference_encryptions"] += 1

for arm in ("F26L", "RCT"):
    pos = [(rid, t) for rid, t in truth.items() if t["class"] == "POS" and t["arm"] == arm]
    arows = []
    for rid, t in pos:
        b = results[rid]["best"]
        correct = sum(x == y for x, y in zip(b["text"], t["enciphered"]))
        full_key, contact_equiv = key_recovery(t, b)
        ok = b["arm"] == arm and correct >= 95 and confidence(b)
        arows.append({"id": rid, "right": correct, "arm_found": b["arm"], "ok": ok,
                      "exact": ok and correct == 97, "confident": confidence(b),
                      "full_key": full_key, "message_contact_equivalent": contact_equiv,
                      "stratum": t["stratum"], "genre": t["genre"], "masked": t["masked"]})
    count = lambda key, value: [sum(r["ok"] for r in arows if r[key] == value), sum(r[key] == value for r in arows)]
    s = {
        "positives": len(pos), "ok": sum(r["ok"] for r in arows), "exact": sum(r["exact"] for r in arows),
        "full_key": sum(r["full_key"] for r in arows),
        "message_contact_equivalent": sum(r["message_contact_equivalent"] for r in arows),
        "by_stratum": {k: count("stratum", k) for k in ("S1", "S2", "S3", "S4")},
        "by_genre": {k: count("genre", k) for k in ("G1", "G2", "G3")},
        "masked": count("masked", True), "unmasked": count("masked", False),
        "misses": [r for r in arows if not r["ok"]],
        "ok_without_true_contact_key": [r for r in arows if r["ok"] and not r["message_contact_equivalent"]],
        "unused_contact_completions": [r for r in arows if r["message_contact_equivalent"] and not r["full_key"]],
        "cells": dict(Counter(f'{t["stratum"]}/{t["genre"]}' for _, t in pos)),
    }
    s["claude_preregistered_go"] = (s["ok"] >= 42 and s["exact"] >= 36 and
        all(v[0] >= 9 for v in s["by_stratum"].values()) and all(v[0] >= 12 for v in s["by_genre"].values()) and
        s["masked"][0] >= 8 and report["negatives_confident_best"] <= 1)
    s["original_design_method_key_ge42_satisfied_even_with_message_equivalence"] = sum(
        r["ok"] and r["message_contact_equivalent"] for r in arows) >= 42
    stored = json.loads((hold / "GATE.json").read_text())["summary"]["arms"][arm]
    for k in ("positives", "ok", "exact", "by_stratum", "by_genre", "masked", "unmasked"):
        assert s[k] == stored[k], (arm, k, s[k], stored[k])
    assert s["claude_preregistered_go"] == stored["go"]
    report["arms"][arm] = s

pos = [(rid, t) for rid, t in truth.items() if t["class"] == "POS"]
overlaps = []
for i, (rid, t) in enumerate(pos):
    for sid, u in pos[i + 1:]:
        if t["genre"] != u["genre"]:
            continue
        longest = 0
        for start in range(78):
            match = u["pt"].find(t["pt"][start:start + 20])
            if match >= 0:
                n = 20
                while start + n < 97 and match + n < 97 and t["pt"][start + n] == u["pt"][match + n]:
                    n += 1
                longest = max(longest, n)
        if longest >= 20:
            overlaps.append({"first": rid, "second": sid, "shared_substring": longest, "genre": t["genre"]})
report["positive_overlaps_ge20"] = overlaps
OUT.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"arms": {a: {k: s[k] for k in ("ok", "exact", "full_key", "message_contact_equivalent",
    "claude_preregistered_go", "original_design_method_key_ge42_satisfied_even_with_message_equivalence")}
    for a, s in report["arms"].items()}, "witnesses": report["saved_reference_witnesses"],
    "positive_encryptions": report["positive_reference_encryptions"],
    "negatives": report["negatives_confident_best"]}, indent=2))
