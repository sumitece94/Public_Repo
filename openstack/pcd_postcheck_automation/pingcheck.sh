#!/bin/bash

# List of IPs to ping
ips=(

10.102.51.111
10.252.160.38
10.102.99.12
10.252.106.170
10.252.104.100
10.252.107.108
10.252.104.123
10.252.106.165
10.252.106.130







)


# Array to store failed or lossy IPs
declare -a failed_ips

echo "🔍 Pinging all IPs (3 packets each)..."
echo "========================================"

# Loop over each IP
for ip in "${ips[@]}"; do
    echo "📡 Pinging $ip..."
    result=$(ping -c 3 -q "$ip" 2>&1)
    if [[ $? -ne 0 ]]; then
        echo "❌ Ping failed for $ip"
        failed_ips+=("$ip (Ping failed)")
    else
        loss=$(echo "$result" | grep -oP '\d+(?=% packet loss)')
        if [[ "$loss" -gt 0 ]]; then
            echo "⚠️  $loss% packet loss for $ip"
            failed_ips+=("$ip ($loss% loss)")
        else
            echo "✅ $ip is reachable with 0% packet loss"
        fi
    fi
    echo "----------------------------------------"
done

# Summary
echo ""
echo "📋 Summary of failures or packet loss"
echo "========================================"
if [ ${#failed_ips[@]} -eq 0 ]; then
    echo "✅ All IPs responded with 0% packet loss."
else
    for f in "${failed_ips[@]}"; do
        echo "🔴 $f"
    done
fi
