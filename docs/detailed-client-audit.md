# Detailed Client Audit for UDM Migration

**Generated:** 2025-12-27
**Total Online Clients:** 63
**Static DHCP Reservations:** 213
**Purpose:** VLAN planning for USG Pro 4 to UDM-SE migration

---

## 1. SSID Client Breakdown

### ACP-WiFi (2.4GHz Primary) - 37 Clients

| Hostname | IP | MAC | Device Type |
|----------|-----|-----|-------------|
| wiz_0e1aba | 10.0.1.131 | 98:77:d5:0e:1a:ba | Wiz Smart Bulb |
| wiz_bf2398 | 10.0.1.95 | a8:bb:50:bf:23:98 | Wiz Smart Bulb |
| wiz_467e84 | 10.0.1.84 | cc:40:85:46:7e:84 | Wiz Smart Bulb |
| wiz_af492e | 10.0.1.76 | 6c:29:90:af:49:2e | Wiz Smart Bulb |
| wiz_25e988 | 10.0.1.88 | 44:4f:8e:25:e9:88 | Wiz Smart Bulb |
| wiz_0e1160 | 10.0.1.164 | 98:77:d5:0e:11:60 | Wiz Smart Bulb |
| wiz_bf2dc3 | 10.0.1.67 | a8:bb:50:bf:2d:c3 | Wiz Smart Bulb |
| wiz_bf09e5 | 10.0.1.203 | a8:bb:50:bf:09:e5 | Wiz Smart Bulb |
| wiz_bf3727 | 10.0.1.18 | a8:bb:50:bf:37:27 | Wiz Smart Bulb |
| wiz_25eb7e | 10.0.1.89 | 44:4f:8e:25:eb:7e | Wiz Smart Bulb |
| wiz_46a0f8 | 10.0.1.80 | cc:40:85:46:a0:f8 | Wiz Smart Bulb |
| wiz_bf379e | 10.0.1.155 | a8:bb:50:bf:37:9e | Wiz Smart Bulb |
| wiz_0e11d6 | 10.0.1.36 | 98:77:d5:0e:11:d6 | Wiz Smart Bulb |
| wiz_bf49ab | 10.0.1.10 | a8:bb:50:bf:49:ab | Wiz Smart Bulb |
| Google-Nest-Mini | 10.0.1.66 | 14:c1:4e:32:15:53 | Smart Speaker |
| Google-Nest-Mini | 10.0.1.35 | 14:c1:4e:c4:e2:e2 | Smart Speaker |
| NEST Therm Office | 10.0.1.73 | cc:a7:c1:44:ea:a9 | Smart Thermostat |
| Emporia | 10.0.1.129 | 34:94:54:cd:a6:50 | Energy Monitor |
| RingDoorbell-ec | 10.0.1.49 | 64:9a:63:c7:a4:ec | Video Doorbell |
| nixplay_W10F-09 | 10.0.1.27 | c0:e7:bf:63:55:08 | Digital Frame |
| TIZEN | 10.0.1.124 | fc:03:9f:ea:fd:90 | Samsung Smart TV |
| wlan0 | 10.0.1.104 | 18:de:50:24:95:94 | ESP/IoT Device |
| wlan0 | 10.0.1.99 | 18:de:50:24:9b:bb | ESP/IoT Device |
| Samsung | 10.0.1.43 | f0:70:4f:6a:0e:22 | Samsung Device |
| Galaxy-S9 | 10.0.1.50 | 56:3a:6d:c1:22:a5 | Phone |
| Anthony-s-Z-Fold4 | 10.0.1.239 | ca:e9:aa:e8:e4:fa | Phone |
| Andrea-s-A10 | 10.0.1.60 | f6:32:92:35:4c:13 | Phone |
| 101584733 | 10.0.1.59 | 84:7a:b6:96:00:83 | Unknown Device |
| Unknown | 10.0.1.38 | 66:f1:8b:21:d5:cf | Unknown |
| Unknown | 10.0.1.252 | 9c:37:cb:cd:8a:d6 | Unknown |
| Unknown | 10.0.1.6 | 12:1e:d4:0c:15:44 | Unknown |
| Unknown | 10.0.1.215 | d8:d6:68:e2:f4:b5 | Unknown |

### SUNNY-5G (5GHz Primary) - 7 Clients

| Hostname | IP | MAC | Device Type |
|----------|-----|-----|-------------|
| Anthony-s-Tab-S8-Ultra | 10.0.1.7 | fa:15:80:15:e1:d7 | Tablet |
| Michael-s-S24-Ultra | 10.0.1.79 | f2:e1:96:21:8b:37 | Phone |
| Tamara-s-S22-Ultra | 10.0.1.25 | 5e:83:92:00:f2:e3 | Phone |
| SM-R950 | 10.0.1.8 | ea:79:49:5b:bd:02 | Galaxy Watch |
| echoshow-eeb2a2156e769f5e | 10.0.1.110 | fc:d7:49:a0:7e:bf | Echo Show |
| Unknown | 10.0.1.154 | 48:31:77:04:ab:ac | Unknown |

### ACP-Guest - 1 Client

| Hostname | IP | MAC | Device Type |
|----------|-----|-----|-------------|
| Galaxy-Tab-A-2016 | 10.0.1.71 | 00:b5:d0:cb:d1:a7 | Tablet (Guest) |

### Wired Connections - 18 Clients

| Hostname | IP | MAC | Device Type |
|----------|-----|-----|-------------|
| UniFi Cloud Key | 10.0.1.2 | 78:8a:20:df:04:77 | Network Controller |
| Synology DS1621 | 10.0.1.251 | 90:09:d0:11:b4:b3 | NAS |
| ubuntu-server | 10.0.1.210 | bc:24:11:59:92:15 | Server (CCPM) |
| MCP Container | 10.0.1.159 | bc:24:11:2d:4a:b8 | LXC Container |
| Proxmox (pve-ai) | 10.0.1.200 | 40:16:7e:a5:0d:51 | Hypervisor |
| Dev-Office-PC-1 | 10.0.1.37 | 70:4d:7b:62:a0:de | Windows 11 PC |
| DEV-PC-Ubuntu | 10.0.1.83 | d8:bb:c1:9a:e1:0c | Ubuntu PC |
| RF-WEB | 10.0.1.98 | dc:a6:32:c8:b8:b9 | Raspberry Pi 4 |
| lag | 10.0.1.151 | bc:24:11:6b:e1:39 | Server |
| lag | 10.0.1.40 | 50:eb:f6:82:3e:92 | Gaming Server |
| SonosZP | 10.0.1.55 | 00:0e:58:a3:b5:ac | Sonos Speaker |
| Onkyo | 10.0.1.54 | 00:09:b0:47:d4:d0 | AV Receiver |
| Keithley DMM6500-1 | 10.0.1.101 | 08:00:11:23:73:27 | SCPI DMM |
| Rigol DP832A-1 | 10.0.1.112 | 00:19:af:5b:b4:23 | SCPI PSU |
| Rigol DL3021A-1 | 10.0.1.105 | 00:19:af:73:09:bc | SCPI DC Load |
| Rigol DP932A-1 | 10.0.1.111 | 00:19:af:93:06:46 | SCPI PSU |
| Rigol (DP932A-2) | 10.0.1.138 | 00:19:af:93:04:f5 | SCPI PSU |
| RIGOL MSO8204 | Unknown | 00:19:af:7e:05:5b | SCPI Scope |
| DG2000 (AWG) | Unknown | 00:19:af:8a:00:3e | SCPI AWG |
| 10.0.0.153 | 10.0.1.45 | 0c:f9:c0:66:c9:92 | Network Device |
| Unknown | 10.0.1.47 | 0c:f9:c0:84:0b:a2 | Network Device |

---

## 2. Wiz Bulb Identification

**Total Wiz Devices: 14**
**All on SSID: ACP-WiFi**
**VLAN Target: VLAN 30 (IoT)**

### MAC Vendor Prefixes Identified

| Prefix | Vendor | Count |
|--------|--------|-------|
| 98:77:d5 | Wiz Connected | 3 |
| a8:bb:50 | Wiz Connected | 6 |
| cc:40:85 | Wiz Connected | 2 |
| 44:4f:8e | Wiz Connected | 2 |
| 6c:29:90 | Wiz Connected | 1 |

### Complete Wiz Device List

| Hostname | IP | MAC | Signal (dBm) | Channel |
|----------|-----|-----|--------------|---------|
| wiz_0e1aba | 10.0.1.131 | 98:77:d5:0e:1a:ba | -75 | 11 |
| wiz_0e1160 | 10.0.1.164 | 98:77:d5:0e:11:60 | -81 | 1 |
| wiz_0e11d6 | 10.0.1.36 | 98:77:d5:0e:11:d6 | -61 | 1 |
| wiz_bf2398 | 10.0.1.95 | a8:bb:50:bf:23:98 | -61 | 1 |
| wiz_bf2dc3 | 10.0.1.67 | a8:bb:50:bf:2d:c3 | -78 | 11 |
| wiz_bf09e5 | 10.0.1.203 | a8:bb:50:bf:09:e5 | -60 | 1 |
| wiz_bf3727 | 10.0.1.18 | a8:bb:50:bf:37:27 | -71 | 1 |
| wiz_bf379e | 10.0.1.155 | a8:bb:50:bf:37:9e | -74 | 11 |
| wiz_bf49ab | 10.0.1.10 | a8:bb:50:bf:49:ab | -54 | 1 |
| wiz_467e84 | 10.0.1.84 | cc:40:85:46:7e:84 | -47 | 1 |
| wiz_46a0f8 | 10.0.1.80 | cc:40:85:46:a0:f8 | -50 | 1 |
| wiz_25e988 | 10.0.1.88 | 44:4f:8e:25:e9:88 | -44 | 1 |
| wiz_25eb7e | 10.0.1.89 | 44:4f:8e:25:eb:7e | -48 | 1 |
| wiz_af492e | 10.0.1.76 | 6c:29:90:af:49:2e | -35 | 1 |

### Signal Quality Analysis

- **Excellent (-35 to -50 dBm):** 5 bulbs
- **Good (-51 to -65 dBm):** 4 bulbs
- **Fair (-66 to -75 dBm):** 3 bulbs
- **Poor (-76 to -85 dBm):** 2 bulbs (wiz_0e1160, wiz_bf2dc3)

---

## 3. IoT Device Inventory

**VLAN 30 (IoT) Candidates: 28 devices**

### Smart Lighting (14)

All Wiz bulbs listed in Section 2 above.

### Smart Home Devices (8)

| Device | IP | MAC | Category | VLAN 30 |
|--------|-----|-----|----------|---------|
| Google-Nest-Mini | 10.0.1.66 | 14:c1:4e:32:15:53 | Voice Assistant | YES |
| Google-Nest-Mini | 10.0.1.35 | 14:c1:4e:c4:e2:e2 | Voice Assistant | YES |
| NEST Therm Office | 10.0.1.73 | cc:a7:c1:44:ea:a9 | Climate Control | YES |
| Emporia | 10.0.1.129 | 34:94:54:cd:a6:50 | Energy Monitor | YES |
| RingDoorbell-ec | 10.0.1.49 | 64:9a:63:c7:a4:ec | Security | YES |
| echoshow-eeb2a2156e769f5e | 10.0.1.110 | fc:d7:49:a0:7e:bf | Voice Assistant | YES |
| nixplay_W10F-09 | 10.0.1.27 | c0:e7:bf:63:55:08 | Digital Frame | YES |
| wlan0 (x2) | 10.0.1.99/104 | 18:de:50:* | ESP/IoT Sensor | YES |

### Entertainment Devices (3)

| Device | IP | MAC | Category | VLAN 30 |
|--------|-----|-----|----------|---------|
| SonosZP | 10.0.1.55 | 00:0e:58:a3:b5:ac | Audio | YES |
| TIZEN (Samsung TV) | 10.0.1.124 | fc:03:9f:ea:fd:90 | Smart TV | YES |
| Onkyo | 10.0.1.54 | 00:09:b0:47:d4:d0 | AV Receiver | YES |

### Personal Devices - NOT for IoT VLAN (7)

| Device | IP | MAC | Category | Notes |
|--------|-----|-----|----------|-------|
| Anthony-s-Tab-S8-Ultra | 10.0.1.7 | fa:15:80:15:e1:d7 | Tablet | Keep on main |
| Anthony-s-Z-Fold4 | 10.0.1.239 | ca:e9:aa:e8:e4:fa | Phone | Keep on main |
| Tamara-s-S22-Ultra | 10.0.1.25 | 5e:83:92:00:f2:e3 | Phone | Keep on main |
| Michael-s-S24-Ultra | 10.0.1.79 | f2:e1:96:21:8b:37 | Phone | Keep on main |
| Galaxy-S9 | 10.0.1.50 | 56:3a:6d:c1:22:a5 | Phone | Keep on main |
| Andrea-s-A10 | 10.0.1.60 | f6:32:92:35:4c:13 | Phone | Keep on main |
| SM-R950 | 10.0.1.8 | ea:79:49:5b:bd:02 | Watch | Keep on main |

---

## 4. Lab Equipment Detection

**VLAN 50 (Lab) Candidates: 11 devices**

### SCPI Test Equipment (7)

| Device | Expected IP | Actual IP | MAC | Status |
|--------|-------------|-----------|-----|--------|
| Keithley DMM6500 | 10.0.1.101 | 10.0.1.101 | 08:00:11:23:73:27 | ONLINE |
| Rigol DL3021A (DC Load) | 10.0.1.105 | 10.0.1.105 | 00:19:af:73:09:bc | ONLINE |
| Rigol MSO8204 (Scope) | 10.0.1.106 | Unknown* | 00:19:af:7e:05:5b | ONLINE (no IP) |
| Rigol DP932A-1 (PSU) | 10.0.1.111 | 10.0.1.111 | 00:19:af:93:06:46 | ONLINE |
| Rigol DP832A-1 (PSU) | 10.0.1.112 | 10.0.1.112 | 00:19:af:5b:b4:23 | ONLINE |
| Rigol DG2052 (AWG) | 10.0.1.120 | Unknown* | 00:19:af:8a:00:3e | ONLINE (no IP) |
| Rigol DP932A-2 (PSU) | 10.0.1.138 | 10.0.1.138 | 00:19:af:93:04:f5 | ONLINE |

*Note: RIGOL MSO8204 and DG2000 show online but UniFi reports "Unknown" IP - may need static DHCP reservation check.

### MAC Vendor Prefixes

| Prefix | Vendor | Equipment Type |
|--------|--------|----------------|
| 08:00:11 | Keithley Instruments | DMM |
| 00:19:af | Rigol Technologies | PSU/Scope/Load/AWG |

### Development Boards (2)

| Device | IP | MAC | Type | Status |
|--------|-----|-----|------|--------|
| RF-WEB | 10.0.1.98 | dc:a6:32:c8:b8:b9 | Raspberry Pi 4 | ONLINE |
| DPM Pi 5 | 10.0.1.53 | (not in current scan) | Raspberry Pi 5 | NOT SEEN |
| Jetson Orin NX | 10.0.1.113 | (not in current scan) | NVIDIA Jetson | NOT SEEN |

### Development PCs (2)

| Device | IP | MAC | Type | Notes |
|--------|-----|-----|------|-------|
| Dev-Office-PC-1 | 10.0.1.37 | 70:4d:7b:62:a0:de | Windows 11 | VLAN 50 candidate |
| DEV-PC-Ubuntu | 10.0.1.83 | d8:bb:c1:9a:e1:0c | Ubuntu | VLAN 50 candidate |

---

## 5. DHCP Static Clients Analysis

**Total Reservations: 213**
**Currently Online: 63**
**Match Rate: ~30%**

### Critical Infrastructure (ONLINE)

| Name | IP | MAC | Purpose | Status |
|------|-----|-----|---------|--------|
| UniFi Cloud Key | 10.0.1.2 | 78:8a:20:df:04:77 | Network Controller | CRITICAL |
| Synology DS1621 | 10.0.1.251 | 90:09:d0:11:b4:b3 | NAS/Storage | CRITICAL |
| ubuntu-server | 10.0.1.210 | bc:24:11:59:92:15 | CCPM Server | CRITICAL |
| Proxmox (pve-ai) | 10.0.1.200 | 40:16:7e:a5:0d:51 | Hypervisor | CRITICAL |
| MCP Container | 10.0.1.159 | bc:24:11:2d:4a:b8 | UniFi MCP | CRITICAL |
| lag (game server) | 10.0.1.40 | 50:eb:f6:82:3e:92 | Game Server | HIGH |

### Lab Equipment (ONLINE)

All SCPI equipment from Section 4 - maintain static IPs on VLAN 50.

### Deprecated/Stale Reservations (from audit)

Based on static-clients.json analysis, many reservations are for:

| Category | Count | Notes |
|----------|-------|-------|
| Old 192.168.x.x subnet | ~20 | Migration remnants |
| Sky boxes (deprecated) | 4 | No longer in use |
| Old Netgear APs | 4 | Replaced by UniFi |
| Former employee devices | ~10 | Should be removed |
| Old Dell servers | 5 | VMs migrated to Proxmox |
| Retired phones | ~15 | No longer on network |

### Recommended Cleanup Actions

1. **Remove 192.168.x.x reservations** - Old subnet no longer in use
2. **Remove Sky box entries** - Service canceled
3. **Remove Netgear AP entries** - Replaced by UniFi APs
4. **Archive former employee devices** - Create backup list first
5. **Consolidate duplicate entries** - Some MACs have multiple reservations

---

## 6. VLAN Migration Summary

### Proposed VLAN Structure

| VLAN ID | Name | Subnet | Purpose | Device Count |
|---------|------|--------|---------|--------------|
| 1 | Default | 10.0.1.0/24 | Main LAN | ~30 |
| 30 | IoT | 10.0.30.0/24 | Smart Home | ~28 |
| 50 | Lab | 10.0.50.0/24 | Test Equipment | ~11 |

### VLAN 30 (IoT) Migration List

```
# Smart Bulbs (14)
98:77:d5:* → VLAN 30 (Wiz)
a8:bb:50:* → VLAN 30 (Wiz)
cc:40:85:* → VLAN 30 (Wiz)
44:4f:8e:* → VLAN 30 (Wiz)
6c:29:90:* → VLAN 30 (Wiz)

# Smart Home (8)
14:c1:4e:* → VLAN 30 (Google Nest)
cc:a7:c1:* → VLAN 30 (Nest Thermostat)
34:94:54:* → VLAN 30 (Emporia)
64:9a:63:* → VLAN 30 (Ring)
fc:d7:49:* → VLAN 30 (Amazon Echo)
c0:e7:bf:* → VLAN 30 (Nixplay)
18:de:50:* → VLAN 30 (ESP devices)

# Entertainment (3)
00:0e:58:* → VLAN 30 (Sonos)
fc:03:9f:* → VLAN 30 (Samsung TV)
00:09:b0:* → VLAN 30 (Onkyo)
```

### VLAN 50 (Lab) Migration List

```
# SCPI Equipment
08:00:11:* → VLAN 50 (Keithley)
00:19:af:* → VLAN 50 (Rigol)

# Dev Boards
dc:a6:32:* → VLAN 50 (Raspberry Pi)
# Add Jetson when discovered

# Dev PCs (optional)
70:4d:7b:62:a0:de → VLAN 50 (Dev-Office-PC-1)
d8:bb:c1:9a:e1:0c → VLAN 50 (DEV-PC-Ubuntu)
```

---

## 7. Action Items for Migration

- [ ] Create VLAN 30 (IoT) on UDM-SE
- [ ] Create VLAN 50 (Lab) on UDM-SE
- [ ] Configure IoT SSID for VLAN 30
- [ ] Configure Lab SSID for VLAN 50 (or wired-only)
- [ ] Create firewall rules: IoT → Internet only
- [ ] Create firewall rules: Lab → Main LAN + Internet
- [ ] Migrate MAC-based VLAN assignments
- [ ] Update SCPI device static IPs to 10.0.50.x
- [ ] Clean up deprecated DHCP reservations
- [ ] Document new IP scheme

---

*Generated from UniFi Controller via MCP*
*GitHub Issue: https://github.com/unmanned-systems-uk/homelab/issues/17*
