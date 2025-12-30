# HomeLab Agent Startup

**Agent:** HomeLab
**Working Directory:** `/home/homelab/HomeLab`

---

## STEP 1: Load Identity

You are the **HomeLab** agent managing infrastructure, SCPI equipment, and AI/ML resources.

Read your definition:
```
Read file: .claude/agents/homelab/AGENT.md
Read file: .claude/agents/homelab/DOMAINS.md
```

---

## STEP 2: Load Last Session from Database

Check database for previous session context:

```bash
echo "=== Last Session from Database ==="
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c \
  "SELECT
     session_date,
     status,
     commits_made,
     files_modified,
     total_tasks_touched,
     summary,
     handoff_notes
   FROM session_reports
   WHERE agent_tag = '[HomeLab]'
   ORDER BY session_date DESC, created_at DESC
   LIMIT 1;" 2>/dev/null || echo "Database unavailable - checking markdown fallback"
```

**If database unavailable, check markdown:**

```bash
echo ""
echo "=== Markdown Fallback ==="
LATEST_MD=$(ls -1 docs/session-summary-*.md 2>/dev/null | tail -1)
if [ -n "$LATEST_MD" ]; then
  echo "Found: $LATEST_MD"
  echo ""
  # Show summary section
  sed -n '/^## Summary/,/^## /p' "$LATEST_MD" | head -10
  echo ""
  # Show handoff notes
  sed -n '/^## Handoff/,/^---/p' "$LATEST_MD" | head -10
else
  echo "No previous session found"
fi
```

---

## STEP 3: Check In-Progress Items

Get any in-progress work from last session:

```bash
echo "=== In-Progress Items ==="
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -t -c \
  "SELECT in_progress_items
   FROM session_reports
   WHERE agent_tag = '[HomeLab]'
   ORDER BY session_date DESC, created_at DESC
   LIMIT 1;" 2>/dev/null | python3 -c "import sys,json; items=json.loads(sys.stdin.read().strip() or '[]'); print('\n'.join(f'  - {i}' for i in items) if items else '  None')" 2>/dev/null || echo "  Could not load"

echo ""
echo "=== Blockers ==="
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -t -c \
  "SELECT blockers
   FROM session_reports
   WHERE agent_tag = '[HomeLab]'
   ORDER BY session_date DESC, created_at DESC
   LIMIT 1;" 2>/dev/null | python3 -c "import sys,json; items=json.loads(sys.stdin.read().strip() or '[]'); print('\n'.join(f'  - {i}' for i in items) if items else '  None')" 2>/dev/null || echo "  Could not load"
```

---

## STEP 4: Check GitHub Issues

```bash
echo ""
echo "=== Open GitHub Issues ==="
gh issue list --repo unmanned-systems-uk/homelab --state open --limit 10
```

---

## STEP 5: Equipment Quick Check

Verify SCPI equipment connectivity:

```bash
echo ""
echo "=== SCPI Equipment ==="
for addr in "101:5025" "105:5555" "106:5555" "111:5025" "120:5555" "138:5025"; do
  ip="10.0.1.${addr%:*}"
  port="${addr#*:}"
  timeout 1 bash -c "echo > /dev/tcp/$ip/$port" 2>/dev/null && echo "$ip: UP" || echo "$ip: DOWN"
done
```

---

## STEP 6: Network Quick Check

```bash
echo ""
echo "=== Network Devices ==="
for device in "10.0.1.1:UDM Pro" "10.0.1.200:Proxmox" "10.0.1.251:NAS" "10.0.1.150:Home Assistant"; do
  ip="${device%:*}"
  name="${device#*:}"
  ping -c 1 -W 1 $ip &>/dev/null && echo "$name ($ip): UP" || echo "$name ($ip): DOWN"
done
```

---

## STEP 7: Create/Update Today's Session

Initialize or continue today's session in database:

```bash
SESSION_DATE=$(date +%Y-%m-%d)
echo ""
echo "=== Today's Session ==="

# Check if session exists for today
EXISTS=$(PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -t -c \
  "SELECT COUNT(*) FROM session_reports WHERE agent_tag='[HomeLab]' AND session_date='$SESSION_DATE';" 2>/dev/null | tr -d ' ')

if [ "$EXISTS" = "0" ] 2>/dev/null; then
  echo "Creating new session for $SESSION_DATE"
  PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c \
    "INSERT INTO session_reports (
        id, agent_id, agent_tag, trigger_type, session_date,
        session_started_at, status, summary,
        completed_items, in_progress_items, blockers,
        total_tasks_touched, tasks_completed, files_modified, commits_made,
        tests_run, tests_passed, created_at, updated_at
    ) VALUES (
        gen_random_uuid(),
        'aaaaaaaa-bbbb-cccc-dddd-222222222222',
        '[HomeLab]',
        'manual',
        '$SESSION_DATE',
        NOW(),
        'draft',
        'HomeLab session started',
        '[]'::jsonb, '[]'::jsonb, '[]'::jsonb,
        0, 0, 0, 0, 0, 0, NOW(), NOW()
    ) RETURNING id, session_date, status;" 2>/dev/null || echo "Could not create session"
else
  echo "Continuing existing session for $SESSION_DATE"
  PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c \
    "SELECT id, status, commits_made, files_modified
     FROM session_reports
     WHERE agent_tag='[HomeLab]' AND session_date='$SESSION_DATE'
     ORDER BY created_at DESC LIMIT 1;" 2>/dev/null || echo "Could not query session"
fi
```

---

## STEP 8: Report Ready

Present status to user:

```
# HomeLab Agent Ready

## Last Session
- **Date:** [from database]
- **Status:** [status]
- **Summary:** [summary]
- **Handoff:** [handoff notes]

## In-Progress from Last Session
[list items or "None"]

## Blockers
[list blockers or "None"]

## GitHub Issues
[X open issues - list titles]

## Equipment Status
[X/6 SCPI devices online]

## Key Network
- UDM Pro (10.0.1.1): [UP/DOWN]
- NAS (10.0.1.251): [UP/DOWN]
- Home Assistant (10.0.1.150): [UP/DOWN]

## Today's Session
[Created new / Continuing existing] - ID: [uuid]

---
What would you like to work on?
```

---

## Database Connection Details

| Parameter | Value |
|-----------|-------|
| Host | 10.0.1.251 |
| Port | 5433 |
| Database | ccpm_db |
| User | ccpm |
| Password | CcpmDb2025Secure |
| Agent ID | aaaaaaaa-bbbb-cccc-dddd-222222222222 |
| Agent Tag | [HomeLab] |

---

## MCP Tools Available

| Tool | Purpose |
|------|---------|
| **Context7** | Library documentation |
| **UniFi MCP** | Network visibility (UDM Pro @ 10.0.1.1) |

### Using Context7

```
mcp__context7__resolve-library-id(libraryName: "docker")
mcp__context7__get-library-docs(context7CompatibleLibraryID: "/docker/docs", topic: "compose")
```

---

## Quick Reference

### Key Paths
- Hardware Inventory: `docs/hardware-inventory.md`
- Server Architecture: `docs/server-stack-architecture.md`
- Network Config: `docs/udm-pro-migration-complete.md`

### SCPI Devices
| Device | IP | Port |
|--------|-----|------|
| DMM | 10.0.1.101 | 5025 |
| Load | 10.0.1.105 | 5555 |
| Scope | 10.0.1.106 | 5555 |
| PSU1 | 10.0.1.111 | 5025 |
| AWG | 10.0.1.120 | 5555 |
| PSU2 | 10.0.1.138 | 5025 |

### Session Commands
| Command | Purpose |
|---------|---------|
| `/update-session-database` | Mid-session checkpoint |
| `/eod` | End of day report (DB + MD) |

---

*HomeLab Agent initialized with session context. Awaiting instructions.*
