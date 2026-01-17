#!/bin/bash
# Test script for transcoding proxy

echo "=== Audio Transcoding Proxy Test ==="
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
curl -s http://localhost:8001/health | jq '.' 2>/dev/null || curl -s http://localhost:8001/health
echo ""
echo ""

# Test 2: Service info
echo "Test 2: Service Info"
curl -s http://localhost:8001/ | jq '.' 2>/dev/null || curl -s http://localhost:8001/
echo ""
echo ""

# Test 3: Transcription (requires audio file)
if [ -f "$1" ]; then
    echo "Test 3: Transcription with $1"
    curl -X POST http://localhost:8001/v1/audio/transcriptions \
        -F "file=@$1" \
        -F "model=whisper-1" \
        -F "response_format=json" | jq '.' 2>/dev/null || \
    curl -X POST http://localhost:8001/v1/audio/transcriptions \
        -F "file=@$1" \
        -F "model=whisper-1" \
        -F "response_format=json"
    echo ""
else
    echo "Test 3: Skipped (no audio file provided)"
    echo "Usage: $0 <audio-file>"
fi

echo ""
echo "=== Tests Complete ==="
