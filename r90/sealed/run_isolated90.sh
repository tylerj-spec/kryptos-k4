#!/bin/sh
# R90: run the blind runner inside BOX only (see r90/sealed/make_sandbox90.py; r87-r89 pattern).
# New mount + network namespace: /workspace, /tmp/claude-0 and /root are replaced by empty tmpfs, BOX is bind-mounted
# at /mnt/box, and there is no network. Usage: run_isolated90.sh BOX OUTNAME PROCS
set -eu
BOX=$(readlink -f "$1"); OUT=$2; PROCS=$3
mkdir -p /mnt/box
exec unshare -m -n sh -c "
  mount --make-rprivate / &&
  mount --bind '$BOX' /mnt/box &&
  mount -t tmpfs none /workspace && mount -t tmpfs none /tmp/claude-0 && mount -t tmpfs none /root &&
  test -z \"\$(ls -A /workspace)\" && test -z \"\$(ls -A /tmp/claude-0)\" &&
  cd /mnt/box && exec python3 -I /mnt/box/r90/blind/run90.py /mnt/box/lm/lm6.v2.bin /mnt/box/input/TARGET.tsv /mnt/box/out/$OUT $PROCS"
