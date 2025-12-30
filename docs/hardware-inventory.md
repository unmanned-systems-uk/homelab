# HomeLab Hardware Inventory

**Last Updated:** 2025-12-30
**Status:** In Progress

---

## 1. Compute Hardware

### Servers / Workstations
| Name | Type | CPU | RAM | Storage | OS | IP Address | Status | Notes |
|------|------|-----|-----|---------|-----|------------|--------|-------|
| DEV-PC-Ubuntu | Workstation | Intel i7-10700 @ 2.90GHz (8c/16t) | 32GB | 1TB Samsung 980 PRO NVMe | Ubuntu 24.04.3 LTS | - | Active | Main dev machine, RTX A2000 GPU |
| Legacy-i7 | Workstation | Intel i7-7820X @ 3.6GHz (8c/16t, 4.5GHz boost, AVX-512) | 32GB | 1TB Samsung 960 PRO NVMe + 2x 500GB Samsung 860 EVO SSD | Ubuntu (temp) | 10.0.1.130 | Active | **PROXMOX TARGET** - GTX 1080 Ti + Quadro P620 |
| PowerEdge-R640 | 1U Rack Server | Xeon (config TBD) | TBD | 10x SFF bays | TBD | TBD | Not Accessible | Dell R640 - NEEDS PHYSICAL ACCESS FOR SPECS |

### Single Board Computers (SBCs)
| Name | Model | CPU/SoC | RAM | Storage | OS | IP Address | Purpose | Notes |
|------|-------|---------|-----|---------|-----|------------|---------|-------|
| DPM-Air | Raspberry Pi 5 | BCM2712 Quad Cortex-A76 | 8GB | SSD | - | 10.0.1.53 | DPM Air-Side | payload-manager Docker |
| SDR-Pi5-1 | Raspberry Pi 5 | BCM2712 Quad Cortex-A76 | 8GB | SSD | - | TBD | SDR Radio Testing | |
| SDR-Pi5-2 | Raspberry Pi 5 | BCM2712 Quad Cortex-A76 | 8GB | SSD | - | TBD | SDR Radio Testing | |
| HA-Pi5 | Raspberry Pi 5 | BCM2712 Quad Cortex-A76 | 16GB | TBD | HAOS | 10.0.1.150 | Home Assistant | NEW 2025-12-30, top-spec model |

### AI Development Boards (moved from AI/ML section for clarity)
| Name | Model | Compute | RAM | Storage | OS | IP Address | Purpose | Notes |
|------|-------|---------|-----|---------|-----|------------|---------|-------|
| Jetson-Dev | NVIDIA Jetson Orin NX | Ampere GPU + 6-core ARM | TBD | TBD | JetPack | 10.0.1.113 | AI/ML Dev | Dual-platform support |

### Mini PCs / NUCs
| Name | Model | CPU | RAM | Storage | OS | IP Address | Purpose | Notes |
|------|-------|-----|-----|---------|-----|------------|---------|-------|
| Jumper-1 | Jumper Mini PC | TBD | TBD | TBD | Windows 10 | TBD | TBD | Ethernet issue - HAOS won't see NIC |
| Jumper-2 | Jumper Mini PC | TBD | TBD | TBD | TBD | TBD | TBD | Spare - untested |
| Jumper-3 | Jumper Mini PC | TBD | TBD | TBD | TBD | TBD | TBD | Spare - untested |

---

## 2. AI/ML Hardware

### GPUs / Accelerators
| Name | Model | VRAM | Host System | Driver | Purpose | Notes |
|------|-------|------|-------------|--------|---------|-------|
| RTX-A2000 | NVIDIA RTX A2000 | 6GB GDDR6 | DEV-PC-Ubuntu | TBD | ML Dev / CUDA | Main AI workstation GPU |
| GTX-1080Ti | NVIDIA GeForce GTX 1080 Ti | 11GB GDDR5X | Legacy-i7 | - | AI VM Passthrough | **PRIMARY AI GPU** - for Proxmox VM passthrough |
| Quadro-P620 | NVIDIA Quadro P620 | 2GB GDDR5 | Legacy-i7 | - | Proxmox Console | Low-profile, host display output |
| Quadro-K5000 | NVIDIA Quadro K5000 | 4GB | - | - | - | **DEAD - 2025-12-13** - Removed from Legacy-i7 |

### AI Development Boards
| Name | Model | Compute | RAM | Storage | Purpose | Notes |
|------|-------|---------|-----|---------|---------|-------|
| (See Jetson-Dev in Compute section) | | | | | | |

---

## 3. Networking

**Ecosystem:** Ubiquiti UniFi
**Controller:** CloudKey v1.1.19 (current) → Dream Machine built-in (future)
**MCP Integration:** Planned - enable Claude network access via UniFi API

### Routers / Firewalls
| Name | Model | Ports | IP Address | Purpose | Notes |
|------|-------|-------|------------|---------|-------|
| Gateway | USG-Pro-4 | 4x GbE | TBD | Primary Router | CURRENT - manages 10.0.1.x |
| Gateway-New | Dream Machine (model TBD) | TBD | - | Future Router | MIGRATION PENDING |

### Switches
| Name | Model | Ports | Managed | IP Address | Notes |
|------|-------|-------|---------|------------|-------|
| (Multiple) | Ubiquiti UniFi | TBD | Yes | TBD | NEEDS ENUMERATION via UniFi Controller |

### Access Points
| Name | Model | Bands | IP Address | Coverage | Notes |
|------|-------|-------|------------|----------|-------|
| (Multiple) | Ubiquiti UniFi | TBD | TBD | TBD | NEEDS ENUMERATION via UniFi Controller |

### Network Controllers
| Name | Model | Version | IP Address | Status | Notes |
|------|-------|---------|------------|--------|-------|
| CloudKey | UniFi CloudKey Gen1 | v1.1.19 | TBD | Current | Will be retired after migration |
| (Dream Machine) | TBD | - | - | Future | Built-in controller, self-hosted |

### Network Notes
- VLANs: Likely configured (TBD - will enumerate via MCP)
- Migration Path: USG-Pro-4 + CloudKey → Dream Machine (all-in-one)
- MCP Goal: UniFi API access for network visibility/management
- Post-Migration: CloudKey retired, controller moves to Dream Machine

---

## 4. Storage

### NAS / Storage Servers
| Name | Model | Capacity | RAID | IP Address | Status | Purpose | Notes |
|------|-------|----------|------|------------|--------|---------|-------|
| ccpm-nas | Synology | ~45TB | TBD | 10.0.1.251 | Active | Primary NAS | Proxmox backup target, SMB share: //ccpm-nas.local/proxmox/ |
| QNAP | TBD | ~24TB | TBD | - | Offline | Secondary NAS | Noisy, needs rebuild |

### Server Storage (R640)
| Location | Drives | Capacity | Status | Notes |
|----------|--------|----------|--------|-------|
| PowerEdge R640 | 8x SFF | TBD | Not Accessible | Check specs when powered up |

### External Drives
| Name | Capacity | Interface | Purpose | Notes |
|------|----------|-----------|---------|-------|
| Backup-1 | 20TB | USB 3.x | Backup | Professional grade |
| Backup-2 | 20TB | USB 3.x | Backup | Professional grade |

### Storage Summary
- **Online:** Synology NAS (primary)
- **Offline:** QNAP (~24TB, needs rebuild)
- **Backup:** 2x 20TB external drives (40TB total backup capacity)
- **Pending:** R640 storage (8 drives, specs TBD)

---

## 5. Electronics Development

**SCPI Network Access:** Enabled - test equipment controllable via network

### Test Equipment (Network/SCPI Enabled)
| Name | Model | IP Address | Serial | Firmware | Specs | Notes |
|------|-------|------------|--------|----------|-------|-------|
| DMM-Keithley | Keithley DMM6500 | 10.0.1.101 | 04423124 | 1.0.04b | 6.5-digit bench multimeter | Touchscreen, graphing, high precision |
| Scope-MSO | Rigol MSO8204 | 10.0.1.106 | DS8A232600343 | 00.01.02.00.02 | 8-ch 2GHz Mixed Signal Oscilloscope | High-end scope, logic analyzer |
| SigGen-AWG | Rigol DG2052 | 10.0.1.120 | DG2P214500096 | 00.02.02.00.00 | 50MHz Dual Channel AWG | Arbitrary waveform generator |
| Load-DC | Rigol DL3021A | 10.0.1.105 | DL3B204100234 | 00.01.02.00.02 | 200W Electronic DC Load | Battery/PSU testing |
| PSU-Rigol-1 | Rigol DP932A | 10.0.1.111 | DP9A244200403 | 01.00.01.00.16 | Triple output (30V/3A x2, 5V/3A) | Programmable DC PSU |
| PSU-Rigol-2 | Rigol DP932A | 10.0.1.138 | DP9A243900363 | 01.00.01.00.16 | Triple output (30V/3A x2, 5V/3A) | Programmable DC PSU |

### Test Equipment (Non-Networked/Other)
| Name | Model | Specs | Status | Notes |
|------|-------|-------|--------|-------|
| | | | | TBD - add any non-networked equipment |

### Microcontrollers & Dev Boards

#### STM32 Ecosystem
| Name | Model | MCU | Features | Qty | Notes |
|------|-------|-----|----------|-----|-------|
| Discovery | STM32F769I-DISCO | STM32F769 | TFT display, touch | 1 | High-end Cortex-M7 |
| Nucleo Boards | Various | Various STM32 | Multiple form factors | Many | Full inventory TBD |

#### ESP32 Ecosystem
| Name | Model | Variant | Features | Qty | Notes |
|------|-------|---------|----------|-----|-------|
| ESP32 | WROOM modules | ESP32 | WiFi/BT | Several | Standard modules |
| ESP32-S2 | DevKits | ESP32-S2 | USB OTG | Several | |
| ESP32-S3 | DevKits | ESP32-S3 | AI acceleration | Several | |
| ESP32-CAM | Camera boards | ESP32 | OV2640 camera | A few | Vision projects |

#### MikroE Ecosystem (mikroelektronika.com)
| Name | Model | MCU Support | Features | Notes |
|------|-------|-------------|----------|-------|
| EasyPIC PRO | v7a | PIC MCUs | Multiple MCU boards | Full PIC dev system |
| Fusion for PIC | v8 | PIC MCUs | Multiple MCU boards | |
| Fusion for PIC32 | - | PIC32 | Multiple MCU boards | 32-bit PIC |
| Fusion for ARM | v8 | ARM Cortex | Multiple MCU boards | ARM development |
| UNI-DS | v8 | Universal | Multi-architecture | Universal dev system |
| HMI Displays | Various | - | Touch displays | Several units |
| **Click Boards** | Various | Add-on modules | Sensors, interfaces, comms | **LOTS** - inventory TBD |

*MikroE Reference: https://www.mikroe.com/development-boards*
*Click Boards: https://www.mikroe.com/click*

#### Arduino (Rarely Used)
| Name | Model | MCU | Qty | Notes |
|------|-------|-----|-----|-------|
| Various | TBD | ATmega | Several | Legacy, rarely used |

#### Other MCUs
| Name | Model | Architecture | Qty | Notes |
|------|-------|--------------|-----|-------|
| | | | | TBD |

### SDR Equipment

#### SDR Receivers
| Name | Model | Frequency Range | Interface | Notes |
|------|-------|-----------------|-----------|-------|
| HackRF-1 | HackRF One | 1MHz - 6GHz | USB | TX/RX capable, wideband |
| HackRF-2 | HackRF Pro | 1MHz - 6GHz | USB | TX/RX capable |
| RTL-SDR-1 | Nooelec NESDR Smart | 25MHz - 1.75GHz | USB | RTL2832U + R820T2 |
| RTL-SDR-2 | Nooelec NESDR Smart | 25MHz - 1.75GHz | USB | RTL2832U + R820T2 |

#### SDR Accessories / Filters
| Name | Model | Type | Frequency | Notes |
|------|-------|------|-----------|-------|
| Antenna Switch | Opera Cake | 8-port antenna switcher | DC-6GHz | HackRF companion, automated switching |
| ADS-B Filter | Nooelec SAWbird+ ADS-B | LNA + Filter | 1090MHz | Aircraft tracking |
| Wideband LNA | Nooelec Lana WB | Wideband LNA | Wide | General purpose amplification |
| FM Filter | Nooelec | Band filter | 88-108MHz | FM broadcast filtering |
| AM Filter | Nooelec | Band filter | MW/AM | AM broadcast filtering |
| HF Upconverter | Ham It Up v2 | Upconverter | HF → VHF | Enables HF reception on RTL-SDR |

#### SDR Capabilities Summary
- **HF Reception:** Via Ham It Up v2 upconverter
- **VHF/UHF:** Native on all receivers
- **ADS-B (1090MHz):** Dedicated filter + LNA
- **Wideband TX/RX:** HackRF devices (1MHz-6GHz)
- **Host Systems:** Pi5 units for dedicated SDR processing

### Programmers / Debuggers
| Name | Model | Supported Targets | Interface | Notes |
|------|-------|-------------------|-----------|-------|
| | | | | TBD |

### Sensors / Modules
| Category | Name | Model | Interface | Qty | Notes |
|----------|------|-------|-----------|-----|-------|
| | | | | | TBD |

### Components Stock
| Category | Description | Qty/Range | Storage Location | Notes |
|----------|-------------|-----------|------------------|-------|
| | | | | TBD |

---

## 6. Peripherals & Misc

### Monitors / Displays
| Name | Model | Size | Resolution | Inputs | Notes |
|------|-------|------|------------|--------|-------|
| | | | | | |

### Input Devices
| Type | Model | Connection | Notes |
|------|-------|------------|-------|
| | | | |

### Other
| Item | Model | Purpose | Notes |
|------|-------|---------|-------|
| | | | |

---

## Network Topology

```
[To be documented - network diagram]
```

---

## Location Map

| Location | Equipment |
|----------|-----------|
| | |

---

## Notes

-
