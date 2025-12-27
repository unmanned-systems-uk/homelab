# GitHub Issue: Setup UniFi MCP Server for Network Visibility

**Title:** Setup UniFi MCP Server for Network Visibility

**Labels:** `priority:critical`, `infrastructure`, `network`

**Assigned:** homelab-specialist

---

## Overview

**Priority:** CRITICAL - Blocks USG → UDM migration  
**Agent:** homelab-specialist  
**Timeline:** ASAP (before UDM migration can begin)

---

## Objective

Install and configure UniFi Network MCP server to provide Claude with complete network visibility, enabling automated documentation and migration planning for the USG Pro 4 → UDM migration.

---

## Why This is Critical

1. **Blocks Migration:** UDM migration cannot proceed without complete network audit
2. **Prevents Errors:** Automated documentation eliminates manual configuration mistakes
3. **Real-Time Comparison:** Enables parallel network testing with live config comparison
4. **Documentation:** Auto-generates network topology, device inventory, firewall rules

---

## Technical Requirements

### MCP Server Selection

**Recommended:** `@sirkirby/unifi-network-mcp`
- Lazy tool registration (96% token savings)
- Code-execution mode (98% token reduction)
- Minimal context usage
- Best for production use

**Alternative:** `gilberth/mcp-unifi-network` (if more features needed)

### Configuration Needed

```json
{
  "mcpServers": {
    "unifi": {
      "command": "npx",
      "args": ["-y", "@sirkirby/unifi-network-mcp"],
      "env": {
        "UNIFI_HOST": "https://CLOUDKEY_IP:8443",
        "UNIFI_USERNAME": "admin_username",
        "UNIFI_PASSWORD": "admin_password",
        "UNIFI_SITE": "default"
      }
    }
  }
}
```

### Prerequisites from User

**REQUIRED before setup can proceed:**
- [ ] CloudKey IP address
- [ ] CloudKey admin username
- [ ] CloudKey admin password
- [ ] Network access from dev machine to CloudKey

---

## Deliverables

Once MCP is operational, generate:

### 1. Network Device Inventory
- [ ] All UniFi switches (models, ports, IPs)
- [ ] All UniFi access points (models, channels, IPs)
- [ ] All connected clients (devices, IPs, MACs)
- [ ] Current network topology

### 2. Configuration Export
- [ ] All firewall rules
- [ ] Port forward configurations
- [ ] DHCP reservations
- [ ] WiFi SSIDs (names, passwords, security settings)
- [ ] Current VLAN configuration (if any)

### 3. Documentation Generation
- [ ] Create `docs/current-network-state.md` with complete audit
- [ ] Create network topology diagram
- [ ] Export configurations for migration reference

---

## Testing Criteria

MCP setup is successful when:
- [ ] MCP server connects to CloudKey without errors
- [ ] Can list all UniFi devices
- [ ] Can retrieve firewall rules
- [ ] Can access WiFi configurations
- [ ] Can enumerate all connected clients

---

## Installation Steps

### 1. Add MCP Server to Claude Code Config

Location: `~/.claude/settings.json` or project `.mcp.json`

```bash
# If using project-specific config
cd ~/ccpm-workspace/HomeLab
# Edit .mcp.json
```

### 2. Test MCP Connection

```bash
# Verify MCP server starts
# Check logs for connection errors
# Test basic commands
```

### 3. Generate Initial Audit

Run comprehensive network scan:
- List all devices
- Export all configurations
- Document current state

### 4. Create Documentation

Generate markdown files in `docs/`:
- Network device inventory
- Current configurations
- Migration baseline

---

## Known Issues / Troubleshooting

### CloudKey Connection
- Ensure HTTPS access to CloudKey:8443
- Self-signed cert may require trust
- Firewall may block connection

### Authentication
- Verify admin credentials are correct
- Check account has full permissions
- CloudKey may require specific user role

### Network Access
- Dev machine must be on 10.0.1.x network
- CloudKey must be reachable via IP
- Port 8443 must not be blocked

---

## Dependencies

**Blocks:**
- USG → UDM Migration (cannot proceed without audit)
- VLAN implementation planning
- Network architecture documentation

**Requires:**
- CloudKey credentials from user
- Network access to 10.0.1.x subnet
- NPM/Node.js installed (for MCP server)

---

## Success Criteria

✅ **MCP Setup Complete When:**
1. MCP server connects to CloudKey successfully
2. Can enumerate all network devices
3. Can retrieve all configurations
4. Documentation generated and committed
5. Claude has full network visibility

✅ **Ready for Migration When:**
1. Complete network inventory documented
2. All current settings exported
3. Firewall rules catalogued
4. DHCP reservations listed
5. WiFi configs backed up

---

## Related Documents

- `docs/usg-to-udm-migration-plan.md` - Complete migration guide
- `docs/network-architecture-discussion-2024-12-27.md` - Planning discussion
- `docs/unifi-mcp-integration.md` - MCP documentation

---

## Agent Instructions

@homelab-specialist:

1. Wait for user to provide CloudKey credentials
2. Install UniFi MCP server with provided credentials
3. Test connection and verify network access
4. Run comprehensive network audit
5. Generate documentation files in `docs/`
6. Report back with inventory summary
7. Signal completion when audit is ready for review

**Do NOT proceed without user providing credentials.**

---

## Next Steps After Completion

1. Review network audit with user
2. Identify any missing/custom configurations
3. Proceed with UDM parallel setup (Phase 1)
4. Begin migration planning with real config data

---

**Status:** ⏳ Awaiting CloudKey credentials from user  
**Assigned:** homelab-specialist agent  
**Priority:** CRITICAL  
**Timeline:** ASAP
