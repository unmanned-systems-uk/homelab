# End of Day Report - 2026-04-17

## Session Overview
- **Duration:** ~8 hours (continued session)
- **Status:** Completed
- **Database Report ID:** `4a5f3391-e7bf-4725-b160-2e947d9466e5`

---

## Work Completed

### 1. SDR Jumper (10.0.1.73) Infrastructure Setup

**NAS Access Configuration:**
- Installed `cifs-utils` (NFS failed due to network issues)
- Mounted CC-Share: `//10.0.1.251/CC-Share` → `/mnt/cc-share`
- Mounted git-share: `//10.0.1.251/git-share` → `/mnt/git-share`
- Added fstab entries for persistence
- Created symlinks: `~/cc-share`, `~/git-share`

**Credentials Files:**
- `/home/sdr/.smbcredentials` (sdr-ops / 9zm8Scv8)
- `/home/sdr/.git-smbcredentials` (homelab-agent / Rw4LIc*r)

### 2. Hydra-Link Private Git Repository

Created private Git repo on NAS for sensitive SDR project:
- **Bare repo:** `/volume1/git-share/Hydra-Link.git`
- **Local project:** `/home/sdr/agents/sdr-ops/Hydra-Link/`
- **Git config:** user.name='SDR-Ops', email='sdr-ops@homelab.local'
- Initial commit pushed successfully

### 3. SSH Key Configuration for NAS Git Access

Added SSH keys to NAS `homelab-agent` authorized_keys:
- W11 PC: `anthony@sunnybrae.co.uk`
- Laptop: `anthony@sunnybrae.co.uk` (second key)
- SDR Jumper: `sdr@sdr-jumper`
- EZBox: `homelab-agent@ezbox`

**Windows SSH Config:**
```
Host ccpm-nas
    HostName 10.0.1.251
    User homelab-agent
    IdentityFile ~/.ssh/id_ed25519
```

### 4. USB Architecture Analysis (Local System)

Analyzed USB topology on Jumper (Intel i3-5005U):
- **Front ports:** Direct to xHCI root hub (NO internal hub)
- **Rear ports:** Also direct connections
- **SDRs:** 2x Nooelec NESDR SMArt v5 (RTL2838) detected
- **Advantage over Pi5:** No hub bottleneck

### 5. R710 RAM Audit

- **Total RAM:** 128GB (16 × 8GB DDR3 ECC @ 1333 MT/s)
- **Empty slots:** 2 (A9, B9)
- **VM allocation:** ~80GB to running VMs
- **Available:** ~70GB for new VMs

### 6. Synology Project Setup Guide

Created reference guide: `docs/synology-project-setup-guide.md`
- Shared folder creation
- User management
- NFS permissions configuration
- Testing procedures

### 7. SDR Agent Fix

Fixed hostname resolution issue:
- Added to `/etc/hosts`: `10.0.1.251 nas ccpm-nas ccpm-nas.local`
- Created SSH config for nas host
- Generated SSH key for sdr user and added to NAS

### 8. CCPM MCP URL Discovery

Found Cloudflare tunnel endpoints on Harbor (10.0.1.202):
| Service | URL |
|---------|-----|
| CCPM MCP | `https://ccpm-mcp.unmanned-systems.uk` |
| HomeLab MCP | `https://homelab-mcp.unmanned-systems.uk` |
| UniFi MCP | `https://mcp.unmanned-systems.uk` |

---

## Infrastructure Status

### Network Devices
| Device | IP | Status |
|--------|-----|--------|
| UDM Pro | 10.0.1.1 | ONLINE |
| NAS | 10.0.1.251 | ONLINE |
| Proxmox (pve-ai) | 10.0.1.200 | OFFLINE |

### SCPI Equipment (2/6 Online)
| Device | IP | Status |
|--------|-----|--------|
| Scope (MSO8204) | 10.0.1.106 | ONLINE |
| AWG (DG2052) | 10.0.1.120 | ONLINE |
| DMM (DMM6500) | 10.0.1.101 | OFFLINE |
| DC Load (DL3021A) | 10.0.1.105 | OFFLINE |
| PSU-1 (DP932A) | 10.0.1.111 | OFFLINE |
| PSU-2 (DP932A) | 10.0.1.138 | OFFLINE |

---

## Blockers / Issues

1. **NFS package install failed** on SDR Jumper - Ubuntu mirror connectivity issues (IPv6 unreachable, timeouts). Workaround: Used SMB/CIFS instead.

2. **Proxmox node pve-ai (10.0.1.200)** showing offline - needs investigation.

3. **RF VM SSH via Cloudflare** - Route added to Cloudflare dashboard but not fully tested. Domain mismatch (ccpmframework.com vs unmanned-systems.uk tunnels).

---

## Handoff Notes for Next Session

1. **Investigate pve-ai (10.0.1.200)** - Proxmox node offline, may need physical check or IPMI access.

2. **Complete RF VM SSH tunnel** - Test SSH connection via Cloudflare once tunnel is properly configured.

3. **SDR Jumper ready** - Fully configured with NAS access, Git repo. Ready for SDR-Ops agent work.

4. **Hydra-Link project** - Initialized and ready for development.

5. **Windows/laptop** - SSH access to NAS Git repos configured and documented.

---

## Key Credentials Reference

| System | User | Notes |
|--------|------|-------|
| SDR Jumper | sdr | 053210 |
| NAS (SMB) | sdr-ops | 9zm8Scv8 |
| NAS (SSH) | homelab-agent | SSH key auth |

---

*HomeLab Agent - End of Day Report*
*Database: ccpm_db @ 10.0.1.251:5433*
*Generated: 2026-04-17*
