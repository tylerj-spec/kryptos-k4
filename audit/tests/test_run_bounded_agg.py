#!/usr/bin/env python3
"""Tests for audit/run_bounded_agg.py: aggregate memory over several processes, aggregate CPU, wall clock, exit code.
Usage: python3 -I audit/tests/test_run_bounded_agg.py"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W = ROOT / "audit/run_bounded_agg.py"
HOLD = ("import time,sys\nb=bytearray(int(sys.argv[1])*2**20)\nfor i in range(0,len(b),4096): b[i]=1\n"
        "time.sleep(float(sys.argv[2]))\n")
FORK = ("import subprocess,sys\nps=[subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2],sys.argv[3]])"
        " for _ in range(int(sys.argv[4]))]\nsys.exit(max(p.wait() for p in ps))\n")
BUSY = "import time\nt=time.time()\nwhile time.time()-t<float(__import__('sys').argv[1]): pass\n"


def job(budget, cmd):
    with tempfile.TemporaryDirectory() as d:
        m, log = Path(d) / "m.json", Path(d) / "log.json"
        m.write_text(json.dumps({"resource_budget": budget}))
        subprocess.run([sys.executable, "-I", str(W), "--manifest", str(m), "--log", str(log), "--"] + cmd,
                       capture_output=True)
        return json.loads(log.read_text())


def main():
    three = [sys.executable, "-c", FORK, HOLD, "150", "2.0", "3"]       # three processes x 150 MB
    r = job({"max_wall_seconds": 60, "max_ram_mb": 2000}, three)
    assert r["status"] == "COMPLETE" and r["aggregate_peak_rss_mb"] >= 400, r
    r = job({"max_wall_seconds": 60, "max_ram_mb": 300}, three)          # each fits, the sum does not
    assert r["status"] == "INCOMPLETE" and "aggregate memory" in r["reason"], r
    r = job({"max_wall_seconds": 60, "max_ram_mb": 2000, "max_cpu_seconds": 2},
            [sys.executable, "-c", FORK, BUSY, "4", "", "2"])            # 2 processes x 4 s busy
    assert r["status"] == "INCOMPLETE" and "CPU" in r["reason"], r
    r = job({"max_wall_seconds": 2, "max_ram_mb": 2000}, [sys.executable, "-c", "import time; time.sleep(30)"])
    assert r["status"] == "INCOMPLETE" and "wall" in r["reason"] and r["wall_seconds"] < 10, r
    r = job({"max_wall_seconds": 60, "max_ram_mb": 2000}, [sys.executable, "-c", "import sys; sys.exit(3)"])
    assert r["status"] == "INCOMPLETE" and r["exit_code"] == 3, r
    print("run_bounded_agg tests OK: aggregate memory (3 x 150 MB vs 300 MB), aggregate CPU, wall, exit code")


if __name__ == "__main__":
    main()
