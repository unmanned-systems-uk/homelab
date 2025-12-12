# CLAUDE.md - HomeLab Agent Instructions

## Project
- **Repo:** `unmanned-systems-uk/homelab`
- **Project ID:** 5
- **Working Directory:** `/home/anthony/ccpm-workspace/HomeLab`
- **Stack:** Infrastructure as Code, Docker, AI/ML tooling

## Project Focus
HomeLab is a versatile home lab infrastructure project with emphasis on:
- AI/ML model development and training environments
- CCPM project management integration
- Infrastructure automation and deployment
- Development environment standardization

## Critical Rules
1. **NEVER close GitHub issues** - User closes issues
2. **Use `gh` CLI** for GitHub (not API tokens)
3. **Correct repo:** `unmanned-systems-uk/homelab`
4. **Test infrastructure changes** before committing
5. **Document all hardware/network configs** in `/docs`

## Workflow Compliance
Query AI-Master API for workflow rules:
```bash
curl -s http://localhost:8080/api/master/workflow-rules | jq .
```

## Quick Commands
```bash
# CCPM API
curl -s http://localhost:8080/api/projects/5 | jq .
curl -s "http://localhost:8080/api/sprints?project_id=5" | jq .
curl -s "http://localhost:8080/api/tasks?project_id=5" | jq .

# GitHub
gh issue list --repo unmanned-systems-uk/homelab
gh issue create --repo unmanned-systems-uk/homelab --title "Title" --body "Body"
```

## Directory Structure
```
HomeLab/
├── docs/           # Documentation, network diagrams, hardware specs
├── infrastructure/ # IaC configs (Docker, Ansible, Terraform)
├── scripts/        # Automation and utility scripts
└── .claude/        # Claude Code commands and configs
    └── commands/   # Custom slash commands
```

## WHO Tags
Format: `[HL-Infra]`, `[HL-AI]`, `[HL-Network]`, `[HL-Docs]`

---
*Managed via CCPM - Project ID 5*
