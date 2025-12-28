# HomeLab Domains

The HomeLab agent manages 7 infrastructure domains.

---

## 1. Network Management

**Primary:** UniFi ecosystem (UDM Pro at 10.0.1.1)

| Item | Details |
|------|---------|
| Controller | UDM Pro built-in |
| Access | https://10.0.1.1 |
| Credentials | admin / USAdman2350!@ |
| MCP | UniFi MCP via `@sirkirby/unifi-network-mcp` |

**MCP Tools:**
- `unifi_list_devices` - List switches, APs
- `unifi_get_clients` - Connected clients
- `unifi_get_networks` - VLANs, subnets

**VLANs:**
| VLAN | Subnet | Purpose |
|------|--------|---------|
| - | 10.0.1.0/24 | Default (SCPI, servers) |
| 10 | 10.0.10.0/24 | Management (switches, APs) |
| 20 | 10.0.20.0/24 | Media |
| 30 | 10.0.30.0/24 | IoT |
| 50 | 10.0.50.0/24 | Lab |

**Tasks:**
- Network topology documentation
- VLAN configuration
- Device inventory
- Troubleshooting connectivity

---

## 2. SCPI Equipment

**Primary:** 6 networked test instruments

| Device | IP | Port | Model |
|--------|-----|------|-------|
| Keithley DMM6500 | 10.0.1.101 | 5025 | 6.5-digit DMM |
| Rigol DL3021A | 10.0.1.105 | 5555 | DC Load |
| Rigol MSO8204 | 10.0.1.106 | 5555 | 2GHz Scope |
| Rigol DP932A | 10.0.1.111 | 5025 | PSU |
| Rigol DG2052 | 10.0.1.120 | 5555 | AWG |
| Rigol DP932A | 10.0.1.138 | 5025 | PSU |

**Quick Check:**
```bash
echo "*IDN?" | nc -w 2 10.0.1.101 5025
```

**Tasks:**
- Equipment discovery and monitoring
- Automated test sequences
- Measurement logging

**SAFETY:** Never enable outputs without user confirmation.

---

## 3. Virtualization

**Primary:** Proxmox VE

| Host | IP | Status |
|------|-----|--------|
| Legacy-i7 | 10.0.1.130 | Active |
| R640 | TBD | Planned |

**Tasks:**
- VM architecture planning
- GPU passthrough (1080 Ti)
- Container deployment
- Backup to NAS (10.0.1.251)

---

## 4. Infrastructure as Code

**Primary:** Docker, Ansible, configuration management

| Tool | Purpose |
|------|---------|
| Docker Compose | Container orchestration |
| Ansible | Host provisioning |
| Git | Version control |

**Tasks:**
- Docker compose files
- Ansible playbooks
- IaC documentation
- Deployment automation

---

## 5. Equipment Inventory

**Primary:** Hardware tracking and documentation

| Document | Purpose |
|----------|---------|
| `docs/hardware-inventory.md` | Master inventory |
| GitHub Issues | Tracking changes |

**Tasks:**
- Maintain inventory documentation
- Track hardware status changes
- Document specifications
- Plan upgrades

---

## 6. AI/ML Operations

**Primary:** GPU workloads, model deployment

| Resource | Details |
|----------|---------|
| GTX 1080 Ti | 11GB VRAM - VM passthrough |
| RTX A2000 | 6GB VRAM - Dev machine |
| Jetson Orin NX | Edge AI (10.0.1.113) |

**Tasks:**
- Model training environments
- GPU passthrough configuration
- Jetson deployment pipelines
- AI service integration (Ollama)

---

## 7. Home Automation

**Primary:** Home Assistant integration (planned)

| Platform | Status |
|----------|--------|
| Home Assistant | Planned |
| HomeSeer | Legacy |

**Tasks:**
- HA container deployment
- Device integration
- Automation scripts

---

*See `.claude/skills/` for detailed patterns and procedures*
