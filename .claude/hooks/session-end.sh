#!/bin/bash
# CCPM Agent Deregistration Hook
# Runs on Stop - marks agent as offline

# Get agent name
if [ -n "$CCPM_AGENT_NAME" ]; then
    SESSION_NAME="$CCPM_AGENT_NAME"
elif [ -n "$TMUX" ]; then
    SESSION_NAME=$(tmux display-message -p '#S' 2>/dev/null)
else
    SESSION_NAME="claude-$$"
fi

# Update heartbeat to offline
curl -s -X POST "http://localhost:8080/api/sessions/${SESSION_NAME}/heartbeat" \
    -H "Content-Type: application/json" \
    -d "{
        \"agent_name\": \"$SESSION_NAME\",
        \"state\": \"offline\",
        \"activity\": \"Session ended\"
    }" > /dev/null 2>&1

# Use absolute path for heartbeats
HEARTBEAT_DIR="/home/anthony/ccpm-workspace/production/.claude/master/heartbeats"

if [ -d "$HEARTBEAT_DIR" ]; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%S+0000')] [OFFLINE] $SESSION_NAME stopped" >> "$HEARTBEAT_DIR/heartbeat.log"

    # Remove heartbeat file
    rm -f "$HEARTBEAT_DIR/${SESSION_NAME}.heartbeat" 2>/dev/null
fi

echo "CCPM Agent deregistered: $SESSION_NAME"
