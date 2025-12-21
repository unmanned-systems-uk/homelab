# Proxmox BIOS Performance Fix Guide

**Host:** 10.0.1.200 (Proxmox)
**Motherboard:** ASUS PRIME X299-DELUXE
**BIOS Version:** 3601
**Date:** 2025-12-21

---

## Current Performance Issues

### Issue 1: RAM Running at JEDEC Default (Slow)
**Current:** DDR4-2133 MT/s
**Capable:** DDR4-3200 MT/s (rated speed)
**Supported:** DDR4-2933 MT/s (with 4 DIMMs on X299)
**Performance Loss:** ~35% memory bandwidth wasted

### Issue 2: GPUs Running at PCIe 1.0 (Very Slow)
**Quadro P620:**
- Current: PCIe 1.0 x8 = 16 Gb/s
- Capable: PCIe 3.0 x16 = 126 Gb/s
- **Performance Loss: 87.3%** (7.8x slower!)

**GTX 1080 Ti:**
- Current: PCIe 1.0 x16 = 32 Gb/s
- Capable: PCIe 3.0 x16 = 126 Gb/s
- **Performance Loss: 74.6%** (3.9x slower!)

---

## BIOS Fix Procedure

### Before You Start
```bash
# Schedule maintenance window (requires host reboot)
# Estimated downtime: 10-15 minutes

# Shutdown all VMs first
ssh root@10.0.1.200 << 'SHUTDOWN'
for vmid in $(qm list | awk "NR>1 {print \$1}"); do
  echo "Shutting down VM $vmid..."
  qm shutdown $vmid
done

# Wait for all to shutdown
sleep 60

# Verify all stopped
qm list
SHUTDOWN
```

### Step 1: Enter BIOS
1. Reboot Proxmox host
2. Press **DEL** or **F2** during POST
3. Enter BIOS Setup

### Step 2: Fix RAM Speed (Enable XMP)

**Navigation:**
```
AI Tweaker → Memory Settings
```

**Settings to Change:**
1. **Memory Frequency:** Currently "Auto" (defaults to 2133)
   - Change to: **DDR4-2933** (highest supported with 4 DIMMs)

   OR (easier method):

2. **XMP (Extreme Memory Profile):** Currently "Disabled"
   - Change to: **XMP Profile 1** or **XMP II**
   - This will auto-select 2933 MHz (BIOS knows 3200 won't work with 4 DIMMs)

**What XMP Does:**
- Automatically loads optimal timings from RAM SPD chip
- Corsair CMK32GX4M4D3200C16 has XMP profile pre-configured
- BIOS will auto-select 2933 instead of 3200 (because 4 DIMMs populated)

### Step 3: Fix PCIe Speed (Enable Gen 3)

**Navigation:**
```
Advanced → System Agent (SA) Configuration → PEG Port Configuration
```

**Settings to Change:**

1. **PCIe Speed:** Currently "Auto" or "Gen1"
   - Change to: **Gen3** or **Auto** (if Auto isn't working, force Gen3)

2. **PCIEX16_1 Link Speed:**
   - Change to: **Gen3**

3. **PCIEX16_2 Link Speed:**
   - Change to: **Gen3**

**Alternative Location (if above not found):**
```
Advanced → PCH Configuration → PCI Express Configuration
```

Settings:
- **PCI Express Native ASPM:** Disabled (or Auto)
- **PCIe Speed:** Gen3
- **Above 4G Decoding:** **Enabled** ← Important for multiple GPUs!
- **Resizable BAR Support:** Enabled (if available)

### Step 4: Verify Other Important Settings

While you're in BIOS, confirm these are enabled:

**For Virtualization (Proxmox):**
```
Advanced → CPU Configuration
├─ Intel Virtualization Technology: Enabled ✅
├─ Intel VT-d: Enabled ✅
├─ SW Guard Extensions (SGX): Disabled
└─ Hyper-Threading: Enabled ✅
```

**For Performance:**
```
AI Tweaker → CPU Core Ratio
├─ CPU Core Ratio: Auto (allows Turbo Boost)
├─ CPU Cache Ratio: Auto
└─ Power Limit: Disabled (allow full boost)

Advanced → CPU Configuration
├─ Intel SpeedStep: Enabled (power saving)
├─ Turbo Mode: Enabled ✅
└─ CPU C-States: Enabled (power saving, OK for Proxmox)
```

### Step 5: Save and Exit
1. Press **F10** (Save Changes and Exit)
2. Confirm: **Yes**
3. System will reboot

### Step 6: Verify Changes Applied

**Boot into Proxmox, then SSH and check:**

```bash
ssh root@10.0.1.200 << 'VERIFY'
echo "=== RAM Speed Verification ==="
dmidecode -t memory | grep -E "Speed:|Configured" | head -8

echo -e "\n=== GPU PCIe Speed Verification ==="
lspci -vvv -s 17:00.0 | grep "LnkSta:" | head -1
lspci -vvv -s 65:00.0 | grep "LnkSta:" | head -1

echo -e "\n=== Expected Results ==="
echo "RAM: Should show 2933 MT/s"
echo "P620: Should show 'Speed 8GT/s, Width x8 (or x16)'"
echo "GTX 1080 Ti: Should show 'Speed 8GT/s, Width x16'"
VERIFY
```

**Expected Output:**
```
=== RAM Speed Verification ===
Speed: 2933 MT/s
Configured Memory Speed: 2933 MT/s

=== GPU PCIe Speed Verification ===
LnkSta: Speed 8GT/s, Width x16  ← PCIe 3.0!
LnkSta: Speed 8GT/s, Width x16  ← PCIe 3.0!
```

### Step 7: Start VMs

```bash
ssh root@10.0.1.200 << 'STARTUP'
# Start VMs in order
qm start 101  # harbor
sleep 20
qm start 100  # whisper
sleep 20
qm start 151  # pterodactyl
sleep 20
qm start 210  # ccpm-vm

# Verify all running
qm list
STARTUP
```

---

## Performance Improvements Expected

### Before Fix:
- RAM: 2133 MT/s = ~17 GB/s bandwidth
- P620: PCIe 1.0 x8 = 2 GB/s bandwidth
- GTX 1080 Ti: PCIe 1.0 x16 = 4 GB/s bandwidth

### After Fix:
- RAM: 2933 MT/s = ~23 GB/s bandwidth **(+35% faster!)**
- P620: PCIe 3.0 x8 = 8 GB/s bandwidth **(+300% faster!)**
- GTX 1080 Ti: PCIe 3.0 x16 = 16 GB/s bandwidth **(+300% faster!)**

### Real-World Impact:
- **VM disk I/O:** 30-40% faster (better RAM speed)
- **GPU workloads (whisper-tts VM):** 3-4x faster (PCIe 3.0)
- **Memory-intensive VMs:** 35% better performance
- **Overall system responsiveness:** Noticeably improved

---

## Troubleshooting

### Problem: RAM Still Shows 2133 After XMP Enable

**Cause:** XMP might not apply correctly with 4 DIMMs

**Fix:**
1. Re-enter BIOS
2. Go to: AI Tweaker → Memory Frequency
3. **Manually select:** DDR4-2933
4. Leave XMP disabled if it's causing issues
5. Save and reboot

### Problem: GPUs Still at PCIe 1.0 After Setting Gen3

**Cause:** BIOS may have multiple conflicting settings

**Fix:**
1. Re-enter BIOS
2. Check **ALL** these locations and set to Gen3:
   - Advanced → System Agent Configuration → PEG Port Configuration
   - Advanced → PCH Configuration → PCI Express Configuration
   - Advanced → Onboard Devices Configuration → PCIe Speed
3. **Disable PCIe ASPM** (power saving can force Gen1)
4. **Enable Above 4G Decoding**
5. Save and reboot

### Problem: System Won't POST After Changes

**Fix:**
1. Power off completely
2. Press and hold power button for 10 seconds
3. Clear CMOS:
   - **Method 1:** Remove CMOS battery for 30 seconds
   - **Method 2:** Use Clear CMOS jumper on motherboard
4. Boot to BIOS defaults
5. Apply changes **one at a time**:
   - First: RAM speed only, test boot
   - Then: PCIe speed, test boot

---

## After CPU/RAM Upgrade

When you install the **i9-10940X + 128GB RAM**, you'll need to adjust settings:

### RAM Changes:
```
Old: 32GB (4x 8GB) DDR4-2933 ✅
New: 128GB (8x 16GB) DDR4-2666 ← Lower speed with 8 DIMMs!
```

**BIOS Change:**
- XMP will auto-select **2666 MHz** (correct for 8 DIMMs)
- OR manually select: **DDR4-2666**
- Do NOT try to force 2933 - unstable with 8 DIMMs!

### GPU Changes (If Adding GTX 1070 Ti):
```
Slot 1: GTX 1070 Ti (new, from main PC)
Slot 2: Empty (or another GPU)
Slot 4: GTX 1080 Ti (existing)
Slot 5: Quadro P620 (for console) OR remove entirely
```

**BIOS Settings:**
- Above 4G Decoding: **Enabled** (required for 3 GPUs)
- Resizable BAR: **Enabled** (if available)
- All PCIe slots: **Gen3**

---

## Quick Reference Card

**When doing BIOS updates, always check:**

| Setting | Location | Value |
|---------|----------|-------|
| XMP Profile | AI Tweaker → Memory | Enabled |
| Memory Frequency | AI Tweaker → Memory | 2933 (now), 2666 (after upgrade) |
| PCIe Speed | Advanced → SA Config → PEG | Gen3 |
| Above 4G Decode | Advanced → PCH Config | Enabled |
| VT-x | Advanced → CPU Config | Enabled |
| VT-d | Advanced → CPU Config | Enabled |
| Turbo Mode | Advanced → CPU Config | Enabled |

---

## Safety Notes

✅ **Safe to change:**
- Memory speed (XMP)
- PCIe speed (Gen3)
- Virtualization settings
- Turbo mode

⚠️ **Don't touch:**
- CPU voltage (leave Auto)
- Memory voltage (leave Auto or 1.35V for XMP)
- Load Line Calibration (leave Auto)
- CPU power limits (leave disabled/auto)

---

## Summary

**Do This Now (Before CPU/RAM Upgrade):**
1. Enable XMP or set RAM to DDR4-2933
2. Set all PCIe slots to Gen3
3. Verify changes applied

**Performance Gain:** 35% faster RAM, 300% faster GPU bandwidth

**Downtime:** 10-15 minutes (shutdown VMs, change BIOS, boot, start VMs)

**Risk:** Very low (all reversible settings)

---

**Ready to proceed?** Let me know when you want to schedule the BIOS update!
