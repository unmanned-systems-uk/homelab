# HomeLab Server Stack Architecture

**Status:** Planning
**Last Updated:** 2025-12-13

---

## Target Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    PowerEdge R640 (Bare Metal)               │
│                    8x SFF drives, Xeon, TBD RAM              │
├──────────────────────────────────────────────────────────────┤
│                      Proxmox VE (Hypervisor)                 │
│                           ↑                                  │
│                    Pulse (Monitoring UI)                     │
├────────────────┬─────────────────┬───────────────────────────┤
│     VM:        │      VM:        │     LXC:                  │
│   Home Asst    │   Docker Host   │    Pulse                  │
│    (HAOS)      │    (Debian)     │   Dashboard               │
│                │       ↓         │                           │
│  Smart home    │   Portainer     │  Real-time                │
│  automation    │   MCP Servers   │  metrics                  │
│                │   AI Services   │                           │
│                │   Chatterbox    │                           │
└────────────────┴─────────────────┴───────────────────────────┘
```

---

## Components

### Layer 1: Hypervisor

| Component | Technology | Purpose |
|-----------|------------|---------|
| Hypervisor | **Proxmox VE** | VM and LXC container management |
| Storage | ZFS (on R640 drives) | Snapshots, compression, redundancy |
| Networking | VLANs via Ubiquiti | Segmentation |

### Layer 2: Monitoring

| Component | Technology | Purpose |
|-----------|------------|---------|
| Dashboard | **Pulse** | Real-time Proxmox/Docker monitoring |
| Deployment | LXC container | Lightweight (1 vCPU, 1GB RAM) |
| Port | 7655 | Web UI access |
| Repo | [rcourtman/Pulse](https://github.com/rcourtman/Pulse) | |

### Layer 3: Virtual Machines

| VM | OS | Purpose | Resources |
|----|-----|---------|-----------|
| Home Assistant | HAOS | Smart home automation | 2 vCPU, 4GB RAM |
| Docker Host | Debian 12 | Container workloads | 4+ vCPU, 8-16GB RAM |
| Dev/Test | Ubuntu 24.04 | Development environment | As needed |

### Layer 4: Containers (on Docker Host)

| Container | Purpose | Notes |
|-----------|---------|-------|
| **Portainer** | Docker management UI | Web-based container management |
| **MCP Servers** | Claude integrations | UniFi, SCPI, custom MCPs |
| **Chatterbox** | TTS AI service | Voice synthesis |
| *Future AI services* | Model inference/training | GPU passthrough required |

---

## Network Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    Ubiquiti Network                          │
├─────────────────────────────────────────────────────────────┤
│  Current: USG-Pro-4 + CloudKey v1.1.19                      │
│  Future:  Dream Machine (all-in-one)                        │
├─────────────────────────────────────────────────────────────┤
│  VLANs (planned):                                           │
│  - Management VLAN (Proxmox, switches, APs)                 │
│  - Server VLAN (VMs, containers)                            │
│  - IoT VLAN (Home Assistant devices)                        │
│  - Lab VLAN (SCPI equipment, dev boards)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## GPU Strategy for AI Workloads

### Requirements Analysis

| Use Case | VRAM Needed | Notes |
|----------|-------------|-------|
| Chatterbox TTS inference | 6-7GB | RTX A2000 may work |
| Chatterbox fine-tuning (LoRA) | 18GB+ | Needs bigger GPU |
| Custom model training (< 1B) | 12GB | |
| Custom model training (1-7B) | 24GB+ | |
| Fine-tuning 7B models | 24-48GB | QLoRA helps reduce |

### GPU Options (Used Market)

| GPU | Type | VRAM | Price (Used) | Best For |
|-----|------|------|--------------|----------|
| RTX 3090 | Gaming | 24GB | £300-400 | Best value, training up to 3B |
| RTX 3090 Ti | Gaming | 24GB | £450-550 | Slightly faster |
| RTX 4090 | Gaming | 24GB | £1400-1600 | Performance |
| RTX A5000 | Workstation | 24GB | £900-1100 | Blower cooling (rack-friendly) |
| RTX A6000 | Workstation | 48GB | £2500-3500 | Large models |

### Buy vs Rent Analysis

| GPU | Buy Price | Cloud Equiv | Break-Even |
|-----|-----------|-------------|------------|
| RTX 3090 | £350 | £0.50/hr | ~700 hours (~29 days 24/7) |
| RTX A6000 | £3000 | £1.50/hr | ~2000 hours (~83 days 24/7) |

### Recommendation

**Hybrid approach:**
- Buy **RTX 3090** (£350) for local experiments and inference
- Rent **cloud A100/H100** for large training runs when needed

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Power up R640, document specs
- [ ] Install Proxmox VE
- [ ] Configure ZFS storage pool
- [ ] Setup basic networking

### Phase 2: Core Services
- [ ] Deploy Pulse LXC for monitoring
- [ ] Create Docker Host VM
- [ ] Install Portainer
- [ ] Migrate Home Assistant to VM

### Phase 3: AI Infrastructure
- [ ] Acquire GPU (RTX 3090 recommended)
- [ ] Configure GPU passthrough to Docker VM
- [ ] Deploy Chatterbox TTS
- [ ] Setup MCP servers

### Phase 4: Integration
- [ ] Setup UniFi MCP for network visibility
- [ ] Setup SCPI MCP for test equipment control
- [ ] Configure VLANs
- [ ] Dream Machine migration

---

## Key Resources

| Resource | URL |
|----------|-----|
| Proxmox VE | https://www.proxmox.com/en/proxmox-ve |
| Pulse | https://github.com/rcourtman/Pulse |
| Portainer | https://www.portainer.io/ |
| Chatterbox TTS | https://github.com/resemble-ai/chatterbox |
| Home Assistant | https://www.home-assistant.io/ |

---

## Notes

- R640 is 1U - GPU options limited by space/power unless using external GPU chassis
- Consider dedicated AI workstation if heavy GPU workloads needed
- MCP servers enable Claude to interact with infrastructure

---

*Document created during HomeLab planning session 2025-12-13*
