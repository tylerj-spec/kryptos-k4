#!/usr/bin/env bash
# R67 isolated blind run WITHOUT Docker (no Docker daemon in the operator container). Same properties the
# pre-registration asks of the container:
#   * network disabled: a fresh, empty network namespace (unshare --net);
#   * nonroot: uid/gid 65534 (setpriv), no supplementary groups, no_new_privs;
#   * read-only root filesystem: a tmpfs root remounted read-only, holding only /usr (bind, read-only),
#     /safe = the staged allowlisted tree (bind, read-only), /out = the empty output directory (bind, writable),
#     /tmp (tmpfs, noexec), /proc, /dev/null. Nothing else from the host (no repository, no sealed truth) exists inside.
# Usage (as root on the operator host): sandbox_run.sh STAGE_DIR OUT_DIR EMPTY_ROOT_DIR [COMMAND ...]
#   default COMMAND = the unchanged R65 runner on /safe/BLIND.tsv with 4 processes.
set -euo pipefail
STAGE=$(realpath "$1"); OUT=$(realpath "$2"); ROOTFS=$(realpath "$3"); shift 3
PY=$(realpath /usr/bin/python3)   # resolve alternatives symlinks on the host: /etc does not exist inside
if [ $# -eq 0 ]; then
  set -- "$PY" -I /safe/r65/blind/run.py /safe/BLIND.tsv /out /safe/models/lm6.v2.bin /safe/models \
         /safe/solver/rk2_solve 4
fi
exec unshare --mount --net --pid --ipc --uts --fork --propagation private /usr/bin/bash -c '
set -euo pipefail
STAGE="$1"; OUT="$2"; R="$3"; shift 3
mount -t tmpfs -o mode=755 tmpfs "$R"
mkdir -p "$R/usr" "$R/safe" "$R/out" "$R/tmp" "$R/proc" "$R/dev"
ln -s usr/bin "$R/bin"; ln -s usr/lib "$R/lib"; ln -s usr/lib64 "$R/lib64"; ln -s usr/sbin "$R/sbin"
mount --rbind /usr "$R/usr";   mount -o remount,bind,ro "$R/usr"
mount --bind "$STAGE" "$R/safe"; mount -o remount,bind,ro "$R/safe"
mount --bind "$OUT" "$R/out"
mount -t tmpfs -o nosuid,nodev,noexec,mode=1777 tmpfs "$R/tmp"
mount -t proc -o nosuid,nodev,noexec proc "$R/proc"
touch "$R/dev/null"; mount --bind /dev/null "$R/dev/null"
mount -o remount,ro "$R"
exec chroot "$R" /usr/bin/setpriv --reuid 65534 --regid 65534 --clear-groups --no-new-privs \
     /usr/bin/env -i PATH=/usr/bin PYTHONDONTWRITEBYTECODE=1 "$@"
' bash "$STAGE" "$OUT" "$ROOTFS" "$@"
