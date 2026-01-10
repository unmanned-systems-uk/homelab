# Fiber Uplink Shopping List - HA Pi Medical Alert Network

**Purpose:** Replace copper uplink US 48 ↔ US 24 with fiber
**Reason:** Medical alert system reliability (Nathan diabetes monitoring)
**Priority:** CRITICAL
**Date:** 2026-01-10

---

## RECOMMENDED: 10Gbps Option (Future-proof)

### Components Needed:

| Item | Qty | Specification | Example Product | Est. Cost |
|------|-----|---------------|-----------------|-----------|
| **SFP+ Module** | 2 | 10GBase-SR, LC, MMF, 850nm | Ubiquiti UF-MM-10G | £20-30 each |
| **Fiber Cable** | 1 | LC-LC, OM4, Duplex, Length TBD | FS.com OM4 LC-LC | £15-25 |
| **TOTAL** | | | | **£55-85** |

### Specifications Detail:

**SFP+ Modules (10Gbps):**
- Type: 10GBase-SR (Short Range multimode)
- Connector: LC Duplex
- Fiber Type: Multimode (MMF)
- Wavelength: 850nm
- Distance: Up to 300m (OM3), 400m (OM4)
- Compatible: UniFi US-48, US-24 PoE
- **Recommended:** Ubiquiti UF-MM-10G (guaranteed compatibility)
- **Alternative:** Generic 10GBase-SR (cheaper, usually works)

**Fiber Cable:**
- Type: Duplex LC-LC
- Grade: OM4 (recommended) or OM3 (acceptable)
- Jacket: Plenum-rated (if running through ceiling) or PVC
- Length: Measure distance + 20% slack
  - Estimate for your install: 2m-5m typical
- Color: Aqua (OM3/OM4 standard) or Yellow (accepted)

---

## BUDGET: 1Gbps Option

### Components Needed:

| Item | Qty | Specification | Example Product | Est. Cost |
|------|-----|---------------|-----------------|-----------|
| **SFP Module** | 2 | 1000Base-SX, LC, MMF, 850nm | Generic 1G SFP | £10-15 each |
| **Fiber Cable** | 1 | LC-LC, OM3, Duplex | Generic OM3 | £8-12 |
| **TOTAL** | | | | **£28-42** |

---

## Purchase Links (UK Suppliers)

### Recommended Suppliers:

**Option 1: FS.com (Best Value)**
- SFP+ 10G: https://www.fs.com/uk/products/74667.html (~£18 each)
- OM4 Cable: https://www.fs.com/uk/products/40196.html (~£12)
- Delivery: 3-5 days
- **Total: ~£48**

**Option 2: Amazon UK (Fast Delivery)**
- Search: "10GBase-SR SFP+ Module LC MMF"
- Search: "OM4 LC-LC Fiber Cable"
- Delivery: Next day available
- **Total: ~£60-80**

**Option 3: Ubiquiti Direct (Guaranteed Compatibility)**
- UF-MM-10G: https://eu.store.ui.com/
- Price: ~£25-30 each
- **Total: ~£65-85 (with cable from FS.com)**

---

## Cable Length Guide

**How to Measure:**

1. Measure physical distance from US 48 to US 24
2. Add routing path (around obstacles, cable management)
3. Add 20% slack for service loops
4. Round up to next standard length

**Standard Lengths Available:**
- 0.5m, 1m, 2m, 3m, 5m, 10m, 15m, 20m

**Example:**
- Physical distance: 3m
- Routing path: +1m (around desk)
- Slack: +0.8m (20%)
- **Order: 5m cable**

---

## Compatibility Verification

### US 48 Dev Office Switch:

**Model:** UniFi Switch 48 (US-48-500W or similar)

**SFP/SFP+ Ports:**
- Count: 4x SFP+ ports (10 Gbps capable)
- Location: Right side of switch
- Compatibility: SFP and SFP+ modules (1G or 10G)
- Auto-negotiation: Yes (10G modules run at 1G/10G auto)

**Verified Compatible:**
- ✅ Ubiquiti UF-MM-10G (10G)
- ✅ Ubiquiti UF-MM-1G (1G)
- ✅ Generic 10GBase-SR modules (most work)
- ✅ Generic 1000Base-SX modules (most work)

### US 24 PoE 250W Cinema Switch:

**Model:** UniFi Switch 24 PoE (US-24-250W)

**SFP Ports:**
- Count: 2x SFP ports (shared with copper ports 23/24)
- Location: Right side (ports 25/26)
- Compatibility: SFP and SFP+ modules
- Speed: 1G or 10G (auto-detect)

**Important:**
- SFP ports share bandwidth with ports 23/24
- When SFP used, corresponding copper port disabled
- Recommended: Use SFP Port 25 (disables Port 23)

---

## Installation Materials (Already Have)

You likely already have these, but verify:

- [ ] Fiber cleaning wipes (isopropyl alcohol wipes OK)
- [ ] Cable ties for fiber management
- [ ] Label maker (label "Medical-HA-Fiber-Uplink")

**DO NOT NEED:**
- ❌ Fiber cleaver (pre-terminated cable)
- ❌ Fusion splicer (using patch cable)
- ❌ OTDR (short distance, not needed)

---

## Recommended Purchase (My Advice)

**Best Option for Medical-Critical System:**

```
SOURCE: FS.com UK
──────────────────────────────────────
2x SFP-10GSR-85 (10GBase-SR SFP+)      £36
   - FS.com P/N: 74667
   - 10Gbps, 850nm, LC, MMF

1x OM4 LC-LC 5m Duplex Cable           £12
   - FS.com P/N: 40196
   - Aqua jacket, LSZH rated

TOTAL: £48 + shipping (~£5)
──────────────────────────────────────
GRAND TOTAL: ~£53

Delivery: 3-5 business days
Quality: Excellent (FS.com is industry standard)
Warranty: Lifetime
```

**Why This Option:**
- 10Gbps for only £20 more than 1G
- FS.com excellent quality (used in datacenters worldwide)
- Lifetime warranty
- Future-proof (10G available when needed)
- Medical-grade reliability

---

## Alternative: If You Need It TODAY

**Amazon UK Next-Day:**

Search terms:
- "10GBASE-SR SFP+ Transceiver 850nm LC MMF"
- "OM4 LC to LC Fiber Optic Cable Duplex Multimode"

Filter: Prime eligible, 4+ stars

**Expected Cost:** £70-90 (premium for next-day)

**Verify before ordering:**
- ✅ 850nm wavelength
- ✅ LC connector (not SC or ST)
- ✅ Duplex (not simplex)
- ✅ Multimode (not singlemode)
- ✅ Compatible with 10GBase-SR

---

## Post-Purchase Checklist

When components arrive:

- [ ] Inspect SFP modules (no damage, dust caps present)
- [ ] Inspect fiber cable (no sharp bends, ends clean)
- [ ] Remove dust caps from SFP LC ports
- [ ] Clean fiber cable ends (even if new)
- [ ] Test SFP modules in switch (should auto-detect)
- [ ] Test link before final installation

---

## Return Policy / Warranty

**FS.com:**
- 30-day return policy
- Lifetime warranty on SFP modules
- Free replacement for DOA units

**Amazon:**
- 30-day return (keep packaging)
- Varies by seller

**Ubiquiti:**
- 1-year warranty
- RMA process via UI.com

**Recommendation:** Order 1 extra cable as backup (only £12)

---

## Technical Notes

### Why Multimode (MMF) not Singlemode (SMF)?

**Short answer:** Distance <100m = multimode is perfect and cheaper

| Type | Distance | Cost | Use Case |
|------|----------|------|----------|
| Multimode (OM3/OM4) | Up to 300m | Lower | Building/datacenter |
| Singlemode (OS2) | Up to 10km+ | Higher | Campus/WAN |

**Your case:** Switch-to-switch in same room = multimode perfect.

### Why 850nm not 1310nm?

- 850nm = Standard for multimode short-range
- 1310nm = Singlemode long-range
- Your SFP modules need to match fiber type

### OM3 vs OM4 Fiber?

Both work for your distance. OM4 slightly better:

| Grade | 10G Distance | Cost Difference |
|-------|--------------|-----------------|
| OM3 | 300m | Baseline |
| OM4 | 400m | +£3-5 |

**Recommendation:** OM4 (future-proof, minimal cost difference)

---

## Post-Installation Verification Commands

After installing fiber uplink:

```bash
# Check link status (should show fiber link)
# UniFi Controller → Devices → US 48 → SFP Port X
# Should display: 10 Gbps FDX (or 1 Gbps if using 1G SFP)

# Verify HA Pi reachable
ping -c 100 10.0.1.150
# Should show 0% packet loss

# Test under load (HA Pi restart - the original failure trigger)
ssh homelab@10.0.1.150 "sudo reboot"
# Monitor - should NOT drop network

# Long-term stability test
ping -i 60 10.0.1.150 > /tmp/ha-pi-ping-test.log &
# Let run for 24 hours, check log for any drops
```

---

**RECOMMENDATION:** Order FS.com 10G option (£53 total). Best value, medical-grade reliability, future-proof.

**URGENT:** If medical alert criticality requires TODAY, use Amazon next-day (£80).

---

*HomeLab Infrastructure - Medical System Network Upgrade*
*Shopping List Generated: 2026-01-10*
