# HomeLab CCPM Alignment Report

**Date:** 2025-12-14
**Agent:** ccpm-master
**Purpose:** Identify configuration gaps preventing HomeLab from following CCPM workflow

---

## Executive Summary

HomeLab agent is **NOT aligned** with CCPM workflow enforcement system. It has outdated/simplified task management instructions that conflict with the workflow triggers implemented in Migration 047.

**Root Cause:** HomeLab's configuration files predate the CCPM workflow enforcement system and contain a simplified task lifecycle that bypasses required workflow steps.

---

## Critical Gaps Identified

### 1. Missing Workflow Instructions in CLAUDE.md

**Location:** `/home/anthony/ccpm-workspace/HomeLab/CLAUDE.md`

**Missing Sections:**
- ✗ Completion Signaling (`signal-completion.sh`)
- ✗ Testing Requirements (test evidence submission workflow)
- ✗ Workflow state progression (todo → in-progress → review → testing → complete)
- ✗ Workflow Rules API endpoint
- ✗ Test approval workflow

**Production CLAUDE.md includes:**
```bash
## Completion Signaling
bash .claude/master/signal-completion.sh

## Testing Requirements
1. Submit test via POST /api/tasks/:id/tests
2. Get approval via POST /api/tests/:id/approve
3. Test status syncs automatically to task

## Key Endpoints
- Workflow Rules: GET /api/master/workflow-rules
```

### 2. Outdated Task Lifecycle in AGENT_RULES.md

**Location:** `/home/anthony/ccpm-workspace/HomeLab/.claude/common/AGENT_RULES.md` (Line 69-83)

**Current (INCORRECT):**
```
status:todo
    ↓
[Agent sets] status:in-progress
    ↓
[Agent does work]
    ↓
[Agent sets] status:complete (HomeLab is simpler than CCPM core)
```

**Should Be (CORRECT):**
```
status:todo
    ↓
[Agent sets] status:in-progress (via API or workflow step completion)
    ↓
[Agent does work]
    ↓
[Agent sets] status:review
    ↓
[Submit test evidence via POST /api/todos/:id/tests]
    ↓
[Get test approval]
    ↓
[Submit completion report]
    ↓
status:testing (automatic after test approval)
    ↓
[Human/Master approves] status:complete
```

### 3. Missing Claude Code Hooks

**Location:** `/home/anthony/ccpm-workspace/HomeLab/.claude/hooks/`

**Current:** EMPTY directory (0 hooks)

**Production has:**
- `notification.sh` - CRITICAL for CCPM workflow notifications
- `session-init.sh` - Session startup
- `session-end.sh` - Session cleanup
- `post-bash.sh` - Post-command hooks
- `prompt-processor.sh` - Prompt processing
- `agent-stop.sh` - Agent shutdown
- `subagent-stop.sh` - Subagent management

**Impact:** Without `notification.sh`, HomeLab cannot receive CCPM task notifications or workflow events.

### 4. Missing Signal Completion Script

**Expected Location:** `/home/anthony/ccpm-workspace/HomeLab/.claude/master/signal-completion.sh`

**Current:** Does NOT exist

**Purpose:** Notify CCPM Master immediately when tasks complete

---

## Workflow Enforcement Impact

HomeLab tasks will **FAIL** with workflow violations when trying to:
1. Skip from `status:in-progress` directly to `status:complete`
2. Complete tasks without test evidence
3. Complete tasks without workflow step progression

**Example Error (from this session):**
```
Database trigger blocked completion: WORKFLOW_VIOLATION: Cannot skip required workflow steps.
```

---

## Required Actions

### Priority 1: Update AGENT_RULES.md

**File:** `/home/anthony/ccpm-workspace/HomeLab/.claude/common/AGENT_RULES.md`

**Change Line 69-83 from:**
```markdown
## Task Lifecycle

For CCPM-tracked tasks:

status:todo
    ↓
[Agent sets] status:in-progress
    ↓
[Agent does work]
    ↓
[Agent sets] status:complete (HomeLab is simpler than CCPM core)
```

**To:**
```markdown
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

### Workflow States
```
status:todo → status:in-progress → status:review → status:testing → status:complete
```

**Never skip states.** Workflow triggers will block invalid transitions.
```

### Priority 2: Update CLAUDE.md

**File:** `/home/anthony/ccpm-workspace/HomeLab/CLAUDE.md`

**Add these sections after line 65:**

```markdown
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
```

### Priority 3: Install Claude Code Hooks

**Source:** `/home/anthony/ccpm-workspace/production/.claude/hooks/`
**Destination:** `/home/anthony/ccpm-workspace/HomeLab/.claude/hooks/`

**Copy these files:**
```bash
cd /home/anthony/ccpm-workspace/production/.claude/hooks
cp -r notification.sh session-init.sh session-end.sh post-bash.sh \
   /home/anthony/ccpm-workspace/HomeLab/.claude/hooks/
```

**Critical:** The `notification.sh` hook enables CCPM to send task notifications to HomeLab.

### Priority 4: Create Signal Completion Script

**Location:** `/home/anthony/ccpm-workspace/HomeLab/.claude/master/`

**Create directory and script:**
```bash
mkdir -p /home/anthony/ccpm-workspace/HomeLab/.claude/master
cp /home/anthony/ccpm-workspace/production/.claude/master/signal-completion.sh \
   /home/anthony/ccpm-workspace/HomeLab/.claude/master/
```

---

## Testing After Changes

After implementing changes, HomeLab should:

1. ✅ Understand workflow state progression
2. ✅ Submit test evidence before completion
3. ✅ Use signal-completion.sh when done
4. ✅ NOT skip workflow steps
5. ✅ Receive CCPM notifications via hooks

**Test Command:**
```bash
# Assign a test task to HomeLab
curl -X PUT "http://localhost:8080/api/todos/:id" \
  -d '{"assigned_to": "agent:homelab", "status": "status:todo"}'

# HomeLab should:
# 1. Receive notification via hook
# 2. Progress through workflow states correctly
# 3. Submit test evidence
# 4. Signal completion when done
```

---

## Risk Assessment

**Current State:** HIGH RISK
- HomeLab will violate workflow triggers
- Tasks will fail to complete
- Database will block invalid state transitions

**After Fixes:** LOW RISK
- HomeLab aligned with CCPM workflow
- Proper test evidence tracking
- Consistent agent behavior across projects

---

## Summary

HomeLab needs **4 configuration updates** to align with CCPM workflow enforcement:

| Update | File | Priority | Complexity |
|--------|------|----------|------------|
| Task lifecycle rules | AGENT_RULES.md | P1 | Medium |
| Workflow instructions | CLAUDE.md | P2 | Low |
| Install hooks | .claude/hooks/ | P3 | Low |
| Signal script | signal-completion.sh | P4 | Low |

**Estimated Time:** 15-20 minutes to implement all changes

---

*Report generated by ccpm-master for HomeLab CCPM alignment*
