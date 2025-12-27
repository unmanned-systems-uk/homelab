# UniFi MCP Server Setup

## Overview

This document describes how to configure the UniFi Network MCP server for Claude Code and Claude Desktop.

**MCP Server:** `@sirkirby/unifi-network-mcp`
**Controller:** 10.0.1.2:8443 (UniFi Controller v7.2.97)

---

## Linux (Claude Code)

**Config Location:** `/home/anthony/ccpm-workspace/HomeLab/.mcp.json`

```json
{
  "mcpServers": {
    "unifi": {
      "command": "npx",
      "args": ["-y", "@sirkirby/unifi-network-mcp"],
      "env": {
        "UNIFI_HOST": "https://10.0.1.2:8443",
        "UNIFI_USERNAME": "<username>",
        "UNIFI_PASSWORD": "<password>",
        "UNIFI_SITE": "default"
      }
    }
  }
}
```

**Note:** The actual `.mcp.json` file is gitignored for security.

---

## Windows (Claude Desktop)

**Config Location:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the UniFi server to your existing config:

```json
{
  "mcpServers": {
    "unifi": {
      "command": "npx",
      "args": ["-y", "@sirkirby/unifi-network-mcp"],
      "env": {
        "UNIFI_HOST": "https://10.0.1.2:8443",
        "UNIFI_USERNAME": "<username>",
        "UNIFI_PASSWORD": "<password>",
        "UNIFI_SITE": "default"
      }
    }
  }
}
```

### Windows Prerequisites

1. **Node.js** must be installed: https://nodejs.org/
2. **npx** must be in PATH (comes with Node.js)
3. Network access to 10.0.1.2:8443 from Windows PC

---

## Verification

After configuration, restart Claude Code/Desktop and verify MCP tools are available:

- `unifi_list_devices` - List all UniFi devices
- `unifi_get_clients` - Get connected clients
- `unifi_get_networks` - Get network configurations

---

## Security Notes

1. **Never commit credentials** - `.mcp.json` is gitignored
2. **Consider dedicated account** - Create read-only UniFi admin for MCP
3. **Network access** - Only works when on 10.0.1.x network

---

## Troubleshooting

### Connection Failed
- Verify 10.0.1.2:8443 is accessible: `curl -sk https://10.0.1.2:8443/status`
- Check credentials are correct
- Ensure UNIFI_SITE is "default" (or your site name)

### MCP Not Loading
- Restart Claude Code/Desktop completely
- Check Node.js is installed: `node --version`
- Check npx is available: `npx --version`

---

*Created: 2024-12-27*
*Related: GitHub Issue #17 - USG to UDM Migration*
