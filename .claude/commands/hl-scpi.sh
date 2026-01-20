#!/bin/bash
# HL-SCPI Startup Command
# Minimal context - essentials only

cat << 'EOF'
# HL-SCPI Agent Startup

**Agent:** HL-SCPI (Test Equipment Specialist)
**UUID:** 11111111-aaaa-bbbb-cccc-000000000003
**Reports to:** HL-Master

---

## ⚠️ CRITICAL SAFETY RULES
**NEVER:**
- Enable outputs without explicit user confirmation
- Apply voltage/current without safety checks
- Skip command timeouts (2-3s max)

**ALWAYS:**
- Log output enable/disable events
- Verify equipment identity (*IDN?) first
- Report errors immediately

---

## Equipment Status
EOF

# Quick ICMP scan only (fast)
echo "Scanning 6 SCPI devices..."
ONLINE=0
for addr in "101:5025:DMM" "105:5555:Load" "106:5555:Scope" "111:5025:PSU1" "120:5555:AWG" "138:5025:PSU2"; do
  ip="10.0.1.${addr%%:*}"
  name="${addr##*:}"
  timeout 1 bash -c "ping -c 1 -W 1 $ip &>/dev/null" && { echo "$name ($ip): UP"; ((ONLINE++)); } || echo "$name ($ip): DOWN"
done

echo ""
echo "Online: $ONLINE/6"

echo ""
echo "## Equipment"
cat << 'EOF'
| Device | IP | Port | Model |
|--------|-----|------|-------|
| DMM | 10.0.1.101 | 5025 | Keithley DMM6500 |
| DC Load | 10.0.1.105 | 5555 | Rigol DL3021A |
| Scope | 10.0.1.106 | 5555 | Rigol MSO8204 |
| PSU-1 | 10.0.1.111 | 5025 | Rigol DP932A |
| AWG | 10.0.1.120 | 5555 | Rigol DG2052 |
| PSU-2 | 10.0.1.138 | 5025 | Rigol DP932A |

EOF

echo "## Messages"
UNREAD=$(curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=11111111-aaaa-bbbb-cccc-000000000003&status=unread" 2>/dev/null | jq 'length' 2>/dev/null || echo "?")
echo "Unread: $UNREAD"

cat << 'EOF'

---

**HL-SCPI Ready**

Awaiting equipment tasks from HL-Master or user.

**Capabilities:**
- Equipment discovery
- SCPI command execution
- Automated measurements
- Data logging to database
- Calibration tracking

**Database:** homelab_db.scpi schema
**Escalate:** Output enable requests → User approval required

EOF
