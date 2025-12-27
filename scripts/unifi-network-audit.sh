#!/bin/bash
# UniFi Network Audit Script
# Gathers all network configuration for USG to UDM migration

set -e

COOKIE_FILE="/tmp/unifi_cookie_$$"
HOST="https://10.0.1.2:8443"
USERNAME="Anthony"
PASSWORD="ABDAdman2350@!"
SITE="default"
OUTPUT_DIR="/home/anthony/ccpm-workspace/HomeLab/audit-data"

mkdir -p "$OUTPUT_DIR"

cleanup() {
    rm -f "$COOKIE_FILE"
}
trap cleanup EXIT

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Login
log "Authenticating with UniFi Controller..."
LOGIN=$(curl -sk -c "$COOKIE_FILE" -X POST "$HOST/api/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

if ! echo "$LOGIN" | grep -q '"rc":"ok"'; then
    echo "ERROR: Authentication failed"
    exit 1
fi
log "Authentication successful"

# Function to fetch and save API data
fetch() {
    local endpoint=$1
    local filename=$2
    log "Fetching $filename..."
    curl -sk -b "$COOKIE_FILE" "$HOST/api/s/$SITE/$endpoint" > "$OUTPUT_DIR/$filename"
}

# Gather all network data
log "Starting network audit..."

fetch "stat/device" "devices.json"
fetch "stat/sta" "clients.json"
fetch "rest/networkconf" "networks.json"
fetch "rest/firewallrule" "firewall-rules.json"
fetch "rest/portforward" "port-forwards.json"
fetch "rest/wlanconf" "wlan-configs.json"
fetch "rest/routing" "routing.json"
fetch "rest/dhcp_lease" "dhcp-leases.json"
fetch "rest/portconf" "port-configs.json"
fetch "rest/user" "static-clients.json"

# Site settings
log "Fetching site settings..."
curl -sk -b "$COOKIE_FILE" "$HOST/api/s/$SITE/get/setting" > "$OUTPUT_DIR/site-settings.json"

# System info
log "Fetching system info..."
curl -sk -b "$COOKIE_FILE" "$HOST/api/s/$SITE/stat/sysinfo" > "$OUTPUT_DIR/system-info.json"

# Health status
log "Fetching health status..."
curl -sk -b "$COOKIE_FILE" "$HOST/api/s/$SITE/stat/health" > "$OUTPUT_DIR/health.json"

log "Network audit complete!"
log "Data saved to: $OUTPUT_DIR"
ls -la "$OUTPUT_DIR"
