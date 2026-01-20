# HomeLab Specialist Agents Directory

**Version:** 1.0.0
**For:** HL-Master reference

---

## Quick Reference

| Agent | UUID (last 4) | Startup | Domain | MCPs | Status |
|-------|---------------|---------|---------|------|--------|
| HL-Master | ...0001 | `/hl-master` | Orchestration | None | Active |
| HL-Network | ...0002 | `/hl-network` | Network | UniFi | Active |
| HL-SCPI | ...0003 | `/hl-scpi` | Test Equipment | None | Active |
| HL-Infra | ...0004 | `/hl-infra` | Infrastructure | None | Active |
| HL-Home | ...0005 | `/hl-home` | Home Automation | Home Assistant | Active |
| HL-AI | ...0006 | `/hl-ai` | AI/ML | None | Active |
| HL-Gate | ...0007 | `/hl-gate` | HomeGate Project | None | Active |

---

## Full UUIDs

```
HL-Master:  11111111-aaaa-bbbb-cccc-000000000001
HL-Network: 11111111-aaaa-bbbb-cccc-000000000002
HL-SCPI:    11111111-aaaa-bbbb-cccc-000000000003
HL-Infra:   11111111-aaaa-bbbb-cccc-000000000004
HL-Home:    11111111-aaaa-bbbb-cccc-000000000005
HL-AI:      11111111-aaaa-bbbb-cccc-000000000006
HL-Gate:    11111111-aaaa-bbbb-cccc-000000000007
```

---

## HL-Network (Network Infrastructure)

**UUID:** `11111111-aaaa-bbbb-cccc-000000000002`
**Startup:** `/hl-network`
**Working Dir:** `/home/homelab/HomeLab`

**Capabilities:**
- UniFi management (UDM Pro @ 10.0.1.1)
- VLAN configuration
- Firewall rule management
- Client tracking
- Network topology
- Connectivity troubleshooting

**MCPs:** UniFi MCP (~4k tokens)
**Context:** ~44k tokens at startup

**When to Delegate:**
- Network configuration changes
- UniFi device management
- Client connectivity issues
- Firewall rules
- VLAN design

---

## HL-SCPI (Test Equipment)

**UUID:** `11111111-aaaa-bbbb-cccc-000000000003`
**Startup:** `/hl-scpi`
**Working Dir:** `/home/homelab/HomeLab`

**Capabilities:**
- SCPI instrument control (6 devices)
- Automated measurements
- Test data logging
- Equipment health monitoring
- Calibration tracking

**MCPs:** None (raw socket commands)
**Context:** ~40k tokens at startup

**When to Delegate:**
- Equipment control
- Measurement tasks
- Test automation
- Equipment discovery
- Data logging

**CRITICAL:** Never enable outputs without user approval

---

## HL-Infra (Infrastructure & Virtualization)

**UUID:** `11111111-aaaa-bbbb-cccc-000000000004`
**Startup:** `/hl-infra`
**Working Dir:** `/home/homelab/HomeLab`

**Capabilities:**
- Proxmox VM management
- Docker orchestration
- Ansible automation
- Infrastructure as Code
- Backup management

**MCPs:** None (SSH, APIs, CLI)
**Context:** ~40k tokens at startup

**When to Delegate:**
- VM lifecycle operations
- Container deployment
- Infrastructure automation
- System updates
- Backup/restore

---

## HL-Home (Home Automation)

**UUID:** `11111111-aaaa-bbbb-cccc-000000000005`
**Startup:** `/hl-home`
**Working Dir:** `/home/homelab/homeassistant`

**Capabilities:**
- Home Assistant management
- Device integration
- Automation development
- Scene management
- Energy monitoring

**MCPs:** Home Assistant MCP (~16k tokens)
**Context:** ~56k tokens at startup

**When to Delegate:**
- Home Assistant configuration
- Device integration
- Automation scripts
- Smart home control
- HA troubleshooting

**Note:** Works in separate repo (`unmanned-systems-uk/homeassistant`)

---

## HL-AI (AI/ML Operations)

**UUID:** `11111111-aaaa-bbbb-cccc-000000000006`
**Startup:** `/hl-ai`
**Working Dir:** `/home/homelab/HomeLab`

**Capabilities:**
- GPU workload management
- Model training/deployment
- Ollama LLM services
- Jetson edge deployment
- ML pipeline orchestration

**MCPs:** None (SSH, Docker, CUDA)
**Context:** ~40k tokens at startup

**When to Delegate:**
- GPU passthrough configuration
- Model training
- LLM deployment
- Jetson operations
- ML pipeline work

---

## HL-Gate (HomeGate Project)

**UUID:** `11111111-aaaa-bbbb-cccc-000000000007`
**Startup:** `/hl-gate`
**Working Dir:** `/home/homelab/HomeGate`

**Capabilities:**
- HomeGate development
- GitHub issue implementation
- Frontend/backend development
- Database schema design
- Deployment to i3 host

**MCPs:** None (code development)
**Context:** ~40k tokens at startup

**When to Delegate:**
- HomeGate development ONLY
- HG- issue implementation
- Dashboard features
- SSH terminal work
- Deployment tasks

**Note:** Works in separate repo (`unmanned-systems-uk/homegate`)

---

## Availability Checks

### Check if Agent is Running

```bash
# Check via messaging (send ping)
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "<AGENT_UUID>",
    "message_type": "info",
    "subject": "Ping",
    "body": "Status check",
    "priority": "low"
  }'

# Wait for response (5-10 seconds)
# If no response, agent is offline
```

### Startup Status Check (On HL-Master Startup)

```bash
echo "## Specialist Agents"
echo "HL-Network: Available"
echo "HL-SCPI: Available"
echo "HL-Infra: Available"
echo "HL-Home: Available"
echo "HL-AI: Available"
echo "HL-Gate: Available"
```

(All agents are always "available" as they're on-demand. Not persistent processes.)

---

## Task Delegation Template

```bash
# Generic task delegation
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "<SPECIALIST_UUID>",
    "message_type": "task",
    "subject": "Task Subject (clear, < 80 chars)",
    "body": "Detailed task description.\n\nRequirements:\n- Requirement 1\n- Requirement 2\n\nUser request: Original user message",
    "priority": "normal",
    "metadata": {
      "task_id": "HL-TASK-YYYY-MM-DD-NNN",
      "user_request": "Original user message",
      "estimated_duration": "10 minutes"
    }
  }'
```

---

## Agent Communication Patterns

### HL-Master → Specialist
- Task assignment
- Status queries
- Session EOD notification

### Specialist → HL-Master
- Task acknowledgment
- Status updates
- Task completion
- Error/failure reports

### Specialist → Specialist
**NOT ALLOWED.** All inter-specialist communication must go through HL-Master.

### Any Agent → Human
- Approval requests
- Critical alerts
- Clarification questions

---

## Context Optimization Summary

| Agent | Base Context | MCP Load | Total Context | Free Space |
|-------|--------------|----------|---------------|------------|
| HL-Master | ~40k | 0 | ~40k | 160k (80%) |
| HL-Network | ~40k | 4k | ~44k | 156k (78%) |
| HL-SCPI | ~40k | 0 | ~40k | 160k (80%) |
| HL-Infra | ~40k | 0 | ~40k | 160k (80%) |
| HL-Home | ~40k | 16k | ~56k | 144k (72%) |
| HL-AI | ~40k | 0 | ~40k | 160k (80%) |
| HL-Gate | ~40k | 0 | ~40k | 160k (80%) |

**Savings vs Monolithic:** 16-20k tokens per agent (8-10% of context)

---

*All specialists report to HL-Master. HL-Master coordinates the ecosystem.*
