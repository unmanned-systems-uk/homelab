# HomeLab Hardware Inventory

**Last Updated:** 2025-12-13
**Source:** Auto-generated from equipment database

---

## 1. Compute Hardware

### Servers / Workstations
| Name | Type | CPU | RAM | Storage | OS | IP Address | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| DEV-PC-Ubuntu | workstation | Intel i7-10700 @ 2.90GHz (8c/16t) | 32GB | 1TB Samsung 980 PRO NVMe | Ubuntu 24.04.3 LTS | - | active | Main dev machine, RTX A2000 GPU |
| Legacy-i7 | workstation | Intel i7 (gen TBD) | - | - | - | - | in storage | Nvidia Quadro K500 - NEEDS POWER-UP FOR SPECS |

### Single Board Computers (SBCs)
| Name | Model | CPU/SoC | RAM | Storage | OS | IP Address | Purpose | Notes |
|---|---|---|---|---|---|---|---|---|
| DPM-Air | Raspberry Pi 5 | BCM2712 Quad Cortex-A76 | 8GB | SSD | - | 10.0.1.53 | DPM Air-Side | payload-manager Docker |
| SDR-Pi5-1 | Raspberry Pi 5 | BCM2712 Quad Cortex-A76 | 8GB | SSD | - | - | SDR Radio Testing | - |
| SDR-Pi5-2 | Raspberry Pi 5 | BCM2712 Quad Cortex-A76 | 8GB | SSD | - | - | SDR Radio Testing | - |

### AI Development Boards
| Name | Model | Compute | RAM | Storage | OS | IP Address | Purpose | Notes |
|---|---|---|---|---|---|---|---|---|
| Jetson-Dev | NVIDIA Jetson Orin NX | Ampere GPU + 6-core ARM | - | - | JetPack | 10.0.1.113 | AI/ML Dev | Dual-platform support |

### GPUs / Accelerators
| Name | Model | VRAM | Purpose | Notes |
|---|---|---|---|---|
| Quadro-K500 | NVIDIA Quadro K500 | ~1GB | Limited ML | Host: Legacy-i7. Very old, limited use |
| RTX-A2000 | NVIDIA RTX A2000 | 6GB GDDR6 | ML Dev / CUDA | Host: DEV-PC-Ubuntu. Main AI workstation GPU |

---

## 2. Networking

### Routers / Firewalls
| Name | Model | Ports | IP Address | Purpose | Notes |
|---|---|---|---|---|---|
| Gateway | USG-Pro-4 | 4x GbE | - | Primary Router | CURRENT - manages 10.0.1.x |
| Gateway-New | Dream Machine (model TBD) | - | - | Future Router | MIGRATION PENDING |

### Switches
| Name | Model | Ports | IP Address | Notes |
|---|---|---|---|---|
| (Multiple) | Ubiquiti UniFi | - | - | NEEDS ENUMERATION via UniFi Controller |

### Access Points
| Name | Model | Bands | IP Address | Coverage | Notes |
|---|---|---|---|---|---|
| (Multiple) | Ubiquiti UniFi | - | - | - | NEEDS ENUMERATION via UniFi Controller |

### Network Controllers
| Name | Model | Version | IP Address | Status | Notes |
|---|---|---|---|---|---|
| CloudKey | UniFi CloudKey Gen1 | v1.1.19 | - | active | Will be retired after migration |

---

## 3. Storage

### NAS / Storage Servers
| Name | Model | Capacity | IP Address | Status | Purpose | Notes |
|---|---|---|---|---|---|---|
| QNAP | - | ~24TB | - | offline | Secondary NAS | Noisy, needs rebuild |
| Synology | - | - | - | active | Primary NAS | Currently in use |

### External Drives
| Name | Capacity | Purpose | Notes |
|---|---|---|---|
| Backup-1 | 20TB | Backup | Professional grade |
| Backup-2 | 20TB | Backup | Professional grade |

---

## 4. Test Equipment

**SCPI Network Access:** Enabled - test equipment controllable via network

### Network/SCPI Enabled Test Equipment
| Name | Manufacturer | Model | IP | Port | Serial | Firmware | Specs | Notes |
|---|---|---|---|---|---|---|---|---|
| DMM-Keithley | Keithley | Keithley DMM6500 | 10.0.1.101 | 5025 | 04423124 | 1.0.04b | 6.5-digit bench multimeter | Touchscreen, graphing, high precision |
| Load-DC | Rigol | Rigol DL3021A | 10.0.1.105 | 5025 | DL3B204100234 | 00.01.02.00.02 | 200W Electronic DC Load | Battery/PSU testing |
| PSU-Rigol-1 | Rigol | Rigol DP932A | 10.0.1.111 | 5025 | DP9A244200403 | 01.00.01.00.16 | Triple output (30V/3A x2, 5V/3A) | Programmable DC PSU |
| PSU-Rigol-2 | Rigol | Rigol DP932A | 10.0.1.138 | 5025 | DP9A243900363 | 01.00.01.00.16 | Triple output (30V/3A x2, 5V/3A) | Programmable DC PSU |
| Scope-MSO | Rigol | Rigol MSO8204 | 10.0.1.106 | 5025 | DS8A232600343 | 00.01.02.00.02 | 8-ch 2GHz Mixed Signal Oscilloscope | High-end scope, logic analyzer |
| SigGen-AWG | Rigol | Rigol DG2052 | 10.0.1.120 | 5025 | DG2P214500096 | 00.02.02.00.00 | 50MHz Dual Channel AWG | Arbitrary waveform generator |

### Other Test Equipment
*None currently*

---

## 5. SDR Equipment

### SDR Receivers
| Name | Manufacturer | Model | Frequency Range | Notes |
|---|---|---|---|---|
| HackRF-1 | Great Scott Gadgets | HackRF One | Range: 1MHz - 6GHz | TX/RX capable, wideband |
| HackRF-2 | Great Scott Gadgets | HackRF Pro | Range: 1MHz - 6GHz | TX/RX capable |
| RTL-SDR-1 | Nooelec | Nooelec NESDR Smart | Range: 25MHz - 1.75GHz | RTL2832U + R820T2 |
| RTL-SDR-2 | Nooelec | Nooelec NESDR Smart | Range: 25MHz - 1.75GHz | RTL2832U + R820T2 |

### SDR Accessories / Filters
| Name | Manufacturer | Model | Type/Frequency | Notes |
|---|---|---|---|---|
| ADS-B Filter | Nooelec | Nooelec SAWbird+ ADS-B | Range: 1090MHz | Aircraft tracking |
| AM Filter | Nooelec | Nooelec | Range: MW/AM | AM broadcast filtering |
| Antenna Switch | - | Opera Cake | Range: DC-6GHz | HackRF companion, automated switching |
| FM Filter | Nooelec | Nooelec | Range: 88-108MHz | FM broadcast filtering |
| HF Upconverter | - | Ham It Up v2 | Range: HF → VHF | Enables HF reception on RTL-SDR |
| Wideband LNA | Nooelec | Nooelec Lana WB | Range: Wide | General purpose amplification |

---

## Inventory Summary

### Equipment Count by Category (Active)
- **Compute**: 7 items
- **Networking**: 5 items
- **Sdr**: 10 items
- **Storage**: 3 items
- **Test Equipment**: 6 items

- **SCPI-enabled devices**: 6
- **Networked devices**: 8

*Database last updated: 2025-12-13T00:34:18.162010*

---
