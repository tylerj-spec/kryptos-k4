#!/usr/bin/env python3
"""R95 independent-model verification (Claude Code). PLAN.md fixes the steps. Written from r95/PREREGISTRATION.md;
imports nothing from r95/ (or any earlier round's cipher or scorer).
  build  WORKDIR TRAIN.txt   compile the pinned r59/blind/lm_build.cpp (g++ -O3 -std=c++17, as r91/model_build) and
                             build K=5; check bytes, sha256 and orders 1-4 against the baseline -> BUILD.json
  run    MODEL5.bin TRAIN.txt  provenance; the registered computation for K=4 and K=5 on the 48 spent cases x 650
                             one-swap neighbors; the recovered-shard check -> RESULT.json, CASES.json, NEIGHBORS.tsv
No K4 input. Standard library only."""
import array
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
EPS = 1e-9
R95_COMMIT = "8f59313c7d4fa6327e0cee41a39f092ebbeb23aa"
PIN = {"model5_sha256": "e9c0848f5e256814387968c09006a44804e90a72aeb79034d0b12abfcce31abd", "model5_bytes": 49426528,
       "model4": ("r91/R59_LOWER4_FROM_K5.bin", "85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41"),
       "train_sha256": "871627e5fd2f84b4afa976516303098f437b5c339b7297db238fcd1ecb0e0434", "train_bytes": 23373369,
       "builder": ("r59/blind/lm_build.cpp", "87b521d7654c07ead5b3bdbaa1da24c5ff60f10ae95b8f9aa8cf83673e2fc915"),
       "panel": ("r94/inputs/PANEL.tsv", "9b3ed6b49d437d4289f2a1126dd79b61ed7158b0e35b408bb39b1409aab8786c"),
       "truth": ("r94/inputs/PANEL_TRUTH.json", "27aecaf0aa2050e12d0d05e6c2ccc84b0598acd170e3e47f8667718732cf6ebf"),
       "shard_blob": "78221aaf4becf19efc0e9834028551bf43cc6237"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}


# ------------------------------------------------------------------------------------------------ build ---------
def build(work, train):
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    src = ROOT / PIN["builder"][0]
    rep = {"builder_sha256_ok": sha(src.read_bytes()) == PIN["builder"][1],
           "train_sha256_ok": sha(Path(train).read_bytes()) == PIN["train_sha256"],
           "train_bytes": Path(train).stat().st_size}
    cc = subprocess.run(["g++", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    subprocess.run(["g++", "-O3", "-std=c++17", str(src), "-o", str(work / "lm_build")], check=True)
    t0 = time.time()
    subprocess.run([str(work / "lm_build"), str(train), str(work / "lm5.bin"), "5"], check=True)
    m5 = (work / "lm5.bin").read_bytes()
    m4 = (ROOT / PIN["model4"][0]).read_bytes()
    rep.update(compiler=cc, build_wall_s=round(time.time() - t0, 2), model5_bytes=len(m5), model5_sha256=sha(m5),
               model5_sha256_ok=sha(m5) == PIN["model5_sha256"] and len(m5) == PIN["model5_bytes"],
               model4_sha256_ok=sha(m4) == PIN["model4"][1],
               header5=list(m5[:8]), header4=list(m4[:8]),
               orders1_4_equal_baseline=m5[8:len(m4)] == m4[8:])
    rep["pass"] = all(rep[k] for k in ("builder_sha256_ok", "train_sha256_ok", "model5_sha256_ok", "model4_sha256_ok",
                                       "orders1_4_equal_baseline"))
    (HERE / "BUILD.json").write_text(json.dumps(rep, indent=1) + "\n")
    print("BUILD", "PASS" if rep["pass"] else "FAIL", json.dumps(rep))


# ------------------------------------------------------------------------------------------------ model ---------
class Model:
    """Header 'R59LM', K, two pad bytes; then float32 log10 tables for orders 1..K, base 26, oldest letter first."""

    def __init__(self, path):
        raw = Path(path).read_bytes()
        assert raw[:5] == b"R59LM" and raw[6:8] == b"\0\0"
        self.K = raw[5]
        self.t, off = [], 8
        for k in range(1, self.K + 1):
            a = array.array("f")
            a.frombytes(raw[off:off + 4 * 26 ** k])
            assert sys.byteorder == "little" and len(a) == 26 ** k
            self.t.append(a)
            off += 4 * 26 ** k
        assert off == len(raw)

    def score(self, text):
        c = [ord(ch) - 65 for ch in text]
        tot = 0.0
        for i in range(len(c)):
            k = min(i + 1, self.K)
            code = 0
            for ch in c[i - k + 1:i + 1]:
                code = code * 26 + ch
            tot += self.t[k - 1][code]
        return tot


# ------------------------------------------------------------------------------------------------ cipher --------
def shifts(n, r, h, d1, d2, N=97):
    s1, s2 = [], []
    for i in range(N):
        tau = (i + r) // n
        s1.append((d1 * tau) % 26)
        s2.append((d2 * ((tau + h) // 26)) % 26)
    return s1, s2


def encrypt(pt, W1, W2, lab):
    ein, eout, n, r, h, d1, d2 = lab
    s1, s2 = shifts(n, r, h, d1, d2, len(pt))
    out = []
    for p, a, b in zip(pt, s1, s2):
        m = (W1[(ALPH[ein].index(p) + a) % 26] - a) % 26
        out.append(ALPH[eout][(W2[(m + b) % 26] - b) % 26])
    return "".join(out)


def decrypt_inv(ct, U, V, lab):
    ein, eout, n, r, h, d1, d2 = lab
    s1, s2 = shifts(n, r, h, d1, d2, len(ct))
    out = []
    for c, a, b in zip(ct, s1, s2):
        m = (V[(ALPH[eout].index(c) + b) % 26] - b) % 26
        out.append(ALPH[ein][(U[(m + a) % 26] - a) % 26])
    return "".join(out)


def inverse(W):
    inv = [0] * 26
    for x, y in enumerate(W):
        inv[y] = x
    return inv


def worked_example():
    """Registration's three-contact analogue: W1=[1,0,2], W2=[2,0,1], n=2, r=1, h=1, d1=d2=1, identity contacts."""
    q, W1, W2, n, r, h = 3, [1, 0, 2], [2, 0, 1], 2, 1, 1
    tau = [(i + r) // n for i in range(3)]
    s1 = [t % q for t in tau]
    s2 = [((t + h) // 26) % q for t in tau]
    P = [0, 1, 2]
    C = [(W2[((W1[(p + a) % q] - a) % q + b) % q] - b) % q for p, a, b in zip(P, s1, s2)]
    U, V = [W1.index(k) for k in range(q)], [W2.index(k) for k in range(q)]
    back = [(U[((V[(c + b) % q] - b) % q + a) % q] - a) % q for c, a, b in zip(C, s1, s2)]
    return {"fast": s1, "slow": s2, "ciphertext": C, "pass": s1 == [0, 1, 1] and s2 == [0, 0, 0] and C == [0, 0, 2]
            and back == P}


# ------------------------------------------------------------------------------------------------ run -----------
def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, check=True).stdout


def provenance():
    rep = {}
    anc = lambda a, b: subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", a, b]).returncode == 0  # noqa
    rep["chronology_c02b7a9_b347130_8f59313"] = anc("c02b7a92", "b3471306") and anc("b3471306", R95_COMMIT)
    proto = git("show", f"{R95_COMMIT}:r95/PROTOCOL.sha256").decode()
    bad = []
    for line in proto.splitlines():
        if line.strip():
            h, p = line.split()[0], line.split()[-1]
            try:
                ok = sha(git("show", f"{R95_COMMIT}:{p}")) == h
            except subprocess.CalledProcessError:
                ok = False
            if not ok:
                bad.append(p)
    rep["r95_protocol_entries"] = len([l for l in proto.splitlines() if l.strip()])
    rep["r95_protocol_mismatches"] = bad
    for k in ("panel", "truth", "model4", "builder"):
        rep[f"{k}_sha256_ok"] = sha((ROOT / PIN[k][0]).read_bytes()) == PIN[k][1]
    blob = git("rev-parse", f"{R95_COMMIT}:r95/development/neighbors/D_000.jsonl").decode().strip()
    rep["shard_blob_ok"] = blob == PIN["shard_blob"]
    rep["pass"] = rep["chronology_c02b7a9_b347130_8f59313"] and not bad and rep["shard_blob_ok"] and all(
        rep[f"{k}_sha256_ok"] for k in ("panel", "truth", "model4", "builder"))
    return rep


def best(rows, cond, key):
    """Exact numerical maximum of the stored score; the first enumeration label wins only on exactly equal scores."""
    b = None
    for row in rows:
        if cond(row) and (b is None or row[key] > b[key]):
            b = row
    return b


def run(model5_path, train):
    t0 = time.time()
    rep = {"reviewer": "Claude Code", "mode": "DEVELOPMENT_SYNTHETIC_TRUTH_ASSISTED_INDEPENDENT_REPLICATION",
           "k4_inputs": 0, "worked_example": worked_example(), "provenance": provenance()}
    builds = [json.loads((HERE / f).read_text()) for f in ("BUILD.json", "BUILD_CR.json") if (HERE / f).exists()]
    m5b = Path(model5_path).read_bytes()
    assert any(b["pass"] for b in builds) and sha(m5b) == PIN["model5_sha256"], "model reconstruction not verified"
    rep["model_reconstruction"] = "BUILD_CR.json (Amendment 1)" if not builds[0]["pass"] else "BUILD.json"
    M = {4: Model(ROOT / PIN["model4"][0]), 5: Model(model5_path)}
    assert M[4].K == 4 and M[5].K == 5
    train_text = Path(train).read_text()
    assert sha(train_text.encode()) == PIN["train_sha256"]
    truth = json.loads((ROOT / PIN["truth"][0]).read_text())
    panel = [l.split("\t") for l in (ROOT / PIN["panel"][0]).read_text().splitlines()[1:] if l]
    cases, nb_lines, shard_rows = [], ["id\twiring\tx\ty\tmatches\talias\tlm4_delta\tlm5_delta"], {}
    checks = {"true_encrypt_ok": 0, "true_decrypt_ok": 0, "neighbor_witness_ok": 0, "neighbors": 0}
    for rid, labs, ct in panel:
        f = labs.split(",")
        lab = (f[0], f[1], *map(int, f[2:]))
        t = truth[rid]
        assert t["ct"] == ct and tuple(t["label"]) == lab
        W1, W2, pt = t["W1"], t["W2"], t["pt"]
        U, V = inverse(W1), inverse(W2)
        checks["true_encrypt_ok"] += encrypt(pt, W1, W2, lab) == ct
        checks["true_decrypt_ok"] += decrypt_inv(ct, U, V, lab) == pt
        tsc = {k: M[k].score(pt) for k in (4, 5)}
        rows = []
        for wname in ("U", "V"):
            for x in range(26):
                for y in range(x + 1, 26):
                    U2, V2 = list(U), list(V)
                    T = U2 if wname == "U" else V2
                    T[x], T[y] = T[y], T[x]
                    text = decrypt_inv(ct, U2, V2, lab)
                    wit = encrypt(text, inverse(U2), inverse(V2), lab) == ct
                    checks["neighbor_witness_ok"] += wit
                    checks["neighbors"] += 1
                    s4, s5 = M[4].score(text), M[5].score(text)
                    rows.append({"wiring": wname, "swap": [x, y], "text": text,
                                 "matches": sum(a == b for a, b in zip(text, pt)), "alias": text == pt,
                                 "lm4": s4, "lm5": s5, "d4": s4 - tsc[4], "d5": s5 - tsc[5], "witness": wit})
        if rid == "D_000":
            shard_rows = rows
        summ = {"id": rid, "cell": t["cell"], "label": list(lab), "truth_lm4": tsc[4], "truth_lm5": tsc[5],
                "true_plaintext_verbatim_in_training": train_text.count(pt)}
        for k, dk in ((4, "d4"), (5, "d5")):
            above = [r for r in rows if r[dk] > EPS]
            ties = [r for r in rows if abs(r[dk]) <= EPS]
            bw = best(rows, lambda r: not r["alias"], f"lm{k}")
            b95 = best(rows, lambda r: r["matches"] < 95, f"lm{k}")
            summ[f"K{k}"] = {
                "any_below95_above_truth": any(r["matches"] < 95 for r in above),
                "below95_above_truth": sum(r["matches"] < 95 for r in above),
                "wrong_text_above_truth": sum(not r["alias"] for r in above),
                "m95_96_above_truth": sum(r["matches"] in (95, 96) for r in above),
                "ties": len(ties), "alias_ties": sum(r["alias"] for r in ties),
                "best_wrong_text": {"wiring": bw["wiring"], "swap": bw["swap"], "matches": bw["matches"],
                                    "delta": bw[dk]} if bw else None,
                "best_below95": {"wiring": b95["wiring"], "swap": b95["swap"], "matches": b95["matches"],
                                 "delta": b95[dk]} if b95 else None}
        summ["match_classes"] = {"alias_97": sum(r["alias"] for r in rows),
                                 "nonalias_97": sum(r["matches"] == 97 and not r["alias"] for r in rows),
                                 "m95_96": sum(r["matches"] in (95, 96) for r in rows),
                                 "below95": sum(r["matches"] < 95 for r in rows)}
        cases.append(summ)
        for r in rows:
            nb_lines.append(f"{rid}\t{r['wiring']}\t{r['swap'][0]}\t{r['swap'][1]}\t{r['matches']}\t{int(r['alias'])}\t"
                            f"{r['d4']:.12f}\t{r['d5']:.12f}")
    # recovered primary shard
    shard = [json.loads(l) for l in git("show", f"{R95_COMMIT}:r95/development/neighbors/D_000.jsonl").decode().splitlines() if l]
    mism = []
    for k, (a, b) in enumerate(zip(shard, shard_rows)):
        ok = (a["id"] == "D_000" and a["inverse_wiring"] == b["wiring"] and a["swap"] == b["swap"] and a["text"] == b["text"]
              and a["matches"] == b["matches"] and a["same_plaintext_on97"] == b["alias"] and a["forward_witness"] is True
              and abs(a["lm4_sum_log10"] - b["lm4"]) <= 1e-8 and abs(a["lm5_sum_log10"] - b["lm5"]) <= 1e-8
              and abs(a["lm4_delta"] - b["d4"]) <= 1e-8 and abs(a["lm5_delta"] - b["d5"]) <= 1e-8)
        if not ok:
            mism.append(k)
    rep["recovered_shard_check"] = {"records": len(shard), "expected": 650, "mismatching_records": mism[:20],
                                    "pass": len(shard) == 650 and not mism}
    rep["checks"] = checks
    cells = sorted({c["cell"] for c in cases})
    rep["endpoint"] = {}
    for k in (4, 5):
        n = sum(c[f"K{k}"]["any_below95_above_truth"] for c in cases)
        rep["endpoint"][f"K{k}"] = {
            "cases_with_any_below95_neighbor_above_truth": n,
            "by_cell": {cl: sum(c[f"K{k}"]["any_below95_above_truth"] for c in cases if c["cell"] == cl) for cl in cells},
            "cases_with_wrong_text_above_truth": sum(c[f"K{k}"]["wrong_text_above_truth"] > 0 for c in cases),
            "cases_with_95_96_above_truth": sum(c[f"K{k}"]["m95_96_above_truth"] > 0 for c in cases),
            "total_below95_neighbors_above_truth": sum(c[f"K{k}"]["below95_above_truth"] for c in cases)}
    n5 = rep["endpoint"]["K5"]["cases_with_any_below95_neighbor_above_truth"]
    rep["registered_rule_applied_to_replication"] = "GO_FOR_CONDITIONAL_DEVELOPMENT" if n5 <= 2 else "SCORE_NO_GO"
    rep["verbatim_truth_in_training_cases"] = sum(c["true_plaintext_verbatim_in_training"] > 0 for c in cases)
    rep["all_checks_pass"] = (rep["worked_example"]["pass"] and rep["provenance"]["pass"] and
                              checks["true_encrypt_ok"] == checks["true_decrypt_ok"] == 48 and
                              checks["neighbor_witness_ok"] == checks["neighbors"] == 31200 and
                              rep["recovered_shard_check"]["pass"])
    rep["wall_s"] = round(time.time() - t0, 2)
    (HERE / "CASES.json").write_text(json.dumps(cases, indent=1) + "\n")
    (HERE / "NEIGHBORS.tsv").write_text("\n".join(nb_lines) + "\n")
    rep["outputs_sha256"] = {f: sha((HERE / f).read_bytes()) for f in ("CASES.json", "NEIGHBORS.tsv")}
    (HERE / "RESULT.json").write_text(json.dumps(rep, indent=1) + "\n")
    print("checks", "PASS" if rep["all_checks_pass"] else "FAIL", "| K5", n5, "/48 | K4",
          rep["endpoint"]["K4"]["cases_with_any_below95_neighbor_above_truth"], "/48 |",
          rep["registered_rule_applied_to_replication"])


if __name__ == "__main__":
    {"build": lambda: build(sys.argv[2], sys.argv[3]), "run": lambda: run(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
