#!/usr/bin/env python3
"""Retrieve UNVERIFIED 1923 Carter/Mace Volume I OCR with provenance.

Requires external internet access. It saves original bytes without modifying text.
OCR is noisy and requires scan-page verification before being used as an exact running key.
"""
import hashlib, json, pathlib, time, urllib.request
URLS = (
  "https://archive.org/download/in.gov.ignca.17094/17094_djvu.txt",
  "https://archive.org/stream/in.gov.ignca.17094/17094_djvu.txt",
)

def main():
    dst = pathlib.Path(__file__).resolve().parent / "carter_1923_download"
    dst.mkdir(exist_ok=True)
    errors = []
    for url in URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "K4-source-research/1.0"})
            with urllib.request.urlopen(req, timeout=40) as res:
                data = res.read()
            txt = data.decode("utf-8",errors="replace")
            if "<html" in txt[:3000].lower() or "<!doctype html" in txt[:3000].lower():
                raise ValueError("Retrieved web HTML, not the raw OCR text file")
            if len(data) < 70000 or "CARTER" not in txt.upper() or "TOMB" not in txt.upper():
                raise ValueError("Retrieved text fails minimal size/title checks: "+str(len(data)))
            outfile=dst/"carter_mace_v1_1923_UNVERIFIED_OCR.txt"
            outfile.write_bytes(data)
            meta={"status":"RAW_UNVERIFIED_OCR", "url":url,
                  "bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),
                  "downloaded_utc_epoch":int(time.time()),
                  "warning":"OCR is not a faithful letter-by-letter transcription. Validate against 1923 scan before key search."}
            (dst/"source_provenance.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
            print("Downloaded raw UNVERIFIED OCR:",outfile,"bytes:",len(data))
            return
        except Exception as exc:
            errors.append(f"{url}: {exc!r}")
    raise RuntimeError("Could not retrieve full OCR. "+"; ".join(errors))

if __name__ == "__main__": main()
