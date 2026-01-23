# MCP Server Development Skill

**Owner:** HomeLab Agent
**Version:** 1.0
**Created:** 2026-01-23

---

## Overview

This skill covers development and maintenance of the HomeLab MCP (Model Context Protocol) server, which provides infrastructure tools to Claude Code agents across the CCPM ecosystem.

---

## MCP Server Architecture

### Server Details

| Property | Value |
|----------|-------|
| Server Name | homelab-mcp |
| Framework | FastMCP 2.0+ |
| Transport | SSE (Server-Sent Events) |
| Container | `homelab-mcp` on Harbor VM |
| Host | 10.0.1.202 |
| Port | 8080 |
| Endpoint | `http://10.0.1.202:8080/sse` |
| Source Code | `mcp-servers/homelab-infra/homelab_server.py` |

### Environment Variables

```bash
HOMELAB_DB_HOST=10.0.1.251
HOMELAB_DB_PORT=5433
HOMELAB_DB_NAME=homelab_db
HOMELAB_DB_USER=ccpm
HOMELAB_DB_PASSWORD=CcpmDb2025Secure
CCPM_AGENT_ID=aaaaaaaa-bbbb-cccc-dddd-222222222222
```

### API Base URLs (in server code)

```python
CCPM_TASK_API = "http://10.0.1.210:8000/api/v1"      # Tasks, Sprints
CCPM_MESSAGING_API = "http://10.0.1.210:8000/api/v1" # Agent Messages
```

---

## Tool Categories

### 1. HomeLab Infrastructure (12 tools)

| Tool | Description |
|------|-------------|
| `homelab_list_devices` | List all devices with optional filters |
| `homelab_get_device` | Get device details by name or IP |
| `homelab_list_scpi_equipment` | List SCPI test equipment |
| `homelab_get_scpi_connection` | Get SCPI connection details |
| `homelab_list_services` | List running services |
| `homelab_check_service_health` | HTTP health check for services |
| `homelab_list_networks` | List VLANs and subnets |
| `homelab_list_firewall_rules` | List firewall rules |
| `homelab_lookup_ip` | Lookup IP allocation |
| `homelab_get_credentials` | Get credentials (audit logged) |
| `homelab_infrastructure_summary` | Get infrastructure overview |
| `homelab_list_vms` | List Proxmox VMs |

### 2. CCPM Agent Tools (8 tools)

| Tool | Description |
|------|-------------|
| `ccpm_list_agents` | List registered agents |
| `ccpm_send_message` | Send message to agent/user |
| `ccpm_check_inbox` | Check agent inbox |
| `ccpm_mark_message_complete` | Complete a message with response |

### 3. CCPM Task Tools (6 tools)

| Tool | Description |
|------|-------------|
| `ccpm_get_task` | Get task by ID |
| `ccpm_list_tasks` | List tasks with filters |
| `ccpm_update_task_status` | Update task status |
| `ccpm_submit_completion_report` | Submit task completion report |
| `ccpm_get_task_instructions` | Get task instructions |
| `ccpm_add_custom_instruction` | Add custom instruction to task |

### 4. CCPM Sprint Tools (2 tools)

| Tool | Description |
|------|-------------|
| `ccpm_get_active_sprint` | Get current active sprint |
| `ccpm_list_sprints` | List all sprints |

### 5. Session Management (4 tools)

| Tool | Description |
|------|-------------|
| `ccpm_create_session` | Create session report |
| `ccpm_log_session_context` | Log context item |
| `ccpm_complete_session` | Complete session with summary |
| `ccpm_get_resume_context` | Get last session context |

### 6. Completion Signaling (1 tool)

| Tool | Description |
|------|-------------|
| `ccpm_signal_completion` | Signal task completion to V2-Master |

---

## Adding New Tools

### Standard Tool Template

```python
@mcp.tool()
def tool_name(
    required_param: str,
    optional_param: str = None
) -> dict:
    """
    Brief description of what the tool does.

    Args:
        required_param: Description of parameter
        optional_param: Description (default: None)

    Returns:
        Description of return value
    """
    try:
        # Implementation
        response = httpx.get(f"{API_BASE}/endpoint", timeout=10.0)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }
```

### Best Practices

1. **Always use `httpx` for HTTP calls** - async-compatible
2. **Set timeout** - Default 10.0 seconds
3. **Handle HTTPStatusError** - Specific error for API failures
4. **Handle generic Exception** - Catch-all for unexpected errors
5. **Return consistent structure** - Always include `success` field
6. **Use descriptive docstrings** - Args and Returns documented
7. **Validate inputs** - Check parameters before API calls

---

## Deployment Process

### 1. Update Server Code

Edit `mcp-servers/homelab-infra/homelab_server.py`

### 2. Copy to Harbor VM

```bash
sshpass -p "053210" scp /home/homelab/HomeLab/mcp-servers/homelab-infra/homelab_server.py \
  ccpm@10.0.1.202:~/mcp-server/homelab_server.py
```

### 3. Rebuild Docker Image

```bash
sshpass -p "053210" ssh ccpm@10.0.1.202 \
  "cd ~/mcp-server && docker build -t homelab-infra:latest ."
```

### 4. Restart Container

```bash
sshpass -p "053210" ssh ccpm@10.0.1.202 \
  "docker stop homelab-mcp && docker rm homelab-mcp && \
   docker run -d --name homelab-mcp -p 8080:8080 --restart unless-stopped \
   -e HOMELAB_DB_HOST=10.0.1.251 \
   -e HOMELAB_DB_PORT=5433 \
   -e HOMELAB_DB_NAME=homelab_db \
   -e HOMELAB_DB_USER=ccpm \
   -e HOMELAB_DB_PASSWORD=CcpmDb2025Secure \
   -e CCPM_AGENT_ID=aaaaaaaa-bbbb-cccc-dddd-222222222222 \
   homelab-infra:latest"
```

### 5. Verify Deployment

```bash
# Check container running
sshpass -p "053210" ssh ccpm@10.0.1.202 "docker ps | grep homelab-mcp"

# Check tool count
sshpass -p "053210" ssh ccpm@10.0.1.202 \
  "docker exec homelab-mcp grep -c '@mcp.tool' /app/homelab_server.py"

# Check logs
sshpass -p "053210" ssh ccpm@10.0.1.202 "docker logs homelab-mcp --tail 20"
```

### 6. MCP Client Reconnect

After deployment, MCP clients cache tool schemas. Clients must reconnect to see new tools.

---

## Database Integration

### HomeLab Database (homelab_db)

```python
# Connection in server
db_config = {
    "host": os.getenv("HOMELAB_DB_HOST", "10.0.1.251"),
    "port": int(os.getenv("HOMELAB_DB_PORT", "5433")),
    "database": os.getenv("HOMELAB_DB_NAME", "homelab_db"),
    "user": os.getenv("HOMELAB_DB_USER", "ccpm"),
    "password": os.getenv("HOMELAB_DB_PASSWORD"),
}
```

### Schemas Available

| Schema | Purpose |
|--------|---------|
| `infrastructure` | Devices, services |
| `credentials` | System credentials |
| `network` | IP allocations, VLANs |
| `virtualization` | Proxmox VMs |
| `scpi` | Test equipment |
| `ai_ml` | Ollama models |
| `audit` | Event logging |

---

## Testing Tools

### Direct API Test

```bash
# Test underlying API before MCP tool
curl -s "http://10.0.1.210:8000/api/v1/endpoint" | python3 -m json.tool
```

### MCP Tool Test (via Claude Code)

```
mcp__homelab__tool_name(param="value")
```

### Verify Tool Exists

```bash
# Count tools in running container
sshpass -p "053210" ssh ccpm@10.0.1.202 \
  "docker exec homelab-mcp grep -c '@mcp.tool' /app/homelab_server.py"
```

---

## Troubleshooting

### Tool Returns Error

1. Test underlying API directly with curl
2. Check API endpoint path (include `/api/v1`)
3. Verify parameters match API schema
4. Check container logs for Python errors

### MCP Client Can't See New Tools

1. Verify container has new code: `docker exec homelab-mcp grep 'tool_name' /app/homelab_server.py`
2. Reconnect MCP client (tools are cached)
3. Check server startup logs for registration errors

### Container Won't Start

1. Check Docker logs: `docker logs homelab-mcp`
2. Verify environment variables
3. Test database connectivity
4. Check for Python syntax errors

### 404 Errors from API

1. Verify API base URL includes `/api/v1`
2. Check if endpoint exists in OpenAPI spec: `curl http://10.0.1.210:8000/openapi.json`
3. Verify API service is running

---

## Key UUIDs

| Entity | UUID |
|--------|------|
| HomeLab Agent | `aaaaaaaa-bbbb-cccc-dddd-222222222222` |
| V2-Master | `4c714f40-d15c-4f0e-bb34-410f2e7e1806` |
| V2-Director | `f6ff605e-e983-4c24-9038-aa84ac955341` |
| Anthony (Human) | `7563bfda-6e47-4e50-b37a-90ccdc47311a` |
| Broadcast (All) | `ffffffff-ffff-ffff-ffff-ffffffffffff` |

---

## Related Documentation

- MCP Server Structure: `docs/homelab-mcp-server-structure.md`
- Database QRC: `docs/database-qrc.md`
- CCPM API Reference: `~/cc-share/Common/agents/API_REFERENCE.md`

---

*HomeLab MCP Server Development Skill - Maintained by HomeLab Agent*
