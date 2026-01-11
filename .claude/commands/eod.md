# End of Day (EOD) Session Report

Generate comprehensive session report and log to BOTH database AND markdown files (belt and braces).

## Database Configuration

**TWO DATABASES - DON'T CONFUSE THEM:**

| Database | Purpose | Use For |
|----------|---------|---------|
| `homelab_db` | Infrastructure data | Devices, credentials, equipment queries |
| `ccpm_db` | Session reports | EOD reports, session_commits |

### Connection Details (Both)

| Parameter | Value |
|-----------|-------|
| Host | 10.0.1.251 |
| Port | 5433 |
| User | ccpm |
| Password | CcpmDb2025Secure |

### Session Reports (ccpm_db)

**Agent ID:** `aaaaaaaa-bbbb-cccc-dddd-222222222222` (HomeLab-Agent)
**Agent Tag:** `[HomeLab]`
**Markdown:** `docs/session-summary-YYYY-MM-DD.md`

---

## STEP 1: Gather Session Metrics

Collect git statistics for the session:

```bash
echo "=== Session Metrics ==="
SESSION_DATE=$(date +%Y-%m-%d)

# Get git statistics since start of day
COMMITS_TODAY=$(git log --since="$SESSION_DATE 00:00:00" --oneline 2>/dev/null | wc -l)
echo "Commits today: $COMMITS_TODAY"

FILES_MODIFIED=$(git log --since="$SESSION_DATE 00:00:00" --name-only --pretty="" 2>/dev/null | sort -u | grep -v '^$' | wc -l)
echo "Files modified: $FILES_MODIFIED"

# Lines added/removed
git log --since="$SESSION_DATE 00:00:00" --numstat --pretty="" 2>/dev/null | awk 'NF==3 {plus+=$1; minus+=$2} END {printf("Lines added: %d\nLines removed: %d\n", plus, minus)}'

# Get commit list
echo ""
echo "=== Commits ==="
git log --since="$SESSION_DATE 00:00:00" --oneline 2>/dev/null | head -10
```

---

## STEP 2: Check GitHub Tasks

```bash
echo ""
echo "=== GitHub Tasks Updated Today ==="
gh issue list --repo unmanned-systems-uk/homelab \
  --state all \
  --limit 20 \
  --json number,title,state,updatedAt \
  --jq '.[] | select(.updatedAt | fromdateiso8601 > (now - 86400)) | "#\(.number): \(.title) [\(.state)]"' 2>/dev/null
```

---

## STEP 3: Check Infrastructure Status

```bash
echo ""
echo "=== Infrastructure Status ==="

# SCPI Equipment
SCPI_UP=0
for addr in "101:5025" "105:5555" "106:5555" "111:5025" "120:5555" "138:5025"; do
  ip="10.0.1.${addr%:*}"
  port="${addr#*:}"
  timeout 1 bash -c "echo > /dev/tcp/$ip/$port" 2>/dev/null && ((SCPI_UP++))
done
echo "SCPI Equipment: $SCPI_UP/6 online"

# Key network devices
NETWORK_UP=0
for ip in "10.0.1.1" "10.0.1.200" "10.0.1.251"; do
  ping -c 1 -W 1 $ip &>/dev/null && ((NETWORK_UP++))
done
echo "Network Devices: $NETWORK_UP/3 online (UDM Pro, Proxmox, NAS)"
```

---

## STEP 4: Write to Database (Primary)

Insert session report directly to PostgreSQL:

```bash
SESSION_DATE=$(date +%Y-%m-%d)
SESSION_END=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Get metrics for SQL
COMMITS=$(git log --since="$SESSION_DATE 00:00:00" --oneline 2>/dev/null | wc -l)
FILES=$(git log --since="$SESSION_DATE 00:00:00" --name-only --pretty="" 2>/dev/null | sort -u | grep -v '^$' | wc -l)
TASKS=$(gh issue list --repo unmanned-systems-uk/homelab --state all --limit 20 --json updatedAt --jq '[.[] | select(.updatedAt | fromdateiso8601 > (now - 86400))] | length' 2>/dev/null || echo "0")

# Insert to database
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db << EOF
INSERT INTO session_reports (
    id, agent_id, agent_tag, trigger_type, session_date,
    session_started_at, session_ended_at, duration_minutes, status,
    summary, completed_items, in_progress_items, blockers, handoff_notes,
    total_tasks_touched, tasks_completed, files_modified, commits_made,
    tests_run, tests_passed, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    'aaaaaaaa-bbbb-cccc-dddd-222222222222',
    '[HomeLab]',
    'manual',
    '$SESSION_DATE',
    '$SESSION_DATE'||'T09:00:00Z',
    '$SESSION_END',
    $(( ($(date +%s) - $(date -d "$SESSION_DATE 09:00:00" +%s)) / 60 )),
    'processed',
    'HomeLab EOD session report - $COMMITS commits, $FILES files modified',
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    'Session complete. Review summary markdown for details.',
    $TASKS, 0, $FILES, $COMMITS, 0, 0, NOW(), NOW()
) RETURNING id, session_date, status;
EOF
```

**Note:** After database insert, gather the session summary, blockers, and handoff notes interactively to update the record or include in markdown.

---

## STEP 5: Write Markdown File (Backup)

Create session summary markdown - this should include the full narrative of what was accomplished:

```bash
SESSION_DATE=$(date +%Y-%m-%d)
cat > docs/session-summary-$SESSION_DATE.md << 'MARKDOWN'
# End of Day Report - {DATE}

## Session Overview
- **Duration:** X hours Y minutes
- **Status:** Completed
- **Database Report ID:** {report_id}

---

## Work Completed

### Git Activity
| Metric | Value |
|--------|-------|
| Commits | X |
| Files Modified | Y |
| Lines Added | +Z |
| Lines Removed | -W |

### Commits Made
```
{commit list}
```

### GitHub Tasks Updated
{list of issues touched}

---

## Infrastructure Status
- **SCPI Equipment:** X/6 online
- **Network Devices:** Y/3 online

---

## Summary
{narrative summary of session accomplishments}

## Blockers / Issues
{any blockers encountered}

## Handoff Notes for Next Session
{priorities and context for next session}

---

*HomeLab Agent - End of Day Report*
*Database: ccpm_db @ 10.0.1.251:5433*
*Generated: {timestamp}*
MARKDOWN
```

**After creating the template, fill in the actual values based on gathered metrics.**

---

## STEP 6: Log Commits to Database

Add individual commits to session_commits table:

```bash
SESSION_DATE=$(date +%Y-%m-%d)

# Get the session report ID we just created
REPORT_ID=$(PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -t -c \
  "SELECT id FROM session_reports WHERE agent_tag='[HomeLab]' AND session_date='$SESSION_DATE' ORDER BY created_at DESC LIMIT 1;")

# Insert each commit
git log --since="$SESSION_DATE 00:00:00" --pretty=format:"%h|%s|%aI" 2>/dev/null | while IFS='|' read hash msg timestamp; do
  PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c \
    "INSERT INTO session_commits (session_report_id, commit_sha, commit_message, commit_author, branch_name, committed_at, files_changed, insertions, deletions)
     VALUES ('$REPORT_ID', '$hash', '$(echo "$msg" | sed "s/'/''/g")', 'HomeLab-Agent', 'main', '$timestamp', 0, 0, 0)
     ON CONFLICT DO NOTHING;" 2>/dev/null
done
```

---

## STEP 7: Skill Knowledge Review

**CRITICAL:** Review session for learnings and update skills.

### Identify What Was Learned:

Ask yourself:
- What problems did we solve?
- What configurations/settings did we discover?
- What tool behaviors did we learn?
- What patterns emerged?

### Common Learning Categories:

**Infrastructure (UniFi, Proxmox, Docker):**
- Network configuration patterns
- Switch/router settings that solved issues
- VM/container best practices discovered

**SCPI Equipment:**
- Instrument command sequences that work
- Timing/timeout patterns
- Measurement techniques

**Database:**
- Query patterns for specific use cases
- Schema design decisions
- Migration techniques

### Add to Skills:

If significant learning occurred:

```bash
# Example: Today we learned UniFi storm control configuration
# Already added to .claude/skills/infrastructure/SKILL.md

# If NOT yet added, do it now:
# Edit appropriate .claude/skills/[skill-name]/SKILL.md
# Add new section with (LEARNED: YYYY-MM-DD)
# Include context, specific values, why it works, when to use
```

### Skill Update Commit Pattern:

```bash
git add .claude/skills/[skill-name]/SKILL.md
git commit -m "skill: Add [topic] to [skill-name]

Learned during [session context/issue].

Added:
- [Specific item 1]
- [Specific item 2]

Reference: docs/session-summary-YYYY-MM-DD.md
"
```

**Note:** If skills were updated during session (proactive), verify they're committed. If not, add now.

---

## STEP 8: Commit Session Summary

```bash
SESSION_DATE=$(date +%Y-%m-%d)
git add docs/session-summary-$SESSION_DATE.md
git commit -m "docs: Add session summary for $SESSION_DATE

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Verification

After EOD, verify both storage locations:

```bash
SESSION_DATE=$(date +%Y-%m-%d)

echo "=== Database Check ==="
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c \
  "SELECT id, session_date, status, commits_made, files_modified FROM session_reports WHERE agent_tag='[HomeLab]' ORDER BY created_at DESC LIMIT 1;"

echo ""
echo "=== Markdown Check ==="
ls -la docs/session-summary-$SESSION_DATE.md 2>/dev/null || echo "Markdown not found"
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

## CC-Share Mount (if needed)

```bash
# Mount CC-Share for shared access
echo "053210" | sudo -S mount -t cifs //10.0.1.251/CC-Share /mnt/cc-share \
  -o username=homelab-agent,password=Homelab053210,uid=1000,gid=1000

# Copy report to share
cp docs/session-summary-$(date +%Y-%m-%d).md /mnt/cc-share/
```

---

*HomeLab Agent - End of Day reporting with database + markdown backup*
