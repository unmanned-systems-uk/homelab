# HomeLab Domains

The HomeLab agent manages 8 infrastructure domains.

---

## 1. Network Management

**Primary:** UniFi ecosystem (UDM Pro at 10.0.1.1)

| Item | Details |
|------|---------|
| Controller | UDM Pro built-in |
| Access | https://10.0.1.1 |
| Credentials | HomeLab-Agent / HomeAdman2350 |
| MCP Endpoint | `https://mcp.unmanned-systems.uk/sse` |
| MCP Host | Harbor VM (10.0.1.202:3001) |

**MCP Tools (81 available):**
- `unifi_list_devices` - List switches, APs
- `unifi_get_clients` - Connected clients
- `unifi_get_networks` - VLANs, subnets
- `unifi_list_firewall_policies` - Firewall rules
- `unifi_get_network_health` - Network status

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
| pve-ai (i9-10940X) | 10.0.1.200 | Active |
| R640 | TBD | Planned |

**VMs:**
| VMID | Name | Purpose |
|------|------|---------|
| 100 | whisper-tts | AI/TTS services |
| 101 | harbor | Docker + MCP services |
| 102 | VM 102 | General |
| 210 | ccpm-v2 | CCPM development |

**GPU Passthrough Ready:**
- GTX 1080 Ti (IOMMU Group 2)
- Quadro K5000 (IOMMU Group 4)

**Tasks:**
- VM architecture planning
- GPU passthrough configuration
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

## 8. HomeGate - Infrastructure Dashboard

**Primary:** Unified homelab command center

| Item | Details |
|------|---------|
| Repository | `unmanned-systems-uk/homegate` |
| Local Path | `/home/homelab/HomeGate` |
| Deployment Host | i3 Mini PC @ 10.0.1.50 |
| Status | Design Complete - Ready for Implementation |

**Core Features:**
- **Persistent SSH Terminal** - Web-based SSH that survives device switching
- **Infrastructure Monitoring** - UniFi, Proxmox, Synology, Home Assistant, SCPI
- **Role-Based Access** - Admin (full control) vs Family (PIN + HA links)
- **Smart Alerting** - Email/SMS for critical infrastructure issues

**Technology Stack:**
| Component | Technology |
|-----------|------------|
| Frontend | React 18 + TypeScript + xterm.js |
| Backend | Node.js 20 + Express + Socket.io |
| Database | PostgreSQL 15+ (existing server) |
| Tunnel | Cloudflare Tunnel (homegate.domain.com) |

**Integration with HomeLab:**
| Integration | Details |
|-------------|---------|
| UniFi MCP | Reuse existing `https://mcp.unmanned-systems.uk/sse` |
| SCPI Monitoring | ICMP/HTTP health checks for 6 instruments |
| Proxmox | Via Pulse API (VMs, containers, resources) |
| Synology NAS | Storage, SMART, Docker status |
| Home Assistant | Smart device count, offline status |
| Portainer | Docker containers (https://10.0.1.202:9443) |
| Ollama/Open WebUI | Local LLM status (https://10.0.1.202:3443) |

**Firewall Rules Required (UDM Pro):**
```
Allow 10.0.1.50 → 10.0.10.0/24  # Management VLAN (switches, APs)
Allow 10.0.1.50 → 10.0.30.0/24  # IoT VLAN (smart home)
Allow 10.0.1.50 → 10.0.50.0/24  # Lab VLAN (SCPI equipment)
```

**Implementation Milestones:**
| Milestone | Issues | Duration |
|-----------|--------|----------|
| 1. Foundation | #1-10 | 2-3 weeks |
| 2. Monitoring | #11-20 | 2-3 weeks |
| 3. SSH Terminal | #21-30 | 2-3 weeks |
| 4. Production | #31-40 | 1-2 weeks |

**Tasks:**
- Implement 40 planned GitHub issues
- Configure cross-VLAN firewall rules
- Deploy to i3 host @ 10.0.1.50
- Integrate with existing UniFi MCP
- Set up Cloudflare Tunnel

---

*See `.claude/skills/` for detailed patterns and procedures*
