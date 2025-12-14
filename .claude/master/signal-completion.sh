#!/bin/bash
# Agent Completion Signal Helper (v2.0)
# Agents use this to notify Master when they finish tasks and auto-update workflow status
# Usage: ./signal-completion.sh <agent-name> <task-id> [task-description] [report-file] [recipient]
#
# v2.0: Now auto-updates task status via API (Task #283)
# Workflow: in-progress -> signal-completion.sh -> status:review

CCPM_API="${CCPM_API:-http://localhost:8080}"
LOG_FILE=".claude/master/signals.log"

AGENT_NAME="$1"
TASK_ID="$2"
TASK_DESC="${3:-Task completed}"
REPORT_FILE="$4"
RECIPIENT="${5:-ccpm-master}"

# Validate required parameters
if [ -z "$AGENT_NAME" ] || [ -z "$TASK_ID" ]; then
    echo "Usage: $0 <agent-name> <task-id> [task-description] [report-file] [recipient]"
    echo ""
    echo "Parameters:"
    echo "  agent-name     : Agent WHO tag (e.g., CC-Backend, CC-Integration)"
    echo "  task-id        : Task ID number to update"
    echo "  task-description: Brief description (optional)"
    echo "  report-file    : Path to completion report (optional)"
    echo "  recipient      : tmux session to notify (default: ccpm-master)"
    echo ""
    echo "Examples:"
    echo "  $0 CC-Backend 283 'Updated signal script'"
    echo "  $0 CC-Integration 299 'Added heartbeat' report.md ccpm-director"
    exit 1
fi

# Validate task ID is numeric
if ! [[ "$TASK_ID" =~ ^[0-9]+$ ]]; then
    echo "Error: task-id must be a number, got: $TASK_ID"
    exit 1
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Step 1: Update task status to 'status:review' via API
# X-Actor format: role:identifier (e.g., agent:CC-Integration)
echo "[$TIMESTAMP] Updating task #$TASK_ID to status:review..."
API_RESPONSE=$(curl -s -X PUT "$CCPM_API/api/agent/tasks/$TASK_ID/status" \
    -H "Content-Type: application/json" \
    -H "X-Actor: agent:$AGENT_NAME" \
    -d "{\"status\": \"status:review\", \"notes\": \"$TASK_DESC\"}" 2>&1)

API_STATUS=$?
if [ $API_STATUS -ne 0 ]; then
    echo "Warning: API call failed (curl error $API_STATUS)"
    echo "[$TIMESTAMP] [API_FAIL] Task #$TASK_ID - curl error: $API_STATUS" >> "$LOG_FILE"
else
    # Check if API returned error
    if echo "$API_RESPONSE" | grep -q '"error"'; then
        ERROR_MSG=$(echo "$API_RESPONSE" | grep -o '"error":"[^"]*"' | head -1)
        echo "Warning: API returned error: $ERROR_MSG"
        echo "[$TIMESTAMP] [API_FAIL] Task #$TASK_ID - $ERROR_MSG" >> "$LOG_FILE"
    else
        echo "Task #$TASK_ID updated to status:review"
        echo "[$TIMESTAMP] [API_OK] Task #$TASK_ID -> status:review by $AGENT_NAME" >> "$LOG_FILE"
    fi
fi

# Step 2: Build notification message
MESSAGE="✅ COMPLETION SIGNAL from $AGENT_NAME: Task #$TASK_ID - $TASK_DESC"
if [ -n "$REPORT_FILE" ] && [ -f "$REPORT_FILE" ]; then
    MESSAGE="$MESSAGE | Report: $REPORT_FILE"
fi

# Step 3: Send to tmux recipient (Master or Director)
if tmux has-session -t "$RECIPIENT" 2>/dev/null; then
    printf '%s\n' "$MESSAGE" | tmux load-buffer - 2>/dev/null
    tmux paste-buffer -t "$RECIPIENT" -d 2>/dev/null
    tmux send-keys -t "$RECIPIENT" C-m 2>/dev/null
    echo "Notified tmux session: $RECIPIENT"
    echo "[$TIMESTAMP] [TMUX_OK] $RECIPIENT <- $MESSAGE" >> "$LOG_FILE"
else
    echo "Warning: tmux session '$RECIPIENT' not found"
    echo "[$TIMESTAMP] [TMUX_FAIL] Session '$RECIPIENT' not found" >> "$LOG_FILE"
fi

# Step 4: Summary
echo ""
echo "Signal complete:"
echo "  Task:      #$TASK_ID"
echo "  Status:    status:review"
echo "  Agent:     $AGENT_NAME"
echo "  Recipient: $RECIPIENT"
