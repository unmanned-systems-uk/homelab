# GPU Passthrough Guide - GTX 1080 Ti on Proxmox

**Target GPU:** NVIDIA GeForce GTX 1080 Ti (11GB)
**Host System:** Legacy-i7 (Proxmox VE)
**Target VM:** ai-workstation (VM 100)
**Created:** 2025-12-13

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [IOMMU Group Verification](#3-iommu-group-verification)
4. [VFIO Configuration](#4-vfio-configuration)
5. [VM Creation](#5-vm-creation)
6. [GPU Passthrough Configuration](#6-gpu-passthrough-configuration)
7. [Guest VM Setup](#7-guest-vm-setup)
8. [Verification](#8-verification)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Overview

### What is GPU Passthrough?

GPU passthrough (PCI passthrough) allows a VM to have direct, near-native access to a physical GPU. The GPU is exclusively assigned to the VM, bypassing the hypervisor for GPU operations.

### Hardware Configuration

| GPU | Model | VRAM | Role |
|-----|-------|------|------|
| GTX 1080 Ti | GeForce GTX 1080 Ti | 11GB GDDR5X | **Passed to VM** - AI/ML workloads |
| Quadro P620 | Quadro P620 | 2GB GDDR5 | **Host GPU** - Proxmox console |

### Why Two GPUs?

- **Quadro P620:** Provides display output for Proxmox host (BIOS, console, emergency access)
- **GTX 1080 Ti:** Dedicated to VM for maximum performance (no sharing with host)

### GTX 1080 Ti Specifications

| Spec | Value |
|------|-------|
| CUDA Cores | 3584 |
| Base Clock | 1480 MHz |
| Boost Clock | 1582 MHz |
| Memory | 11GB GDDR5X |
| Memory Bandwidth | 484 GB/s |
| TDP | 250W |
| Compute Capability | 6.1 |
| NVENC | Yes (2x) |
| NVDEC | Yes |

---

## 2. Prerequisites

### BIOS Requirements (Already configured in main guide)

- [x] Intel VT-d: **Enabled**
- [x] Intel VT-x: **Enabled**
- [x] Above 4G Decoding: **Enabled**
- [x] CSM: **Disabled**

### Proxmox Host Requirements

- [x] IOMMU enabled in GRUB (`intel_iommu=on iommu=pt`)
- [x] VFIO modules loaded
- [x] NVIDIA drivers blacklisted on host

### Verify Prerequisites

```bash
# SSH to Proxmox host
ssh root@10.0.1.130

# Check IOMMU is enabled
dmesg | grep -e DMAR -e IOMMU | head -5
# Should show: "DMAR: IOMMU enabled"

# Check kernel command line
cat /proc/cmdline
# Should contain: intel_iommu=on

# Check VFIO modules
lsmod | grep vfio
# Should show: vfio_pci, vfio_iommu_type1, vfio
```

---

## 3. IOMMU Group Verification

### Why IOMMU Groups Matter

All devices in the same IOMMU group must be passed through together. The GTX 1080 Ti needs to be in its own group (or with only its audio device).

### List All IOMMU Groups

```bash
#!/bin/bash
# Save as /root/iommu-groups.sh
for d in /sys/kernel/iommu_groups/*/devices/*; do
  n=${d#*/iommu_groups/*}
  n=${n%%/*}
  printf "IOMMU Group %s:\t" "$n"
  lspci -nns "${d##*/}"
done | sort -t: -k1 -n
```

```bash
chmod +x /root/iommu-groups.sh
./root/iommu-groups.sh
```

### Find GTX 1080 Ti

```bash
# Find NVIDIA devices
lspci -nn | grep -i nvidia

# Example output:
# 01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP102 [GeForce GTX 1080 Ti] [10de:1b06]
# 01:00.1 Audio device [0403]: NVIDIA Corporation GP102 HDMI Audio Controller [10de:10ef]
# 05:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP107GL [Quadro P620] [10de:1cb6]
```

### Verify Group Isolation

The GTX 1080 Ti (01:00.0) and its audio device (01:00.1) should be in the same IOMMU group, with no other devices.

```bash
# Check specific IOMMU group (replace X with group number)
ls -la /sys/kernel/iommu_groups/X/devices/
```

**Good example:**
```
IOMMU Group 1:
    01:00.0 NVIDIA GeForce GTX 1080 Ti
    01:00.1 NVIDIA GP102 HDMI Audio
```

**Problem example (would need ACS override):**
```
IOMMU Group 1:
    01:00.0 NVIDIA GeForce GTX 1080 Ti
    01:00.1 NVIDIA GP102 HDMI Audio
    02:00.0 Some other device    <-- Cannot pass through GPU alone
```

### If IOMMU Groups are Not Isolated

The X299 chipset typically has good IOMMU group isolation. If devices are grouped together:

1. Try different PCIe slots (GPU in primary x16 slot usually best)
2. Consider ACS override patch (not recommended for security)

---

## 4. VFIO Configuration

### Identify GPU PCI IDs

```bash
# Get vendor:device IDs for GTX 1080 Ti
lspci -nn | grep -i "1080"

# Example:
# 01:00.0 VGA: NVIDIA [10de:1b06]   <-- GPU
# 01:00.1 Audio: NVIDIA [10de:10ef]  <-- HDMI Audio
```

**Note the IDs:**
- GPU: `10de:1b06`
- Audio: `10de:10ef`

### Bind GPU to VFIO at Boot

```bash
# Create VFIO configuration
echo "options vfio-pci ids=10de:1b06,10de:10ef" > /etc/modprobe.d/vfio.conf

# Ensure VFIO loads before nvidia drivers
echo "softdep nvidia pre: vfio-pci" >> /etc/modprobe.d/vfio.conf
echo "softdep nvidiafb pre: vfio-pci" >> /etc/modprobe.d/vfio.conf
echo "softdep nouveau pre: vfio-pci" >> /etc/modprobe.d/vfio.conf

# Update initramfs
update-initramfs -u -k all

# Reboot
reboot
```

### Verify VFIO Binding

```bash
# After reboot, check GPU is bound to vfio-pci
lspci -k | grep -A 3 "1080"

# Should show:
# 01:00.0 VGA compatible controller: NVIDIA Corporation GP102 [GeForce GTX 1080 Ti]
#     Kernel driver in use: vfio-pci
#     Kernel modules: nouveau
# 01:00.1 Audio device: NVIDIA Corporation GP102 HDMI Audio Controller
#     Kernel driver in use: vfio-pci
#     Kernel modules: snd_hda_intel
```

---

## 5. VM Creation

### Create ai-workstation VM (VM 100)

#### Via Web UI

1. **Datacenter → pve-legacy → Create VM**

2. **General Tab:**
   - VM ID: `100`
   - Name: `ai-workstation`
   - Start at boot: Yes (after testing)

3. **OS Tab:**
   - ISO image: Ubuntu 22.04 LTS or your preferred Linux
   - Type: Linux
   - Version: 6.x - 2.6 Kernel

4. **System Tab:**
   - Machine: `q35` (required for PCIe passthrough)
   - BIOS: `OVMF (UEFI)` (recommended for GPU passthrough)
   - Add EFI Disk: Yes
   - SCSI Controller: VirtIO SCSI

5. **Disks Tab:**
   - Bus/Device: VirtIO Block (virtio0)
   - Storage: local-lvm
   - Disk size: 200GB
   - Cache: Write back
   - Discard: Yes (for SSD TRIM)

6. **CPU Tab:**
   - Sockets: 1
   - Cores: 6
   - Type: `host` (required for optimal GPU performance)
   - Enable NUMA: If needed

7. **Memory Tab:**
   - Memory: 24576 MB (24GB)
   - Ballooning: Disable (recommended for GPU workloads)

8. **Network Tab:**
   - Bridge: vmbr0
   - Model: VirtIO (paravirtualized)

9. **Confirm and Create**

#### Via Command Line

```bash
# Create VM
qm create 100 \
  --name ai-workstation \
  --memory 24576 \
  --balloon 0 \
  --cores 6 \
  --sockets 1 \
  --cpu host \
  --machine q35 \
  --bios ovmf \
  --efidisk0 local-lvm:1,format=raw,efitype=4m,pre-enrolled-keys=1 \
  --scsihw virtio-scsi-pci \
  --virtio0 local-lvm:200,discard=on \
  --net0 virtio,bridge=vmbr0 \
  --ostype l26

# Attach ISO for installation
qm set 100 --ide2 local:iso/ubuntu-22.04.3-desktop-amd64.iso,media=cdrom
qm set 100 --boot order=ide2
```

---

## 6. GPU Passthrough Configuration

### Add GPU to VM

```bash
# Get PCI address of GTX 1080 Ti
lspci | grep -i "1080"
# Example: 01:00.0

# Add GPU to VM (replace 01:00 with actual address)
qm set 100 -hostpci0 01:00,pcie=1,x-vga=1

# The above adds:
# - hostpci0: First PCIe passthrough device
# - 01:00: PCI address (includes 01:00.0 GPU and 01:00.1 Audio)
# - pcie=1: Use PCIe instead of conventional PCI
# - x-vga=1: Mark as primary VGA (for boot display)
```

### Configure VM for GPU

```bash
# Edit VM configuration
nano /etc/pve/qemu-server/100.conf

# Add/modify these lines:
args: -cpu 'host,+kvm_pv_unhalt,+kvm_pv_eoi,hv_vendor_id=NV43FIX,kvm=off'
```

**Explanation:**
- `hv_vendor_id=NV43FIX`: Hides hypervisor from NVIDIA driver (prevents Code 43 error)
- `kvm=off`: Further hides KVM from guest

### Full VM Configuration Example

```bash
cat /etc/pve/qemu-server/100.conf

# Example output:
agent: 1
args: -cpu 'host,+kvm_pv_unhalt,+kvm_pv_eoi,hv_vendor_id=NV43FIX,kvm=off'
balloon: 0
bios: ovmf
boot: order=virtio0;ide2;net0
cores: 6
cpu: host
efidisk0: local-lvm:vm-100-disk-0,efitype=4m,pre-enrolled-keys=1,size=1M
hostpci0: 01:00,pcie=1,x-vga=1
ide2: local:iso/ubuntu-22.04.3-desktop-amd64.iso,media=cdrom
machine: q35
memory: 24576
name: ai-workstation
net0: virtio=XX:XX:XX:XX:XX:XX,bridge=vmbr0
numa: 0
ostype: l26
scsihw: virtio-scsi-pci
smbios1: uuid=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
sockets: 1
virtio0: local-lvm:vm-100-disk-1,discard=on,size=200G
vmgenid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## 7. Guest VM Setup

### Start VM and Install OS

1. Start VM from Proxmox UI
2. Connect via noVNC console (initial boot uses QEMU display)
3. Install Ubuntu/Linux normally
4. After install, remove ISO and reboot

### Install NVIDIA Drivers in Guest

```bash
# SSH into VM (or use console)
ssh user@10.0.1.131

# Update system
sudo apt update && sudo apt upgrade -y

# Install prerequisites
sudo apt install -y build-essential dkms

# Add NVIDIA driver repository
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update

# Install NVIDIA driver (check latest version)
sudo apt install -y nvidia-driver-535

# Reboot
sudo reboot
```

### Verify GPU in Guest

```bash
# Check NVIDIA driver
nvidia-smi

# Expected output:
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xxx       Driver Version: 535.xxx       CUDA Version: 12.x   |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  GeForce GTX 1080 Ti  Off | 00000000:01:00.0 Off |                  N/A |
|  0%   35C    P8    10W / 250W |      0MiB / 11264MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

### Install CUDA Toolkit (Optional)

```bash
# Download CUDA (check latest version for your driver)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-2

# Add to PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify
nvcc --version
```

### Install Docker with NVIDIA Support

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# Test GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

---

## 8. Verification

### Host-Side Checks

```bash
# On Proxmox host

# Verify GPU is passed through
qm config 100 | grep hostpci

# Check VM is using VFIO
cat /sys/bus/pci/devices/0000:01:00.0/driver_override
# Should show: vfio-pci
```

### Guest-Side Checks

```bash
# In the VM

# GPU detected
lspci | grep -i nvidia

# Driver loaded
nvidia-smi

# CUDA works
python3 -c "import torch; print(torch.cuda.is_available())"
# Should print: True

# Memory test
nvidia-smi -q -d MEMORY
```

### Performance Test

```bash
# Install stress test
pip3 install gpustat

# Run GPU stress test
# Option 1: Using nvidia-smi
nvidia-smi dmon -s puc

# Option 2: Using PyTorch
python3 << 'EOF'
import torch
import time

# Check GPU
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# Simple benchmark
x = torch.randn(10000, 10000, device='cuda')
start = time.time()
for _ in range(100):
    y = torch.matmul(x, x)
torch.cuda.synchronize()
print(f"MatMul benchmark: {time.time() - start:.2f}s")
EOF
```

---

## 9. Troubleshooting

### Code 43 Error (Windows) / Driver Fails (Linux)

**Symptoms:** GPU detected but driver fails to load

**Solutions:**

```bash
# 1. Ensure hypervisor hiding is enabled
# In /etc/pve/qemu-server/100.conf:
args: -cpu 'host,+kvm_pv_unhalt,+kvm_pv_eoi,hv_vendor_id=NV43FIX,kvm=off'

# 2. Verify BIOS ROM is not needed (usually not for Linux guests)
# If needed, dump GPU ROM:
cd /sys/bus/pci/devices/0000:01:00.0/
echo 1 > rom
cat rom > /tmp/gpu.rom
echo 0 > rom
# Then add to VM: romfile=/tmp/gpu.rom
```

### VM Won't Start - "IOMMU Group Not Viable"

**Symptoms:** Error about IOMMU groups

**Solutions:**

```bash
# Check IOMMU groups
./root/iommu-groups.sh | grep "01:00"

# If GPU shares group with other devices:
# 1. Move GPU to different PCIe slot
# 2. Pass through all devices in group
# 3. Use ACS override (security risk, last resort)
```

### No Display Output on GPU

**Symptoms:** VM starts but no video from GPU

**Solutions:**

1. Ensure `x-vga=1` is set in hostpci configuration
2. Connect monitor to GTX 1080 Ti outputs
3. Check UEFI display settings in VM

```bash
# Force primary display
qm set 100 -vga none
# Then ensure hostpci has x-vga=1
```

### Poor Performance

**Symptoms:** GPU works but slower than expected

**Solutions:**

```bash
# 1. Verify CPU type is 'host'
qm config 100 | grep cpu

# 2. Check for CPU pinning
taskset -c -p $(pgrep -f "100.*kvm")

# 3. Disable memory ballooning
qm set 100 --balloon 0

# 4. Use hugepages (advanced)
# Add to VM args: -mem-prealloc -mem-path /dev/hugepages
```

### GPU Reset Issues

**Symptoms:** VM won't start after previous shutdown, requires host reboot

**Solutions:**

```bash
# Some GPUs have reset bugs. Workarounds:

# 1. Use vendor-reset module (for AMD GPUs, less relevant for NVIDIA)

# 2. Ensure clean shutdown
qm shutdown 100  # graceful
# vs
qm stop 100      # forced (may cause issues)

# 3. Reset PCI device manually
echo 1 > /sys/bus/pci/devices/0000:01:00.0/reset
```

---

## Appendix A: Quick Reference

### Key Files

| File | Purpose |
|------|---------|
| `/etc/default/grub` | IOMMU boot parameters |
| `/etc/modules` | VFIO module loading |
| `/etc/modprobe.d/vfio.conf` | GPU binding to VFIO |
| `/etc/modprobe.d/blacklist.conf` | Driver blacklisting |
| `/etc/pve/qemu-server/100.conf` | VM configuration |

### Key Commands

| Command | Purpose |
|---------|---------|
| `lspci -nn \| grep -i nvidia` | List NVIDIA devices with IDs |
| `lspci -k \| grep -A 3 nvidia` | Check driver binding |
| `dmesg \| grep -i iommu` | IOMMU status |
| `qm config 100` | View VM config |
| `qm set 100 -hostpci0 XX:XX` | Add PCI device |

### GTX 1080 Ti PCI IDs

| Device | Vendor:Device ID |
|--------|------------------|
| GPU | 10de:1b06 |
| HDMI Audio | 10de:10ef |

---

## Appendix B: AI/ML Software Stack

### Recommended Stack for ai-workstation

| Software | Purpose | Install |
|----------|---------|---------|
| Docker | Containerization | `curl -fsSL https://get.docker.com \| sh` |
| NVIDIA Container Toolkit | GPU in Docker | See Section 7 |
| PyTorch | ML Framework | `pip install torch` |
| TensorFlow | ML Framework | `pip install tensorflow` |
| Jupyter | Notebooks | `pip install jupyterlab` |
| nvtop | GPU Monitor | `apt install nvtop` |

### Docker Compose for AI Services

```yaml
# docker-compose.yml example
version: '3.8'
services:
  jupyter:
    image: jupyter/tensorflow-notebook:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

*HomeLab Specialist - GPU Passthrough Guide v1.0*
