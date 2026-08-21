#!/usr/bin/env bash
set -euo pipefail
echo "===== OPENVPN VALIDATION ====="
systemctl is-active openvpn-server@server
echo "--- IPv4 Forwarding ---"
sysctl net.ipv4.ip_forward
echo "--- VPN Interface ---"
ip -br addr show tun0 2>/dev/null || true
echo "--- Listening Sockets ---"
ss -lunpt
echo "--- Firewall ---"
ufw status verbose
echo "--- Routes ---"
ip route
echo "===== VALIDATION COMPLETE ====="
