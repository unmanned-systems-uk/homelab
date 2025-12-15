# CCPM AI Enhancement Plan

**Created:** 2025-12-15
**Purpose:** Custom Ollama model + MCP server for complete CCPM system understanding
**Status:** Strategic Planning Phase

---

## Vision

Build a **CCPM-native AI system** with two components:

1. **Custom Ollama Model** - Fine-tuned to understand CCPM architecture, code patterns, and domain knowledge
2. **CCPM MCP Server** - Real-time access to CCPM database, API, and system state

**Result:** AI agents that truly understand CCPM's 120+ table schema, workflow engine, testing framework, and agent orchestration.

---

## Current CCPM System Analysis

### Codebase Scale
- **Go Backend:** 134 files (~70,000+ lines)
- **JavaScript Frontend:** 12 files
- **Total Code:** ~81,000 lines
- **Database:** SQLite with 120+ tables (11.5 MB)

### Key System Components

| Component | Tables | Purpose |
|-----------|--------|---------|
| **Agent Orchestration** | 10+ | Background agents, sessions, performance tracking |
| **Sprint Management** | 5+ | Sprints, tasks, todos, dependencies |
| **Testing Framework** | 15+ | Test plans, results, templates, approvals |
| **Context System** | 8+ | Context bundles, sessions, archives |
| **Workflow Engine** | 8+ | Rules, decisions, executions |
| **Master AI System** | 10+ | Decision logs, health monitoring, API budgets |
| **Lessons Learned** | 12+ | Lessons, validations, feedback, outcomes |
| **Terminal/Tmux** | 10+ | Session logs, configs, search |
| **Compliance** | 5+ | Audit logs, escalations, deliverables |
| **Projects** | 3+ | Projects, issues, comments |

### API Surface
- **REST API:** ~100+ endpoints (estimated from table structure)
- **Current Host:** localhost:8080
- **Target Host:** Harbor VM (10.0.1.202) or dedicated CCPM VM

---

## Component 1: Custom CCPM Ollama Model

### Approach: Fine-Tuning vs RAG

**Option A: Fine-Tuned Model** (Recommended)
- Base model: llama3:8b or codellama:13b
- Training data: CCPM codebase + documentation + architectural patterns
- Result: Model "knows" CCPM architecture intrinsically

**Option B: RAG (Retrieval-Augmented Generation)**
- Base model: existing llama3:8b
- Vector database: Embeddings of CCPM code/docs
- Result: Model retrieves relevant code on-demand

**Recommendation:** **Hybrid approach** - Fine-tune for architecture understanding + MCP for live data access

---

### Training Data Sources

**1. Code Repository**
```
/home/anthony/ccpm-workspace/production/ccpm-server/
├── internal/           # Core business logic
│   ├── database/       # Data models
│   ├── api/            # REST endpoints
│   ├── agents/         # Agent orchestration
│   ├── workflow/       # Workflow engine
│   └── github/         # GitHub integration
├── cmd/                # Entry points
├── scripts/            # Automation
└── static/             # Frontend
```

**2. Database Schema**
- Extract schema: `sqlite3 ccpm.db .schema > ccpm_schema.sql`
- 120+ tables with relationships
- Indexes, constraints, triggers

**3. Documentation**
- API documentation
- Architecture diagrams
- Workflow rules
- Agent definitions

**4. Conversation History**
- CCPM development sessions
- Problem-solving patterns
- Design decisions

---

### Fine-Tuning Process (Ollama)

**Step 1: Prepare Training Data**
```bash
# Create training dataset
cd /home/anthony/ccpm-workspace/production/ccpm-server

# Extract all Go code with comments
find . -name "*.go" -exec cat {} \; > /tmp/ccpm_code.txt

# Extract database schema
sqlite3 ccpm.db .schema > /tmp/ccpm_schema.sql

# Create QA pairs
python3 scripts/generate-training-pairs.py \
  --code /tmp/ccpm_code.txt \
  --schema /tmp/ccpm_schema.sql \
  --output /tmp/ccpm_training.jsonl
```

**Training pair examples:**
```json
{"prompt": "What tables store task dependencies?", "response": "Task dependencies are stored in the `task_dependencies` table with columns: id, task_id, depends_on_task_id, dependency_type, created_at. Related tables: `tasks`, `dependency_resolution_log`."}

{"prompt": "How does the workflow engine execute rules?", "response": "The workflow engine uses these tables: `workflow_rules` (rule definitions), `workflow_decisions` (execution results), `workflow_rule_executions` (audit trail). Rules are evaluated in internal/workflow/engine.go using the RuleEngine struct."}

{"prompt": "Explain the agent orchestration system", "response": "CCPM uses background agents tracked in `background_agents`, `agent_sessions`, and `agent_activity_log`. Agent status transitions are logged in `agent_status` and `agent_idle_events`. Performance is monitored via `agent_performance_snapshots`."}
```

**Step 2: Create Modelfile**
```dockerfile
# Modelfile-ccpm-expert
FROM llama3:8b

# System prompt for CCPM expertise
SYSTEM """
You are a CCPM (Claude Code Project Management) expert assistant.

You have deep knowledge of:
- CCPM architecture (120+ table SQLite database)
- Go backend codebase (internal/database, internal/api, internal/workflow)
- Agent orchestration system (background agents, sessions, performance)
- Testing framework (test plans, templates, approvals)
- Workflow engine (rules, decisions, executions)
- Sprint management (sprints, tasks, todos, dependencies)
- Context management system (bundles, sessions, archives)
- Master AI decision system
- Terminal/tmux integration

When answering:
1. Reference specific tables, files, or functions
2. Explain relationships between components
3. Provide code examples from actual codebase
4. Consider workflow implications
5. Mention relevant API endpoints

Database location: /home/anthony/ccpm-workspace/production/ccpm-server/ccpm.db
API endpoint: http://localhost:8080 (migrating to Harbor VM)
"""

# Training data
ADAPTER /tmp/ccpm_training.jsonl

# Parameters for precise technical responses
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_predict 2048
```

**Step 3: Fine-Tune Model**
```bash
# SSH to Whisper VM (has GPU for training)
ssh ccpm@10.0.1.201

# Create model
ollama create ccpm-expert -f Modelfile-ccpm-expert

# Test model
ollama run ccpm-expert "Explain the task_dependencies table structure"
```

**Training time estimate:** 2-4 hours on GTX 1080 Ti (11GB VRAM)

---

## Component 2: CCPM MCP Server

### Purpose
Provide **live access** to CCPM system state for AI agents:
- Query database in real-time
- Execute workflow rules
- Check agent status
- Retrieve context bundles
- Monitor system health
- Create/update tasks, sprints, tests

### Architecture

```
Open WebUI / Claude Desktop
    ↓
CCPM MCP Server (SSE transport)
    ↓
┌─────────────────────────────────┐
│ CCPM API (http://10.0.1.202:8080) │
│ CCPM Database (SQLite)            │
│ CCPM Filesystem (logs, context)   │
└─────────────────────────────────┘
```

### MCP Tools Design (30+ tools)

**Sprint Management Tools (5 tools)**
```python
@mcp.tool()
def ccpm_list_sprints(project_id: int = None, status: str = None) -> list:
    """List sprints with optional filters"""

@mcp.tool()
def ccpm_get_sprint(sprint_id: int) -> dict:
    """Get sprint details with tasks and metrics"""

@mcp.tool()
def ccpm_create_sprint(project_id: int, name: str, goal: str) -> dict:
    """Create new sprint"""

@mcp.tool()
def ccpm_list_tasks(sprint_id: int = None, status: str = None) -> list:
    """List tasks with filters"""

@mcp.tool()
def ccpm_update_task_status(task_id: int, status: str) -> dict:
    """Update task status with workflow validation"""
```

**Agent Tools (5 tools)**
```python
@mcp.tool()
def ccpm_list_agents(status: str = None) -> list:
    """List background agents and their status"""

@mcp.tool()
def ccpm_get_agent_health(agent_id: str) -> dict:
    """Get agent health metrics and performance"""

@mcp.tool()
def ccpm_agent_activity(agent_id: str, hours: int = 24) -> list:
    """Get agent activity log"""

@mcp.tool()
def ccpm_start_agent_session(agent_type: str, context: dict) -> dict:
    """Start new agent session"""

@mcp.tool()
def ccpm_agent_metrics(agent_id: str) -> dict:
    """Get agent performance snapshots"""
```

**Testing Tools (5 tools)**
```python
@mcp.tool()
def ccpm_list_test_plans(sprint_id: int = None) -> list:
    """List test plans with status"""

@mcp.tool()
def ccpm_create_test_plan(sprint_id: int, template_id: int) -> dict:
    """Create test plan from template"""

@mcp.tool()
def ccpm_submit_test_result(test_id: int, result: str, evidence: dict) -> dict:
    """Submit test result with evidence"""

@mcp.tool()
def ccpm_approve_test(test_id: int, approver: str) -> dict:
    """Approve test result"""

@mcp.tool()
def ccpm_test_coverage(sprint_id: int) -> dict:
    """Get test coverage metrics"""
```

**Workflow Tools (3 tools)**
```python
@mcp.tool()
def ccpm_execute_workflow_rule(rule_id: int, context: dict) -> dict:
    """Execute workflow rule and get decision"""

@mcp.tool()
def ccpm_get_workflow_decisions(task_id: int) -> list:
    """Get workflow decisions for task"""

@mcp.tool()
def ccpm_validate_workflow_transition(task_id: int, new_status: str) -> dict:
    """Validate if status transition is allowed"""
```

**Context Tools (4 tools)**
```python
@mcp.tool()
def ccpm_get_context_bundle(bundle_id: int) -> dict:
    """Get context bundle with all entries"""

@mcp.tool()
def ccpm_list_context_sessions(agent_id: str) -> list:
    """List context sessions for agent"""

@mcp.tool()
def ccpm_archive_context(session_id: int) -> dict:
    """Archive context session"""

@mcp.tool()
def ccpm_search_context(query: str) -> list:
    """Search context entries"""
```

**Lessons Learned Tools (3 tools)**
```python
@mcp.tool()
def ccpm_get_lessons(project_id: int = None) -> list:
    """Get lessons learned"""

@mcp.tool()
def ccpm_apply_lesson(lesson_id: int, task_id: int) -> dict:
    """Apply lesson to task"""

@mcp.tool()
def ccpm_validate_lesson(lesson_id: int, outcome: str) -> dict:
    """Validate lesson effectiveness"""
```

**System Health Tools (3 tools)**
```python
@mcp.tool()
def ccpm_system_health() -> dict:
    """Get system health status"""

@mcp.tool()
def ccpm_master_status() -> dict:
    """Get Master AI status and decisions"""

@mcp.tool()
def ccpm_api_budget_status() -> dict:
    """Get API budget usage"""
```

**Database Query Tools (2 tools)**
```python
@mcp.tool()
def ccpm_query_database(query: str) -> list:
    """Execute read-only SQL query (SELECT only)"""

@mcp.tool()
def ccpm_get_table_schema(table_name: str) -> dict:
    """Get table schema and relationships"""
```

---

### CCPM MCP Server Implementation

**Location:** `/home/anthony/ccpm-workspace/HomeLab/mcp-servers/ccpm-server/`

**Structure:**
```
ccpm-server/
├── ccpm_mcp_server.py      # Main MCP server
├── ccpm_client.py           # CCPM API client wrapper
├── database_tools.py        # Direct database access tools
├── Dockerfile               # Container build
├── requirements.txt         # Dependencies
├── catalog.yaml             # Docker MCP catalog
└── README.md                # Documentation
```

**requirements.txt:**
```
fastmcp>=2.0.0
httpx>=0.25.0          # For CCPM API calls
sqlite3                 # For direct DB access (if needed)
```

**Example Implementation:**
```python
# ccpm_mcp_server.py
from fastmcp import FastMCP
import httpx
import sqlite3
from pathlib import Path

mcp = FastMCP("ccpm-server")

# Configuration
CCPM_API_URL = "http://10.0.1.202:8080"  # After migration
CCPM_DB_PATH = "/data/ccpm.db"  # Volume mount

@mcp.tool()
async def ccpm_list_sprints(project_id: int = None, status: str = None) -> list:
    """List sprints with optional project and status filters."""
    async with httpx.AsyncClient() as client:
        params = {}
        if project_id:
            params['project_id'] = project_id
        if status:
            params['status'] = status

        response = await client.get(f"{CCPM_API_URL}/api/sprints", params=params)
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def ccpm_get_agent_health(agent_id: str) -> dict:
    """Get agent health metrics and current status."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CCPM_API_URL}/api/agents/{agent_id}/health")
        response.raise_for_status()
        return response.json()

@mcp.tool()
def ccpm_get_table_schema(table_name: str) -> dict:
    """Get database table schema and column information."""
    conn = sqlite3.connect(CCPM_DB_PATH)
    cursor = conn.cursor()

    # Get table info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    # Get foreign keys
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys = cursor.fetchall()

    conn.close()

    return {
        "table": table_name,
        "columns": [{"name": col[1], "type": col[2], "nullable": not col[3]} for col in columns],
        "foreign_keys": [{"column": fk[3], "references": f"{fk[2]}({fk[4]})"} for fk in foreign_keys]
    }

if __name__ == "__main__":
    mcp.run(transport="sse", port=8081, host="0.0.0.0")
```

**Deployment:**
```bash
# Build image
cd ~/ccpm-workspace/HomeLab/mcp-servers/ccpm-server
docker build -t ccpm-mcp:latest .

# Deploy to Harbor VM (or dedicated CCPM VM)
ssh ccpm@10.0.1.202 "docker run -d \
  --name ccpm-mcp \
  --network openwebui-net \
  -p 8081:8081 \
  -v /path/to/ccpm.db:/data/ccpm.db:ro \
  ccpm-mcp:latest"
```

---

## Migration Strategy: Local → HomeLab Server

### Phase 1: CCPM Server Migration (Sprint 1)

**Goal:** Move CCPM server from local dev machine to dedicated HomeLab VM

**Tasks:**
1. **Provision CCPM VM on Proxmox**
   - OS: Ubuntu 24.04 LTS
   - Resources: 4 CPU, 8GB RAM, 100GB storage
   - Network: 10.0.1.x static IP (e.g., 10.0.1.210)

2. **Setup CCPM Server Environment**
   - Install Go 1.21
   - Install SQLite
   - Clone ccpm repository
   - Build server binary

3. **Database Migration**
   - Export local database: `sqlite3 ccpm.db .dump > ccpm_backup.sql`
   - Transfer to VM
   - Import and verify integrity

4. **NGINX Reverse Proxy**
   - Configure SSL (Let's Encrypt or self-signed)
   - Proxy https://ccpm.homelab.local → http://10.0.1.210:8080

5. **Testing**
   - Verify all API endpoints
   - Test agent orchestration
   - Verify workflow engine
   - Test GitHub integration

**Success Criteria:** CCPM server running on HomeLab VM, accessible via HTTPS

---

### Phase 2: Custom CCPM Model Training (Sprint 2)

**Goal:** Create fine-tuned Ollama model with CCPM expertise

**Tasks:**
1. **Generate Training Data**
   - Extract all Go code
   - Extract database schema
   - Create QA pairs (500-1000 examples)
   - Include architectural patterns

2. **Train Model on Whisper VM**
   - Create Modelfile
   - Train with Ollama
   - Validate responses
   - Benchmark performance

3. **Integration Testing**
   - Test model with real CCPM questions
   - Compare to base llama3:8b
   - Measure accuracy improvement

**Success Criteria:** ccpm-expert model deployed on Whisper VM with >80% accuracy on CCPM architecture questions

---

### Phase 3: CCPM MCP Server Development (Sprint 3)

**Goal:** Build MCP server for CCPM system access

**Tasks:**
1. **Design MCP Tools** (30+ tools)
   - Sprint management (5 tools)
   - Agent monitoring (5 tools)
   - Testing framework (5 tools)
   - Workflow engine (3 tools)
   - Context system (4 tools)
   - Lessons learned (3 tools)
   - System health (3 tools)
   - Database queries (2 tools)

2. **Implement MCP Server**
   - FastMCP framework
   - CCPM API client wrapper
   - Direct database access (read-only)
   - Audit logging

3. **Deploy to Harbor VM**
   - Build Docker container
   - Configure network access
   - Mount database volume

4. **Test Integration**
   - Test all tools
   - Verify security
   - Performance testing

**Success Criteria:** CCPM MCP server deployed and accessible from Open WebUI

---

### Phase 4: Open WebUI Integration (Sprint 4)

**Goal:** Connect custom model + MCP to Open WebUI

**Tasks:**
1. **Configure Open WebUI**
   - Add CCPM MCP server
   - Create "CCPM Expert" model profile
   - Configure system prompts

2. **Create CCPM Chat Interface**
   - Custom page for CCPM queries
   - Pre-defined prompts
   - Quick actions (create sprint, update task, etc.)

3. **End-to-End Testing**
   - Test conversational sprint management
   - Test task creation via natural language
   - Test agent monitoring
   - Test workflow execution

**Success Criteria:** Full conversational CCPM management through Open WebUI

---

## Timeline Estimate

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Server Migration | 1 week | 20-30 hours |
| Phase 2: Model Training | 1 week | 15-20 hours |
| Phase 3: MCP Development | 2 weeks | 40-50 hours |
| Phase 4: Integration | 1 week | 15-20 hours |
| **Total** | **5-6 weeks** | **90-120 hours** |

---

## Benefits

**1. True CCPM Understanding**
- AI knows table relationships without looking them up
- Understands workflow engine patterns
- Recognizes agent orchestration logic

**2. Real-Time System Access**
- Query live database state
- Execute workflow rules
- Monitor agent health
- Create/update entities

**3. Conversational Project Management**
- "Create a sprint for HomeLab MCP development"
- "Show me all failing tests in Sprint 28"
- "What agents are currently idle?"
- "Apply lesson #42 to task #1065"

**4. Unified AI Ecosystem**
- CCPM-expert model for architecture questions
- CCPM MCP for live system operations
- HomeLab MCP for infrastructure
- All accessible from Open WebUI

---

## Next Steps

**Immediate (This Session):**
1. ✅ Document strategy
2. Create GitHub issue for CCPM migration
3. Create Sprint 29 for Phase 1 (Server Migration)
4. Generate training data script

**Week 1:**
- Provision CCPM VM on Proxmox
- Migrate database
- Deploy server
- Test endpoints

**Week 2:**
- Generate training dataset
- Train ccpm-expert model
- Validate accuracy

**Weeks 3-4:**
- Develop CCPM MCP server
- Implement 30+ tools
- Deploy and test

**Week 5:**
- Integrate with Open WebUI
- End-to-end testing
- Documentation

---

## Questions for User

1. **VM Allocation:** Create dedicated CCPM VM (10.0.1.210) or use existing VM?
2. **Model Base:** Use llama3:8b or codellama:13b for fine-tuning?
3. **MCP Scope:** All 30+ tools or start with MVP (10 core tools)?
4. **Migration Timing:** Start Phase 1 immediately or after current MCP testing?
5. **Authentication:** Add API key auth to CCPM MCP server?

---

**Status:** Ready for sprint creation and implementation kickoff 🚀

