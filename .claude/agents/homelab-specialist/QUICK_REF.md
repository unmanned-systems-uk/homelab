# HomeLab Specialist Quick Reference

## Identity
- **WHO:** `[HL-Specialist]`
- **Project ID:** 5
- **Repo:** unmanned-systems-uk/homelab

## Slash Commands
- `/start-homelab` - Full agent startup
- `/homelab-status` - System status
- `/scpi-scan` - Equipment scan
- `/network-scan` - Subnet scan

## CCPM API
```bash
# Health
curl -s http://localhost:8080/api/health | jq .

# Tasks
curl -s "http://localhost:8080/api/todos?project_id=5" | jq .

# Create task
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"project_id":5,"title":"...","description":"..."}'
```

## SCPI Quick
```bash
# DMM reading
echo "MEAS:VOLT:DC?" | nc -w 2 10.0.1.101 5025

# PSU voltage
echo ":MEAS:VOLT? CH1" | nc -w 2 10.0.1.111 5025
```

## Key IPs
| Device | IP |
|--------|-----|
| Gateway | 10.0.1.1 |
| DMM | 10.0.1.101 |
| Load | 10.0.1.105 |
| Scope | 10.0.1.106 |
| PSU1 | 10.0.1.111 |
| Jetson | 10.0.1.113 |
| AWG | 10.0.1.120 |
| PSU2 | 10.0.1.138 |

## Context7 MCP
```
mcp__context7__resolve-library-id(libraryName: "proxmox")
mcp__context7__get-library-docs(context7CompatibleLibraryID: "...", topic: "...")
```

## Docs
- `docs/hardware-inventory.md`
- `docs/server-stack-architecture.md`
- `docs/learning-hub.md`
