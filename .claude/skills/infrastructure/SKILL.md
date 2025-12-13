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

### VLAN Assignments (Planned)

| VLAN | Name | Purpose | Subnet |
|------|------|---------|--------|
| 10 | Management | Proxmox, switches, APs | 10.0.10.x |
| 20 | Servers | VMs, containers | 10.0.20.x |
| 30 | IoT | Home Assistant devices | 10.0.30.x |
| 40 | Lab | SCPI equipment, dev | 10.0.40.x |

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
