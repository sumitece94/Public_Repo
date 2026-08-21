#!/usr/bin/env bash
set -euo pipefail

PROFILE="${MAAS_PROFILE:-admin}"
SYSTEM_ID="${1:?Usage: $0 <system-id>}"

OS="${MAAS_OS:-ubuntu}"
SERIES="${MAAS_SERIES:-jammy}"

command -v maas >/dev/null 2>&1 || {
    echo "ERROR: maas CLI is not installed."
    exit 1
}

echo "===== MAAS Deployment ====="
echo "System ID : ${SYSTEM_ID}"
echo "OS        : ${OS}"
echo "Release   : ${SERIES}"

maas "$PROFILE" machine deploy "$SYSTEM_ID"     osystem="$OS"     distro_series="$SERIES"

echo "Deployment request submitted."
