# UDM Pro Migration Complete

**Date:** 2025-12-28
**Migration:** USG-Pro-4 + CloudKey → UDM Pro

---

## Summary

Successfully migrated from USG-Pro-4 with CloudKey to UDM Pro. Fresh installation with all devices re-adopted and network reconfigured.

## Network Configuration

### Networks

| Network | VLAN | Subnet | Gateway | DHCP Range |
|---------|------|--------|---------|------------|
| Management | 10 | 10.0.10.0/24 | 10.0.10.1 | 10.0.10.50-99 |
| Media | 20 | 10.0.20.0/24 | 10.0.20.1 | 10.0.20.50-250 |
| Default (Main) | - | 10.0.1.0/24 | 10.0.1.1 | 10.0.1.50-250 |
| IoT | 30 | 10.0.30.0/24 | 10.0.30.1 | 10.0.30.50-250 |
| Lab | 50 | 10.0.50.0/24 | 10.0.50.1 | 10.0.50.50-250 |

### Firewall Rules

| Rule | Action | Description |
|------|--------|-------------|
| Block IoT to LAN | DROP | Prevents IoT devices from accessing main network |
| Block IoT to Lab | DROP | Prevents IoT devices from accessing lab equipment |

## Infrastructure Devices (Management VLAN 10)

### Switches (4) - Fixed IPs

| Switch | IP | Port Count |
|--------|-----|------------|
| US 48 Dev Office | 10.0.10.10 | 48 |
| US 24 Dev Desk | 10.0.10.11 | 24 |
| US 24 PoE 250W Studio | 10.0.10.12 | 24 PoE |
| US 24 PoE 250W Cinema | 10.0.10.13 | 24 PoE |

### Access Points (7) - Fixed IPs

| AP | IP | Model |
|----|-----|-------|
| AC Pro #1 | 10.0.10.20 | UAP-AC-Pro |
| AC Pro #2 | 10.0.10.21 | UAP-AC-Pro |
| AC Pro #3 | 10.0.10.22 | UAP-AC-Pro |
| AC Pro #4 | 10.0.10.23 | UAP-AC-Pro |
| AC Pro #5 | 10.0.10.24 | UAP-AC-Pro |
| AC Pro #6 | 10.0.10.25 | UAP-AC-Pro |
| AC Pro #7 | 10.0.10.26 | UAP-AC-Pro |

### Gateway

- UDM Pro "Sunnybrae" (LAN: 10.0.1.1, WAN: 5.65.176.201)

## SCPI Equipment (Default LAN - Static IPs)

| Device | IP | MAC | Model |
|--------|-----|-----|-------|
| Keithley DMM | 10.0.1.101 | 08:00:11:23:73:27 | DMM6500 |
| Rigol PSU | 10.0.1.105 | 00:19:af:5b:b4:23 | DP832A |
| Rigol Scope | 10.0.1.106 | 00:19:af:7e:05:5b | MSO8204 |
| Rigol DC Load | 10.0.1.107 | 00:19:af:73:09:bc | DL3021A |
| Rigol PSU-1 | 10.0.1.111 | 00:19:af:93:04:f5 | DP932A |
| Rigol AWG | 10.0.1.120 | 00:19:af:8a:00:3e | DG2052 |
| Rigol PSU-2 | 10.0.1.138 | 00:19:af:93:06:46 | DP932A |
| Synology NAS | 10.0.1.251 | 90:09:d0:11:b4:b3 | - |

## WiFi Networks

| SSID | Network | Purpose |
|------|---------|---------|
| SUNNY-5G | Default | Main devices |
| ACP-WiFi | IoT (VLAN 30) | IoT devices |

## Access Credentials

- **UDM Pro URL:** https://10.0.1.1
- **Username:** admin
- **Password:** USAdman2350!@

## Migration Process

1. Connected to fresh UDM Pro on factory subnet (192.168.1.0/24)
2. SSH into all 11 UniFi devices with old CloudKey credentials
3. Factory reset devices to clear old adoption keys
4. Set-inform to new controller
5. Adopted all devices via API with CSRF token
6. Changed subnet from 192.168.1.0/24 to 10.0.1.0/24
7. Created DHCP reservations for SCPI equipment
8. Created IoT (VLAN 30) and Lab (VLAN 50) networks
9. Added firewall rules to isolate IoT
10. Created Management VLAN 10 for infrastructure
11. Assigned fixed IPs to all switches and APs

## Completed Items

- [x] All 11 UniFi devices adopted
- [x] SCPI equipment connectivity verified (8/8 online)
- [x] IoT devices on VLAN 30 (14 Wiz bulbs + others)
- [x] WiFi SSIDs configured
- [x] Management VLAN with fixed IPs for infrastructure

## Notes

- SCPI equipment has static IPs configured in firmware
- Old CloudKey can be decommissioned
- Clean CloudKey backup saved: `backups/cloudkey_clean_backup_20251228_004029.unf`

---

*Migration completed: 2025-12-28*
*Last updated: 2025-12-28 (added Management VLAN)*
