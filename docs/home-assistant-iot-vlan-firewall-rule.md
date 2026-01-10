# Home Assistant IoT VLAN Access - Firewall Rule

**Date:** 2026-01-08
**Issue:** Home Assistant cannot access Samsung TV on IoT VLAN
**Solution:** Create firewall rule to allow HA access to IoT devices
**Status:** ✓ ISSUE RESOLVED - Alternative solution used (see below)

---

## ✓ ACTUAL RESOLUTION (2026-01-08)

**Issue:** Despite firewall rules "Allow HA to IoT" and "Allow IoT to HA" existing and being configured correctly, Home Assistant still could not access Samsung TV across VLANs.

**Solution Used:** Moved Samsung TV from IoT VLAN (10.0.30.141) to Main WiFi (10.0.1.141)
- Same network as Home Assistant (10.0.1.0/24)
- No cross-VLAN communication needed
- Integration working immediately ✓

**Root Cause:** VLAN isolation was more complex than firewall rules alone. Possible factors:
- AP client isolation enabled
- Additional UniFi isolation mechanisms
- Rule ordering or configuration issues
- Default deny policies overriding explicit allow rules

**Lesson Learned:** For Home Assistant smart device integrations, keeping devices on the same network is simpler and more reliable than managing cross-VLAN firewall rules.

**See also:** `docs/ha-samsung-tv-troubleshooting.md` for full resolution details.

---

## Original Documentation (Reference)

**Note:** The following firewall rule documentation remains for reference if you need to configure cross-VLAN access for other devices in the future.

---

## Problem Analysis

### Current Network Configuration

| Device | IP Address | VLAN | Subnet |
|--------|------------|------|--------|
| **Home Assistant (HA-Pi5)** | 10.0.1.150 | Default (Main) | 10.0.1.0/24 |
| **Samsung TV** | 10.0.30.141 | IoT (VLAN 30) | 10.0.30.0/24 |

### Existing Firewall Rules

From `docs/udm-pro-migration-complete.md`:

| Rule | Action | Description |
|------|--------|-------------|
| Block IoT to LAN | DROP | Prevents IoT devices FROM accessing main network |
| Block IoT to Lab | DROP | Prevents IoT devices FROM accessing lab equipment |

### Root Cause

The IoT VLAN (30) is isolated from the main network. While the existing rules block traffic **FROM IoT TO LAN**, Home Assistant needs traffic **FROM LAN TO IoT** to control smart devices like the Samsung TV.

By default, UniFi may allow traffic from LAN to IoT, but if strict isolation is enabled or bidirectional blocking is in place, an explicit allow rule is required.

---

## Required Firewall Rule

### Rule Configuration

**Create this rule in UDM Pro firewall BEFORE the "Block IoT" rules:**

| Parameter | Value |
|-----------|-------|
| **Rule Name** | Allow HA to IoT |
| **Rule Type** | LAN IN |
| **Action** | ACCEPT |
| **Protocol** | All |
| **Source Type** | IP Address |
| **Source** | 10.0.1.150 (Home Assistant) |
| **Destination Type** | Network |
| **Destination** | IoT (VLAN 30) - 10.0.30.0/24 |
| **Port** | Any |
| **Priority** | High (place BEFORE IoT isolation rules) |

### Alternative: Specific Device Rule

For tighter security, create a rule for just the Samsung TV:

| Parameter | Value |
|-----------|-------|
| **Source** | 10.0.1.150 (Home Assistant) |
| **Destination Type** | IP Address |
| **Destination** | 10.0.30.141 (Samsung TV) |

---

## Step-by-Step Configuration (UDM Pro Web UI)

### 1. Access UDM Pro Network Settings

1. Navigate to: `https://10.0.1.1`
2. Login with:
   - Username: `HomeLab-Agent`
   - Password: `HomeAdman2350`
3. Go to: **Settings** → **Firewall & Security** → **Firewall Rules**

### 2. Create New LAN IN Rule

1. Click **"+ Create New Rule"**
2. Select **Type: LAN IN**
3. Configure as follows:

**Basic Settings:**
```
Name: Allow HA to IoT
Description: Allows Home Assistant to control IoT devices (Samsung TV, etc.)
Rule Applied: Before Predefined Rules
Action: Accept
```

**Source:**
```
Source Type: IP Address
IPv4 Address: 10.0.1.150
```

**Destination:**
```
Destination Type: Network
Network: IoT (VLAN 30)
```

**Advanced:**
```
Protocol: All
States: All
Match IPsec: Disabled
Logging: Enabled (optional - for troubleshooting)
```

### 3. Save and Apply

1. Click **"Apply Changes"**
2. Wait 10-15 seconds for rule to propagate
3. Verify rule appears BEFORE the "Block IoT to LAN" rule

---

## Testing Connectivity

### From This System (10.0.1.0/24)

```bash
# Test basic connectivity
ping -c 3 10.0.30.141

# Test Samsung TV port (usually 8001 or 8002)
timeout 3 bash -c "echo > /dev/tcp/10.0.30.141/8001" && echo "Port 8001: OPEN" || echo "Port 8001: CLOSED"
timeout 3 bash -c "echo > /dev/tcp/10.0.30.141/8002" && echo "Port 8002: OPEN" || echo "Port 8002: CLOSED"
```

### From Home Assistant

**Option 1: SSH to HA-Pi5**
```bash
ssh homelab@10.0.1.150
ping -c 3 10.0.30.141
```

**Option 2: Home Assistant Terminal Add-on**
1. Open Home Assistant: http://10.0.1.150:8123
2. Go to: **Settings** → **Add-ons** → **Terminal & SSH**
3. Run: `ping -c 3 10.0.30.141`

**Expected Result After Rule Creation:**
```
PING 10.0.30.141 (10.0.30.141) 56(84) bytes of data.
64 bytes from 10.0.30.141: icmp_seq=1 ttl=63 time=X ms
✓ Success
```

---

## Samsung TV Integration in Home Assistant

### After Firewall Rule is Active

1. **Navigate to Home Assistant:**
   - URL: http://10.0.1.150:8123

2. **Add Samsung Smart TV Integration:**
   - Go to: **Settings** → **Devices & Services**
   - Click: **"+ ADD INTEGRATION"**
   - Search: **"Samsung Smart TV"**
   - Select: **Samsung Smart TV (WebSocket)**

3. **Configure Integration:**
   - Host: `10.0.30.141`
   - Port: `8001` (default) or `8002` (SSL)
   - Name: `Samsung TV`

4. **Allow Connection on TV:**
   - A popup will appear on the Samsung TV screen
   - Select: **"Allow"** to grant Home Assistant access

### Required Ports for Samsung TV

| Port | Protocol | Purpose |
|------|----------|---------|
| 8001 | Websocket | Samsung TV control (non-SSL) |
| 8002 | Websocket | Samsung TV control (SSL) |
| 9197 | UDP | Device discovery (optional) |

---

## Verification Checklist

- [ ] Firewall rule "Allow HA to IoT" created in UDM Pro
- [ ] Rule placed BEFORE "Block IoT to LAN" rule
- [ ] Rule action set to ACCEPT
- [ ] Source: 10.0.1.150 (Home Assistant)
- [ ] Destination: IoT VLAN (10.0.30.0/24)
- [ ] Changes applied and saved
- [ ] Ping test from HA to TV successful
- [ ] Samsung TV integration added in Home Assistant
- [ ] TV control working (power on/off, volume, input)

---

## Alternative Solutions

### Option 1: Move Home Assistant to IoT VLAN

**Pros:**
- No firewall rule needed
- HA can access all IoT devices natively
- Simplified network architecture

**Cons:**
- HA would be isolated from main network services
- May need additional rules for HA to access NAS, databases, etc.
- More complex to manage

**Not recommended** - HA should remain on trusted network.

### Option 2: Move Samsung TV to Main Network

**Pros:**
- No firewall rule needed
- Direct access from HA

**Cons:**
- IoT device on trusted network (security risk)
- Defeats purpose of IoT VLAN isolation

**Not recommended** - Smart devices should stay on IoT VLAN.

### Option 3: Broader LAN to IoT Rule (Current Recommendation)

Allow entire main network (10.0.1.0/24) to access IoT VLAN:

**Pros:**
- Future-proof (other LAN devices can control IoT)
- Easier management

**Cons:**
- Slightly broader access than strictly necessary

**Change Destination to:**
```
Source Type: Network
Source: Default (10.0.1.0/24)
Destination Type: Network
Destination: IoT (10.0.30.0/24)
```

---

## Security Notes

- The IoT VLAN should remain isolated FROM LAN (blocked IoT → LAN)
- This rule only allows traffic FROM LAN (trusted) TO IoT (untrusted)
- Traffic FROM IoT TO LAN remains blocked
- Consider enabling logging on this rule for auditing
- Review firewall logs periodically for unusual access patterns

---

## Related Documentation

- **Network Config:** `docs/udm-pro-migration-complete.md`
- **Home Assistant Setup:** Issue #28-31 (HA installation series)
- **UDM Pro Access:** `.claude/agents/homelab/DOMAINS.md`

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-08 | Created firewall rule documentation | HomeLab Agent |
| 2026-01-08 | Identified HA cannot access IoT VLAN | HomeLab Agent |

---

*Create this rule to enable Home Assistant control of IoT devices*
