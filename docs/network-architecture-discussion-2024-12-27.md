# Homelab Network Architecture Discussion

**Date:** 2024-12-27  
**Status:** Planning Phase  
**Priority:** Critical Infrastructure Foundation  

---

## Overview

This document captures the strategic planning discussion for rebuilding and cleaning up the homelab network architecture before the system becomes unmanageable.

---

## Current Situation

### Network Infrastructure (End-of-Life Crisis)
- **Gateway:** USG Pro 4 (end-of-life product)
- **Controller:** CloudKey Gen1 v1.1.19 (will be retired)
- **ISP:** Sky Broadband FTTP via Openreach ONT
- **Network:** 10.0.1.x subnet, all Ubiquiti hardware
- **Problem:** Building on sunset hardware - every day of delay makes migration more complex

### IoT Security Issue (Growing Rapidly)
- **20+ Philips Wiz bulbs** on main WiFi (no VLAN segmentation)
- Growing rapidly, already a security nightmare
- Bulbs difficult to reconfigure (manual process per device)
- **Technical debt** - do it now with 20 devices, or later with 50+

### Management Vision
- **Claude Code CLI:** Deep system management and complex setup
- **Local Llama:** Basic system queries (complementary to Claude CLI)
- **HomeGate (Pi 5):** Web landing page/dashboard for homelab navigation (Homer/Dashy/Heimdall)

### Home Automation Strategy
- **Hybrid Approach:** HomeSeer + Home Assistant
- **HA:** Modern UI, massive device support (1300+ integrations)
- **HomeSeer:** Complex automation logic, stability, professional support
- **Integration:** MQTT bridge for bidirectional control
- **Not yet implemented**

---

## Key Questions & Answers

### 1. Where will Claude CLI agent live?
**Answer: Proxmox LXC container (not a Pi)**

**Rationale:**
- Needs reliable uptime, network access, decent I/O
- Pi is underpowered, SD card failure would kill management plane
- Location: VLAN 10 (Management)
- Spec: Ubuntu 24.04 LXC, 2-4 cores, 4-8GB RAM

### 2. Where will Llama agent live?
**Answer: Nvidia Jetson Orin NX OR Proxmox with GPU passthrough**

**Rationale:**
- Needs GPU for acceptable inference speed
- Jetson is power-efficient, purpose-built
- Location: VLAN 10 (Management) or VLAN 50 (Lab)
- Reality check: Will it actually be used, or is it a cool project?

### 3. When do we need HomeGate (Pi 5)?
**Answer: Low priority, repurpose for dashboard/monitoring**

**Clarification:**
- NOT a network gateway (UDM is the gateway)
- Dashboard for navigation (Homer, Dashy, Heimdall)
- Alternative uses: Monitoring (Grafana/Prometheus), Home Assistant host, Pi-hole secondary
- Location: VLAN 10 (Management)

### 4. USG to UDM migration priority?
**Answer: PRIORITY #1 - Do this immediately, before anything else**

**Rationale:**
- Every service/VLAN/automation built on USG = configuration to recreate later
- USG is end-of-life, building on sunset hardware
- UDM has better VLAN management, IDS/IPS, built-in controller
- Eliminates CloudKey dependency
- **DO NOT PASS GO** - this is the foundation

### 5. VLAN timing?
**Answer: PRIORITY #2 - Immediately after UDM migration**

**Status:** Already too late with 20+ IoT devices on main network

**Required VLANs:**
- VLAN 10: Management (Proxmox, UDM, Claude CLI, monitoring)
- VLAN 20: Trusted Devices (workstations, phones)
- VLAN 30: IoT/Home Automation (bulbs, sensors, smart devices)
- VLAN 40: Guest
- VLAN 50: Lab/Experimental (Jetson, test environments)

### 6. Wiz Bulb Migration Strategy?
**Answer: No magic solution - grind through it**

**Options:**
1. **Do it now** with 20 bulbs (2-3 hours of pain)
2. **Do it later** with 50+ bulbs (week of pain)

**Approach:**
- Create IoT SSID on VLAN 30
- Move 5 bulbs at a time
- Test automation after each batch
- Firewall rules: Allow internet + Home Assistant, Deny management/trusted VLANs

---

## Critical Decisions Made

### Migration Strategy: Option C (Parallel Setup)

**User's Innovative Approach:**
```
1. Install UniFi MCP now → Claude gets full network visibility
2. Setup dual Ethernet on dev PC (one to old network, one to new UDM)
3. Claude builds understanding of old system, backup all
4. Research official UniFi migration guidance
5. Setup new UDM on separate ethernet connection
6. Bypass Sky router, direct ONT to UDM connection
7. Test internet connectivity on new network
8. Parallel operation until ready for cutover
```

**Why This is Brilliant:**
- Zero downtime during setup/testing
- Claude can compare old vs new configs in real-time
- Thorough testing before cutover
- Easy rollback (just swap cables back)
- Professional approach for production home network

### Sky Broadband Configuration

**CRITICAL DISCOVERY:** Sky does NOT use PPPoE

**Connection Type:** DHCP with DHCPv4 Option 61 authentication

**WAN Configuration:**
```yaml
Connection Type: DHCP
DHCP Option 61: anything@skydsl|SKY_HUB_MAC_ADDRESS
IPv6: Disabled (due to MAP-T incompatibility)
VLAN: None (Sky FTTP doesn't use VLAN tagging)
```

**Known Issue:** UniFi requests MAP-T (DHCPv6 Option 95) but doesn't support it
**Solution:** Disable IPv6 on WAN OR update to UniFi OS 4.1.13+

---

## Architecture Decisions

### Proposed Network Topology

```
Internet (Sky FTTP)
   │
Openreach ONT
   │
UDM (Unified Dream Machine)
   ├─ WAN (DHCP + Option 61 auth to Sky)
   │
   ├─ VLAN 10: Management (10.0.10.x/24)
   │   ├─ Proxmox management interface
   │   ├─ Claude CLI LXC
   │   ├─ Monitoring stack
   │   └─ HomeGate Pi 5 dashboard
   │
   ├─ VLAN 20: Trusted (10.0.20.x/24)
   │   ├─ Workstations
   │   ├─ Phones
   │   └─ Personal devices
   │
   ├─ VLAN 30: IoT (10.0.30.x/24)
   │   ├─ Wiz bulbs
   │   ├─ Smart sensors
   │   ├─ Home automation devices
   │   └─ Firewall: Internet + HA only
   │
   ├─ VLAN 40: Guest (10.0.40.x/24)
   │   └─ Isolated guest access
   │
   └─ VLAN 50: Lab (10.0.50.x/24)
       ├─ Jetson experiments
       ├─ Test VMs
       └─ Experimental projects
```

### Proxmox Server
- **Host:** Legacy-i7 (i7-7820X, 32GB RAM)
- **GPUs:** GTX 1080 Ti (AI workloads), Quadro P620 (host console)
- **Location:** VLAN 10 (Management)
- **VMs/LXCs:**
  - Claude CLI LXC (Ubuntu 24.04, 2-4 cores, 4-8GB RAM)
  - Home Assistant VM (optional, or run on Pi)
  - Monitoring stack (Grafana, Prometheus)

### Storage
- **Primary NAS:** Synology (~45TB) at 10.0.1.251
- **Backup:** 2x 20TB external drives
- **Proxmox Backup:** To Synology via SMB

---

## Things NOT Recommended (and Why)

❌ **Pi 5 as gateway** - UDM is your gateway, don't split responsibility  
❌ **Rushing into Home Assistant** - Get networking right first  
❌ **Over-engineering with Llama** - Start with Claude CLI, add Llama if clear use case emerges  
❌ **Complex SD-WAN** - Not needed yet, keep it simple  
❌ **Production services on Pis** - Great for learning, terrible for reliability  
❌ **Running everything on USG** - It's EOL, every day makes migration harder  

---

## Implementation Sequence

### Week 1: Foundation (CRITICAL)
1. **Install UniFi MCP** → Claude gets network visibility
2. **Full network audit** → Document everything before touching hardware
3. **Research Sky configuration** → Verify Option 61 auth ✅ DONE
4. **UDM parallel setup** → New network on separate ethernet
5. **Migrate USG → UDM** → 30-60 min family downtime

### Week 2: Segmentation
6. **Create VLANs** on UDM
7. **Create IoT SSID** on VLAN 30
8. **Migrate Wiz bulbs** in batches (5 per day)
9. **Configure inter-VLAN firewall rules**

### Week 3: Management Layer
10. **Create Claude CLI LXC** on Proxmox
11. **Configure SSH access**, install Claude Code
12. **Document infrastructure** in markdown
13. **Setup monitoring** (if time permits)

### Week 4: Optional Enhancements
14. **Jetson + Llama setup** (if needed)
15. **Home Assistant deployment** (HomeSeer hybrid)
16. **Automated backups**
17. **HomeGate dashboard** (Pi 5)

---

## Critical Success Factors

1. **Stop building horizontally** (more devices/services)
2. **Fix foundation first** (network infrastructure)
3. **UDM migration is non-negotiable Priority #1**
4. **VLAN segmentation is Priority #2**
5. **Don't wait** - complexity grows exponentially with time

---

## Brutal Truths Acknowledged

1. **You're not too late, but at the inflection point**
   - 6 months from now with 40+ devices = nightmare migration
   - Technical debt must be paid now

2. **The bulb migration will suck**
   - No sugarcoating: 20 devices, manual process
   - But better now than later

3. **USG migration can't wait**
   - Every day of delay = more configuration to recreate
   - You're already building on a deprecated platform

4. **VLANs should have been done at 5 IoT devices**
   - You're at 20 now, still manageable
   - Don't let it get to 50

---

## Next Immediate Actions

**Priority 1: Setup UniFi MCP (GitHub Issue Created)**
- Install MCP server for network visibility
- Claude needs CloudKey IP + credentials
- Automated network audit before migration

**Priority 2: Obtain Requirements**
- CloudKey IP address
- CloudKey admin credentials
- Sky Hub MAC address (for Option 61)
- Dual ethernet verification on dev PC

**Priority 3: Schedule Migration**
- Coordinate with family for downtime window
- Typically: Evening after work/school
- Expected: 30-60 minutes offline

---

## Key Insights from Discussion

### On Homelab Philosophy
- **Clean architecture now** prevents exponential complexity later
- **Foundation before features** - network before services
- **Technical debt compounds** - pay it down early

### On Family Networks
- **Production environment** requires professional approach
- **Zero-downtime testing** is essential with dependents
- **Rollback plans** are mandatory, not optional
- **Family tolerance** is finite - use it wisely

### On Migration Strategy
- **Parallel setup** beats big-bang migration for home environments
- **Automated documentation** (MCP) prevents manual errors
- **Dual network access** enables real-time comparison
- **Staged approach** reduces risk significantly

---

## Questions for Follow-Up

### Network
- [ ] What is CloudKey IP address?
- [ ] What are CloudKey admin credentials?
- [ ] What is Sky Hub MAC address?
- [ ] Does dev PC have dual ethernet?

### Timing
- [ ] When can family tolerate 30-60 min downtime?
- [ ] What's timeline for obtaining UDM if not owned yet?
- [ ] When does user return to work? (confirmed: 2 days)

### Hardware
- [ ] Which UDM model? (confirmed: UDM Basic, no PoE)
- [ ] How many Wiz bulbs total? (confirmed: 20+, growing)
- [ ] UniFi switches/APs inventory? (need MCP for this)

---

## Documentation Created

1. **usg-to-udm-migration-plan.md** - Complete step-by-step migration guide
2. **This document** - Strategic discussion summary
3. **GitHub Issue** - UniFi MCP setup task (to be created)

---

## Handoff to Homelab Specialist Agent

**Task:** Install and configure UniFi MCP server  
**Prerequisites:** CloudKey IP + admin credentials  
**Deliverable:** Complete automated network audit  
**Timeline:** ASAP - blocks all other work  

See GitHub issue for detailed requirements.

---

**Status:** Planning Complete, Awaiting MCP Setup  
**Next Review:** After network audit complete  
**Migration Target:** Within 3 days of receiving UDM hardware
