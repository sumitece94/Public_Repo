#!/usr/bin/env bash
set -euo pipefail

echo "===== Ubuntu Node Validation ====="

echo
echo "--- Hostname ---"
hostnamectl --static

echo
echo "--- Operating System ---"
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    echo "${PRETTY_NAME}"
fi

echo
echo "--- Kernel ---"
uname -r

echo
echo "--- CPU ---"
nproc

echo
echo "--- Memory ---"
free -h

echo
echo "--- Storage ---"
lsblk

echo
echo "--- Network ---"
ip -br addr

echo
echo "--- Failed Services ---"
systemctl --failed --no-pager || true

echo
echo "--- Disk Usage ---"
df -h

echo
echo "===== Validation Complete ====="
