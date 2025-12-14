# CLAUDE.md - HomeLab Agent Instructions

## Project
- **Repo:** `unmanned-systems-uk/homelab`
- **Project ID:** 5
- **Working Directory:** `/home/anthony/ccpm-workspace/HomeLab`
- **Stack:** Infrastructure as Code, Docker, AI/ML tooling, Proxmox

## HomeLab Specialist Agent

**To activate the full agent context, run:**
```
/start-homelab
```

This loads the complete agent definition with:
- Full capability set
- SCPI equipment access
- MCP tool integration
- Session startup checklist

### Agent Identity
- **WHO Tag:** `[HL-Specialist]`
- **Definition:** `.claude/agents/homelab-specialist/AGENT_DEFINITION.md`
- **Rules:** `.claude/common/AGENT_RULES.md`

---

## Project Focus

HomeLab is a versatile home lab infrastructure project with emphasis on:
- AI/ML model development and training environments
- CCPM project management integration
- Infrastructure automation and deployment (Proxmox, Docker)
- Test equipment automation (SCPI)
- Network management (UniFi)

---

## Critical Rules

1. **NEVER close GitHub issues** - User closes issues
2. **Use `gh` CLI** for GitHub (not API tokens)
3. **Correct repo:** `unmanned-systems-uk/homelab`
4. **Test infrastructure changes** before committing
5. **Document all hardware/network configs** in `/docs`
6. **NEVER enable SCPI outputs** without explicit user confirmation
7. **TIMEOUT all network commands** (2-3 seconds max)

---

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/start-homelab` | Load full agent context |
| `/homelab-status` | Quick system status check |
| `/scpi-scan` | Scan SCPI equipment |
| `/network-scan` | Scan 10.0.1.x subnet |

---

## CCPM Workflow Compliance

HomeLab tasks use the same workflow enforcement as all CCPM agents.

### Query Workflow Rules
```bash
curl -s http://localhost:8080/api/master/workflow-rules | jq .
```

### Completion Signaling
When you complete tasks, signal Master immediately:
```bash
bash .claude/master/signal-completion.sh
```

### Testing Requirements
All tasks require test evidence before completion:
1. Submit test: `POST /api/todos/:id/tests` with evidence
2. Get approval: `POST /api/tests/:id/approve` (or wait for human approval)
3. Test status syncs automatically to task

### Task Status API
```bash
# Update task status
curl -X PUT "http://localhost:8080/api/todos/:id" \
  -H "Content-Type: application/json" \
  -d '{"status": "status:in-progress"}'

# Submit test evidence
curl -X POST "http://localhost:8080/api/todos/:id/tests" \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "manual_technical",
    "tested_by": "agent:homelab",
    "environment": "production",
    "result": "pass",
    "evidence": {...}
  }'

# Submit completion report
curl -X POST "http://localhost:8080/api/todos/:id/report" \
  -H "Content-Type: application/json" \
  -d '{"report": "..."}'

# Complete task (after test approved)
curl -X POST "http://localhost:8080/api/human/todos/:id/complete" \
  -H "X-Actor: human:master"
```

---

## Quick Commands

```bash
# CCPM API
curl -s http://localhost:8080/api/health | jq .
curl -s http://localhost:8080/api/projects/5 | jq .
curl -s "http://localhost:8080/api/sprints?project_id=5" | jq .
curl -s "http://localhost:8080/api/todos?project_id=5" | jq .

# GitHub
gh issue list --repo unmanned-systems-uk/homelab
gh issue create --repo unmanned-systems-uk/homelab --title "Title" --body "Body"

# Quick SCPI check
echo "*IDN?" | nc -w 2 10.0.1.101 5025
```

---

## Directory Structure

```
HomeLab/
├── docs/               # Documentation, hardware inventory
│   ├── hardware-inventory.md
│   ├── server-stack-architecture.md
│   ├── learning-hub.md
│   └── unifi-mcp-integration.md
├── infrastructure/     # IaC configs (Docker, Ansible, Proxmox)
├── scripts/            # Automation scripts
├── ai-models/          # AI/ML configurations
└── .claude/            # Agent system
    ├── agents/         # Agent definitions
    ├── commands/       # Slash commands
    ├── skills/         # Skills (infrastructure, scpi-automation)
    ├── common/         # Shared rules
    └── hooks/          # Claude Code hooks
```

---

## SCPI Equipment (10.0.1.x)

| Device | IP | Port | Model |
|--------|-----|------|-------|
| DMM | 10.0.1.101 | 5025 | Keithley DMM6500 |
| Scope | 10.0.1.106 | 5555 | Rigol MSO8204 |
| AWG | 10.0.1.120 | 5555 | Rigol DG2052 |
| DC Load | 10.0.1.105 | 5555 | Rigol DL3021A |
| PSU 1 | 10.0.1.111 | 5025 | Rigol DP932A |
| PSU 2 | 10.0.1.138 | 5025 | Rigol DP932A |

---

## MCP Tools Available

| Tool | Purpose |
|------|---------|
| **Context7** | Library documentation lookup |
| **UniFi MCP** | Network visibility (planned) |

### Using Context7

```
# Resolve library ID first
mcp__context7__resolve-library-id(libraryName: "docker")

# Then fetch docs
mcp__context7__get-library-docs(context7CompatibleLibraryID: "/docker/docs", topic: "compose")
```

---

## Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| infrastructure | `.claude/skills/infrastructure/` | Proxmox, Docker, networking |
| scpi-automation | `.claude/skills/scpi-automation/` | Test equipment control |

---

## WHO Tags

| Tag | Domain |
|-----|--------|
| `[HL-Specialist]` | Main agent |
| `[HL-Infra]` | Infrastructure tasks |
| `[HL-AI]` | AI/ML tasks |
| `[HL-Network]` | Network tasks |
| `[HL-SCPI]` | Test equipment |
| `[HL-Docs]` | Documentation |

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/hardware-inventory.md` | All equipment |
| `docs/server-stack-architecture.md` | Proxmox/VM design |
| `docs/learning-hub.md` | AI/ML resources |
| `docs/session-summary-*.md` | Session records |

---

*HomeLab Specialist Agent - Managed via CCPM Project ID 5*
