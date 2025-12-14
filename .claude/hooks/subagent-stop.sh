#!/bin/bash
# SubagentStop Hook - Notify when subagent tasks complete
# This fires when a Task tool subagent finishes

# Read hook input from stdin
INPUT=$(cat)

# Get agent name
if [ -n "$TMUX" ]; then
    AGENT_NAME=$(tmux display-message -p '#S' 2>/dev/null)
else
    AGENT_NAME="unknown"
fi

HEARTBEAT_DIR="/home/anthony/ccpm-workspace/production/.claude/master/heartbeats"

# Extract subagent type and result
SUBAGENT_TYPE=$(echo "$INPUT" | jq -r '.subagent_type // "unknown"' 2>/dev/null)
RESULT_SUMMARY=$(echo "$INPUT" | jq -r '.result // "completed"' 2>/dev/null | head -c 200)

# Log subagent completion
echo "[$(date -u '+%Y-%m-%dT%H:%M:%S')] [SUBAGENT] $AGENT_NAME: $SUBAGENT_TYPE completed" >> "$HEARTBEAT_DIR/subagents.log"

# Update heartbeat to show subagent finished
curl -s -X POST "http://localhost:8080/api/sessions/${AGENT_NAME}/heartbeat" \
    -H "Content-Type: application/json" \
    -d "{\"agent_name\": \"$AGENT_NAME\", \"state\": \"active\", \"activity\": \"Subagent $SUBAGENT_TYPE completed\"}" > /dev/null 2>&1

exit 0
