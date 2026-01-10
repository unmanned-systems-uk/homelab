# HA Pi Network Fix - UniFi Configuration Guide

**Issue:** HA Pi causing recurring network failures on US 24 Cinema switch
**Root Cause:** STP topology changes + potential broadcast storm during HA Pi restarts
**Impact:** CRITICAL - Medical alert system for Nathan's diabetes monitoring
**Date:** 2026-01-10

---

## IMMEDIATE: UniFi Configuration Changes

### Step 1: Configure US 48 Dev Office Port 14 (Uplink to US 24)

**Access:** UniFi Controller → Devices → US 48 Dev Office → Ports → Port 14

**Changes Required:**

1. **Port Profile/Name:** "Uplink-US24-Cinema-Medical"

2. **Spanning Tree:**
   - ☑ **Enable STP Edge Port (PortFast)**
   - Effect: Port immediately enters forwarding state, no STP recalculation on topology changes

3. **Link Speed:**
   - Change from: Auto-Negotiate
   - Change to: **1 Gbps Full Duplex (Force)**
   - Effect: Eliminates auto-negotiation timeout issues

4. **Storm Control:**
   - ☑ **Enable Storm Control**
   - Broadcast Threshold: **10%**
   - Multicast Threshold: **10%**
   - Unknown Unicast Threshold: **10%**
   - Effect: Prevents broadcast storms from bringing down link

5. **Apply Changes** → Confirm

---

### Step 2: Configure US 24 Cinema Port 2 (HA Pi Connection)

**Access:** UniFi Controller → Devices → US 24 PoE 250W Cinema → Ports → Port 2

**Changes Required:**

1. **Port Profile/Name:** "HA-Pi-Medical-Alert"

2. **Storm Control:**
   - ☑ **Enable Storm Control**
   - Broadcast Threshold: **10%**
   - Multicast Threshold: **10%**
   - Unknown Unicast Threshold: **10%**
   - Effect: Limits HA service broadcasts (mDNS, Avahi, SSDP)

3. **Port Isolation:**
   - ☐ **Disable Port Isolation** (ensure UNCHECKED)
   - Effect: Allows HA Pi to communicate with all VLANs

4. **VLAN:**
   - Verify: Native VLAN 1 (10.0.1.0/24)
   - Profile: Default/All

5. **Apply Changes** → Confirm

---

## Verification Steps

### After Applying Config Changes:

```bash
# 1. Verify HA Pi connectivity
ping -c 5 10.0.1.150

# 2. Check switch port status
# UniFi Controller → Devices → US 48 → Port 14
# Should show: 1000 FDX, STP Edge Port Enabled

# 3. Monitor for 5 minutes
watch -n 10 'ping -c 1 10.0.1.150'

# 4. Test HA Pi restart
# SSH to HA Pi and restart - should NOT cause network drop
```

---

## PERMANENT FIX: Fiber Uplink Upgrade

### Components Ordered:

**Option 1: 1Gbps Fiber (Recommended for Medical)**
```
- 2x Ubiquiti UF-RJ45-1G SFP to RJ45 Module (if keeping RJ45)
  OR
- 2x Generic 1000Base-SX SFP Module (LC connector, multimode)
- 1x LC-LC OM3/OM4 Multimode Fiber Cable (length as needed)
```

**Option 2: 10Gbps Fiber (Future-proof)**
```
- 2x Ubiquiti UF-MM-10G SFP+ Module (LC, multimode)
- 1x LC-LC OM3/OM4 Multimode Fiber Cable
- Note: Both switches support 10G, future-proofs link
```

**Recommended:** 10Gbps for £10-20 more - same reliability, future-proof

---

### Installation Procedure (When Components Arrive):

**Current Topology:**
```
US 48 Port 14 (copper) → US 24 Uplink Port (copper)
```

**New Topology:**
```
US 48 SFP+ Port (fiber) → US 24 SFP+ Uplink Port (fiber)
```

**Steps:**

1. **Pre-Installation:**
   - Note current US 48 Port 14 configuration
   - Backup UniFi settings
   - Schedule during low-usage window (HA Pi can tolerate brief outage)

2. **Physical Installation:**
   - Insert SFP module into US 48 available SFP+ port
   - Insert SFP module into US 24 SFP+ uplink port
   - Connect LC-LC fiber cable between modules
   - **DO NOT disconnect copper yet**

3. **UniFi Configuration:**
   - US 48 → New SFP port → Copy settings from Port 14:
     - STP Edge Port: Enabled
     - Storm Control: 10%
     - Profile: "Uplink-US24-Cinema-Medical"
   - Verify link shows UP and ACTIVE
   - Verify HA Pi reachable through new path

4. **Cutover:**
   - **Disconnect copper cable from US 48 Port 14**
   - Verify HA Pi still reachable (now via fiber)
   - Monitor for 10 minutes

5. **Verification:**
   ```bash
   ping -c 100 10.0.1.150  # Should show 0% loss

   # Test HA Pi restart (this was the failure trigger)
   ssh ha-pi "sudo reboot"
   # Monitor - should NOT cause network drop
   ```

6. **Cleanup:**
   - Disable US 48 Port 14 (old copper port)
   - Update port descriptions in UniFi
   - Document in network diagram

---

## Monitoring Plan

### Next 48 Hours (Config Changes Applied):

- [ ] Monitor UniFi logs for port state changes
- [ ] Monitor HA Pi uptime/connectivity
- [ ] Test HA Pi restart at least once
- [ ] Watch for STP topology change events

**Check:** UniFi Controller → Events → Filter by "Port" and "STP"

### Post-Fiber Installation:

- [ ] 7-day stability verification
- [ ] HA Pi restart tests (3x minimum)
- [ ] Monitor medical alert system reliability
- [ ] Confirm no recurrence

---

## Troubleshooting

### If Issue Persists After Config Changes:

**Immediate Action:**
1. Apply fiber upgrade (don't wait for testing period)
2. Check for other network loops
3. Review HA Pi network services (disable unnecessary mDNS/Avahi)

### If Fiber Link Won't Come Up:

1. Verify SFP modules seated properly
2. Check fiber cable not damaged (bent radius >1 inch)
3. Verify SFP modules compatible (Ubiquiti or generic 1G/10G)
4. Check UniFi recognizes SFP modules (should auto-detect)
5. Try different SFP+ ports if available

---

## Expected Component Costs

| Item | Recommended | Est. Cost |
|------|-------------|-----------|
| **Budget Option (1G)** | | |
| 2x 1G SFP Modules | Generic 1000Base-SX | £20-30 |
| 1x LC-LC Fiber Cable (OM3) | 1m-5m as needed | £8-15 |
| **TOTAL** | | **£28-45** |
| | | |
| **Recommended (10G)** | | |
| 2x Ubiquiti UF-MM-10G | Official UniFi | £40-60 |
| 1x LC-LC OM4 Fiber Cable | Premium rated | £15-25 |
| **TOTAL** | | **£55-85** |

**Recommendation:** Go with 10G option - minimal cost difference, future-proof, medical-grade reliability.

---

## Medical Alert System Protection

### Immediate (While Waiting for Fiber):

- [ ] Verify HA Pi has UPS battery backup
- [ ] Test battery runtime (should sustain >2 hours)
- [ ] Document offline alert procedures for Nathan
- [ ] Ensure mobile alerts configured (if network fails, push notifications continue)

### Long-term:

- [ ] Cellular failover module for critical alerts
- [ ] Redundant HA instance on different network segment
- [ ] Offline alert queuing/retry mechanism

---

## Network Topology (After Fiber Upgrade)

```
Internet
  │
UDM Pro (10.0.1.1)
  │
US 48 Dev Office (10.0.10.10)
  │
  ├─ Port 14: [DISABLED - Old Copper]
  │
  └─ SFP+ Port X: [FIBER UPLINK] ──────────┐
                                            │ LC-LC OM4 Fiber
                                            │
                 ┌──────────────────────────┘
                 │
           SFP+ Uplink Port
                 │
        US 24 PoE Cinema (10.0.10.13)
                 │
           Port 2 (Storm Control)
                 │
           HA Pi (10.0.1.150)
           [Medical Alert System]
           [Separate PSU - NOT PoE]
```

---

**Status:** Configuration changes ready to apply NOW.
**Fiber components:** On order - install when received.
**Priority:** CRITICAL - Medical alert system.
**Next:** User to apply UniFi config changes above.

---

*HomeLab Infrastructure - Medical System Network Remediation*
*Created: 2026-01-10*
