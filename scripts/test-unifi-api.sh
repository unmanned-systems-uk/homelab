#!/bin/bash
# Test UniFi Controller API connectivity

COOKIE_FILE="/tmp/unifi_cookie_$$"
HOST="https://10.0.1.2:8443"
USERNAME="Anthony"
PASSWORD="ABDAdman2350@!"
SITE="default"

# Login
echo "=== Logging in to UniFi Controller ==="
LOGIN_RESULT=$(curl -sk -c "$COOKIE_FILE" -X POST "$HOST/api/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

echo "$LOGIN_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Login:', 'SUCCESS' if d.get('meta',{}).get('rc')=='ok' else 'FAILED')" 2>/dev/null

# Get devices
echo ""
echo "=== UniFi Devices ==="
curl -sk -b "$COOKIE_FILE" "$HOST/api/s/$SITE/stat/device" | python3 -m json.tool 2>/dev/null

# Cleanup
rm -f "$COOKIE_FILE"
