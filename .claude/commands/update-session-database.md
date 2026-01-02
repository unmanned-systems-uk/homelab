# Update Session Database

Mid-session database dump - save current progress to database without ending the session.

## Database Configuration

**TWO DATABASES - DON'T CONFUSE THEM:**

| Database | Purpose | Use For |
|----------|---------|---------|
| `homelab_db` | Infrastructure data | Devices, credentials, equipment queries |
| `ccpm_db` | Session reports | EOD reports, session_commits |

### Session Reports Database: `ccpm_db`

| Parameter | Value |
|-----------|-------|
| Host | 10.0.1.251 |
| Port | 5433 |
| Database | `ccpm_db` |
| User | ccpm |
| Password | CcpmDb2025Secure |
| Agent ID | `aaaaaaaa-bbbb-cccc-dddd-222222222222` |
| Agent Tag | `[HomeLab]` |

---

## Purpose

Use this command to:
- Save session progress mid-work (checkpoints)
- Update session with new accomplishments
- Record blockers or issues as they occur
- Create recovery point before risky operations

---

## STEP 1: Check for Existing Session Today

```bash
SESSION_DATE=$(date +%Y-%m-%d)
echo "=== Checking for existing session ==="
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c \
  "SELECT id, status, commits_made, files_modified, created_at
   FROM session_reports
   WHERE agent_tag='[HomeLab]' AND session_date='$SESSION_DATE'
   ORDER BY created_at DESC LIMIT 1;"
```

---

## STEP 2: Gather Current Metrics

```bash
SESSION_DATE=$(date +%Y-%m-%d)
echo "=== Current Session Metrics ==="

COMMITS=$(git log --since="$SESSION_DATE 00:00:00" --oneline 2>/dev/null | wc -l)
echo "Commits: $COMMITS"

FILES=$(git log --since="$SESSION_DATE 00:00:00" --name-only --pretty="" 2>/dev/null | sort -u | grep -v '^$' | wc -l)
echo "Files modified: $FILES"

TASKS=$(gh issue list --repo unmanned-systems-uk/homelab --state all --limit 20 --json updatedAt --jq '[.[] | select(.updatedAt | fromdateiso8601 > (now - 86400))] | length' 2>/dev/null || echo "0")
echo "GitHub tasks touched: $TASKS"

echo ""
echo "=== Recent Commits ==="
git log --since="$SESSION_DATE 00:00:00" --oneline 2>/dev/null | head -5
```

---

## STEP 3A: Create New Session (if none exists today)

```bash
SESSION_DATE=$(date +%Y-%m-%d)
SESSION_NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Get metrics
COMMITS=$(git log --since="$SESSION_DATE 00:00:00" --oneline 2>/dev/null | wc -l)
FILES=$(git log --since="$SESSION_DATE 00:00:00" --name-only --pretty="" 2>/dev/null | sort -u | grep -v '^$' | wc -l)
TASKS=$(gh issue list --repo unmanned-systems-uk/homelab --state all --limit 20 --json updatedAt --jq '[.[] | select(.updatedAt | fromdateiso8601 > (now - 86400))] | length' 2>/dev/null || echo "0")

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
    NULL,
    0,
    'draft',
    'HomeLab session in progress - $COMMITS commits so far',
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    'Session in progress',
    $TASKS, 0, $FILES, $COMMITS, 0, 0, NOW(), NOW()
) RETURNING id, session_date, status;
EOF

echo "New session created"
```

---

## STEP 3B: Update Existing Session

```bash
SESSION_DATE=$(date +%Y-%m-%d)
SESSION_NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Get metrics
COMMITS=$(git log --since="$SESSION_DATE 00:00:00" --oneline 2>/dev/null | wc -l)
FILES=$(git log --since="$SESSION_DATE 00:00:00" --name-only --pretty="" 2>/dev/null | sort -u | grep -v '^$' | wc -l)
TASKS=$(gh issue list --repo unmanned-systems-uk/homelab --state all --limit 20 --json updatedAt --jq '[.[] | select(.updatedAt | fromdateiso8601 > (now - 86400))] | length' 2>/dev/null || echo "0")

PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db << EOF
UPDATE session_reports
SET
    commits_made = $COMMITS,
    files_modified = $FILES,
    total_tasks_touched = $TASKS,
    summary = 'HomeLab session in progress - $COMMITS commits, $FILES files modified',
    updated_at = NOW()
WHERE agent_tag = '[HomeLab]'
  AND session_date = '$SESSION_DATE'
  AND id = (SELECT id FROM session_reports WHERE agent_tag='[HomeLab]' AND session_date='$SESSION_DATE' ORDER BY created_at DESC LIMIT 1)
RETURNING id, session_date, commits_made, files_modified, updated_at;
EOF

echo "Session updated"
```

---

## STEP 4: Sync Recent Commits

Add any new commits since last sync:

```bash
SESSION_DATE=$(date +%Y-%m-%d)

# Get the session report ID
REPORT_ID=$(PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -t -c \
  "SELECT id FROM session_reports WHERE agent_tag='[HomeLab]' AND session_date='$SESSION_DATE' ORDER BY created_at DESC LIMIT 1;" | tr -d ' ')

echo "Syncing commits to session: $REPORT_ID"

# Insert each commit (ON CONFLICT prevents duplicates)
git log --since="$SESSION_DATE 00:00:00" --pretty=format:"%h|%s|%aI" 2>/dev/null | while IFS='|' read hash msg timestamp; do
  PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c \
    "INSERT INTO session_commits (session_report_id, commit_sha, commit_message, commit_author, branch_name, committed_at, files_changed, insertions, deletions)
     VALUES ('$REPORT_ID', '$hash', '$(echo "$msg" | sed "s/'/''/g")', 'HomeLab-Agent', 'main', '$timestamp', 0, 0, 0)
     ON CONFLICT DO NOTHING;" 2>/dev/null
done

# Show commit count
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c \
  "SELECT COUNT(*) as commits_logged FROM session_commits WHERE session_report_id = '$REPORT_ID';"
```

---

## STEP 5: Update with Narrative (Optional)

If you want to add narrative context, use this template:

```bash
SESSION_DATE=$(date +%Y-%m-%d)

# Update with narrative (replace SUMMARY, IN_PROGRESS, BLOCKERS with actual content)
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db << 'EOF'
UPDATE session_reports
SET
    summary = 'YOUR SUMMARY HERE',
    in_progress_items = '["Current task 1", "Current task 2"]'::jsonb,
    blockers = '["Blocker 1 if any"]'::jsonb,
    updated_at = NOW()
WHERE agent_tag = '[HomeLab]'
  AND session_date = 'SESSION_DATE'
  AND id = (SELECT id FROM session_reports WHERE agent_tag='[HomeLab]' AND session_date='SESSION_DATE' ORDER BY created_at DESC LIMIT 1);
EOF
```

---

## Quick One-Liner (Metrics Only)

For a fast checkpoint without narrative:

```bash
SESSION_DATE=$(date +%Y-%m-%d) && COMMITS=$(git log --since="$SESSION_DATE 00:00:00" --oneline 2>/dev/null | wc -l) && FILES=$(git log --since="$SESSION_DATE 00:00:00" --name-only --pretty="" 2>/dev/null | sort -u | grep -v '^$' | wc -l) && PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c "UPDATE session_reports SET commits_made=$COMMITS, files_modified=$FILES, updated_at=NOW() WHERE agent_tag='[HomeLab]' AND session_date='$SESSION_DATE' RETURNING id, commits_made, files_modified;"
```

---

## Verification

```bash
SESSION_DATE=$(date +%Y-%m-%d)
echo "=== Current Session State ==="
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c \
  "SELECT id, status, commits_made, files_modified, total_tasks_touched,
          to_char(updated_at, 'HH24:MI:SS') as last_updated
   FROM session_reports
   WHERE agent_tag='[HomeLab]' AND session_date='$SESSION_DATE'
   ORDER BY created_at DESC LIMIT 1;"
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

*HomeLab Agent - Mid-session database checkpoint*
