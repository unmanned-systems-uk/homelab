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

---

## Troubleshooting

### UniFi Port Configuration for Network Stability (LEARNED: 2026-01-10)

**Context:** HA Pi causing recurring network failures (Issue #36). HA Pi restarts triggered STP topology changes causing US 48 uplink port to enter blocking state. Medical-critical system (Nathan diabetes monitoring).

**Problem Pattern:**
- Device restart → MAC address flush → STP recalculation
- Uplink port enters blocking state
- Requires physical cable replug to restore
- **Only occurred during HA Pi backend work (service restarts)**

**Solution - UniFi Port Settings:**

**For Uplink Ports (switch-to-switch):**
```
Advanced → Manual
Link Speed: 1Gbps FDX (forced - disable auto-negotiate)

Storm Control: ☑ Enable
  ☑ Broadcast:  100 kpps (UI enforced minimum)
  ☑ Multicast:  100 kpps (tight) or 200 kpps (permissive)
  ☑ Unicast:    1000 kpps (67% of 1G link capacity)

Loop Protection: ☑ Enable
Spanning Tree Protocol: ☑ Enable
```

**For Edge Device Ports (server/device connections):**
```
Storm Control: ☑ Enable
  ☑ Broadcast:  100 kpps
  ☑ Multicast:  100 kpps (or 200 kpps for discovery-heavy devices)
  ☑ Unicast:    1000 kpps

Port Isolation: ☐ Disable (unless isolating device)
```

**UniFi UI Notes:**
- Storm Control thresholds are in **pKts/s** (kilo packets per second)
- 100 kpps = 100,000 packets/second
- **Loop Protection = STP Edge Port / PortFast** (UniFi terminology)
- Link Speed shows as "1Gbps FDX" when forced (not "Auto")

**Why This Works:**
- **Forced Link Speed:** Eliminates auto-negotiation timeout issues
- **Storm Control:** Limits broadcast/multicast/unicast floods that trigger port protection
- **Loop Protection:** Port bypasses STP recalculation (immediate forwarding state)
- **STP Still Enabled:** Network-wide loop prevention remains active

**Threshold Calculations (for 1Gbps link):**
```
Max theoretical: ~1,488,000 pps (64-byte packets)

Broadcast:  100 kpps = 6.7% of max
Multicast:  100 kpps = 6.7% of max (or 200 = 13.4%)
Unicast:    1000 kpps = 67% of max

Conservative for medical-critical systems
```

**When to Use:**
- Medical or life-safety critical infrastructure
- Devices with aggressive service discovery (mDNS, Avahi, SSDP)
- After experiencing network drops correlated with device restarts
- Uplink ports in daisy-chained switch topology
- Any port where STP blocking causes outages

**When NOT to Use:**
- Ports that actually need STP protection (redundant uplinks creating loops)
- Ports where you want loop detection (test/lab environments)

**Verification:**
```bash
# Test device restart doesn't drop network
ping -c 100 [device-ip]
ssh [device] "sudo reboot"
# Monitor ping - should show 0% loss

# Check UniFi Events
UniFi Controller → Events → Filter: "Port" and "STP"
# Should NOT see topology change events
```

**Related:**
- Issue #36: HA Pi Network Failure
- docs/ha-pi-network-fix-unifi-config.md
- docs/session-summary-2026-01-10.md
- Network: US 48 Port 14 → US 24 Port 2 → HA Pi (10.0.1.150)

**Permanent Fix:** Upgrade copper uplink to fiber SFP+ (eliminates electrical/ground loop issues)

---

### Fiber vs Copper Uplinks for Critical Systems

**When to Use Fiber:**
- Medical/life-safety critical infrastructure
- Experiencing electrical interference issues
- Long runs (>100m eventually)
- 10Gbps future-proofing desired
- Ground loop isolation needed

**Components (1Gbps or 10Gbps):**
```
2x SFP/SFP+ modules:
  - 1G: 1000Base-SX (850nm, LC, MMF)
  - 10G: 10GBase-SR (850nm, LC, MMF)

1x Fiber cable:
  - LC-LC duplex
  - OM3 (300m @ 10G) or OM4 (400m @ 10G)
  - Aqua jacket = multimode
```

**Cost:** ~£50-85 for complete 10G upgrade

**Benefits over Copper:**
- Galvanic isolation (no electrical connection)
- Immune to EMI/RFI interference
- No auto-negotiation issues (fixed speed)
- Higher reliability for critical systems
