#!/usr/bin/env python3
"""Development rehearsal of the R99 target pipeline on a SYNTHETIC tree (no K4 file, no published letter).
Builds DIR with copies of the R99 sources (constants re-pointed at synthetic files), a synthetic GO gate, a
synthetic 'ciphertext' that is a planted keyed-tableau plaintext-autokey encryption of random text with tier alphabets, and a synthetic
CLUES literal holding that text's letters at positions 21-33 and 63-73. Then runs run_target99.py and
evaluate99.py there. Output is DEVELOPMENT_ONLY. Usage: python3 -I r99/dev/smoke_target99.py DIR"""
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

REAL = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REAL / "r99"), str(REAL / "r76")]
import autokey99 as AK  # noqa: E402
import alphabets as AL  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    D = Path(sys.argv[1]).resolve()
    assert not D.exists(), "fresh directory required"
    rng = random.Random(997001)
    tier = [a for _, a in AL.large_tier()]
    L, (s1, s2), c = rng.choice([3, 8, 20, 40]), rng.choice(AK.SIGNS), rng.randrange(26)
    conv = (L, s1, s2, c)
    A = rng.choice(tier)
    pt = "".join(rng.choice(AK.AZ) for _ in range(97))
    ct = AK.encrypt(pt, A, L, s1, s2, c, [rng.randrange(26) for _ in range(L)])
    (D / "r99/holdout").mkdir(parents=True)
    (D / "r39/ic_gate").mkdir(parents=True)
    (D / "r73/sealed").mkdir(parents=True)
    (D / "r76").symlink_to(REAL / "r76")
    (D / "r39/ic_gate/k4_ciphertext.txt").write_text(ct + "\n")
    (D / "r73/sealed/reveal_k4.py").write_text(f'CLUES = ((21, "{pt[21:34]}"), (63, "{pt[63:74]}"))\n')
    ct_sha = sha((D / "r39/ic_gate/k4_ciphertext.txt").read_bytes())
    clue_sha = sha((D / "r73/sealed/reveal_k4.py").read_bytes())
    for f in ("autokey99.py", "checker99.py", "evaluate99.py", "validate99.py"):
        (D / "r99" / f).write_bytes((REAL / "r99" / f).read_bytes())
    src = (REAL / "r99/run_target99.py").read_text()
    for name, val in (("CT_SHA", ct_sha), ("CLUE_SHA", clue_sha)):
        line = next(x for x in src.splitlines() if x.startswith(name + " = "))
        src = src.replace(line, f'{name} = "{val}"')
    (D / "r99/run_target99.py").write_text(src)
    (D / "r99/PREREGISTRATION.md").write_bytes((REAL / "r99/PREREGISTRATION.md").read_bytes())
    qa = json.loads((REAL / "r99/QA_MANIFEST.json").read_text())
    qa["gate_verdict"] = "GO"
    (D / "r99/QA_MANIFEST.json").write_text(json.dumps(qa, indent=1) + "\n")
    srcs = ("autokey99.py", "checker99.py", "validate99.py", "run_target99.py", "evaluate99.py")
    (D / "r99/SOURCE.sha256").write_text("".join(f"{sha((D / 'r99' / f).read_bytes())}  r99/{f}\n" for f in srcs))
    (D / "r99/PROTOCOL.sha256").write_text(f"{sha((D / 'r99/PREREGISTRATION.md').read_bytes())}  r99/PREREGISTRATION.md\n")
    gate = {"status": "COMPLETE", "gate_verdict": "GO",
            "source_sha256": {f: sha((D / "r99" / f).read_bytes()) for f in srcs}}
    (D / "r99/holdout/CHECKER_GATE.json").write_text(json.dumps(gate) + "\n")
    (D / "r99/holdout/VALIDATION_RESOURCE.json").write_text(json.dumps(
        {"status": "COMPLETE", "wall_seconds": 1, "cpu_seconds": 1, "max_rss_mb": 1}) + "\n")
    names = ["r99/holdout/CHECKER_GATE.json", "r99/holdout/VALIDATION_RESOURCE.json", "r99/PROTOCOL.sha256",
             "r99/SOURCE.sha256"]
    (D / "r99/holdout/GATE_FROZEN.sha256").write_text("".join(f"{sha((D / n).read_bytes())}  {n}\n" for n in names))
    git = lambda *a: subprocess.run(["git", *a], cwd=D, check=True, capture_output=True)  # noqa: E731
    git("init", "-q")
    git("add", "-A")
    git("-c", "user.name=smoke", "-c", "user.email=smoke@example.invalid", "commit", "-qm", "synthetic")
    run = subprocess.run([sys.executable, "-I", str(D / "r99/run_target99.py"), "--out-dir", str(D / "r99/k4")],
                         cwd=D, capture_output=True, text=True)
    print(run.stdout, run.stderr)
    assert run.returncode == 0
    fz = [f"r99/k4/{n}" for n in ("INPUTS.tsv", "AGGREGATES.json")]
    (D / "r99/k4/FROZEN.sha256").write_text("".join(f"{sha((D / n).read_bytes())}  {n}\n" for n in fz))
    ev = subprocess.run([sys.executable, "-I", str(D / "r99/evaluate99.py"), str(D / "r99/k4/AGGREGATES.json"),
                         str(D / "EVAL.json")], cwd=D, capture_output=True, text=True)
    print(ev.stdout, ev.stderr)
    assert ev.returncode == 0
    res = json.loads((D / "EVAL.json").read_text())
    print(json.dumps({"development_only": True, "planted": conv, "decision": res["decision"],
                      "planted_lag": res["per_lag"].get(str(L)),
                      **{k: v for k, v in res.items() if k not in ("per_lag", "aggregates_sha256")}}))


if __name__ == "__main__":
    main()
