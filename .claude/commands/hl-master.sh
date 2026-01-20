#!/bin/bash
# HL-Master Startup Command
# Minimal context - summaries only

cat << 'EOF'
# HL-Master Agent Startup

**Agent:** HL-Master (Orchestrator)
**UUID:** 11111111-aaaa-bbbb-cccc-000000000001
**Role:** Task routing, session management, specialist coordination

---

## Last Session
EOF

# Query last session (one-liner summary only)
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -t -A -c \
  "SELECT session_date || ' | ' || status || ' | ' || COALESCE(summary, 'No summary')
   FROM session_reports
   WHERE agent_tag='[HL-Master]'
   ORDER BY session_date DESC
   LIMIT 1;" 2>/dev/null || echo "Database unavailable"

echo ""
echo "## GitHub Issues"

# Count only, top 3
ISSUE_COUNT=$(gh issue list --repo unmanned-systems-uk/homelab --state open --json number 2>/dev/null | jq 'length' 2>/dev/null || echo "?")
echo "Open: $ISSUE_COUNT"
echo ""
gh issue list --repo unmanned-systems-uk/homelab --state open --limit 3 --json number,title 2>/dev/null | \
  jq -r '.[] | "#\(.number) - \(.title)"' 2>/dev/null || echo "Unable to query issues"

echo ""
echo "## Messages"

# Unread count only
UNREAD=$(curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=11111111-aaaa-bbbb-cccc-000000000001&status=unread" 2>/dev/null | jq 'length' 2>/dev/null || echo "?")
echo "Unread: $UNREAD"

echo ""
echo "## Specialist Agents"
echo "- HL-Network (Network): Available"
echo "- HL-SCPI (Equipment): Available"
echo "- HL-Infra (Proxmox/Docker): Available"
echo "- HL-Home (Home Assistant): Available"
echo "- HL-AI (GPU/ML): Available"
echo "- HL-Gate (HomeGate Project): Available"

echo ""
echo "## Today's Session"

SESSION_DATE=$(date +%Y-%m-%d)
echo "Session: $SESSION_DATE - Initialized"

cat << 'EOF'

---

**HL-Master Ready**

What would you like to work on?

**Routing:**
- Network tasks → HL-Network
- SCPI/test equipment → HL-SCPI
- Proxmox/Docker → HL-Infra
- Home Assistant → HL-Home
- GPU/AI/ML → HL-AI
- HomeGate project → HL-Gate
- Multi-domain → I'll coordinate

**Commands:**
- `/hl-<agent>` - Start specialist agent
- `/check-messages` - Check CCPM inbox
- `/eod` - End of day report

EOF
