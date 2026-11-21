#!/usr/bin/env python3
"""Run one experiment job under AGGREGATE resource limits (the semantics ChatGPT's R89 review asked for before the
next experiment: r89/audit/REVIEW_20261121.md, correction E). audit/run_bounded.py is pinned by earlier rounds and is
left unchanged; this wrapper is its successor for new rounds.

Semantics (all from the round's QA_MANIFEST.json resource_budget):
  max_wall_seconds   wall clock of the whole job;
  max_ram_mb         AGGREGATE resident memory of every process in the job's process group (sampled), and also the
                     per-process address-space limit (RLIMIT_AS), so no single process can exceed it either;
  max_cpu_seconds    AGGREGATE CPU time (user + system) of the process group; optional, default
                     max_wall_seconds x the machine's CPU count.
The job runs in a new session (its own process group). Every SAMPLE seconds the wrapper sums VmRSS and CPU time over
all live members of the group (/proc), plus the CPU of members already reaped; if any aggregate exceeds its budget the
whole group is killed and the job is INCOMPLETE. Sampling can miss a spike shorter than one interval (the per-process
RLIMIT_AS still applies). A killed, timed-out or non-zero job is INCOMPLETE, never a result.
The log keeps the fields audit/check_guardrails.py reads (status, wall_seconds, max_rss_mb), with max_rss_mb = the
AGGREGATE sampled peak, and adds cpu_seconds, aggregate_peak_rss_mb, per_process_peak_rss_mb and the semantics.
Usage: python3 -I audit/run_bounded_agg.py --manifest rNN/QA_MANIFEST.json --log LOG.json -- COMMAND..."""
import argparse
import json
import os
import resource
import signal
import subprocess
import sys
import time

SAMPLE = 0.25
PAGE = os.sysconf("SC_PAGE_SIZE")
TICK = os.sysconf("SC_CLK_TCK")


def group_usage(pgid):
    """(resident MB, cpu seconds incl. reaped children of live members) over live members of the process group."""
    rss = cpu = 0.0
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/stat") as f:
                st = f.read()
            fields = st[st.rindex(")") + 2:].split()
            if int(fields[2]) != pgid:          # field 5 (pgrp) after state and ppid
                continue
            cpu += sum(int(x) for x in fields[11:15]) / TICK   # utime, stime, cutime, cstime
            with open(f"/proc/{d}/statm") as f:
                rss += int(f.read().split()[1]) * PAGE / 2 ** 20
        except (FileNotFoundError, ProcessLookupError, ValueError, IndexError):
            continue
    return rss, cpu


def run(command, wall, ram_mb, cpu_s):
    limit = ram_mb * 1024 * 1024

    def child_setup():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    proc = subprocess.Popen(command, preexec_fn=child_setup)
    pgid, reason, peak, peak_cpu, samples = proc.pid, None, 0.0, 0.0, 0
    while True:
        code = proc.poll()
        if code is not None:
            break
        rss, cpu = group_usage(pgid)
        samples += 1
        peak, peak_cpu = max(peak, rss), max(peak_cpu, cpu)
        if time.monotonic() - start > wall:
            reason = "wall-clock budget exceeded"
        elif rss > ram_mb:
            reason = f"aggregate memory budget exceeded ({rss:.1f} MB > {ram_mb} MB)"
        elif cpu > cpu_s:
            reason = f"aggregate CPU budget exceeded ({cpu:.1f} s > {cpu_s} s)"
        if reason:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            code = proc.wait()
            break
        time.sleep(SAMPLE)
    try:                                       # reap any stragglers left in the group
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    wall_s = time.monotonic() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_total = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    if reason is None and code != 0:
        reason = f"killed by signal {-code}" if code < 0 else f"exit code {code}"
    if reason is None and cpu_total > cpu_s:
        reason = f"aggregate CPU budget exceeded ({cpu_total:.1f} s > {cpu_s} s)"
    return {
        "status": "COMPLETE" if reason is None else "INCOMPLETE",
        "reason": reason,
        "exit_code": code,
        "wall_seconds": round(wall_s, 3),
        "max_rss_mb": round(peak, 1),
        "aggregate_peak_rss_mb": round(peak, 1),
        "per_process_peak_rss_mb": round(max(after.ru_maxrss, before.ru_maxrss) / 1024, 1),
        "cpu_seconds": round(max(cpu_total, peak_cpu), 3),
        "samples": samples,
        "sample_interval_s": SAMPLE,
        "budget": {"max_wall_seconds": wall, "max_ram_mb": ram_mb, "max_cpu_seconds": cpu_s},
        "semantics": "aggregate over the job's process group: sampled resident memory and CPU time; "
                     "per-process RLIMIT_AS = max_ram_mb; wall clock of the whole job",
        "wrapper": "audit/run_bounded_agg.py",
        "command": command,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("command", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not cmd:
        ap.error("no command")
    b = json.load(open(a.manifest))["resource_budget"]
    cpu_s = int(b.get("max_cpu_seconds") or b["max_wall_seconds"] * (os.cpu_count() or 1))
    rep = run(cmd, int(b["max_wall_seconds"]), int(b["max_ram_mb"]), cpu_s)
    with open(a.log, "w") as f:
        f.write(json.dumps(rep, indent=2) + "\n")
    print(f"{rep['status']}: {rep['wall_seconds']} s wall, {rep['cpu_seconds']} s CPU, aggregate peak "
          f"{rep['aggregate_peak_rss_mb']} MB" + (f" ({rep['reason']})" if rep["reason"] else ""), file=sys.stderr)
    sys.exit(0 if rep["status"] == "COMPLETE" else 1)


if __name__ == "__main__":
    main()
