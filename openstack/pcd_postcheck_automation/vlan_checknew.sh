#!/bin/bash

# Check for VLAN file argument
if [[ -z "$1" ]]; then
  echo "Usage: $0 <vlan_file>"
  exit 1
fi

VLAN_FILE="$1"

if [[ ! -f "$VLAN_FILE" ]]; then
  echo "Error: VLAN file '$VLAN_FILE' does not exist."
  exit 1
fi

# Loop through each VLAN ID in the provided file
while read -r vlan || [[ -n "$vlan" ]]; do
  # Skip empty lines and comments
  [[ -z "$vlan" || "$vlan" =~ ^# ]] && continue

  echo "Checking VLAN: $vlan"

  # Capture output of openstack command
  output=$(openstack network list --provider-segment "$vlan")

  # Count lines excluding header/footer lines
  # openstack network list outputs at least 3 lines for header/footer if empty
  line_count=$(echo "$output" | sed '/^+/d' | sed '/^| ID/d' | grep -cve '^\s*$')

  if [[ $line_count -eq 0 ]]; then
    echo "VLAN $vlan does not exist."
  else
    echo "$output"
  fi

  echo    # blank line for readability
done < "$VLAN_FILE"

