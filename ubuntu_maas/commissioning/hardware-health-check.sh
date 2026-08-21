#!/usr/bin/env bash
set -euo pipefail

echo "===== MAAS Hardware Health Check ====="

echo
echo "--- CPU ---"
lscpu | grep -E 'Model name|CPU\(s\)|NUMA' || true

echo
echo "--- Memory ---"
free -h

echo
echo "--- Storage ---"
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT

echo
echo "--- Network ---"
ip -br link
ip -br addr

echo
echo "--- PCI Devices ---"
lspci | head -50

echo
echo "--- Kernel ---"
uname -r

echo
echo "--- Failed Services ---"
systemctl --failed --no-pager || true

echo
echo "===== Hardware Health Check Complete ====="
