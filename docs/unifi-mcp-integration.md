# UniFi MCP Integration Plan

**Status:** Planned
**Priority:** High - enables Claude network visibility

---

## Available UniFi MCP Servers

### Option 1: unifi-network-mcp (Recommended)
- **Repo:** [sirkirby/unifi-network-mcp](https://github.com/sirkirby/unifi-network-mcp)
- **Features:**
  - Lazy tool registration (96% token savings)
  - Code-execution mode (98% token reduction)
  - Minimal context usage
- **Best for:** Efficient, production use

### Option 2: mcp-unifi-network (Full Featured)
- **Repo:** [gilberth/mcp-unifi-network](https://github.com/gilberth/mcp-unifi-network)
- **Features:**
  - Dual firewall support (legacy + Zone-Based ZBF)
  - Automatic version detection
  - Device management (gateways, switches, APs, clients)
  - Network admin (VLANs, networks, IP groups)
  - Real-time monitoring
- **Best for:** Comprehensive network management

### Option 3: mcp-server-unifi
- **Repo:** [zcking/mcp-server-unifi](https://lobehub.com/mcp/zcking-mcp-server-unifi)
- **Features:**
  - Natural language interactions
  - UniFi API wrapper
- **Auth:** API key via `UNIFI_API_KEY` env var

---

## Current Setup

| Component | Current | Future |
|-----------|---------|--------|
| Gateway | USG-Pro-4 | Dream Machine |
| Controller | CloudKey Gen1 v1.1.19 | Built-in to Dream Machine |
| Controller Type | Self-hosted | Self-hosted |

## Requirements

1. **UniFi Controller Access**
   - Controller IP: CloudKey IP (current) or Dream Machine IP (future)
   - API credentials (username/password or API key)
   - Network access from dev machine (10.0.1.x subnet)

2. **Claude Code Config**
   - Add MCP server to `~/.claude/settings.json` or project `.mcp.json`

---

## Configuration Template

```json
{
  "mcpServers": {
    "unifi": {
      "command": "npx",
      "args": ["-y", "@sirkirby/unifi-network-mcp"],
      "env": {
        "UNIFI_HOST": "https://YOUR_CONTROLLER_IP:8443",
        "UNIFI_USERNAME": "your-username",
        "UNIFI_PASSWORD": "your-password",
        "UNIFI_SITE": "default"
      }
    }
  }
}
```

---

## Capabilities Once Integrated

- List all network devices (switches, APs, clients)
- View device status and statistics
- Monitor bandwidth and client connections
- View/manage VLANs and networks
- Firewall rule visibility
- Real-time network health

---

## Migration Consideration

Current: USG-Pro-4 → Future: Dream Machine

- MCP should work with both (same UniFi API)
- May need controller reconfiguration during migration
- Test MCP access after migration

---

## Next Steps

1. [ ] Determine UniFi Controller location (self-hosted or cloud)
2. [ ] Create API credentials for Claude access
3. [ ] Choose MCP server (recommend: sirkirby for efficiency)
4. [ ] Install and configure
5. [ ] Test network enumeration
6. [ ] Document all discovered devices in inventory

---

*Created: 2025-12-12*
