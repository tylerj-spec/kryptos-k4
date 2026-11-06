#!/usr/bin/env python3
"""Build an allowlisted, read-only R67 blind runner root outside the repository.

Usage: python3 r67/sealed/stage_blind.py CONTROL_DIR STAGE_DIR EN_LM MODEL_DIR R63_SOLVER

This does NOT run a solver, open synthetic truth or K4 plaintext, or make a K4
candidate. Only CONTROL_DIR/BLIND.tsv is copied from the control directory.
Run the staged payload in a network-disabled, read-only, unprivileged container;
mount ONLY the staged tree read-only and a separate empty output directory.
"""
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIN = ROOT / "r67/REFERENCE_SHA256"
SHA_EN_REG = ROOT / "r59/blind/LM_SHA256"
SHA_DE_REG = ROOT / "r63/blind/MODELS.sha256"

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def pins():
    entries = []
    for line in PIN.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        h, role, rel = line.split("  ", 2)
        if len(h) != 64 or not all(x in "0123456789abcdef" for x in h):
            raise ValueError("invalid R67 dependency hash")
        entries.append((h, role, rel))
    if len(entries) != 10 or len(set(rel for _, _, rel in entries)) != 10:
        raise ValueError("expected ten unique pinned R65 dependencies")
    return entries

def copy_checked(source, destination, expected, execute=False):
    if not source.is_file() or source.is_symlink():
        raise ValueError("missing or unsafe dependency: " + str(source))
    if digest(source) != expected:
        raise ValueError("dependency digest mismatch: " + str(source))
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    destination.chmod(0o555 if execute else 0o444)
    if digest(destination) != expected:
        raise ValueError("staging copy digest mismatch")

def main():
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    ctrl, dest, en_lm, model_dir, solver = map(Path, sys.argv[1:])
    dest = dest.absolute()
    if dest.exists():
        raise SystemExit("refusing to overwrite stage directory")
    if dest.resolve().is_relative_to(ROOT.resolve()):
        raise SystemExit("stage directory must be outside full repository")
    if ctrl.resolve().is_relative_to(dest.resolve()):
        raise SystemExit("staging destination must not contain control directory")
    manifest = json.loads((ctrl / "MANIFEST.json").read_text())
    blind = ctrl / "BLIND.tsv"
    if digest(blind) != manifest["blind_sha256"]:
        raise SystemExit("control ciphertext file changed")
    rows = blind.read_text().splitlines()
    if len(rows) != 217 or rows[0] != "id\tciphertext":
        raise SystemExit("expected 216 blind ciphertext controls")
    seen = set()
    for row in rows[1:]:
        rid, ct = row.split("\t")
        if rid in seen or not rid.startswith("CTRL_") or len(ct) != 97 or not ct.isascii() or not ct.isupper() or not ct.isalpha():
            raise SystemExit("bad/duplicate blind control row")
        seen.add(rid)
    sources = {
        "r63/blind/rk2_solve.cpp": ROOT / "r63/blind/rk2_solve.cpp",
        "solver/rk2_solve": solver,
        "models/lm6.v2.bin": en_lm,
        "k4kit/data/word_model_orth.tsv": ROOT / "k4kit/data/word_model_orth.tsv",
        "r61/routes.txt": ROOT / "r61/routes.txt",
        "models/lm6_de.bin": model_dir / "lm6_de.bin",
        "models/de_words.tsv": model_dir / "de_words.tsv",
        "r65/blind/run.py": ROOT / "r65/blind/run.py",
        "r64/blind/run.py": ROOT / "r64/blind/run.py",
        "r65/PREREGISTRATION.md": ROOT / "r65/PREREGISTRATION.md",
    }
    expected = {rel: h for h, _, rel in pins()}
    en_registry = SHA_EN_REG.read_text().split()[0]
    de_registry = {ln.split()[1]: ln.split()[0] for ln in SHA_DE_REG.read_text().splitlines() if ln.strip()}
    if expected["models/lm6.v2.bin"] != en_registry:
        raise SystemExit("English model registry mismatch")
    for filename in ("lm6_de.bin", "de_words.tsv"):
        if expected["models/" + filename] != de_registry[filename]:
            raise SystemExit("German model registry mismatch")
    dest.mkdir(parents=True)
    for rel, src in sources.items():
        copy_checked(src, dest / rel, expected[rel], execute=(rel == "solver/rk2_solve"))
    # Keep canonical registries at the exact repository-relative paths.
    for path, source in (("r59/blind/LM_SHA256", SHA_EN_REG),
                         ("r63/blind/MODELS.sha256", SHA_DE_REG)):
        out = dest / path
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, out)
        out.chmod(0o444)
    out = dest / "BLIND.tsv"
    shutil.copyfile(blind, out)
    out.chmod(0o444)
    # No truth, clues, full repo, r67 evaluator or candidate-history enters the stage.
    entries = sorted(str(f.relative_to(dest)) for f in dest.rglob("*") if f.is_file())
    allowed = set(sources) | {"r59/blind/LM_SHA256", "r63/blind/MODELS.sha256", "BLIND.tsv"}
    if set(entries) != allowed or len(entries) != 13:
        raise RuntimeError("staging allowlist violation")
    for folder in sorted((p for p in dest.rglob("*") if p.is_dir()), reverse=True):
        folder.chmod(0o555)
    dest.chmod(0o555)
    print("Isolated stage created:", dest, "files", len(entries))
    print("Mount this tree :ro, OUTDIR separately :rw; network none; read-only rootfs; nonroot user.")
    print("python3 -I /safe/r65/blind/run.py /safe/BLIND.tsv /out /safe/models/lm6.v2.bin /safe/models /safe/solver/rk2_solve 4")
    print("Staged BLIND sha256:", digest(dest / "BLIND.tsv"))

if __name__ == "__main__":
    main()
