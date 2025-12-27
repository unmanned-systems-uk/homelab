# Homelab Network Migration - Handoff Document

**Date:** 2024-12-27  
**Next Chat:** Fresh context for migration execution  
**Status:** Planning complete, ready for MCP setup

---

## Quick Context for New Chat

This chat discussed homelab network architecture cleanup and migration planning. The user wants to rebuild the network foundation before it becomes unmanageable.

**Current Crisis:** Building on end-of-life hardware (USG Pro 4) with 20+ IoT devices on main WiFi (no VLANs)

**Solution:** Migrate to UDM using parallel network setup (Option C) with automated documentation via UniFi MCP

---

## Critical Discoveries

### 1. Sky Broadband Configuration
**NOT PPPoE** - Uses DHCP with Option 61 authentication:
```yaml
Connection Type: DHCP
DHCP Option 61: anything@skydsl|SKY_HUB_MAC_ADDRESS
IPv6: Disabled (MAP-T incompatibility)
```

### 2. Migration Strategy (Option C)
**Brilliant approach** suggested by user:
- Install UniFi MCP for automated network audit
- Dual ethernet setup (old + new network simultaneously)
- Parallel testing before cutover
- Zero downtime during setup/testing
- 30-60 min family downtime only during final cutover

### 3. Priority Sequence
1. **FIRST:** UniFi MCP setup (blocks everything else)
2. **SECOND:** USG → UDM migration
3. **THIRD:** VLAN implementation
4. **LATER:** Home automation, Claude CLI, Llama, etc.

---

## Documents Created in This Chat

All saved in `C:\Code\homelab\docs\`:

1. **usg-to-udm-migration-plan.md**
   - Complete step-by-step migration guide
   - Sky WAN configuration details
   - 5-phase implementation plan
   - Rollback procedures
   - Risk assessment

2. **network-architecture-discussion-2024-12-27.md**
   - Strategic planning discussion summary
   - Key questions and answers
   - Architecture decisions
   - Critical success factors

3. **GITHUB_ISSUE_UniFi_MCP_Setup.md**
   - GitHub issue template for MCP setup
   - User needs to create this issue manually
   - Assign to homelab-specialist agent

---

## Immediate Next Steps

### For User (Before New Chat)
1. **Create GitHub issue** from `GITHUB_ISSUE_UniFi_MCP_Setup.md`
2. **Gather credentials:**
   - CloudKey IP address
   - CloudKey admin username/password
   - Sky Hub MAC address (for Option 61)
3. **Verify dual ethernet** setup on dev PC possible
4. **Start new chat** with homelab-specialist for MCP setup

### For Homelab Agent (In New Chat)
1. **Read context** from these documents:
   - `docs/usg-to-udm-migration-plan.md`
   - `docs/network-architecture-discussion-2024-12-27.md`
2. **Install UniFi MCP** with user-provided credentials
3. **Generate network audit** (complete device inventory)
4. **Create documentation** in `docs/current-network-state.md`
5. **Report ready** for migration Phase 1

---

## Hardware Summary

**Current:**
- USG Pro 4 (gateway, EOL)
- CloudKey Gen1 (controller)
- Multiple UniFi switches/APs (need MCP to enumerate)
- 20+ Philips Wiz bulbs (on main WiFi, security risk)

**Target:**
- UDM Basic (no PoE)
- Built-in controller (replaces CloudKey)
- VLAN segmentation (10, 20, 30, 40, 50)

**Compute:**
- Proxmox: Legacy-i7 (i7-7820X, 32GB, GTX 1080 Ti + Quadro P620)
- Dev PC: DEV-PC-Ubuntu (i7-10700, 32GB, RTX A2000)
- Pi 5 x3 (8GB each) - one for HomeGate dashboard
- Jetson Orin NX (for potential Llama hosting)

---

## Key Decisions Locked In

✅ **UDM Model:** UDM Basic (no PoE)  
✅ **Migration Strategy:** Option C (parallel setup)  
✅ **WAN Config:** DHCP + Option 61 (NOT PPPoE)  
✅ **VLAN Plan:** 5 VLANs (10, 20, 30, 40, 50)  
✅ **Claude CLI Location:** Proxmox LXC (not Pi)  
✅ **HomeGate Purpose:** Web dashboard (Homer/Dashy), not gateway  
✅ **Priority:** MCP → UDM → VLANs → Everything else  

---

## What NOT to Do

❌ Build more services on USG (it's EOL)  
❌ Add more IoT devices before VLAN setup  
❌ Rush into Home Assistant before network stable  
❌ Skip the MCP setup (needed for migration)  
❌ Big-bang migration (use parallel approach)  

---

## References for New Chat

### Sky Broadband Resources
- UniFi + Sky Setup: https://helpforum.sky.com/t5/Broadband/Sky-Broadband-with-Ubiquiti-Unifi-Dream-Machine-Pro/td-p/4514120
- MAP-T Issue: https://helpforum.sky.com/t5/Broadband/Sky-Fibre-amp-Unifi-Dream-Machine/td-p/4735135

### UniFi Resources
- Setup Guide: https://help.ui.com/hc/en-us/articles/4416276882327-How-to-Set-Up-UniFi
- MCP Server: https://github.com/sirkirby/unifi-network-mcp

---

## Success Criteria for MCP Setup

When MCP is operational:
- [ ] Can list all UniFi devices
- [ ] Can retrieve firewall rules
- [ ] Can access WiFi configurations
- [ ] Can enumerate all clients
- [ ] Documentation generated in `docs/current-network-state.md`

When ready for UDM migration:
- [ ] Complete network inventory documented
- [ ] All current settings exported
- [ ] User has UDM hardware
- [ ] Family downtime window scheduled
- [ ] Dual ethernet tested and working

---

## Timeline Estimate

- **MCP Setup:** 1-2 hours (tonight/tomorrow)
- **Network Audit:** Automated (minutes)
- **UDM Parallel Setup:** Day 1, 2-3 hours (no downtime)
- **Testing/Verification:** Day 1 evening, 1-2 hours
- **Cutover:** Day 2, 30-60 min (family downtime)
- **VLAN Migration:** Week 2, staged (minimal disruption)

**Total:** 2-3 days for complete UDM migration + VLANs

---

## Handoff to New Chat

**To homelab-specialist agent:**

Read these files first:
1. `docs/usg-to-udm-migration-plan.md` - Your playbook
2. `docs/network-architecture-discussion-2024-12-27.md` - Strategic context
3. `docs/GITHUB_ISSUE_UniFi_MCP_Setup.md` - Your first task

Wait for user to provide:
- CloudKey credentials
- Confirmation to proceed

Then:
1. Install UniFi MCP
2. Generate network audit
3. Create `docs/current-network-state.md`
4. Report back when ready for Phase 1

**User will start clean chat for better context management.**

---

## Final Notes

**Brutal Honesty Applied:** No sugarcoating, professional approach  
**Option C Validated:** User's parallel network idea is the correct approach  
**Sky Config Researched:** DHCP + Option 61, NOT PPPoE (critical discovery)  
**Documentation Complete:** All planning captured in markdown  
**Ready to Execute:** Just needs MCP setup to begin  

**Status:** ✅ Planning phase complete, ready for execution

---

**Last Updated:** 2024-12-27  
**Created By:** Claude (this chat)  
**Next Action:** User creates GitHub issue and starts new chat with homelab agent
