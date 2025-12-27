# USG Pro 4 to UDM Migration Plan

**Status:** Planning  
**Priority:** CRITICAL - Foundation for all homelab work  
**Timeline:** 2-3 days (staged approach)  
**Project ID:** 5  

---

## Executive Summary

Migrate from end-of-life USG Pro 4 + CloudKey Gen1 to UniFi Dream Machine (UDM Basic) using parallel network setup with zero-downtime testing before final cutover.

**Critical Discovery:** Sky Broadband uses DHCP with Option 61 authentication, NOT PPPoE.

---

## Hardware

### Current Setup
- **Gateway:** USG Pro 4 (end-of-life)
- **Controller:** CloudKey Gen1 v1.1.19
- **Network:** 10.0.1.x subnet
- **ISP:** Sky Broadband FTTP via Openreach ONT
- **Switches:** Multiple UniFi (need enumeration via MCP)
- **APs:** Multiple UniFi (need enumeration via MCP)

### Target Setup
- **Gateway:** UDM Basic (no PoE)
- **Controller:** Built-in to UDM
- **Network:** 10.0.1.x subnet (maintain)
- **ISP:** Direct ONT → UDM connection

---

## Migration Strategy: Option C (Parallel Setup)

### Why This Approach?

✅ **Zero downtime during setup phase**  
✅ **Full testing before cutover**  
✅ **Automated documentation via UniFi MCP**  
✅ **Easy rollback** (just swap cables back)  
✅ **Family network remains stable**  
✅ **Professional approach for production environment**  

### Key Innovation: Dual Ethernet Setup

```
Current Network (10.0.1.x)          New Network (192.168.1.x temp)
        │                                    │
        │                                    │
   ┌────▼────┐                          ┌───▼────┐
   │ USG Pro │                          │  UDM   │
   │   + CK  │                          │ Basic  │
   └────┬────┘                          └───┬────┘
        │                                    │
        │         ┌──────────────┐          │
        └─────────┤  Dev PC      ├──────────┘
                  │  (2x NIC)    │
                  └──────────────┘
                  
Dev PC can access BOTH networks simultaneously
Claude can compare/verify configs in real-time
```

---

## Sky Broadband WAN Configuration

### Critical Information

**Sky Broadband DOES NOT use PPPoE**  
**Connection Type:** DHCP with DHCPv4 Option 61 authentication

### WAN Settings for UDM

```yaml
WAN Configuration:
  Connection Type: DHCP
  DHCP Option 61: anything@skydsl|XX:XX:XX:XX:XX:XX
    (where XX:XX:XX:XX:XX:XX is Sky Hub MAC address)
  IPv6: Disabled (due to MAP-T incompatibility)
  VLAN: None (Sky FTTP doesn't use VLAN tagging)
```

### Known Issue: MAP-T Incompatibility

**Problem:** UniFi requests MAP-T (DHCPv6 Option 95) but doesn't support it  
**Symptom:** Connection works initially, then drops after 12-24 hours  
**Solution:** Disable IPv6 on WAN interface  
**Alternative:** Update to UniFi OS 4.1.13+ (reportedly fixes issue)

### Connection Process

1. **Physical:** Openreach ONT → UDM WAN port (RJ45 ethernet)
2. **Auto-Config:** UDM DHCP request with Option 61
3. **Sky Auth:** Sky validates Option 61 string
4. **IP Assignment:** Sky assigns public IPv4 (likely CGNAT)
5. **Internet:** Working connection

### Troubleshooting

If connection fails:
- Verify Option 61 string format: `anything@skydsl|MAC`
- Use Sky Hub MAC address (find on label or in Sky Hub admin)
- Disable IPv6 entirely on WAN
- Power cycle ONT (leave off 2+ hours to clear session)
- Contact Sky to opt-out of IPv4 sharing (if needed)

---

## Phase 0: Pre-Migration (Tonight/Tomorrow)

### Task 1: Install UniFi MCP Server

**Purpose:** Give Claude full network visibility for automated documentation

**Setup:**
```json
{
  "mcpServers": {
    "unifi": {
      "command": "npx",
      "args": ["-y", "@sirkirby/unifi-network-mcp"],
      "env": {
        "UNIFI_HOST": "https://CLOUDKEY_IP:8443",
        "UNIFI_USERNAME": "admin_username",
        "UNIFI_PASSWORD": "admin_password",
        "UNIFI_SITE": "default"
      }
    }
  }
}
```

**Deliverables:**
- [ ] Complete network device inventory
- [ ] Current DHCP reservations list
- [ ] Firewall rules export
- [ ] Port forward configurations
- [ ] WiFi SSID settings (names, passwords, security)
- [ ] VLAN configuration (if any)
- [ ] Current network topology diagram

### Task 2: Sky Broadband Preparation

- [ ] Get Sky Hub MAC address (needed for Option 61)
- [ ] Document current WAN settings from USG
- [ ] Verify Openreach ONT location and accessibility
- [ ] Check ONT has multiple ethernet ports (or plan cable swap)

### Task 3: Dual Ethernet Verification

- [ ] Confirm Dev PC has 2x Ethernet ports OR
- [ ] Obtain USB Ethernet adapter (if needed)
- [ ] Test dual NIC configuration on different subnets

### Task 4: Backup Current Configuration

- [ ] Export USG configuration via CloudKey
- [ ] Screenshot all custom settings
- [ ] Document any non-standard configurations
- [ ] Export network device list from CloudKey

**Completion Criteria:** Claude has full network visibility via MCP + all configs documented

---

## Phase 1: Parallel UDM Setup (Day 1 - No Downtime)

**Duration:** 2-3 hours  
**Family Impact:** NONE (old network stays online)

### Step 1.1: Physical UDM Setup

```
Openreach ONT ────┬──► USG Pro (current, 10.0.1.x)
                  │
                  └──► UDM Basic (new, 192.168.1.x temp)
```

**Actions:**
- [ ] Unbox UDM
- [ ] Connect UDM WAN port to ONT (if ONT has 2 ports) OR
- [ ] Use ethernet switch on ONT output (temporary)
- [ ] Power on UDM
- [ ] Connect PC NIC #2 to UDM LAN port

### Step 1.2: Initial UDM Configuration

**Access:** Via UDM's default WiFi or direct ethernet (192.168.1.1)

- [ ] Run initial setup wizard
- [ ] Create admin account
- [ ] **IMPORTANT:** Use DIFFERENT subnet than current (192.168.1.x)
- [ ] Configure WAN for Sky Broadband (see WAN config above)
- [ ] Test internet connectivity on UDM
- [ ] Update UDM to latest firmware

### Step 1.3: Sky WAN Configuration

```
WAN Settings:
├── IPv4 Connection: DHCP
├── DHCP Option 61: anything@skydsl|SKY_HUB_MAC
├── DNS: Auto (or 1.1.1.1, 8.8.8.8)
├── IPv6: Disabled
└── VLAN ID: None
```

**Verification:**
```bash
# From UDM shell or network settings
# Should show public IP (not 0.0.0.0)
# Should have internet connectivity
```

### Step 1.4: Migrate Settings to UDM

Using Claude + MCP data:
- [ ] Create networks matching current 10.0.1.x (but on 192.168.1.x for now)
- [ ] Import WiFi SSID settings (DIFFERENT name for now: "HomeWiFi-NEW")
- [ ] Migrate DHCP reservations
- [ ] Replicate firewall rules
- [ ] Copy port forward rules
- [ ] Configure VLANs (prepare but don't enforce yet)

### Step 1.5: Test New UDM Network

**Test Devices:**
- [ ] Connect laptop to "HomeWiFi-NEW"
- [ ] Verify internet access
- [ ] Test DNS resolution
- [ ] Access NAS (10.0.1.251) - WILL FAIL (different subnet)
- [ ] Test critical services

**Expected Results:**
- Internet: ✅ Working
- Local devices: ❌ Not reachable (different subnet - expected)

**Completion Criteria:** UDM functional, internet working, settings migrated

---

## Phase 2: Dual Network Testing (Day 1 Evening - No Downtime)

**Duration:** 1-2 hours  
**Family Impact:** NONE

### Step 2.1: Dual Ethernet Configuration

**Dev PC Network Setup:**
```
NIC 1 (eth0): 10.0.1.x via DHCP → Old USG network
NIC 2 (eth1): 192.168.1.x via DHCP → New UDM network
```

**Verification:**
```bash
# Linux
ip addr show
ping -I eth0 10.0.1.1  # Old USG
ping -I eth1 192.168.1.1  # New UDM

# Windows
ipconfig /all
# Should see both NICs with different IPs
```

### Step 2.2: Side-by-Side Comparison

Using Claude:
- [ ] Compare firewall rules (old vs new)
- [ ] Verify DHCP scopes match
- [ ] Check WiFi settings identical
- [ ] Confirm port forwards migrated
- [ ] Review any custom configs

### Step 2.3: Configuration Refinement

Fix any discrepancies found:
- [ ] Update UDM settings to match USG exactly
- [ ] Add any missing custom configurations
- [ ] Test edge cases (VPN, port forwards, etc.)

**Completion Criteria:** UDM configuration verified matching USG

---

## Phase 3: Cutover Preparation (Day 2 Morning)

**Duration:** 1 hour  
**Family Impact:** NONE (still planning)

### Step 3.1: Final Checklist

**Network Readiness:**
- [ ] UDM internet confirmed working
- [ ] All settings verified migrated
- [ ] WiFi SSID renamed to match current: "YourHomeWiFi"
- [ ] WiFi password matches exactly
- [ ] DHCP range matches: 10.0.1.x/24
- [ ] Static IPs/reservations configured
- [ ] Firewall rules active
- [ ] Port forwards tested

**Rollback Plan:**
- [ ] Document exact cable configuration
- [ ] Have USG/CloudKey ready to power on
- [ ] Know exact time required to rollback (est: 5 min)

### Step 3.2: Family Coordination

- [ ] Announce maintenance window
- [ ] Confirm time works for family (suggest: evening after work/school)
- [ ] Expected downtime: 30 minutes
- [ ] Backup plan: Mobile hotspot if extended

### Step 3.3: Switch Adoption Plan

**If UniFi switches/APs need adoption:**
- [ ] Review adoption process for each device type
- [ ] Prepare SSH commands for manual adoption (if needed)
- [ ] Have UniFi adoption scripts ready

**Completion Criteria:** Go/No-Go decision made, family notified

---

## Phase 4: THE CUTOVER (Day 2 Evening - 30-60 min Downtime)

**⚠️ CRITICAL PHASE - FAMILY NETWORK DOWN ⚠️**

### Pre-Cutover Checklist (T-15 minutes)

- [ ] All family members notified
- [ ] Non-critical devices powered down
- [ ] Rollback plan reviewed
- [ ] Tools ready (cables, labels, etc.)

### Cutover Sequence

#### T-0:00 - Announce Downtime
```
"Network maintenance starting now. 
Expected downtime: 30 minutes. 
Do not reboot devices."
```

#### T-0:02 - Shutdown Old Network
```
Power down sequence:
1. CloudKey Gen1
2. USG Pro 4
3. Wait 30 seconds (let network settle)
```

#### T-0:05 - UDM Network Reconfiguration

**CRITICAL:** Change UDM from temp subnet to production subnet

```
UDM Network Settings:
├── LAN Network: Change from 192.168.1.0/24 → 10.0.1.0/24
├── Gateway IP: 10.0.1.1
├── DHCP Range: 10.0.1.100 - 10.0.1.254
├── DNS: 10.0.1.1 (UDM) or external
└── Apply & Restart Network
```

**This will disconnect your PC - EXPECTED**

#### T-0:10 - Physical Cable Swap

**Disconnect from ONT:**
```
OLD: ONT ──► USG Pro WAN
NEW: ONT ──► UDM WAN (already connected if dual-port ONT)
```

**Connect to Switch Stack:**
```
OLD: USG Pro LAN ──► Main Switch
NEW: UDM LAN ──► Main Switch
```

**Label cables** before disconnecting (prevents confusion)

#### T-0:15 - Power Up New Network

```
Power up sequence:
1. UDM Basic (if powered down)
2. Wait for boot (2-3 minutes)
3. Check UDM status lights
4. Power up switches
5. Power up APs
6. Wait for adoption (3-5 minutes)
```

#### T-0:20 - Device Adoption

**UniFi devices should auto-adopt to new controller**

If devices don't adopt:
```bash
# SSH to switch/AP
ssh ubnt@DEVICE_IP
# Run adoption command
set-inform http://10.0.1.1:8080/inform
```

#### T-0:25 - Verification & Testing

**Critical Tests:**
- [ ] PC reconnects to WiFi automatically
- [ ] Internet access working
- [ ] DNS resolution functional
- [ ] NAS accessible (10.0.1.251)
- [ ] Proxmox accessible (10.0.1.130)
- [ ] Test from mobile device
- [ ] Test from family member device

**Wiz Bulb Check:**
- [ ] Bulbs reconnected automatically (same SSID/password)
- [ ] Home Assistant can control bulbs
- [ ] No manual reconfiguration needed

#### T-0:30 - Network Open

```
"Network maintenance complete.
All devices should reconnect automatically.
Report any issues immediately."
```

### Post-Cutover Monitoring (2-4 hours)

- [ ] Monitor UDM dashboard for anomalies
- [ ] Check all critical services operational
- [ ] Verify no devices stuck offline
- [ ] Test edge cases (VPN, port forwards, remote access)
- [ ] Document any issues encountered

**Success Criteria:**
- All devices online
- Internet working
- No family complaints
- Wiz bulbs functional
- NAS/Proxmox accessible

---

## Phase 5: Post-Migration Cleanup (Day 3+)

### Immediate Tasks (Day 3)

- [ ] Verify 24-hour stability
- [ ] Check UDM logs for errors
- [ ] Confirm all devices adopted
- [ ] Test any untested services

### Week 1 Tasks

- [ ] Monitor for MAP-T issues (connection drops)
- [ ] Document any quirks or fixes required
- [ ] Update homelab documentation
- [ ] Retire CloudKey Gen1 (power down, archive)
- [ ] Retire USG Pro 4 (keep as spare or sell)

### Week 2: VLAN Implementation (Separate Phase)

**DO NOT rush VLANs immediately after migration**

Wait until network is stable (7+ days), then:
- [ ] Plan VLAN strategy (see VLAN Migration Plan)
- [ ] Move IoT devices to VLAN 30 (5 bulbs at a time)
- [ ] Configure inter-VLAN firewall rules
- [ ] Move management to VLAN 10
- [ ] Move trusted devices to VLAN 20

---

## Rollback Procedures

### If Cutover Fails (Within 30 minutes)

**IMMEDIATE ROLLBACK:**
1. Power down UDM
2. Power up USG Pro 4
3. Power up CloudKey Gen1
4. Wait 5 minutes for network to stabilize
5. Reconnect old cables (USG to switch stack)
6. Verify internet working
7. **Estimated rollback time: 5-10 minutes**

### If Issues Discovered Later (Hours/Days)

**Staged Rollback:**
1. Keep both networks running in parallel again
2. Move critical devices back to old network
3. Troubleshoot new network offline
4. Re-attempt cutover when fixed

---

## Risk Assessment

### HIGH RISK
❌ **Sky WAN connectivity failure**  
   - Mitigation: Test thoroughly in Phase 1, have Sky support number ready
   - Rollback: Use Sky Hub temporarily if UDM fails

❌ **Switch/AP adoption failure**  
   - Mitigation: Have manual adoption commands ready
   - Rollback: Devices will re-adopt to old controller if powered back on

### MEDIUM RISK
⚠️ **DHCP conflicts during transition**  
   - Mitigation: Use different subnet during parallel setup
   - Rollback: Power cycle devices to clear old DHCP leases

⚠️ **Family device compatibility issues**  
   - Mitigation: Test with multiple device types in Phase 1
   - Rollback: Revert to old network immediately

### LOW RISK
✓ **Wiz bulbs fail to reconnect**  
   - Mitigation: Same SSID/password = auto-reconnect
   - Fallback: Manual reconfiguration if needed (but shouldn't be)

---

## Critical Success Factors

1. **UniFi MCP operational BEFORE starting** (full network visibility)
2. **Sky WAN config tested and working** (Phase 1)
3. **Dual ethernet testing successful** (Phase 2)
4. **Family coordination and timing** (Phase 4)
5. **Rollback plan tested and ready** (Always)

---

## Tools & Resources

### Required Tools
- [ ] 2x Ethernet cables (spares)
- [ ] Cable labels
- [ ] USB Ethernet adapter (if needed)
- [ ] Mobile hotspot (backup internet)
- [ ] Notepad for manual documentation

### Documentation
- [ ] Current network topology (from MCP)
- [ ] Device inventory (from MCP)
- [ ] Firewall rules export
- [ ] DHCP reservations list
- [ ] WiFi settings (SSIDs, passwords)

### Reference Links
- Sky + UniFi Setup: https://helpforum.sky.com/t5/Broadband/Sky-Broadband-with-Ubiquiti-Unifi-Dream-Machine-Pro/td-p/4514120
- UniFi Setup Guide: https://help.ui.com/hc/en-us/articles/4416276882327-How-to-Set-Up-UniFi
- MAP-T Issue Thread: https://helpforum.sky.com/t5/Broadband/Sky-Fibre-amp-Unifi-Dream-Machine/td-p/4735135

---

## Next Steps

1. **Create GitHub Issue** for UniFi MCP setup
2. **Handoff to homelab-specialist agent** for MCP installation
3. **Obtain CloudKey credentials** for MCP configuration
4. **Get Sky Hub MAC address** for Option 61
5. **Schedule cutover window** with family

---

## Completion Criteria

**Phase 0 Complete When:**
- ✅ UniFi MCP operational
- ✅ Complete network inventory generated
- ✅ All settings documented
- ✅ Sky WAN config researched

**Phase 1 Complete When:**
- ✅ UDM online with internet
- ✅ Settings migrated
- ✅ Test devices working on new network

**Phase 4 Complete When:**
- ✅ Old network powered down
- ✅ New network operational
- ✅ All devices reconnected
- ✅ Zero family complaints

**Migration Complete When:**
- ✅ 7-day stability confirmed
- ✅ All services operational
- ✅ Documentation updated
- ✅ Old equipment retired

---

**Migration Status:** ⏳ Awaiting UniFi MCP Setup (Phase 0)

**Last Updated:** 2024-12-27  
**Next Review:** After MCP installation complete
