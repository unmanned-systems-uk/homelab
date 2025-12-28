# CLAUDE.md - HomeLab Agent

## Project

- **Repo:** `unmanned-systems-uk/homelab`
- **Directory:** `/home/anthony/ccpm-workspace/HomeLab`
- **Stack:** Infrastructure as Code, Docker, AI/ML, SCPI Automation

---

## Quick Start

Run `/start-homelab` to load full agent context.

---

## Domains

The HomeLab agent manages 7 infrastructure domains:

| # | Domain | Description |
|---|--------|-------------|
| 1 | Network | UniFi (UDM Pro), VLANs, switches, APs |
| 2 | SCPI Equipment | 6 networked test instruments |
| 3 | Virtualization | Proxmox, VMs, containers |
| 4 | Infrastructure as Code | Docker, Ansible |
| 5 | Equipment Inventory | Hardware tracking |
| 6 | AI/ML Operations | GPU, Jetson, models |
| 7 | Home Automation | Home Assistant (planned) |

---

## Task Tracking

**GitHub Issues only** - no external APIs:

```bash
# List open issues
gh issue list --repo unmanned-systems-uk/homelab

# Create issue
gh issue create --repo unmanned-systems-uk/homelab --title "Title" --body "Body"

# Add label
gh issue edit <number> --add-label "in-progress" --repo unmanned-systems-uk/homelab
```

**Workflow:** `todo` → `in-progress` → `done` (via labels)

---

## Critical Rules

1. **NEVER close GitHub issues** - User closes issues
2. **NEVER enable SCPI outputs** without explicit user confirmation
3. **TIMEOUT all network commands** (2-3 seconds max)
4. **Document all changes** in git
5. **Session summaries** for significant work (`docs/session-summary-YYYY-MM-DD.md`)

---

## Equipment Reference

### SCPI Equipment (10.0.1.x)

| Device | IP | Port | Model |
|--------|-----|------|-------|
| DMM | 10.0.1.101 | 5025 | Keithley DMM6500 |
| DC Load | 10.0.1.105 | 5555 | Rigol DL3021A |
| Scope | 10.0.1.106 | 5555 | Rigol MSO8204 |
| PSU-1 | 10.0.1.111 | 5025 | Rigol DP932A |
| AWG | 10.0.1.120 | 5555 | Rigol DG2052 |
| PSU-2 | 10.0.1.138 | 5025 | Rigol DP932A |

### Network Devices

| Device | IP | Description |
|--------|-----|-------------|
| UDM Pro | 10.0.1.1 | UniFi Dream Machine Pro |
| NAS | 10.0.1.251 | Synology DS1621 |
| Jetson | 10.0.1.113 | Orin NX |
| Pi5 DPM | 10.0.1.53 | Raspberry Pi 5 |

---

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/start-homelab` | Full agent startup |
| `/homelab-status` | System + equipment status |
| `/scpi-scan` | Scan SCPI equipment |
| `/network-scan` | Scan 10.0.1.x subnet |

---

## Quick Commands

```bash
# GitHub
gh issue list --repo unmanned-systems-uk/homelab
gh issue create --repo unmanned-systems-uk/homelab --title "Title" --body "Body"

# Quick SCPI check
echo "*IDN?" | nc -w 2 10.0.1.101 5025

# Network ping
ping -c 1 -W 1 10.0.1.1
```

---

## MCP Tools

| Tool | Purpose |
|------|---------|
| **Context7** | Library documentation lookup |
| **UniFi MCP** | Network visibility (UDM Pro @ 10.0.1.1) |

### UniFi MCP Tools

```
unifi_list_devices    - List all UniFi devices (switches, APs)
unifi_get_clients     - Get connected clients
unifi_get_networks    - Get network/VLAN configurations
unifi_get_firewalls   - Get firewall rules
```

### Using Context7

```
mcp__context7__resolve-library-id(libraryName: "docker")
mcp__context7__get-library-docs(context7CompatibleLibraryID: "/docker/docs", topic: "compose")
```

---

## Directory Structure

```
HomeLab/
├── docs/               # Documentation, hardware inventory
├── infrastructure/     # IaC configs (Docker, Ansible, Proxmox)
├── scripts/            # Automation scripts
└── .claude/
    ├── agents/homelab/ # Agent definition
    ├── commands/       # Slash commands
    ├── skills/         # infrastructure, scpi-automation
    └── common/         # Shared rules
```

---

## Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| infrastructure | `.claude/skills/infrastructure/` | Proxmox, Docker, networking |
| scpi-automation | `.claude/skills/scpi-automation/` | Test equipment control |

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/hardware-inventory.md` | All equipment |
| `docs/server-stack-architecture.md` | Infrastructure design |
| `docs/learning-hub.md` | AI/ML resources |
| `docs/session-summary-*.md` | Session records |
| `docs/udm-pro-migration-complete.md` | Network config |

---

*HomeLab Agent - Standalone infrastructure management*
