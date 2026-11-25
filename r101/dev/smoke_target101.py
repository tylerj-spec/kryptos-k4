#!/usr/bin/env python3
"""Development rehearsal of the R101 target pipeline on a SYNTHETIC tree (no K4 file, no published letter).
Builds DIR with copies of the R101 sources (constants re-pointed at synthetic files), a synthetic GO gate, a synthetic
'ciphertext' that is a plaintext-autokey encryption on a uniformly random alphabet (lag 2), and a synthetic CLUES
literal holding that text's letters at positions 21-33 and 63-73; then runs run_target101.py and evaluate101.py
there. Output is DEVELOPMENT_ONLY. Usage: python3 -I r101/dev/smoke_target101.py DIR"""
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

REAL = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REAL / "r99")]
import autokey99 as AK  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    D = Path(sys.argv[1]).resolve()
    assert not D.exists(), "fresh directory required"
    rng = random.Random(1017001)
    A = "".join(rng.sample(AK.AZ, 26))
    L, (s1, s2) = 2, rng.choice(AK.SIGNS)
    pt = "".join(rng.choice(AK.AZ) for _ in range(97))
    ct = AK.encrypt(pt, A, L, s1, s2, rng.randrange(26), [rng.randrange(26) for _ in range(L)])
    for d in ("r101/holdout", "r39/ic_gate", "r73/sealed"):
        (D / d).mkdir(parents=True)
    (D / "r99").symlink_to(REAL / "r99")
    (D / "r39/ic_gate/k4_ciphertext.txt").write_text(ct + "\n")
    (D / "r73/sealed/reveal_k4.py").write_text(f'CLUES = ((21, "{pt[21:34]}"), (63, "{pt[63:74]}"))\n')
    srcs = ("freealpha101.py", "dfs101.py", "validate101.py", "run_target101.py", "evaluate101.py")
    for f in srcs:
        (D / "r101" / f).write_bytes((REAL / "r101" / f).read_bytes())
    src = (D / "r101/run_target101.py").read_text()
    for name, path in (("CT_SHA", "r39/ic_gate/k4_ciphertext.txt"), ("CLUE_SHA", "r73/sealed/reveal_k4.py")):
        line = next(x for x in src.splitlines() if x.startswith(name + " = "))
        src = src.replace(line, f'{name} = "{sha((D / path).read_bytes())}"')
    (D / "r101/run_target101.py").write_text(src)
    (D / "r101/PREREGISTRATION.md").write_bytes((REAL / "r101/PREREGISTRATION.md").read_bytes())
    qa = json.loads((REAL / "r101/QA_MANIFEST.json").read_text())
    qa["gate_verdict"] = "GO"
    (D / "r101/QA_MANIFEST.json").write_text(json.dumps(qa, indent=1) + "\n")
    (D / "r101/SOURCE.sha256").write_text("".join(f"{sha((D / 'r101' / f).read_bytes())}  r101/{f}\n" for f in srcs))
    (D / "r101/PROTOCOL.sha256").write_text(f"{sha((D / 'r101/PREREGISTRATION.md').read_bytes())}  r101/PREREGISTRATION.md\n")
    (D / "r101/holdout/CHECKER_GATE.json").write_text(json.dumps(
        {"status": "COMPLETE", "gate_verdict": "GO", "source_sha256": {f: sha((D / "r101" / f).read_bytes()) for f in srcs}}) + "\n")
    (D / "r101/holdout/VALIDATION_RESOURCE.json").write_text(json.dumps(
        {"status": "COMPLETE", "wall_seconds": 1, "cpu_seconds": 1, "max_rss_mb": 1}) + "\n")
    names = ["r101/holdout/CHECKER_GATE.json", "r101/holdout/VALIDATION_RESOURCE.json", "r101/PROTOCOL.sha256",
             "r101/SOURCE.sha256"]
    (D / "r101/holdout/GATE_FROZEN.sha256").write_text("".join(f"{sha((D / n).read_bytes())}  {n}\n" for n in names))
    git = lambda *a: subprocess.run(["git", *a], cwd=D, check=True, capture_output=True)  # noqa: E731
    git("init", "-q")
    git("add", "-A")
    git("-c", "user.name=smoke", "-c", "user.email=smoke@example.invalid", "commit", "-qm", "synthetic")
    run = subprocess.run([sys.executable, "-I", str(D / "r101/run_target101.py"), "--out-dir", str(D / "r101/k4")],
                         cwd=D, capture_output=True, text=True)
    print(run.stdout, run.stderr)
    assert run.returncode == 0
    fz = [f"r101/k4/{n}" for n in ("INPUTS.tsv", "AGGREGATES.json")]
    (D / "r101/k4/FROZEN.sha256").write_text("".join(f"{sha((D / n).read_bytes())}  {n}\n" for n in fz))
    ev = subprocess.run([sys.executable, "-I", str(D / "r101/evaluate101.py"), str(D / "r101/k4/AGGREGATES.json"),
                         str(D / "EVAL.json")], cwd=D, capture_output=True, text=True)
    print(ev.stdout, ev.stderr)
    assert ev.returncode == 0
    res = json.loads((D / "EVAL.json").read_text())
    planted = [c for c in res["k4_cells"] if (c["L"], c["s1"], c["s2"]) == (L, s1, s2)]
    print(json.dumps({"development_only": True, "planted": [L, s1, s2], "planted_cell": planted,
                      **{k: v for k, v in res.items() if k not in ("k4_cells", "aggregates_sha256")}}))


if __name__ == "__main__":
    main()
