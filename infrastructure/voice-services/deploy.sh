#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# Voice Services Deployment Script
# Deploy Wyoming + OpenAI-compatible API stack to Whisper VM
# ═══════════════════════════════════════════════════════════════════

set -e

WHISPER_HOST="10.0.1.201"
WHISPER_USER="ccpm"
REMOTE_PATH="/home/ccpm/voice-services"

echo "═══════════════════════════════════════════════════════════════════"
echo "Voice Services Deployment"
echo "═══════════════════════════════════════════════════════════════════"

# Check connectivity
echo "[1/6] Checking connectivity to $WHISPER_HOST..."
if ! ping -c 1 -W 3 "$WHISPER_HOST" > /dev/null 2>&1; then
    echo "ERROR: Cannot reach $WHISPER_HOST"
    exit 1
fi
echo "  ✓ Host reachable"

# Disable old service if exists
echo "[2/6] Disabling old tts-service..."
ssh "$WHISPER_USER@$WHISPER_HOST" 'echo "053210" | sudo -S systemctl disable --now tts-service 2>/dev/null || true'
echo "  ✓ Old service disabled"

# Check/install Docker
echo "[3/6] Checking Docker installation..."
if ! ssh "$WHISPER_USER@$WHISPER_HOST" 'command -v docker &> /dev/null'; then
    echo "  Installing Docker..."
    ssh "$WHISPER_USER@$WHISPER_HOST" 'curl -fsSL https://get.docker.com | sudo sh && sudo usermod -aG docker $USER'
    echo "  ✓ Docker installed (may need re-login)"
else
    echo "  ✓ Docker already installed"
fi

# Copy files
echo "[4/6] Copying voice services files..."
ssh "$WHISPER_USER@$WHISPER_HOST" "mkdir -p $REMOTE_PATH/openai-wrapper"
scp docker-compose.yml "$WHISPER_USER@$WHISPER_HOST:$REMOTE_PATH/"
scp openai-wrapper/* "$WHISPER_USER@$WHISPER_HOST:$REMOTE_PATH/openai-wrapper/"
echo "  ✓ Files copied"

# Deploy stack
echo "[5/6] Deploying Docker stack..."
ssh "$WHISPER_USER@$WHISPER_HOST" "cd $REMOTE_PATH && docker compose pull && docker compose up -d --build"
echo "  ✓ Stack deployed"

# Verify
echo "[6/6] Verifying services..."
sleep 10

PIPER_OK=$(curl -s --connect-timeout 5 "http://$WHISPER_HOST:10200" > /dev/null 2>&1 && echo "UP" || echo "DOWN")
WHISPER_OK=$(curl -s --connect-timeout 5 "http://$WHISPER_HOST:10300" > /dev/null 2>&1 && echo "UP" || echo "DOWN")
API_OK=$(curl -s --connect-timeout 5 "http://$WHISPER_HOST:8000/health" 2>/dev/null | grep -q "healthy" && echo "UP" || echo "DOWN")

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Deployment Complete"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Service Status:"
echo "  Wyoming Piper (TTS):    $PIPER_OK  - http://$WHISPER_HOST:10200"
echo "  Wyoming Whisper (STT):  $WHISPER_OK  - http://$WHISPER_HOST:10300"
echo "  OpenAI API Wrapper:     $API_OK  - http://$WHISPER_HOST:8000"
echo ""
echo "Home Assistant Configuration:"
echo "  wyoming:"
echo "    - host: $WHISPER_HOST"
echo "      port: 10200  # Piper TTS"
echo "    - host: $WHISPER_HOST"
echo "      port: 10300  # Whisper STT"
echo ""
echo "Test TTS:"
echo "  curl -X POST http://$WHISPER_HOST:8000/v1/audio/speech \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"input\":\"Hello world\",\"voice\":\"amy\"}' \\"
echo "    --output test.wav"
echo ""
