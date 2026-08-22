#!/bin/bash

# List of project names to check
project_names=(


ddcp_tst
gs_sup
mna_csd
ti_cpsm
)


#Recources to check
resources=("cores" "instances" "ram" "volumes" "per-volume-gigabytes")

echo "Checking quota = 0 for selected resources (ignoring -1)..."
echo "==========================================================="

for name in "${project_names[@]}"; do
  # Get project ID by matching project name exactly (case-sensitive)
  project_id=$(openstack project list -f value -c ID -c Name | grep -w "$name" | awk '{print $1}')

  if [[ -z "$project_id" ]]; then
    echo "❌ Project not found: $name"
    echo "-----------------------------------------------------------"
    continue
  fi

  echo "Project: $name (ID: $project_id)"
  show_warning=0

  for resource in "${resources[@]}"; do
    value=$(openstack quota show "$project_id" -f value -c "$resource" 2>/dev/null)

    if [[ "$value" != "-1" && "$value" == "0" ]]; then
      echo "  ⚠️  $resource quota is 0"
      show_warning=1
    fi
  done

  [[ "$show_warning" -eq 0 ]] && echo "  ✅ All selected quotas are set (none = 0)"
  echo "-----------------------------------------------------------"
done

