# Whisper VM Management via MCP Integration

**Created:** 2025-12-15
**Status:** Planning
**Approach:** MCP Server + Open WebUI Native Integration

---

## Discovery: Open WebUI Native MCP Support

Open WebUI v0.6.31+ has **built-in MCP server integration**, eliminating the need for complex sidecar architectures.

**Documentation:** https://docs.openwebui.com/features/mcp/

**Key Features:**
- Admin Settings → External Tools → Add MCP Server
- Streamable HTTP transport (SSE compatible)
- Tools callable directly from chat interface
- Native authentication integration

---

## Architecture

### Current Infrastructure

**Harbor VM (10.0.1.202):**
- Open WebUI: https://10.0.1.202:3443 (`ghcr.io/open-webui/open-webui:main`)
- HomeLab MCP Server: http://10.0.1.202:8080/sse (SSE transport) ✅ Already running

**Whisper VM (10.0.1.201):**
- SSH: Port 22 (ccpm user)
- Ollama: Port 11434
- GPU: GTX 1080 Ti

### Proposed Solution

**Option 1: Extend HomeLab MCP Server (Recommended)**

Add new tools to existing `homelab-mcp` container:

```python
# New tools to add:
@mcp.tool()
async def whisper_ssh_command(command: str) -> str:
    """Execute command on Whisper VM via SSH"""

@mcp.tool()
async def whisper_gpu_status() -> dict:
    """Get GPU utilization, memory, temperature from Whisper VM"""

@mcp.tool()
async def ollama_list_models() -> list:
    """List all Ollama models on Whisper VM"""

@mcp.tool()
async def ollama_pull_model(model_name: str) -> str:
    """Pull new Ollama model on Whisper VM"""

@mcp.tool()
async def ollama_delete_model(model_name: str) -> str:
    """Delete Ollama model from Whisper VM"""

@mcp.tool()
async def whisper_read_file(file_path: str) -> str:
    """Read file from Whisper VM (e.g., Modelfiles)"""

@mcp.tool()
async def whisper_write_file(file_path: str, content: str) -> str:
    """Write file to Whisper VM"""
```

**Option 2: Create Dedicated Whisper MCP Server**

New container `whisper-mcp` alongside `homelab-mcp`:

```yaml
services:
  whisper-mcp:
    build: ./whisper-mcp
    ports:
      - "8082:8000"
    environment:
      - WHISPER_SSH_HOST=10.0.1.201
      - WHISPER_SSH_USER=ccpm
    volumes:
      - ~/.ssh/id_ed25519:/app/.ssh/id_ed25519:ro
```

---

## Feature Implementation via MCP Tools

### Feature 1: SSH Command Execution

**MCP Tool:** `whisper_ssh_command(command: str)`

**Usage in Open WebUI:**
```
User: "Check GPU status on Whisper VM"
Assistant calls: whisper_ssh_command("nvidia-smi")
→ Returns GPU utilization, memory, temp
```

**Implementation:**
- Use `asyncssh` library
- SSH to 10.0.1.201 as ccpm user
- Execute command, return stdout
- Security: No path restrictions (user has full SSH access anyway)

### Feature 2: Ollama Model Management

**MCP Tools:**
- `ollama_list_models()` → Calls Ollama API `/api/tags`
- `ollama_pull_model(model_name)` → Calls `/api/pull`, streams progress
- `ollama_delete_model(model_name)` → Calls `/api/delete`
- `ollama_create_model(name, modelfile)` → Calls `/api/create` with Modelfile content

**Usage in Open WebUI:**
```
User: "What Ollama models are installed on Whisper?"
Assistant calls: ollama_list_models()
→ Returns: ["requirements-agent:latest", "claude-refiner:latest", "llama3:8b"]

User: "Pull gemma:2b model"
Assistant calls: ollama_pull_model("gemma:2b")
→ Streams progress updates
```

**Implementation:**
- Use `httpx` to call Ollama API (http://10.0.1.201:11434)
- For pull operations: stream progress back via MCP
- No SSH needed (Ollama has REST API)

### Feature 3: System Resource Monitoring

**MCP Tool:** `whisper_gpu_status()`

**Usage in Open WebUI:**
```
User: "How much GPU memory is being used on Whisper?"
Assistant calls: whisper_gpu_status()
→ Returns: {"utilization": 45, "memory_used": 4096, "memory_total": 11264, "temperature": 68}
```

**Implementation:**
- SSH to Whisper VM
- Run: `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits`
- Parse CSV output
- Return structured JSON

### Feature 4: File Browser

**MCP Tools:**
- `whisper_list_files(directory: str)` → List directory contents
- `whisper_read_file(file_path: str)` → Read file content
- `whisper_write_file(file_path, content)` → Write/update file

**Usage in Open WebUI:**
```
User: "Show me the requirements-agent Modelfile"
Assistant calls: whisper_read_file("/home/ccpm/Modelfile-requirements-agent")
→ Returns file contents

User: "Update the temperature to 0.6 in that Modelfile"
Assistant: [reads file, modifies temperature line, writes back]
→ Calls: whisper_write_file("/home/ccpm/Modelfile-requirements-agent", updated_content)
```

**Implementation:**
- Use SFTP via `asyncssh`
- Security: Restrict to `/home/ccpm` directory only
- Path traversal protection: `os.path.abspath()` validation

---

## Integration Steps

### Step 1: Extend HomeLab MCP Server

**File:** `/home/anthony/ccpm-workspace/HomeLab/homelab-mcp/tools/whisper.py`

```python
import asyncssh
import httpx
from mcp import Server

mcp = Server("homelab")

@mcp.tool()
async def whisper_ssh_command(command: str) -> str:
    """Execute command on Whisper VM via SSH

    Args:
        command: Shell command to execute on Whisper VM

    Returns:
        Command output (stdout + stderr)
    """
    async with asyncssh.connect(
        host="10.0.1.201",
        username="ccpm",
        client_keys=["/app/.ssh/id_ed25519"]
    ) as conn:
        result = await conn.run(command)
        return result.stdout + result.stderr

@mcp.tool()
async def ollama_list_models() -> list:
    """List all Ollama models installed on Whisper VM

    Returns:
        List of model names with sizes and last modified dates
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("http://10.0.1.201:11434/api/tags")
        data = response.json()
        return [
            {
                "name": m["name"],
                "size_gb": round(m["size"] / 1e9, 2),
                "modified": m["modified_at"]
            }
            for m in data["models"]
        ]

@mcp.tool()
async def whisper_gpu_status() -> dict:
    """Get GPU utilization and memory stats from Whisper VM

    Returns:
        Dictionary with GPU metrics (utilization, memory, temperature)
    """
    async with asyncssh.connect(
        host="10.0.1.201",
        username="ccpm",
        client_keys=["/app/.ssh/id_ed25519"]
    ) as conn:
        result = await conn.run(
            "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu "
            "--format=csv,noheader,nounits"
        )
        util, mem_used, mem_total, temp = result.stdout.strip().split(", ")
        return {
            "utilization_percent": int(util),
            "memory_used_mb": int(mem_used),
            "memory_total_mb": int(mem_total),
            "temperature_celsius": int(temp)
        }

# Add more tools for file operations, model pulling, etc.
```

### Step 2: Update HomeLab MCP Dockerfile

**File:** `/home/anthony/ccpm-workspace/HomeLab/homelab-mcp/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add SSH client for Whisper VM access
RUN apt-get update && apt-get install -y openssh-client && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Expose SSE endpoint
EXPOSE 8000

CMD ["python", "server.py"]
```

**Update requirements.txt:**
```
fastmcp
asyncssh
httpx
```

### Step 3: Rebuild and Deploy MCP Server

```bash
cd ~/ccpm-workspace/HomeLab/homelab-mcp
docker build -t homelab-mcp:whisper .
ssh ccpm@10.0.1.202 "docker stop homelab-mcp && docker rm homelab-mcp"
ssh ccpm@10.0.1.202 "docker run -d \
  --name homelab-mcp \
  --network openwebui-net \
  -p 8080:8000 \
  -v ~/.ssh/id_ed25519:/app/.ssh/id_ed25519:ro \
  -v ~/data/homelab.db:/app/data/homelab.db \
  homelab-mcp:whisper"
```

### Step 4: Add MCP Server to Open WebUI

1. Open https://10.0.1.202:3443
2. Login as admin
3. Navigate to **⚙️ Admin Settings → External Tools**
4. Click **+ Add Server**
5. Configure:
   - **Name:** Whisper VM Manager
   - **Type:** MCP (Streamable HTTP)
   - **Server URL:** `http://homelab-mcp:8000/sse`
   - **Description:** Manage Whisper VM, Ollama models, GPU monitoring
6. Save
7. Verify tools appear in Open WebUI

### Step 5: Test MCP Tools

**Test 1: List Ollama Models**
```
User: "What Ollama models are installed?"
→ Assistant should call ollama_list_models()
→ Display: requirements-agent, claude-refiner, llama3
```

**Test 2: Check GPU Status**
```
User: "What's the GPU utilization on Whisper?"
→ Assistant calls whisper_gpu_status()
→ Display: 45% utilization, 4GB used, 68°C
```

**Test 3: Execute SSH Command**
```
User: "Check disk space on Whisper VM"
→ Assistant calls whisper_ssh_command("df -h /")
→ Display: Filesystem usage
```

---

## Advantages Over Sidecar Approach

**Simpler Architecture:**
- ✅ No custom FastAPI service needed
- ✅ No custom authentication (Open WebUI handles it)
- ✅ No WebSocket/SSE endpoint management
- ✅ No Nginx reverse proxy configuration

**Better User Experience:**
- ✅ Tools callable directly from chat (natural language)
- ✅ No separate UI to learn
- ✅ LLM decides when to use tools (intelligent)
- ✅ Multi-tool chaining (e.g., "check GPU, then pull model if space available")

**Security:**
- ✅ Open WebUI's existing auth system
- ✅ MCP's standard security model
- ✅ Audit logging via MCP server
- ✅ No additional attack surface (no exposed APIs)

**Maintenance:**
- ✅ Standard MCP server (well-documented pattern)
- ✅ Open WebUI updates won't break integration
- ✅ Easy to add new tools (just add @mcp.tool())

---

## Limitations

**Terminal Access:**
- MCP tools are request/response (no persistent terminal)
- Solution: `whisper_ssh_command()` can run commands, but no interactive shell
- For interactive terminal: Would still need WebSocket-based solution (separate feature)

**Real-Time Streaming:**
- GPU metrics: Can be polled, but not true real-time dashboard
- Solution: User asks "check GPU status" periodically, or we add a streaming tool

**File Browser UI:**
- No visual tree view (would need separate UI)
- Solution: LLM can navigate files via tools, but it's conversational, not visual

---

## Next Steps

1. **Extend HomeLab MCP server** with Whisper management tools
2. **Test tools locally** before deploying to Harbor
3. **Deploy updated MCP server** to Harbor VM
4. **Add MCP server to Open WebUI** via Admin Settings
5. **Create documentation** for users on how to use tools
6. **Test end-to-end** with real tasks

---

**Status:** Ready to implement
**Estimated Time:** 1-2 days (much faster than sidecar approach!)
**Dependencies:** asyncssh, httpx libraries

