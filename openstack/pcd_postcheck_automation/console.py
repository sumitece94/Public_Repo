import subprocess
import json
import requests
import sys
import platform
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PING_TIMEOUT = "1"


def run_cmd(cmd):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def find_vm_all_projects(vm_name):
    result = run_cmd([
        "openstack", "server", "list",
        "--all-projects",
        "--name", vm_name,
        "-f", "json"
    ])
    if result.returncode != 0 or not result.stdout:
        return None

    for s in json.loads(result.stdout):
        if s.get("Name", "").lower() == vm_name.lower():
            return s["ID"]
    return None


def get_server_details(vm_id):
    result = run_cmd(["openstack", "server", "show", vm_id, "-f", "json"])
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def get_project_name(project_id):
    result = run_cmd([
        "openstack", "project", "show",
        project_id, "-f", "value", "-c", "name"
    ])
    return result.stdout.strip() if result.returncode == 0 else "Unknown"


def get_console_url(vm_id):
    result = run_cmd([
        "openstack", "console", "url", "show",
        vm_id, "-f", "value", "-c", "url"
    ])
    return result.stdout.strip() if result.returncode == 0 else None


def check_console(url):
    try:
        r = requests.head(url, timeout=3, verify=False)
        return r.status_code in (200, 302)
    except Exception:
        return False


def get_ip(details):
    addresses = details.get("addresses")

    if isinstance(addresses, dict):
        for _, v in addresses.items():
            if isinstance(v, list) and v:
                first = v[0]
                if isinstance(first, dict):
                    return first.get("addr")
                elif isinstance(first, str):
                    return first

    if isinstance(addresses, str):
        for part in addresses.split(","):
            if "=" in part:
                return part.split("=")[1].strip()

    return None


def ping_once(ip):
    if not ip:
        return False
    count = "-n" if platform.system().lower() == "windows" else "-c"
    timeout = "-w" if platform.system().lower() == "windows" else "-W"
    try:
        return subprocess.run(
            ["ping", count, "1", timeout, PING_TIMEOUT, ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode == 0
    except Exception:
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 console_check.py <vm_list_file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        vm_names = [l.strip() for l in f if l.strip()]

    problems = []

    print("=" * 70)
    print("Console + Ping Check (ALL TENANTS, POWER-STATE AWARE)")
    print("=" * 70)

    for vm in vm_names:
        vm_issues = []

        print(f"VM Name        : {vm}")

        vm_id = find_vm_all_projects(vm)
        if not vm_id:
            print("Status         : ❌ VM NOT FOUND")
            problems.append((vm, ["VM NOT FOUND"]))
            print("-" * 70)
            continue

        details = get_server_details(vm_id)
        status = details.get("status")
        power_state = details.get("OS-EXT-STS:power_state")

        power_map = {1: "RUNNING"}
        if power_state != 1:
            vm_issues.append("POWER OFF")

        print(f"VM Status      : {status}")
        print(f"Power State    : {power_map.get(power_state, 'NOT RUNNING')}")

        project_id = details.get("project_id") or details.get("tenant_id")
        tenant = get_project_name(project_id) if project_id else "Unknown"
        print(f"Tenant/Project : {tenant}")

        console_url = get_console_url(vm_id)
        if console_url:
            print(f"Console URL    : {console_url}")
            if power_state == 1:
                if check_console(console_url):
                    print("Console Access : ✅ OK")
                else:
                    print("Console Access : ❌ FAILED")
                    vm_issues.append("CONSOLE FAILED")
            else:
                print("Console Access : ❌ FAILED (VM not running)")
                vm_issues.append("CONSOLE FAILED")
        else:
            print("Console URL    : ❌ Not Available")
            print("Console Access : ❌ FAILED")
            vm_issues.append("NO CONSOLE")

        ip = get_ip(details)
        if ip:
            if ping_once(ip):
                print(f"Ping ({ip})    : ✅ Reachable")
            else:
                print(f"Ping ({ip})    : ❌ Unreachable")
                vm_issues.append("PING FAILED")
        else:
            print("Ping           : ❌ No IP")
            vm_issues.append("NO IP")

        if vm_issues:
            problems.append((vm, vm_issues))

        print("-" * 70)

    # ===== SUMMARY =====
    print("\n" + "=" * 70)
    print("SUMMARY (PROBLEMATIC VMs)")
    print("=" * 70)

    if not problems:
        print("✅ No problematic VMs found")
    else:
        print(f"{'VM Name':<25}Issue(s)")
        print("-" * 70)
        for vm, issues in problems:
            print(f"{vm:<25}{', '.join(issues)}")
        print("-" * 70)
        print(f"Total Problematic VMs : {len(problems)}")

    print("=" * 70)


if __name__ == "__main__":
    main()

