# End of Day Report - 2026-02-04

## Session Overview
- **Duration:** ~9 hours (continued from previous session)
- **Status:** Completed
- **Database Report ID:** 4d807f41-1321-48f1-b381-5e76c476365b

---

## Work Completed

### 1. MCP Server Split Completion

Completed the separation of CCPM tools from HomeLab MCP server:
- Removed ~2,200 lines of CCPM code from `homelab_server.py`
- Server reduced from 2,790 to 571 lines
- HomeLab MCP now exposes only 11 infrastructure tools
- CCPM MCP exposes 34 dedicated CCPM tools

### 2. Cloudflare Tunnel Configuration

Added routes to existing `unifi-mcp` tunnel for all MCP servers:
| Subdomain | Service | Port |
|-----------|---------|------|
| mcp.unmanned-systems.uk | UniFi MCP | 3001 |
| homelab-mcp.unmanned-systems.uk | HomeLab MCP | 8080 |
| ccpm-mcp.unmanned-systems.uk | CCPM MCP | 9000 |
| github-mcp.unmanned-systems.uk | GitHub MCP | 8082 |

### 3. HomeLab MCP Deployment Fix

Discovered V2-Infrastructure had overwritten `~/mcp-server/` with CCPM code. Fixed by:
- Created separate `~/homelab-mcp/` directory on Harbor VM
- Created correct Dockerfile copying `homelab_server.py`
- Rebuilt and redeployed container
- Verified server shows "HomeLab MCP Server (Infrastructure Only)"

### 4. VM 105 RAM Crisis Resolution

NEX-CAM-DEV (10.0.1.130) locked up during build with RAM maxed (7.38/8GB):
- Freed RAM by reducing VM 100 (whisper-tts) from 16GB to 8GB
- Waited for OOM killer - VM recovered
- Shut down VM 105 and increased RAM to 12GB
- Restarted successfully

### 5. MCP Transport Configuration

Fixed `.mcp.json` configuration:
- ccpm-mcp uses **HTTP transport** with `/mcp` endpoint (not SSE)
- Other servers use SSE transport with `/sse` endpoint

```json
{
  "mcpServers": {
    "homelab": {"type": "sse", "url": "http://10.0.1.202:8080/sse"},
    "ccpm": {"type": "http", "url": "http://10.0.1.202:9000/mcp"},
    "unifi": {"type": "sse", "url": "https://mcp.unmanned-systems.uk/sse"},
    "homeassistant": {"type": "http", "url": "http://10.0.1.150:8123/api/mcp"}
  }
}
```

---

## Infrastructure Status

| Component | Status |
|-----------|--------|
| UDM Pro (10.0.1.1) | Online |
| Proxmox (10.0.1.200) | Online |
| NAS (10.0.1.251) | Online |
| Harbor VM (10.0.1.202) | Online |

### MCP Servers

| Server | Port | Transport | Status |
|--------|------|-----------|--------|
| homelab-mcp | 8080 | SSE | Online |
| ccpm-mcp | 9000 | HTTP | Online |
| github-mcp | 8082 | SSE | Online |
| unifi-mcp | 3001 | SSE | Online |

---

## Files Modified

- `mcp-servers/homelab-infra/homelab_server.py` - Removed CCPM tools
- `.mcp.json` - Fixed ccpm transport configuration
- `.claude/skills/cloudflare/SKILL.md` - Added new tunnel routes

---

## Commits

| Hash | Message |
|------|---------|
| 806b15a | refactor(mcp): Split CCPM tools out of HomeLab MCP server |

---

## Learnings

### MCP Transport Types
- **SSE (Server-Sent Events):** Uses `/sse` endpoint, persistent connection
- **HTTP (Streamable):** Uses `/mcp` endpoint, request/response based
- FastMCP servers can use either transport via `mcp.run(transport="sse")` or `mcp.run(transport="http")`

### Container Deployment
- Always verify Dockerfile is copying the correct source file
- Container logs are essential for verifying correct server is running
- Use separate directories for different services to avoid confusion

---

## Handoff Notes for Next Session

1. All 4 MCP servers are operational and tested
2. MCP split is complete - infrastructure tools in homelab-mcp, CCPM tools in ccpm-mcp
3. Cloudflare tunnels configured for external access
4. VM 105 now has 12GB RAM - monitor for future builds

---

*HomeLab Agent - End of Day Report*
*Database: ccpm_db @ 10.0.1.251:5433*
*Generated: 2026-02-04*
