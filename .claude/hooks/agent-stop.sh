#!/bin/bash
# Stop Hook - Auto-update status when agent finishes responding
# This fires after Claude Code completes its response

# Read hook input from stdin
INPUT=$(cat)

# Get agent name
if [ -n "$TMUX" ]; then
    AGENT_NAME=$(tmux display-message -p '#S' 2>/dev/null)
else
    AGENT_NAME="unknown"
fi

HEARTBEAT_DIR="/home/anthony/ccpm-workspace/production/.claude/master/heartbeats"

# Extract stop reason if available
STOP_REASON=$(echo "$INPUT" | jq -r '.reason // "completed"' 2>/dev/null)

# Log response completion
echo "[$(date -u '+%Y-%m-%dT%H:%M:%S')] [RESPONSE] $AGENT_NAME finished responding ($STOP_REASON)" >> "$HEARTBEAT_DIR/activity.log"

# Update heartbeat to awaiting (waiting for next input)
curl -s -X POST "http://localhost:8080/api/sessions/${AGENT_NAME}/heartbeat" \
    -H "Content-Type: application/json" \
    -d "{\"agent_name\": \"$AGENT_NAME\", \"state\": \"awaiting\", \"activity\": \"Response complete, awaiting next input\"}" > /dev/null 2>&1

exit 0
