# Project Context Architecture - MCP vs Alternatives

**Created:** 2025-12-15
**Status:** Discussion / Proposal (NOT implemented)
**Purpose:** Explore how to give requirements-agent project context

---

## The Core Question

**How should `requirements-agent` access project information?**

User asks:
1. Should this be an MCP server?
2. If yes, how do we keep it up-to-date?
3. What are the alternative methods?

---

## Option 1: MCP Server for Project Context 🏆

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  requirements-agent (Llama 3 8B)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ "What files handle authentication?"
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  CCPM Project Context MCP Server                            │
│  - ccpm_list_files(pattern)                                 │
│  - ccpm_search_code(query)                                  │
│  - ccpm_get_file_info(path)                                 │
│  - ccpm_explain_component(name)                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Queries live codebase
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  CCPM Codebase (/home/anthony/ccpm-workspace/production)   │
│  - Real-time file scanning                                  │
│  - Git history                                              │
│  - Documentation                                            │
└─────────────────────────────────────────────────────────────┘
```

---

### MCP Tools Design

```python
# CCPM Project Context MCP Server
from fastmcp import FastMCP

mcp = FastMCP("ccpm-context")

@mcp.tool()
def ccpm_list_auth_files() -> list[dict]:
    """List all files related to authentication in CCPM."""
    return [
        {"path": "/production/ccpm-server/internal/auth/auth.go",
         "purpose": "Core authentication logic, JWT generation/validation"},
        {"path": "/production/ccpm-server/internal/middleware/jwt.go",
         "purpose": "JWT middleware for API route protection"}
    ]

@mcp.tool()
def ccpm_search_code(query: str, directory: str = None) -> list[dict]:
    """Search CCPM codebase for specific code patterns."""
    # Uses ripgrep/grep to search actual codebase
    pass

@mcp.tool()
def ccpm_explain_component(component: str) -> dict:
    """Explain what a CCPM component does."""
    knowledge = {
        "authentication": {
            "description": "JWT-based auth system",
            "files": ["auth.go", "jwt.go"],
            "current_method": "JWT tokens",
            "database": "Users table in ccpm.db"
        },
        "api": {
            "description": "REST API endpoints",
            "patterns": ["/api/sprints", "/api/tasks", "/api/todos"],
            "framework": "Gin (Go)"
        },
        # ... more components
    }
    return knowledge.get(component, {"error": "Unknown component"})

@mcp.tool()
def ccpm_get_project_info() -> dict:
    """Get high-level CCPM project information."""
    return {
        "name": "CCPM (Claude Code Project Management)",
        "language": "Go",
        "database": "SQLite",
        "location": "/home/anthony/ccpm-workspace/production/ccpm-server",
        "structure": {
            "backend": "Go (Gin framework)",
            "frontend": "Vanilla JavaScript",
            "database": "SQLite (ccpm.db)"
        }
    }

@mcp.tool()
def ccpm_translate_user_term(term: str) -> dict:
    """Translate user's casual terms to technical components."""
    translations = {
        "login stuff": {
            "technical_term": "authentication system",
            "files": ["auth.go", "jwt.go"],
            "component": "authentication"
        },
        "database": {
            "technical_term": "SQLite database",
            "file": "ccpm.db",
            "orm": "GORM"
        },
        "api": {
            "technical_term": "REST API",
            "location": "/api/* routes",
            "framework": "Gin"
        }
    }
    return translations.get(term.lower(), {"error": "Unknown term"})
```

---

### Pros of MCP Approach ✅

1. **Always Up-to-Date**
   - Queries live codebase (not static snapshot)
   - See file changes in real-time
   - Git history available

2. **Extensible**
   - Add tools as needed
   - Works with other MCP clients (Claude Desktop, etc.)
   - Can combine multiple MCP servers

3. **Standardized**
   - Uses Model Context Protocol standard
   - Compatible with future MCP ecosystem
   - Can share with team

4. **Powerful Queries**
   - Code search (ripgrep)
   - File scanning
   - Git blame/history
   - Dependency analysis

5. **Multi-Project Support**
   - One MCP server per project
   - Or one server with multiple project contexts
   - Easy to add DPM-V2, NEX-Cam, etc.

---

### Cons of MCP Approach ⚠️

1. **Complexity**
   - Need to build MCP server
   - Need to integrate with Ollama workflow
   - More moving parts

2. **Performance**
   - Real-time file scanning can be slow for large codebases
   - MCP overhead (network calls, even if localhost)

3. **Ollama Integration**
   - Ollama models don't natively support MCP (yet)
   - Would need custom integration layer
   - OR: Have requirements-agent call an intermediate service that uses MCP

4. **Maintenance**
   - MCP server needs updates as project structure changes
   - Need to document MCP tools

---

## How to Keep MCP Up-to-Date

### Method 1: Dynamic File Scanning (No Maintenance) ⭐

**Concept:** MCP server scans codebase on every request

```python
@mcp.tool()
def ccpm_list_auth_files() -> list[dict]:
    """Dynamically scan for auth-related files."""
    import glob
    auth_files = glob.glob("/home/anthony/ccpm-workspace/**/*auth*.go", recursive=True)
    return [{"path": f, "modified": os.path.getmtime(f)} for f in auth_files]
```

**Pros:**
- ✅ Zero maintenance (always current)
- ✅ Automatically sees new files
- ✅ Git history via `git log`

**Cons:**
- ⚠️ Slower (file I/O on every request)
- ⚠️ No semantic understanding (just file matching)

---

### Method 2: Indexed with Auto-Refresh

**Concept:** Build index, refresh periodically or on git hooks

```python
# Cron job or git post-commit hook
# Runs: python refresh_ccpm_index.py

def refresh_index():
    """Re-index CCPM codebase."""
    index = {
        "files": scan_all_files(),
        "functions": extract_functions(),
        "api_routes": parse_api_routes(),
        "database_schema": parse_schema(),
        "last_updated": datetime.now()
    }
    save_to_db(index)
```

**Git Hook:** `.git/hooks/post-commit`
```bash
#!/bin/bash
# Auto-refresh project context after commits
python /path/to/refresh_ccpm_index.py
```

**Pros:**
- ✅ Fast queries (pre-indexed)
- ✅ Semantic understanding (parsed structure)
- ✅ Automatic updates (git hooks)

**Cons:**
- ⚠️ Requires git hook setup
- ⚠️ Index can be stale between commits
- ⚠️ More complex

---

### Method 3: Hybrid (Best of Both)

**Concept:** Static index for common queries, dynamic scan for specifics

```python
@mcp.tool()
def ccpm_explain_component(component: str) -> dict:
    """Fast lookup from pre-built index."""
    return STATIC_INDEX[component]  # Instant

@mcp.tool()
def ccpm_search_code(pattern: str) -> list[dict]:
    """Live search for specific patterns."""
    return ripgrep_search(pattern)  # Real-time
```

**Pros:**
- ✅ Fast for common queries
- ✅ Accurate for specific searches
- ✅ Balance of speed and freshness

---

## Option 2: Static Knowledge Base (No MCP)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  requirements-agent (Llama 3 8B)                            │
│  SYSTEM PROMPT includes:                                    │
│  - Project: CCPM (Go + SQLite)                             │
│  - Auth files: auth.go, jwt.go                             │
│  - Common terms: "login stuff" = authentication            │
└─────────────────────────────────────────────────────────────┘
```

**Implementation:** Enhanced Modelfile

```bash
FROM llama3:8b

SYSTEM """
You are a Requirements Analyst with knowledge of:

PROJECT: CCPM (Claude Code Project Management)
Location: /home/anthony/ccpm-workspace/production/ccpm-server
Language: Go (backend), Vanilla JS (frontend)
Database: SQLite (ccpm.db)

COMPONENTS:
1. Authentication (auth.go, jwt.go)
   - Current: JWT tokens
   - Location: internal/auth/
   - Common user terms: "login stuff", "auth", "security"

2. API (Gin framework)
   - Routes: /api/sprints, /api/tasks, /api/todos, /api/projects
   - Common user terms: "api", "endpoints", "server"

3. Database (SQLite)
   - File: ccpm.db
   - ORM: GORM
   - Common user terms: "database", "db", "data"

TERMINOLOGY MAPPING:
- "login stuff" → authentication in auth.go, jwt.go
- "api" → REST endpoints in /api/
- "database" → SQLite (ccpm.db)
- "the server" → ccpm-server Go application

When user mentions these terms, reference the actual components.
Ask clarifying questions using this knowledge.

[Continue with original requirements analyst instructions...]
"""
```

---

### Pros of Static Approach ✅

1. **Simplicity**
   - Just update Modelfile
   - No separate server needed
   - Easy to understand

2. **Speed**
   - No external lookups
   - Everything in model context
   - Fast responses

3. **Portability**
   - Model file is self-contained
   - Easy to share with team
   - No infrastructure dependencies

---

### Cons of Static Approach ⚠️

1. **Manual Updates**
   - ❌ Need to manually update Modelfile when project changes
   - ❌ Can become stale
   - ❌ Doesn't scale to large projects

2. **Limited Context**
   - ❌ System prompt has token limit (~4096 tokens)
   - ❌ Can't include entire codebase
   - ❌ No real-time queries

3. **Single Project**
   - ❌ Need separate model for each project
   - ❌ Or very generic knowledge

---

## Option 3: RAG (Retrieval-Augmented Generation)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  requirements-agent (Llama 3 8B)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ "Tell me about login stuff"
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Embedding Search (Vector DB)                               │
│  - Queries: Chroma/FAISS/Qdrant                            │
│  - Finds: Similar code/docs                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Returns: auth.go description + code snippets
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  requirements-agent responds with context                   │
│  "I see auth.go handles JWT authentication..."             │
└─────────────────────────────────────────────────────────────┘
```

---

### Implementation Concept

```python
# 1. Index CCPM codebase (one-time or on git hooks)
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings()
docs = load_ccpm_files()  # Load all .go, .js, .md files
vectorstore = Chroma.from_documents(docs, embeddings)

# 2. Query when user mentions something
user_query = "login stuff"
relevant_docs = vectorstore.similarity_search(user_query, k=3)

# 3. Inject into requirements-agent prompt
context = "\n".join([doc.page_content for doc in relevant_docs])
prompt = f"User needs help with: {user_query}\n\nProject context:\n{context}\n\nAsk clarifying questions."
```

---

### Pros of RAG ✅

1. **Semantic Search**
   - ✅ Finds relevant code even with vague queries
   - ✅ "login stuff" → finds auth.go (semantic similarity)
   - ✅ Handles synonyms, related terms

2. **Scalable**
   - ✅ Works with large codebases
   - ✅ Can index documentation, comments, README
   - ✅ No token limit issues

3. **Dynamic Context**
   - ✅ Only retrieves what's relevant
   - ✅ Efficient use of context window
   - ✅ Can combine multiple sources

---

### Cons of RAG ⚠️

1. **Infrastructure**
   - ⚠️ Need vector database (Chroma, FAISS, etc.)
   - ⚠️ Need embedding model (CPU/GPU intensive)
   - ⚠️ More complex setup

2. **Update Mechanism**
   - ⚠️ Need to re-index when code changes
   - ⚠️ Git hooks or cron jobs required
   - ⚠️ Embedding generation can be slow

3. **Integration**
   - ⚠️ Requires custom workflow script changes
   - ⚠️ Not native to Ollama
   - ⚠️ More moving parts

---

## Comparison Matrix

| Feature | MCP Server | Static Knowledge | RAG |
|---------|-----------|------------------|-----|
| **Setup Complexity** | High | Low | Medium |
| **Always Up-to-Date** | Yes (dynamic scan) | No (manual) | Semi (needs reindex) |
| **Response Speed** | Medium (API calls) | Fast (in-prompt) | Medium (vector search) |
| **Scalability** | High | Low (token limit) | High |
| **Semantic Understanding** | Low (text matching) | Medium | High (embeddings) |
| **Multi-Project** | Easy (multiple servers) | Hard (separate models) | Easy (separate indices) |
| **Maintenance** | Low (auto-scans) | High (manual updates) | Medium (auto-reindex) |
| **Infrastructure Needs** | MCP server | None | Vector DB + embeddings |
| **Integration with Ollama** | Complex (custom layer) | Native (Modelfile) | Medium (script changes) |
| **Team Sharing** | Easy (MCP standard) | Easy (Modelfile) | Medium (DB export) |

---

## Recommendation: Hybrid Approach 🏆

**Phase 1 (Now): Static Knowledge** ⚡
- Update requirements-agent Modelfile with CCPM basics
- Quick win, works immediately
- Test with users, gather feedback

**Phase 2 (Short-term): MCP Server** 🎯
- Build CCPM Context MCP server
- Start simple (file listing, component explanation)
- Add tools based on user needs
- Use dynamic scanning (no maintenance)

**Phase 3 (Long-term): Add RAG** 🚀
- Index codebase with embeddings
- Semantic search for complex queries
- Combine with MCP for best of both worlds

---

## Example: MCP + RAG Hybrid

```
User: "I need to make the login more secure"
         ↓
[RAG Search]: "login", "secure" → Finds auth.go, jwt.go, security docs
         ↓
[MCP Query]: ccpm_explain_component("authentication")
         ↓
requirements-agent: "I see CCPM uses JWT authentication in auth.go and jwt.go.
                     Current method has potential vulnerabilities with token
                     refresh. Would you like to:
                     1. Implement OAuth 2.0
                     2. Add refresh token rotation
                     3. Implement rate limiting"
```

**Why this is powerful:**
- RAG found the relevant files semantically
- MCP provided structured component info
- Agent asked informed, specific questions
- User gets better experience

---

## Keeping System Up-to-Date

### Git Hooks Approach (Recommended)

**Setup once:**
```bash
# .git/hooks/post-commit
#!/bin/bash
echo "Updating project context..."

# Update MCP index (if using MCP)
curl -X POST http://localhost:8080/mcp/ccpm-context/refresh

# Update RAG embeddings (if using RAG)
python ~/scripts/reindex-ccpm.py

echo "Project context updated!"
```

**Every commit automatically:**
- ✅ Refreshes MCP server index
- ✅ Regenerates RAG embeddings
- ✅ No manual intervention
- ✅ Always current

---

### Watch Service Approach

```bash
# systemd service watching codebase
[Unit]
Description=CCPM Context Auto-Update

[Service]
ExecStart=/usr/bin/inotifywait -m -r /home/anthony/ccpm-workspace/production \
  -e modify,create,delete --format '%w%f' | \
  while read file; do
    python /home/anthony/scripts/reindex-ccpm.py
  done

[Install]
WantedBy=multi-user.target
```

**Real-time updates:**
- ✅ Detects file changes instantly
- ✅ Triggers re-index automatically
- ✅ Always up-to-date

---

## Alternative: No Automation (Manual)

**Just remember to run:**
```bash
# When you make significant project changes
~/scripts/update-project-context.sh
```

**Pros:** Simple, no infrastructure
**Cons:** Easy to forget, can become stale

---

## Answer to Your Questions

### Q1: Should this be an MCP?

**My recommendation:** **Yes, eventually**

**Reasoning:**
- MCP is the future standard for AI-tool integration
- Enables powerful, extensible queries
- Works with Claude Desktop and other tools
- But: Start with static knowledge (quick win), migrate to MCP when proven

---

### Q2: How to keep MCP up-to-date?

**Best approach: Git hooks + dynamic scanning**

```python
# MCP server uses dynamic scanning (no manual updates)
@mcp.tool()
def ccpm_list_auth_files():
    return glob.glob("**/auth*.go")  # Always current

# Git hook triggers reindex for RAG (if using)
# .git/hooks/post-commit
python reindex-ccpm.py
```

**Result:** Zero manual maintenance

---

### Q3: What are alternative methods?

**Three main alternatives:**

1. **Static Knowledge** (Modelfile system prompt)
   - Pros: Simple, fast, works now
   - Cons: Manual updates, limited scale
   - **Best for:** Quick start, small projects

2. **RAG** (Vector DB + embeddings)
   - Pros: Semantic search, scalable, dynamic
   - Cons: Infrastructure needed, complex
   - **Best for:** Large codebases, semantic understanding

3. **Fine-Tuning** (Train model on project)
   - Pros: Deeply understands project, very fast
   - Cons: Requires training data, needs re-training on changes
   - **Best for:** Stable, mature projects

**My pick:** Start with #1 (static), add MCP (#2) when needed, consider fine-tuning (#3) long-term

---

## Next Steps

### Immediate (Test Today)
1. Update requirements-agent Modelfile with CCPM basics (15 minutes)
2. Test with structured and unstructured inputs
3. Gather user feedback

### Short-term (Next Week)
1. Design CCPM Context MCP server tools
2. Build minimal MCP server (3-4 tools)
3. Integrate with workflow script

### Long-term (Ongoing)
1. Add RAG for semantic search
2. Collect training data for fine-tuning
3. Expand to other projects (DPM-V2, NEX-Cam)

---

**Status:** Discussion document (NOT implemented)
**Decision needed:** Which approach to pursue first?
**Recommendation:** Static → MCP → RAG (phased approach)

---

*Architectural exploration by HomeLab Specialist Agent*
*Based on user's excellent questions about MCP feasibility*
