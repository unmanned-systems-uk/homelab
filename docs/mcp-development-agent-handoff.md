# MCP Development Agent - Handoff Document

**Created:** 2025-12-15
**For:** Future MCP development agent
**Context:** HomeLab Specialist Agent research and planning phase complete

---

## Mission

Develop a Model Context Protocol (MCP) server to integrate Whisper VM management tools into Open WebUI, enabling conversational infrastructure management through natural language.

---

## What Has Been Done ✅

### 1. Research Completed

**Open WebUI MCP Support:**
- ✅ Open WebUI v0.6.31+ has native MCP integration
- ✅ Supports SSE (Server-Sent Events) transport
- ✅ Configuration: Admin Settings → External Tools → Add MCP Server
- ✅ Tools are callable directly from chat interface

**Documentation:**
- https://docs.openwebui.com/features/mcp/
- Transport: "MCP (Streamable HTTP)" only (no stdio)

### 2. Infrastructure Verified

**Current Setup:**
- ✅ Open WebUI running on Harbor VM (10.0.1.202:3443)
- ✅ HomeLab MCP server running on Harbor VM (10.0.1.202:8080/sse)
- ✅ SSE transport compatible with Open WebUI requirements
- ✅ Whisper VM accessible via SSH from Harbor (10.0.1.201)

### 3. Requirements Documented

**Tools Needed:**
1. `whisper_ssh_command(command: str)` - Execute shell commands on Whisper VM
2. `ollama_list_models()` - List Ollama models
3. `ollama_pull_model(model_name: str)` - Pull new Ollama model
4. `ollama_delete_model(model_name: str)` - Delete Ollama model
5. `whisper_gpu_status()` - Get GPU metrics (nvidia-smi)
6. `whisper_read_file(file_path: str)` - Read files from Whisper VM
7. `whisper_write_file(file_path: str, content: str)` - Write files to Whisper VM

**Security Requirements:**
- SSH key-based authentication (ccpm@10.0.1.201)
- Path restrictions for file operations (`/home/ccpm` only)
- Audit logging for all operations

### 4. Testing Tasks Created

**HomeLab Project Tasks:**
- Task #1063: Verify Open WebUI MCP compatibility
- Task #1065: Extend HomeLab MCP with Whisper tools
- Task #1067: Deploy updated MCP server
- Task #1068: Configure MCP in Open WebUI
- Task #1069: Test MCP tools from chat
- Task #1070: Document findings

**GitHub Issue:** #436 in cc-project-management repo

### 5. Open WebUI Customization Research

**Three levels documented:**
1. Environment variables (simple)
2. CSS customization (moderate)
3. Source code fork (advanced)

**Key findings:**
- Open WebUI is fully open source (MIT license)
- Source code available: https://github.com/open-webui/open-webui
- Tech stack: Svelte (frontend) + Python FastAPI (backend)
- Can be forked and customized 100%

**Documentation created:**
- `openwebui-customization-guide.md`
- `openwebui-fork-guide.md`

---

## What You Need to Do

### Phase 1: Extend HomeLab MCP Server

**Location:** Harbor VM, existing `homelab-mcp` container

**Current MCP Server:**
- Base: FastMCP Python library
- Transport: SSE (already compatible)
- Endpoint: http://10.0.1.202:8080/sse
- Database: homelab.db (SQLite with encrypted credentials)

**Your Tasks:**

1. **Add Dependencies**
   ```python
   # requirements.txt
   fastmcp
   asyncssh
   httpx
   ```

2. **Create Whisper Tools Module**
   ```python
   # File: tools/whisper.py
   from mcp import Server
   import asyncssh
   import httpx

   mcp = Server("homelab")

   @mcp.tool()
   async def whisper_ssh_command(command: str) -> str:
       """Execute command on Whisper VM via SSH"""
       async with asyncssh.connect(
           host="10.0.1.201",
           username="ccpm",
           client_keys=["/app/.ssh/id_ed25519"]
       ) as conn:
           result = await conn.run(command)
           return result.stdout + result.stderr

   @mcp.tool()
   async def ollama_list_models() -> list:
       """List Ollama models on Whisper VM"""
       async with httpx.AsyncClient() as client:
           response = await client.get("http://10.0.1.201:11434/api/tags")
           data = response.json()
           return [{"name": m["name"], "size_gb": round(m["size"] / 1e9, 2)}
                   for m in data["models"]]

   # Add remaining tools...
   ```

3. **Update Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app

   # Add SSH client
   RUN apt-get update && apt-get install -y openssh-client

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .
   EXPOSE 8000
   CMD ["python", "server.py"]
   ```

4. **Build and Deploy**
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

### Phase 2: Configure Open WebUI

**Access:** https://10.0.1.202:3443

**Steps:**
1. Login as admin
2. Navigate to ⚙️ Admin Settings → External Tools
3. Click "+ Add Server"
4. Configure:
   - **Name:** Whisper VM Manager
   - **Type:** MCP (Streamable HTTP)
   - **Server URL:** http://homelab-mcp:8000/sse
   - **Description:** Manage Whisper VM, Ollama models, GPU monitoring
5. Save configuration
6. Verify tools appear in Open WebUI

### Phase 3: Test Integration

**Test Cases:**

1. **List Ollama Models**
   ```
   User: "What Ollama models are installed on Whisper?"
   Expected: Assistant calls ollama_list_models()
   Expected Output: List of requirements-agent, claude-refiner, llama3:8b
   ```

2. **Check GPU Status**
   ```
   User: "What's the GPU utilization on Whisper VM?"
   Expected: Assistant calls whisper_gpu_status()
   Expected Output: Utilization %, memory used/total, temperature
   ```

3. **Execute SSH Command**
   ```
   User: "Check disk space on Whisper VM"
   Expected: Assistant calls whisper_ssh_command("df -h /")
   Expected Output: Filesystem usage table
   ```

4. **Pull Ollama Model**
   ```
   User: "Pull the gemma:2b model on Whisper"
   Expected: Assistant calls ollama_pull_model("gemma:2b")
   Expected Output: Download progress, success confirmation
   ```

5. **Read Modelfile**
   ```
   User: "Show me the requirements-agent Modelfile"
   Expected: Assistant calls whisper_read_file("/home/ccpm/Modelfile-requirements-agent")
   Expected Output: File contents displayed
   ```

### Phase 4: Document Findings

**Create Report:**
- UX patterns (how natural language → tool calls works)
- Authentication model (how Open WebUI passes user context)
- Limitations discovered
- Performance observations
- Recommendations for CCPM integration

**Update Task #1070** with findings

---

## Key Files and Locations

### HomeLab MCP Server
- **Location:** Harbor VM (10.0.1.202)
- **Container:** `homelab-mcp`
- **Code:** `~/ccpm-workspace/HomeLab/homelab-mcp/`
- **Endpoint:** http://10.0.1.202:8080/sse
- **Database:** `~/data/homelab.db` (SQLite, encrypted)

### Open WebUI
- **Location:** Harbor VM (10.0.1.202)
- **Container:** `open-webui`
- **Access:** https://10.0.1.202:3443
- **Data:** `/app/backend/data/webui.db` (SQLite)
- **Network:** `openwebui-net` (Docker bridge)

### Whisper VM
- **IP:** 10.0.1.201
- **SSH:** Port 22, user `ccpm`, key-based auth
- **Ollama:** http://10.0.1.201:11434
- **GPU:** GTX 1080 Ti (11GB VRAM)
- **Models:** requirements-agent, claude-refiner, llama3:8b

### SSH Key
- **Location:** Harbor VM `~/.ssh/id_ed25519`
- **Mount:** Volume mount to MCP container (read-only)
- **Permissions:** 600, restricted to ccpm user

---

## Documentation References

### Created During Research Phase

1. **`whisper-mcp-integration-plan.md`**
   - MCP-based architecture vs sidecar approach
   - Tool specifications
   - Implementation steps

2. **`openwebui-customization-guide.md`**
   - Customization levels (env vars, CSS, fork)
   - Licensing information
   - Recommended approaches

3. **`openwebui-fork-guide.md`**
   - Fork process
   - Build instructions
   - Maintenance workflow

4. **`two-phase-workflow-architecture.md`**
   - requirements-agent + claude-refiner workflow
   - Complete architecture documentation
   - Usage examples

5. **`project-context-enhancement-proposal.md`**
   - Future enhancement: project-aware requirements-agent
   - RAG vs MCP vs static approaches

### External References

- [Open WebUI MCP Docs](https://docs.openwebui.com/features/mcp/)
- [Open WebUI Repository](https://github.com/open-webui/open-webui)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [FastMCP Library](https://github.com/jlowin/fastmcp)

---

## Success Criteria

**Minimum Viable Product:**
- ✅ MCP server with at least 3 tools working
- ✅ Open WebUI can discover and call tools
- ✅ Natural language queries successfully invoke tools
- ✅ Tools return useful data to chat interface

**Stretch Goals:**
- File operations (read/write Modelfiles)
- Model management (pull/delete with progress)
- Real-time GPU monitoring
- Error handling and user-friendly messages

---

## Known Challenges

### 1. Authentication Passthrough
**Issue:** How does Open WebUI pass user context to MCP tools?
**Investigation Needed:** Check if MCP protocol includes user identity in requests

### 2. Streaming Responses
**Issue:** Model pull operations take time, need progress updates
**Solution:** Investigate if MCP supports streaming/progressive responses

### 3. Error Handling
**Issue:** SSH failures, Ollama API errors need graceful handling
**Solution:** Wrap all tool calls in try/except, return user-friendly errors

### 4. Security
**Issue:** SSH command execution is powerful, could be dangerous
**Solution:**
- Input validation on commands
- Audit logging (already implemented in homelab.db)
- Consider command whitelist for production

---

## Timeline Estimate

**Phase 1:** Extend MCP Server (4-8 hours)
- Add dependencies
- Implement tools
- Test locally

**Phase 2:** Deploy and Configure (1-2 hours)
- Build Docker image
- Deploy to Harbor
- Configure Open WebUI

**Phase 3:** Testing (2-4 hours)
- Test each tool
- Document UX patterns
- Fix issues

**Phase 4:** Documentation (1-2 hours)
- Create findings report
- Update task status
- Recommendations

**Total:** 8-16 hours (1-2 days)

---

## Questions for Clarification

1. **Scope:** Should we implement all 7 tools or start with 3 basic ones?
2. **UI:** Just MCP tools or also custom Open WebUI pages?
3. **Security:** What level of SSH access is acceptable? (read-only, full shell?)
4. **Integration:** Should MCP tools integrate with CCPM workflow (audit logging)?

---

## Handoff Checklist

**Before You Start:**
- [ ] Read this entire document
- [ ] Review `whisper-mcp-integration-plan.md`
- [ ] Access Open WebUI (https://10.0.1.202:3443) - verify login works
- [ ] SSH to Harbor VM - verify homelab-mcp container running
- [ ] SSH to Whisper VM - verify access from Harbor works

**Development:**
- [ ] Clone/update homelab-mcp repository
- [ ] Add asyncssh and httpx dependencies
- [ ] Implement tools (start with 3: ssh_command, list_models, gpu_status)
- [ ] Test tools locally
- [ ] Build Docker image
- [ ] Deploy to Harbor VM

**Testing:**
- [ ] Configure MCP server in Open WebUI
- [ ] Test tool discovery
- [ ] Test tool execution from chat
- [ ] Document UX patterns
- [ ] Fix any issues found

**Documentation:**
- [ ] Create findings report
- [ ] Update task #1070
- [ ] Commit code to git
- [ ] Update session summary

---

## Contact Information

**Current Status:**
- GitHub Issue: #436 (cc-project-management)
- Testing Tasks: #1063-#1070 (HomeLab project)
- Implementation Plan: `whisper-mcp-integration-plan.md`

**For Questions:**
- Review documentation in `docs/` directory
- Check Open WebUI documentation
- Test locally before deploying

---

**Good luck! The foundation is laid - now build something awesome!** 🚀

---

*Handoff prepared by HomeLab Specialist Agent*
*Session: 2025-12-15*
