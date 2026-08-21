# AWS EC2 OpenVPN Ansible Automation

Practical lab project demonstrating OpenVPN deployment, configuration, security hardening and validation on Ubuntu EC2 using Ansible.

> Sanitized portfolio example. No AWS credentials, SSH private keys, OpenVPN private keys, certificates, production IPs or customer data are included.

## Technology
- AWS EC2
- Ubuntu Linux
- Ansible
- OpenVPN Community Edition
- UFW
- Linux networking
- Bash

## Workflow
AWS EC2 Ubuntu VM → Ansible SSH → OpenVPN installation → server configuration → IP forwarding/NAT → firewall → SSH hardening → validation.

## Structure
```text
aws-openvpn-ansible-automation/
├── README.md
├── .gitignore
├── inventory/hosts.example
├── group_vars/vpn.example.yml
├── playbooks/
│   ├── openvpn-install.yml
│   ├── openvpn-configure.yml
│   ├── security-hardening.yml
│   └── validate-openvpn.yml
├── roles/
│   ├── openvpn/{tasks,handlers,templates}
│   └── security/{tasks,handlers}
└── scripts/validate-vpn.sh
```

## Run
Copy examples locally:
```bash
cp inventory/hosts.example inventory/hosts
cp group_vars/vpn.example.yml group_vars/vpn.yml
```

Install:
```bash
ansible-playbook -i inventory/hosts playbooks/openvpn-install.yml
```

Configure:
```bash
ansible-playbook -i inventory/hosts playbooks/openvpn-configure.yml
```

Harden:
```bash
ansible-playbook -i inventory/hosts playbooks/security-hardening.yml
```

Validate:
```bash
ansible-playbook -i inventory/hosts playbooks/validate-openvpn.yml
```

## Security
Never commit AWS keys, SSH private keys, OpenVPN private keys, CA keys, real inventory files, passwords, tokens or production IP information. Example files use placeholders such as `<EC2_PUBLIC_IP>`, `<SSH_USER>` and `<SSH_PRIVATE_KEY>`.

## Portfolio Skills
AWS EC2 | Ubuntu Linux | Ansible | OpenVPN | Linux Networking | UFW | NAT | IP Forwarding | SSH Hardening | Configuration Management | Infrastructure Automation | Operations
