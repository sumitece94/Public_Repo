#!/usr/bin/env bash
set -euo pipefail

PROFILE="${MAAS_PROFILE:-admin}"
SYSTEM_ID="${1:?Usage: $0 <system-id>}"

command -v maas >/dev/null 2>&1 || {
    echo "ERROR: maas CLI is not installed."
    exit 1
}

echo "Releasing MAAS machine: ${SYSTEM_ID}"

maas "$PROFILE" machine release "$SYSTEM_ID"     comment="Released through MAAS operations workflow"

echo "Release request submitted."
