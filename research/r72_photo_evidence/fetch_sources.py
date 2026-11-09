#!/usr/bin/env python3
"""Fetch licensed public-image references when this machine has access.

No OCR, image manipulation, K4 plaintext analysis, or GitHub mutations.
Run at repository root:
  python3 research/r72_photo_evidence/fetch_sources.py --priority
  python3 research/r72_photo_evidence/fetch_sources.py --all
  python3 research/r72_photo_evidence/fetch_sources.py --ids nova-17 panel-14x31
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "image_manifest.json"

def detect_image(data):
    if data[:3] == bytes.fromhex("ffd8ff"):
        return "jpg"
    if data[:8] == bytes.fromhex("89504e470d0a1a0a"):
        return "png"
    raise ValueError("Not a JPEG/PNG file (may be an HTML error or blocked response)")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--priority", action="store_true")
    g.add_argument("--all", action="store_true")
    g.add_argument("--ids", nargs="+")
    p.add_argument("--output", type=Path, default=HERE / "originals")
    args = p.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = data["images"]
    if args.all:
        selection = items
    elif args.priority:
        selection = [x for x in items if x["priority"] == "high"]
    else:
        ids = set(args.ids)
        selection = [x for x in items if x["id"] in ids]
        missing = ids - {x["id"] for x in selection}
        if missing:
            p.error("Unknown image IDs: " + ", ".join(sorted(missing)))
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    for item in selection:
        row = {"id": item["id"], "url": item["source_url"], "saved": False}
        try:
            req = Request(item["source_url"], headers={"User-Agent": "Kryptos-R72-photo-research/1.0"})
            with urlopen(req, timeout=25) as f:
                raw = f.read(30 * 1024 * 1024 + 1)
            if len(raw) > 30 * 1024 * 1024:
                raise ValueError("File exceeds 30 MiB limit")
            ext = detect_image(raw)
            filepath = args.output / (item["id"] + "." + ext)
            filepath.write_bytes(raw)
            row.update({
                "saved": True, "path": str(filepath), "bytes": len(raw),
                "format": ext, "sha256": hashlib.sha256(raw).hexdigest()
            })
        except Exception as exc:
            row["error"] = type(exc).__name__ + ": " + str(exc)[:240]
        results.append(row)
        print(item["id"], "OK" if row["saved"] else "FAILED", row.get("error", ""))
    dest = args.output / "fetch_manifest.json"
    dest.write_text(json.dumps({"version": 1, "results": results}, indent=2) + "\n", encoding="utf-8")
    print("Saved", sum(x["saved"] for x in results), "of", len(results))
    return 0 if all(x["saved"] for x in results) else 1

if __name__ == "__main__":
    sys.exit(main())
