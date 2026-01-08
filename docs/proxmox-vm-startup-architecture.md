# Proxmox VM Startup Architecture

**Last Updated:** 2026-01-08
**Proxmox Host:** pve-ai (10.0.1.200)
**Reason:** Configured auto-start after power outage incident

---

## Overview

This document defines the automatic startup configuration for Proxmox VMs to ensure infrastructure services come online automatically after power events or host reboots.

---

## Startup Configuration

### Priority 1: Core Infrastructure

**harbor (VMID 101)** @ 10.0.1.202

```
onboot: 1
startup: order=1,up=30,down=60
```

**Services Provided:**
- Docker container orchestration
- UniFi MCP endpoint (https://mcp.unmanned-systems.uk/sse @ port 3001)
- Portainer (https://10.0.1.202:9443)
- Ollama/Open WebUI (https://10.0.1.202:3443)

**Resources:**
- CPU: 2 cores (host type)
- RAM: 4096 MB
- Disk: 50 GB (local-lvm)

**Rationale:** Harbor provides critical infrastructure services including the UniFi MCP integration used by other systems. Must start first and be fully initialized before dependent services.

---

### Priority 2: Development Tools

**ccpm-v2 (VMID 210)** @ 10.0.1.210

```
onboot: 1
startup: order=2,up=20,down=30
```

**Services Provided:**
- CCPM project management system (http://10.0.1.210:8000)
- CCPM API and database (PostgreSQL @ 10.0.1.251:5433)
- Development environment

**Resources:**
- CPU: 4 cores
- RAM: 8192 MB
- Disk: 40 GB (local-lvm)

**Rationale:** CCPM provides project management and task tracking for HomeLab operations. Starts after core infrastructure but before optional services.

---

### Priority 3: AI/ML Services

**whisper-tts (VMID 100)** @ 10.0.1.201

```
onboot: 1
startup: order=3,up=15,down=20
```

**Services Provided:**
- Whisper AI transcription
- Text-to-speech services
- AI/ML workloads

**Resources:**
- CPU: Host type
- RAM: 16384 MB (16 GB)
- Disk: 100 GB (local-lvm)

**Rationale:** AI services are useful but not critical for infrastructure operations. Starts last to ensure core services have priority during boot.

---

## Manual Start VMs

### VM 102 (VMID 102)

```
onboot: 0 (default)
startup: not configured
```

**Status:** Unknown/unused VM, no services identified
**Resources:** 1 core, 6144 MB RAM, 32 GB disk
**Rationale:** No auto-start configured - purpose unclear

---

### ha-test (VMID 103)

```
onboot: 0 (default)
startup: not configured
```

**Status:** Home Assistant test environment
**Resources:** 2048 MB RAM, 6 GB disk
**Rationale:** Test environment - manual start only

---

## Startup Sequence Timeline

After Proxmox host boot:

```
T+0s    : Proxmox host online
T+0s    : harbor (VMID 101) starts
T+30s   : ccpm-v2 (VMID 210) starts
T+50s   : whisper-tts (VMID 100) starts
T+65s   : All infrastructure services online
```

**Total initialization time:** ~65 seconds from Proxmox boot

---

## Shutdown Sequence

During host shutdown, VMs shut down in reverse order:

```
T+0s    : Shutdown signal received
T+0s    : whisper-tts (VMID 100) shutdown initiated (20s grace)
T+20s   : ccpm-v2 (VMID 210) shutdown initiated (30s grace)
T+50s   : harbor (VMID 101) shutdown initiated (60s grace)
T+110s  : All VMs stopped gracefully
```

**Total graceful shutdown time:** ~110 seconds

---

## Verification Commands

### Check Auto-Start Configuration

```bash
ssh root@10.0.1.200 "qm list"
ssh root@10.0.1.200 "qm config 101 | grep -E '(onboot|startup)'"
ssh root@10.0.1.200 "qm config 210 | grep -E '(onboot|startup)'"
ssh root@10.0.1.200 "qm config 100 | grep -E '(onboot|startup)'"
```

### Verify Services Online

```bash
# harbor services
timeout 3 bash -c "echo > /dev/tcp/10.0.1.202/9443" && echo "Portainer: ONLINE"
timeout 3 bash -c "echo > /dev/tcp/10.0.1.202/3443" && echo "Ollama: ONLINE"
timeout 3 bash -c "echo > /dev/tcp/10.0.1.202/3001" && echo "MCP: ONLINE"

# ccpm-v2 services
timeout 3 bash -c "echo > /dev/tcp/10.0.1.210/8000" && echo "CCPM API: ONLINE"

# Network connectivity
ping -c 1 10.0.1.202 && echo "harbor: UP"
ping -c 1 10.0.1.210 && echo "ccpm-v2: UP"
ping -c 1 10.0.1.201 && echo "whisper-tts: UP"
```

---

## Modifying Auto-Start Configuration

### Enable Auto-Start for a VM

```bash
ssh root@10.0.1.200 "qm set <VMID> -onboot 1 -startup order=<N>,up=<DELAY>,down=<GRACE>"
```

**Parameters:**
- `order`: Startup priority (1 = first, higher numbers start later)
- `up`: Delay in seconds before starting next VM
- `down`: Grace period in seconds for graceful shutdown

### Disable Auto-Start for a VM

```bash
ssh root@10.0.1.200 "qm set <VMID> -onboot 0"
ssh root@10.0.1.200 "qm set <VMID> -delete startup"
```

---

## Service Dependencies

```
harbor (VMID 101)
  ├─ UniFi MCP (port 3001)
  │   └─ Required by: HomeGate, network monitoring
  ├─ Portainer (port 9443)
  │   └─ Required by: Docker container management
  └─ Ollama (port 3443)
      └─ Required by: AI/ML operations

ccpm-v2 (VMID 210)
  └─ CCPM API (port 8000)
      └─ Required by: Task management, session tracking

whisper-tts (VMID 100)
  └─ AI/ML services
      └─ Required by: Optional AI workloads
```

---

## Recovery After Power Event

1. **Automatic:** Proxmox host boots and starts VMs in configured order
2. **Verify:** Check VM status with `qm list`
3. **Verify:** Check service availability (see commands above)
4. **Manual Start (if needed):** `ssh root@10.0.1.200 "qm start <VMID>"`

---

## Related Documentation

- **Hardware Inventory:** `docs/hardware-inventory.md`
- **Server Architecture:** `docs/server-stack-architecture.md`
- **Network Configuration:** `docs/udm-pro-migration-complete.md`

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-08 | Initial configuration after power outage | HomeLab Agent |
| 2026-01-08 | Configured auto-start for VMs 100, 101, 210 | HomeLab Agent |

---

*Configured to ensure infrastructure resilience after power events*
