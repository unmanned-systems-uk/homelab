# HomeLab Session Summary - 2025-12-14

**Agent:** HomeLab Specialist
**Duration:** Extended session
**Focus:** Infrastructure setup, MCP server deployment, Docker services

---

## Completed This Session

### 1. Whisper TTS VM (VM 100) - Setup Complete

| Property | Value |
|----------|-------|
| VMID | 100 |
| Name | whisper-tts |
| IP | 10.0.1.201 |
| OS | Ubuntu 24.04 Server |
| CPU | 6 cores |
| RAM | 16GB |
| Disk | 100GB |
| GPU | GTX 1080 Ti (11GB) - passthrough |
| SSH | `ssh ccpm@10.0.1.201` |
| tmux | `whisper` |

**Software Installed:**
- NVIDIA Driver 570 + CUDA 12.8
- Python 3.12 with venv at `~/whisper-venv`
- PyTorch 2.5.1+cu121
- faster-whisper 1.2.1
- piper-tts 1.3.0

**Resource Monitoring Scripts:**
- `~/resource_monitor.py` - Logs CPU, RAM, GPU stats
- `~/analyze_resources.py` - Summarizes collected metrics

**Status:** Ready for Backend Designer to implement TTS API (Issue #7)

---

### 2. Harbor VM (VM 101) - Docker Services

| Property | Value |
|----------|-------|
| VMID | 101 |
| Name | harbor |
| IP | 10.0.1.202 |
| OS | Ubuntu 24.04 Server |
| CPU | 2 cores |
| RAM | 4GB |
| Disk | 50GB |
| SSH | `ssh ccpm@10.0.1.202` |
| tmux | `harbor` |

**Services Running:**

| Service | URL | Container |
|---------|-----|-----------|
| Portainer | https://10.0.1.202:9443 | portainer |
| HomeLab MCP | http://10.0.1.202:8080/sse | homelab-mcp |

**Portainer Credentials:**
- Username: `Anthony`
- Password: `PORTAdman2350!@`
- (Also stored encrypted in homelab.db)

---

### 3. HomeLab Infrastructure MCP Server

**Location:** `HomeLab/mcp-servers/homelab-infra/`

**Files:**
```
homelab-infra/
├── homelab_server.py     # FastMCP server with 8 tools
├── Dockerfile            # Container definition
├── catalog.yaml          # Docker MCP gateway config
├── requirements.txt      # Python dependencies
├── infrastructure/db/    # Encryption module
└── README.md             # Documentation
```

**Available Tools:**
| Tool | Description |
|------|-------------|
| `homelab_list_vms` | List all virtual machines |
| `homelab_get_vm` | Get VM details by ID or name |
| `homelab_get_credentials` | Get credentials (AUDIT LOGGED) |
| `homelab_list_services` | List all services |
| `homelab_check_service_health` | Check service health endpoint |
| `homelab_list_hosts` | List Proxmox hosts |
| `homelab_get_host` | Get host details |
| `homelab_lookup_ip` | Look up IP allocation |

**Transport:** SSE (Server-Sent Events) for network access

**Claude Desktop Integration:**
```json
{
  "homelab-infra": {
    "transport": "sse",
    "url": "http://10.0.1.202:8080/sse"
  }
}
```

---

### 4. Infrastructure Database Updates

**Database:** `/home/anthony/ccpm-workspace/HomeLab/infrastructure/homelab.db`

**Current Data:**

| Table | Records |
|-------|---------|
| proxmox_hosts | 1 (homelab-pve @ 10.0.1.200) |
| virtual_machines | 2 (whisper, harbor) |
| credentials | 3 (vm:100, host:1, service:portainer) |
| services | 3+ (portainer, etc.) |

**Sync Command:**
```bash
scp ~/ccpm-workspace/HomeLab/infrastructure/homelab.db ccpm@10.0.1.202:~/data/
ssh ccpm@10.0.1.202 "docker restart homelab-mcp"
```

---

### 5. GitHub Issues Updated

- **Issue #7** - Added resource logging requirement for Whisper TTS
- **Issue #9** - Marked MCP server implementation complete
- **Issue #11** - Created: MCP Server deployment documentation

---

## Proxmox Infrastructure Overview

**Host:** homelab-pve @ 10.0.1.200

| VMID | Name | IP | Purpose | Status |
|------|------|-----|---------|--------|
| 100 | whisper-tts | 10.0.1.201 | TTS Voice Server (GPU) | Running |
| 101 | harbor | 10.0.1.202 | Docker + MCP Services | Running |

---

## Key Access Information

### SSH Access (key-based)
```bash
ssh ccpm@10.0.1.201  # whisper
ssh ccpm@10.0.1.202  # harbor
ssh root@10.0.1.200  # proxmox
```

### tmux Sessions
```bash
ssh ccpm@10.0.1.201 "tmux attach -t whisper"
ssh ccpm@10.0.1.202 "tmux attach -t harbor"
```

### Web UIs
- Proxmox: https://10.0.1.200:8006
- Portainer: https://10.0.1.202:9443

---

## Next Steps / Pending Tasks

### Immediate
1. **Test MCP Server with Claude Desktop** - Add to mcp_servers.json and verify tools work
2. **Backend Designer tasks** - Whisper TTS API implementation (Issue #7)

### Future
- Add more VMs to infrastructure database as created
- Set up database sync automation (cron or on-change)
- Consider adding more services to harbor VM

---

## Sprint Context

**Sprint WSP-S1** tasks were assigned but redirected to Backend Designer:
- FastAPI Core Server Setup
- TTS REST API Endpoints
- Chatterbox TTS Integration
- Agent Identity Database Schema
- CCPM Integration Testing

HomeLab Specialist focus remains on infrastructure, not TTS API development.

---

## Commands Reference

### Docker Management (on harbor)
```bash
# View containers
ssh ccpm@10.0.1.202 "docker ps"

# View MCP logs
ssh ccpm@10.0.1.202 "docker logs homelab-mcp"

# Restart services
ssh ccpm@10.0.1.202 "docker restart homelab-mcp"
ssh ccpm@10.0.1.202 "docker restart portainer"
```

### Database Queries
```bash
# List VMs
sqlite3 ~/ccpm-workspace/HomeLab/infrastructure/homelab.db "SELECT vm_id, name, ip_address FROM virtual_machines"

# Check credentials
sqlite3 ~/ccpm-workspace/HomeLab/infrastructure/homelab.db "SELECT target_type, target_name, username FROM credentials"
```

---

*Session documented by HomeLab Specialist Agent*
