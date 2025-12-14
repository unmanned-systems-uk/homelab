#!/bin/bash
# CCPM Agent Auto-Registration Hook
# Runs on SessionStart - registers agent with CCPM heartbeat system

# Extract agent name from tmux session or use default
if [ -n "$TMUX" ]; then
    SESSION_NAME=$(tmux display-message -p '#S' 2>/dev/null)
else
    SESSION_NAME="claude-$$"
fi

# Set environment variables for the session
if [ -n "$CLAUDE_ENV_FILE" ]; then
    echo "export CCPM_AGENT_NAME=\"$SESSION_NAME\"" >> "$CLAUDE_ENV_FILE"
    echo "export CCPM_API=\"http://localhost:8080/api\"" >> "$CLAUDE_ENV_FILE"
    echo "export CCPM_PROJECT_DIR=\"$CLAUDE_PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"
fi

# Register with CCPM heartbeat API
curl -s -X POST "http://localhost:8080/api/sessions/${SESSION_NAME}/heartbeat" \
    -H "Content-Type: application/json" \
    -d "{
        \"agent_name\": \"$SESSION_NAME\",
        \"state\": \"active\",
        \"activity\": \"Session started\"
    }" > /dev/null 2>&1

# Use absolute path for heartbeats (production workspace)
HEARTBEAT_DIR="/home/anthony/ccpm-workspace/production/.claude/master/heartbeats"

if [ -d "$HEARTBEAT_DIR" ]; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%S+0000')] [REGISTER] $SESSION_NAME started (PID: $$)" >> "$HEARTBEAT_DIR/heartbeat.log"

    # Write heartbeat file
    cat > "$HEARTBEAT_DIR/${SESSION_NAME}.heartbeat" << EOF
agent: $SESSION_NAME
pid: $$
started: $(date -u '+%Y-%m-%dT%H:%M:%S+0000')
project: $CLAUDE_PROJECT_DIR
EOF
fi

echo "CCPM Agent registered: $SESSION_NAME"
