#!/bin/bash
# HL-Network Startup Command
# Minimal context - essentials only

cat << 'EOF'
# HL-Network Agent Startup

**Agent:** HL-Network (Network Infrastructure Specialist)
**UUID:** 11111111-aaaa-bbbb-cccc-000000000002
**Reports to:** HL-Master

---

## Responsibilities
- UniFi management (UDM Pro @ 10.0.1.1)
- VLAN configuration
- Firewall rules
- Client tracking
- Connectivity troubleshooting

---

## Critical Device
EOF

# Quick UDM Pro check
ping -c 1 -W 1 10.0.1.1 &>/dev/null && echo "UDM Pro (10.0.1.1): UP ✓" || echo "UDM Pro (10.0.1.1): DOWN ✗"

echo ""
echo "## UniFi MCP"
echo "Endpoint: https://mcp.unmanned-systems.uk/sse"
echo "Status: Loaded on first use (~4k tokens)"
echo "Tools: 81 available (unifi_list_devices, unifi_list_clients, etc.)"

echo ""
echo "## VLANs"
cat << 'EOF'
- Default (10.0.1.0/24) - Servers, SCPI
- Management (10.0.10.0/24) - UniFi devices
- IoT (10.0.30.0/24) - Smart home
- Lab (10.0.50.0/24) - Test isolation

EOF

echo "## Messages"
UNREAD=$(curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=11111111-aaaa-bbbb-cccc-000000000002&status=unread" 2>/dev/null | jq 'length' 2>/dev/null || echo "?")
echo "Unread: $UNREAD"

cat << 'EOF'

---

**HL-Network Ready**

Awaiting network tasks from HL-Master or user.

**Capabilities:**
- Network scans
- Client lookups
- VLAN configuration
- Firewall rule management
- Connectivity troubleshooting

**Database:** homelab_db.network schema
**Escalate:** Multi-domain tasks to HL-Master

EOF
