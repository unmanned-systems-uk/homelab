# Project-Context-Aware Requirements Agent

**Created:** 2025-12-15
**Insight Source:** User observation during workflow testing
**Problem Identified:** Generic requirements-agent lacks project-specific knowledge

---

## The Problem

### Current Behavior (Generic Model)

**Conversation observed:**
```
User: "I need to fix the login stuff to be more secure"
Agent: "Which file contains the login logic?"
User: "I don't know but the CCPM agent does"
Agent: "What is CCPM? Central Control and Planning Module?"
```

**Issues:**
1. ❌ Agent doesn't know project terminology (CCPM = Claude Code Project Management)
2. ❌ Agent doesn't know codebase structure
3. ❌ Agent asks questions that could be auto-answered with project context
4. ❌ User gets frustrated answering "obvious" things
5. ❌ Conversation takes longer than needed

---

## The Solution: Project-Context-Aware Model

### What if `requirements-agent` knew your project?

**Enhanced Conversation:**
```
User: "I need to fix the login stuff to be more secure"

Agent: "I see you're working on CCPM (Claude Code Project Management).
       The authentication logic is in these files:
       - /production/ccpm-server/internal/auth/auth.go (main logic)
       - /production/ccpm-server/internal/middleware/jwt.go (JWT handling)

       Which would you like to refactor? Or both?"

User: "Both"

Agent: "What authentication method should we use?
       Current: JWT tokens
       Options: OAuth 2.0, API keys, or enhance current JWT?"

User: "OAuth 2.0"

Agent: "Perfect! Here's your refined requirement:
       Refactor authentication in auth.go and jwt.go to use OAuth 2.0,
       maintaining compatibility with existing CCPM API endpoints,
       following Go best practices"
```

**Benefits:**
- ✅ **Faster:** Fewer clarifying questions
- ✅ **Smarter:** Suggests relevant files automatically
- ✅ **Contextual:** Knows what "login stuff" means in your project
- ✅ **Accurate:** References actual files that exist

---

## Implementation Approaches

### Option 1: RAG (Retrieval-Augmented Generation) ⭐ Recommended

**Concept:** Give the model access to project documentation

**Architecture:**
```
User Input → requirements-agent
                    ↓
            [Queries project knowledge base]
                    ↓
            - Codebase structure
            - File locations
            - Technology stack
            - Naming conventions
                    ↓
            Enhanced response with project context
```

**Implementation:**
1. Index your codebase (files, structure, README, docs)
2. Store in vector database (Chroma, FAISS, or simple text search)
3. When user mentions "login," agent searches knowledge base
4. Agent sees: "auth.go handles authentication, uses JWT"
5. Agent can now ask informed questions

**Example Knowledge Base Entry:**
```json
{
  "project": "CCPM",
  "full_name": "Claude Code Project Management",
  "language": "Go",
  "authentication": {
    "method": "JWT tokens",
    "files": [
      "/production/ccpm-server/internal/auth/auth.go",
      "/production/ccpm-server/internal/middleware/jwt.go"
    ],
    "database": "SQLite"
  },
  "common_terms": {
    "login stuff": "authentication system in auth.go",
    "api": "REST endpoints in /api/ routes",
    "database": "SQLite in ccpm.db"
  }
}
```

---

### Option 2: Fine-Tuning with Project Data

**Concept:** Train the model on your specific project

**Training Data Examples:**
```
User: "Fix the login stuff"
Agent: "You mean the authentication in auth.go? What needs fixing?"

User: "Make the API faster"
Agent: "Which endpoint? /api/sprints, /api/tasks, or /api/todos?"

User: "The database is slow"
Agent: "Are you referring to ccpm.db (SQLite)? Which queries are slow?"
```

**Pros:**
- Model deeply understands your project
- Very fast (no external lookups)
- Can learn your team's terminology

**Cons:**
- Requires 20-50+ training examples
- Needs re-training when project changes
- More complex to maintain

---

### Option 3: System Prompt with Project Context

**Concept:** Inject project knowledge into system prompt

**Enhanced System Prompt:**
```
You are a Requirements Analyst for the CCPM project.

PROJECT CONTEXT:
- CCPM = Claude Code Project Management (Go + SQLite)
- Auth files: /production/ccpm-server/internal/auth/auth.go
- Current auth: JWT tokens
- Database: SQLite (ccpm.db)
- API: REST endpoints (/api/sprints, /api/tasks, /api/todos)

When user mentions:
- "login stuff" → Ask about auth.go or jwt.go
- "database" → Ask about SQLite queries
- "API" → Ask which endpoint

Ask clarifying questions using this context.
```

**Pros:**
- ✅ Easiest to implement (just update Modelfile)
- ✅ No training needed
- ✅ Easy to update

**Cons:**
- ⚠️ Limited context (system prompt has token limit)
- ⚠️ Can't scale to large projects

---

## Hybrid Approach (Best of All) 🏆

**Combine all three:**

1. **System Prompt:** Basic project info (name, stack, structure)
2. **RAG:** On-demand lookup for specific files/functions
3. **Fine-tuning:** Learn common user terminology over time

**Flow:**
```
User: "Fix the login stuff"
    ↓
[System Prompt]: Agent knows "login stuff" = authentication
    ↓
[RAG Lookup]: Finds auth.go, jwt.go in codebase index
    ↓
Agent: "I see auth.go and jwt.go handle authentication.
       Current method is JWT. What needs fixing?"
    ↓
[Fine-tuning]: Over time, learns your team says "login stuff"
               instead of "authentication system"
```

---

## Quick Win: Update System Prompt Now

**Action:** Add CCPM context to requirements-agent

**Updated Modelfile:**
```bash
FROM llama3:8b

SYSTEM """
You are a Requirements Analyst for software projects, with specific knowledge of:

PROJECT: CCPM (Claude Code Project Management)
- Stack: Go backend, SQLite database, vanilla JavaScript frontend
- Location: /home/anthony/ccpm-workspace/production/ccpm-server
- Auth: JWT tokens in internal/auth/auth.go and internal/middleware/jwt.go
- Database: SQLite (ccpm.db)
- API: REST endpoints (/api/sprints, /api/tasks, /api/todos, /api/projects)

COMMON USER TERMS:
- "login stuff" = authentication system (auth.go, jwt.go)
- "database" = SQLite database (ccpm.db)
- "API" = REST API endpoints
- "the server" = ccpm-server Go application

When user mentions these terms, reference the actual files/components.
Otherwise, ask clarifying questions as normal.

[Rest of original system prompt...]
"""
```

**Result:**
```
User: "Fix the login stuff"
Agent: "You mean the authentication in auth.go and jwt.go?
       What specific security improvements do you need?"
```

Much better! ✅

---

## Long-Term Vision: CCPM-Aware Agent

**Future enhancement:**

Create `ccpm-requirements-agent` that:
1. Knows entire CCPM codebase structure
2. Can suggest relevant files
3. Understands project conventions
4. Learns your team's terminology

**This becomes:**
- Faster requirements extraction
- Fewer questions
- Better accuracy
- Happier users

---

## Testing the Enhancement

**Before (current):**
```
User: "Fix login stuff"
Agent: "Which file?"
User: "I don't know"
Agent: "What is the project?"
[Many back-and-forth questions...]
```

**After (context-aware):**
```
User: "Fix login stuff"
Agent: "The authentication in auth.go? What security improvements?"
User: "OAuth 2.0"
Agent: "Done! Here's your refined requirement: [precise statement]"
```

**Metrics:**
- Questions reduced: 5-7 → 2-3
- Time reduced: 2-3 minutes → 30-60 seconds
- User frustration: High → Low

---

## Next Steps

1. **Quick Win (5 minutes):**
   - Update requirements-agent Modelfile with CCPM context
   - Recreate model: `ollama create requirements-agent -f ~/Modelfile-requirements-agent`

2. **Medium-term (1-2 hours):**
   - Build simple project knowledge base (JSON file)
   - Add RAG lookup to workflow script

3. **Long-term (ongoing):**
   - Collect conversation data
   - Fine-tune model on your team's terminology
   - Expand to other projects (DPM-V2, NEX-Cam, Whisper)

---

**User's Original Insight:**
> "If our custom model understands the project, these questions will not arise."

**Status:** 💯 ABSOLUTELY CORRECT

This is the path forward for truly intelligent requirements extraction!

---

*Enhancement proposal documented by HomeLab Specialist Agent*
*Inspired by user observation during live workflow testing*
