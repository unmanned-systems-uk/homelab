#!/bin/bash
# PostToolUse Hook for Bash - Auto-detect completion signals
# If agent runs signal-completion.sh, auto-update task status

# Read tool result from stdin
INPUT=$(cat)

# Get agent name
if [ -n "$TMUX" ]; then
    AGENT_NAME=$(tmux display-message -p '#S' 2>/dev/null)
else
    AGENT_NAME="unknown"
fi

# Check if the command was a completion signal
COMMAND=$(echo "$INPUT" | jq -r '.input.command // empty' 2>/dev/null)

if echo "$COMMAND" | grep -q "signal-completion"; then
    # Extract task ID from command
    TASK_ID=$(echo "$COMMAND" | grep -oE '#[0-9]+' | grep -oE '[0-9]+' | head -1)

    if [ -n "$TASK_ID" ]; then
        # Log completion
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%S')] [COMPLETE] $AGENT_NAME finished Task #$TASK_ID" >> /home/anthony/ccpm-workspace/production/.claude/master/heartbeats/completions.log

        # Update heartbeat
        curl -s -X POST "http://localhost:8080/api/sessions/${AGENT_NAME}/heartbeat" \
            -H "Content-Type: application/json" \
            -d "{\"agent_name\": \"$AGENT_NAME\", \"state\": \"idle\", \"activity\": \"Completed Task #$TASK_ID\"}" > /dev/null 2>&1
    fi
fi

exit 0
