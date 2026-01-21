# /start-homegate

**HomeGate Project Management & Orchestration Mode**

Initialize a session with full focus on HomeGate project management, multi-agent coordination, and development orchestration.

---

## Usage

```
/start-homegate
```

Use this command at session start to:
- Load complete HomeGate project context
- Check system and deployment status
- Review pending tasks and issues
- Enter project management orchestration mode
- Prepare for multi-agent development coordination

---

## What This Command Does

### 1. Load Project Context

**Read core project files:**
- `/home/homelab/HomeGate/CLAUDE.md` - Project instructions and architecture
- `/home/homelab/HomeGate/agents/.claude/common/RULES.md` - Shared development rules
- `/home/homelab/HomeGate/README.md` - Project overview

**Verify agent configurations:**
- `agents/homegate/.claude/AGENT.md` - Full-stack agent
- `agents/frontend/.claude/AGENT.md` - React specialist
- `agents/backend/.claude/AGENT.md` - Node.js specialist
- `agents/devops/.claude/AGENT.md` - Docker specialist

### 2. Check Project Status

**Git repository:**
```bash
cd /home/homelab/HomeGate
git status
git log -5 --oneline
git branch -a
```

**Docker deployments:**
```bash
docker ps --filter "name=homegate" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker logs homegate-backend --tail 20
docker logs homegate-frontend --tail 20
```

**Production accessibility:**
```bash
curl -I http://10.0.1.50 2>&1 | head -5
```

### 3. Review Tasks & Issues

**GitHub issues (unmanned-systems-uk/homegate):**
```bash
gh issue list --repo unmanned-systems-uk/homegate --limit 10
```

**CCPM agent messages (HomeGate Agent):**
```bash
curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=11111111-aaaa-bbbb-cccc-000000000007&status=pending" | python3 -m json.tool
```

**Database connectivity:**
```bash
PGPASSWORD="PASSWORD" psql -h 10.0.1.251 -p 5433 -U homegate -d homegate_db -c "SELECT COUNT(*) as user_count FROM public.users;" 2>&1
```

### 4. Set Orchestration Focus

**Project management mode activated:**
- Multi-agent coordination ready
- Task delegation capabilities active
- Cross-functional feature planning enabled
- Architecture decision authority granted
- Deployment orchestration ready

**Available agents for delegation:**
- **homegate** (yourself) - Full-stack features, architecture, integration
- **frontend** - React/TypeScript UI work, components, styling
- **backend** - Node.js/Express APIs, database, services
- **devops** - Docker, nginx, deployment, infrastructure

### 5. Generate Status Summary

**Provide concise summary:**
```
HomeGate Project Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Repository: unmanned-systems-uk/homegate
Branch: [current branch]
Last Commit: [hash] [message]
Uncommitted Changes: [count files]

Deployment Status:
  ✓ Backend:  [status] - [uptime]
  ✓ Frontend: [status] - [uptime]
  ✓ Production: http://10.0.1.50 [accessible/unreachable]

Database: homegate_db @ 10.0.1.251:5433 [connected/error]

Open Issues: [count]
Pending Messages: [count]

Project Management Mode: ACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready for orchestration. What would you like to focus on?
```

---

## Project Management Capabilities

When this command is active, you have authority to:

### Architecture & Design
- Make architectural decisions for HomeGate
- Design database schemas and migrations
- Plan integration strategies
- Define API contracts
- Review and approve technical approaches

### Multi-Agent Coordination
- Delegate frontend work to frontend agent
- Delegate backend work to backend agent
- Delegate deployment work to devops agent
- Coordinate cross-functional features
- Resolve agent conflicts and dependencies

### Task Management
- Break down features into tasks
- Prioritize development work
- Track progress via GitHub issues
- Update task labels (todo → in-progress → done)
- Create and manage milestones

### Development Workflow
- Review code changes before commit
- Ensure tests pass before deployment
- Coordinate frontend + backend releases
- Manage database migrations
- Handle rollbacks and hotfixes

### External Integrations
- Plan UniFi Network integration work
- Plan Proxmox VE integration work
- Plan Home Assistant integration work
- Plan SCPI equipment integration work
- Coordinate with HomeLab master agent

### Quality & Standards
- Enforce code quality standards (TypeScript strict, ESLint)
- Ensure security best practices (parameterized queries, auth)
- Validate error handling and logging
- Review Docker configurations
- Maintain documentation

---

## Key Project Information

### Technology Stack
- **Frontend:** React 18 + TypeScript + Tailwind CSS + Vite
- **Backend:** Node.js 20 + Express + Socket.io + node-pty
- **Database:** PostgreSQL 15 @ 10.0.1.251:5433
- **Deployment:** Docker + Docker Compose + nginx
- **Production:** i3 Mini PC @ 10.0.1.50

### Core Features
1. **Persistent SSH Terminals** (xterm.js + node-pty)
2. **Infrastructure Monitoring** (UniFi, Proxmox, SCPI)
3. **Backup Monitoring** (Proxmox backup jobs)
4. **Network Analytics** (UniFi MCP integration)
5. **Smart Alerting** (Multi-channel notifications)
6. **Role-Based Access** (JWT authentication)

### Active Integrations
- **UniFi Network** - MCP @ https://mcp.unmanned-systems.uk/sse
- **Proxmox VE** - REST API @ https://10.0.1.200:8006/api2/json
- **Home Assistant** - MCP integration (planned)
- **SCPI Equipment** - TCP/IP direct connections

### Database Schemas
- `public` - Users, SSH sessions, credentials
- `metrics` - Time-series monitoring data
- `config` - System configuration

---

## Common Project Management Tasks

### Start New Feature
1. Review requirements with user
2. Create GitHub issue (unmanned-systems-uk/homegate)
3. Plan implementation (frontend + backend + database)
4. Delegate to appropriate specialist agent(s)
5. Coordinate integration work
6. Test end-to-end
7. Deploy to production
8. Update issue status

### Fix Production Bug
1. Check production logs (`docker logs homegate-backend`)
2. Reproduce issue locally
3. Identify root cause (frontend/backend/database)
4. Delegate fix to appropriate agent
5. Test fix in development
6. Deploy hotfix to production
7. Verify fix in production
8. Document in git commit

### Coordinate Multi-Agent Feature
1. Break down feature into frontend + backend tasks
2. Use TodoWrite to plan subtasks
3. Start backend work first (API contract)
4. Parallel frontend work once API defined
5. Integration testing
6. DevOps agent handles deployment
7. Verify in production

### Release Management
1. Review all pending changes (`git log`)
2. Ensure all tests pass
3. Build containers (`docker compose build`)
4. Deploy to production (`docker compose up -d --force-recreate`)
5. Monitor logs for errors
6. Test critical paths
7. Tag release in git
8. Update GitHub issues

---

## Integration with CCPM V2

### HomeGate Agent Identity
- **HomeGate Agent ID:** `11111111-aaaa-bbbb-cccc-000000000007`
- **HomeLab Agent ID:** `aaaaaaaa-bbbb-cccc-dddd-222222222222`
- **CCPM API:** http://10.0.1.210:8000/api/v1
- **Message Types:** task_assignment, status_request, query, alert, info

### Cross-Project Communication
HomeGate integrates with HomeLab infrastructure:
- Uses UniFi MCP (shared with HomeLab)
- Monitors SCPI equipment (managed by HomeLab)
- Tracks Proxmox VMs (shared infrastructure)
- Coordinates via CCPM messaging

### Messaging Commands
```bash
# Check HomeGate inbox
curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=11111111-aaaa-bbbb-cccc-000000000007&status=pending"

# Send message to HomeLab agent
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000007" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "aaaaaaaa-bbbb-cccc-dddd-222222222222",
    "message_type": "info",
    "subject": "HomeGate deployment status",
    "body": "Deployment successful",
    "priority": "normal"
  }'
```

---

## Quick Reference Commands

### Git
```bash
cd /home/homelab/HomeGate
git status                              # Check status
git log -10 --oneline                   # Recent commits
gh issue list --repo unmanned-systems-uk/homegate  # List issues
```

### Docker
```bash
docker compose build homegate-frontend   # Build frontend
docker compose build homegate-backend    # Build backend
docker compose up -d --force-recreate homegate-frontend  # Deploy frontend
docker compose up -d --force-recreate homegate-backend   # Deploy backend
docker logs homegate-backend -f         # Follow logs
```

### Database
```bash
PGPASSWORD="PASSWORD" psql -h 10.0.1.251 -p 5433 -U homegate -d homegate_db
```

### Production
```bash
curl http://10.0.1.50                   # Test frontend
curl http://10.0.1.50/api/health        # Test backend
```

---

## Notes

- **Authority Level:** Full project management and architectural decision authority
- **Coordination:** Can delegate to specialized agents (frontend, backend, devops)
- **Integration:** Coordinates with HomeLab agent for infrastructure concerns
- **Best Practice:** Use TodoWrite for complex multi-step features
- **Communication:** Concise terminal-friendly responses, no emojis unless requested

---

**Command Version:** 1.0
**Last Updated:** 2026-01-20
**Agent:** HomeLab Master (HomeGate Orchestration Mode)
