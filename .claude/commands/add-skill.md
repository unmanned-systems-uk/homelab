# Add Skill Knowledge

Capture newly learned information and add it to the appropriate skill knowledge base.

## Purpose

When you learn something new during a session (troubleshooting techniques, configuration patterns, tool usage), this command captures that knowledge and adds it to the relevant skill for future reference.

---

## Usage

User invokes: `/add-skill`

Then specify:
1. **What was learned** - Brief description
2. **Skill to update** - Which skill this belongs to (infrastructure, scpi-automation, database, etc.)
3. **Category** - What section to add it to (patterns, troubleshooting, configuration, tools, etc.)

---

## Instructions

### Step 1: Identify What Was Learned

Ask yourself:
- What problem did we just solve?
- What configuration/pattern did we discover?
- What tool behavior did we learn?
- What best practice emerged?

### Step 2: Determine Target Skill

**Available Skills:**
- `infrastructure` - Proxmox, Docker, networking (UniFi), storage
- `scpi-automation` - Test equipment control and automation
- `database` - PostgreSQL, homelab_db, ccpm_db operations
- `[future skills as needed]`

### Step 3: Add to Skill Knowledge

Read the skill's `SKILL.md` file and add the new knowledge to the appropriate section:

**Common Sections:**
- **Patterns** - Reusable configuration patterns, templates
- **Troubleshooting** - Solutions to specific problems
- **Configuration** - Specific settings and their meanings
- **Tools** - Tool usage patterns and best practices
- **Checklists** - Pre/post task verification steps

### Step 4: Format the Addition

Use this format:

````markdown
### [Topic Name] (LEARNED: YYYY-MM-DD)

**Context:** [What problem/situation led to this learning]

**Solution/Pattern:**
```
[Configuration, command, or pattern]
```

**Why This Works:**
- [Explanation point 1]
- [Explanation point 2]

**When to Use:**
- [Use case 1]
- [Use case 2]

**Related:**
- [Links to docs, GitHub issues, session summaries]
````

---

## Example Usage

**User:** `/add-skill`

**You respond:**
```
I'll add the knowledge we just gained. What did we learn?

Recent session context:
- HA Pi network failure troubleshooting
- UniFi storm control configuration
- STP/Loop Protection settings

Which should I capture?
```

**User:** "The UniFi port configuration for storm control and loop protection"

**You:**
```
Adding to: .claude/skills/infrastructure/SKILL.md
Section: UniFi Port Configuration
Category: Troubleshooting > Network Stability

[Shows the new section being added]
```

---

## Auto-Capture During /eod

The `/eod` command now includes a step to review the session and identify learnings:

```
## Skill Knowledge Updates

During this session, we learned:
- [ ] UniFi storm control configuration (pKts/s thresholds)
- [ ] Loop Protection = STP Edge Port in UniFi
- [ ] Medical-critical network hardening patterns

Should I add these to skills? (Y/n)
```

---

## Skill Knowledge Principles

### What to Capture:

✅ **Capture:**
- Configuration patterns that solved real problems
- Tool behaviors discovered through troubleshooting
- Best practices learned through experience
- Settings and their actual effects (not documentation copy)
- Troubleshooting procedures that worked

❌ **Don't Capture:**
- One-off fixes specific to single issue
- Information already well-documented elsewhere
- Temporary workarounds
- Obvious/common knowledge

### Quality Over Quantity:

- **Be specific:** "Storm control: Broadcast 100 kpps prevents HA Pi network drops"
- **Not generic:** "Storm control prevents network problems"

- **Include context:** "Loop Protection enabled on uplink ports prevents STP blocking during topology changes"
- **Not vague:** "Enable loop protection"

---

## Skill File Locations

```
.claude/skills/
├── infrastructure/
│   └── SKILL.md          # Proxmox, Docker, UniFi, networking
├── scpi-automation/
│   └── SKILL.md          # Test equipment patterns
├── database/
│   └── SKILL.md          # PostgreSQL, migrations, queries
└── [new-skill]/
    └── SKILL.md          # Created as needed
```

---

## Creating New Skills

If knowledge doesn't fit existing skills:

1. **Create new skill directory:** `.claude/skills/[skill-name]/`
2. **Create SKILL.md** with structure:
   ```markdown
   # [Skill Name] Skill

   **Skill Name:** [skill-name]
   **Version:** 1.0.0

   ## Purpose
   [What this skill covers]

   ## Allowed Tools
   [Tools this skill can use]

   ## Patterns
   [Learned patterns and configurations]

   ## Resources
   [Documentation references]
   ```

3. **Document in CLAUDE.md** - Add to skills list

---

## Verification

After adding skill knowledge:

- [ ] Knowledge added to appropriate SKILL.md section
- [ ] Includes context (what problem it solved)
- [ ] Includes specific values/commands (not just concepts)
- [ ] Dated with (LEARNED: YYYY-MM-DD)
- [ ] Committed with descriptive message
- [ ] Cross-referenced to session summary or GitHub issue

---

## Git Commit Pattern

```bash
git add .claude/skills/[skill-name]/SKILL.md
git commit -m "skill: Add [topic] to [skill-name] knowledge base

Learned during [context/issue].

Added:
- [Specific pattern/config 1]
- [Specific pattern/config 2]

Solves: [Problem description]
Reference: [Session summary/issue link]
"
```

---

**Example:** Adding today's UniFi learning:

```bash
git add .claude/skills/infrastructure/SKILL.md
git commit -m "skill: Add UniFi storm control and STP configuration patterns

Learned during HA Pi network failure investigation (Issue #36).

Added:
- Storm control thresholds (pKts/s format)
- Loop Protection = STP Edge Port mapping
- Medical-critical network hardening patterns

Solves: Network drops during HA Pi service restarts
Reference: docs/session-summary-2026-01-10.md, Issue #36
"
```

---

*HomeLab Agent - Continuous Learning System*
*Version: 1.0*
