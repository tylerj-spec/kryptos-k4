#!/bin/sh
# R89: run the joint blind runner inside BOX only (see r89/sealed/make_sandbox89.py; r87/r88 pattern).
# New mount + network namespace: /workspace, /tmp/claude-0 and /root are replaced by empty tmpfs, BOX is bind-mounted
# at /mnt/box, and there is no network. The annealing kernel is compiled inside the box (r89/.build), once.
# Usage: run_isolated89.sh BOX OUTNAME ARMS PROCS
set -eu
BOX=$(readlink -f "$1"); OUT=$2; ARMS=$3; PROCS=$4
mkdir -p /mnt/box
exec unshare -m -n sh -c "
  mount --make-rprivate / &&
  mount --bind '$BOX' /mnt/box &&
  mount -t tmpfs none /workspace && mount -t tmpfs none /tmp/claude-0 && mount -t tmpfs none /root &&
  test -z \"\$(ls -A /workspace)\" && test -z \"\$(ls -A /tmp/claude-0)\" &&
  cd /mnt/box && exec python3 -I /mnt/box/r89/blind/run89.py /mnt/box/lm/lm6.v2.bin /mnt/box/input/TARGET.tsv /mnt/box/out/$OUT $ARMS $PROCS"
