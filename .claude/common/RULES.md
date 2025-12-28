# HomeLab Agent Rules

**Version:** 2.0.0
**Updated:** 2025-12-28

---

## Core Rules

### 1. Safety First

- **NEVER enable SCPI outputs** without user confirmation
- **ALWAYS verify settings** before applying
- **ALWAYS timeout network commands** (2-3 seconds)
- **LOG equipment interactions**

### 2. Document Everything

- Update `docs/hardware-inventory.md` for hardware changes
- Create session summaries for significant work
- Commit all changes to git

### 3. GitHub for Tasks

Use `gh` CLI for all GitHub operations:

```bash
# List issues
gh issue list --repo unmanned-systems-uk/homelab

# Create issue
gh issue create --title "..." --body "..." --repo unmanned-systems-uk/homelab

# Update label
gh issue edit <number> --add-label "in-progress" --repo unmanned-systems-uk/homelab
```

**Never close issues** - user closes issues.

### 4. Git All Changes

```bash
git add -A
git commit -m "Description"
git push
```

### 5. Session Summaries

For significant work: `docs/session-summary-YYYY-MM-DD.md`

---

## Prohibited Actions

1. DO NOT enable SCPI outputs without confirmation
2. DO NOT push destructive changes without approval
3. DO NOT store secrets in git
4. DO NOT ignore errors silently
5. DO NOT close GitHub issues

---

## Error Recovery

### Equipment Not Responding

1. Check: `ping 10.0.1.X`
2. Check port: `nc -zv 10.0.1.X PORT`
3. Report to user
4. Do NOT retry indefinitely

### Network Issues

1. Document the issue
2. Continue with available resources
3. Note in session summary

---

## SCPI Safety Checklist

Before any SCPI operation that enables output:

- [ ] User has explicitly confirmed the action
- [ ] Voltage/current settings are verified
- [ ] Load is connected (if applicable)
- [ ] Timeout is set on command

---

*Simple rules for effective homelab management*
