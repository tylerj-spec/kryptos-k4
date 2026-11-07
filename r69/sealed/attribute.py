#!/usr/bin/env python3
"""R69 analysis (after the freeze and verify). Uses no published K4 letters at any point.
Per ciphertext, from the 16 F totals T(F_b1b2b3b4) (bit 1 = that carved row read right-to-left):
  main effect of row r : E_r = mean T(b_r = 1) - mean T(b_r = 0),  r = 1..4 (row 1 = 4 letters, rows 2-4 = 31);
  interaction rows 2x4 : I_24 = mean T(b2 = b4) - mean T(b2 != b4)   (descriptive only);
  S_max = max over the 16 F readings.
Set-A ciphertexts also get the B profile: B_max = max over the 62 B readings, its argmax, and
  D = B_max - T(SNAKE_L)  (how much the best start column beats the sculpture's column 27).
Modes:
  gate  BLIND.tsv RESULTS.jsonl SEALED_TRUTH.json REPORT.json
        F plants: rows_ok = signs of E_2, E_3, E_4 all match the true bits (+ if reversed). PASS iff >= 24 of 32.
        B plants: argmax over B readings equals the true reading (reported, not gated).
  k4    TARGET.tsv RESULTS.jsonl REPORT.json
        nulls = SHUF_* (300) and R67_CTRL_* (192), pooled N = 492.
        p_r = (1 + #nulls with |E_r| >= |E_r(K4)|) / (N + 1);  p_S = (1 + #nulls with S_max >= K4's) / (N + 1).
        Row r is SIGNIFICANT iff p_r <= 0.0025 (= 0.01 / 4).
        Outcome: ARTIFACT if p_S > 0.01; else ALTERNATING if the significant rows are exactly {2, 4}, both with E > 0;
                 else ROW_SPECIFIC if any row is significant; else DIFFUSE.
        Secondary (descriptive): K4's B_max and D against SHUF_000-099; argmax start column and parity."""
import json
import sys
from pathlib import Path

F = [f"F_{b:04b}" for b in range(16)]


def contrasts(read):
    t = {n: read[n]["total"] for n in F}
    bit = lambda n, r: int(n[1 + r])  # noqa: E731  (r = 1..4 -> character r of 'b1b2b3b4' after 'F_')
    e = {}
    for r in range(1, 5):
        on = [t[n] for n in F if bit(n, r)]
        off = [t[n] for n in F if not bit(n, r)]
        e[f"E{r}"] = sum(on) / 8 - sum(off) / 8
    eq = [t[n] for n in F if bit(n, 2) == bit(n, 4)]
    ne = [t[n] for n in F if bit(n, 2) != bit(n, 4)]
    e["I24"] = sum(eq) / 8 - sum(ne) / 8
    e["S_max"] = max(t.values())
    e["S_argmax"] = max(F, key=lambda n: (t[n], n))
    if any(n.startswith("B_") for n in read):
        b = {n: v["total"] for n, v in read.items() if n.startswith("B_")}
        e["B_max"] = max(b.values())
        e["B_argmax"] = max(b, key=lambda n: (b[n], n))
        e["D"] = e["B_max"] - read["B_c27_q0"]["total"]
    return e


def load(res):
    return {json.loads(l)["id"]: json.loads(l) for l in Path(res).read_text().splitlines() if l.strip()}


def gate(blind, res, truth_p, rep):
    rows, truth = load(res), json.loads(Path(truth_p).read_text())
    assert set(rows) == set(truth) == {l.split("\t")[0] for l in Path(blind).read_text().splitlines()[1:] if l}
    out, f_ok, b_ok = [], 0, 0
    for i, t in sorted(truth.items()):
        c = contrasts(rows[i]["readings"])
        rec = {"id": i, "true": t["reading"], **c}
        if t["reading"].startswith("F_"):
            bits = t["reading"][2:]
            rec["rows_ok"] = all((c[f"E{r}"] > 0) == (bits[r - 1] == "1") for r in (2, 3, 4))
            rec["argmax_ok"] = c["S_argmax"] == t["reading"]
            f_ok += rec["rows_ok"]
        else:
            rec["argmax_ok"] = c["B_argmax"] == t["reading"]
            b_ok += rec["argmax_ok"]
        out.append(rec)
    nf = sum(1 for t in truth.values() if t["reading"].startswith("F_"))
    summ = {"F_plants": nf, "F_rows_ok": f_ok, "F_argmax_ok": sum(r["argmax_ok"] for r in out if r["true"].startswith("F_")),
            "B_plants": len(truth) - nf, "B_argmax_ok": b_ok, "bar": 24, "passed": f_ok >= 24}
    Path(rep).write_text(json.dumps({"summary": summ, "rows": out}, indent=1) + "\n")
    print("R69 gate:", summ, "K4 RUN" if summ["passed"] else "GATE FAILED: INCONCLUSIVE, no K4 run")
    for r in out:
        print(r["id"], r["true"], "rows_ok" if r.get("rows_ok") else "", "argmax_ok" if r["argmax_ok"] else "",
              {k: round(r[k], 1) for k in ("E1", "E2", "E3", "E4")}, r["S_argmax"], r.get("B_argmax", ""))


def k4(target, res, rep):
    rows = load(res)
    ids = [l.split("\t")[0] for l in Path(target).read_text().splitlines()[1:] if l]
    assert set(rows) == set(ids)
    c = {i: contrasts(rows[i]["readings"]) for i in ids}
    nulls = [i for i in ids if i.startswith(("SHUF_", "R67_"))]
    assert len(nulls) == 492
    k = c["K4"]
    n1 = len(nulls) + 1
    rep_rows = {}
    for r in range(1, 5):
        key = f"E{r}"
        ge = sum(abs(c[i][key]) >= abs(k[key]) for i in nulls)
        rep_rows[r] = {"E": k[key], "p": (1 + ge) / n1, "nulls_ge": ge,
                       "p_shuffles": (1 + sum(abs(c[i][key]) >= abs(k[key]) for i in nulls if i.startswith("SHUF_"))) / 301,
                       "p_structured": (1 + sum(abs(c[i][key]) >= abs(k[key]) for i in nulls if i.startswith("R67_"))) / 193,
                       "null_abs_sorted_top5": sorted((abs(c[i][key]) for i in nulls), reverse=True)[:5],
                       "significant": (1 + ge) / n1 <= 0.0025}
    ge_s = sum(c[i]["S_max"] >= k["S_max"] for i in nulls)
    p_s = (1 + ge_s) / n1
    sig = sorted(r for r, d in rep_rows.items() if d["significant"])
    if p_s > 0.01:
        outcome = "ARTIFACT"
    elif sig == [2, 4] and rep_rows[2]["E"] > 0 and rep_rows[4]["E"] > 0:
        outcome = "ALTERNATING"
    elif sig:
        outcome = "ROW_SPECIFIC"
    else:
        outcome = "DIFFUSE"
    ge_i = sum(abs(c[i]["I24"]) >= abs(k["I24"]) for i in nulls)
    shuf_a = [i for i in ids if i.startswith("SHUF_") and rows[i]["set"] == "A"]
    sec = {"K4_B_max": k["B_max"], "K4_B_argmax": k["B_argmax"], "K4_D": k["D"],
           "p_B_max_vs_100_shuffles": (1 + sum(c[i]["B_max"] >= k["B_max"] for i in shuf_a)) / (len(shuf_a) + 1),
           "p_D_vs_100_shuffles": (1 + sum(c[i]["D"] >= k["D"] for i in shuf_a)) / (len(shuf_a) + 1),
           "K4_profile_by_start_column": {f"c{col:02d}": max(rows["K4"]["readings"][f"B_c{col:02d}_q{q}"]["total"]
                                                             for q in (0, 1)) for col in range(31)}}
    out = {"outcome": outcome, "significant_rows": sig, "rows": rep_rows,
           "S_max": {"K4": k["S_max"], "argmax": k["S_argmax"], "p": p_s, "nulls_ge": ge_s},
           "I24": {"K4": k["I24"], "p_descriptive": (1 + ge_i) / n1},
           "K4_F_totals": {n: rows["K4"]["readings"][n]["total"] for n in F},
           "secondary_B": sec, "null_counts": {"shuffles": 300, "structured": 192}}
    Path(rep).write_text(json.dumps(out, indent=1) + "\n")
    print("R69 outcome:", outcome, "significant rows:", sig)
    for r, d in rep_rows.items():
        print(f"  row {r}: E {d['E']:+.2f}  p {d['p']:.4f}  (shuffles {d['p_shuffles']:.4f}, structured {d['p_structured']:.4f})")
    print(f"  S_max {k['S_max']:.2f} ({k['S_argmax']}) p {p_s:.4f}; I24 {k['I24']:+.2f} p {(1 + ge_i) / n1:.4f}")
    print(f"  secondary: B_max {k['B_max']:.2f} at {k['B_argmax']}, D {k['D']:+.2f}, "
          f"p(B_max) {sec['p_B_max_vs_100_shuffles']:.3f}, p(D) {sec['p_D_vs_100_shuffles']:.3f}")


if __name__ == "__main__":
    if sys.argv[1] == "gate":
        gate(*sys.argv[2:6])
    elif sys.argv[1] == "k4":
        k4(*sys.argv[2:5])
    else:
        raise SystemExit("mode must be gate or k4")
