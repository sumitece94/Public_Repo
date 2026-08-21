#!/usr/bin/env bash
set -euo pipefail

PROFILE="${MAAS_PROFILE:-admin}"

command -v maas >/dev/null 2>&1 || {
    echo "ERROR: maas CLI is not installed."
    exit 1
}

command -v jq >/dev/null 2>&1 || {
    echo "ERROR: jq is not installed."
    exit 1
}

echo "===== MAAS Machine Inventory ====="

maas "$PROFILE" machines read |
jq -r '
  .[] |
  [
    .system_id,
    (.hostname // "-"),
    (.status_name // "-"),
    (.architecture // "-"),
    (.cpu_count // 0),
    (.memory // 0)
  ] | @tsv
'

echo "===== Inventory Complete ====="
