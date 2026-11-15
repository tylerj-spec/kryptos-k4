#!/usr/bin/env python3
"""Run one experiment job under the hard limits in a round's QA manifest.

Every job that reads the K4 ciphertext must be started through this
wrapper. It enforces the preregistered wall-clock and memory budget,
kills the whole process group when either is exceeded, and writes a
resource log. A job that is killed, times out or exits non-zero is
recorded as INCOMPLETE. INCOMPLETE is never a cryptographic result.

Usage:
  python3 -I audit/run_bounded.py --manifest rNN/QA_MANIFEST.json \
      --log rNN/k4/run/RESOURCE_LOG.json -- python3 rNN/blind/solve.py ...
"""
import argparse
import json
import os
import resource
import signal
import subprocess
import sys
import time


def run(command, max_wall_seconds, max_ram_mb):
    limit = max_ram_mb * 1024 * 1024

    def child_setup():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    start = time.monotonic()
    proc = subprocess.Popen(command, preexec_fn=child_setup)
    reason = None
    try:
        code = proc.wait(timeout=max_wall_seconds)
    except subprocess.TimeoutExpired:
        reason = "wall-clock budget exceeded"
        os.killpg(proc.pid, signal.SIGKILL)
        code = proc.wait()
    wall = time.monotonic() - start
    peak_kb = max(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss, before)
    if reason is None and code != 0:
        reason = (f"killed by signal {-code}" if code < 0
                  else f"exit code {code} (a MemoryError here means the "
                       "memory budget was reached)")
    return {
        "status": "COMPLETE" if reason is None else "INCOMPLETE",
        "reason": reason,
        "exit_code": code,
        "wall_seconds": round(wall, 3),
        "max_rss_mb": round(peak_kb / 1024, 1),
        "budget": {"max_wall_seconds": max_wall_seconds, "max_ram_mb": max_ram_mb},
        "command": command,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("give the job command after --")
    with open(args.manifest, encoding="utf-8") as f:
        budget = json.load(f)["resource_budget"]
    log = run(command, budget["max_wall_seconds"], budget["max_ram_mb"])
    with open(args.log, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
        f.write("\n")
    print(f"{log['status']}: {log['wall_seconds']} s, {log['max_rss_mb']} MB"
          + (f" ({log['reason']})" if log["reason"] else ""), file=sys.stderr)
    return 0 if log["status"] == "COMPLETE" else 3


if __name__ == "__main__":
    sys.exit(main())
