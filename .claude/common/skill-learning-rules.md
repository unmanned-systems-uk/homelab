# CRITICAL: Skill Learning Rules

**Priority:** CRITICAL - Core Learning System
**Applies to:** ALL sessions, ALL tasks
**Status:** ACTIVE

---

## Rule: Continuous Knowledge Capture

**When you learn something new during a session, you MUST capture it to skills.**

### What Triggers Skill Learning:

1. **Problem Solved** - You troubleshot and fixed an issue
2. **Configuration Discovered** - Found settings/values that work
3. **Tool Behavior Learned** - Discovered how a tool actually works
4. **Pattern Emerged** - Identified a reusable approach
5. **Best Practice Validated** - Confirmed what works in production

### Examples from Real Sessions:

✅ **Capture This:**
- "UniFi storm control uses pKts/s (kilo packets/second), not pps"
- "Loop Protection in UniFi = STP Edge Port / PortFast"
- "HA Pi network drops solved by: Storm Control 100/100/1000 + Loop Protection"
- "Medical-critical systems need <10% bandwidth storm thresholds"

❌ **Don't Capture This:**
- "Rebooted the server" (no learning)
- "Applied updates" (routine task)
- "Checked documentation" (no new knowledge)

---

## Mandatory Integration Points

### 1. During /eod Command

The `/eod` command MUST include a "Skill Knowledge Updates" section:

```markdown
## Skill Knowledge Updates

Review session for learnings:

**Potential Additions:**
- [ ] [Thing 1 learned]
- [ ] [Thing 2 learned]
- [ ] [Thing 3 learned]

Capture to skills? (default: yes)
```

**If user says yes or no response:** Capture learnings automatically

**If user says no:** Skip, but note in session summary

### 2. User Invokes /add-skill

**Immediate response:**
1. Review recent session context
2. Identify what was learned
3. Ask user which knowledge to capture
4. Add to appropriate skill
5. Commit with descriptive message

### 3. Proactive Identification

When you solve a significant problem, proactively suggest:

```
💡 I just learned: [specific knowledge]

This should be added to the [skill-name] skill for future reference.
Should I capture this now? (Y/n)
```

**Default to YES** - capture unless user says no

---

## Skill Knowledge Quality Standards

### Must Include:

1. **Context** - What problem/situation led to this
2. **Specific Values** - Actual numbers, settings, commands (not just concepts)
3. **Why It Works** - Technical explanation
4. **When to Use** - Applicable scenarios
5. **Date Learned** - (LEARNED: YYYY-MM-DD)
6. **Reference** - Link to session summary, GitHub issue, or documentation

### Format Example:

```markdown
### UniFi Storm Control Configuration (LEARNED: 2026-01-10)

**Context:** HA Pi network failures during service restarts (Issue #36)

**Configuration:**
```
Storm Control (pKts/s format - kilo packets per second):
- Broadcast:  100  (UI minimum)
- Multicast:  100  (tight) or 200 (permissive)
- Unicast:    1000 (67% of 1G link)
```

**Why This Works:**
- Limits traffic types that can flood network during service restarts
- Prevents STP port auto-disable from broadcast storms
- Values chosen for medical-critical systems (tight margins)

**When to Use:**
- Any uplink port in medical/critical infrastructure
- Ports connected to devices with aggressive service discovery (mDNS, Avahi)
- After experiencing network drops correlated with device restarts

**Related:**
- docs/session-summary-2026-01-10.md
- GitHub Issue #36
- Network: US 48 Port 14, US 24 Port 2
```

---

## Skill Selection Guide

| Topic | Target Skill |
|-------|-------------|
| UniFi, VLANs, switches, network | infrastructure |
| Proxmox, VMs, Docker | infrastructure |
| SCPI equipment, test automation | scpi-automation |
| PostgreSQL, schemas, queries | database |
| Home Assistant (when separate project) | homeassistant |
| New domain not covered | Create new skill |

---

## Commit Standards for Skill Updates

**Pattern:**
```bash
git commit -m "skill: Add [topic] to [skill-name]

Learned during [context].

Added:
- [Specific item 1]
- [Specific item 2]

Solves: [Problem]
Reference: [Link]
"
```

**Always:**
- Use `skill:` prefix for skill knowledge commits
- Reference the problem/issue that led to the learning
- Include specific items added (not generic "updated docs")
- Link to session summary or GitHub issue

---

## Knowledge Review Cadence

### Daily (End of Day):
- Review session for learnings
- Capture to skills via /eod

### Weekly (Session Summaries):
- Review past week's session summaries
- Identify patterns across multiple sessions
- Extract meta-learnings (higher-level patterns)

### Monthly:
- Review skill effectiveness
- Reorganize if needed
- Archive obsolete knowledge

---

## Knowledge Deprecation

**When to Remove/Update:**
- Technology version changed (old config no longer works)
- Better solution discovered
- Pattern no longer recommended

**How to Deprecate:**
```markdown
### [Old Pattern] ⚠️ DEPRECATED (2026-XX-XX)

**Deprecated Reason:** [Why no longer recommended]

**Replacement:** See [New Pattern] below

~~[Old content struck through]~~

**Migration Guide:**
- [How to migrate from old to new]
```

---

## Success Metrics

**Good skill knowledge:**
- Solves real problems you encountered
- Includes specific, actionable values
- Has clear context (why/when to use)
- Referenced in future sessions when similar problems arise

**Poor skill knowledge:**
- Generic advice from documentation
- No specific values (just concepts)
- No context for when to apply
- Never referenced again

---

## Integration with Agent Startup

Skills are loaded during `/start-homelab`:
1. Agent reads AGENT.md (identity)
2. Agent reads DOMAINS.md (domains managed)
3. **Agent reads all SKILL.md files** (accumulated knowledge)
4. Skills inform decision-making throughout session

---

**ENFORCEMENT:**

This is a **CRITICAL RULE** - not optional. Every session where you learn something must result in skill knowledge capture, either:
1. During the session (proactive suggestion)
2. During /eod (automated review)
3. Via /add-skill (user-directed)

**Failure to capture learnings = failure to improve = unacceptable**

---

*HomeLab Agent - Continuous Learning Enforcement*
*Status: ACTIVE - Mandatory Compliance*
*Created: 2026-01-10*
