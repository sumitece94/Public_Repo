#!/usr/bin/env python3

import subprocess
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 40

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_cmd(cmd):

    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def delete_flow(vm):

    print(f"{CYAN}Processing -> {vm}{RESET}")

    # FAST lookup
    r = run_cmd([
        "openstack",
        "server",
        "list",
        "--all-projects",
        "--name",
        vm,
        "-f",
        "json"
    ])

    if r.returncode != 0:
        return vm, "LOOKUP_FAILED"

    try:
        servers = json.loads(r.stdout)
    except:
        return vm, "JSON_ERROR"

    exact_matches = []
    duplicate_found = False

    for s in servers:

        name = s.get("Name", "").strip()

        if name == vm:
            exact_matches.append(s)

        elif name.startswith(vm):
            duplicate_found = True

    if len(exact_matches) == 0:
        return vm, "VM_NOT_FOUND"

    if len(exact_matches) > 1:
        return vm, "DUPLICATE_EXACT_VM"

    if duplicate_found:
        return vm, "DUPLICATE_NAME_FOUND"

    vm_id = exact_matches[0]["ID"]

    d = run_cmd([
        "openstack",
        "server",
        "delete",
        vm_id
    ])

    if d.returncode == 0:
        return vm, "DELETED"

    return vm, "DELETE_FAILED"


def main():

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} vm.txt")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        lines = [x.strip() for x in f if x.strip()]

    seen = set()
    vms = []

    for vm in lines:

        if vm in seen:
            print(f"{YELLOW}[INPUT_DUPLICATE_SKIPPED] {vm}{RESET}")
            continue

        seen.add(vm)
        vms.append(vm)

    results = []

    print(f"\n{BOLD}========== DELETE PHASE =========={RESET}\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [
            executor.submit(delete_flow, vm)
            for vm in vms
        ]

        for f in as_completed(futures):
            results.append(f.result())

    print(f"\n{BOLD}============= FINAL RESULT ============={RESET}\n")

    for vm, status in sorted(results):

        color = (
            GREEN if status == "DELETED"
            else YELLOW if "DUPLICATE" in status
            else RED
        )

        print(
            f"{vm:<45} "
            f"{color}{status}{RESET}"
        )

    print(f"\n{BOLD}========================================{RESET}")
    print("Script completed.\n")


if __name__ == "__main__":
    main()
