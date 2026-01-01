# Home Assistant Focus Mode

Switch context to Home Assistant management and development.

---

## HA Repository

**For dedicated HA work, switch to the HA repository:**

```bash
cd /home/homelab/homeassistant
```

**HA Repo:** `unmanned-systems-uk/homeassistant`
**Path:** `/home/homelab/homeassistant`
**Commands:** `/start-ha`, `/ha-status`, `/ha-integrations`

---

## Home Assistant System Info

| Item | Value |
|------|-------|
| **Host** | HA-Pi5 (Raspberry Pi 5 8GB) |
| **IP** | 10.0.1.150 |
| **Port** | 8123 |
| **OS** | HAOS 16.3 |
| **Storage** | Micron 2300 NVMe 512GB |
| **Network** | Default VLAN (10.0.1.0/24) |
| **Access** | http://10.0.1.150:8123 |

---

## Step 1: Check HA Status

```bash
echo "=== Home Assistant Status ==="
ping -c 1 -W 2 10.0.1.150 &>/dev/null && echo "HA Host: ONLINE" || echo "HA Host: OFFLINE"
curl -s --connect-timeout 3 http://10.0.1.150:8123/api/ -o /dev/null && echo "HA API: RESPONDING" || echo "HA API: NOT RESPONDING"
```

---

## Step 2: Check GitHub Issues

```bash
echo ""
echo "=== HA-Related GitHub Issues ==="
gh issue list --repo unmanned-systems-uk/homelab --state open --label "home-assistant" 2>/dev/null || \
gh issue list --repo unmanned-systems-uk/homelab --state open | grep -i "HA\|home.assistant\|wiz\|iot" || echo "No HA issues found"
```

---

## Step 3: Query homelab_db for HA Context

```bash
echo ""
echo "=== HA Device Info from Database ==="
PGPASSWORD=CcpmDb2025Secure psql -h 10.0.1.251 -p 5433 -U ccpm -d homelab_db -t -c "
SELECT device_name, primary_ip, status, notes
FROM infrastructure.devices
WHERE device_name LIKE '%HA%' OR notes ILIKE '%home assistant%' OR notes ILIKE '%HAOS%';"
```

---

## HA Architecture Layers

When working on HA, identify which layer(s) are involved:

| Layer | Domain | Tools/Languages |
|-------|--------|-----------------|
| **A** | UI Configuration | Dashboards, Areas, Helpers |
| **B** | YAML Configuration | Automations, Scripts, Scenes |
| **C** | Templates | Jinja2 with HA variables |
| **D** | Blueprints | Reusable automation patterns |
| **E** | Visual Automation | Node-RED, AppDaemon |
| **F** | Custom Frontend | JavaScript/TypeScript cards |
| **G** | Custom Integrations | Python custom_components |

---

## Network Context (from today's session)

| Network | Subnet | Purpose |
|---------|--------|---------|
| Default | 10.0.1.0/24 | HA host, infrastructure |
| IoT | 10.0.30.0/24 (VLAN 30) | Wiz bulbs, smart devices |

**Firewall Rules Active:**
- Allow HA to IoT (10000)
- Allow IoT to HA (10001)
- Block IoT to LAN (10002)

---

## Current Integrations Status

*Update this list as integrations are added:*

| Integration | Status | Notes |
|-------------|--------|-------|
| Wiz | In Progress | 14 devices, manual IP entry |
| Synology NAS | Pending | Port 5001 (HTTPS) |
| Samsung TV | Pending | 10.0.30.90, 10.0.30.141 |
| NUT (UPS) | Planned | Issue #33 - Move to HomeGate |
| Emporia Energy | Planned | Issue #34 - Needs HACS |

---

## Common HA Tasks

### Check HA Logs (via SSH to HomeGate)
```bash
# HA doesn't have SSH by default - use the console or API
curl -s http://10.0.1.150:8123/api/error_log -H "Authorization: Bearer YOUR_TOKEN"
```

### Restart HA
```bash
curl -X POST http://10.0.1.150:8123/api/services/homeassistant/restart \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List All Entities
```bash
curl -s http://10.0.1.150:8123/api/states -H "Authorization: Bearer YOUR_TOKEN" | python3 -c "import json,sys; states=json.load(sys.stdin); print(f'{len(states)} entities'); [print(s['entity_id']) for s in states[:20]]"
```

---

## HA Best Practices

1. **Test automations** in Developer Tools before saving
2. **Use areas** to organize devices by room
3. **Template sensors** for complex calculated values
4. **Blueprints** for repeatable automation patterns
5. **Backup before major changes** - Settings > System > Backups

---

## Path to Dedicated HA Agent

When HA work becomes complex (custom integrations, Node-RED, etc.):

1. Create dedicated repo: `unmanned-systems-uk/homeassistant`
2. Build HA MCP Server with direct API access
3. Deploy HA-Agent with specialized knowledge
4. Use Git Issues for task management
5. HomeLab-Master coordinates infrastructure needs

---

## Report Format

After completing HA tasks, summarize:

| Item | Status |
|------|--------|
| HA System | Online/Offline |
| Task Completed | Description |
| Integrations Changed | List |
| Issues Created/Updated | #numbers |
| Next Steps | What remains |
