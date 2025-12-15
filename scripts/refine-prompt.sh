#!/bin/bash
# Claude CLI Prompt Refiner using Ollama Llama 3
# Usage: ./refine-prompt.sh "conversational prompt here"

OLLAMA_URL="http://10.0.1.201:11434"
CONVERSATIONAL_INPUT="$1"

if [ -z "$CONVERSATIONAL_INPUT" ]; then
    echo "Usage: $0 \"your conversational prompt\""
    exit 1
fi

# System prompt for Claude CLI translation
SYSTEM_PROMPT="You are a Claude CLI command translator. Your task is to convert conversational user input into a structured JSON object for the claude cli command. Output ONLY valid JSON with these exact fields: cli_command (always 'claude'), subcommand (e.g. 'chat'), model (e.g. 'claude-3-5-sonnet'), system_prompt_append (any special instructions), user_query (the cleaned, precise query). Be concise and precise."

# Call Ollama API
RESPONSE=$(curl -s "$OLLAMA_URL/api/generate" -d "{
  \"model\": \"llama3:8b\",
  \"system\": \"$SYSTEM_PROMPT\",
  \"prompt\": \"$CONVERSATIONAL_INPUT\",
  \"format\": \"json\",
  \"stream\": false
}")

# Extract the response field (contains the JSON)
REFINED_JSON=$(echo "$RESPONSE" | jq -r '.response')

echo "=== Conversational Input ==="
echo "$CONVERSATIONAL_INPUT"
echo ""
echo "=== Refined JSON Output ==="
echo "$REFINED_JSON" | jq .
echo ""
echo "=== Ready for Claude CLI ==="

# Parse and construct Claude command
CLI_CMD=$(echo "$REFINED_JSON" | jq -r '.cli_command // "claude"')
SUBCOMMAND=$(echo "$REFINED_JSON" | jq -r '.subcommand // "chat"')
MODEL=$(echo "$REFINED_JSON" | jq -r '.model // "claude-3-5-sonnet"')
SYSTEM_APPEND=$(echo "$REFINED_JSON" | jq -r '.system_prompt_append // ""')
USER_QUERY=$(echo "$REFINED_JSON" | jq -r '.user_query')

if [ -n "$SYSTEM_APPEND" ]; then
    echo "$CLI_CMD $SUBCOMMAND --model $MODEL --system \"$SYSTEM_APPEND\" \"$USER_QUERY\""
else
    echo "$CLI_CMD $SUBCOMMAND --model $MODEL \"$USER_QUERY\""
fi
