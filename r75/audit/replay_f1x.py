#!/usr/bin/env python3
"""T2 (audit/NEXT_STEPS.md): replay R75's F1X feasibility setting by setting with the independent checker
r75/audit/f1x_safe.py, and compare with the archived results. POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY.
Nothing is decoded and no key is completed: f1x_safe only propagates constraints and counts (Python int).

Grid (as r75/sealed/exact.py f1x, r75/PREREGISTRATION.md): cfg = (pa1, ca1, pa2, ca2, s1, s2), alphabets
AZ/KRY/PAL/ABS, signs +-1, 1,024 conventions in f1x's CFG1 order; periods m1, m2 = 1..26; 692,224 settings.

  --replay TARGET.tsv OUT.json IDS...   independent replay (f1x_safe only): per ciphertext, settings and feasible
                                        settings by checks, every feasible setting with >= 3 checks and its exact
                                        solution count, the period 15-18 cells, a sha256 of the full feasibility map
  --drop TARGET.tsv OUT.json IDS...     the equal-period cells 15..18 x 15..18 with one published letter set aside
                                        (R83a's F1XD step), exact counts
  --compare OUT.json REPLAY.json...     compare with (a) r75/k4/EXACT.json, (b) r83/k4/run/R83A.json F1XD, (c) the
                                        original f1x() re-run with its decode branch switched off (R75's grid_of()
                                        replaced by None, as r83/f1xd_lowmem.py), setting by setting
Usage: python3 -I r75/audit/replay_f1x.py --replay r75/k4/TARGET.tsv OUT.json K4 NULL_000 ..."""
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import f1x_safe as F  # noqa: E402

A4 = ("AZ", "KRY", "PAL", "ABS")
CFG1 = [(pa1, ca1, pa2, ca2, s1, s2) for pa1 in A4 for ca1 in A4 for pa2 in A4 for ca2 in A4
        for s1 in (1, -1) for s2 in (1, -1)]
PERIODS = [(m1, m2) for m1 in range(1, 27) for m2 in range(1, 27)]
BIG = range(15, 19)
I63 = 2 ** 63


def clues():
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402  -- post-freeze audit only
    pos = [o + j for o, t in CLUES for j in range(len(t))]
    known = "".join(t for _, t in CLUES)
    assert pos == list(range(21, 34)) + list(range(63, 74))
    return pos, known


def load(tsv):
    rows = [l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l]
    return dict(rows)


def replay_one(args):
    rid, ct = args
    pos, known = clues()
    tested, feas = {}, {}
    ge3, big = [], {"settings": 0, "feasible": 0, "feasible_over_2^63": 0, "max_active_count_digits": 0}
    bitmap = bytearray((len(CFG1) * len(PERIODS) + 7) // 8)
    k = 0
    for ci, cfg in enumerate(CFG1):
        for m1, m2 in PERIODS:
            r = F.check_setting(ct, pos, known, cfg, m1, m2)
            ck = r["checks"]
            tested[ck] = tested.get(ck, 0) + 1
            if r["feasible"]:
                feas[ck] = feas.get(ck, 0) + 1
                bitmap[k >> 3] |= 1 << (k & 7)
                if ck >= 3:
                    ge3.append([ci, m1, m2, ck, str(r["active_solution_count"])])
            if m1 in BIG and m2 in BIG:
                big["settings"] += 1
                if r["feasible"]:
                    big["feasible"] += 1
                    a = r["active_solution_count"]
                    big["feasible_over_2^63"] += a >= I63
                    big["max_active_count_digits"] = max(big["max_active_count_digits"], len(str(a)))
            k += 1
    return rid, {"tested_by_checks": dict(sorted(tested.items())), "feasible_by_checks": dict(sorted(feas.items())),
                 "feasible_ge3": len(ge3), "ge3_settings": ge3, "periods_15_18": big,
                 "feasibility_map_sha256": hashlib.sha256(bytes(bitmap)).hexdigest()}


def drop_one(args):
    """Equal-period block 15..18 x 15..18: settings infeasible with all 24 letters but feasible once one is set aside,
    with exact counts (R83a F1XD semantics)."""
    rid, ct = args
    pos, known = clues()
    out = []
    for ci, cfg in enumerate(CFG1):
        for m1 in BIG:
            for m2 in BIG:
                full = F.check_setting(ct, pos, known, cfg, m1, m2)
                if full["feasible"] or full["checks"] < 3:
                    continue
                freed = []
                for a in range(len(pos)):
                    p2 = pos[:a] + pos[a + 1:]
                    k2 = known[:a] + known[a + 1:]
                    r = F.check_setting(ct, p2, k2, cfg, m1, m2)
                    if r["feasible"]:
                        freed.append([pos[a], str(r["active_solution_count"]), r["active_solution_count"] >= I63])
                if freed:
                    out.append({"cfg": list(cfg), "m1": m1, "m2": m2, "checks": full["checks"], "freed_by": freed})
    return rid, out


def run_pool(fn, tsv, ids, procs=4):
    cts = load(tsv)
    with Pool(procs) as pool:
        return dict(pool.imap_unordered(fn, [(i, cts[i]) for i in ids]))


# ------------------------------------------------------------------------------------------------ comparison
def original_ge3(ct):
    """The ORIGINAL f1x() (r75/sealed/exact.py, unchanged file) with its decode branch switched off in this process
    only: {(cfg, m1, m2): (checks, nsol as int64)} for every feasible setting with >= 3 checks, and its tallies."""
    import numpy as np
    sys.path.insert(0, str(ROOT / "r75"))
    sys.path.insert(0, str(ROOT / "r75" / "sealed"))
    import exact as R75
    R75.grid_of = lambda u: None
    pos, known = clues()
    col = R75.Collector(None)
    R75.f1x(np.array([ord(ch) - 65 for ch in ct]), np.array(pos), np.array([ord(ch) - 65 for ch in known]), col)
    assert all(r["decode"] is None for r in col.rows)
    rows = {(tuple(r["setting"]["cfg"]), r["setting"]["m1"], r["setting"]["m2"]):
            (r["checks"], r["setting"]["solutions"]) for r in col.rows}
    return rows, dict(col.tested["F1X"]), dict(col.feasible["F1X"])


def compare(out, replays):
    rep = {}
    for p in replays:
        rep.update(json.loads(Path(p).read_text())["results"])
    ex75 = json.loads((ROOT / "r75/k4/EXACT.json").read_text())
    r83 = json.loads((ROOT / "r83/k4/run/R83A.json").read_text())["F1XD"]["none"]
    t75, t83 = load(ROOT / "r75/k4/TARGET.tsv"), load(ROOT / "r83/k4/TARGET.tsv")
    res = {"feasibility_disagreements": [], "count_disagreements": [], "per_ciphertext": {}}
    for key, r in rep.items():
        src, rid = key.split(":")
        ct = (t75 if src == "R75" else t83)[rid]
        new = {(CFG1[ci], m1, m2): (ck, int(n)) for ci, m1, m2, ck, n in r["ge3_settings"]}
        orig, otested, ofeas = original_ge3(ct)
        row = {"feasible_ge3_replay": len(new), "feasible_ge3_original_rerun": len(orig)}
        # (c) setting by setting against the original code path
        for s in set(new) ^ set(orig):
            res["feasibility_disagreements"].append({"ciphertext": key, "setting": [list(s[0]), s[1], s[2]],
                                                     "replay": s in new, "original": s in orig})
        for s in set(new) & set(orig):
            true, old = new[s][1], orig[s][1]
            if true != old or new[s][0] != orig[s][0]:
                res["count_disagreements"].append({"ciphertext": key, "setting": [list(s[0]), s[1], s[2]],
                                                   "checks": [new[s][0], orig[s][0]], "true_count": str(true),
                                                   "int64_count": str(old), "true_over_2^63": true >= I63})
        row["tallies_equal_original_rerun"] = (
            {int(k): v for k, v in r["tested_by_checks"].items()} == {int(k): v for k, v in otested.items()} and
            {int(k): v for k, v in r["feasible_by_checks"].items()} == {int(k): v for k, v in ofeas.items() if v})
        # (a) R75's archive
        if src == "R75":
            if rid == "K4":
                a = ex75["K4"]["F1X"]
                row["archive_R75_tested_equal"] = {int(k): v for k, v in a["settings_with_checks"].items()} == \
                    {int(k): v for k, v in r["tested_by_checks"].items()}
                row["archive_R75_feasible_equal"] = {int(k): v for k, v in a["feasible_by_checks"].items() if v} == \
                    {int(k): v for k, v in r["feasible_by_checks"].items()}
                lst = a["feasible_list"]
                bad = [x for x in lst if (tuple(x["setting"]["cfg"]), x["setting"]["m1"], x["setting"]["m2"]) not in new
                       or new[(tuple(x["setting"]["cfg"]), x["setting"]["m1"], x["setting"]["m2"])][1]
                       != x["setting"]["solutions"]]
                row["archive_R75_list_checked"] = len(lst)
                row["archive_R75_list_mismatch"] = bad
            else:
                row["archive_R75_feasible_ge3"] = ex75["shuffles"][rid]["F1X"]["feasible"]
                row["archive_R75_feasible_ge3_equal"] = ex75["shuffles"][rid]["F1X"]["feasible"] == len(new)
        # (b) R83a's F1XD record (its EXACT tallies)
        if src == "R83" or rid == "K4":
            a = r83[rid]["F1X"]
            row["archive_R83_tested_equal"] = {int(k): v for k, v in a["tested_by_checks"].items()} == \
                {int(k): v for k, v in r["tested_by_checks"].items()}
            row["archive_R83_feasible_equal"] = {int(k): v for k, v in a["feasible_by_checks"].items() if v} == \
                {int(k): v for k, v in r["feasible_by_checks"].items()}
            lst = a["feasible_list"]
            row["archive_R83_list_checked"] = len(lst)
            row["archive_R83_list_mismatch"] = [x for x in lst if (tuple(x["cfg"]), x["m1"], x["m2"]) not in new]
        row["periods_15_18"] = r["periods_15_18"]
        res["per_ciphertext"][key] = row
    res["n_feasibility_disagreements"] = len(res["feasibility_disagreements"])
    res["n_count_disagreements"] = len(res["count_disagreements"])
    res["count_disagreements_all_over_2^63"] = all(d["true_over_2^63"] for d in res["count_disagreements"])
    Path(out).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k.startswith("n_") or k.startswith("count_d")}))


def main():
    mode = sys.argv[1]
    if mode in ("--replay", "--drop"):
        tsv, out, ids = sys.argv[2], sys.argv[3], sys.argv[4:]
        src = "R75" if "r75" in tsv else "R83"
        res = run_pool(replay_one if mode == "--replay" else drop_one, tsv, ids)
        Path(out).write_text(json.dumps({"classification": "POST-FREEZE CRIB-ASSISTED EXCLUSION-ONLY REPLAY (T2); "
                                                           "no decode, no completed key",
                                         "checker": "r75/audit/f1x_safe.py check_setting", "target": tsv,
                                         "results": {f"{src}:{k}": res[k] for k in ids}}, indent=0) + "\n")
        print(mode, "done", len(res))
    elif mode == "--compare":
        compare(sys.argv[2], sys.argv[3:])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
