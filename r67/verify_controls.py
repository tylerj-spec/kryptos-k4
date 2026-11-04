#!/usr/bin/env python3
"""R67 pre-reveal integrity audit. Does NOT read sealed synthetic truth or K4 clues.

Usage: python3 r67/verify_controls.py BLIND.tsv RUN_DIR STAGED_READONLY_DIR REPORT.json
Validates all pinned model, binary, runner and route SHA256 hashes, both frozen
manifests, and independent reencryption of *every* 97-letter raw solver witness.
Only PASSED reports permit post-freeze descriptive evaluation.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r64/sealed"))
from common import forward, routes  # noqa: E402


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pins():
    pin = {}
    for line in (ROOT / "r67/REFERENCE_SHA256").read_text().splitlines():
        if line and not line.startswith("#"):
            h, role, path = line.split("  ", 2)
            pin[(role, Path(path).name)] = (h, path)
    if len(pin) != 10:
        raise ValueError("expected exactly ten pinned R65 dependencies")
    return pin


def frozen_lines(p):
    pairs = {}
    for line in p.read_text().splitlines():
        parts = line.split("  ", 2)
        if len(parts) != 3:
            raise ValueError("invalid frozen manifest")
        h, role, filename = parts
        if (role, filename) in pairs:
            raise ValueError("duplicate frozen role/filename")
        pairs[(role, filename)] = h
    return pairs


def main():
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    inp, run, stage, report = map(Path, sys.argv[1:])
    if report.exists():
        raise SystemExit("refusing to overwrite verification report")
    problems = []
    pinned = pins()
    frozen = frozen_lines(run / "FROZEN.sha256")
    for (role, name), (expected, path) in pinned.items():
        if frozen.get((role, name)) != expected:
            problems.append("frozen dependency mismatch " + role + "/" + name)
        staged = stage / path
        if not staged.is_file() or sha(staged) != expected:
            problems.append("pinned dependency or stage mismatch " + path)
    for field, path in (("input", inp), ("results", run / "RESULTS.jsonl")):
        matches = [(name, h) for (role, name), h in frozen.items() if role == field]
        if len(matches) != 1 or sha(path) != matches[0][1]:
            problems.append(field + " freeze SHA mismatch")
    expect_frozen_count = len(pinned) + 2
    if len(frozen) != expect_frozen_count:
        problems.append("missing or extraneous FROZEN.sha256 entries")
    if sha(stage / "BLIND.tsv") != sha(inp):
        problems.append("staged input differs from archived input")
    en_ref = (stage / "r59/blind/LM_SHA256").read_text().split()[0]
    de_ref = {ln.split()[1]: ln.split()[0] for ln in
              (stage / "r63/blind/MODELS.sha256").read_text().splitlines() if ln.strip()}
    if en_ref != pinned[("english_lm", "lm6.v2.bin")][0]:
        problems.append("English model registry mismatch")
    for name in ("lm6_de.bin", "de_words.tsv"):
        if de_ref.get(name) != pinned[("key_model", name)][0]:
            problems.append("German model registry mismatch")
    truth_free_files = sorted(str(f.relative_to(stage)) for f in stage.rglob("*") if f.is_file())
    expected_files = sorted([path for _, path in pinned.values()] +
                            ["r59/blind/LM_SHA256", "r63/blind/MODELS.sha256", "BLIND.tsv"])
    if truth_free_files != expected_files:
        problems.append("stage allowlist mismatch")
    work_manifest = {}
    for line in (run / "WORK.sha256").read_text().splitlines():
        h, name = line.split("  ", 1)
        if name in work_manifest:
            problems.append("duplicate work SHA name")
        work_manifest[name] = h
        f = run / "work" / name
        if not f.is_file() or sha(f) != h:
            problems.append("work checksum mismatch " + name)
    on_disk = {f.name for f in (run / "work").iterdir() if f.is_file()}
    if on_disk != set(work_manifest):
        problems.append("missing or extra raw work files")
    cts = dict(l.split("\t") for l in inp.read_text().splitlines()[1:] if l)
    if len(cts) != 216 or any(len(s) != 97 or not s.isascii() or not s.isupper() for s in cts.values()):
        problems.append("216 validated 97-letter ciphertext rows required")
    allrows = [json.loads(l) for l in (run / "RESULTS.jsonl").read_text().splitlines() if l.strip()]
    rows = {r["id"]: r for r in allrows}
    if len(rows) != len(allrows) or set(rows) != set(cts):
        problems.append("missing or duplicate result IDs")
    rr = routes()
    names = list(rr)
    if len(rr) != 10:
        problems.append("unexpected number of routes")
    nwit = 0
    for rid, ct in cts.items():
        f = run / "work" / (rid + ".s1.jsonl")
        if not f.is_file():
            problems.append("missing solver outputs " + rid)
            continue
        raw = [json.loads(line) for line in f.read_text().splitlines() if line.strip()]
        inds = []
        for row in raw:
            try:
                i = int(row["id"].rsplit("__", 1)[1])
                inds.append(i)
                name = names[i]
                for w in [row["best"]] + row["per_convention"] + row["top"]:
                    nwit += 1
                    if len(w["plaintext"]) != 97 or len(w["key"]) != 97:
                        problems.append("incomplete witness " + rid)
                    elif forward(w["plaintext"], w["key"], w["convention"], rr[name]) != ct:
                        problems.append("witness does not reencrypt " + rid + "/" + name)
            except (KeyError, ValueError, IndexError, TypeError) as exc:
                problems.append("malformed witness " + rid + ": " + str(exc))
        if sorted(inds) != list(range(10)):
            problems.append("missing/duplicate routes " + rid)
    control_manifest = json.loads((inp.parent / "MANIFEST.json").read_text())
    if control_manifest.get("blind_sha256") != sha(inp):
        problems.append("control blind manifest mismatch")
    expected_prereg = (ROOT / "r67/PREREGISTRATION.sha256").read_text().split()[0]
    if (control_manifest.get("preregistration_sha256") != expected_prereg
            or sha(ROOT / "r67/PREREGISTRATION.md") != expected_prereg):
        problems.append("R67 preregistration hash mismatch")
    output = {"status": "PASSED" if not problems else "INVALID",
              "controls": len(cts), "witnesses_checked": nwit,
              "problem_count": len(problems), "problems": problems,
              "input_sha256": sha(inp),
              "results_sha256": sha(run / "RESULTS.jsonl"),
              "work_manifest_sha256": sha(run / "WORK.sha256"),
              "freeze_manifest_sha256": sha(run / "FROZEN.sha256"),
              "preregistration_sha256": expected_prereg}
    report.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: v for k, v in output.items() if k != "problems"}, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
