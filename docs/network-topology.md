# Network Topology - Sunnybrae

**Generated:** 2025-12-27
**Total Devices:** 14 (12 online, 2 offline)

---

## Physical Topology

```
                                    ┌─────────────────┐
                                    │    INTERNET     │
                                    └────────┬────────┘
                                             │
                              ┌──────────────┴──────────────┐
                              │      ISP Router            │
                              │      192.168.0.1           │
                              └──────────────┬──────────────┘
                                             │
                    ┌────────────────────────┴────────────────────────┐
                    │                                                 │
            ┌───────┴───────┐                                ┌────────┴───────┐
            │    WAN1       │                                │    WAN2 (4G)   │
            │   Primary     │                                │    Failover    │
            └───────┬───────┘                                └────────┬───────┘
                    │                                                 │
                    └────────────────────┬────────────────────────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         │   USG Pro 4 (Sunnybrae-GW)    │
                         │   Model: UGW4                 │
                         │   IP: 192.168.0.6             │
                         │   Firmware: 4.4.57            │
                         │   [MIGRATION TARGET]          │
                         └───────────────┬───────────────┘
                                         │
                                         │ LAN (10.0.1.x)
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
    ┌───────┴───────┐           ┌────────┴────────┐          ┌────────┴────────┐
    │  CloudKey     │           │ SW1-48 (Office) │          │   Other Switches │
    │  10.0.1.2     │           │ US48            │          │   (via uplinks)  │
    │  Controller   │           │ 10.0.1.78       │          └─────────────────┘
    └───────────────┘           └────────┬────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────┐
        │                                │                            │
┌───────┴───────┐               ┌────────┴────────┐          ┌────────┴────────┐
│ SW2-24-PoE    │               │ SW3-24-PoE      │          │ Dev-Desk SW     │
│ (Studio)      │               │ (Cinema)        │          │ US24            │
│ US24P250      │               │ US24P250        │          │ 10.0.1.193      │
│ 10.0.1.137    │               │ 10.0.1.140      │          └────────┬────────┘
└───────┬───────┘               └────────┬────────┘                   │
        │                                │                    ┌───────┴───────┐
        │                                │                    │ SUN-AC-Office │
┌───────┴───────┐               ┌────────┴────────┐          │ U7PG2         │
│ Studio APs    │               │ Cinema AP       │          │ 10.0.1.109    │
│               │               │                 │          └───────────────┘
│ SUN-AP-Studio │               │ SUN-AP-Cinema   │
│ 10.0.1.21     │               │ U7PG2           │
│               │               │ 10.0.1.31       │
│ SUN-AP-Studio │               └─────────────────┘
│ -Bed          │
│ 10.0.1.22     │
└───────────────┘


                    ┌─────────────────────────────────────┐
                    │         REMOTE LOCATION             │
                    │         (HAAS Hoose)                │
                    │         [OFFLINE]                   │
                    │                                     │
                    │  ┌───────────────┐  ┌────────────┐  │
                    │  │ USW-Flex-5    │  │ AP-U6-Lite │  │
                    │  │ USMINI        │  │ UAL6       │  │
                    │  │ 10.0.1.162    │  │ 10.0.1.24  │  │
                    │  │ [OFFLINE]     │  │ [OFFLINE]  │  │
                    │  └───────────────┘  └────────────┘  │
                    └─────────────────────────────────────┘
```

---

## Device Summary

### Gateway (1)
| Name | Model | IP | Status |
|------|-------|-----|--------|
| Sunnybrae-Gateway | UGW4 | 192.168.0.6 | Online |

### Switches (5)
| Name | Model | IP | Ports | Status |
|------|-------|-----|-------|--------|
| Sunnybrae-Office-SW1-48 | US48 | 10.0.1.78 | 48 | Online |
| Sunnybrae-Studio-SW2-24-PoE | US24P250 | 10.0.1.137 | 24 | Online |
| Sunnybrae-Cinema-SW3-24-POE | US24P250 | 10.0.1.140 | 24 | Online |
| SUN-Office-Dev-Desk | US24 | 10.0.1.193 | 24 | Online |
| USW-Flex-5-port-SW-HAAS Hoose | USMINI | 10.0.1.162 | 5 | **OFFLINE** |

### Access Points (8)
| Name | Model | IP | Location | Status |
|------|-------|-----|----------|--------|
| SUN-AC-Office | U7PG2 | 10.0.1.109 | Office | Online |
| Sun-AP-GarFl | U7PG2 | 10.0.1.19 | Garden Floor | Online |
| SUN-AP-AK-Bed | U7PG2 | 10.0.1.23 | AK Bedroom | Online |
| SUN-AP-Chaple | U7PG2 | 10.0.1.29 | Chapel | Online |
| SUN-AP-Cinema | U7PG2 | 10.0.1.31 | Cinema | Online |
| SUN-AP-Studio | U7PG2 | 10.0.1.21 | Studio | Online |
| SUN-AP-Studio-Bed | U7PG2 | 10.0.1.22 | Studio Bedroom | Online |
| ACP-AP-U6-Lite-HAAS-Hoose | UAL6 | 10.0.1.24 | HAAS Hoose | **OFFLINE** |

---

## Network Segments

| Segment | Subnet | Purpose |
|---------|--------|---------|
| WAN | 192.168.0.x | ISP connection |
| LAN | 10.0.1.x | Internal network |

---

## WiFi Coverage

```
                    ┌─────────────────────────────────────────────┐
                    │              SUNNYBRAE PROPERTY             │
                    │                                             │
    ┌───────────────┼───────────────┬───────────────┬─────────────┤
    │   OFFICE      │   STUDIO      │   CINEMA      │   CHAPEL    │
    │               │               │               │             │
    │ SUN-AC-Office │ SUN-AP-Studio │ SUN-AP-Cinema │ SUN-AP-     │
    │               │ SUN-AP-Studio │               │ Chaple      │
    │               │ -Bed          │               │             │
    └───────────────┼───────────────┼───────────────┼─────────────┤
                    │   GARDEN FL   │   AK BED      │             │
                    │               │               │             │
                    │ Sun-AP-GarFl  │ SUN-AP-AK-Bed │             │
                    │               │               │             │
                    └───────────────┴───────────────┴─────────────┘

    SSIDs: ACP-Guest, ACP-WiFi, SUNNY-5G, dev-24g
```

---

## Uplink Hierarchy

```
USG Pro 4 (Gateway)
    │
    └── SW1-48 (Office - Core)
            │
            ├── SW2-24-PoE (Studio)
            │       ├── SUN-AP-Studio
            │       └── SUN-AP-Studio-Bed
            │
            ├── SW3-24-PoE (Cinema)
            │       └── SUN-AP-Cinema
            │
            ├── Dev-Desk SW (Office)
            │       └── SUN-AC-Office
            │
            ├── Sun-AP-GarFl
            ├── SUN-AP-AK-Bed
            └── SUN-AP-Chaple
```

---

*Generated from UniFi Controller via MCP*
