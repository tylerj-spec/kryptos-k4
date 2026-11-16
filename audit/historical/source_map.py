#!/usr/bin/env python3
"""T5 (audit/NEXT_STEPS.md): source map for the ledger rows that scan.py classes GENERIC_SOURCE or UNRESOLVED_PATH.
Documentation only. For each row, every file name the row itself mentions (*.py, *.md, *.json, *.cpp, ...) is searched
by basename among tracked files and inside R32_handoff_original.zip. Rows that mention no file are searched for a
small fixed list of known legacy tools by family keyword (KNOWN below, each verified by hand). No status is changed.
Usage: python3 -I audit/historical/source_map.py INVENTORY.json OUT.json"""
import json
import re
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILE = re.compile(r"[A-Za-z0-9_./*-]+\.(?:py|md|json|jsonl|cpp|c|sh|txt|tsv|log)\b")
# files related to a row, checked by hand (SOURCE_MAP.md says how each relates; none is the row's original script)
KNOWN = {"L12": ["k4kit/tools/trifid_any.py", "k4kit/results/trifid_any.log"],
         "L25": ["archive/2026-10-26_chatgpt_starter/sources/2026-10-22_world_clock_and_sources.md"],
         "L37": ["archive/2026-10-26_chatgpt_starter/sources/world_clock_360.md"]}


def main():
    inv = json.loads(Path(sys.argv[1]).read_text())
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True,
                             check=True).stdout.split()
    with zipfile.ZipFile(ROOT / "R32_handoff_original.zip") as z:
        tracked += ["R32_handoff_original.zip!" + n for n in z.namelist() if not n.endswith("/")]
    by_base = defaultdict(list)
    for p in tracked:
        by_base[Path(p.split("!")[-1]).name].append(p)
    ledger = {}
    for line in (ROOT / "LEDGER.md").read_text().splitlines():
        m = re.match(r"\| (L\d+) \|", line)
        if m:
            ledger[m.group(1)] = line
    rows = []
    for r in inv["ledger"]["rows"]:
        if not (r["generic"] or r["unresolved_paths"]):
            continue
        text = ledger.get(r["id"], "")
        names = list(dict.fromkeys(FILE.findall(text)))
        found, missing = {}, []
        for n in names:
            base = Path(n).name
            if "*" in base:
                hits = [p for p in tracked if re.fullmatch(base.replace(".", r"\.").replace("*", ".*"),
                                                           Path(p.split("!")[-1]).name)
                        and Path(n).parent.name in p]
            else:
                hits = by_base.get(base, [])
            (found.__setitem__(n, hits[:6]) if hits else missing.append(n))
        known = [k for k in KNOWN.get(r["id"], []) if k in tracked]
        rows.append({"id": r["id"], "status": r["recorded_status"], "source_tag": r["source"],
                     "scan_class": r["provenance"], "method": r["method"], "mentioned_files_found": found,
                     "mentioned_files_not_found": missing, "known_legacy_tools": known})
    Path(sys.argv[2]).write_text(json.dumps({"rows": rows}, indent=1) + "\n")
    print(len(rows), "rows;", sum(1 for x in rows if x["mentioned_files_found"] or x["known_legacy_tools"]),
          "with some file found")


if __name__ == "__main__":
    main()
