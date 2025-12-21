# Proxmox Host Upgrade Guide - Physical Hardware

**Current System:** 10.0.1.200 (Proxmox Host)
**Motherboard:** ASUS PRIME X299-DELUXE
**Current CPU:** Intel i7-7820X (8C/16T @ 3.6GHz)
**Current RAM:** 32GB DDR4 (4x 8GB @ 2133MHz)
**Socket:** LGA 2066

---

## CPU Upgrade Path

### Current BIOS Version
```
Version: 3601
Date: 09/24/2021
```

### Step 1: Check CPU Compatibility

**Your board supports:**
- ✅ Skylake-X (7th gen) - Current CPU
- ✅ Cascade Lake-X (10th gen) - **Requires BIOS 3006 or newer**

**Current BIOS (3601) = ✅ READY for any CPU!**

### Recommended CPUs (in order):

#### Option 1: Intel i9-10980XE (BEST)
- **Cores:** 18 cores / 36 threads (2.25x current)
- **Clock:** 3.0 GHz base, 4.6 GHz boost
- **Cache:** 24.75 MB L3
- **TDP:** 165W
- **Price:** $400-600 (used market)
- **Performance:** ~150% better multi-threaded
- **Proxmox Capacity:** Can run 15-18 VMs comfortably

#### Option 2: Intel i9-10940X (BEST VALUE)
- **Cores:** 14 cores / 28 threads (1.75x current)
- **Clock:** 3.3 GHz base, 4.6 GHz boost
- **Cache:** 19.25 MB L3
- **TDP:** 165W
- **Price:** $300-450 (used)
- **Performance:** ~120% better multi-threaded
- **Proxmox Capacity:** Can run 12-14 VMs comfortably

#### Option 3: Intel i9-9980XE (Good)
- **Cores:** 18 cores / 36 threads
- **Clock:** 3.0 GHz base, 4.4 GHz boost
- **Price:** $350-500 (used)
- **Note:** Older gen than 10th, slightly slower boost

#### Option 4: Intel i9-9940X (Budget)
- **Cores:** 14 cores / 28 threads
- **Clock:** 3.3 GHz base, 4.4 GHz boost
- **Price:** $250-400 (used)

---

## RAM Upgrade Path

### Current Configuration
```
Total: 32GB (4x 8GB DDR4-2133)
Populated Slots: A1, B1, C1, D1
Empty Slots: A2, B2, C2, D2
Maximum Capacity: 128GB (8x 16GB)
```

### RAM Upgrade Options

#### Option 1: Add 32GB (Total: 64GB)
**Cost:** ~$80-120
```
Buy: 4x 8GB DDR4-3200 (or 2933) matching Corsair
Install in: A2, B2, C2, D2
Result: 64GB total (8x 8GB)
```

#### Option 2: Replace All (Total: 128GB)
**Cost:** ~$250-350
```
Remove: All current 4x 8GB sticks
Buy: 8x 16GB DDR4-3200 ECC or non-ECC
Install in: All 8 slots
Result: 128GB total (8x 16GB)
```

#### Option 3: Max Out (Total: 256GB)
**Cost:** ~$600-800
```
Remove: All current sticks
Buy: 8x 32GB DDR4-3200
Install in: All 8 slots
Result: 256GB total (8x 32GB)
Note: Check CPU support for 256GB (10980XE supports it)
```

### Recommended RAM Speed
- **Current:** DDR4-2133 (slow)
- **Recommended:** DDR4-3200 or DDR4-2933
- **Benefit:** ~30% better memory bandwidth
- **Note:** X299 supports quad-channel, so install in sets of 4

---

## Upgrade Process

### CPU Upgrade Steps

#### 1. Verify BIOS Version (Already Done)
```bash
ssh root@10.0.1.200 "dmidecode -t bios | grep Version"
# Current: 3601 ✅ (supports 10th gen)
```

#### 2. Backup Everything
```bash
# Backup Proxmox config
ssh root@10.0.1.200 << 'BACKUP'
mkdir -p /root/backup-before-cpu-upgrade
cp -r /etc/pve /root/backup-before-cpu-upgrade/
vzdump --all --compress zstd --storage <storage-name>
BACKUP
```

#### 3. Shutdown Host
```bash
ssh root@10.0.1.200 "shutdown -h now"
```

#### 4. Physical CPU Replacement
1. **Power off completely** and unplug power
2. **Discharge static:** Touch metal case
3. **Remove cooler** (careful with thermal paste)
4. **Release CPU socket lever**
5. **Remove old i7-7820X**
6. **Clean socket** (compressed air, no liquids)
7. **Install new CPU** (align triangle, don't force)
8. **Apply thermal paste** (pea-sized dot center)
9. **Reinstall cooler** (ensure good contact)
10. **Reconnect power**

#### 5. First Boot
```bash
# Watch POST screen
# CPU should be detected
# Press DEL to enter BIOS
# Verify new CPU shows correctly
# Save and exit
```

#### 6. Verify in Proxmox
```bash
ssh root@10.0.1.200 << 'VERIFY'
echo "=== New CPU Info ==="
lscpu | grep -E "Model name|CPU\(s\)|Core|Thread"

echo -e "\n=== Performance Test ==="
# Run quick benchmark
sysbench cpu --threads=32 run | grep "events per second"
VERIFY
```

---

## RAM Upgrade Steps

### Adding More RAM (Easiest)

#### 1. Shutdown Host
```bash
ssh root@10.0.1.200 "shutdown -h now"
```

#### 2. Install New Sticks
1. Power off and unplug
2. Ground yourself
3. Open empty slots: A2, B2, C2, D2
4. Insert new 8GB sticks (press firmly until clips snap)
5. Close case, reconnect power

#### 3. Boot and Verify
```bash
ssh root@10.0.1.200 "free -h"
# Should show new total (64GB)
```

### Replacing All RAM (For 128GB+)

1. Shutdown host
2. Remove all 4 existing 8GB sticks
3. Install 8x 16GB sticks in all slots
4. Boot and verify

---

## Performance Comparison

### Current (i7-7820X + 32GB)
- 8 cores / 16 threads
- Can comfortably run: 6-8 VMs
- Total RAM: 32GB
- Average per VM: ~4GB

### After i9-10980XE + 128GB
- 18 cores / 36 threads (2.25x more)
- Can comfortably run: **15-20 VMs**
- Total RAM: 128GB (4x more)
- Average per VM: ~6-8GB
- **Much better for Proxmox workloads**

---

## Cost Breakdown

### Option 1: CPU Only (i9-10940X)
- CPU: $300-450 (used)
- Thermal paste: $10
- **Total:** ~$350-460
- **Benefit:** 75% more CPU power

### Option 2: CPU + 32GB RAM (64GB total)
- CPU: $300-450
- RAM: $80-120 (4x 8GB DDR4-3200)
- **Total:** ~$430-570
- **Benefit:** 75% more CPU + 100% more RAM

### Option 3: CPU + Replace All RAM (128GB)
- CPU: $450-600 (i9-10980XE)
- RAM: $250-350 (8x 16GB DDR4-3200)
- **Total:** ~$700-950
- **Benefit:** 125% more CPU + 300% more RAM
- **⭐ Best bang for buck long-term**

---

## Important Considerations

### Power Supply
Your X299 board likely has 8-pin + 4-pin CPU power connectors.
- **Check:** Does your PSU have these connectors?
- **i9-10980XE TDP:** 165W (but can boost to 250W+)
- **Recommended PSU:** 750W+ (good quality)

### CPU Cooler
- **Current:** What cooler do you have?
- **Required:** 165W+ TDP rating
- **Options:**
  - Noctua NH-D15 (~$100, best air cooler)
  - Corsair H115i AIO (~$150, 280mm liquid)
  - Be Quiet! Dark Rock Pro 4 (~$90)

Check that your current cooler supports 165W TDP!

### Thermal Management
```bash
# After upgrade, monitor temps
ssh root@10.0.1.200 << 'MONITOR'
watch -n 2 'sensors | grep -E "Core|Package"'
# Package should stay under 80°C under load
MONITOR
```

---

## Where to Buy CPUs (Used Market)

### Recommended Platforms
1. **eBay** - Good buyer protection, check seller ratings
2. **r/hardwareswap** (Reddit) - Good prices, verify timestamps
3. **ServerTheHome Forums** - Enthusiast community
4. **Local Craigslist/FB Marketplace** - Can test before buying

### What to Check
- ✅ Seller has good ratings/history
- ✅ CPU comes with original packaging (ideal)
- ✅ Photos show actual CPU markings
- ✅ Return policy offered
- ❌ Avoid "CPU only, no returns" listings
- ❌ Skip CPUs with bent pins (LGA2066 pins on board, easier to damage)

---

## BIOS Settings After Upgrade

### Recommended Settings for Proxmox

```
AI Tweaker / Performance:
- XMP Profile: Enabled (for RAM speed)
- CPU Power Limit: Disabled (allow full boost)

Advanced:
- Virtualization (VT-x): Enabled ✅
- VT-d: Enabled ✅
- C-States: Enabled (power saving)
- Turbo Mode: Enabled

Boot:
- Fast Boot: Disabled
- CSM: Disabled (UEFI only)
```

---

## Post-Upgrade VM Reallocation

After upgrade to 18 cores / 128GB:

### Current VMs
```
100 | whisper  | 6 cores | 24GB
101 | harbor   | 2 cores | 4GB
210 | ccpm-vm  | 4 cores | 8GB
151 | lag      | 1 core  | 2GB  ← Can upgrade to 4 cores!
```

### New Allocation (Example)
```
Total: 18 cores / 128GB

100 | whisper     | 8 cores  | 32GB  (upgraded)
101 | harbor      | 2 cores  | 8GB   (more RAM)
210 | ccpm-vm     | 4 cores  | 16GB  (more RAM)
151 | pterodactyl | 4 cores  | 16GB  (CPU + RAM upgrade)
NEW | game-server | 4 cores  | 24GB  (dedicated game VM)

Reserved for host: 2 cores, 16GB
```

---

## Timeline

1. **Order CPU:** 1-2 weeks (shipping)
2. **BIOS update:** Not needed (already 3601)
3. **Physical install:** 1-2 hours (CPU swap)
4. **Testing:** 1 hour (verify all VMs boot)
5. **RAM upgrade:** +30 mins (if doing same time)

**Total downtime:** 2-4 hours

---

## Risks & Mitigation

### Potential Issues
1. **CPU DOA (Dead on Arrival)**
   - Mitigation: Buy from reputable seller with returns
   
2. **Bent socket pins**
   - Mitigation: Be VERY careful during install, don't force
   
3. **Insufficient cooling**
   - Mitigation: Check cooler TDP rating first
   
4. **Power supply overload**
   - Mitigation: Verify PSU has 750W+ and proper connectors

### Safety Checklist
- ✅ Back up all VMs before starting
- ✅ Have your current CPU available (in case rollback needed)
- ✅ Test new CPU with minimal config first
- ✅ Monitor temps for first 24 hours

---

## My Recommendation

### Best Upgrade Path (Budget-Conscious)
```
1. Buy i9-10940X ($350)
2. Add 32GB RAM ($100) = 64GB total
3. Total cost: ~$450
4. Result: 75% more CPU + 100% more RAM
```

### Best Upgrade Path (Future-Proof)
```
1. Buy i9-10980XE ($550)
2. Replace all RAM with 8x16GB ($300) = 128GB
3. Upgrade PSU if needed ($100)
4. Total cost: ~$950
5. Result: 125% more CPU + 300% more RAM
6. Will last 5+ years for Proxmox hosting
```

---

## Summary

### Can you upgrade?
- **CPU:** ✅ YES - Up to i9-10980XE (18 cores)
- **RAM:** ✅ YES - Up to 128GB easily (256GB max)
- **Motherboard:** ✅ EXCELLENT - No need to replace!

### Should you upgrade?
- **If running many VMs:** ✅ YES - Worth it
- **If 8 cores sufficient:** Maybe wait
- **If RAM pressure:** ✅ YES - Easy upgrade

### Bottom Line
Your **ASUS PRIME X299-DELUXE** is a fantastic board with lots of upgrade headroom. The i9-10980XE or i9-10940X would be excellent upgrades, and adding RAM is straightforward.

**Go for it!** 🚀

