# HomeLab Agent Startup

**Agent:** HomeLab
**Working Directory:** `/home/anthony/ccpm-workspace/HomeLab`

---

## STEP 1: Load Identity

You are the **HomeLab** agent managing infrastructure, SCPI equipment, and AI/ML resources.

Read your definition:
```
Read file: .claude/agents/homelab/AGENT.md
Read file: .claude/agents/homelab/DOMAINS.md
```

---

## STEP 2: Check GitHub Issues

```bash
echo "=== Open GitHub Issues ==="
gh issue list --repo unmanned-systems-uk/homelab --state open --limit 10
```

---

## STEP 3: Equipment Quick Check

Verify SCPI equipment connectivity:

```bash
echo ""
echo "=== SCPI Equipment ==="
for addr in "101:5025" "105:5555" "106:5555" "111:5025" "120:5555" "138:5025"; do
  ip="10.0.1.${addr%:*}"
  port="${addr#*:}"
  timeout 1 bash -c "echo > /dev/tcp/$ip/$port" 2>/dev/null && echo "$ip: UP" || echo "$ip: DOWN"
done
```

---

## STEP 4: Load Last Session

Check for recent session summaries:

```bash
echo ""
echo "=== Recent Sessions ==="
ls -1 docs/session-summary-*.md 2>/dev/null | tail -3
```

Read the most recent one if it exists.

---

## STEP 5: Report Ready

Present status to user:

```
# HomeLab Agent Ready

## GitHub Issues
[X open issues - list titles]

## Equipment Status
[X/6 SCPI devices online]

## Key Network
- UDM Pro (10.0.1.1): [UP/DOWN]
- NAS (10.0.1.251): [UP/DOWN]

## Recent Session
[Date if exists, or "None"]

---
What would you like to work on?
```

---

## MCP Tools Available

| Tool | Purpose |
|------|---------|
| **Context7** | Library documentation |

### Using Context7

```
mcp__context7__resolve-library-id(libraryName: "docker")
mcp__context7__get-library-docs(context7CompatibleLibraryID: "/docker/docs", topic: "compose")
```

---

## Quick Reference

### Key Paths
- Hardware Inventory: `docs/hardware-inventory.md`
- Server Architecture: `docs/server-stack-architecture.md`
- Network Config: `docs/udm-pro-migration-complete.md`

### SCPI Devices
| Device | IP | Port |
|--------|-----|------|
| DMM | 10.0.1.101 | 5025 |
| Load | 10.0.1.105 | 5555 |
| Scope | 10.0.1.106 | 5555 |
| PSU1 | 10.0.1.111 | 5025 |
| AWG | 10.0.1.120 | 5555 |
| PSU2 | 10.0.1.138 | 5025 |

---

*HomeLab Agent initialized. Awaiting instructions.*
