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
| Default (Main) | None | 10.0.1.0/24 | 10.0.1.1 | 10.0.1.50-250 |
| IoT | 30 | 10.0.30.0/24 | 10.0.30.1 | 10.0.30.50-250 |
| Lab | 50 | 10.0.50.0/24 | 10.0.50.1 | 10.0.50.50-250 |

### Firewall Rules

| Rule | Action | Description |
|------|--------|-------------|
| Block IoT to LAN | DROP | Prevents IoT devices from accessing main network |
| Block IoT to Lab | DROP | Prevents IoT devices from accessing lab equipment |

## Adopted Devices

### Switches (4)
- US 24 Dev Desk (10.0.1.142)
- US 24 PoE 250W Studio (10.0.1.203)
- US 24 PoE 250W Cinema (10.0.1.198)
- US 48 Dev Office (10.0.1.191)

### Access Points (7)
- AC Pro x7 (various IPs in 10.0.1.x range)

### Gateway
- UDM Pro "Sunnybrae" (WAN: 5.65.176.201)

## DHCP Reservations

| Device | IP | MAC |
|--------|-----|-----|
| Keithley-DMM6500 | 10.0.1.101 | 08:00:11:23:73:27 |
| Rigol-DCLoad | 10.0.1.105 | 00:19:af:5b:b4:23 |
| Rigol-MSO8204 | 10.0.1.106 | 00:19:af:7e:05:5b |
| Rigol-SpecAn | 10.0.1.107 | 00:19:af:73:09:bc |
| Rigol-PSU-1 | 10.0.1.111 | 00:19:af:93:04:f5 |
| Rigol-DG2052 | 10.0.1.120 | 00:19:af:8a:00:3e |
| Rigol-PSU-2 | 10.0.1.138 | 00:19:af:93:06:46 |
| Synology-NAS | 10.0.1.251 | 90:09:d0:11:b4:b3 |

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

## Outstanding Items

- [ ] Verify SCPI equipment connectivity (may need power cycle)
- [ ] Move IoT devices to VLAN 30
- [ ] Move lab equipment to VLAN 50 (optional)
- [ ] Configure WiFi SSIDs for each VLAN
- [ ] Test inter-VLAN routing for Lab

## Notes

- SCPI equipment has static IPs configured in firmware
- Equipment may need power cycle to reconnect after switch reprovisioning
- Old CloudKey can be decommissioned
- Clean CloudKey backup saved: `backups/cloudkey_clean_backup_20251228_004029.unf`

---

*Migration completed: 2025-12-28*
