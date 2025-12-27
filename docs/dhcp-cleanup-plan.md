# DHCP Cleanup Plan - CloudKey

**Generated:** 2025-12-27 23:39:04
**Status:** AWAITING USER APPROVAL

---

## Summary

| Metric | Count |
|--------|-------|
| Total Entries | 213 |
| **To DELETE** | **43** |
| To KEEP | 170 |

### Deletion Breakdown

| Category | Count | Description |
|----------|-------|-------------|
| A - Old Subnet | 5 | 192.168.x.x entries (deprecated) |
| B - Deprecated HW | 11 | Sky boxes, Netgear, old Dell servers |
| C - IoT (VLAN 30) | 27 | Smart home devices moving to IoT VLAN |
| D - Stale | 0 | Not seen in 90+ days |
| **TOTAL** | **43** | |

---

## ENTRIES TO DELETE

### Category A: Old Subnet (192.168.x.x)

| MAC | Name | Fixed IP | Reason |
|-----|------|----------|--------|
| `2c:b0:5d:a7:89:28` | Netgear AP2-Studio | 192.168.1.102 | Old subnet: 192.168.1.102 |
| `2c:b0:5d:a7:7e:e8` | Netgere AP Chapel | 192.168.1.101 | Old subnet: 192.168.1.101 |
| `d2:2c:7e:08:ce:7a` | Netgear_AP_ | 192.168.1.104 | Old subnet: 192.168.1.104 |
| `28:c6:8e:07:e4:68` | Netgere AP Cinema | 192.168.1.105 | Old subnet: 192.168.1.105 |
| `48:ba:4e:ff:e0:1e` | Officejet 7610 | 192.168.1.60 | Old subnet: 192.168.1.60 |

### Category B: Deprecated Hardware

| MAC | Name | Fixed IP | Reason |
|-----|------|----------|--------|
| `c0:3e:0f:48:0c:fd` | Sky Box1 | N/A | Deprecated hardware: sky box1 |
| `00:19:fb:e8:5f:6c` | Sky Box2 | N/A | Deprecated hardware: sky box2 |
| `a4:ba:db:2e:57:09` | Dell-server-1-maintanance | N/A | Deprecated hardware: dell-server-1-maintanance |
| `00:0c:29:de:d8:54` | Dell-Server-1-Samba | 10.0.1.14 | Deprecated hardware: dell-server-1-samba |
| `d0:58:fc:10:ce:78` | SKY Q 1-b | N/A | Deprecated hardware: sky q 1-b |
| `d0:58:fc:10:ce:7a` | SKY Q 1-a | N/A | Deprecated hardware: sky q 1-a |
| `d0:67:e5:f3:b5:88` | Del-R710-1-VM | 10.0.1.11 | Deprecated hardware: del-r710-1-vm |
| `00:0c:29:01:e0:ba` | Dell-R710-GIT-1 | 10.0.1.13 | Deprecated hardware: dell-r710-git-1 |
| `76:45:6f:a9:d8:ce` | Skypad (Paul Kerry) | 10.0.3.248 | Deprecated hardware: skypad (paul kerry) |
| `de:2b:db:b1:8e:f7` | SkyPhone (Paul Kerry) | 10.0.3.243 | Deprecated hardware: skyphone (paul kerry) |
| `d6:30:bc:3a:7e:d6` | Skydroid Receiver | N/A | Deprecated hardware: skydroid receiver |

### Category C: IoT Devices (Moving to VLAN 30)

| MAC | Name | Fixed IP | Online | Reason |
|-----|------|----------|--------|--------|
| `cc:a7:c1:44:ea:a9` | NEST Therm Office | 10.0.1.73 | YES | IoT device - moving to VLAN 30 |
| `00:09:b0:47:d4:d0` | Onkyo | N/A | YES | IoT device - moving to VLAN 30 |
| `44:4f:8e:25:eb:7e` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `44:4f:8e:25:e9:88` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `cc:40:85:46:a0:f8` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `cc:40:85:46:7e:84` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `14:c1:4e:32:15:53` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `c0:e7:bf:63:55:08` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `00:0e:58:a3:b5:ac` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `64:9a:63:c7:a4:ec` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `34:94:54:cd:a6:50` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `18:de:50:24:95:94` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `a8:bb:50:bf:49:ab` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `98:77:d5:0e:1c:6a` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `18:de:50:24:9b:bb` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `fc:03:9f:ea:fd:90` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `fc:d7:49:a0:7e:bf` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `a8:bb:50:bf:23:98` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `14:c1:4e:c4:e2:e2` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `6c:29:90:af:49:2e` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `a8:bb:50:bf:37:9e` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `a8:bb:50:bf:2d:c3` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `a8:bb:50:bf:09:e5` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `a8:bb:50:bf:37:27` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `98:77:d5:0e:11:60` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `98:77:d5:0e:1a:ba` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |
| `98:77:d5:0e:11:d6` | Unknown | N/A | YES | IoT device - moving to VLAN 30 |

### Category D: Stale/Offline (90+ days)

*None identified (devices caught in other categories)*

---

## ENTRIES TO KEEP (Protected)

### Critical Infrastructure (DO NOT DELETE)

| MAC | Name | Fixed IP | Status |
|-----|------|----------|--------|
| `78:8a:20:df:04:77` | UniFi Cloud Key | N/A | ONLINE |
| `50:eb:f6:82:3e:92` | Unknown | N/A | ONLINE |
| `90:09:d0:11:b4:b3` | Synology DS1621 | 10.0.1.251 | ONLINE |
| `40:16:7e:a5:0d:51` | Unknown | N/A | ONLINE |
| `bc:24:11:59:92:15` | Unknown | N/A | ONLINE |

### SCPI Test Equipment (DO NOT DELETE)

| MAC | Name | Fixed IP | Status |
|-----|------|----------|--------|
| `08:00:11:23:73:27` | Keathley DMM6500-1 | 10.0.1.101 | ONLINE |
| `00:19:af:93:06:46` | Rigol DP932A-1 | 10.0.1.111 | ONLINE |
| `00:19:af:5b:b4:23` | Rigol DP832A-1 | 10.0.1.112 | ONLINE |
| `00:19:af:73:09:bc` | Rigol DL3021A-1 | 10.0.1.105 | ONLINE |
| `00:19:af:7e:05:5b` | RIGOL MSO8204 | 10.0.1.106 | ONLINE |
| `00:19:af:75:03:ac` | RIGOL RSA5065N | 10.0.1.107 | ONLINE |
| `00:19:af:8a:00:3e` | Unknown | N/A | ONLINE |
| `00:19:af:93:04:f5` | Unknown | N/A | ONLINE |

### Development Hardware (DO NOT DELETE)

| MAC | Name | Fixed IP | Status |
|-----|------|----------|--------|
| `70:4d:7b:62:a0:de` | Dev-Office-PC-1 | 10.0.1.37 | ONLINE |
| `d8:bb:c1:9a:e1:0c` | Unknown | 10.0.1.83 | ONLINE |
| `dc:a6:32:c8:b8:b9` | Unknown | N/A | ONLINE |

### UniFi Network Devices (DO NOT DELETE)

| MAC | Name | Fixed IP | Status |
|-----|------|----------|--------|
| `78:8a:20:98:32:cd` | ACP-Bridge-Station-1 | N/A | ONLINE |
| `78:8a:20:98:31:cc` | ACP-Bridge-AP-1 | 10.0.0.18 | ONLINE |
| `b4:fb:e4:2e:f2:76` | Unknown | N/A | ONLINE |

### Other Active Devices (151 entries)

*These devices are active and not categorized for deletion.*

---

## APPROVAL REQUIRED

**Review the entries above carefully.**

To proceed with cleanup, respond with:

```
APPROVED - PROCEED WITH CLEANUP
```

This will delete **43 entries** from the CloudKey DHCP reservations.

---

*Safety backup saved to: docs/dhcp-reservations-before-cleanup.json*