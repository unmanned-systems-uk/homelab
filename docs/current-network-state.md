# Current Network State - USG to UDM Migration Audit

**Generated:** 2025-12-27
**Controller:** UniFi Controller v7.2.97 (CloudKey @ 10.0.1.2:8443)
**Purpose:** Pre-migration audit for USG Pro 4 replacement

---

## Executive Summary

| Metric | Count |
|--------|-------|
| UniFi Devices | 14 (12 online, 2 offline) |
| Access Points | 8 (7 online) |
| Switches | 5 (4 online) |
| Gateway | 1 (USG Pro 4) |
| Connected Clients | 54 |
| Static IP Reservations | 213 |
| Networks/VLANs | 5 |
| WiFi SSIDs | 4 |
| Port Forwards | 1 |
| Firewall Rules | 17 |

---

## Gateway (Migration Target)

| Property | Value |
|----------|-------|
| **Device** | Sunnybrae-Gateway |
| **Model** | UGW4 (USG Pro 4) |
| **IP** | 192.168.0.6 |
| **MAC** | 74:83:c2:1a:3a:2d |
| **Firmware** | v4.4.57 |
| **Status** | Online |

### WAN Interfaces

| Interface | Type | Purpose |
|-----------|------|---------|
| WAN1 | DHCP | Primary (900 Mbps down / 115 Mbps up) |
| WAN2 (4G) | DHCP | Failover backup |

---

## UniFi Devices Inventory

### Access Points (8)

| Name | Model | IP | MAC | Firmware | Status |
|------|-------|-----|-----|----------|--------|
| SUN-AC-Office | U7PG2 | 10.0.1.109 | fc:ec:da:1c:01:f6 | v6.6.77 | Online |
| Sun-AP-GarFl | U7PG2 | 10.0.1.19 | e0:63:da:ac:cd:e7 | v6.6.77 | Online |
| SUN-AP-AK-Bed | U7PG2 | 10.0.1.23 | e0:63:da:ac:ca:c6 | v6.6.77 | Online |
| SUN-AP-Chaple | U7PG2 | 10.0.1.29 | fc:ec:da:19:f5:e7 | v6.6.77 | Online |
| SUN-AP-Cinema | U7PG2 | 10.0.1.31 | e0:63:da:a9:f6:e4 | v6.6.77 | Online |
| SUN-AP-Studio-Bed | U7PG2 | 10.0.1.22 | e0:63:da:ac:cb:0e | v6.6.77 | Online |
| SUN-AP-Studio | U7PG2 | 10.0.1.21 | e0:63:da:ac:cc:11 | v6.6.77 | Online |
| ACP-AP-U6-Lite-HAAS-Hoose | UAL6 | 10.0.1.24 | 60:22:32:30:db:28 | v6.6.55 | **OFFLINE** |

### Switches (5)

| Name | Model | IP | MAC | Firmware | Status |
|------|-------|-----|-----|----------|--------|
| Sunnybrae-Office-SW1-48 | US48 | 10.0.1.78 | fc:ec:da:40:e6:cb | v7.1.26 | Online |
| Sunnybrae-Studio-SW2-24-PoE | US24P250 | 10.0.1.137 | 78:8a:20:f9:d2:8c | v7.1.26 | Online |
| Sunnybrae-Cinema-SW3-24-POE | US24P250 | 10.0.1.140 | 78:8a:20:bf:5b:98 | v7.1.26 | Online |
| SUN-Office-Dev-Desk | US24 | 10.0.1.193 | b4:fb:e4:2e:f2:75 | v7.2.123 | Online |
| USW-Flex-5-port-SW-HAAS Hoose | USMINI | 10.0.1.162 | d0:21:f9:bd:d2:23 | v2.1.3 | **OFFLINE** |

---

## Network Configuration

### LAN Networks

| Name | Subnet | DHCP Range | VLAN | Purpose |
|------|--------|------------|------|---------|
| Sunnybrae | 10.0.1.0/24 | 10.0.1.6 - 10.0.1.254 | None (native) | Main LAN |

### VPN Configurations

| Name | Type | Status | Notes |
|------|------|--------|-------|
| ~~Selkirk~~ | ~~OpenVPN Site-to-Site~~ | **DEPRECATED** | No longer required for migration |
| VPN Server | L2TP | Disabled | Not in use |

**Note:** Site-to-site VPN to Selkirk is deprecated and not required for UDM migration.

---

## WiFi Configuration

### SSIDs

| SSID | Security | Band | Guest | Network | Password |
|------|----------|------|-------|---------|----------|
| ACP-Guest | Open | 2.4G + 5G | Yes | Sunnybrae | N/A |
| ACP-WiFi | WPA2-PSK | 2.4G only | No | Sunnybrae | `acpadman` |
| SUNNY-5G | WPA2-PSK | 5G only | No | Sunnybrae | `acpadman` |
| dev-24g | WPA2-PSK | 2.4G only | No | Sunnybrae | `dev-24g-2350` |

---

## Port Forwards

| Name | External Port | Internal IP | Internal Port | Protocol |
|------|---------------|-------------|---------------|----------|
| Nathan | 27015 | 10.0.1.40 | 27015 | TCP/UDP |

---

## Firewall Rules

### Custom Rules

| Name | Ruleset | Action | Source | Destination |
|------|---------|--------|--------|-------------|
| Block ACP-NAS | WAN_IN | Reject | 10.0.0.151 | 10.0.0.151 |

### IPS Deny List (Auto-Generated)

16 IPS-generated block rules for malicious IPs targeting:
- 10.0.1.40 (Nathan's gaming server)
- 10.0.1.77

Blocked IPs:
- 46.38.253.161
- 144.6.197.157
- 15.204.223.128
- 94.23.76.244
- 192.42.132.106
- 141.145.201.126

---

## DHCP Configuration

| Setting | Value |
|---------|-------|
| DHCP Range | 10.0.1.6 - 10.0.1.254 |
| Lease Time | 86400 seconds (24 hours) |
| Static Reservations | 213 clients |
| Gateway | 10.0.1.1 (default) |
| mDNS | Enabled |
| NAT | Enabled |

---

## Migration Checklist

### Pre-Migration Tasks

- [x] Network device inventory complete
- [x] WiFi configuration documented
- [x] Port forwards documented
- [x] Firewall rules documented
- [x] VPN configurations documented
- [ ] Backup current controller configuration
- [ ] Document DHCP static reservations (213 entries)
- [ ] Verify site-to-site VPN partner readiness

### Migration Considerations

1. ~~**Site-to-Site VPN:**~~ **DEPRECATED** - Selkirk VPN no longer required
2. **4G Failover:** WAN2 failover configuration must be recreated
3. **IPS Rules:** 16 auto-generated firewall rules from Threat Management
4. **Static IPs:** 213 DHCP reservations to migrate
5. **Port Forward:** Gaming server on 10.0.1.40 (port 27015)

### UDM Feature Compatibility

| Feature | USG Pro 4 | UDM-SE | Notes |
|---------|-----------|--------|-------|
| Dual WAN | Yes | Yes | Failover supported |
| Site-to-Site VPN | OpenVPN | WireGuard/OpenVPN | May require reconfiguration |
| IPS/IDS | Yes | Yes | Enhanced on UDM |
| CloudKey Required | Yes | No | Integrated controller |

---

## Raw Data Location

All raw API exports are stored in:
```
/home/anthony/ccpm-workspace/HomeLab/audit-data/
├── devices.json         # UniFi hardware (357 KB)
├── clients.json         # Connected clients (72 KB)
├── networks.json        # Network/VLAN config (4 KB)
├── firewall-rules.json  # Firewall rules (11 KB)
├── port-forwards.json   # Port forwarding (252 B)
├── wlan-configs.json    # WiFi SSIDs (6 KB)
├── site-settings.json   # Site configuration (13 KB)
├── static-clients.json  # DHCP reservations (69 KB)
├── system-info.json     # Controller info (2 KB)
└── health.json          # Health status (2 KB)
```

---

## Next Steps

1. **Restart Claude Code:** Load MCP server from .mcp.json
2. **Test MCP Tools:** Verify `unifi_tool_index` lists 81 tools
3. **Choose UDM Model:** UDM-SE recommended for multi-WAN and PoE
4. **Export Controller Backup:** Settings > System > Backup
5. **Schedule Migration Window:** Recommend off-hours (minimal client impact)
6. **Test Plan:** Verify all services post-migration

---

*Generated by HomeLab Network Audit Script*
*GitHub Issue: #17*
