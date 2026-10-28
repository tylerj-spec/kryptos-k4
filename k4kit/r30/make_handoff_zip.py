#!/usr/bin/env python3
"""Build the small R30 handoff zip for Tyler/ChatGPT: brief, ledger, R30 code, protocols, logs, shortlist and a
compact per-family summary (the large ranked JSONs stay in the repo). Writes k4kit/handoffs/R30_handoff.zip."""
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
REPO = KIT.parent
OUT = KIT / "handoffs" / "R30_handoff.zip"

summ = {}
for f in sorted((HERE / "runs").glob("*.json")):
    d = json.load(open(f))
    if "ranked" in d:
        summ[f.stem] = {"summary": d["summary"], "top20": [{k: x[k] for k in ("id", "W", "plaintext", "forced_mask",
                                                                              "forced_beyond_clues")}
                                                           for x in d["ranked"][:20]],
                        "replication": d.get("replication", {})}
    else:
        summ[f.stem] = d
(HERE / "runs" / "R30_SUMMARIES.json").write_text(json.dumps(summ, indent=1) + "\n")

files = [KIT / "handoffs" / "R30_claude_code.md", KIT / "LEDGER.md", KIT / "CLAUDE.md",
         REPO / "archive" / "sources" / "README.md", REPO / "archive" / "sources" / "carter_mace_1923_v1_doran_google_ocr.txt"]
files += sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix in (".py", ".md", ".json", ".csv", ".sha256"))
files += sorted((HERE / "runs").glob("*.log")) + [HERE / "runs" / "R30_SUMMARIES.json", HERE / "runs" / "e1_passes.csv",
                                                  HERE / "runs" / "lang_models.json", HERE / "runs" / "chain.sh",
                                                  HERE / "runs" / "chain2.sh"]
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, p.relative_to(REPO))
print(OUT, OUT.stat().st_size, "bytes,", len(files), "files")
