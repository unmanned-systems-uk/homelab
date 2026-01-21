# HomeLab MCP Server - Current Structure

**Created:** 2025-12-15
**Updated:** 2026-01-21 (CCPM Integration v2 - Session API Fix)
**Status:** Production (running on Harbor VM)
**Purpose:** Documentation of existing MCP server for evaluation and extension

---

## Overview

**Container:** `homelab-mcp` (homelab-infra:latest)
**Location:** Harbor VM (10.0.1.202)
**Transport:** SSE (Server-Sent Events)
**Endpoint:** http://10.0.1.202:8080/sse
**Runtime User:** mcpuser (non-root)

---

## Directory Structure

### Source Code (Dev Machine)

```
~/ccpm-workspace/HomeLab/mcp-servers/homelab-infra/
├── homelab_server.py          # Main MCP server (FastMCP)
├── Dockerfile                 # Container build definition
├── catalog.yaml               # Docker MCP catalog (for Claude Desktop)
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation
├── database.py                # (Purpose unknown - need to check)
└── infrastructure/
    └── db/
        ├── __init__.py       # Package init
        ├── encryption.py     # Fernet credential encryption
        └── models.py         # Database schema/models
```

### Container Runtime Structure

```
/app/                          # Working directory
├── homelab_server.py          # Main server script
├── requirements.txt           # Dependencies list
└── infrastructure/
    └── db/
        ├── __init__.py
        ├── encryption.py
        └── models.py

/data/
└── homelab.db                 # Mounted database (from Harbor host)
```

---

## Current MCP Tools

### 25 Tools Implemented

#### HomeLab Infrastructure Tools (11 tools)

| Tool | Purpose | Security |
|------|---------|----------|
| `homelab_list_devices(category, status, type)` | List all devices in infrastructure | Read-only |
| `homelab_get_device(name, ip)` | Get detailed device information | Read-only |
| `homelab_list_scpi_equipment(type)` | List SCPI test equipment | Read-only |
| `homelab_get_scpi_connection(device)` | Get SCPI connection details | Read-only |
| `homelab_list_services(device, type)` | List services | Read-only |
| `homelab_check_service_health(name)` | HTTP health check | Network call |
| `homelab_list_networks()` | List VLANs and networks | Read-only |
| `homelab_list_firewall_rules()` | List firewall rules | Read-only |
| `homelab_lookup_ip(ip)` | Lookup IP allocation | Read-only |
| `homelab_get_credentials(target)` | Get credentials for device/service | **AUDIT LOGGED** |
| `homelab_infrastructure_summary()` | Get infrastructure summary | Read-only |

#### CCPM Agent Messaging Tools (4 tools)

| Tool | Purpose | Security |
|------|---------|----------|
| `ccpm_list_agents(status, type)` | List all registered CCPM agents | Read-only |
| `ccpm_send_message(to, subject, body, ...)` | Send message to agent (with name resolution) | Agent auth |
| `ccpm_check_inbox(agent_id, include_read)` | Check agent inbox for messages | Agent auth |
| `ccpm_mark_message_complete(msg_id, response)` | Mark message as complete | Agent auth |

#### CCPM Task Management Tools (4 tools)

| Tool | Purpose | Security |
|------|---------|----------|
| `ccpm_get_task(task_id)` | Get task details | Read-only |
| `ccpm_list_tasks(sprint_id, status, assignee)` | List tasks with filters | Read-only |
| `ccpm_update_task_status(id, status, reason)` | Update task status (agent role) | Agent auth |
| `ccpm_submit_completion_report(id, report, by)` | Submit task completion report | Agent auth |

#### CCPM Sprint Management Tools (2 tools)

| Tool | Purpose | Security |
|------|---------|----------|
| `ccpm_get_active_sprint()` | Get current active sprint | Read-only |
| `ccpm_list_sprints(status)` | List sprints with filter | Read-only |

#### CCPM Session Logging Tools (4 tools)

| Tool | Purpose | Security |
|------|---------|----------|
| `ccpm_create_session(agent_id, agent_tag, trigger_type, summary)` | Create session report | Agent auth |
| `ccpm_log_session_context(report_id, context_type, context_key, value)` | Log context item | Agent auth |
| `ccpm_complete_session(report_id, summary, metrics...)` | Complete session with metrics | Agent auth |
| `ccpm_get_resume_context(agent_id)` | Get resume context from last session | Agent auth |

**Note:** Session tools use `/api/v1/session-reports` endpoint (not `/api/sessions`).

---

## Architecture

### Tech Stack

**Framework:** FastMCP 2.0+
**Language:** Python 3.11
**Transport:** SSE (Server-Sent Events over HTTP)
**Database:** PostgreSQL (homelab_db @ 10.0.1.251:5433)
**Encryption:** Fernet (AES-128 via cryptography library)
**HTTP Client:** httpx (for health checks and CCPM API calls)
**External APIs:**
- CCPM Task API: http://10.0.1.210:8000/api
- CCPM Messaging API: http://10.0.1.210:8000/api/v1

### Data Flow

```
Claude Agent
    ↓
MCP Client (Claude Desktop / Open WebUI)
    ↓
SSE Transport (http://10.0.1.202:8080/sse)
    ↓
homelab_server.py (FastMCP)
    ↓
├── PostgreSQL Database (homelab_db) + Encryption Module
├── CCPM Task API (10.0.1.210:8080/api)
└── CCPM Messaging API (10.0.1.210:8000/api/v1)
    ↓
Returns: JSON data to agent
```

### Security Model

**Authentication:** None (relies on network security)
**Authorization:** None (all clients have full access)
**Encryption:** Credentials encrypted at rest (Fernet)
**Audit Logging:** All credential access logged to `audit_log` table
**Sandboxing:** Non-root user (mcpuser), read-only DB mount

---

## Database Schema

### Tables Used by MCP Server

1. **virtual_machines**
   - VM inventory (vm_id, name, ip, status, host_id)

2. **proxmox_hosts**
   - Hypervisor hosts (id, node_name, ip_address)

3. **services**
   - Service registry (service_name, url, port, protocol, health_endpoint, vm_id)

4. **credentials**
   - Encrypted credentials (target_type, target_id, username, password_encrypted, ssh_key_path, auth_type)

5. **network_config**
   - IP allocations (ip_address, hostname, allocated_to, type)

6. **audit_log**
   - Security audit trail (action, target_type, target_id, user, details, ip_address, timestamp)

---

## Dependencies

### requirements.txt

```
fastmcp>=2.0.0          # MCP server framework
cryptography>=41.0.0    # Fernet encryption for credentials
httpx>=0.25.0          # Async HTTP client for health checks and CCPM API
psycopg2-binary>=2.9.0  # PostgreSQL database driver
```

### System Dependencies

- Python 3.11
- Docker (for container runtime)
- SQLite 3 (built into Python)

---

## Deployment Configuration

### Current Docker Deployment (Harbor VM)

```bash
docker run -d \
  --name homelab-mcp \
  --network openwebui-net \
  -p 8080:8080 \
  -e HOMELAB_DB_HOST=10.0.1.251 \
  -e HOMELAB_DB_PORT=5433 \
  -e HOMELAB_DB_NAME=homelab_db \
  -e HOMELAB_DB_USER=ccpm \
  -e HOMELAB_DB_PASSWORD=CcpmDb2025Secure \
  -e CCPM_MESSAGING_API=http://10.0.1.210:8000/api/v1 \
  -e CCPM_TASK_API=http://10.0.1.210:8000/api \
  -e CCPM_AGENT_ID=aaaaaaaa-bbbb-cccc-dddd-222222222222 \
  --restart unless-stopped \
  homelab-infra:latest
```

**Network:**
- Bridge network: `openwebui-net`
- Port mapping: 8080 (host) → 8080 (container)

**Environment Variables:**
- `HOMELAB_DB_HOST` - PostgreSQL host (10.0.1.251)
- `HOMELAB_DB_PORT` - PostgreSQL port (5433)
- `HOMELAB_DB_NAME` - Database name (homelab_db)
- `HOMELAB_DB_USER` - Database user (ccpm)
- `HOMELAB_DB_PASSWORD` - Database password
- `HOMELAB_DB_KEY` (optional, for credential decryption)
- `CCPM_MESSAGING_API` - Messaging API base URL
- `CCPM_TASK_API` - Task API base URL
- `CCPM_AGENT_ID` - Agent UUID for outgoing messages

---

## Key Code Components

### Server Initialization

```python
from fastmcp import FastMCP

mcp = FastMCP("homelab-infra")

# Define tools with @mcp.tool() decorator
@mcp.tool()
def homelab_list_vms(status: str = None) -> list[dict]:
    # Implementation...

# Run SSE server
if __name__ == "__main__":
    mcp.run(transport="sse", port=8080, host="0.0.0.0")
```

### Database Connection

```python
@contextmanager
def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    try:
        yield conn
    finally:
        conn.close()
```

### Credential Decryption

```python
def get_encryption():
    """Get encryption instance if key is available."""
    if not DB_KEY:
        return None
    from infrastructure.db.encryption import CredentialEncryption
    return CredentialEncryption(DB_KEY.encode())
```

### Audit Logging

```python
def log_audit(conn, action, target_type, target_id, user="mcp-agent", details=None):
    """Log security-sensitive actions."""
    conn.execute("""
        INSERT INTO audit_log (action, target_type, target_id, user, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (action, target_type, target_id, user, details, "docker"))
    conn.commit()
```

---

## Open WebUI Integration Compatibility

### Current Status: ✅ Compatible

**Transport:** SSE (Server-Sent Events)
- Open WebUI requires: "MCP (Streamable HTTP)" via SSE ✅
- HomeLab MCP provides: SSE on port 8080 ✅

**Endpoint:** http://10.0.1.202:8080/sse
- Already accessible from Open WebUI container (same network) ✅

**Configuration:**
```
Admin Settings → External Tools → Add MCP Server
- Name: HomeLab Infrastructure
- Type: MCP (Streamable HTTP)
- Server URL: http://homelab-mcp:8000/sse  (internal Docker network)
```

---

## Strengths

1. **Clean Architecture**
   - ✅ Single-file server (homelab_server.py)
   - ✅ Clear separation of concerns (DB, encryption, tools)
   - ✅ Well-documented with docstrings

2. **Security Features**
   - ✅ Encrypted credentials at rest
   - ✅ Audit logging for sensitive operations
   - ✅ Non-root container user
   - ✅ Read-only database mount

3. **FastMCP Framework**
   - ✅ SSE transport (Open WebUI compatible)
   - ✅ Easy to add new tools (@mcp.tool() decorator)
   - ✅ Type hints for tool parameters

4. **Production Ready**
   - ✅ Already deployed and running
   - ✅ 8 working tools
   - ✅ Handles errors gracefully

---

## Limitations / Areas for Extension

### 1. No SSH Capabilities

**Current:** Can query VM details but cannot execute commands
**Needed:** SSH tool for Whisper VM management

**Impact:** Cannot manage Ollama, check GPU, read/write files

### 2. No External API Calls (besides health checks)

**Current:** Only queries local database
**Needed:** Ollama API integration (http://10.0.1.201:11434)

**Impact:** Cannot list/pull/delete Ollama models

### 3. Limited Network Operations

**Current:** HTTP health checks only
**Needed:** More sophisticated service interactions

### 4. Authentication/Authorization

**Current:** No authentication, all clients have full access
**Consideration:** For Open WebUI multi-user, might need user context

### 5. Docker-Only Deployment

**Current:** Designed for Docker Desktop MCP Toolkit
**Needed:** Standalone SSE server deployment (already done on Harbor!)

---

## Extension Plan for Whisper VM Tools

### What Needs to Be Added

**New Dependencies:**
```python
# requirements.txt
fastmcp>=2.0.0
cryptography>=41.0.0
httpx>=0.25.0
asyncssh>=2.14.0        # NEW: SSH client
```

**New Tools (7 additions):**

1. `whisper_ssh_command(command: str)` - Execute shell command
2. `ollama_list_models()` - List Ollama models
3. `ollama_pull_model(model_name: str)` - Pull model
4. `ollama_delete_model(model_name: str)` - Delete model
5. `whisper_gpu_status()` - GPU metrics (nvidia-smi)
6. `whisper_read_file(file_path: str)` - Read file via SFTP
7. `whisper_write_file(file_path, content)` - Write file via SFTP

**Implementation Approach:**
- Add new section in homelab_server.py: "Whisper VM Tools"
- Use asyncssh for SSH/SFTP operations
- Use httpx for Ollama API calls
- Maintain same audit logging pattern

---

## Files Requiring Modification

### To Add Whisper Tools

**1. requirements.txt**
- Add `asyncssh>=2.14.0`

**2. homelab_server.py**
- Import asyncssh
- Add SSH connection helper
- Add 7 new @mcp.tool() functions

**3. Dockerfile**
- Add openssh-client package
- Mount SSH key volume

**4. Deployment command**
- Add SSH key volume mount: `-v ~/.ssh/id_ed25519:/app/.ssh/id_ed25519:ro`

**5. catalog.yaml** (if using Docker Desktop)
- Add new tool definitions

---

## Recommended Structure After Extension

```
homelab-infra/
├── homelab_server.py
│   ├── [Existing] Database Helpers
│   ├── [Existing] VM Tools (8 tools)
│   ├── [Existing] Credential Tools
│   ├── [Existing] Service Tools
│   ├── [Existing] Host Tools
│   ├── [Existing] Network Tools
│   └── [NEW] Whisper VM Tools (7 tools)  ← Add here
├── Dockerfile
│   └── [MODIFIED] Add openssh-client
├── requirements.txt
│   └── [MODIFIED] Add asyncssh
└── infrastructure/db/
    └── (unchanged)
```

**Total Tools After Extension:** 8 existing + 7 new = **15 tools**

---

## Testing Strategy

### Phase 1: Local Testing

```bash
# Build updated image
cd ~/ccpm-workspace/HomeLab/mcp-servers/homelab-infra
docker build -t homelab-infra:whisper .

# Test locally
docker run -it --rm \
  -v ~/ccpm-workspace/HomeLab/infrastructure/homelab.db:/data/homelab.db:ro \
  -v ~/.ssh/id_ed25519:/app/.ssh/id_ed25519:ro \
  -p 8080:8000 \
  homelab-infra:whisper
```

### Phase 2: Deploy to Harbor

```bash
# Save and load image
docker save homelab-infra:whisper | ssh ccpm@10.0.1.202 docker load

# Stop old container
ssh ccpm@10.0.1.202 "docker stop homelab-mcp && docker rm homelab-mcp"

# Deploy new version
ssh ccpm@10.0.1.202 "docker run -d \
  --name homelab-mcp \
  --network openwebui-net \
  -p 8080:8000 \
  -v /home/ccpm/data/homelab.db:/data/homelab.db:ro \
  -v ~/.ssh/id_ed25519:/app/.ssh/id_ed25519:ro \
  homelab-infra:whisper"
```

### Phase 3: Test from Open WebUI

1. Configure MCP server in Admin Settings
2. Test tool discovery
3. Test each new tool from chat

---

## Questions for Evaluation

1. **Should we keep all tools in one file?**
   - Pro: Simple, easy to understand
   - Con: File getting large (currently 380 lines, will be ~600+)
   - Alternative: Split into modules (homelab/vm_tools.py, homelab/whisper_tools.py)

2. **Should we add authentication?**
   - Current: Open to any client on network
   - Consideration: Open WebUI multi-user support
   - Options: JWT tokens, API keys, mTLS

3. **Should we support multiple transports?**
   - Current: SSE only
   - Options: stdio (for Claude Desktop), WebSocket
   - Impact: More complex, more deployment options

4. **Should we split into multiple MCP servers?**
   - Current: One server, all tools
   - Alternative: homelab-infra + homelab-whisper (separate containers)
   - Pro: Clearer separation, independent updates
   - Con: More containers to manage

5. **Error handling improvements?**
   - Current: Basic try/except
   - Enhancement: Structured error responses, retry logic

---

## Current vs Proposed

### Current (Production)

```
HomeLab MCP Server
├── 8 tools (VMs, credentials, services, hosts, network)
├── Transport: SSE
├── Database: SQLite (read-only)
├── Security: Encryption + audit logging
└── Deployment: Single container on Harbor
```

### Proposed (After Whisper Extension)

```
HomeLab MCP Server (Extended)
├── 15 tools total:
│   ├── 8 existing (infrastructure)
│   └── 7 new (Whisper VM management)
├── Transport: SSE (unchanged)
├── Database: SQLite (unchanged)
├── Security: Same + SSH key management
├── Dependencies: +asyncssh
└── Deployment: Same container, +SSH key mount
```

---

## Summary

**Current State:** ✅ **Production-ready infrastructure MCP server**
- 8 working tools
- SSE transport (Open WebUI compatible)
- Clean architecture
- Security features (encryption, audit logging)

**Extension Needed:** 7 Whisper VM management tools
- Minimal changes to existing code
- Well-defined implementation plan
- Estimated effort: 8-16 hours

**Compatibility:** ✅ **Ready for Open WebUI integration**
- Already using SSE transport
- No changes needed for Open WebUI support
- Can add to Open WebUI External Tools immediately

---

**Status:** Production with CCPM integration (2026-01-21)
**Next:** Deploy updated container to Harbor VM

---

## CCPM Integration (2026-01-21)

### Overview

Extended the HomeLab MCP Server with 12 CCPM (Claude Code Project Manager) tools to enable native MCP interaction with project management and agent messaging systems.

### Why MCP Over REST API

Based on agent feedback across multiple projects:
1. **Discoverability** - Tools appear in Claude's tool list automatically
2. **Type Safety** - Schema validation prevents malformed requests
3. **No URL Memorization** - Agents use named tools instead of crafting curl commands
4. **Agent Name Resolution** - Send messages to "HomeLab-Agent" instead of UUID lookup
5. **Validation** - Parameters validated before API calls

### Implementation Details

**Agent Caching:**
- Agent list cached for 5 minutes (reduces API calls)
- Automatic refresh on cache expiration
- Fallback to stale cache if API unavailable

**Name Resolution:**
- `ccpm_send_message()` accepts agent names or UUIDs
- Automatic resolution using cached agent registry
- Case-insensitive name matching

**Error Handling:**
- Structured error responses with error codes
- HTTP status code propagation
- Clear, actionable error messages

### Environment Variables

```bash
# CCPM API endpoints (both on port 8000)
CCPM_TASK_API=http://10.0.1.210:8000/api
CCPM_MESSAGING_API=http://10.0.1.210:8000/api/v1

# Agent identity (for sending messages)
CCPM_AGENT_ID=aaaaaaaa-bbbb-cccc-dddd-222222222222  # HomeLab-Agent
```

### Tool Categories

1. **Agent Messaging (4 tools)** - Inter-agent communication
2. **Task Management (4 tools)** - CCPM task operations
3. **Sprint Management (2 tools)** - Sprint queries
4. **Session Logging (4 tools)** - Session reports via `/api/v1/session-reports`

### Deployment Notes

When deploying updated container:
1. Build new image: `docker build -t homelab-infra:latest .`
2. Save and transfer: `docker save homelab-infra:latest | ssh ccpm@10.0.1.202 docker load`
3. Stop old container: `docker stop homelab-mcp && docker rm homelab-mcp`
4. Start new container with CCPM env vars:
   ```bash
   docker run -d \
     --name homelab-mcp \
     --network openwebui-net \
     -p 8080:8080 \
     -e CCPM_TASK_API=http://10.0.1.210:8000/api \
     -e CCPM_MESSAGING_API=http://10.0.1.210:8000/api/v1 \
     -e CCPM_AGENT_ID=aaaaaaaa-bbbb-cccc-dddd-222222222222 \
     -e HOMELAB_DB_HOST=10.0.1.251 \
     -e HOMELAB_DB_PORT=5433 \
     -e HOMELAB_DB_NAME=homelab_db \
     -e HOMELAB_DB_USER=ccpm \
     -e HOMELAB_DB_PASSWORD=CcpmDb2025Secure \
     --restart unless-stopped \
     homelab-infra:latest
   ```

### Testing Checklist

- [x] All 14 CCPM tools implemented (4 messaging + 4 task + 2 sprint + 4 session)
- [x] Agent name → UUID resolution working
- [x] Error handling returns structured responses
- [x] Python syntax validation passed
- [x] Test suite created (15 tests, all passing)
- [x] CCPM_TASK_API port fixed (8080 → 8000)
- [x] Session tools use correct endpoint (/api/v1/session-reports)
- [x] Container rebuilt and tested
- [x] Deployed to Harbor VM (http://10.0.1.202:8080/sse)
- [ ] Tools visible in Claude when MCP connected
- [ ] End-to-end messaging test between agents

