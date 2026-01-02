# Home Assistant Configuration

**Last Updated:** 2026-01-02
**Device:** HA-Pi5 (Raspberry Pi 5)
**OS:** HAOS 16.3

---

## Connection Details

| Property | Value |
|----------|-------|
| **Internal IP** | 10.0.1.150 |
| **Web Port** | 8123 |
| **SSH Port** | 22222 |
| **External URL** | https://ha.unmanned-systems.uk |
| **MCP Endpoint** | https://ha.unmanned-systems.uk/api/mcp |

---

## SSH Access

| Property | Value |
|----------|-------|
| **Host** | 10.0.1.150 |
| **Port** | 22222 |
| **Addon** | Terminal & SSH |
| **Key Path** | `/home/homelab/.ssh/ha_access` |

```bash
# SSH to HA
ssh -p 22222 -i ~/.ssh/ha_access root@10.0.1.150
```

---

## Installed Components

### HACS (Home Assistant Community Store)
- **Status:** Installed
- **Purpose:** Community integrations and frontend cards

### Frontend Cards (via HACS)
| Card | Purpose |
|------|---------|
| ApexCharts Card | Advanced charting for energy dashboard |

### Integrations
| Integration | Status | Details |
|-------------|--------|---------|
| Emporia Vue | Active | Energy monitoring |

---

## Emporia Vue - Monitored Circuits

| Circuit | Description |
|---------|-------------|
| Main Supply | 3-phase main supply |
| Studio | Studio power |
| Chaple L1 | Chapel Line 1 |
| Chaple L2 | Chapel Line 2 |
| Chaple L3 | Chapel Line 3 |
| Cinema | Cinema room |
| Garden Flat | Garden flat power |
| Laundry | Laundry room |
| Main House Upper | Main house upper floor |
| Main House Lower | Main house lower floor |
| Balance | Calculated balance |

**Total Circuits:** 11

---

## MCP Integration

### Claude Code Configuration
File: `/home/homelab/homeassistant/.mcp.json`

```json
{
  "mcpServers": {
    "homeassistant": {
      "type": "http",
      "url": "http://10.0.1.150:8123/api/mcp",
      "headers": {
        "Authorization": "Bearer <TOKEN>"
      }
    }
  }
}
```

### Claude Desktop Configuration
Requires `mcp-proxy` for stdio transport.

File: `C:\Users\antho\AppData\Roaming\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "Home Assistant": {
      "command": "mcp-proxy",
      "args": [
        "--transport=streamablehttp",
        "--stateless",
        "https://ha.unmanned-systems.uk/api/mcp"
      ],
      "env": {
        "API_ACCESS_TOKEN": "<TOKEN>"
      }
    }
  }
}
```

---

## Cloudflare Tunnel

| Property | Value |
|----------|-------|
| **Tunnel Name** | unifi-mcp |
| **Public Hostname** | ha.unmanned-systems.uk |
| **Origin** | http://10.0.1.150:8123 |
| **Status** | Healthy |

---

## Related Documentation

- GitHub Issue #11: HomeLab Infrastructure MCP Server
- `/home/homelab/homeassistant/` - HA Agent repository

---

*HomeLab - Home Assistant Configuration Reference*
