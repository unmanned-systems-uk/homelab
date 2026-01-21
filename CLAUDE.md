# CLAUDE.md - HomeLab Agent

## Project

- **Repo:** `unmanned-systems-uk/homelab`
- **Directory:** `/home/anthony/HomeLab`
- **Stack:** Infrastructure as Code, Docker, AI/ML, SCPI Automation

---

## Quick Start

Run `/start-homelab` to load full agent context.

---

## Domains

The HomeLab agent manages 8 infrastructure domains:

| # | Domain | Description |
|---|--------|-------------|
| 1 | Network | UniFi (UDM Pro), VLANs, switches, APs |
| 2 | SCPI Equipment | 6 networked test instruments |
| 3 | Virtualization | Proxmox, VMs, containers |
| 4 | Infrastructure as Code | Docker, Ansible |
| 5 | Equipment Inventory | Hardware tracking |
| 6 | AI/ML Operations | GPU, Jetson, models |
| 7 | Home Automation | Home Assistant @ 10.0.1.150 (Active) |
| 8 | **HomeGate** | Unified infrastructure dashboard (i3 @ 10.0.1.50) |

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
6. **USE homelab_db** for all infrastructure data (NOT ccpm_db)

---

## HomeLab Database (CRITICAL)

**ALWAYS use `homelab_db`** - this is the infrastructure database, NOT ccpm_db.

| Parameter | Value |
|-----------|-------|
| **Host** | 10.0.1.251 |
| **Port** | 5433 |
| **Database** | `homelab_db` |
| **User** | ccpm |
| **Password** | CcpmDb2025Secure |

### Quick Connect

```bash
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d homelab_db
```

### Schemas

| Schema | Purpose |
|--------|---------|
| `infrastructure` | Devices, services |
| `credentials` | System credentials, SSH keys |
| `network` | Network assignments, VLANs |
| `virtualization` | Proxmox VMs |
| `scpi` | Test equipment |
| `ai_ml` | Ollama models, GPU tracking |
| `audit` | System events log |

### Common Queries

```sql
-- List all devices
SELECT device_name, primary_ip, status FROM infrastructure.devices;

-- Get device metadata (e.g., HA-Pi5)
SELECT device_name, metadata FROM infrastructure.devices WHERE device_name = 'HA-Pi5';

-- List credentials
SELECT system_name, system_type, port FROM credentials.system_credentials;
```

### Session Reports (ccpm_db)

Session reports go to `ccpm_db` (different database):
- Agent ID: `aaaaaaaa-bbbb-cccc-dddd-222222222222` (HomeLab)
- Agent Tag: `[HomeLab]`

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
| HomeGate Host | 10.0.1.50 | i3 Mini PC (Ubuntu 24.04) |

### Shared Folder (CC-Share)

When the user refers to **"cc-share"**, **"CC-Share"**, or **"/mnt/CC-Share"**, they mean the shared network storage location on the Synology NAS used for cross-system file sharing.

| Parameter | Value |
|-----------|-------|
| **Local Path** | `~/cc-share` (symlink) |
| **Project Folder** | `~/cc-share/HomeLab` |
| **NAS Location** | `\\ccpm-nas.local\CC-Share` |
| **GVFS Mount** | `/run/user/1000/gvfs/smb-share:server=ccpm-nas.local,share=cc-share/` |

```bash
# Access shared files
ls ~/cc-share/

# Copy file to share
/cc-share <file_path>

# Full GVFS path (if symlink doesn't work)
/run/user/1000/gvfs/smb-share:server=ccpm-nas.local,share=cc-share/
```

**Note:** This is a Synology NAS SMB share mounted via GVFS (Gnome). Use `~/cc-share`, NOT `/mnt/cc-share`.

**Auto-Mount:** Configured via systemd user service to mount automatically on login.
**Configuration:** See `docs/cc-share-persistent-mount.md` for details.

---

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/start-homelab` | Full agent startup |
| `/homelab-status` | System + equipment status |
| `/scpi-scan` | Scan SCPI equipment |
| `/network-scan` | Scan 10.0.1.x subnet |
| `/cc-share <file>` | Copy file to CC-Share |

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
| **HomeLab MCP** | Infrastructure tools (Harbor @ 10.0.1.202) |
| **UniFi MCP** | Network visibility (UDM Pro @ 10.0.1.1) |
| **Home Assistant MCP** | Smart home control (HA @ 10.0.1.150) |
| **Context7** | Library documentation lookup |

### HomeLab MCP Server (IMPORTANT)

**This is our primary infrastructure MCP server - use it for extending capabilities.**

| Parameter | Value |
|-----------|-------|
| **Container** | `homelab-mcp` (homelab-infra:latest) |
| **Location** | Harbor VM (10.0.1.202) |
| **Endpoint** | `http://10.0.1.202:8080/sse` |
| **Framework** | FastMCP 2.0+ |
| **Transport** | SSE (Server-Sent Events) |
| **Source Code** | `mcp-servers/homelab-infra/homelab_server.py` |
| **Documentation** | `docs/homelab-mcp-server-structure.md` |

**Current 8 Tools:**
| Tool | Purpose |
|------|---------|
| `homelab_list_vms()` | List all VMs |
| `homelab_get_vm()` | Get VM details |
| `homelab_get_credentials()` | Get credentials (audit logged) |
| `homelab_list_services()` | List services |
| `homelab_check_service_health()` | HTTP health check |
| `homelab_list_hosts()` | List Proxmox hosts |
| `homelab_get_host()` | Get host details |
| `homelab_lookup_ip()` | Lookup IP allocation |

**Extension:** To add new MCP tools (e.g., CCPM messaging), extend `homelab_server.py` - do NOT create new servers.

### Home Assistant MCP Tools

```
mcp__homeassistant__*  - Home Assistant entity control and queries
```

**Capabilities:**
- Query entity states (lights, sensors, switches)
- Control devices (turn on/off, set values)
- Trigger automations and scripts
- Access HA prompts for context

**Note:** Only entities exposed via Settings > Voice Assistants > Assist are accessible.

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

## Related Projects

### HomeGate - Infrastructure Dashboard

| Item | Details |
|------|---------|
| Repository | `unmanned-systems-uk/homegate` |
| Local Path | `/home/homelab/HomeGate` |
| Host | i3 Mini PC @ 10.0.1.50 |
| Status | Design Complete |

**Features:** Persistent SSH terminals, infrastructure monitoring, role-based access, smart alerting

**Integration:** Reuses UniFi MCP (`https://mcp.unmanned-systems.uk/sse`), monitors SCPI equipment, Proxmox VMs, NAS

```bash
# HomeGate issues
gh issue list --repo unmanned-systems-uk/homegate
```

### Home Assistant

| Item | Details |
|------|---------|
| Repository | `unmanned-systems-uk/homeassistant` |
| Local Path | `/home/homelab/homeassistant` |
| Host | HA-Pi5 @ 10.0.1.150:8123 |
| OS | HAOS 16.3 on NVMe |
| Status | Active |

**For dedicated HA work:** `cd /home/homelab/homeassistant` and use `/start-ha`

**Active Integrations:** Wiz (14 bulbs on IoT VLAN 10.0.30.x)

```bash
# HA issues
gh issue list --repo unmanned-systems-uk/homeassistant
```

---

## CCPM V2 Integration

This agent is connected to the CCPM V2 project management system.

### Shared Documentation
- **API Reference:** `~/cc-share/Common/agents/API_REFERENCE.md`
- **Workflow Guide:** `~/cc-share/Common/agents/WORKFLOW_GUIDE.md`
- **Task/Sprint Guide:** `~/cc-share/Common/agents/TASK_SPRINT_GUIDE.md`

### HomeLab Agent ID
```
aaaaaaaa-bbbb-cccc-dddd-222222222222
```

### API Base URL
```
http://10.0.1.210:8000/api/v1
```

### Key Commands
- `/check-messages` - Check for pending messages from other agents
- Create tasks via API (see Task/Sprint Guide in cc-share)
- Send messages via API (see API Reference in cc-share)

### Message the Director (Human)
```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=aaaaaaaa-bbbb-cccc-dddd-222222222222" \
  -H "Content-Type: application/json" \
  -d '{
    "to_user_id": "7563bfda-6e47-4e50-b37a-90ccdc47311a",
    "message_type": "query",
    "subject": "Subject here",
    "body": "Message body",
    "priority": "normal"
  }'
```

### Broadcast to ALL Agents
```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=aaaaaaaa-bbbb-cccc-dddd-222222222222" \
  -H "Content-Type: application/json" \
  -d '{
    "to_user_id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
    "message_type": "info",
    "subject": "Subject",
    "body": "Message",
    "priority": "normal"
  }'
```

---

*HomeLab Agent - Standalone infrastructure management*
