#!/usr/bin/env python3
"""Build k4kit/handoffs/R32_handoff.zip: brief, ledger, R32 code, protocol, frozen outputs, reveal, logs."""
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT, REPO = HERE.parent, HERE.parents[1]
OUT = KIT / "handoffs" / "R32_handoff.zip"
files = [KIT / "handoffs" / "R32_claude_code.md", KIT / "LEDGER.md", KIT / "CLAUDE.md"]
files += [p for p in sorted(HERE.rglob("*")) if p.is_file() and "runs" not in p.parts and p.suffix in (".md", ".py", ".cpp", ".sh", ".sha256", ".json")]
files += [p for p in sorted((HERE / "runs").iterdir()) if p.suffix in (".tsv", ".json", ".sha256", ".log") or p.name.endswith("_ct.txt")
          or p.name in ("routes_f1.txt", "k4_ciphertext.txt")]
files = [p for p in files if not p.name.startswith(("part_", "idcheck_"))]
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, p.relative_to(REPO))
print(OUT, OUT.stat().st_size, "bytes,", len(files), "files")
