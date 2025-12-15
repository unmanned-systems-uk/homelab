#!/bin/bash
# Two-Phase Claude CLI Workflow
# Phase 1: Human waffle → Clear requirement (requirements-agent)
# Phase 2: Clear requirement → JSON (claude-refiner)

OLLAMA_URL="http://10.0.1.201:11434"
CONVERSATION_HISTORY=""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Claude CLI Workflow - Two-Phase Prompt Refinement          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Phase 1: Requirements Extraction (conversational)"
echo "I'll help you define a clear requirement through questions."
echo "Type 'quit' to exit at any time."
echo ""

# Phase 1: Requirements Extraction Loop
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 1: Tell me what you need (in your own words)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

REFINED_REQUIREMENT=""

while true; do
    # Get user input
    echo -n "You: "
    read USER_INPUT

    # Check for quit
    if [[ "$USER_INPUT" == "quit" ]]; then
        echo "Workflow cancelled."
        exit 0
    fi

    # Add to conversation history
    CONVERSATION_HISTORY="${CONVERSATION_HISTORY}User: ${USER_INPUT}\n"

    # Call requirements-agent with proper JSON escaping
    echo -n "Requirements Agent: "

    # Build JSON payload properly using jq
    JSON_PAYLOAD=$(jq -n \
        --arg model "requirements-agent" \
        --arg prompt "$CONVERSATION_HISTORY" \
        '{model: $model, prompt: $prompt, stream: false}')

    # Make API call with error handling
    API_RESPONSE=$(curl -s "$OLLAMA_URL/api/generate" \
        -H "Content-Type: application/json" \
        -d "$JSON_PAYLOAD" 2>&1)

    # Check if curl succeeded
    if [ $? -ne 0 ]; then
        echo "[ERROR: Failed to connect to Ollama API]"
        echo "Debug: $API_RESPONSE"
        continue
    fi

    # Extract response with error handling
    AGENT_RESPONSE=$(echo "$API_RESPONSE" | jq -r '.response // "ERROR: No response"')

    # Check for API errors
    if echo "$API_RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
        API_ERROR=$(echo "$API_RESPONSE" | jq -r '.error')
        echo "[ERROR: $API_ERROR]"
        continue
    fi

    # Check if response is null or empty
    if [ -z "$AGENT_RESPONSE" ] || [ "$AGENT_RESPONSE" == "null" ]; then
        echo "[ERROR: Received null response from model]"
        echo "Debug - Full API response:"
        echo "$API_RESPONSE" | jq .
        continue
    fi

    # Display agent response
    echo "$AGENT_RESPONSE"
    echo ""

    # Add to conversation history
    CONVERSATION_HISTORY="${CONVERSATION_HISTORY}Assistant: ${AGENT_RESPONSE}\n"

    # Check if agent has finalized requirement
    if echo "$AGENT_RESPONSE" | grep -q "Here's your refined requirement:"; then
        # Extract the refined requirement
        REFINED_REQUIREMENT=$(echo "$AGENT_RESPONSE" | sed -n 's/.*Here'"'"'s your refined requirement: \(.*\)/\1/p')

        if [ -z "$REFINED_REQUIREMENT" ]; then
            # Try alternate extraction
            REFINED_REQUIREMENT=$(echo "$AGENT_RESPONSE" | grep -A 10 "refined requirement" | tail -1)
        fi

        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✓ Phase 1 Complete: Clear requirement defined!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        break
    fi
done

# Phase 2: JSON Translation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 2: Converting to Claude CLI JSON..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Refined Requirement:"
echo "  $REFINED_REQUIREMENT"
echo ""

# Call claude-refiner with proper JSON escaping
JSON_PAYLOAD=$(jq -n \
    --arg model "claude-refiner" \
    --arg prompt "$REFINED_REQUIREMENT" \
    '{model: $model, prompt: $prompt, stream: false}')

API_RESPONSE=$(curl -s "$OLLAMA_URL/api/generate" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD")

CLAUDE_JSON=$(echo "$API_RESPONSE" | jq -r '.response')

# Validate JSON response
if [ -z "$CLAUDE_JSON" ] || [ "$CLAUDE_JSON" == "null" ]; then
    echo "[ERROR: Failed to get JSON from claude-refiner]"
    echo "Debug - Full API response:"
    echo "$API_RESPONSE" | jq .
    exit 1
fi

echo "Claude CLI JSON:"
echo "$CLAUDE_JSON" | jq . 2>/dev/null || echo "$CLAUDE_JSON"
echo ""

# Parse JSON and build Claude command
CLI_CMD=$(echo "$CLAUDE_JSON" | jq -r '.cli_command // "claude"')
SUBCOMMAND=$(echo "$CLAUDE_JSON" | jq -r '.subcommand // "chat"')
MODEL=$(echo "$CLAUDE_JSON" | jq -r '.model // "claude-3-5-sonnet"')
SYSTEM_APPEND=$(echo "$CLAUDE_JSON" | jq -r '.system_prompt_append // ""')
USER_QUERY=$(echo "$CLAUDE_JSON" | jq -r '.user_query')

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Phase 2 Complete: Ready for Claude CLI!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Recommended Claude CLI Command:"
echo ""
if [ -n "$SYSTEM_APPEND" ]; then
    echo "  $CLI_CMD $SUBCOMMAND --model $MODEL --system \"$SYSTEM_APPEND\" \"$USER_QUERY\""
else
    echo "  $CLI_CMD $SUBCOMMAND --model $MODEL \"$USER_QUERY\""
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Workflow complete! Copy the command above and run it."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
