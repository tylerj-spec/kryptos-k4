#!/usr/bin/env python3
"""R40 copy of the strictblind contract test (R31 request: blind code must not be able to see the clues). Fails if any file under blind/
mentions a clue word, defines clue/mask identifiers, accepts a mask argument, or imports a non-standard module."""
import ast
import re
import sys
from pathlib import Path

BLIND = Path(__file__).resolve().parents[1] / "blind"   # r40/blind
FORBIDDEN_WORDS = ["EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK"]
FORBIDDEN_IDS = ["ANCH", "CLUE", "CRIB", "MASK", "k4common", "key_oracle", "r30lib", "sealed"]
STDLIB = set(sys.stdlib_module_names)
bad = []
for f in sorted(BLIND.iterdir()):
    if not f.is_file():
        continue
    text = f.read_text()
    code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith(("//", "#")))   # comments may explain
    for w in FORBIDDEN_WORDS:
        if w in code.upper():
            bad.append(f"{f.name}: contains clue word {w}")
    if f.suffix == ".py":
        tree = ast.parse(text)
        idents = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                idents.add(node.id)
            elif isinstance(node, ast.Attribute):
                idents.add(node.attr)
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                idents.add(node.name)
            elif isinstance(node, ast.arg):
                idents.add(node.arg)
    else:   # C++/shell: identifiers = code with comments and string literals removed
        idents = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", re.sub(r'"(?:\\.|[^"\\])*"', "", code)))
    for w in FORBIDDEN_IDS:
        hits = sorted(i for i in idents if re.match(rf"{w}", i, re.I))
        if hits:
            bad.append(f"{f.name}: forbidden identifier(s) {hits}")
    if f.suffix == ".py":
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                    [node.module] if isinstance(node, ast.ImportFrom) else []
            for n in names:
                if n.split(".")[0] not in STDLIB:
                    bad.append(f"{f.name}: imports non-standard module {n}")
for f in sorted(BLIND.glob("*.cpp")):   # the CLIs take no mask: argument counts are fixed
    t = f.read_text()
    if not re.search(r"argc != (10|7)\b", t):
        bad.append(f"{f.name}: unexpected CLI")
print("\n".join(bad) if bad else f"CONTRACT OK: {len(list(BLIND.iterdir()))} blind files clean")
sys.exit(1 if bad else 0)
