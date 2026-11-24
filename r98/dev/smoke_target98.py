#!/usr/bin/env python3
"""Development rehearsal of the R98 target pipeline on a SYNTHETIC tree (no K4 file, no published letter).
Builds DIR with copies of the R98 sources (constants re-pointed at synthetic files), a synthetic GO gate, a
synthetic 'ciphertext' that is a planted Slidefair encryption of random text with tier alphabets, and a synthetic
CLUES literal holding that text's letters at positions 21-33 and 63-73. Then runs run_target98.py and
evaluate98.py there. Output is DEVELOPMENT_ONLY. Usage: python3 -I r98/dev/smoke_target98.py DIR"""
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

REAL = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REAL / "r98"), str(REAL / "r76")]
import slidefair98 as SF  # noqa: E402
import alphabets as AL  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    D = Path(sys.argv[1]).resolve()
    assert not D.exists(), "fresh directory required"
    rng = random.Random(987001)
    tier = [a for _, a in AL.large_tier()]
    conv = SF.CONVENTIONS[rng.randrange(16)]
    PA, CA = rng.choice(tier), rng.choice(tier)
    pt = "".join(rng.choice(SF.AZ) for _ in range(97))
    ct = SF.encrypt(pt, PA, CA, conv, [rng.randrange(26) for _ in range(97)])
    (D / "r98/holdout").mkdir(parents=True)
    (D / "r39/ic_gate").mkdir(parents=True)
    (D / "r73/sealed").mkdir(parents=True)
    (D / "r76").symlink_to(REAL / "r76")
    (D / "r39/ic_gate/k4_ciphertext.txt").write_text(ct + "\n")
    (D / "r73/sealed/reveal_k4.py").write_text(f'CLUES = ((21, "{pt[21:34]}"), (63, "{pt[63:74]}"))\n')
    ct_sha = sha((D / "r39/ic_gate/k4_ciphertext.txt").read_bytes())
    clue_sha = sha((D / "r73/sealed/reveal_k4.py").read_bytes())
    for f in ("slidefair98.py", "checker98.py", "evaluate98.py", "validate98.py"):
        (D / "r98" / f).write_bytes((REAL / "r98" / f).read_bytes())
    src = (REAL / "r98/run_target98.py").read_text()
    for name, val in (("CT_SHA", ct_sha), ("CLUE_SHA", clue_sha)):
        line = next(x for x in src.splitlines() if x.startswith(name + " = "))
        src = src.replace(line, f'{name} = "{val}"')
    (D / "r98/run_target98.py").write_text(src)
    (D / "r98/PREREGISTRATION.md").write_bytes((REAL / "r98/PREREGISTRATION.md").read_bytes())
    qa = json.loads((REAL / "r98/QA_MANIFEST.json").read_text())
    qa["gate_verdict"] = "GO"
    (D / "r98/QA_MANIFEST.json").write_text(json.dumps(qa, indent=1) + "\n")
    srcs = ("slidefair98.py", "checker98.py", "validate98.py", "run_target98.py", "evaluate98.py")
    (D / "r98/SOURCE.sha256").write_text("".join(f"{sha((D / 'r98' / f).read_bytes())}  r98/{f}\n" for f in srcs))
    (D / "r98/PROTOCOL.sha256").write_text(f"{sha((D / 'r98/PREREGISTRATION.md').read_bytes())}  r98/PREREGISTRATION.md\n")
    gate = {"status": "COMPLETE", "gate_verdict": "GO",
            "source_sha256": {f: sha((D / "r98" / f).read_bytes()) for f in srcs}}
    (D / "r98/holdout/CHECKER_GATE.json").write_text(json.dumps(gate) + "\n")
    (D / "r98/holdout/VALIDATION_RESOURCE.json").write_text(json.dumps(
        {"status": "COMPLETE", "wall_seconds": 1, "cpu_seconds": 1, "max_rss_mb": 1}) + "\n")
    names = ["r98/holdout/CHECKER_GATE.json", "r98/holdout/VALIDATION_RESOURCE.json", "r98/PROTOCOL.sha256",
             "r98/SOURCE.sha256"]
    (D / "r98/holdout/GATE_FROZEN.sha256").write_text("".join(f"{sha((D / n).read_bytes())}  {n}\n" for n in names))
    git = lambda *a: subprocess.run(["git", *a], cwd=D, check=True, capture_output=True)  # noqa: E731
    git("init", "-q")
    git("add", "-A")
    git("-c", "user.name=smoke", "-c", "user.email=smoke@example.invalid", "commit", "-qm", "synthetic")
    run = subprocess.run([sys.executable, "-I", str(D / "r98/run_target98.py"), "--out-dir", str(D / "r98/k4")],
                         cwd=D, capture_output=True, text=True)
    print(run.stdout, run.stderr)
    assert run.returncode == 0
    fz = [f"r98/k4/{n}" for n in ("INPUTS.tsv", "AGGREGATES.json")]
    (D / "r98/k4/FROZEN.sha256").write_text("".join(f"{sha((D / n).read_bytes())}  {n}\n" for n in fz))
    ev = subprocess.run([sys.executable, "-I", str(D / "r98/evaluate98.py"), str(D / "r98/k4/AGGREGATES.json"),
                         str(D / "EVAL.json")], cwd=D, capture_output=True, text=True)
    print(ev.stdout, ev.stderr)
    assert ev.returncode == 0
    res = json.loads((D / "EVAL.json").read_text())
    print(json.dumps({"development_only": True, "planted_convention": conv, "decision": res["decision"],
                      "synthetic_target": res["k4"], "shuffles": res["shuffles"]}))


if __name__ == "__main__":
    main()
