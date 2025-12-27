# Session Context: USG to UDM Migration

**Created:** 2024-12-27
**Updated:** 2025-12-27 18:20 UTC
**GitHub Issue:** [#17 - Setup UniFi MCP Server for Network Visibility](https://github.com/unmanned-systems-uk/homelab/issues/17)
**Status:** MCP DEPLOYED - REQUIRES CLAUDE CODE RESTART

---

## Quick Resume Instructions

After restarting Claude Code:

```
1. MCP server should auto-load from .mcp.json
2. Test: Use unifi_tool_index to list available tools
3. If MCP not working, check container: ssh root@10.0.1.200 "pct exec 300 -- docker logs unifi-mcp"
```

---

## Task Completion Status

### Completed
- [x] Identified CloudKey at 10.0.1.2:8443 (UniFi Controller v7.2.97)
- [x] Tested UniFi Controller API connectivity
- [x] Ran comprehensive network audit (14 devices, 54 clients, 213 static IPs)
- [x] Generated `docs/current-network-state.md` with full inventory
- [x] Deployed UniFi MCP server on Proxmox LXC container
- [x] Configured `.mcp.json` for Claude Code integration
- [x] Updated GitHub Issue #17 with progress

### Pending (After Restart)
- [ ] Restart Claude Code to load MCP server
- [ ] Verify MCP tools available (81 tools expected)
- [ ] Test real-time network queries via MCP
- [ ] Create static DHCP reservation for MCP container (10.0.1.159)

### Migration Tasks (Future)
- [ ] Choose UDM model (UDM-SE recommended)
- [ ] Export controller backup from CloudKey
- [ ] Schedule migration window
- [ ] Execute migration

---

## MCP Server Configuration

### Deployed Infrastructure

| Component | Value |
|-----------|-------|
| **Proxmox Host** | pve-ai (10.0.1.200) |
| **Container ID** | LXC 300 |
| **Container Name** | unifi-mcp |
| **Container IP** | 10.0.1.159 (DHCP - needs static reservation) |
| **Container Password** | `MCPserver2350` |
| **Docker Image** | `ghcr.io/sirkirby/unifi-network-mcp:latest` |
| **Docker Port** | 3000 (internal) |
| **Nginx HTTP Port** | 8080 (Claude Code CLI) |
| **Nginx HTTPS Port** | 8443 (self-signed, local only) |
| **Cloudflare Tunnel** | `https://mcp.unmanned-systems.uk/sse` |
| **Tunnel ID** | 3d770e65-6f08-4421-aea4-9540df951eca |
| **HTTP Endpoint** | `http://10.0.1.159:8080/sse` (local) |
| **HTTPS Endpoint** | `https://mcp.unmanned-systems.uk/sse` (recommended) |
| **Tools Available** | 81 UniFi network tools |

### Container Environment Variables

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

### Claude Code Configuration (HTTP)

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

### Claude Desktop Configuration (Cloudflare Tunnel)

Claude Desktop requires HTTPS with a valid certificate. Use the Cloudflare Tunnel URL:

```
https://mcp.unmanned-systems.uk/sse
```

| Field | Value |
|-------|-------|
| **Name** | `unifi` |
| **Remote MCP server URL** | `https://mcp.unmanned-systems.uk/sse` |
| **OAuth Client ID** | *leave blank* |
| **OAuth Client Secret** | *leave blank* |

**Note:** Valid SSL certificate provided by Cloudflare. Works from anywhere.

### Nginx Proxy Configuration

An nginx reverse proxy is required because the MCP Python library validates the Host header.
- **Port 8080 (HTTP):** For Claude Code CLI
- **Port 8443 (HTTPS):** For Claude Desktop (self-signed SSL cert)

Config file: `/etc/nginx/sites-available/mcp-proxy`

```bash
# Restart nginx proxy
ssh root@10.0.1.200 "pct exec 300 -- systemctl restart nginx"

# Check nginx status
ssh root@10.0.1.200 "pct exec 300 -- systemctl status nginx"
```

### Container Management Commands

```bash
# Check MCP server status
ssh root@10.0.1.200 "pct exec 300 -- docker logs --tail 30 unifi-mcp"

# Restart MCP container
ssh root@10.0.1.200 "pct exec 300 -- docker restart unifi-mcp"

# Stop/Start LXC container
ssh root@10.0.1.200 "pct stop 300"
ssh root@10.0.1.200 "pct start 300"

# Enter container shell
ssh root@10.0.1.200 "pct enter 300"

# Check Docker status inside container
ssh root@10.0.1.200 "pct exec 300 -- docker ps"
```

### MCP Tools Available

After Claude Code restart, these meta-tools will be available:

| Tool | Purpose |
|------|---------|
| `unifi_tool_index` | List all 81 available UniFi tools |
| `unifi_execute` | Run any tool by name |
| `unifi_batch` | Run multiple tools in one call |
| `unifi_batch_status` | Check batch operation status |
| `unifi_load_tools` | Dynamically load specific tools |

---

## Network Infrastructure Summary

### Core Devices

| Device | Model | IP | Purpose |
|--------|-------|-----|---------|
| **USG Pro 4** | UGW4 | 192.168.0.6 | Gateway (MIGRATION TARGET) |
| **CloudKey** | UCK-G2 | 10.0.1.2:8443 | Controller v7.2.97 |
| **MCP Server** | LXC 300 | 10.0.1.159 | UniFi MCP (NEW) |

### Network Statistics

| Metric | Value |
|--------|-------|
| UniFi Devices | 14 (12 online, 2 offline) |
| Access Points | 8 (7 online, 1 offline) |
| Switches | 5 (4 online, 1 offline) |
| Connected Clients | 54 |
| Static IP Reservations | 213 |
| WiFi SSIDs | 4 |
| Port Forwards | 1 |
| Firewall Rules | 17 |

### Access Points

| Name | Model | IP | Status |
|------|-------|-----|--------|
| SUN-AC-Office | U7PG2 | 10.0.1.109 | Online |
| Sun-AP-GarFl | U7PG2 | 10.0.1.19 | Online |
| SUN-AP-AK-Bed | U7PG2 | 10.0.1.23 | Online |
| SUN-AP-Chaple | U7PG2 | 10.0.1.29 | Online |
| SUN-AP-Cinema | U7PG2 | 10.0.1.31 | Online |
| SUN-AP-Studio-Bed | U7PG2 | 10.0.1.22 | Online |
| SUN-AP-Studio | U7PG2 | 10.0.1.21 | Online |
| ACP-AP-U6-Lite-HAAS-Hoose | UAL6 | 10.0.1.24 | OFFLINE |

### Switches

| Name | Model | IP | Status |
|------|-------|-----|--------|
| Sunnybrae-Office-SW1-48 | US48 | 10.0.1.78 | Online |
| Sunnybrae-Studio-SW2-24-PoE | US24P250 | 10.0.1.137 | Online |
| Sunnybrae-Cinema-SW3-24-POE | US24P250 | 10.0.1.140 | Online |
| SUN-Office-Dev-Desk | US24 | 10.0.1.193 | Online |
| USW-Flex-5-port-SW-HAAS Hoose | USMINI | 10.0.1.162 | OFFLINE |

### WiFi Configuration

| SSID | Security | Band | Password |
|------|----------|------|----------|
| ACP-Guest | Open | 2.4G + 5G | N/A (Guest) |
| ACP-WiFi | WPA2-PSK | 2.4G | `acpadman` |
| SUNNY-5G | WPA2-PSK | 5G | `acpadman` |
| dev-24g | WPA2-PSK | 2.4G | `dev-24g-2350` |

### Port Forwards

| Name | External Port | Internal IP | Protocol |
|------|---------------|-------------|----------|
| Nathan | 27015 | 10.0.1.40 | TCP/UDP |

### WAN Configuration

| Interface | Type | Speed | Purpose |
|-----------|------|-------|---------|
| WAN1 | DHCP | 900/115 Mbps | Primary |
| WAN2 (4G) | DHCP | Variable | Failover |

---

## Migration Considerations

### DEPRECATED - No Longer Required

- ~~Site-to-Site VPN to Selkirk (213.123.199.105)~~ - **DEPRECATED, NOT NEEDED**

### Still Required

1. **4G Failover:** WAN2 failover configuration must be recreated on UDM
2. **IPS Rules:** 16 auto-generated firewall rules (will migrate with controller backup)
3. **Static IPs:** 213 DHCP reservations to verify post-migration
4. **Port Forward:** Gaming server on 10.0.1.40 (port 27015)
5. **WiFi Configs:** 4 SSIDs with passwords

### UDM Model Recommendation

**UDM-SE** is recommended for:
- Dual WAN support (primary + 4G failover)
- Built-in PoE+ ports
- Integrated controller (replaces CloudKey)
- Enhanced IPS/IDS performance
- 2.5GbE WAN port

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

---

## Raw Data Files

All network audit exports are stored in:

```
/home/anthony/ccpm-workspace/HomeLab/audit-data/
├── devices.json         # UniFi hardware (357 KB)
├── clients.json         # Connected clients (72 KB)
├── networks.json        # Network/VLAN config (4 KB)
├── firewall-rules.json  # Firewall rules (11 KB)
├── port-forwards.json   # Port forwarding (252 B)
├── wlan-configs.json    # WiFi SSIDs (6 KB)
├── site-settings.json   # Site configuration (13 KB)
├── static-clients.json  # DHCP reservations (69 KB)
├── system-info.json     # Controller info (2 KB)
└── health.json          # Health status (2 KB)
```

---

## Fallback Scripts

If MCP is unavailable, use direct API scripts:

```bash
# Test API connectivity
bash scripts/test-unifi-api.sh

# Run full network audit
bash scripts/unifi-network-audit.sh
```

---

## Related Documentation

| File | Purpose |
|------|---------|
| `docs/current-network-state.md` | Complete network audit with all details |
| `docs/unifi-mcp-setup.md` | MCP setup instructions (Windows included) |
| `.mcp.json` | MCP server configuration (gitignored) |
| `audit-data/*.json` | Raw API exports |

---

## Troubleshooting

### MCP Server Not Responding

```bash
# 1. Check if container is running
ssh root@10.0.1.200 "pct status 300"

# 2. Check Docker container
ssh root@10.0.1.200 "pct exec 300 -- docker ps"

# 3. Check logs for errors
ssh root@10.0.1.200 "pct exec 300 -- docker logs --tail 50 unifi-mcp"

# 4. Restart Docker container
ssh root@10.0.1.200 "pct exec 300 -- docker restart unifi-mcp"

# 5. Test SSE endpoint directly
curl -H "Host: localhost" http://10.0.1.159:3000/sse
```

### MCP Not Loading in Claude Code

1. Verify `.mcp.json` exists in project root
2. Restart Claude Code completely (not just new session)
3. Check for approval prompt for new MCP server
4. Verify network connectivity to 10.0.1.159:3000

---

## Session History

| Date | Action |
|------|--------|
| 2024-12-27 | Initial context created, CloudKey identified |
| 2025-12-27 | Network audit completed via direct API |
| 2025-12-27 | MCP server deployed on Proxmox LXC 300 |
| 2025-12-27 | .mcp.json configured, awaiting restart |

---

*Resume command: `cat docs/session-context-udm-migration.md`*
*GitHub Issue: https://github.com/unmanned-systems-uk/homelab/issues/17*
