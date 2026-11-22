import concurrent.futures
import hashlib
import importlib.util
import json
import sys
import urllib.request
from pathlib import Path

repo = Path(sys.argv[1])
dest = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("original_r59_corpus", repo / "r59/corpus/build_corpus.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
jobs = []
for name, filename, expected, role in mod.BOOKS:
    if role == "train":
        jobs.append(("raw/" + name + ".txt", mod.BASE.format(repo=name, file=filename), expected))
for name, expected in mod.NLTK.items():
    jobs.append(("nltk/" + name + ".zip", mod.NLTK_URL.format(name=name), expected))


def job(row):
    name, url, expected = row
    p = dest / name
    try:
        body = urllib.request.urlopen(url, timeout=45).read()
        actual = hashlib.sha256(body).hexdigest()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body)
        return {"path": name, "url": url, "bytes": len(body), "sha256": actual,
                "expected": expected, "verified": actual == expected}
    except Exception as exc:
        return {"path": name, "url": url, "expected": expected, "verified": False,
                "error": type(exc).__name__ + ": " + str(exc)}


with concurrent.futures.ThreadPoolExecutor(4) as ex:
    results = list(ex.map(job, jobs))
report = {"attempt": "current pinned source URLs, one attempt each", "results": results,
          "all_verified": all(r["verified"] for r in results)}
(dest / "ACQUISITION.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"verified": sum(r["verified"] for r in results), "total": len(results),
                  "failures": [r for r in results if not r["verified"]]}, indent=2), flush=True)
sys.exit(0 if report["all_verified"] else 2)
