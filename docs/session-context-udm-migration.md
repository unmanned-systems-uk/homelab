# Session Context: USG to UDM Migration

**Created:** 2024-12-27
**Updated:** 2025-12-27 22:45 UTC
**GitHub Issue:** [#17 - Setup UniFi MCP Server for Network Visibility](https://github.com/unmanned-systems-uk/homelab/issues/17)
**Status:** MCP OPERATIONAL (Claude Code only - Desktop not supported)

---

## Quick Resume Instructions

```bash
# MCP is already working in Claude Code CLI
# Test with:
unifi_tool_index

# If MCP not responding, restart the container:
ssh root@10.0.1.200 "pct exec 300 -- systemctl restart cloudflared && docker restart unifi-mcp"
```

---

## IMPORTANT: Claude Desktop Limitation

**Claude Desktop CANNOT connect to this MCP server.**

Reason: Claude Desktop requires OAuth authentication for remote MCP servers. The `sirkirby/unifi-network-mcp` server does not support OAuth.

| Client | Status | URL |
|--------|--------|-----|
| **Claude Code (CLI)** | ✅ WORKS | `http://10.0.1.159:8080/sse` |
| **Claude Desktop** | ❌ NOT SUPPORTED | OAuth required |

**Workaround:** Use Claude Code CLI for all UniFi network operations.

---

## Task Completion Status

### Completed ✅
- [x] Identified CloudKey at 10.0.1.2:8443 (UniFi Controller v7.2.97)
- [x] Tested UniFi Controller API connectivity
- [x] Ran comprehensive network audit (14 devices, 54 clients, 213 static IPs)
- [x] Generated `docs/current-network-state.md` with full inventory
- [x] Deployed UniFi MCP server on Proxmox LXC 300 (10.0.1.159)
- [x] Configured nginx reverse proxy (port 8080)
- [x] Set up HTTPS with self-signed cert (port 8443)
- [x] Created Cloudflare Tunnel with valid SSL
- [x] Registered domain `unmanned-systems.uk` on Cloudflare
- [x] Created subdomain `mcp.unmanned-systems.uk`
- [x] Configured cloudflared as systemd service (auto-starts)
- [x] Verified MCP works in Claude Code (81 tools available)
- [x] Network health check performed successfully
- [x] Updated GitHub Issue #17 with full documentation

### Not Possible ❌
- [ ] ~~Claude Desktop MCP access~~ - Requires OAuth (not supported by this MCP server)

### Pending (Migration Tasks)
- [ ] Create static DHCP reservation for MCP container (10.0.1.159)
- [ ] Choose UDM model (UDM-SE recommended)
- [ ] Export controller backup from CloudKey
- [ ] Schedule migration window
- [ ] Execute migration

---

## MCP Server Architecture

```
Claude Code → http://10.0.1.159:8080/sse
    ↓
Nginx (port 8080) → rewrites Host header to "localhost"
    ↓
Docker (port 3000) → ghcr.io/sirkirby/unifi-network-mcp:latest
    ↓
CloudKey API (10.0.1.2:8443) → UniFi Controller v7.2.97
```

### Cloudflare Tunnel (for external access)

```
External → https://mcp.unmanned-systems.uk/sse
    ↓
Cloudflare Edge (valid SSL)
    ↓
Cloudflare Tunnel (ID: 3d770e65-6f08-4421-aea4-9540df951eca)
    ↓
LXC 300 → nginx:8080 → Docker:3000 → CloudKey
```

---

## Infrastructure Details

| Component | Value |
|-----------|-------|
| **Proxmox Host** | pve-ai (10.0.1.200) |
| **Container ID** | LXC 300 |
| **Container Name** | unifi-mcp |
| **Container IP** | 10.0.1.159 (DHCP - needs static reservation) |
| **Container Password** | `MCPserver2350` |
| **Docker Image** | `ghcr.io/sirkirby/unifi-network-mcp:latest` |
| **Docker Port** | 3000 (internal) |
| **Nginx HTTP** | 8080 (Claude Code) |
| **Nginx HTTPS** | 8443 (self-signed) |
| **Cloudflare Tunnel** | `https://mcp.unmanned-systems.uk/sse` |
| **Tunnel ID** | 3d770e65-6f08-4421-aea4-9540df951eca |
| **Domain** | unmanned-systems.uk (Cloudflare DNS) |
| **Tools Available** | 81 UniFi network tools |

---

## Container Environment Variables

```bash
UNIFI_HOST=10.0.1.2
UNIFI_USERNAME=Anthony
UNIFI_PASSWORD=ABDAdman2350@!
UNIFI_PORT=8443
UNIFI_SITE=default
UNIFI_VERIFY_SSL=false
UNIFI_CONTROLLER_TYPE=direct
UNIFI_MCP_HTTP_ENABLED=true
UNIFI_MCP_HTTP_FORCE=true
```

---

## Claude Code Configuration

File: `/home/anthony/ccpm-workspace/HomeLab/.mcp.json`

```json
{
  "mcpServers": {
    "unifi": {
      "type": "sse",
      "url": "http://10.0.1.159:8080/sse"
    }
  }
}
```

---

## Available MCP Tools (81 total)

### Meta-Tools
| Tool | Purpose |
|------|---------|
| `unifi_tool_index` | List all 81 available UniFi tools |
| `unifi_execute` | Run any tool by name |
| `unifi_batch` | Run multiple tools in parallel |
| `unifi_batch_status` | Check batch operation status |

### Tool Categories
| Category | Examples |
|----------|----------|
| **Clients** | list_clients, get_client_details, block_client, rename_client |
| **Devices** | list_devices, get_device_details, reboot_device, upgrade_device |
| **Networks** | list_networks, create_network, update_network |
| **Firewall** | list_firewall_policies, create_firewall_policy, toggle_firewall_policy |
| **VPN** | list_vpn_clients, list_vpn_servers, update_vpn_client_state |
| **QoS** | list_qos_rules, create_qos_rule, toggle_qos_rule_enabled |
| **Routing** | list_routes, create_route, list_traffic_routes |
| **Port Forwards** | list_port_forwards, create_port_forward, toggle_port_forward |
| **WLANs** | list_wlans, create_wlan, update_wlan |
| **Stats** | get_network_health, get_network_stats, get_top_clients, get_dpi_stats |
| **Alarms/Events** | list_alarms, list_events, archive_alarm |
| **Guests** | authorize_guest, create_voucher, list_vouchers |

---

## Container Management Commands

```bash
# Check all services
ssh root@10.0.1.200 "pct exec 300 -- bash -c 'systemctl status cloudflared | head -3; docker ps --format \"{{.Names}} {{.Status}}\"'"

# Restart everything
ssh root@10.0.1.200 "pct exec 300 -- bash -c 'systemctl restart cloudflared; systemctl restart nginx; docker restart unifi-mcp'"

# View MCP logs
ssh root@10.0.1.200 "pct exec 300 -- docker logs --tail 30 unifi-mcp"

# View tunnel logs
ssh root@10.0.1.200 "pct exec 300 -- journalctl -u cloudflared -n 20"

# Enter container
ssh root@10.0.1.200 "pct enter 300"

# Test SSE endpoint
curl -s -m 3 http://10.0.1.159:8080/sse
```

---

## Network Infrastructure Summary

### Core Devices

| Device | Model | IP | Purpose |
|--------|-------|-----|---------|
| **USG Pro 4** | UGW4 | 192.168.0.6 | Gateway (MIGRATION TARGET) |
| **CloudKey** | UCK-G2 | 10.0.1.2:8443 | Controller v7.2.97 |
| **MCP Server** | LXC 300 | 10.0.1.159 | UniFi MCP |

### Network Statistics (from health check)

| Subsystem | Status | Details |
|-----------|--------|---------|
| **WAN** | ✅ OK | IP: 192.168.0.6, Latency: 15ms |
| **WWW** | ✅ OK | ↓352 Mbps / ↑56 Mbps |
| **WLAN** | ⚠️ Warning | 1 AP disconnected (7 online) |
| **LAN** | ⚠️ Warning | 1 switch disconnected (4 online) |
| **VPN** | ❌ Error | Site-to-site inactive (DEPRECATED - not needed) |

### Gateway Stats (USG Pro 4)

| Metric | Value |
|--------|-------|
| Firmware | 4.4.57 |
| Uptime | 18 days |
| CPU | 8% |
| Memory | 26% |
| CPU Temp | 60°C |

### Client Summary

| Type | Count |
|------|-------|
| Total Clients | 55 |
| WiFi Users | 36 |
| WiFi Guests | 1 |
| LAN Users | 18 |

---

## Credentials Reference

### UniFi Controller (CloudKey)

| Field | Value |
|-------|-------|
| URL | https://10.0.1.2:8443 |
| Username | Anthony |
| Password | ABDAdman2350@! |
| Site | default |

### Proxmox Host

| Field | Value |
|-------|-------|
| Host | 10.0.1.200 |
| User | root |
| Password | PROXAdman2350 |

### MCP Container (LXC 300)

| Field | Value |
|-------|-------|
| IP | 10.0.1.159 |
| User | root |
| Password | MCPserver2350 |

### Cloudflare

| Field | Value |
|-------|-------|
| Account | sunnybrae2024@gmail.com |
| Domain | unmanned-systems.uk |
| Tunnel | unifi-mcp |

---

## Migration Considerations

### DEPRECATED - No Longer Required
- ~~Site-to-Site VPN to Selkirk~~ - **NOT NEEDED**

### Still Required for UDM Migration
1. **4G Failover:** WAN2 failover configuration
2. **IPS Rules:** 16 auto-generated firewall rules
3. **Static IPs:** 213 DHCP reservations
4. **Port Forward:** Gaming server on 10.0.1.40 (port 27015)
5. **WiFi Configs:** 4 SSIDs with passwords

### UDM Model Recommendation
**UDM-SE** for dual WAN, built-in PoE+, integrated controller

---

## Fallback Scripts (if MCP unavailable)

```bash
# Test API connectivity
bash scripts/test-unifi-api.sh

# Run full network audit
bash scripts/unifi-network-audit.sh
```

---

## Session History

| Date | Action |
|------|--------|
| 2024-12-27 | Initial context created |
| 2025-12-27 18:00 | Network audit via direct API |
| 2025-12-27 19:00 | MCP deployed on Proxmox LXC 300 |
| 2025-12-27 20:00 | Nginx proxy configured, HTTPS added |
| 2025-12-27 21:45 | Cloudflare Tunnel created |
| 2025-12-27 22:00 | Domain unmanned-systems.uk on Cloudflare |
| 2025-12-27 22:10 | mcp.unmanned-systems.uk subdomain created |
| 2025-12-27 22:30 | Discovered Claude Desktop requires OAuth |
| 2025-12-27 22:45 | Confirmed MCP works in Claude Code only |

---

*Resume: Read this file at start of session*
*GitHub Issue: https://github.com/unmanned-systems-uk/homelab/issues/17*
