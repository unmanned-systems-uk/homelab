# HomeLab MCP Server - Current Structure

**Created:** 2025-12-15
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

### 8 Tools Implemented

| Tool | Purpose | Security |
|------|---------|----------|
| `homelab_list_vms(status)` | List all VMs, optional filter | Read-only |
| `homelab_get_vm(vm_id, name)` | Get VM details | Read-only |
| `homelab_get_credentials(target)` | Get credentials for vm/host/service | **AUDIT LOGGED** |
| `homelab_list_services(vm_id)` | List services, optional VM filter | Read-only |
| `homelab_check_service_health(name)` | HTTP health check | Network call |
| `homelab_list_hosts()` | List Proxmox hosts | Read-only |
| `homelab_get_host(host_id, name)` | Get host details | Read-only |
| `homelab_lookup_ip(ip)` | Lookup IP allocation | Read-only |

---

## Architecture

### Tech Stack

**Framework:** FastMCP 2.0+
**Language:** Python 3.11
**Transport:** SSE (Server-Sent Events over HTTP)
**Database:** SQLite (homelab.db)
**Encryption:** Fernet (AES-128 via cryptography library)
**HTTP Client:** httpx (for health checks)

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
SQLite Database (homelab.db) + Encryption Module
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
httpx>=0.25.0          # Async HTTP client for health checks
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
  -p 8080:8000 \
  -v /home/ccpm/data/homelab.db:/data/homelab.db:ro \
  homelab-infra:latest
```

**Volume Mounts:**
- Database: `/home/ccpm/data/homelab.db` → `/data/homelab.db` (read-only)

**Network:**
- Bridge network: `openwebui-net`
- Port mapping: 8080 (host) → 8000 (container)

**Environment Variables:**
- `HOMELAB_DB_PATH=/data/homelab.db` (default)
- `HOMELAB_DB_KEY` (optional, for credential decryption)
- `MCP_PORT=8080` (SSE server port)

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

**Status:** Ready for evaluation and extension planning
**Next:** Decide on modular structure vs single-file approach

