# HomeLab Multi-Agent Architecture

**Version:** 1.0.0
**Created:** 2026-01-13
**Status:** Design Phase

---

## Executive Summary

Transform the monolithic HomeLab agent into a **distributed multi-agent system** with specialized agents for each infrastructure domain. This architecture reduces context usage by 30-40% per agent and enables parallel task execution.

**Key Innovation:** Context-optimized agents that only load the tools and data they need.

---

## Problem Statement

### Current Issues
- **50% context usage at startup** (100k/200k tokens)
- MCP tools consume 20k tokens (10%) - ALL tools loaded regardless of task
- Single agent handles 9 diverse domains
- No task parallelization
- Limited specialization depth

### Context Breakdown (Current Monolithic Agent)
```
System prompt:        3.2k tokens (1.6%)
System tools:        16.1k tokens (8.1%)
MCP tools:           20.0k tokens (10.0%)  ← OPTIMIZATION TARGET
  ├─ Home Assistant: ~16k (20 tools)
  └─ UniFi:          ~4k  (11 tools)
Memory files:         3.4k tokens (1.7%)
Messages:            12.2k tokens (6.1%)
Free space:         100.0k tokens (50.1%)
Autocompact buffer:  45.0k tokens (22.5%)
```

---

## Solution: Specialized Agent System

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      HL-Master                          │
│        (Orchestrator & Session Management)              │
│         - No MCPs (delegates everything)                │
│         - Routes tasks to specialists                   │
│         - Manages session reports                       │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
   │HL-Network│      │ HL-SCPI   │      │HL-Infra │
   │         │      │           │      │         │
   │UniFi MCP│      │ No MCPs   │      │ No MCPs │
   │  (4k)   │      │           │      │         │
   └─────────┘      └───────────┘      └─────────┘
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
   │HL-Home  │      │  HL-AI    │      │HL-Gate  │
   │         │      │           │      │         │
   │ HA MCP  │      │ No MCPs   │      │ No MCPs │
   │ (16k)   │      │           │      │         │
   └─────────┘      └───────────┘      └─────────┘
```

---

## Agent Definitions

### 1. HL-Master (Orchestrator)

**Agent UUID:** `11111111-aaaa-bbbb-cccc-000000000001`
**Startup:** `/hl-master`
**Working Dir:** `/home/homelab/HomeLab`

**Responsibilities:**
- Task routing and delegation
- Session report management (database + markdown)
- Cross-domain coordination
- GitHub issue triage
- Human interface

**MCPs:** None (delegates to specialists)

**Context Budget:** ~40k tokens at startup (30k saved from no MCPs)

**Startup Checklist:**
1. Load identity and routing rules
2. Check last session (database)
3. List GitHub issues (summary only)
4. Check agent availability (ping all specialists)
5. Load in-progress cross-domain tasks

**When to Use:**
- Multi-domain tasks
- Session management
- Task planning and routing
- Status reporting

---

### 2. HL-Network (Network Infrastructure)

**Agent UUID:** `11111111-aaaa-bbbb-cccc-000000000002`
**Startup:** `/hl-network`
**Working Dir:** `/home/homelab/HomeLab`

**Responsibilities:**
- UniFi management (UDM Pro @ 10.0.1.1)
- VLAN configuration
- Firewall rules
- Network topology
- Device connectivity troubleshooting
- Client tracking

**MCPs:** UniFi MCP only (~4k tokens)

**Context Budget:** ~44k tokens at startup (16k saved)

**Key Resources:**
- UniFi controller: `https://10.0.1.1`
- UniFi MCP: `https://mcp.unmanned-systems.uk/sse`
- Database: `network` schema in `homelab_db`

**Startup Checklist:**
1. Load network agent identity
2. Verify UDM Pro connectivity (10.0.1.1)
3. Load UniFi MCP (4k tokens)
4. Check critical device status (UDM Pro, switches, APs)
5. Summary of VLANs and subnets

**When to Use:**
- Network configuration changes
- Firewall rule management
- Client connectivity issues
- VLAN design
- Network monitoring

---

### 3. HL-SCPI (Test Equipment)

**Agent UUID:** `11111111-aaaa-bbbb-cccc-000000000003`
**Startup:** `/hl-scpi`
**Working Dir:** `/home/homelab/HomeLab`

**Responsibilities:**
- SCPI equipment control (6 instruments)
- Automated measurement sequences
- Test data logging
- Equipment discovery and health monitoring
- Calibration tracking

**MCPs:** None (raw socket/netcat commands)

**Context Budget:** ~40k tokens at startup (20k saved)

**Equipment:**
```
10.0.1.101:5025 - Keithley DMM6500
10.0.1.105:5555 - Rigol DL3021A (DC Load)
10.0.1.106:5555 - Rigol MSO8204 (Scope)
10.0.1.111:5025 - Rigol DP932A (PSU-1)
10.0.1.120:5555 - Rigol DG2052 (AWG)
10.0.1.138:5025 - Rigol DP932A (PSU-2)
```

**Database:** `scpi` schema in `homelab_db`

**Startup Checklist:**
1. Load SCPI agent identity
2. Quick equipment scan (ICMP only)
3. Load equipment database (last known states)
4. Check for scheduled measurements

**Safety Rules:**
- NEVER enable outputs without explicit user confirmation
- NEVER apply voltage/current without safety checks
- Always timeout all commands (2-3 seconds max)
- Log all output enable/disable events

**When to Use:**
- Equipment control and measurements
- Automated test sequences
- Equipment calibration
- Test data analysis

---

### 4. HL-Infra (Infrastructure & Virtualization)

**Agent UUID:** `11111111-aaaa-bbbb-cccc-000000000004`
**Startup:** `/hl-infra`
**Working Dir:** `/home/homelab/HomeLab`

**Responsibilities:**
- Proxmox VM management
- Docker container orchestration
- Ansible playbooks
- Infrastructure as Code (IaC)
- Backup management (to NAS)
- System updates and patching

**MCPs:** None (uses SSH, Proxmox API, Docker CLI)

**Context Budget:** ~40k tokens at startup (20k saved)

**Key Systems:**
- Proxmox: `https://10.0.1.200:8006`
- Harbor VM (Docker): `10.0.1.202`
- CCPM V2 VM: `10.0.1.210`
- Whisper/TTS VM: `10.0.1.201`
- Synology NAS: `10.0.1.251`

**Database:** `virtualization` and `infrastructure` schemas in `homelab_db`

**Startup Checklist:**
1. Load infra agent identity
2. Check Proxmox host status (10.0.1.200)
3. List VM states (running/stopped)
4. Check Docker services on Harbor
5. Verify NAS connectivity

**When to Use:**
- VM lifecycle management
- Container deployment
- Infrastructure automation
- Backup and disaster recovery
- System maintenance

---

### 5. HL-Home (Home Automation)

**Agent UUID:** `11111111-aaaa-bbbb-cccc-000000000005`
**Startup:** `/hl-home`
**Working Dir:** `/home/homelab/homeassistant`

**Responsibilities:**
- Home Assistant management (HA-Pi5 @ 10.0.1.150)
- Device integration (Wiz, Zigbee, Z-Wave)
- Automation and scene management
- Voice assistant (Assist)
- Energy monitoring (Emporia)

**MCPs:** Home Assistant MCP only (~16k tokens)

**Context Budget:** ~56k tokens at startup (4k saved)

**Key Systems:**
- Home Assistant: `http://10.0.1.150:8123`
- HA-Pi5 (HAOS 16.3 on NVMe)
- Wiz bulbs: 14 devices on IoT VLAN (10.0.30.x)

**Database:** Home Assistant database (separate)

**GitHub Repo:** `unmanned-systems-uk/homeassistant`

**Startup Checklist:**
1. Load home automation agent identity
2. Verify HA connectivity (10.0.1.150:8123)
3. Load Home Assistant MCP (16k tokens)
4. Check critical device states
5. List pending GitHub issues (HA repo)

**When to Use:**
- Home Assistant configuration
- Device integration and troubleshooting
- Automation development
- Smart home control
- Energy monitoring setup

---

### 6. HL-AI (AI/ML Operations)

**Agent UUID:** `11111111-aaaa-bbbb-cccc-000000000006`
**Startup:** `/hl-ai`
**Working Dir:** `/home/homelab/HomeLab`

**Responsibilities:**
- GPU workload management
- Model training and deployment
- Ollama/LLM services
- Jetson Orin NX deployment
- ML pipeline orchestration

**MCPs:** None (uses SSH, Docker, CUDA)

**Context Budget:** ~40k tokens at startup (20k saved)

**Key Systems:**
- GTX 1080 Ti (11GB VRAM) - VM passthrough ready
- RTX A2000 (6GB VRAM) - Dev machine
- Jetson Orin NX @ 10.0.1.113
- Whisper VM @ 10.0.1.201
- Ollama (Harbor): `https://10.0.1.202:3443`

**Database:** `ai_ml` schema in `homelab_db`

**Startup Checklist:**
1. Load AI/ML agent identity
2. Check GPU availability (Proxmox)
3. Check Jetson connectivity
4. List Ollama models
5. Check GPU utilization

**When to Use:**
- Model training and fine-tuning
- GPU passthrough configuration
- LLM service deployment
- Edge AI (Jetson) deployment
- ML pipeline development

---

### 7. HL-Gate (HomeGate Project)

**Agent UUID:** `11111111-aaaa-bbbb-cccc-000000000007`
**Startup:** `/hl-gate`
**Working Dir:** `/home/homelab/HomeGate`

**Responsibilities:**
- HomeGate project development
- GitHub issue implementation (40 issues in Sprint S1-S4)
- Frontend/backend development
- Database schema design
- Deployment to i3 host @ 10.0.1.50

**MCPs:** None (code development)

**Context Budget:** ~40k tokens at startup (20k saved)

**Key Systems:**
- Deployment host: i3 @ 10.0.1.50
- PostgreSQL: `homelab_db` @ 10.0.1.251:5433
- Cloudflare Tunnel: `homegate.domain.com`

**GitHub Repo:** `unmanned-systems-uk/homegate`

**Startup Checklist:**
1. Load HomeGate project agent identity
2. Check GitHub issues (homegate repo only)
3. Check current sprint progress
4. Verify i3 host connectivity (10.0.1.50)
5. List in-progress issues

**When to Use:**
- HomeGate development only
- Implementing GitHub issues HG-001 through HG-040
- Database schema work
- Frontend/backend development
- Deployment and testing

---

## File Structure

```
/home/homelab/HomeLab/
├── .claude/
│   ├── agents/
│   │   ├── homelab/              # Legacy (deprecated)
│   │   ├── hl-master/            # Master orchestrator
│   │   │   ├── AGENT.md          # Identity and mission
│   │   │   ├── ROUTING.md        # Task routing rules
│   │   │   └── AGENTS.md         # Specialist agent directory
│   │   ├── hl-network/           # Network specialist
│   │   │   ├── AGENT.md
│   │   │   └── NETWORK.md        # UniFi reference
│   │   ├── hl-scpi/              # Test equipment specialist
│   │   │   ├── AGENT.md
│   │   │   └── EQUIPMENT.md      # SCPI reference
│   │   ├── hl-infra/             # Infrastructure specialist
│   │   │   ├── AGENT.md
│   │   │   └── INFRA.md          # Proxmox/Docker reference
│   │   ├── hl-home/              # Home automation specialist
│   │   │   ├── AGENT.md
│   │   │   └── HOME.md           # HA reference
│   │   ├── hl-ai/                # AI/ML specialist
│   │   │   ├── AGENT.md
│   │   │   └── AI.md             # GPU/ML reference
│   │   └── hl-gate/              # HomeGate project specialist
│   │       ├── AGENT.md
│   │       └── PROJECT.md        # HomeGate reference
│   ├── commands/
│   │   ├── hl-master.sh          # Master startup
│   │   ├── hl-network.sh         # Network agent startup
│   │   ├── hl-scpi.sh            # SCPI agent startup
│   │   ├── hl-infra.sh           # Infra agent startup
│   │   ├── hl-home.sh            # Home agent startup
│   │   ├── hl-ai.sh              # AI agent startup
│   │   └── hl-gate.sh            # Gate agent startup
│   ├── skills/
│   │   ├── infrastructure/       # Shared by hl-infra, hl-master
│   │   └── scpi-automation/      # Shared by hl-scpi, hl-master
│   └── common/
│       ├── messaging.md          # CCPM V2 messaging patterns
│       ├── database.md           # Database access (homelab_db)
│       └── session-reports.md    # Session report format
```

---

## MCP Configuration Strategy

### Per-Agent MCP Loading

**Key Insight:** Only load the MCPs each agent needs.

| Agent | MCPs Loaded | Token Cost | Savings |
|-------|-------------|------------|---------|
| HL-Master | None | 0 tokens | -20k |
| HL-Network | UniFi only | ~4k tokens | -16k |
| HL-SCPI | None | 0 tokens | -20k |
| HL-Infra | None | 0 tokens | -20k |
| HL-Home | Home Assistant only | ~16k tokens | -4k |
| HL-AI | None | 0 tokens | -20k |
| HL-Gate | None | 0 tokens | -20k |

**Implementation:**
- Each agent has its own `.claude/mcp-config.json` in its agent directory
- Startup command only loads relevant MCPs
- Context savings: **16-20k tokens per agent** (8-10% of total context)

---

## CCPM V2 Messaging Integration

### All Agents MUST Use Messaging

**Core Principle:** All inter-agent communication goes through CCPM V2 messaging API.

**Message Flow:**
```
Human → HL-Master: "Fix network issue"
HL-Master → HL-Network: Task assignment
HL-Network → HL-Master: Status updates
HL-Master → Human: Task completion
```

### Agent UUIDs (in CCPM database)

```sql
-- Insert all agent UUIDs into agent_registry table
INSERT INTO agent_registry (agent_id, agent_name, agent_type, status) VALUES
('11111111-aaaa-bbbb-cccc-000000000001', 'HL-Master', 'orchestrator', 'active'),
('11111111-aaaa-bbbb-cccc-000000000002', 'HL-Network', 'specialist', 'active'),
('11111111-aaaa-bbbb-cccc-000000000003', 'HL-SCPI', 'specialist', 'active'),
('11111111-aaaa-bbbb-cccc-000000000004', 'HL-Infra', 'specialist', 'active'),
('11111111-aaaa-bbbb-cccc-000000000005', 'HL-Home', 'specialist', 'active'),
('11111111-aaaa-bbbb-cccc-000000000006', 'HL-AI', 'specialist', 'active'),
('11111111-aaaa-bbbb-cccc-000000000007', 'HL-Gate', 'specialist', 'active');
```

### Messaging Patterns

**1. Task Assignment (Master → Specialist)**
```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "11111111-aaaa-bbbb-cccc-000000000002",
    "message_type": "task",
    "subject": "Network Scan Required",
    "body": "Scan 10.0.1.0/24 subnet and report device status",
    "priority": "high"
  }'
```

**2. Status Update (Specialist → Master)**
```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000002" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "11111111-aaaa-bbbb-cccc-000000000001",
    "message_type": "info",
    "subject": "Network Scan Complete",
    "body": "Found 47 devices. 3 offline. Report attached.",
    "priority": "normal"
  }'
```

**3. Human Message (Any Agent → Human)**
```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=<AGENT_UUID>" \
  -H "Content-Type: application/json" \
  -d '{
    "to_user_id": "7563bfda-6e47-4e50-b37a-90ccdc47311a",
    "message_type": "query",
    "subject": "Need clarification",
    "body": "Question about task...",
    "priority": "normal"
  }'
```

**4. Check Inbox (On Every Startup)**
```bash
curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=<AGENT_UUID>&status=unread"
```

---

## Startup Command Design (Minimal Context)

### Goal: < 10k tokens for startup command content

**Bad (Current):** Full equipment lists, full GitHub issues, full database dumps
**Good (New):** Summaries, counts, critical items only

### HL-Master Startup (`/hl-master`)

```bash
#!/bin/bash
# .claude/commands/hl-master.sh

echo "# HL-Master Startup"
echo ""

# 1. Identity (minimal)
echo "## Identity"
echo "Agent: HL-Master (Orchestrator)"
echo "UUID: 11111111-aaaa-bbbb-cccc-000000000001"
echo ""

# 2. Last session (summary only)
echo "## Last Session"
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -t -c \
  "SELECT session_date || ' | ' || status || ' | ' || commits_made || ' commits | ' || summary
   FROM session_reports WHERE agent_tag='[HL-Master]'
   ORDER BY session_date DESC LIMIT 1;" 2>/dev/null
echo ""

# 3. GitHub issues (count only, top 3)
echo "## GitHub Issues"
ISSUE_COUNT=$(gh issue list --repo unmanned-systems-uk/homelab --state open --json number | jq 'length')
echo "Open issues: $ISSUE_COUNT"
gh issue list --repo unmanned-systems-uk/homelab --state open --limit 3 --json number,title,labels | \
  jq -r '.[] | "#\(.number) - \(.title)"'
echo ""

# 4. Check specialist agents (availability)
echo "## Specialist Agents"
echo "HL-Network: Available"
echo "HL-SCPI: Available"
echo "HL-Infra: Available"
echo "HL-Home: Available"
echo "HL-AI: Available"
echo "HL-Gate: Available"
echo ""

# 5. Check messages (unread count)
echo "## Messages"
UNREAD=$(curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=11111111-aaaa-bbbb-cccc-000000000001&status=unread" | jq 'length')
echo "Unread messages: $UNREAD"
echo ""

# 6. Today's session
echo "## Today's Session"
echo "Session initialized. Ready for task routing."
echo ""

echo "What would you like to work on?"
```

**Estimated tokens:** ~3-5k (vs 12k+ for current)

### HL-Network Startup (`/hl-network`)

```bash
#!/bin/bash
# .claude/commands/hl-network.sh

echo "# HL-Network Startup"
echo ""

# 1. Identity
echo "Agent: HL-Network (Network Infrastructure)"
echo "UUID: 11111111-aaaa-bbbb-cccc-000000000002"
echo ""

# 2. Critical device check (minimal)
echo "## Critical Devices"
ping -c 1 -W 1 10.0.1.1 &>/dev/null && echo "UDM Pro: UP" || echo "UDM Pro: DOWN"
echo ""

# 3. UniFi MCP status
echo "## UniFi MCP"
echo "Endpoint: https://mcp.unmanned-systems.uk/sse"
echo "Status: Loading on first use (4k tokens)"
echo ""

# 4. Check messages
UNREAD=$(curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=11111111-aaaa-bbbb-cccc-000000000002&status=unread" | jq 'length')
echo "## Messages: $UNREAD unread"
echo ""

echo "Ready for network tasks."
```

**Estimated tokens:** ~2-3k (plus 4k for UniFi MCP on first use)

---

## Task Routing Rules (HL-Master)

### Routing Decision Tree

```
Task received → Analyze keywords/context → Route to specialist

Keywords:
├─ "network", "vlan", "firewall", "switch", "ap", "client" → HL-Network
├─ "scpi", "dmm", "scope", "awg", "psu", "measurement" → HL-SCPI
├─ "proxmox", "vm", "docker", "ansible", "backup" → HL-Infra
├─ "home assistant", "ha", "smart", "light", "automation" → HL-Home
├─ "gpu", "model", "training", "ollama", "jetson" → HL-AI
├─ "homegate", "hg-", "dashboard" → HL-Gate
└─ Multi-domain or unclear → HL-Master handles directly
```

### Delegation Example

**User:** "Scan the network and find all offline devices"

**HL-Master Logic:**
1. Identify domain: Network
2. Create task message for HL-Network
3. Send via CCPM API
4. Monitor for response
5. Report back to user

---

## Session Report Strategy

### Who Reports What?

**HL-Master:**
- Owns the master session report for the day
- Aggregates reports from all specialists
- Creates unified markdown + database entry

**Specialists:**
- Report task completion to HL-Master via messaging
- Do NOT create their own session reports
- Log work in their messages

**Database Schema:**
```sql
-- Extend session_reports table
ALTER TABLE session_reports ADD COLUMN agent_uuid UUID;
ALTER TABLE session_reports ADD COLUMN delegated_tasks JSONB DEFAULT '[]';

-- Example delegated_tasks structure:
{
  "tasks": [
    {
      "agent": "HL-Network",
      "task": "Network scan",
      "status": "completed",
      "duration_minutes": 15
    }
  ]
}
```

---

## Implementation Plan

### Phase 1: Agent Definitions (2-3 hours)
1. Create agent directories in `.claude/agents/`
2. Write AGENT.md for each specialist
3. Write domain-specific reference docs (NETWORK.md, etc.)
4. Define messaging patterns in `.claude/common/messaging.md`

### Phase 2: Startup Commands (1-2 hours)
1. Create minimal-context startup scripts in `.claude/commands/`
2. Test context usage for each agent
3. Optimize to stay under target budgets

### Phase 3: MCP Configuration (1 hour)
1. Create per-agent MCP configs
2. Test MCP loading for HL-Network and HL-Home
3. Verify context savings

### Phase 4: CCPM Integration (2-3 hours)
1. Register all agent UUIDs in database
2. Test messaging between agents
3. Create routing logic in HL-Master
4. Test end-to-end task delegation

### Phase 5: Testing (2-3 hours)
1. Test each agent independently
2. Test HL-Master task routing
3. Test messaging flows
4. Verify session reporting

**Total Estimated Time:** 8-12 hours

---

## Benefits

### Context Savings
- **Per agent:** 16-20k tokens saved (no unused MCPs)
- **Startup time:** Faster agent initialization
- **Free context:** More room for task work

### Specialization
- **Deeper expertise:** Each agent focuses on one domain
- **Better documentation:** Domain-specific reference docs
- **Faster task completion:** No context switching

### Parallelization
- **Multiple agents:** Work on different domains simultaneously
- **Async messaging:** Non-blocking task delegation
- **Scalability:** Add more specialists as needed

### Maintainability
- **Modular design:** Each agent is independent
- **Clear boundaries:** No domain overlap
- **Easy updates:** Modify one agent without affecting others

---

## Migration Path

### Option A: Clean Break
- Deprecate current `homelab` agent
- Launch all 7 new agents
- User chooses specialist or HL-Master

### Option B: Gradual Transition
- Keep current agent as legacy
- Launch HL-Master first
- Add specialists one at a time
- Migrate tasks gradually

**Recommendation:** Option A (clean break) - cleaner architecture, immediate benefits

---

## Next Steps

1. **Review this design** - Approve architecture and agent definitions
2. **Register agent UUIDs** - Add to CCPM database
3. **Create agent definitions** - Write all AGENT.md files
4. **Build startup commands** - Minimal-context scripts
5. **Test context usage** - Verify savings
6. **Deploy and test** - Full system integration

---

## Appendix: Agent Quick Reference

| Agent | UUID | Startup | MCPs | Context | Primary Domain |
|-------|------|---------|------|---------|----------------|
| HL-Master | ...0001 | /hl-master | None | ~40k | Orchestration |
| HL-Network | ...0002 | /hl-network | UniFi | ~44k | Network |
| HL-SCPI | ...0003 | /hl-scpi | None | ~40k | Test Equipment |
| HL-Infra | ...0004 | /hl-infra | None | ~40k | Proxmox/Docker |
| HL-Home | ...0005 | /hl-home | Home Assistant | ~56k | Home Automation |
| HL-AI | ...0006 | /hl-ai | None | ~40k | AI/ML |
| HL-Gate | ...0007 | /hl-gate | None | ~40k | HomeGate Project |

---

**Status:** Ready for implementation
**Owner:** HL-Master (HomeLab-Agent)
**Review Date:** 2026-01-13
