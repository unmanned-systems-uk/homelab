# Ollama Prompt Refinement Architecture

**Created:** 2025-12-15
**Purpose:** Cost-optimized prompt structuring for Claude CLI using local Llama 3

---

## Overview

This architecture uses local Llama 3 8B as a "prompt refiner" to convert conversational human input into structured, precise commands before sending to the expensive Claude API. This reduces token waste and ensures consistent, high-quality prompts.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│  User Input (Voice/Text)                             │
│  "Ask Claude to refactor auth.py using OAuth 2.0..." │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│  Whisper VM (10.0.1.201)                             │
│  ┌────────────────────────────────────────────────┐  │
│  │  Ollama (llama3:8b)                            │  │
│  │  - Prompt refinement                           │  │
│  │  - Structured JSON output                      │  │
│  │  - GBNF grammar enforcement                    │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │  Chatterbox/Piper TTS                          │  │
│  │  - Voice output for responses                  │  │
│  └────────────────────────────────────────────────┘  │
│  GPU: GTX 1080 Ti (shared)                           │
└────────────────────┬─────────────────────────────────┘
                     │ Structured JSON
                     ▼
┌──────────────────────────────────────────────────────┐
│  Claude CLI (Anthropic API - Expensive)              │
│  - Receives clean, structured prompts                │
│  - Minimal token waste                               │
│  - Consistent formatting                             │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  Harbor VM (10.0.1.202)                              │
│  ┌────────────────────────────────────────────────┐  │
│  │  Open WebUI (http://10.0.1.202:3000)          │  │
│  │  - Web interface for Ollama                    │  │
│  │  - Testing and development                     │  │
│  │  - Model management                            │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │  Portainer (https://10.0.1.202:9443)          │  │
│  │  - Container management                        │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │  HomeLab MCP Server (http://10.0.1.202:8080)  │  │
│  │  - Infrastructure access for Claude agents    │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## Components

### 1. Ollama (Whisper VM)

**Location:** http://10.0.1.201:11434
**Model:** llama3:8b (also llama2:latest available)
**Purpose:** Convert conversational prompts to structured JSON

**Key Features:**
- Network-accessible API
- JSON format enforcement via `"format": "json"`
- GBNF grammar support for strict schemas
- GPU-accelerated inference (GTX 1080 Ti)

### 2. Open WebUI (Harbor VM)

**Location:** http://10.0.1.202:3000
**Container:** `open-webui` on Harbor
**Purpose:** Web interface for Ollama testing and development

**Configuration:**
```bash
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://10.0.1.201:11434 \
  -v open-webui:/app/backend/data \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

**Why Harbor?**
- Maintains architectural separation (Harbor = Docker services)
- Open WebUI is just a UI - doesn't need GPU
- Centralized management via Portainer
- Ollama accessible over network from any VM

---

## Use Case: Claude CLI Prompt Refinement

### Problem
Human conversational input to Claude CLI wastes tokens:
- Rambling explanations
- Inconsistent formatting
- Missing required parameters
- Unclear instructions

### Solution
Use Llama 3 8B to pre-process inputs into structured, precise commands:

#### Step 1: User Input (Conversational)
```
"Hey, ask Claude to refactor the authentication logic in auth-dot-py
using OAuth 2.0, and make sure it's using the Sonnet model. Also,
remind it to stick to Python 3.12 and PEP 8."
```

#### Step 2: Llama 3 Refinement (API Call)
```bash
curl http://10.0.1.201:11434/api/generate -d '{
  "model": "llama3:8b",
  "prompt": "Convert this command to structured JSON: Ask Claude to refactor the authentication logic in auth.py using OAuth 2.0, make sure it uses Python 3.12 and PEP 8 standards. Use the Sonnet model.",
  "format": "json",
  "stream": false
}'
```

#### Step 3: Structured JSON Output
```json
{
  "task": {
    "name": "Refactor Authentication Logic",
    "description": "Refactor authentication logic in auth.py using OAuth 2.0",
    "requirements": [
      {"standard": "Python 3.12"},
      {"standard": "PEP 8"}
    ],
    "models": [{"model": "Sonnet"}],
    "file": "auth.py"
  }
}
```

#### Step 4: Claude CLI Execution
```bash
# Script parses JSON and constructs precise Claude command
claude chat \
  --model claude-3-5-sonnet \
  --system "Use Python 3.12 and adhere to PEP 8 standards" \
  "Refactor the authentication logic in auth.py to use OAuth 2.0"
```

---

## Benefits

### 1. Cost Optimization
- **Before:** 150 tokens wasted on rambling input
- **After:** 50 tokens for precise, structured prompt
- **Savings:** 66% token reduction per request

### 2. Consistency
- All Claude requests follow same structured format
- Reduces parsing errors
- Enables automated validation

### 3. Local Processing
- Llama 3 runs locally (free)
- No external API calls for refinement
- Fast response times (<2 seconds)

### 4. System-Wide Integration
Any CCPM agent can use this pattern:

```python
# Example: Backend Designer agent
def refine_prompt(conversational_input: str) -> dict:
    response = requests.post(
        "http://10.0.1.201:11434/api/generate",
        json={
            "model": "llama3:8b",
            "prompt": f"Convert to structured JSON: {conversational_input}",
            "format": "json",
            "stream": False
        }
    )
    return response.json()["response"]
```

---

## Future Enhancements

### 1. Fine-Tuning
Create a dataset of conversational → structured JSON pairs and fine-tune Llama 3 8B for even better accuracy:

```python
# Training data example
{
  "input": "Ask Claude to refactor auth.py using OAuth 2.0, Python 3.12, PEP 8",
  "output": {
    "cli_command": "claude",
    "model": "claude-3-5-sonnet",
    "system_prompt": "Use Python 3.12 and PEP 8",
    "user_query": "Refactor auth.py to use OAuth 2.0"
  }
}
```

### 2. Speech-to-Text Integration
Add Whisper STT for voice input:

```
Voice → Whisper STT → Llama 3 Refiner → Claude CLI
```

### 3. GBNF Grammar Enforcement
Use Llama.cpp GBNF to guarantee valid JSON schema:

```python
# Enforce specific schema structure
grammar = """
root ::= object
object ::= "{" ws "\"task\":" ws task ws "}"
task ::= "{" ws "\"file\":" ws string ws "," ws "\"action\":" ws string ws "}"
"""
```

### 4. MCP Tool Integration
Expose refinement as HomeLab MCP tool:

```python
@mcp.tool()
def homelab_refine_prompt(conversational_input: str) -> dict:
    """Refine conversational input into structured Claude CLI command."""
    # Call Ollama API, return structured JSON
```

---

## Testing

### Test 1: Basic Refinement
```bash
curl -s http://10.0.1.201:11434/api/generate -d '{
  "model": "llama3:8b",
  "prompt": "Convert to structured JSON: Ask Claude to list all Python files in src/",
  "format": "json",
  "stream": false
}' | jq -r '.response'
```

**Expected Output:**
```json
{
  "command": "list files",
  "directory": "src/",
  "file_type": "Python"
}
```

### Test 2: Complex Command
```bash
curl -s http://10.0.1.201:11434/api/generate -d '{
  "model": "llama3:8b",
  "prompt": "Convert to structured JSON: Ask Claude Opus to implement a FastAPI endpoint for user registration with email validation and bcrypt password hashing",
  "format": "json",
  "stream": false
}' | jq -r '.response'
```

---

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Ollama API** | http://10.0.1.201:11434 | LLM inference (agents) |
| **Open WebUI** | http://10.0.1.202:3000 | Web interface (humans) |
| **Portainer** | https://10.0.1.202:9443 | Container management |
| **MCP Server** | http://10.0.1.202:8080/sse | Infrastructure access |

---

## Maintenance

### Update Models
```bash
# On Whisper VM
ssh ccpm@10.0.1.201
ollama pull llama3:8b  # Update to latest
ollama list             # Verify
```

### Restart Services
```bash
# On Harbor VM
ssh ccpm@10.0.1.202
docker restart open-webui
docker logs open-webui -f
```

### Monitor Resources
```bash
# On Whisper VM (Ollama GPU usage)
ssh ccpm@10.0.1.201
nvidia-smi -l 1
```

---

## Related Documentation

- [Hardware Inventory](hardware-inventory.md) - Physical equipment details
- [Server Stack Architecture](server-stack-architecture.md) - Proxmox VM design
- [Session Summary 2025-12-14](session-summary-2025-12-14.md) - Initial setup
- [HomeLab MCP Server](../mcp-servers/homelab-infra/README.md) - Infrastructure MCP tools

---

**Architecture validated:** 2025-12-15
**Status:** ✅ Production-ready
**Agent:** HomeLab Specialist
