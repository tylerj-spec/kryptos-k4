#!/usr/bin/env python3
"""R53 contract tests for source, inbound payload and sealed separation.

Source inspection is not a formal security proof; the Docker mount separation,
no-network, and frozen-commit-before-evaluation workflow enforce the boundary.
"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLIND = ROOT / "r53" / "blind"
PROGRAM = BLIND / "solve.py"
src = PROGRAM.read_text()
up = src.upper()
BANNED_TOKENS = (
    "EASTNORTHEAST", "BERLINCLOCK", "NORTHEAST", "K4COMMON",
    "KEY_ORACLE", "SEALED/", "R52/", "FITTED_PLAINTEXT",
)
for t in BANNED_TOKENS:
    assert t not in up, f"blind code contains forbidden source {t}"
tree = ast.parse(src)
imports = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imports.update(x.name.split(".")[0] for x in node.names)
    elif isinstance(node, ast.ImportFrom):
        raise AssertionError("relative or from-import forbidden in source-firewall demo")
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            assert node.func.id not in {"open", "eval", "exec", "__import__"}
assert imports <= {"sys", "json", "math", "hashlib"}, imports

# The source must reject "helpful" plaintext/key/crib metadata outright.
ct = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 3 + "ABCDEFGHIJKLMNOPQRS"
assert len(ct) == 97
good = {"id": "CONTROL", "ciphertext": ct}


def run(payload):
    return subprocess.run(
        [sys.executable, "-I", str(PROGRAM)],
        input=json.dumps(payload) + "\n",
        capture_output=True, text=True, timeout=6,
        cwd=str(BLIND)
    )


run_good = run(good)
assert run_good.returncode == 0, run_good.stderr
result = json.loads(run_good.stdout)
assert result["id"] == "CONTROL"
assert len(result["candidates"]) == 26
assert all(len(x["plaintext"]) == 97 for x in result["candidates"])
assert result["ciphertext_sha256"] == hashlib.sha256(ct.encode()).hexdigest()

for field, value in (
    ("plaintext", "A" * 97),
    ("key", 0),
    ("mask", "?" * 97),
    ("crib", "DO_NOT_TRUST"),
    ("positions", [1, 2, 3]),
    ("letter_hints", "CANARY"),
    ("correctness", 0.99),
):
    bad = dict(good)
    bad[field] = value
    p = run(bad)
    assert p.returncode != 0, f"accepted extra solver field: {field}"
for bad_ct in ("A"*96, "A"*98, "A"*96+"?", "a"*97):
    p = run({"id": "CONTROL", "ciphertext": bad_ct})
    assert p.returncode != 0, "accepted invalid ciphertext"

print("R53 CONTRACT PASS: blind source independent of K4 facts; extra key/plaintext/position fields rejected")
