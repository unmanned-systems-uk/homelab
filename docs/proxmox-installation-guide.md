# Proxmox VE Installation Guide - Legacy-i7

**Target System:** Legacy-i7 (Office-Ubuntu-1)
**IP Address:** 10.0.1.130
**Created:** 2025-12-13
**Status:** Ready for Installation

---

## Table of Contents

1. [Hardware Overview](#1-hardware-overview)
2. [Pre-Installation Checklist](#2-pre-installation-checklist)
3. [BIOS Configuration](#3-bios-configuration)
4. [Storage Layout Design](#4-storage-layout-design)
5. [Proxmox Installation](#5-proxmox-installation)
6. [Post-Installation Configuration](#6-post-installation-configuration)
7. [VM/LXC Structure](#7-vmlxc-structure)
8. [Network Configuration](#8-network-configuration)
9. [Verification Steps](#9-verification-steps)

---

## 1. Hardware Overview

### System Specifications

| Component | Details |
|-----------|---------|
| **CPU** | Intel Core i7-7820X (8 cores / 16 threads, 3.6GHz base, 4.5GHz boost) |
| **Architecture** | Skylake-X, LGA 2066, AVX-512 support |
| **RAM** | 32GB DDR4 |
| **Motherboard** | ASUS PRIME X299-DELUXE |
| **Chipset** | Intel X299 |

### Storage Configuration

| Device | Model | Capacity | Current Use | Planned Use |
|--------|-------|----------|-------------|-------------|
| NVMe | Samsung 960 PRO | 1TB | Boot (Ubuntu) | **Proxmox OS + VM Storage** |
| SSD 1 | Samsung 860 EVO | 500GB | Old Windows | **WIPE - Data/ISO storage** |
| SSD 2 | Samsung 860 EVO | 500GB | Old Windows | **WIPE - Data/Backup** |

### GPU Configuration

| GPU | Model | VRAM | Purpose |
|-----|-------|------|---------|
| **Primary** | NVIDIA GeForce GTX 1080 Ti | 11GB GDDR5X | VM Passthrough (AI workloads) |
| **Secondary** | NVIDIA Quadro P620 | 2GB GDDR5 | Proxmox host console |

### Key Features

- **VT-d Support:** Yes (Intel Virtualization for Directed I/O)
- **VT-x Support:** Yes (Hardware Virtualization)
- **IOMMU:** Supported via Intel VT-d
- **PCIe Lanes:** 44 lanes (i7-7820X) + 24 lanes (X299 chipset)
- **ECC Support:** Yes (X299 supports ECC with compatible RAM)

---

## 2. Pre-Installation Checklist

### Required Items

- [ ] Proxmox VE 8.x ISO (download from https://www.proxmox.com/en/downloads)
- [ ] USB drive (8GB+) for installation media
- [ ] Keyboard/monitor connected (use Quadro P620 output)
- [ ] Network cable connected
- [ ] Static IP planned: 10.0.1.130

### Data Backup

- [ ] Backup any needed data from current Ubuntu installation
- [ ] Note any important configurations
- [ ] Document current network settings

### Download Proxmox ISO

```bash
# On any Linux machine
wget https://enterprise.proxmox.com/iso/proxmox-ve_8.3-1.iso
# Verify checksum from https://www.proxmox.com/en/downloads
```

### Create Bootable USB

```bash
# Find USB device (careful - this will erase data!)
lsblk

# Write ISO to USB (replace /dev/sdX with actual device)
sudo dd bs=4M if=proxmox-ve_8.3-1.iso of=/dev/sdX conv=fsync status=progress
```

---

## 3. BIOS Configuration

### Accessing BIOS

1. Power on/restart the system
2. Press **DEL** or **F2** repeatedly during POST
3. Enter ASUS UEFI BIOS

### Required BIOS Settings

#### Advanced → CPU Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| **Intel Virtualization Technology** | Enabled | VT-x for VM hardware virtualization |
| **Intel VT-d** | Enabled | IOMMU for GPU passthrough |
| **Hyper-Threading** | Enabled | 16 threads for VM allocation |

#### Advanced → System Agent (SA) Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| **VT-d** | Enabled | PCIe passthrough support |
| **Above 4G Decoding** | Enabled | Required for GPU passthrough |

#### Advanced → PCH Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| **IOMMU** | Enabled | If separate option exists |

#### Boot → Boot Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| **CSM (Compatibility Support Module)** | Disabled | Use pure UEFI |
| **Secure Boot** | Disabled | Proxmox compatibility |

#### Boot → Boot Option Priorities

1. Set USB drive as first boot option (for installation)
2. After install, set NVMe as first boot option

### Save and Exit

1. Press **F10** to save and exit
2. Confirm changes
3. System will restart

### Verification

After saving, you should see in boot:
- VT-x and VT-d status in BIOS info screen
- UEFI boot mode active

---

## 4. Storage Layout Design

### Partition Strategy

#### NVMe (Samsung 960 PRO 1TB) - `/dev/nvme0n1`

| Partition | Size | Type | Mount | Purpose |
|-----------|------|------|-------|---------|
| nvme0n1p1 | 1GB | EFI | /boot/efi | UEFI boot partition |
| nvme0n1p2 | 931GB | LVM | local-lvm | Proxmox OS + VM storage |

**LVM Breakdown (approx):**
- Root filesystem: 50GB
- Swap: 8GB
- VM images (local-lvm): ~870GB

#### SSD 1 (Samsung 860 EVO 500GB) - `/dev/sda`

| Partition | Size | Type | Mount | Purpose |
|-----------|------|------|-------|---------|
| sda1 | 500GB | ext4 | /mnt/data | ISO storage, backups, container data |

#### SSD 2 (Samsung 860 EVO 500GB) - `/dev/sdb`

| Partition | Size | Type | Mount | Purpose |
|-----------|------|------|-------|---------|
| sdb1 | 500GB | ext4 | /mnt/backup | VM backups, snapshots |

### Storage Pools (Post-Install)

| Pool Name | Type | Device | Purpose |
|-----------|------|--------|---------|
| local | Directory | /var/lib/vz | ISO images, templates, snippets |
| local-lvm | LVM-thin | nvme0n1p2 | VM disks (thin provisioned) |
| data | Directory | /mnt/data | Container bind mounts, shared data |
| backup | Directory | /mnt/backup | Vzdump backups |

---

## 5. Proxmox Installation

### Boot from USB

1. Insert USB with Proxmox ISO
2. Power on system
3. Press **F8** (ASUS boot menu) or enter BIOS to select USB boot
4. Select "Install Proxmox VE (Graphical)"

### Installation Steps

#### Step 1: License Agreement
- Read and accept EULA
- Click "I agree"

#### Step 2: Target Disk Selection
- Select: **Samsung 960 PRO 1TB (nvme0n1)**
- Click "Options" to configure:
  - Filesystem: **ext4** (recommended) or **ZFS** (if desired)
  - If ext4: Use default LVM layout
  - hdsize: Leave at maximum
  - swapsize: 8 (GB)
  - maxroot: 50 (GB)
  - minfree: 16 (GB for LVM operations)

#### Step 3: Location and Time Zone
- Country: United Kingdom
- Time zone: Europe/London
- Keyboard: en-gb (UK)

#### Step 4: Administration Password
- Password: [Set strong password]
- Confirm password
- Email: [Your email for notifications]

#### Step 5: Network Configuration
- Management Interface: Select primary NIC (likely enp*)
- Hostname (FQDN): `pve-legacy.local` or `legacy-i7.local`
- IP Address: **10.0.1.130/24** (static)
- Gateway: **10.0.1.1**
- DNS Server: **10.0.1.1** (or 8.8.8.8)

#### Step 6: Summary
- Review all settings
- Click "Install"
- Wait for installation (5-10 minutes)

#### Step 7: Reboot
- Remove USB when prompted
- System boots into Proxmox VE

---

## 6. Post-Installation Configuration

### Access Web Interface

```
URL: https://10.0.1.130:8006
Username: root
Password: [your password]
Realm: Linux PAM
```

### Disable Enterprise Repository (No Subscription)

```bash
# SSH to Proxmox
ssh root@10.0.1.130

# Disable enterprise repo
sed -i 's/^deb/#deb/' /etc/apt/sources.list.d/pve-enterprise.list

# Add no-subscription repo
echo "deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription" > /etc/apt/sources.list.d/pve-no-subscription.list

# Update
apt update && apt full-upgrade -y
```

### Configure Additional Storage

```bash
# Format and mount SSD 1 (data)
mkfs.ext4 /dev/sda
mkdir -p /mnt/data
echo '/dev/sda /mnt/data ext4 defaults 0 2' >> /etc/fstab
mount /mnt/data

# Format and mount SSD 2 (backup)
mkfs.ext4 /dev/sdb
mkdir -p /mnt/backup
echo '/dev/sdb /mnt/backup ext4 defaults 0 2' >> /etc/fstab
mount /mnt/backup

# Verify mounts
df -h
```

### Add Storage in Proxmox UI

1. Datacenter → Storage → Add → Directory
   - ID: `data`
   - Directory: `/mnt/data`
   - Content: ISO image, Container template, Snippets

2. Datacenter → Storage → Add → Directory
   - ID: `backup`
   - Directory: `/mnt/backup`
   - Content: VZDump backup file

### Enable IOMMU for GPU Passthrough

```bash
# Edit GRUB
nano /etc/default/grub

# Change GRUB_CMDLINE_LINUX_DEFAULT to:
GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on iommu=pt"

# Update GRUB
update-grub

# Add VFIO modules
echo "vfio" >> /etc/modules
echo "vfio_iommu_type1" >> /etc/modules
echo "vfio_pci" >> /etc/modules
echo "vfio_virqfd" >> /etc/modules

# Blacklist NVIDIA drivers on host
echo "blacklist nouveau" >> /etc/modprobe.d/blacklist.conf
echo "blacklist nvidia" >> /etc/modprobe.d/blacklist.conf
echo "blacklist nvidiafb" >> /etc/modprobe.d/blacklist.conf

# Update initramfs
update-initramfs -u -k all

# Reboot
reboot
```

### Verify IOMMU

```bash
# Check IOMMU is enabled
dmesg | grep -e DMAR -e IOMMU

# List IOMMU groups
find /sys/kernel/iommu_groups/ -type l | sort -V
```

---

## 7. VM/LXC Structure

### Planned Configuration

| ID | Type | Name | CPU | RAM | Storage | GPU | Purpose |
|----|------|------|-----|-----|---------|-----|---------|
| 100 | VM | ai-workstation | 6 cores | 24GB | 200GB | GTX 1080 Ti | AI/ML development, Docker |
| 101 | LXC | docker-host | 2 cores | 4GB | 50GB | - | Portainer, general containers |
| 102 | LXC | home-assistant | 2 cores | 2GB | 20GB | - | Home automation |
| 103 | LXC | n8n | 2 cores | 2GB | 20GB | - | Workflow automation |

### Resource Allocation

**Total Resources:**
- CPU: 8 cores / 16 threads
- RAM: 32GB

**Allocation:**
| VM/LXC | Cores | RAM | Notes |
|--------|-------|-----|-------|
| Proxmox Host | 2 | 4GB | Reserved for hypervisor |
| ai-workstation | 6 | 24GB | Primary workload |
| docker-host | 2 | 4GB | Shared cores OK |
| home-assistant | 2 | 2GB | Shared cores OK |
| n8n | 2 | 2GB | Shared cores OK |
| **Overcommit** | 14/16 | 36/32GB | RAM may need balancing |

**Note:** LXC containers share host kernel, more efficient than VMs. Consider reducing ai-workstation RAM to 20GB if memory pressure occurs.

---

## 8. Network Configuration

### Current Network

| Setting | Value |
|---------|-------|
| Gateway | 10.0.1.1 |
| Subnet | 10.0.1.0/24 |
| Proxmox Host | 10.0.1.130 |

### VM/LXC IP Planning

| VM/LXC | Hostname | IP Address |
|--------|----------|------------|
| ai-workstation | ai-workstation | 10.0.1.131 |
| docker-host | docker-host | 10.0.1.132 |
| home-assistant | homeassistant | 10.0.1.133 |
| n8n | n8n | 10.0.1.134 |

### Bridge Configuration (Default)

Proxmox creates `vmbr0` by default, bridged to physical NIC.

```bash
# View network config
cat /etc/network/interfaces

# Should show something like:
# auto vmbr0
# iface vmbr0 inet static
#     address 10.0.1.130/24
#     gateway 10.0.1.1
#     bridge-ports enp*
#     bridge-stp off
#     bridge-fd 0
```

---

## 9. Verification Steps

### Post-Installation Checks

```bash
# Check Proxmox version
pveversion -v

# Check storage
pvesm status

# Check network
ip addr show

# Check IOMMU groups (for GPU passthrough)
for d in /sys/kernel/iommu_groups/*/devices/*; do
  n=$(basename $(dirname $(dirname $d)))
  echo "IOMMU Group $n: $(lspci -nns ${d##*/})"
done | sort -V

# Find GTX 1080 Ti IOMMU group
lspci -nn | grep -i nvidia

# Check memory
free -h

# Check CPU
lscpu | grep -E "^CPU\(s\)|Thread|Core|Model name"
```

### Web UI Verification

1. Access https://10.0.1.130:8006
2. Check:
   - [ ] Node status shows all hardware
   - [ ] Storage pools visible
   - [ ] No subscription nag (if using no-subscription repo)
   - [ ] Network configuration correct

### GPU Passthrough Readiness

```bash
# GTX 1080 Ti should be in its own IOMMU group
# Note the PCI address (e.g., 01:00.0, 01:00.1)

# Verify VFIO is ready
lsmod | grep vfio

# Check GPU is not bound to nvidia/nouveau
lspci -k | grep -A 3 "NVIDIA"
# Should show: Kernel driver in use: vfio-pci
```

---

## Next Steps

After completing this guide:

1. **GPU Passthrough Setup** - See `gpu-passthrough-guide.md`
2. **Create ai-workstation VM** - With GPU passthrough
3. **Create LXC containers** - docker-host, home-assistant, n8n
4. **Configure Portainer** - In docker-host container
5. **Test AI workloads** - Verify GPU acceleration in VM

---

## Troubleshooting

### Cannot access web UI

```bash
# Check if pveproxy is running
systemctl status pveproxy

# Check firewall
iptables -L

# Try restarting
systemctl restart pveproxy
```

### IOMMU not working

```bash
# Verify BIOS settings (VT-d enabled)
# Check GRUB config
cat /proc/cmdline
# Should contain: intel_iommu=on
```

### GPU still bound to nvidia driver

```bash
# Ensure blacklist is active
cat /etc/modprobe.d/blacklist.conf

# Regenerate initramfs
update-initramfs -u -k all
reboot
```

---

## References

- [Proxmox VE Documentation](https://pve.proxmox.com/wiki/Main_Page)
- [Proxmox GPU Passthrough](https://pve.proxmox.com/wiki/PCI_Passthrough)
- [ASUS X299 Manual](https://www.asus.com/motherboards-components/motherboards/prime/prime-x299-deluxe/)
- [Intel i7-7820X Specs](https://ark.intel.com/content/www/us/en/ark/products/123767/intel-core-i77820x-xseries-processor-11m-cache-up-to-4-30-ghz.html)

---

*HomeLab Specialist - Proxmox Installation Guide v1.0*
