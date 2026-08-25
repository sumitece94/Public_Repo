import subprocess
import json
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIG =================
MAX_WORKERS = 8
SECURITY_GROUP_NAME = "allow-all"
REBOOT_TIMEOUT = 300
REBOOT_POLL = 5
SLEEP_AFTER_PORT_ENABLE = 2

# ================= COLORS =================
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ================= COMMON =================
def run_cmd(cmd, env=None):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )


def get_env(project):
    env = os.environ.copy()
    env["OS_PROJECT_NAME"] = project
    return env


# ================= SG FUNCTIONS =================
def get_vm_id(vm, env):
    r = run_cmd(["openstack", "server", "show", vm, "-c", "id", "-f", "value"], env)
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def get_allow_all_sg_id(env):
    r = run_cmd(["openstack", "security", "group", "list", "-f", "json"], env)
    if r.returncode != 0:
        return None

    for sg in json.loads(r.stdout):
        if sg["Name"] == SECURITY_GROUP_NAME:
            return sg["ID"]
    return None


def sg_flow(vm, project):
    print(f"{CYAN}Processing SG -> {vm} ({project}){RESET}")

    env = get_env(project)
    vm_id = get_vm_id(vm, env)

    if not vm_id:
        print(f"{RED}[VM_NOT_FOUND]{RESET}")
        return vm, project, "VM_NOT_FOUND"

    r = run_cmd(["openstack", "port", "list", "--server", vm_id, "-f", "json"], env)
    ports = json.loads(r.stdout)

    if not ports:
        print(f"{RED}[NO_PORT]{RESET}")
        return vm, project, "NO_PORT"

    port_id = ports[0]["ID"]

    r2 = run_cmd([
        "openstack", "port", "show", port_id,
        "-c", "security_group_ids",
        "-c", "port_security_enabled",
        "-f", "json"
    ], env)

    port_data = json.loads(r2.stdout)

    if port_data.get("security_group_ids"):
        print(f"{YELLOW}[ALREADY_HAS_SG]{RESET}")
        return vm, project, "ALREADY_HAS_SG"

    if not port_data.get("port_security_enabled"):
        print(f"{CYAN}[Enabling port security]{RESET}")
        run_cmd(["openstack", "port", "set", "--enable-port-security", port_id], env)
        time.sleep(SLEEP_AFTER_PORT_ENABLE)

    sg_id = get_allow_all_sg_id(env)
    if not sg_id:
        print(f"{RED}[ALLOW_ALL_SG_NOT_FOUND]{RESET}")
        return vm, project, "SG_NOT_FOUND"

    r3 = run_cmd(
        ["openstack", "server", "add", "security", "group", vm_id, sg_id],
        env
    )

    if r3.returncode == 0:
        print(f"{GREEN}[SG_ATTACHED]{RESET}")
        return vm, project, "ATTACHED"
    else:
        print(f"{RED}[SG_FAILED] {r3.stderr.strip()}{RESET}")
        return vm, project, "FAILED"


# ================= REBOOT FUNCTIONS =================
def reboot_flow(vm, project):
    print(f"{CYAN}Processing Reboot -> {vm} ({project}){RESET}")

    env = get_env(project)
    vm_id = get_vm_id(vm, env)

    if not vm_id:
        print(f"{RED}[REBOOT_VM_NOT_FOUND]{RESET}")
        return vm, project, "VM_NOT_FOUND"

    r = run_cmd(["openstack", "server", "reboot", "--soft", vm_id], env)
    if r.returncode != 0:
        print(f"{RED}[REBOOT_FAILED]{RESET}")
        return vm, project, "REBOOT_FAILED"

    waited = 0
    while waited < REBOOT_TIMEOUT:
        status = run_cmd(
            ["openstack", "server", "show", vm_id, "-c", "status", "-f", "value"],
            env
        ).stdout.strip()

        if status == "ACTIVE":
            print(f"{GREEN}[ACTIVE]{RESET}")
            return vm, project, "ACTIVE"

        time.sleep(REBOOT_POLL)
        waited += REBOOT_POLL

    print(f"{RED}[TIMEOUT]{RESET}")
    return vm, project, "TIMEOUT"


# ================= MAIN =================
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 sg_attach_and_reboot.py vmlist.txt [--reboot]")
        sys.exit(1)

    reboot_requested = "--reboot" in sys.argv
    reboot_confirmed = False

    if reboot_requested:
        confirm = input("\nType 'yes' to confirm reboot: ")
        if confirm.lower() == "yes":
            reboot_confirmed = True
        else:
            print("\nReboot skipped. SG only mode.\n")

    with open(sys.argv[1]) as f:
        lines = [line.strip() for line in f if line.strip()]

    entries = []
    seen = set()

    for line in lines:
        try:
            vm, project = line.split()
            if vm in seen:
                print(f"{YELLOW}[DUPLICATE SKIPPED] {vm}{RESET}")
                continue
            seen.add(vm)
            entries.append((vm, project))
        except ValueError:
            print(f"{RED}[INVALID FORMAT] {line}{RESET}")

    sg_results = []
    reboot_results = []

    # ===== SG PHASE =====
    print(f"\n{BOLD}===== SECURITY GROUP PHASE ====={RESET}\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(sg_flow, vm, project) for vm, project in entries]
        for f in as_completed(futures):
            sg_results.append(f.result())

    # ===== REBOOT PHASE =====
    if reboot_confirmed:
        print(f"\n{BOLD}===== REBOOT PHASE ====={RESET}\n")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(reboot_flow, vm, project) for vm, project in entries]
            for f in as_completed(futures):
                reboot_results.append(f.result())

    # ===== FINAL SUMMARY =====
    print(f"\n{BOLD}================ FINAL RESULT ================ {RESET}\n")

    for vm, project, sg_status in sg_results:
        reboot_status = "-"
        for rvm, rproject, rstatus in reboot_results:
            if rvm == vm and rproject == project:
                reboot_status = rstatus

        sg_color = GREEN if sg_status in ["ATTACHED", "ALREADY_HAS_SG"] else RED
        rb_color = GREEN if reboot_status == "ACTIVE" else RED if reboot_status != "-" else RESET

        print(
            f"{vm:<25} {project:<20} "
            f"{sg_color}{sg_status:<20}{RESET} "
            f"{rb_color}{reboot_status}{RESET}"
        )

    print(f"\n{BOLD}=============================================={RESET}")
    print("Script completed.\n")


if __name__ == "__main__":
    main()
