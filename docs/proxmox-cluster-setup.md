# Proxmox Cluster Setup Guide

## Overview

This guide covers setting up a Proxmox VE cluster with:
- **pve-ai** (10.0.1.200) - Primary node
- **R710** (10.0.1.145) - Secondary node
- **HomeGate i3** (10.0.1.50) - QDevice for quorum

## Prerequisites

### Version Requirements
All cluster nodes must run the **same major PVE version**.

| Node | Current Version | Target Version |
|------|-----------------|----------------|
| pve-ai | 9.1.0 | 9.x |
| R710 | 8.4.17 | **Needs upgrade to 9.x** |

**IMPORTANT:** Do not attempt to cluster nodes with different major versions (8.x + 9.x will fail).

---

## Part 1: Upgrade R710 to PVE 9.x

### 1.1 Pre-Upgrade Checklist

```bash
# Backup all VMs on R710
ssh root@10.0.1.145 "vzdump --all --dumpdir /mnt/pve/nas-backup/dump --mode snapshot"

# Verify current version
ssh root@10.0.1.145 "pveversion -v"

# Check disk space (need ~5GB free on root)
ssh root@10.0.1.145 "df -h /"

# List running VMs (shut down or migrate before upgrade)
ssh root@10.0.1.145 "qm list"
```

### 1.2 Upgrade Debian Bookworm to Trixie

PVE 9.x requires Debian Trixie (testing). This is a major OS upgrade.

**Step 1: Update current system fully**
```bash
ssh root@10.0.1.145
apt update && apt dist-upgrade -y
reboot
```

**Step 2: Update sources.list for Trixie**
```bash
# Backup current sources
cp /etc/apt/sources.list /etc/apt/sources.list.bak

# Update to Trixie
cat > /etc/apt/sources.list << 'EOF'
deb http://ftp.uk.debian.org/debian trixie main contrib non-free non-free-firmware
deb http://ftp.uk.debian.org/debian trixie-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security trixie-security main contrib non-free-firmware
EOF
```

**Step 3: Update Proxmox repos for PVE 9.x**
```bash
# Update PVE repo
echo "deb http://download.proxmox.com/debian/pve trixie pve-no-subscription" > /etc/apt/sources.list.d/pve-no-subscription.list

# Remove old Ceph repo if present (will be replaced)
rm -f /etc/apt/sources.list.d/ceph.list
```

**Step 4: Perform the upgrade**
```bash
apt update
apt dist-upgrade -y

# This will take 15-30 minutes and download ~1GB
# Answer prompts carefully - generally keep existing configs
```

**Step 5: Reboot and verify**
```bash
reboot

# After reboot, verify version
pveversion -v
# Should show: proxmox-ve: 9.x.x
```

### 1.3 Post-Upgrade Verification

```bash
# Check all services
systemctl status pve-cluster pvedaemon pveproxy

# Verify VMs start correctly
qm list
qm start <vmid>

# Check storage
pvesm status
```

---

## Part 2: Set Up QDevice on HomeGate i3

The QDevice provides quorum for a 2-node cluster, preventing split-brain.

### 2.1 Install Corosync QDevice on i3 (10.0.1.50)

```bash
ssh homelab@10.0.1.50

# Install QDevice daemon
sudo apt update
sudo apt install -y corosync-qnetd

# Enable and start service
sudo systemctl enable corosync-qnetd
sudo systemctl start corosync-qnetd

# Verify it's running
sudo systemctl status corosync-qnetd

# Check it's listening (default port 5403)
sudo ss -tlnp | grep 5403
```

### 2.2 Configure Firewall (if applicable)

```bash
# Allow QDevice traffic from Proxmox nodes
sudo ufw allow from 10.0.1.200 to any port 5403
sudo ufw allow from 10.0.1.145 to any port 5403
```

---

## Part 3: Create Proxmox Cluster

### 3.1 Create Cluster on Primary Node (pve-ai)

```bash
ssh root@10.0.1.200

# Create the cluster
pvecm create homelab-cluster

# Verify cluster status
pvecm status
```

### 3.2 Join R710 to Cluster

```bash
ssh root@10.0.1.145

# Join the cluster (will prompt for pve-ai root password)
pvecm add 10.0.1.200

# Verify membership
pvecm status
pvecm nodes
```

### 3.3 Add QDevice to Cluster

Run this on **any cluster node** (e.g., pve-ai):

```bash
ssh root@10.0.1.200

# Add QDevice (10.0.1.50 is the i3)
pvecm qdevice setup 10.0.1.50

# This will:
# - Connect to the QDevice host
# - Exchange certificates
# - Configure corosync to use the QDevice
```

### 3.4 Verify Cluster + QDevice

```bash
# Check cluster status
pvecm status

# Should show:
# - 2 nodes
# - Quorum: 3 (2 nodes + 1 QDevice vote)

# Check QDevice specifically
pvecm qdevice status
```

---

## Part 4: Post-Cluster Configuration

### 4.1 Configure Shared Storage

Both nodes should see the same storage for live migration:

```bash
# Verify NAS storage is visible on both nodes
pvesm status

# Expected shared storage:
# - nas-backup (NFS - backups)
# - nas-iso (NFS - ISOs)
```

### 4.2 Test Live Migration

```bash
# Migrate a VM from R710 to pve-ai
qm migrate <vmid> pve-ai --online

# Migrate back
qm migrate <vmid> pve-r710 --online
```

### 4.3 Configure HA (Optional)

High Availability automatically restarts VMs on another node if one fails:

```bash
# Add VM to HA group (via GUI or CLI)
ha-manager add vm:<vmid>

# Set HA policy
ha-manager set vm:<vmid> --state started --group ha-group
```

---

## Troubleshooting

### Cluster Join Fails
```bash
# Check network connectivity
ping -c 3 10.0.1.200

# Check corosync ports (5404-5405 UDP)
nc -vzu 10.0.1.200 5405

# Check time sync (must be within 1 second)
date
```

### QDevice Not Connecting
```bash
# On QDevice host (i3):
sudo systemctl status corosync-qnetd
sudo journalctl -u corosync-qnetd -f

# On cluster node:
corosync-qdevice-tool -s
```

### Split-Brain Recovery
```bash
# If cluster loses quorum:
pvecm expected 1  # Dangerous - only use if you know what you're doing
```

---

## Network Requirements

| Port | Protocol | Purpose |
|------|----------|---------|
| 5404-5405 | UDP | Corosync cluster |
| 5403 | TCP | QDevice |
| 22 | TCP | SSH (cluster setup) |
| 8006 | TCP | Proxmox Web UI |
| 3128 | TCP | SPICE proxy |
| 111, 2049 | TCP/UDP | NFS (shared storage) |

---

## Summary

| Step | Action | Status |
|------|--------|--------|
| 1 | Upgrade R710 to PVE 9.x | Pending |
| 2 | Install QDevice on i3 | Pending |
| 3 | Create cluster on pve-ai | Pending |
| 4 | Join R710 to cluster | Pending |
| 5 | Add QDevice | Pending |
| 6 | Test live migration | Pending |

**Estimated time:** 1-2 hours (mostly waiting for R710 upgrade)

---

*Last updated: 2026-02-28*
