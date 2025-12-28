# UniFi MCP Server Setup

## Overview

This document describes how to configure the UniFi Network MCP server for Claude Code.

**MCP Server:** `@sirkirby/unifi-network-mcp`
**Controller:** UDM Pro at 10.0.1.1

---

## Configuration

**Config Location:** `/home/anthony/HomeLab/.mcp.json`

```json
{
  "mcpServers": {
    "unifi": {
      "command": "npx",
      "args": ["-y", "@sirkirby/unifi-network-mcp"],
      "env": {
        "UNIFI_HOST": "https://10.0.1.1",
        "UNIFI_USERNAME": "admin",
        "UNIFI_PASSWORD": "<password>",
        "UNIFI_SITE": "default"
      }
    }
  }
}
```

**Note:** The actual `.mcp.json` file is gitignored for security.

---

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `unifi_list_devices` | List all UniFi devices (switches, APs) |
| `unifi_get_clients` | Get connected clients |
| `unifi_get_networks` | Get network/VLAN configurations |
| `unifi_get_firewalls` | Get firewall rules |
| `unifi_get_port_forwards` | Get port forwarding rules |

---

## Prerequisites

1. **Node.js** must be installed
2. **npx** must be in PATH (comes with Node.js)
3. Network access to 10.0.1.1 (UDM Pro)

---

## Verification

After configuration, restart Claude Code and verify MCP tools are available.

Test commands:
- List devices: Use `unifi_list_devices`
- Get clients: Use `unifi_get_clients`

---

## Network Details

| Device | IP | Role |
|--------|-----|------|
| UDM Pro | 10.0.1.1 | Gateway + Controller |

**VLANs:**
| VLAN | Subnet | Purpose |
|------|--------|---------|
| - | 10.0.1.0/24 | Default (SCPI, servers) |
| 10 | 10.0.10.0/24 | Management |
| 20 | 10.0.20.0/24 | Media |
| 30 | 10.0.30.0/24 | IoT |
| 50 | 10.0.50.0/24 | Lab |

---

## Security Notes

1. **Never commit credentials** - `.mcp.json` is gitignored
2. **Network access** - Only works when on 10.0.1.x network

---

## Troubleshooting

### Connection Failed
- Verify 10.0.1.1 is accessible: `ping 10.0.1.1`
- Check credentials are correct
- UDM Pro uses port 443 (not 8443 like CloudKey)

### MCP Not Loading
- Restart Claude Code completely
- Check Node.js: `node --version`
- Check npx: `npx --version`

---

*Updated: 2025-12-28 - Migrated from CloudKey to UDM Pro*
*Related: GitHub Issue #17*
