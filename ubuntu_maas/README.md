# Ubuntu MAAS Deployment & Operations

A practical lab repository demonstrating Ubuntu MAAS deployment, bare-metal provisioning,
machine lifecycle management, cloud-init configuration, health validation, and operational
automation.

> This repository contains sanitized lab examples only. No production credentials,
> internal IP addresses, customer data, private keys, or company-specific configuration
> are included.

## Project Objectives

- Deploy and manage Ubuntu systems through MAAS
- Automate machine commissioning and deployment
- Perform post-deployment Linux validation
- Use cloud-init for baseline configuration
- Perform basic hardware and network health checks
- Demonstrate repeatable MAAS operational workflows

## Technology Stack

- Ubuntu Linux
- MAAS
- MAAS CLI
- Cloud-init
- Bash / Shell
- KVM / VMware lab environments
- Linux networking
- Git / GitHub

## Repository Structure

```text
ubuntu-maas-deployment-operations/
├── README.md
├── .gitignore
├── config/
│   └── maas-lab.env.example
├── scripts/
│   ├── maas-inventory.sh
│   ├── commission-machine.sh
│   ├── deploy-ubuntu.sh
│   ├── release-machine.sh
│   └── validate-node.sh
├── commissioning/
│   └── hardware-health-check.sh
└── cloud-init/
    └── ubuntu-base.yaml
```

## MAAS Lifecycle

```text
Machine Discovery
       |
       v
Commissioning
       |
       v
Hardware Validation
       |
       v
Allocation
       |
       v
Ubuntu Deployment
       |
       v
Cloud-init Configuration
       |
       v
Post-Deployment Validation
       |
       v
Operations / Monitoring
       |
       v
Release / Recommission
```

## Configuration

Copy the example environment file and customize it for a local lab:

```bash
cp config/maas-lab.env.example config/maas-lab.env
source config/maas-lab.env
```

Do not commit `maas-lab.env`.

## Example Workflow

### 1. Check machines

```bash
./scripts/maas-inventory.sh
```

### 2. Commission a machine

```bash
./scripts/commission-machine.sh <system-id>
```

### 3. Deploy Ubuntu

```bash
./scripts/deploy-ubuntu.sh <system-id>
```

### 4. Validate the deployed node

Run on the deployed Ubuntu host:

```bash
./scripts/validate-node.sh
```

### 5. Release the machine

```bash
./scripts/release-machine.sh <system-id>
```

## Security

The repository intentionally uses placeholders and documentation-safe example values.

Never commit:

- Passwords
- API keys
- MAAS authentication tokens
- SSH private keys
- kubeconfig files
- Production IP addresses
- Internal DNS names
- Customer information

## Purpose

This repository is maintained as a technical portfolio/lab demonstrating practical
Ubuntu MAAS deployment and infrastructure operations concepts.
