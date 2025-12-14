# HomeLab Agent Rules

**Version:** 1.0.0
**Applies To:** All HomeLab agents

---

## Golden Rules

### Rule 1: Documentation First

Before making infrastructure changes:
- Document the current state
- Document the planned change
- Document the expected outcome

### Rule 2: Safety First

For SCPI/equipment control:
- NEVER enable outputs without explicit user confirmation
- ALWAYS verify settings before applying
- ALWAYS timeout network commands
- LOG all equipment interactions

### Rule 3: Use CCPM for Task Tracking

All significant work should be tracked:
```bash
# Check for existing task
curl -s "http://localhost:8080/api/todos?project_id=5" | jq .

# Create task if needed
curl -X POST "http://localhost:8080/api/todos" \
  -H "Content-Type: application/json" \
  -d '{"project_id": 5, "title": "...", "description": "..."}'
```

### Rule 4: Git All Changes

All documentation and code changes must be committed:
```bash
git add -A
git commit -m "Description of change"
git push
```

### Rule 5: Update Inventory

When hardware changes (added, removed, moved, broken):
- Update `docs/hardware-inventory.md`
- Commit the change
- Note in session summary if applicable

### Rule 6: Session Summaries

For significant sessions, create a summary:
- `docs/session-summary-YYYY-MM-DD.md`
- Include decisions made, changes done, next steps

### Rule 7: Use MCP Tools

Leverage available MCP tools:
- **Context7**: For library/tool documentation lookup
- **UniFi MCP**: For network visibility (when configured)
- **Future MCPs**: SCPI, Home Assistant, etc.

---

## Task Lifecycle (CCPM Workflow Enforcement)

**IMPORTANT:** CCPM enforces strict workflow progression via database triggers (Migration 047).
You CANNOT skip workflow steps. Follow this exact sequence:

### Standard Task Workflow

1. **Start Work:**
   - Task begins in `status:todo`
   - Update to `status:in-progress` when starting
   - OR mark first workflow step as complete

2. **Complete Work:**
   - Update to `status:review` when work done
   - Submit test evidence: `POST /api/todos/:id/tests`
   - Include: test_type, environment, result, evidence (JSON)

3. **Get Approval:**
   - Test must be approved before completion
   - Check test status: `GET /api/todos/:id/tests`
   - Wait for `status: "approved"`

4. **Submit Completion Report:**
   - Document deliverables, testing, next steps
   - POST to `/api/todos/:id/report`

5. **Mark Complete:**
   - Use Human endpoint: `POST /api/human/todos/:id/complete`
   - Task transitions: `status:testing` → `status:complete`
   - Signal completion: `bash .claude/master/signal-completion.sh`
   - Update GitHub issue if linked

### Workflow States
```
status:todo → status:in-progress → status:review → status:testing → status:complete
```

**Never skip states.** Workflow triggers will block invalid transitions.

---

## Communication

### With User (Director)

- Be concise but complete
- Present options when decisions needed
- Confirm before destructive actions
- Use tables for structured data

### Status Updates

Provide clear status at session start:
```
## System Status
- CCPM: OK/DOWN
- Equipment: X/6 online
- Last session: YYYY-MM-DD
```

---

## File Organization

| Path | Purpose |
|------|---------|
| `docs/` | All documentation |
| `infrastructure/` | IaC configs |
| `scripts/` | Automation scripts |
| `ai-models/` | AI/ML configs |
| `.claude/` | Agent system |

---

## Prohibited Actions

1. **DO NOT** push to main without explicit approval for destructive changes
2. **DO NOT** enable SCPI outputs without user confirmation
3. **DO NOT** make changes to CCPM core (use CCPM agents for that)
4. **DO NOT** store secrets in git
5. **DO NOT** ignore errors silently

---

## Emergency Procedures

### If Equipment Doesn't Respond

1. Check network connectivity: `ping 10.0.1.X`
2. Check port: `nc -zv 10.0.1.X PORT`
3. Report to user
4. Do NOT retry indefinitely

### If CCPM Server Down

1. Note in session
2. Continue work locally
3. Sync with CCPM when restored

---

*These rules ensure safe, documented, and traceable HomeLab operations.*
