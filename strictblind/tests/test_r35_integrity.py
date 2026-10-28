#!/usr/bin/env python3
"""R35 targeted regression tests: key normalization, independent routes, freeze behavior."""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SB = ROOT / "strictblind"
spec = importlib.util.spec_from_file_location("routes", SB / "blind/routes.py")
routes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routes)

with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    path = temp / "mixed_routes.txt"
    subprocess.run([sys.executable, "-I", str(SB / "blind/routes.py"),
                    "rot-mixed", "4", "5", str(path)], check=True, capture_output=True)
    lines = path.read_text().splitlines()
    assert len(lines) == 2 * 2 * 2 * 2 * 2, len(lines)
    for line in lines:
        name, order, indices = line.split()
        perm = [int(v) for v in indices.split(",")]
        assert order in ("S_then_T", "T_then_S")
        assert len(perm) == 97 and sorted(perm) == list(range(97))
        assert perm == routes.mixed_rotation(name)
    assert routes.mixed_rotation("R4x5/CW-CCW/fwd") != routes.rotation("R4x5/CW/fwd")
    assert routes.mixed_rotation("R4x5/CW-CCW/inv") == routes.inv(routes.mixed_rotation("R4x5/CW-CCW/fwd"))
    (temp / "ct.txt").write_text("aBc" * 32 + "z\n")
    (temp / "keys.txt").write_text("aBc" * 33)
    source = (SB / "blind/scan.cpp").read_text()
    assert "if (c >= 'a' && c <= 'z')" in source
    assert "if (c >= 'a' && c <= 'z')" in (SB / "sealed/whole_family.cpp").read_text()
    manifest = temp / "manifest.json"
    manifest.write_text('{"runs":[]}')
    (temp / "FROZEN.sha256").write_text("existing freeze")
    p = subprocess.run([sys.executable, "-I", str(SB / "blind/experiment.py"), str(temp)],
                       capture_output=True, text=True)
    assert p.returncode != 0 and "already frozen" in (p.stdout + p.stderr)
print("R35 INTEGRITY OK")
