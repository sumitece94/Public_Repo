#!/usr/bin/env python3

import subprocess
import sys
import os
import time
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
    return env


def get_vm_id(vm, env):
    r = run_cmd(
        ["openstack", "server", "show", vm, "-c", "id", "-f", "value"],
        env,
    )

    if r.returncode != 0:
        return None

    return r.stdout.strip()


def reboot_vm(vm, project):
    print(f"{CYAN}Rebooting {vm} ({project}){RESET}")

    env = get_env(project)

    vm_id = get_vm_id(vm, env)

    if not vm_id:
        return vm, project, "VM_NOT_FOUND"

    r = run_cmd(
        ["openstack", "server", "reboot", "--soft", vm_id],
        env,
    )

    if r.returncode != 0:
        return vm, project, "REBOOT_FAILED"

    waited = 0

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
                vm, project = line.split()

                if (vm, project) in seen:
                    continue

                seen.add((vm, project))
                entries.append((vm, project))

            except ValueError:
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
        elif status in ["VM_NOT_FOUND", "ERROR", "REBOOT_FAILED", "STATUS_FAILED", "TIMEOUT"]:
            color = RED
        else:
            color = YELLOW

        print(f"{vm:<45} {project:<20} {color}{status}{RESET}")

    print(f"\n{BOLD}=================================={RESET}")


if __name__ == "__main__":
    main()
