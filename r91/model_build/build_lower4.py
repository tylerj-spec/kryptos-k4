import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1])
base = Path(__file__).resolve().parent
acq = json.loads((base / "ACQUISITION.json").read_text())
assert acq["all_verified"]
for item in acq["results"]:
    assert hashlib.sha256((base / item["path"]).read_bytes()).hexdigest() == item["expected"]
spec = importlib.util.spec_from_file_location("r59_original_builder", repo / "r59/corpus/build_corpus.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.BOOKS = [b for b in mod.BOOKS if b[3] == "train"]
mod.CARTER = base / "carter_az.txt"
sys.argv = ["build_corpus.py", "build", str(base / "raw"), str(base / "corpus"), str(base / "nltk")]
mod.main()
subprocess.run(["g++", "-O3", "-std=c++17", str(repo / "r59/blind/lm_build.cpp"),
                "-o", str(base / "lm_build")], check=True)
subprocess.run([str(base / "lm_build"), str(base / "corpus/train.txt"), str(base / "lm5.bin"), "5"], check=True)
blob = (base / "lm5.bin").read_bytes()
assert blob[:6] == b"R59LM\x05"
lower = b"R59LM\x04\x00\x00" + blob[8:8 + 4 * sum(26 ** k for k in range(1, 5))]
(base / "R59_LOWER4_FROM_K5.bin").write_bytes(lower)
receipt = {
    "description": "Exact lower-order1-4 tables of the archived R59 K=6 construction: K=5 yields the same continuation counts for orders below5; only the unneeded top order differs.",
    "source_commit": "bef9e7d7bcbecc1ca870fa46f0dd78d8a0805d77",
    "acquisition_sha256": hashlib.sha256((base / "ACQUISITION.json").read_bytes()).hexdigest(),
    "corpus_builder_sha256": hashlib.sha256((repo / "r59/corpus/build_corpus.py").read_bytes()).hexdigest(),
    "model_builder_sha256": hashlib.sha256((repo / "r59/blind/lm_build.cpp").read_bytes()).hexdigest(),
    "carter_sha256": hashlib.sha256(mod.CARTER.read_bytes()).hexdigest(),
    "training_letters_sha256": hashlib.sha256((base / "corpus/train.txt").read_bytes()).hexdigest(),
    "training_bytes": (base / "corpus/train.txt").stat().st_size,
    "model_bytes": len(lower),
    "model_sha256": hashlib.sha256(lower).hexdigest(),
    "compiler": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
    "all_19_external_raw_digests_match": True,
    "full_order6_model_not_rebuilt": True,
}
(base / "BUILD_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2), flush=True)
