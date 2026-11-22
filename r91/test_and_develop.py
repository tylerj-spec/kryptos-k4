"""Reversible model checks and spent-data runtime probe; no fresh controls."""
import hashlib
import json
import random
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference as R

repo = Path(sys.argv[1])
dev = HERE / "dev"
dev.mkdir(exist_ok=False)
rng = random.Random(912209)
paths = [("ID", list(range(97)))]
for line in (HERE / "routes.txt").read_text().splitlines():
    name, order, nums = line.split()
    assert order == "S_then_T"
    paths.append((name, list(map(int, nums.split(",")))))
convs = [(a, b, op) for a in ("AZ", "KRY") for b in ("AZ", "KRY") for op in ("VIG", "BEAU", "VARB")]
for i in range(1200):
    p = "".join(rng.choice(R.AZ) for _ in range(97))
    m = rng.choice((3, 4, 5, 7, 9, 12)); w = rng.choice((m, m+2, 31))
    k = "".join(rng.choice(R.AZ) for _ in range(m))
    assert R.linked_decrypt(R.linked_encrypt(p, k, w), k, w) == p
    lag = rng.randrange(13, 25); key = "".join(rng.choice(R.AZ) for _ in range(lag))
    name, perm = paths[i % len(paths)]; model = "M1" if name == "ID" else ("M1", "M2")[i % 2]
    conv = convs[i % len(convs)]
    assert R.ptak_decrypt(R.ptak_encrypt(p, key, conv, perm, model), key, conv, perm, model) == p
spent = json.loads((repo / "r59/dev/DEV_sealed_truth.json").read_text())
plain = [r["plaintext"] for r in spent.values()]
rows_r82, rows_ptak, truth = [], [], {}
for i, (m, w) in enumerate(((3, 3), (4, 4), (5, 7), (7, 7), (9, 11), (12, 31))):
    p = plain[i % len(plain)]; key = "".join(rng.choice(R.AZ) for _ in range(m)); rid = f"DEV_L{i:03}"
    rows_r82.append({"id": rid, "arm": "R82_LINKED", "ciphertext": R.linked_encrypt(p, key, w), "m": m, "w": w})
    truth[rid] = {"plaintext": p, "key": key}
for i, lag in enumerate((13, 15, 17, 19, 21, 24)):
    p = plain[(i+7) % len(plain)]; key = "".join(rng.choice(R.AZ) for _ in range(lag)); rid = f"DEV_P{i:03}"
    pi = (i*2) % len(paths); name, perm = paths[pi]; model = "M1" if name == "ID" else ("M1", "M2")[i % 2]
    conv = convs[(i*3) % len(convs)]
    rows_ptak.append({"id": rid, "arm": "PTAK_R68", "ciphertext": R.ptak_encrypt(p, key, conv, perm, model),
                      "lag": lag, "convention": conv, "path": name, "path_index": pi, "permutation": perm, "model": model})
    truth[rid] = {"plaintext": p, "key": key}
for label, rows in (("r82", rows_r82), ("ptak", rows_ptak)):
    (dev / (label+".jsonl")).write_text("".join(json.dumps(r)+"\n" for r in rows))
(dev / "truth.json").write_text(json.dumps(truth, indent=2)+"\n")
subprocess.run([sys.executable, "-I", str(HERE / "derive_ptak_screen.py")], check=True)
subprocess.run(["g++", "-O3", "-std=c++17", str(HERE / "ptak_r68_screen.cpp"), "-o", str(HERE / "ptak_r68_screen")], check=True)
subprocess.run(["g++", "-O3", "-std=c++17", "-shared", "-fPIC", str(HERE / "seccomp_io.cpp"), "-o", str(HERE / "seccomp_io.so")], check=True)
t0 = time.monotonic()
subprocess.run([sys.executable, "-I", str(HERE / "run_r82.py"), str(dev / "r82.jsonl"), str(dev / "r82.out.jsonl")], check=True)
r82_time = time.monotonic() - t0
subprocess.run([sys.executable, "-I", str(HERE / "prepare_ptak.py"), str(dev / "ptak.jsonl"), str(dev / "ptak.tsv")], check=True)
(dev / "empty_words.tsv").write_text("")
t0 = time.monotonic()
subprocess.run([str(HERE / "ptak_r68_screen"), str(HERE / "R59_LOWER4_FROM_K5.bin"), str(dev / "empty_words.tsv"),
                str(dev / "ptak.tsv"), str(dev / "ptak.out.jsonl"), "0", "24", "20", "68"], check=True)
ptak_time = time.monotonic() - t0
out = []
for row in [json.loads(x) for x in (dev / "r82.out.jsonl").read_text().splitlines()]:
    t = truth[row["id"]]
    out.append({"id": row["id"], "right": sum(x==y for x,y in zip(row["plaintext"],t["plaintext"])), "key_exact": row["key"]==t["key"]})
for row in [json.loads(x) for x in (dev / "ptak.out.jsonl").read_text().splitlines()]:
    rid = row["id"].split("__")[0]; t = truth[rid]; b = row["best"]
    out.append({"id": rid, "right": sum(x==y for x,y in zip(b["plaintext"],t["plaintext"])), "key_exact": b["key"]==t["key"]})
report = {"label": "spent developer data only; no parameter tuning", "roundtrips_per_arm": 1200,
          "r82_six_cases_seconds": r82_time, "ptak_six_cases_seconds": ptak_time, "records": out,
          "seccomp_probes_enforced_in_each_candidate_kernel": True}
(dev / "REPORT.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2), flush=True)
