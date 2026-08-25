#!/usr/bin/env python3

import subprocess
import sys
import os
import json
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIG =================
MAX_WORKERS = 20
REBOOT_TIMEOUT = 300
REBOOT_POLL = 5

# ================= COLORS =================
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

UUID_REGEX = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def run_cmd(cmd, env=None):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )


def get_env(project):
    env = os.environ.copy()
    env["OS_PROJECT_NAME"] = project
    # Remove OS_PROJECT_ID so OS_PROJECT_NAME is respected
    env.pop("OS_PROJECT_ID", None)
    return env


def get_key(d, key_name):
    """Utility to handle uppercase/lowercase JSON keys across openstackclient versions."""
    return d.get(key_name) or d.get(key_name.lower()) or d.get(key_name.upper())


def get_vm_id(vm_or_id, env):
    # 1. If input is already a UUID, use it directly
    if UUID_REGEX.match(vm_or_id):
        return vm_or_id, ""

    # 2. Search by server name using JSON format for exact duplicate detection
    r = run_cmd(
        ["openstack", "server", "list", "--name", vm_or_id, "-f", "json"],
        env,
    )

    if r.returncode != 0:
        return None, "LOOKUP_FAILED"

    try:
        data = json.loads(r.stdout)
    except Exception:
        return None, "LOOKUP_PARSE_FAILED"

    matches = [i for i in data if get_key(i, "Name") == vm_or_id]

    if not matches:
        return None, "VM_NOT_FOUND"

    if len(matches) > 1:
        return None, f"DUPLICATE_VM ({len(matches)} matches)"

    return get_key(matches[0], "ID"), ""


def reboot_vm(vm, project):
    print(f"{CYAN}Rebooting {vm} ({project}){RESET}")

    env = get_env(project)

    vm_id, err_status = get_vm_id(vm, env)

    if not vm_id:
        return vm, project, err_status

    r = run_cmd(
        ["openstack", "server", "reboot", "--soft", vm_id],
        env,
    )

    if r.returncode != 0:
        return vm, project, "REBOOT_FAILED"

    # Brief delay to allow OpenStack Nova to update state out of ACTIVE
    time.sleep(3)

    waited = 3

    while waited < REBOOT_TIMEOUT:
        s = run_cmd(
            [
                "openstack",
                "server",
                "show",
                vm_id,
                "-c",
                "status",
                "-f",
                "value",
            ],
            env,
        )

        if s.returncode != 0:
            return vm, project, "STATUS_FAILED"

        status = s.stdout.strip()

        if status == "ACTIVE":
            return vm, project, "ACTIVE"

        if status == "ERROR":
            return vm, project, "ERROR"

        time.sleep(REBOOT_POLL)
        waited += REBOOT_POLL

    return vm, project, "TIMEOUT"


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} vmlist.txt")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        entries = []
        seen = set()

        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                a = line.split()
                project = a[-1]
                vm = " ".join(a[:-1])

                if (vm, project) in seen:
                    continue

                seen.add((vm, project))
                entries.append((vm, project))

            except (ValueError, IndexError):
                print(f"{RED}Invalid line: {line}{RESET}")

    print(f"\n{YELLOW}Total VMs : {len(entries)}{RESET}")

    confirm = input("Type 'yes' to reboot all VMs: ")

    if confirm.lower() != "yes":
        print("Cancelled.")
        sys.exit(0)

    results = []

    print(f"\n{BOLD}========== REBOOT START =========={RESET}\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(reboot_vm, vm, project)
            for vm, project in entries
        ]

        for future in as_completed(futures):
            results.append(future.result())

    print(f"\n{BOLD}========== FINAL RESULT =========={RESET}\n")

    results.sort()

    for vm, project, status in results:
        if status == "ACTIVE":
            color = GREEN
        elif (
            status == "VM_NOT_FOUND"
            or status.startswith("DUPLICATE_VM")
            or status in ["ERROR", "REBOOT_FAILED", "STATUS_FAILED", "TIMEOUT"]
        ):
            color = RED
        else:
            color = YELLOW

        print(f"{vm:<45} {project:<20} {color}{status}{RESET}")

    print(f"\n{BOLD}=================================={RESET}")


if __name__ == "__main__":
    main()
