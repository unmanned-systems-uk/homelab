# HomeLab Session Summary - 2025-12-13

**Director:** CCPM-Director (Claude Opus 4.5)
**Focus:** New Project Setup - HomeLab
**Duration:** Extended session

---

## Project Created

| Item | Value |
|------|-------|
| **Project Name** | HomeLab |
| **CCPM Project ID** | 5 |
| **GitHub Repo** | https://github.com/unmanned-systems-uk/homelab |
| **Sprint** | HomeLab Sprint 1 - Foundation (ID: 32) |
| **Working Directory** | `/home/anthony/ccpm-workspace/HomeLab` |

---

## Documents Created

| Document | Purpose | Lines |
|----------|---------|-------|
| `docs/hardware-inventory.md` | Full equipment catalogue | 200+ |
| `docs/server-stack-architecture.md` | Proxmox/VM architecture | 174 |
| `docs/unifi-mcp-integration.md` | UniFi MCP setup plan | ~100 |
| `docs/learning-hub.md` | AI/ML learning resources | 393 |
| `CLAUDE.md` | Agent instructions | ~50 |
| `README.md` | Project overview | ~20 |

---

## Hardware Documented

### Compute
| System | Status |
|--------|--------|
| DEV-PC-Ubuntu | i7-10700, 32GB, RTX A2000, 1TB NVMe - Active |
| Legacy-i7 | Powered up, **Quadro K5000 DEAD**, needs basic GPU for SSH |
| PowerEdge R640 | 10SFF 1U, specs TBD when accessible |
| Raspberry Pi 5 x3 | DPM-Air (10.0.1.53), 2x SDR testing |
| Jetson Orin NX | 10.0.1.113, AI/ML dev |

### Test Equipment (SCPI Auto-Discovered)
| Device | IP | Model |
|--------|-----|-------|
| DMM | 10.0.1.101 | Keithley DMM6500 (6.5-digit) |
| Oscilloscope | 10.0.1.106 | Rigol MSO8204 (2GHz 8-ch) |
| Signal Gen | 10.0.1.120 | Rigol DG2052 (50MHz AWG) |
| DC Load | 10.0.1.105 | Rigol DL3021A (200W) |
| PSU | 10.0.1.111 | Rigol DP932A |
| PSU | 10.0.1.138 | Rigol DP932A |

### Networking
- **Current:** USG-Pro-4 + CloudKey v1.1.19
- **Future:** Dream Machine (migration pending)
- **Ecosystem:** Ubiquiti UniFi throughout

### Storage
- Synology NAS (active)
- QNAP ~24TB (offline, needs rebuild)
- 2x 20TB external backup drives

### Dev Boards
- STM32F769I-DISCO + many Nucleos
- ESP32: WROOM, S2, S3, CAMs
- MikroE ecosystem: EasyPIC PRO v7a, Fusion for PIC/PIC32/ARM, UNI-DS v8, HMI displays, **lots of Click boards**

### SDR
- HackRF One, HackRF Pro
- 2x Nooelec NESDR Smart
- Opera Cake (antenna switcher)
- Filters: SAWbird+ ADS-B, Lana WB, FM, AM
- Ham It Up v2 (HF upconverter)

---

## Server Stack Architecture (Planned)

```
┌──────────────────────────────────────────────────┐
│              PowerEdge R640 (Bare Metal)         │
├──────────────────────────────────────────────────┤
│              Proxmox VE (Hypervisor)             │
│                    ↑                             │
│              Pulse (Monitoring UI)               │
├────────────┬────────────┬────────────────────────┤
│   VM:      │   VM:      │   LXC:                 │
│  Home Asst │  Docker    │   Pulse                │
│   (HAOS)   │   Host     │   Dashboard            │
│            │     ↓      │                        │
│            │ Portainer  │                        │
│            │ MCP Servers│                        │
│            │ n8n        │                        │
│            │ Chatterbox │                        │
└────────────┴────────────┴────────────────────────┘
```

---

## Key Technologies Discussed

| Technology | Purpose | Link |
|------------|---------|------|
| **Proxmox VE** | Hypervisor | https://www.proxmox.com/ |
| **Pulse** | Proxmox monitoring | https://github.com/rcourtman/Pulse |
| **Portainer** | Docker management | https://www.portainer.io/ |
| **n8n** | Workflow automation | https://github.com/n8n-io/n8n |
| **Chatterbox** | TTS with voice cloning | https://github.com/resemble-ai/chatterbox |
| **UniFi MCP** | Network integration | https://github.com/sirkirby/unifi-network-mcp |

---

## GPU Discussion Summary

### Dead GPU
- **Quadro K5000** in Legacy-i7 is **dead** - needs replacement for basic display/SSH

### AI GPU Recommendation
- **Best value:** Used RTX 3090 (24GB) @ £300-400
- **Break-even vs cloud:** ~700 hours (~29 days)
- **Hybrid approach:** Local GPU for experiments + cloud for big training

### Jetson vs Desktop
| Aspect | Jetson Orin NX | RTX 3090 |
|--------|----------------|----------|
| CUDA Cores | 1024 | 10496 |
| VRAM | 8-16GB unified | 24GB dedicated |
| Power | 15-25W | 350W |
| Best for | Edge inference | Training |

### Chatterbox Requirements
- Inference: 6-7GB VRAM
- Fine-tuning (LoRA): 18GB+ VRAM

---

## CCPM Tasks Created

| ID | Title | Status |
|----|-------|--------|
| 909 | Implement Equipment Inventory Database | **Completed** |

## GitHub Issues Created

| # | Title | Repo |
|---|-------|------|
| 1 | Implement Equipment Inventory Database | unmanned-systems-uk/homelab |

---

## Pending Items

| Task | Priority |
|------|----------|
| Power up R640 and document config | When accessible |
| Setup UniFi MCP server | High |
| Get basic GPU for Legacy-i7 (SSH access) | Medium |
| Rebuild QNAP NAS | Low |
| Build SCPI test automation | Future |
| Acquire RTX 3090 for AI workloads | When ready |

---

## Network Scan Results (52 devices on 10.0.1.x)

Key IPs discovered:
- 10.0.1.1 - Gateway
- 10.0.1.53 - Pi5 (DPM-Air)
- 10.0.1.92 - Android H16 (DPM Ground)
- 10.0.1.101 - Keithley DMM
- 10.0.1.105 - Rigol DC Load
- 10.0.1.106 - Rigol Oscilloscope
- 10.0.1.111 - Rigol PSU
- 10.0.1.113 - Jetson Orin NX
- 10.0.1.120 - Rigol Signal Gen
- 10.0.1.138 - Rigol PSU

---

## Next Session Considerations

User wants to explore **server-side implementations** that may influence design:
- Alternative hypervisor options?
- Container orchestration (K3s, Docker Swarm)?
- Storage solutions?
- AI serving platforms?

**Note:** Legacy-i7 is powered on but needs a basic GPU for display output to enable SSH setup.

---

## Quick Resume Commands

```bash
# Check HomeLab project
curl -s http://localhost:8080/api/projects/5 | jq .

# Check sprint
curl -s "http://localhost:8080/api/sprints?project_id=5" | jq .

# Working directory
cd /home/anthony/ccpm-workspace/HomeLab

# GitHub repo
gh repo view unmanned-systems-uk/homelab --web
```

---

*Session ended: 2025-12-13*
*Context at close: 78% (157k/200k tokens)*
