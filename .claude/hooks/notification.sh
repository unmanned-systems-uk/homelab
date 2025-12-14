#!/bin/bash
# Notification Hook - Relay important notifications to Master
# This fires when Claude Code sends any notification

# Read hook input from stdin
INPUT=$(cat)

# Get agent name
if [ -n "$TMUX" ]; then
    AGENT_NAME=$(tmux display-message -p '#S' 2>/dev/null)
else
    AGENT_NAME="unknown"
fi

HEARTBEAT_DIR="/home/anthony/ccpm-workspace/production/.claude/master/heartbeats"
WHISPER_DIR="/home/anthony/ccpm-workspace/whisper"
CCPM_SPEAK="$WHISPER_DIR/speak.sh"

# Extract notification content
MESSAGE=$(echo "$INPUT" | jq -r '.message // "notification"' 2>/dev/null | head -c 500)
NOTIFICATION_TYPE=$(echo "$INPUT" | jq -r '.type // "info"' 2>/dev/null)

# Log notification
echo "[$(date -u '+%Y-%m-%dT%H:%M:%S')] [NOTIFY] $AGENT_NAME [$NOTIFICATION_TYPE]: $MESSAGE" >> "$HEARTBEAT_DIR/notifications.log"

# Voice notification function
# For agent-specific messages, always use dynamic TTS so we hear which agent
# For generic alerts (error sounds), use pre-generated audio
voice_notify() {
    local sound_name="$1"
    local message="$2"
    local use_dynamic="${3:-true}"  # Default to dynamic TTS for agent identification

    if [ -x "$CCPM_SPEAK" ]; then
        if [ "$use_dynamic" = "true" ] && [ -n "$message" ]; then
            # Use dynamic TTS to include agent name
            "$CCPM_SPEAK" --say "$message" --quiet &
        elif [ -f "$WHISPER_DIR/audio/system/${sound_name}.wav" ]; then
            # Use pre-generated sound for generic alerts
            "$CCPM_SPEAK" --play "$sound_name" --quiet &
        elif [ -n "$message" ]; then
            # Fallback to dynamic TTS
            "$CCPM_SPEAK" --say "$message" --quiet &
        fi
    fi
}

# Voice alerts based on notification type
# All messages include agent name so user knows which agent needs attention
case "$NOTIFICATION_TYPE" in
    error)
        voice_notify "error" "$AGENT_NAME has an error"
        ;;
    critical)
        voice_notify "critical" "Critical alert from $AGENT_NAME"
        ;;
    warning)
        voice_notify "warning" "$AGENT_NAME has a warning"
        ;;
    question|input_needed)
        voice_notify "question" "$AGENT_NAME has a question"
        ;;
    task_complete|complete)
        voice_notify "task_complete" "$AGENT_NAME task complete"
        ;;
    blocked)
        voice_notify "blocked" "$AGENT_NAME is blocked"
        ;;
    approval|approval_needed|permission_prompt)
        voice_notify "need_approval" "$AGENT_NAME needs approval"
        ;;
    idle_prompt)
        voice_notify "waiting_input" "$AGENT_NAME is waiting for input"
        ;;
    *)
        # For unknown types, still announce the agent
        if [ -n "$NOTIFICATION_TYPE" ]; then
            voice_notify "attention" "$AGENT_NAME needs attention"
        fi
        ;;
esac

# If it's an error or critical notification, update heartbeat
if echo "$NOTIFICATION_TYPE" | grep -qiE "(error|critical|warning)"; then
    curl -s -X POST "http://localhost:8080/api/sessions/${AGENT_NAME}/heartbeat" \
        -H "Content-Type: application/json" \
        -d "{\"agent_name\": \"$AGENT_NAME\", \"state\": \"alert\", \"activity\": \"$NOTIFICATION_TYPE: $MESSAGE\"}" > /dev/null 2>&1
fi

exit 0
