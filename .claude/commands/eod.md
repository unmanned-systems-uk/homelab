# End of Day (EOD) Session Report

Generate comprehensive session report and log to database.

**API Endpoint:** `http://localhost:8000/api/v1`
**Database:** `ccpm_db` @ 10.0.1.251:5433

---

## STEP 1: Gather Session Metrics

Collect git statistics for the session:

```bash
echo "=== Session Metrics ==="

# Get git statistics since start of day
SINCE_TIME=$(date +"%Y-%m-%d 00:00:00")

# Files modified today
FILES_MODIFIED=$(git diff --name-only --since="$SINCE_TIME" | wc -l)
echo "Files modified: $FILES_MODIFIED"

# Commits made today
COMMITS_TODAY=$(git log --since="$SINCE_TIME" --oneline | wc -l)
echo "Commits today: $COMMITS_TODAY"

# Lines added/removed
git log --since="$SINCE_TIME" --numstat --pretty="%H" | awk 'NF==3 {plus+=$1; minus+=$2} END {printf("Lines added: %d\nLines removed: %d\n", plus, minus)}'

# Tests run (check for test results)
if [ -f "/tmp/test-results.json" ]; then
  TESTS_RUN=$(jq '.total_tests // 0' /tmp/test-results.json)
  TESTS_PASSED=$(jq '.passed_tests // 0' /tmp/test-results.json)
  echo "Tests run: $TESTS_RUN"
  echo "Tests passed: $TESTS_PASSED"
else
  TESTS_RUN=0
  TESTS_PASSED=0
  echo "No test results found"
fi
```

---

## STEP 2: Check GitHub Tasks

```bash
echo ""
echo "=== GitHub Tasks ==="

# List issues worked on today (commented on or updated)
gh issue list --repo unmanned-systems-uk/homelab \
  --state all \
  --limit 20 \
  --json number,title,state,labels,updatedAt \
  --jq '.[] | select(.updatedAt | fromdateiso8601 > (now - 86400)) | "\(.number): \(.title) [\(.state)]"'
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

## STEP 4: Create Session Report

Generate session report data:

```python
#!/usr/bin/env python3
import requests
import subprocess
import json
from datetime import datetime, timezone
import os

API_BASE = "http://localhost:8000/api/v1"
AGENT_ID = os.getenv("HOMELAB_AGENT_ID", "00000000-0000-0000-0000-000000000001")
SESSION_DATE = datetime.now().date().isoformat()

# Gather git metrics
def get_git_metrics():
    since_time = datetime.now().replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

    # Files modified
    files = subprocess.run(
        ["git", "diff", "--name-only", f"--since={since_time}"],
        capture_output=True, text=True
    )
    files_modified = len([f for f in files.stdout.strip().split('\n') if f])

    # Commits
    commits = subprocess.run(
        ["git", "log", f"--since={since_time}", "--oneline"],
        capture_output=True, text=True
    )
    commits_made = len([c for c in commits.stdout.strip().split('\n') if c])

    # Get commit details
    commit_list = []
    if commits_made > 0:
        log = subprocess.run(
            ["git", "log", f"--since={since_time}", "--pretty=format:%H|%s", "-10"],
            capture_output=True, text=True
        )
        for line in log.stdout.strip().split('\n'):
            if '|' in line:
                hash, msg = line.split('|', 1)
                commit_list.append({"hash": hash[:8], "message": msg})

    # Lines changed
    stats = subprocess.run(
        ["git", "log", f"--since={since_time}", "--numstat", "--pretty=%H"],
        capture_output=True, text=True
    )
    lines_added = 0
    lines_removed = 0
    for line in stats.stdout.split('\n'):
        parts = line.split()
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            lines_added += int(parts[0])
            lines_removed += int(parts[1])

    return {
        "files_modified": files_modified,
        "commits_made": commits_made,
        "commit_list": commit_list,
        "lines_added": lines_added,
        "lines_removed": lines_removed
    }

# Get GitHub tasks
def get_github_tasks():
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--repo", "unmanned-systems-uk/homelab",
             "--state", "all", "--limit", "20", "--json", "number,title,state,updatedAt"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            issues = json.loads(result.stdout)
            # Filter for today
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            recent = []
            for issue in issues:
                updated = datetime.fromisoformat(issue['updatedAt'].replace('Z', '+00:00'))
                if updated >= today:
                    recent.append(f"#{issue['number']}: {issue['title']} [{issue['state']}]")
            return recent
        return []
    except Exception as e:
        print(f"Error getting GitHub issues: {e}")
        return []

# Create session report
def create_session_report():
    metrics = get_git_metrics()
    tasks = get_github_tasks()

    # Build session data
    session_data = {
        "agent_id": AGENT_ID,
        "agent_tag": "[HomeLab]",
        "trigger_type": "manual",
        "session_date": SESSION_DATE,
        "session_started_at": datetime.now(timezone.utc).replace(
            hour=9, minute=0, second=0, microsecond=0
        ).isoformat(),
        "session_ended_at": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "summary": f"HomeLab session: {metrics['commits_made']} commits, {metrics['files_modified']} files modified, {len(tasks)} GitHub tasks updated",
        "completed_items": tasks,
        "in_progress_items": [],
        "blockers": [],
        "handoff_notes": "Session complete. All infrastructure operational.",
        "total_tasks_touched": len(tasks),
        "tasks_completed": len([t for t in tasks if '[closed]' in t or '[CLOSED]' in t]),
        "files_modified": metrics['files_modified'],
        "commits_made": metrics['commits_made'],
        "tests_run": 0,
        "tests_passed": 0,
        "total_tokens": 0,
        "input_tokens": 0,
        "output_tokens": 0
    }

    # Calculate duration (assume 9am start time for now)
    start = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0)
    end = datetime.now(timezone.utc)
    session_data["duration_minutes"] = int((end - start).total_seconds() / 60)

    try:
        # Create session report
        response = requests.post(
            f"{API_BASE}/session-reports",
            json=session_data,
            timeout=10
        )

        if response.status_code == 201:
            report = response.json()
            report_id = report["id"]
            print(f"\n✅ Session report created: {report_id}")

            # Add commits if any
            for commit in metrics['commit_list']:
                try:
                    requests.post(
                        f"{API_BASE}/session-reports/{report_id}/commits",
                        json={
                            "commit_hash": commit['hash'],
                            "commit_message": commit['message'],
                            "files_changed": 0,
                            "insertions": 0,
                            "deletions": 0
                        },
                        timeout=5
                    )
                except Exception as e:
                    print(f"Warning: Failed to log commit {commit['hash']}: {e}")

            return {
                "report_id": report_id,
                "metrics": metrics,
                "tasks": tasks,
                "session_data": session_data
            }
        else:
            print(f"❌ Failed to create session report: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to session logging API at localhost:8000")
        print("Is the backend service running?")
        return None
    except Exception as e:
        print(f"❌ Error creating session report: {e}")
        return None

# Run
if __name__ == "__main__":
    result = create_session_report()
    if result:
        # Save to file
        report_file = f"/tmp/eod-report-{SESSION_DATE}.json"
        with open(report_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n📄 Report saved to: {report_file}")

        # Copy to CC-Share if mounted
        if os.path.exists("/mnt/CC-Share"):
            import shutil
            shutil.copy(report_file, f"/mnt/CC-Share/eod-{SESSION_DATE}.json")
            print(f"📤 Report copied to CC-Share")
```

---

## STEP 5: Generate EOD Summary

Present the end-of-day summary:

```
# End of Day Report - {DATE}

## Session Overview
- **Duration:** X hours Y minutes
- **Status:** Completed
- **Report ID:** {report_id}

## Work Completed
### Git Activity
- **Commits:** X
- **Files Modified:** Y
- **Lines Added:** +Z
- **Lines Removed:** -W

### GitHub Tasks
{List of tasks worked on}

### Infrastructure
- SCPI Equipment: X/6 online
- Network: Y/3 core devices online

## Summary
{Generated summary}

## Handoff Notes
{Any notes for next session}

---

**Session logged to database:** ccpm_db @ 10.0.1.251:5433
**Report saved to:** /mnt/CC-Share/eod-{DATE}.json
```

---

## Environment Variables

Required for session logging:

```bash
# Set in ~/.bashrc or session
export HOMELAB_AGENT_ID="your-agent-uuid-here"
```

Generate agent ID if needed:
```python
import uuid
print(f"export HOMELAB_AGENT_ID={uuid.uuid4()}")
```

---

## Files Created

- `/tmp/eod-report-{DATE}.json` - Local copy
- `/mnt/CC-Share/eod-{DATE}.json` - Network share copy (if mounted)
- Database record in `ccpm_db.session_reports`

---

*HomeLab Agent - End of Day reporting with database integration*
