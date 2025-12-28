# OFFLINE MIGRATION GUIDE - USG to UDM Pro

**CRITICAL: Use this if you lose internet/Claude access during migration**

**Generated:** 2025-12-27
**Status:** Complete standalone guide

---

## 🚨 EMERGENCY CONTACT INFO

If something goes wrong and you need help:
- UniFi Support: https://help.ui.com (from phone/different network)
- Rollback instructions: See "EMERGENCY ROLLBACK" section below

---

## 📋 CURRENT STATE (Starting Point)

**Network Status:**
- USG Pro 4: 10.0.1.1 (production gateway)
- CloudKey: 10.0.1.2:8443 (controller)
- Current network: 10.0.1.0/24
- All devices working normally

**What You Have:**
- UDM Pro (new, unboxed)
- DEV-PC-Ubuntu at 10.0.1.83
  - Primary NIC: enp2s0 (10.0.1.83)
  - USB NIC: enx00e04c680674 (not configured yet)
- Clean CloudKey backup file (.unf) - from agent cleanup

**What You Need:**
- 2x Ethernet cables
- Sky Hub MAC address: ________________ (write it here)
- 15-30 minutes of family downtime for final cutover

---

## 🎯 COMPLETE MIGRATION STEPS

### PHASE 1: USG LAN 2 SETUP (5 min, ZERO downtime)

**Goal:** Create fake WAN network for UDM Pro testing

#### Step 1.1: Create Network on CloudKey

**Access:** https://10.0.1.2:8443

```
Login → Settings → Networks → Create New Network

Fill in:
┌─────────────────────────────────────────┐
│ Name: UDM-Fake-WAN                      │
│ Purpose: Corporate                      │
│ VLAN: [leave blank]                     │
│ Gateway/Subnet: 192.168.99.1/24         │
│                                         │
│ ☑ DHCP Enabled                          │
│ DHCP Range:                             │
│   Start: 192.168.99.100                 │
│   End: 192.168.99.200                   │
│   Lease Time: 86400                     │
│                                         │
│ ☐ Auto Scale Network (OFF)              │
└─────────────────────────────────────────┘

Click "Apply" → Wait 10 seconds
```

#### Step 1.2: Assign LAN 2 Port

```
Devices → Sunnybrae-Gateway (USG Pro 4) → Settings → Ports

Find: LAN 2
Click to expand

┌─────────────────────────────────────────┐
│ Network Assignment: UDM-Fake-WAN        │
└─────────────────────────────────────────┘

Click "Apply"

USG will provision (30-60 seconds, status bar shows progress)
```

#### Step 1.3: Verify LAN 2 Active

```
Devices → Sunnybrae-Gateway → Ports

LAN 2 should show:
✓ IP: 192.168.99.1
✓ Network: UDM-Fake-WAN  
✓ Status: Active (green)
```

**✅ CHECKPOINT:** USG LAN 2 is now a gateway at 192.168.99.1

---

### PHASE 2: UDM PRO INITIAL SETUP (30 min, ZERO downtime)

**Goal:** Setup UDM on fake WAN, restore backup, configure temporary LAN

#### Step 2.1: Physical Connections

```
1. Connect ethernet cable:
   USG Pro 4 [LAN 2 port] → UDM Pro [WAN port]

2. Power on UDM Pro
   - Blue LED will pulse (booting)
   - Wait 2-3 minutes for full boot
   - LED turns solid white when ready
```

#### Step 2.2: Access UDM Setup Wizard

**Option A: Via DHCP Discovery**
```
From DEV-PC browser:
http://unifi (might auto-discover)
or
https://192.168.99.x (check DHCP leases on CloudKey to find exact IP)
```

**Option B: Direct Connection (if discovery fails)**
```
1. Connect laptop directly to UDM Pro LAN port 1
2. Wait for DHCP (you'll get 192.168.1.x)
3. Access: https://192.168.1.1
```

#### Step 2.3: Run Setup Wizard

```
Step 1: Welcome Screen
→ Click "Next"

Step 2: Create Admin Account
┌─────────────────────────────────────────┐
│ Username: [your choice]                 │
│ Password: [strong password]             │
│ Confirm Password: [same]                │
└─────────────────────────────────────────┘
→ Click "Next"

Step 3: Restore from Backup ⭐ IMPORTANT
┌─────────────────────────────────────────┐
│ ○ Set up as new device                  │
│ ● Restore from backup                   │
│                                         │
│ [Choose File] → Select clean .unf file  │
│   from agent cleanup                    │
└─────────────────────────────────────────┘
→ Click "Restore"

Wait 5-10 minutes for restore to complete
UDM will reboot automatically

Step 4: After Reboot - Login
Use the credentials you just created
```

#### Step 2.4: Configure Temporary LAN

**Important:** We need different subnet from production (10.0.1.x) for parallel testing

```
Settings → Networks → Default (LAN)

Edit:
┌─────────────────────────────────────────┐
│ Gateway/Subnet: 192.168.1.1/24          │
│ DHCP Range: 192.168.1.100-200           │
└─────────────────────────────────────────┘

Apply Changes
```

#### Step 2.5: Verify Settings Restored

**Check these imported from backup:**

```
Settings → Networks → WiFi
✓ ACP-Guest (Open)
✓ ACP-WiFi (password: acpadman)
✓ SUNNY-5G (password: acpadman)
✓ dev-24g (password: dev-24g-2350)

Settings → Firewall & Security → Port Forwarding
✓ Nathan (27015 → 10.0.1.40)

Settings → Networks → LAN → DHCP
✓ ~30-40 static reservations (from cleanup)
```

**✅ CHECKPOINT:** UDM Pro running on fake WAN with all settings restored

---

### PHASE 3: DEV-PC DUAL NETWORK (5 min, ZERO downtime)

**Goal:** Configure DEV-PC to access both old and new networks simultaneously

#### Step 3.1: Create Netplan Config

**On DEV-PC-Ubuntu:**

```bash
sudo nano /etc/netplan/02-usb-nic.yaml
```

**Paste this EXACT config:**

```yaml
network:
  version: 2
  ethernets:
    enx00e04c680674:
      dhcp4: true
      dhcp4-overrides:
        route-metric: 200
      optional: true
```

**Save:** Ctrl+O, Enter, Ctrl+X

#### Step 3.2: Apply Config

```bash
sudo netplan apply
```

**If errors, try:**
```bash
sudo netplan --debug apply
```

#### Step 3.3: Physical Connection

```
Connect ethernet cable:
UDM Pro [LAN Port 1] → DEV-PC USB NIC (enx00e04c680674)
```

#### Step 3.4: Verify Dual Network

**Check IP addresses:**
```bash
ip addr show

# Should see:
# enp2s0: inet 10.0.1.83/24        (old network)
# enx00e04c680674: inet 192.168.1.xxx/24  (new network)
```

**Check routes:**
```bash
ip route show

# Should see:
# default via 10.0.1.1 dev enp2s0 metric 100        (primary)
# default via 192.168.1.1 dev enx00e04c680674 metric 200  (backup)
# 10.0.1.0/24 dev enp2s0
# 192.168.1.0/24 dev enx00e04c680674
```

**Test connectivity:**
```bash
# Old network (USG)
ping -c 3 10.0.1.1
ping -c 3 10.0.1.2

# New network (UDM)
ping -c 3 192.168.1.1
```

**✅ CHECKPOINT:** DEV-PC can access BOTH networks

---

### PHASE 4: PARALLEL TESTING (1-2 hours, ZERO downtime)

**Goal:** Thoroughly test UDM Pro before cutover

#### Test 4.1: UDM Pro Web Interface

```
Browser: https://192.168.1.1

✓ Can login
✓ Dashboard shows devices (from backup)
✓ Settings look correct
✓ No errors in logs
```

#### Test 4.2: WiFi SSIDs

```
From phone/tablet:

✓ Can see all 4 SSIDs (ACP-Guest, ACP-WiFi, SUNNY-5G, dev-24g)
✓ Passwords work (don't connect yet, just verify)
```

#### Test 4.3: Test Device Connection

```
Connect test laptop/phone to UDM Pro WiFi:
1. Join "dev-24g" SSID (password: dev-24g-2350)
2. Should get IP: 192.168.1.x
3. Test internet: ping 8.8.8.8
4. Test websites work
5. Disconnect when done
```

#### Test 4.4: Verify Critical Settings

```
Settings → Internet → WAN
✓ Connection: DHCP (currently getting 192.168.99.x from USG LAN 2)
✓ Gateway: 192.168.99.1
✓ Status: Connected

Settings → Networks → LAN
✓ Subnet: 192.168.1.0/24 (temporary)

Settings → System → Backups
✓ Last backup shows (from CloudKey restore)
```

**✅ CHECKPOINT:** UDM Pro fully functional on fake WAN

---

### PHASE 5: PRE-CUTOVER PREPARATION (30 min)

**Goal:** Get everything ready for final cutover

#### Step 5.1: Announce Downtime

**Tell family:**
```
"Network will be down for 15-20 minutes starting at [TIME]
Save any work, pause downloads, expect WiFi to drop"
```

#### Step 5.2: Document Current State

**Take photos:**
- USG physical connections
- Switch connections
- Cable labels

**Record IPs (in case of rollback):**
```
USG: 10.0.1.1
CloudKey: 10.0.1.2
NAS: 10.0.1.251
Proxmox: 10.0.1.200
```

#### Step 5.3: Prepare UDM Pro for Production

**On UDM Pro (https://192.168.1.1):**

```
Settings → Networks → Default (LAN) → Edit

Change from temporary to production subnet:
┌─────────────────────────────────────────┐
│ Gateway/Subnet: 10.0.1.1/24             │
│ DHCP Range: 10.0.1.6-254                │
└─────────────────────────────────────────┘

⚠️ DO NOT APPLY YET! Just prepare the change.
```

**Configure WAN for Sky Broadband:**

```
Settings → Internet → Primary (WAN1) → Edit

⚠️ DO NOT APPLY YET! Just prepare:
┌─────────────────────────────────────────┐
│ Connection Type: DHCP                   │
│                                         │
│ Advanced → Manual:                      │
│   DHCP Option 61 (Client ID):          │
│   anything@skydsl|[YOUR_SKY_HUB_MAC]   │
│                                         │
│ Replace [YOUR_SKY_HUB_MAC] with actual │
│ MAC from Sky Hub (format: aa:bb:cc)    │
│                                         │
│ IPv6: Disabled                          │
└─────────────────────────────────────────┘

Example:
anything@skydsl|aa:bb:cc:dd:ee:ff
```

**✅ CHECKPOINT:** Ready for cutover, settings prepared but not applied

---

### PHASE 6: THE CUTOVER (15 min, FAMILY DOWNTIME)

**⚠️ POINT OF NO RETURN - Family WiFi goes down now**

#### Step 6.1: Shutdown Old Network

```
1. CloudKey: Settings → System → Shutdown
   Wait for shutdown (2 min)

2. USG Pro 4: Unplug power
   Wait 30 seconds
```

#### Step 6.2: Reconfigure UDM Pro

**On UDM Pro (via DEV-PC USB NIC to 192.168.1.1):**

```
Settings → Networks → Default (LAN)
Apply the change prepared earlier:
- Gateway: 10.0.1.1/24
- DHCP: 10.0.1.6-254
→ Click "Apply Changes"

Settings → Internet → Primary (WAN1)
Apply the Sky config prepared earlier:
- Connection: DHCP
- Option 61: anything@skydsl|[YOUR_SKY_HUB_MAC]
- IPv6: Disabled
→ Click "Apply Changes"

⚠️ You'll lose connection to UDM when LAN changes!
This is expected.
```

#### Step 6.3: Physical Reconnection

```
1. DISCONNECT:
   - UDM WAN from USG LAN 2
   - DEV-PC USB NIC from UDM

2. CONNECT:
   - ONT → UDM Pro WAN port
   - UDM Pro LAN port 1 → Main switch (SW1-48)
     (wherever USG LAN was connected before)

3. Power cycle UDM Pro:
   - Unplug power
   - Wait 10 seconds  
   - Plug back in
   - Wait 2-3 minutes for full boot
```

#### Step 6.4: Verify Internet

**On DEV-PC (should auto-reconnect to 10.0.1.x):**

```bash
# Check you got new IP
ip addr show enp2s0
# Should show: 10.0.1.x (might be different from .83)

# Check gateway
ip route | grep default
# Should show: default via 10.0.1.1 dev enp2s0

# Test internet
ping -c 3 8.8.8.8
ping -c 3 google.com
```

**Access UDM at new address:**
```
Browser: https://10.0.1.1

Should see UDM dashboard
Check: Settings → Internet → WAN
✓ Status: Connected
✓ IP: (Sky DHCP IP, something like 90.x.x.x)
✓ Gateway: (Sky gateway)
```

#### Step 6.5: Device Adoption

**UniFi devices should auto-adopt:**

```
UDM → Devices

Check all show as "Connected":
✓ Switches (4 online)
✓ Access Points (7 online)

If any show "Managed by Other":
1. Click device
2. Click "Forget"
3. Wait 30 seconds
4. Click "Adopt"

If device stuck offline:
SSH to device or factory reset
ssh ubnt@DEVICE_IP
set-inform http://10.0.1.1:8080/inform
```

#### Step 6.6: Verify Family Devices

```
Have family reconnect WiFi:
- Same SSIDs (ACP-WiFi, SUNNY-5G)
- Same passwords (acpadman)
- Should auto-reconnect for most devices

Test:
✓ Phones/tablets connect
✓ Internet working
✓ Streaming works
```

**✅ CHECKPOINT:** Migration complete! UDM Pro is now production gateway

---

## 🔥 EMERGENCY ROLLBACK

**If something goes wrong and you need to go back:**

### Rollback Step 1: Shutdown UDM Pro

```
UDM: Settings → System → Shutdown
or
Unplug UDM Pro power
```

### Rollback Step 2: Restore USG Pro 4

```
1. Disconnect UDM from ONT
2. Connect ONT → USG Pro 4 WAN port
3. Connect USG LAN 1 → Main switch
4. Power on USG Pro 4
5. Wait 2-3 minutes
```

### Rollback Step 3: Start CloudKey

```
1. Power on CloudKey
2. Wait 3-5 minutes for full boot
3. Access: https://10.0.1.2:8443
```

### Rollback Step 4: Verify

```
✓ Internet working (ping 8.8.8.8)
✓ CloudKey accessible
✓ Devices showing in controller
✓ Family WiFi working

You're back to original state.
```

**Time to rollback: 5-10 minutes**

---

## 🐛 TROUBLESHOOTING

### Problem: Can't access UDM setup wizard

**Solution A: Direct connection**
```
1. Connect laptop directly to UDM LAN port
2. Wait 30 seconds for DHCP
3. Access: https://192.168.1.1
```

**Solution B: Factory reset UDM**
```
1. Locate reset button (small hole on back)
2. Power on UDM
3. Hold reset button for 10+ seconds
4. LED flashes different colors
5. Release when LED is off
6. Wait 5 minutes for reset
7. Access: https://192.168.1.1
```

### Problem: UDM WAN not getting internet

**Check 1: Physical connection**
```
✓ ONT → UDM WAN (correct port?)
✓ Green link light on both ends?
✓ Try different ethernet cable
```

**Check 2: Sky DHCP Option 61**
```
Settings → Internet → WAN → Advanced
Verify exact format:
anything@skydsl|aa:bb:cc:dd:ee:ff

Common mistakes:
✗ Missing pipe character |
✗ Wrong MAC address
✗ Spaces in string
✗ IPv6 enabled (should be disabled)
```

**Check 3: Power cycle ONT**
```
1. Unplug ONT power
2. Wait 30 seconds
3. Plug back in
4. Wait 2 minutes
5. Power cycle UDM
```

### Problem: Devices won't adopt to UDM

**Solution 1: SSH set-inform**
```
ssh ubnt@DEVICE_IP
Password: (from old controller device credentials)

set-inform http://10.0.1.1:8080/inform
exit
```

**Solution 2: Factory reset device**
```
Via UniFi web:
1. Device → Settings
2. Scroll to bottom
3. Click "Factory Reset"
4. Confirm
5. Wait 5 minutes
6. Device appears as "Pending Adoption"
7. Click "Adopt"

Via physical button:
1. Unplug device
2. Hold reset button
3. Plug in power (keep holding)
4. Wait for LED pattern change
5. Release button
6. Adopt in UDM web UI
```

### Problem: CloudKey backup restore fails

**Symptoms:**
- Restore hangs
- Error during restore
- UDM reboots repeatedly

**Solutions:**

**Try 1: Restore during setup wizard**
```
Factory reset UDM
Run setup wizard from beginning
Choose "Restore from backup" option
Upload backup file
Wait patiently (can take 10+ minutes)
```

**Try 2: Restore after setup**
```
Complete setup as new device
Login to UDM
Settings → System → Backups
Click "Restore from Backup"
Upload .unf file
```

**Try 3: Different backup**
```
If you have multiple backups, try:
- "Settings Only" backup (smaller, faster)
- Older backup from CloudKey
```

### Problem: No internet after cutover

**Check WAN connection:**
```
Settings → Internet
Status should show: Connected
IP should show: (Sky DHCP, like 90.x.x.x)

If "Disconnected":
1. Check physical cable (ONT → UDM WAN)
2. Verify DHCP Option 61 correct
3. Power cycle ONT
4. Power cycle UDM
```

**Check DNS:**
```
Settings → Internet → WAN → Advanced
DNS Servers:
- Auto (from DHCP) OR
- Manual: 8.8.8.8, 8.8.4.4
```

**Test from command line:**
```bash
# On DEV-PC
ping 8.8.8.8          # Should work (tests routing)
ping google.com       # Should work (tests DNS)

# If first works but second fails = DNS problem
# If neither works = routing/WAN problem
```

### Problem: Family devices won't reconnect

**WiFi still shows but no internet:**
```
1. Forget network on device
2. Reconnect manually
3. Enter password: acpadmin (or dev-24g-2350)
```

**WiFi doesn't show at all:**
```
Check UDM:
Settings → WiFi
✓ SSIDs enabled?
✓ Passwords correct?

Check APs:
Devices → Access Points
✓ All online?
✓ All adopted?

If APs offline:
- Check PoE switch ports
- Check physical connections
- Readopt APs if needed
```

---

## 📞 SUPPORT RESOURCES

### UniFi Documentation
```
https://help.ui.com/hc/en-us/articles/4416276882327
(UDM Pro Setup Guide)

https://help.ui.com/hc/en-us/articles/360008976393
(Backups and Migration)
```

### Sky Broadband + UniFi
```
https://helpforum.sky.com/t5/Broadband/Sky-Broadband-with-Ubiquiti-Unifi-Dream-Machine-Pro/td-p/4514120
```

### Community Forums
```
https://community.ui.com
(Search for similar issues)
```

---

## 📋 QUICK REFERENCE

### Sky WAN Configuration
```
Connection: DHCP
DHCP Option 61: anything@skydsl|[SKY_HUB_MAC]
IPv6: Disabled
```

### Network Subnets
```
Production: 10.0.1.0/24 (gateway 10.0.1.1)
Fake WAN: 192.168.99.0/24 (gateway 192.168.99.1)
Temp UDM: 192.168.1.0/24 (gateway 192.168.1.1)
```

### WiFi Passwords
```
ACP-WiFi: acpadman
SUNNY-5G: acpadman
dev-24g: dev-24g-2350
ACP-Guest: Open (no password)
```

### Critical Device IPs (Production)
```
Gateway: 10.0.1.1 (will be UDM after migration)
NAS: 10.0.1.251
Proxmox: 10.0.1.200
CCPM: 10.0.1.210
MCP: 10.0.1.159
Gaming: 10.0.1.40 (Nathan - port forward 27015)
```

### DEV-PC Network Interfaces
```
Primary: enp2s0 (MAC: d8:bb:c1:9a:e1:0c)
USB NIC: enx00e04c680674 (MAC: 00:e0:4c:68:06:74)
```

### SCPI Equipment (Keep these IPs)
```
10.0.1.101 - Keithley DMM6500
10.0.1.105 - Rigol DL3021A
10.0.1.106 - Rigol MSO8204
10.0.1.107 - Rigol RSA5065N
10.0.1.111 - Rigol DP932A-1
10.0.1.112 - Rigol DP832A-1
10.0.1.120 - Rigol DG2052
10.0.1.138 - Rigol DP932A-2
```

---

## ✅ POST-MIGRATION CHECKLIST

**Verify everything works:**

- [ ] Internet working (ping 8.8.8.8)
- [ ] Websites loading
- [ ] UDM accessible (https://10.0.1.1)
- [ ] All switches online (4 devices)
- [ ] All APs online (7 devices)
- [ ] Family WiFi working
- [ ] Phones/tablets connected
- [ ] Streaming services work
- [ ] NAS accessible
- [ ] Proxmox accessible
- [ ] Gaming server accessible (Nathan)
- [ ] Port forward working (test 27015)

**Optional tests:**

- [ ] SCPI equipment pingable
- [ ] DEV-PC on network
- [ ] Take speed test (Sky 900/115 Mbps)

---

## 🎯 NEXT STEPS (After Migration Complete)

**Week 1: Stabilization**
- Monitor network for issues
- Verify all services working
- Family feedback on WiFi

**Week 2: VLAN Implementation**
- Create VLAN 30 (IoT)
- Create VLAN 50 (Lab)
- Move devices in batches
- Configure firewall rules

**Week 3: SCPI Renumbering**
- Move SCPI to VLAN 50
- Renumber to 10.0.50.101-108
- Update scripts/configs

---

## 📝 NOTES SECTION

**Use this space to record:**
- Issues encountered:


- Solutions that worked:


- Times/durations:


- Sky Hub MAC: ____________________________

- UDM Pro Serial: ____________________________

---

**END OF OFFLINE GUIDE**

*Keep this document accessible during migration*
*Print or save offline copy*
*Last updated: 2025-12-27*
