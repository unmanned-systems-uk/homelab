# Infrastructure Skill

**Skill Name:** infrastructure
**Version:** 1.0.0

---

## Purpose

This skill provides patterns and best practices for HomeLab infrastructure work including Proxmox, Docker, networking, and storage.

---

## Allowed Tools

- Read, Write, Edit, Glob, Grep
- Bash (infrastructure commands)
- WebFetch, WebSearch
- Context7 MCP
- UniFi MCP

---

## Patterns

### Proxmox VM Creation

When creating VM definitions:

```yaml
# Standard VM template
vm:
  name: descriptive-name
  id: 1XX  # 100-199 range for HomeLab
  cores: 2-4
  memory: 4096-8192  # MB
  disk: 32-64  # GB
  network:
    bridge: vmbr0
    vlan: XX  # if applicable
  os: debian-12 | ubuntu-24.04 | haos
```

### Docker Compose Standards

```yaml
version: '3.8'
services:
  service-name:
    image: image:tag
    container_name: hl-service-name  # prefix with hl-
    restart: unless-stopped
    environment:
      - TZ=Europe/London
    volumes:
      - ./data:/data  # relative paths
    networks:
      - homelab
    labels:
      - "homelab.service=true"

networks:
  homelab:
    external: true
```

### VLAN Assignments (Active)

| VLAN | Name | Purpose | Subnet |
|------|------|---------|--------|
| - | Default | SCPI equipment, servers | 10.0.1.x |
| 10 | Management | Switches, APs | 10.0.10.x |
| 20 | Media | Media devices | 10.0.20.x |
| 30 | IoT | Smart home devices | 10.0.30.x |
| 50 | Lab | Development, testing | 10.0.50.x |

### File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Docker compose | `docker-compose.{service}.yml` | `docker-compose.n8n.yml` |
| Ansible playbook | `{target}-{action}.yml` | `proxmox-setup.yml` |
| Scripts | `{action}-{target}.sh` | `backup-vms.sh` |

---

## Checklist

Before completing infrastructure tasks:

- [ ] Configuration uses variables, not hardcoded values
- [ ] Secrets are in environment variables or vault
- [ ] Backups/snapshots considered
- [ ] Documentation updated
- [ ] Tested in non-production first (if applicable)

---

## Resources

Use Context7 MCP for documentation:
- Proxmox: `/proxmox/pve-docs`
- Docker: `/docker/docs`
- Ansible: `/ansible/ansible`

---

## UniFi MCP

**Controller:** UDM Pro at 10.0.1.1

### Available Tools

| Tool | Purpose |
|------|---------|
| `unifi_list_devices` | List all UniFi devices (switches, APs) |
| `unifi_get_clients` | Get connected clients |
| `unifi_get_networks` | Get network/VLAN configurations |
| `unifi_get_firewalls` | Get firewall rules |
| `unifi_get_port_forwards` | Get port forwarding rules |

### Network Queries

```
# List all devices
unifi_list_devices

# Get client list
unifi_get_clients

# Get VLAN/network config
unifi_get_networks
```

### Infrastructure Devices (VLAN 10)

| Device | IP | Type |
|--------|-----|------|
| US 48 Dev Office | 10.0.10.10 | Switch |
| US 24 Dev Desk | 10.0.10.11 | Switch |
| US 24 PoE Studio | 10.0.10.12 | Switch |
| US 24 PoE Cinema | 10.0.10.13 | Switch |
| AC Pro APs | 10.0.10.20-26 | Access Points |
