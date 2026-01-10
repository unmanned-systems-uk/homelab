# Home Assistant - Samsung TV Connection Troubleshooting

**Date:** 2026-01-08
**Issue:** Home Assistant cannot access Samsung TV on 10.0.30.141
**Status:** ✓ RESOLVED - Moved TV to Main WiFi

---

## ✓ RESOLUTION (2026-01-08)

**Root Cause:** VLAN isolation issue between Home Assistant (10.0.1.150) and Samsung TV (10.0.30.141 on IoT VLAN). Despite firewall rules "Allow HA to IoT" and "Allow IoT to HA" existing, cross-VLAN communication was still blocked.

**Solution:** Moved Samsung TV from IoT VLAN (10.0.30.0/24) to Main WiFi (10.0.1.0/24)
- **Old IP:** 10.0.30.141 (IoT VLAN 30)
- **New IP:** 10.0.1.141 (Main network)
- **Result:** Home Assistant integration now working ✓

**Lesson Learned:** Even with explicit firewall rules, VLAN isolation can be more complex than expected. Additional factors may include:
- AP client isolation settings
- Hidden or default deny rules
- Rule ordering issues
- Unifi Security Gateway advanced isolation features

**Recommendation:** For smart home devices that need integration with Home Assistant, keep them on the same network unless strict IoT isolation is required for security.

---

## Original Troubleshooting (Reference)

**Note:** The following troubleshooting steps were created when the TV was on IoT VLAN. They remain here for reference if you need to troubleshoot cross-VLAN issues in the future.

---

## Verified Working Components ✓

| Component | Status | Details |
|-----------|--------|---------|
| **Samsung TV Online** | ✓ | 10.0.30.141 responding to ping |
| **Port 8001 (WebSocket)** | ✓ | OPEN |
| **Port 8002 (SSL WebSocket)** | ✓ | OPEN |
| **Port 8080 (HTTP)** | ✓ | OPEN |
| **Port 9197 (Discovery)** | ✓ | OPEN |
| **Firewall Rules** | ✓ | "Allow HA to IoT" exists |
| **Firewall Rules** | ✓ | "Allow IoT to HA" exists |
| **Network Connectivity** | ✓ | Main network can reach IoT VLAN |

**Conclusion:** Network and firewall are correctly configured. Issue is likely with Home Assistant integration or Samsung TV pairing.

---

## Test Connectivity from Home Assistant

### Option 1: Use Home Assistant Terminal (Recommended)

1. **Access Home Assistant:**
   - URL: http://10.0.1.150:8123
   - Or: https://ha.unmanned-systems.uk

2. **Open Terminal & SSH Add-on:**
   - Click: **Settings** (⚙️)
   - Click: **Add-ons**
   - Select: **Terminal & SSH**
   - Click: **OPEN WEB UI**

3. **Test connectivity:**
   ```bash
   # Test ping to Samsung TV
   ping -c 5 10.0.30.141

   # Test port 8001 (WebSocket)
   nc -zv 10.0.30.141 8001

   # Test port 8002 (SSL WebSocket)
   nc -zv 10.0.30.141 8002
   ```

4. **Expected results:**
   ```
   ✓ Ping: 5 packets transmitted, 5 received
   ✓ Port 8001: succeeded!
   ✓ Port 8002: succeeded!
   ```

### Option 2: SSH from Another System

```bash
ssh -p 22222 homelab@10.0.1.150
# (Requires SSH key configured)
ping -c 5 10.0.30.141
```

---

## Check Samsung TV Integration Status

### 1. Check Current Integrations

1. Go to: **Settings** → **Devices & Services**
2. Look for: **Samsung Smart TV** integration
3. Check status:
   - **Not listed:** Integration not added yet
   - **Listed but "Unavailable":** Connection/pairing issue
   - **Listed and "Connected":** Integration working

### 2. If Integration Exists But Not Working

**Check integration details:**
1. Click on **Samsung Smart TV** integration
2. Click: **Configure**
3. Verify:
   - Host: `10.0.30.141` (correct IP)
   - Port: `8001` or `8002`
   - Method: `Websocket`

**Common issues:**
- Wrong IP address
- TV is in standby mode (won't respond)
- TV rejected pairing request
- MAC address changed

---

## Add Samsung TV Integration (If Not Configured)

### Step-by-Step Setup

1. **Navigate to Integrations:**
   - Go to: **Settings** → **Devices & Services**
   - Click: **+ ADD INTEGRATION** (bottom right)

2. **Search for Samsung:**
   - Type: `Samsung`
   - Select: **Samsung Smart TV**

3. **Auto-Discovery:**
   - HA may automatically discover TV at 10.0.30.141
   - If found: Click **"SELECT"**
   - If not found: Click **"MANUALLY ADD"**

4. **Manual Configuration:**
   ```
   Host: 10.0.30.141
   Port: 8001
   Name: Samsung TV
   ```

5. **Pairing Request:**
   - A popup will appear on your **Samsung TV screen**
   - Use TV remote to select: **"Allow"**
   - ⚠️ **IMPORTANT:** This must be done within 30 seconds

6. **Verify Connection:**
   - Integration should show as "Connected"
   - Device should appear in Devices list

---

## Samsung TV Configuration Checklist

### Check TV Network Settings

On the Samsung TV (using remote):

1. **Press:** Settings button
2. **Navigate to:** General → Network
3. **Check:**
   - Network Status: Connected
   - IP Address: `10.0.30.141` (verify correct)
   - Connection: WiFi or Ethernet

### Enable Smart Features

1. **Navigate to:** General → Network → Expert Settings
2. **Verify enabled:**
   - Power On with Mobile: **ON**
   - IP Remote: **ON** (or "Allow remote control")

### Check Allowed Devices

1. **Navigate to:** General → External Device Manager
2. **Check:** Device Connection Manager
3. **Look for:** Home Assistant or any blocked devices
4. **Action:** Remove any blocks, allow connection

---

## Common Issues and Solutions

### Issue 1: TV Not Responding

**Symptoms:**
- Ping fails from HA
- Integration shows "Unavailable"

**Solutions:**
1. **Wake the TV:** Turn on with remote (not standby)
2. **Check network:** Verify TV is on correct network
3. **Restart TV:** Full power cycle (unplug 30 seconds)
4. **Check IP:** TV may have obtained new DHCP address

**Test:**
```bash
# From HA Terminal
ping -c 5 10.0.30.141
```

### Issue 2: Pairing Rejected

**Symptoms:**
- Popup appeared on TV but timed out
- Integration fails with "Could not connect"

**Solutions:**
1. **Remove integration:** Settings → Devices & Services → Samsung TV → Delete
2. **Restart HA:** Settings → System → Restart
3. **Re-add integration:** Follow setup steps again
4. **Be ready:** Have TV remote in hand, accept within 30 seconds

### Issue 3: "Connection Refused"

**Symptoms:**
- Network is working but HA can't connect
- Ports appear closed from HA

**Solutions:**
1. **Check TV firewall:** Some Samsung TVs have built-in firewalls
2. **Try different port:**
   - Port 8001 (non-SSL)
   - Port 8002 (SSL)
3. **Disable AP Isolation:** On UDM Pro, ensure AP client isolation is OFF for IoT VLAN

### Issue 4: TV IP Changed

**Symptoms:**
- Integration worked before but not now
- New TV IP address

**Solutions:**
1. **Set Static IP on TV:**
   - TV Settings → Network → IP Settings → Manual
   - IP: `10.0.30.141`
   - Subnet: `255.255.255.0`
   - Gateway: `10.0.30.1`
   - DNS: `10.0.1.1` or `8.8.8.8`

2. **Create DHCP Reservation on UDM Pro:**
   - https://10.0.1.1
   - Settings → Networks → IoT → DHCP
   - Add reservation for TV MAC address → 10.0.30.141

---

## Verify UDM Pro Firewall Rules

### Check Rule Configuration

1. **Access UDM Pro:** https://10.0.1.1
2. **Navigate to:** Settings → Firewall & Security → Firewall Rules
3. **Verify rules exist:**

**Rule 1: Allow HA to IoT**
```
Type: LAN IN
Action: ACCEPT
Source: 10.0.1.150 (HA)
Destination: IoT Network (10.0.30.0/24)
```

**Rule 2: Allow IoT to HA**
```
Type: LAN OUT (or LAN IN from IoT perspective)
Action: ACCEPT
Source: IoT Network (10.0.30.0/24)
Destination: 10.0.1.150 (HA)
```

4. **Check rule order:**
   - Allow rules should be BEFORE block rules
   - Firewall processes rules top-to-bottom

5. **Enable logging (optional):**
   - Edit rule → Advanced → Logging: ON
   - View logs: Settings → System → Logs → Firewall

---

## Home Assistant Logs

### View Integration Logs

1. **Navigate to:** Settings → System → Logs
2. **Search for:** `samsungtv` or `samsung`
3. **Look for errors:**
   ```
   Connection timeout
   Connection refused
   Authentication failed
   Device not found
   ```

### Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    homeassistant.components.samsungtv: debug
```

Restart Home Assistant and check logs again.

---

## Alternative: Use Samsung TV API

### Manual Test from HA Terminal

```bash
# Test Samsung TV API (port 8001)
curl -v http://10.0.30.141:8001/api/v2/

# Test Samsung TV API (port 8002 SSL)
curl -k https://10.0.30.141:8002/api/v2/
```

**Expected:** Response with JSON data or connection info

---

## Next Steps

### If Connectivity Test FAILS from HA Terminal

1. **Check HA routing:**
   ```bash
   # From HA Terminal
   ip route show
   traceroute 10.0.30.141
   ```

2. **Check if HA can reach other IoT devices:**
   ```bash
   # Test other IoT VLAN devices
   ping 10.0.30.1  # IoT gateway
   ```

3. **Restart HA networking:**
   - Settings → System → Restart

### If Connectivity Test SUCCEEDS but Integration Fails

1. **TV pairing issue:** Remove integration, restart HA, re-add
2. **TV firmware:** Update Samsung TV firmware
3. **HA version:** Update Home Assistant OS
4. **Try alternative:** Use `Broadlink RM` or `MQTT` for TV control

---

## Samsung TV Integration Features

### Once Working, You'll Have:

**Controls:**
- Power On/Off
- Volume Up/Down/Mute
- Change Input/Source
- Channel Control
- Media Playback

**Sensors:**
- Power State (on/off)
- Source (HDMI1, HDMI2, etc.)
- Volume Level

**Automations:**
- Turn on TV when motion detected
- Switch to HDMI1 when gaming console detected
- Turn off TV at bedtime
- Lower volume during phone calls

---

## Related Documentation

- **Firewall Guide:** `docs/home-assistant-iot-vlan-firewall-rule.md`
- **Network Config:** `docs/udm-pro-migration-complete.md`
- **HA Device Info:** `homelab_db.infrastructure.devices` (HA-Pi5)

---

## Quick Reference

| Item | Value |
|------|-------|
| **Home Assistant** | http://10.0.1.150:8123 |
| **External URL** | https://ha.unmanned-systems.uk |
| **Samsung TV IP** | 10.0.30.141 |
| **TV Control Port** | 8001 (non-SSL) or 8002 (SSL) |
| **HA SSH Port** | 22222 (requires key) |
| **HA Terminal** | Settings → Add-ons → Terminal & SSH |

---

*Firewall and network are configured correctly - focus on HA integration setup and TV pairing*
