# CCPM V2 Messaging Patterns

**For:** All HomeLab agents
**Version:** 1.0.0

---

## Core Principle

**ALL inter-agent communication MUST use CCPM V2 messaging API.**

No direct calls, no shared state, no file-based communication between agents.

---

## API Endpoint

```
Base URL: http://10.0.1.210:8000/api/v1
```

---

## Agent UUIDs

| Agent | UUID |
|-------|------|
| HL-Master | `11111111-aaaa-bbbb-cccc-000000000001` |
| HL-Network | `11111111-aaaa-bbbb-cccc-000000000002` |
| HL-SCPI | `11111111-aaaa-bbbb-cccc-000000000003` |
| HL-Infra | `11111111-aaaa-bbbb-cccc-000000000004` |
| HL-Home | `11111111-aaaa-bbbb-cccc-000000000005` |
| HL-AI | `11111111-aaaa-bbbb-cccc-000000000006` |
| HL-Gate | `11111111-aaaa-bbbb-cccc-000000000007` |
| Human (Anthony) | `7563bfda-6e47-4e50-b37a-90ccdc47311a` |
| V2-Master | `4c714f40-d15c-4f0e-bb34-410f2e7e1806` |
| BROADCAST | `ffffffff-ffff-ffff-ffff-ffffffffffff` |

---

## Message Types

| Type | Purpose | Priority |
|------|---------|----------|
| `task` | Task assignment | high/normal |
| `info` | Status update, completion | normal |
| `query` | Question, needs response | high |
| `alert` | Critical issue | critical |
| `broadcast` | Announcement to all | normal |

---

## Pattern 1: Task Assignment (Master → Specialist)

**When:** HL-Master delegates work to a specialist agent

```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "11111111-aaaa-bbbb-cccc-000000000002",
    "message_type": "task",
    "subject": "Network Scan Required",
    "body": "Scan 10.0.1.0/24 subnet and report:\n- Total devices\n- Offline devices\n- New devices (not in database)\n\nUser request: Find all offline network devices",
    "priority": "high",
    "metadata": {
      "user_request": "Find all offline network devices",
      "task_id": "HL-TASK-2026-01-13-001"
    }
  }'
```

**Response:** Task ID returned

---

## Pattern 2: Task Acceptance (Specialist → Master)

**When:** Specialist acknowledges task and begins work

```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000002" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "11111111-aaaa-bbbb-cccc-000000000001",
    "message_type": "info",
    "subject": "Task HL-TASK-2026-01-13-001 Started",
    "body": "Network scan initiated. ETA: 5 minutes.",
    "priority": "normal",
    "metadata": {
      "task_id": "HL-TASK-2026-01-13-001",
      "status": "in_progress"
    }
  }'
```

---

## Pattern 3: Task Completion (Specialist → Master)

**When:** Specialist finishes assigned work

```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000002" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "11111111-aaaa-bbbb-cccc-000000000001",
    "message_type": "info",
    "subject": "Task HL-TASK-2026-01-13-001 Complete",
    "body": "Network scan complete.\n\nResults:\n- Total devices: 47\n- Offline: 3 (10.0.1.112, 10.0.1.130, 10.0.1.155)\n- New devices: 1 (10.0.1.203)\n\nAction required: Investigate 10.0.1.203 (unknown device).",
    "priority": "normal",
    "metadata": {
      "task_id": "HL-TASK-2026-01-13-001",
      "status": "completed",
      "duration_minutes": 4,
      "results": {
        "total_devices": 47,
        "offline": ["10.0.1.112", "10.0.1.130", "10.0.1.155"],
        "new_devices": ["10.0.1.203"]
      }
    }
  }'
```

---

## Pattern 4: Query Human (Any Agent → Human)

**When:** Agent needs clarification or approval

```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=<AGENT_UUID>" \
  -H "Content-Type: application/json" \
  -d '{
    "to_user_id": "7563bfda-6e47-4e50-b37a-90ccdc47311a",
    "message_type": "query",
    "subject": "Approval Required: Enable PSU Output",
    "body": "Task requires enabling PSU-1 output with:\n- Voltage: 12V\n- Current Limit: 2A\n\nApprove?",
    "priority": "high",
    "metadata": {
      "requires_approval": true,
      "task_id": "HL-TASK-2026-01-13-005"
    }
  }'
```

---

## Pattern 5: Alert (Any Agent → Master + Human)

**When:** Critical issue detected

```bash
# To Master
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000002" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "11111111-aaaa-bbbb-cccc-000000000001",
    "message_type": "alert",
    "subject": "CRITICAL: UDM Pro Unreachable",
    "body": "UDM Pro (10.0.1.1) not responding to ping. Network may be down.",
    "priority": "critical"
  }'

# To Human
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000002" \
  -H "Content-Type: application/json" \
  -d '{
    "to_user_id": "7563bfda-6e47-4e50-b37a-90ccdc47311a",
    "message_type": "alert",
    "subject": "CRITICAL: UDM Pro Unreachable",
    "body": "UDM Pro (10.0.1.1) not responding. Immediate attention required.",
    "priority": "critical"
  }'
```

---

## Pattern 6: Broadcast (Master → All)

**When:** Announcement to all agents

```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
    "message_type": "broadcast",
    "subject": "Session EOD in 30 minutes",
    "body": "Finish current tasks and prepare session reports.",
    "priority": "normal"
  }'
```

---

## Pattern 7: Check Inbox (On Startup)

**When:** Agent starts or user runs `/check-messages`

```bash
# Get unread messages
curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=<AGENT_UUID>&status=unread" | jq

# Get all messages (last 24h)
curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=<AGENT_UUID>&limit=50" | jq
```

---

## Pattern 8: Mark Message Read

**When:** Agent processes a message

```bash
# Mark specific message as read
curl -X PUT "http://10.0.1.210:8000/api/v1/agent-messages/<MESSAGE_ID>/read" \
  -H "Content-Type: application/json"
```

---

## Best Practices

### For Specialists
1. **Check inbox on startup** - Process any pending tasks
2. **Acknowledge tasks immediately** - Send "task started" message
3. **Report completion** - Always send results back to Master
4. **Alert on failures** - Don't fail silently
5. **Include metadata** - Task IDs, durations, results

### For HL-Master
1. **Track task IDs** - Use unique identifiers (HL-TASK-YYYY-MM-DD-NNN)
2. **Route by domain** - Use keyword matching
3. **Aggregate results** - Combine specialist reports
4. **Monitor timeouts** - Alert if specialist doesn't respond in reasonable time
5. **Session reporting** - Include delegated task summary

### Message Structure
```json
{
  "to_agent_id": "uuid-here",
  "message_type": "task|info|query|alert|broadcast",
  "subject": "Clear, concise subject (< 80 chars)",
  "body": "Detailed message body. Can be multi-line.\n\nUse markdown for formatting.",
  "priority": "critical|high|normal|low",
  "metadata": {
    "task_id": "HL-TASK-2026-01-13-001",
    "status": "in_progress|completed|failed",
    "any_custom_field": "value"
  }
}
```

---

## Error Handling

### Network Timeout
```bash
# Use timeout for all API calls
timeout 5 curl -X POST ... || echo "CCPM API unreachable - fallback to local logging"
```

### Failed Task
```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=<AGENT_UUID>" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "11111111-aaaa-bbbb-cccc-000000000001",
    "message_type": "alert",
    "subject": "Task HL-TASK-2026-01-13-001 Failed",
    "body": "Network scan failed: Permission denied on 10.0.1.100\n\nError: Connection refused",
    "priority": "high",
    "metadata": {
      "task_id": "HL-TASK-2026-01-13-001",
      "status": "failed",
      "error": "Connection refused"
    }
  }'
```

---

## Quick Reference Commands

```bash
# Check inbox
curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=<UUID>&status=unread"

# Send task
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=<FROM_UUID>" \
  -H "Content-Type: application/json" \
  -d '{"to_agent_id":"<TO_UUID>","message_type":"task","subject":"...","body":"...","priority":"normal"}'

# Send to human
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=<UUID>" \
  -H "Content-Type: application/json" \
  -d '{"to_user_id":"7563bfda-6e47-4e50-b37a-90ccdc47311a","message_type":"query","subject":"...","body":"...","priority":"high"}'

# Broadcast
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=<UUID>" \
  -H "Content-Type: application/json" \
  -d '{"to_agent_id":"ffffffff-ffff-ffff-ffff-ffffffffffff","message_type":"broadcast","subject":"...","body":"...","priority":"normal"}'
```

---

*All HomeLab agents must follow these patterns. No exceptions.*
