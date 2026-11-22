#!/usr/bin/env python3
"""Compilation, bounded-format IPC and Python-integer aggregation. No clues."""
import hashlib
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

LABELS = 145728
OBSERVATIONS = 24
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABETS = tuple("".join(dict.fromkeys(word + AZ))
                  for word in ("", "KRYPTOS", "PALIMPSEST", "ABSCISSA"))


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    return sha_bytes(Path(path).read_bytes())


def verify_protocol(root, source_commit):
    root = Path(root)
    manifest = root / "r93/PROTOCOL.sha256"
    committed = subprocess.check_output(["git", "show", f"{source_commit}:r93/PROTOCOL.sha256"], cwd=root)
    if manifest.read_bytes() != committed:
        raise ValueError("protocol manifest differs from published source commit")
    receipt = {}
    for line in committed.decode("ascii").splitlines():
        expected, name = line.split(maxsplit=1)
        if name in receipt:
            raise ValueError("duplicate protocol entry")
        at_commit = subprocess.check_output(["git", "show", f"{source_commit}:{name}"], cwd=root)
        if sha_bytes(at_commit) != expected or sha_file(root/name) != expected:
            raise ValueError(f"source mismatch: {name}")
        receipt[name] = expected
    required = {"r93/PREREGISTRATION.md", "r93/MODE_CLARIFICATION.md", "r93/checker93.cpp",
                "r93/reference93.py", "r93/scope93.py", "r93/runner93.py", "r93/validate93.py",
                "r93/run_target93.py", "audit/run_bounded_agg.py", "r73/sealed/reveal_k4.py"}
    if not required <= set(receipt):
        raise ValueError("protocol omits required source")
    return receipt


def build(source, binary):
    flags = ["-O3", "-std=c++17", "-Wall", "-Wextra", "-Werror"]
    subprocess.run(["g++", *flags, str(source), "-o", str(binary)], check=True)
    compiler = subprocess.check_output(["g++", "--version"], text=True).splitlines()[0]
    return {"source_sha256": sha_file(source), "binary_sha256": sha_file(binary),
            "compiler": compiler, "flags": flags, "python_version": sys.version}


def run_records(binary, mode, lines):
    payload = ("\n".join(lines)+"\n").encode("ascii")
    result = subprocess.run([str(binary), mode], input=payload, capture_output=True, check=True)
    assert len(result.stdout) == 4*len(lines), "kernel output count mismatch"
    words = [word for (word,) in struct.iter_unpack("<I", result.stdout)]
    return words, {"records": len(lines), "input_sha256": sha_bytes(payload),
                   "output_sha256": sha_bytes(result.stdout)}


def setting_line(plaintext, ciphertext, positions, ia, oa, n, phase, direction):
    fields = [str(len(ia)), str(len(ciphertext)), str(len(positions)), str(n), str(phase),
              str(direction), ia, oa, ciphertext, "".join(plaintext[i] for i in positions)]
    return " ".join(fields + list(map(str, positions)))


def read_exact(stream, count):
    pieces = []
    while count:
        piece = stream.read(count)
        if not piece:
            raise RuntimeError("incomplete kernel output")
        pieces.append(piece)
        count -= len(piece)
    return b"".join(pieces)


def scan(binary, inputs, positions, observed, synthetic_required_codes=None):
    assert len(positions) == len(observed) == OBSERVATIONS
    assert len(set(positions)) == OBSERVATIONS
    assert 1 <= len(inputs) <= 201
    assert len({rid for rid, _ in inputs}) == len(inputs)
    header = [f"R93SCAN1 {len(inputs)} 97 {OBSERVATIONS}", *ALPHABETS,
              " ".join(map(str, positions)), observed]
    rows = [f"{rid} {ciphertext}" for rid, ciphertext in inputs]
    payload = ("\n".join(header+rows)+"\n").encode("ascii")
    assert len(payload) < 65536
    # A regular temporary input file avoids pipe deadlock when a kernel emits
    # one large result block before consuming later input rows.
    with tempfile.TemporaryFile() as incoming:
        incoming.write(payload)
        incoming.seek(0)
        proc = subprocess.Popen([str(binary), "--scan"], stdin=incoming, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    try:
        reports = {}
        digest = hashlib.sha256()
        mask = (1 << OBSERVATIONS)-1
        for rid, _ in inputs:
            raw = read_exact(proc.stdout, LABELS*4)
            digest.update(raw)
            if synthetic_required_codes is not None:
                index, required = synthetic_required_codes[rid]
                assert 0 <= index < LABELS
                actual = struct.unpack_from("<I", raw, index*4)[0]
                assert actual & required == required, "bulk scan rejects known synthetic setting"
            exact, deletion, pairs, settings = 0, 0, 0, 0
            for (word,) in struct.iter_unpack("<I", raw):
                assert word < (1 << (OBSERVATIONS+1))
                omitted = word & mask
                strict = bool(word >> OBSERVATIONS)
                assert not strict or omitted == mask
                exact += strict
                deletion += bool(omitted)
                pairs += omitted.bit_count()
                settings += 1
            assert settings == LABELS and 0 <= exact <= deletion <= settings
            assert deletion <= pairs <= OBSERVATIONS*deletion
            reports[rid] = {"settings": settings, "exact_feasible_labels": exact,
                            "drop_feasible_labels": deletion,
                            "drop_feasible_label_observation_pairs": pairs}
        assert not proc.stdout.read(1), "extra kernel output"
        error = proc.stderr.read().decode("utf-8", "replace")
        if proc.wait() != 0:
            raise RuntimeError(f"kernel failed: {error}")
        return reports, {"input_sha256": sha_bytes(payload), "bitfield_stream_sha256": digest.hexdigest(),
                         "labels_per_input": LABELS, "input_count": len(inputs),
                         "bitfield_stream_persisted": False, "count_arithmetic": "Python int"}
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
