# Open WebUI - Fork and Customize Guide

**Created:** 2025-12-15
**Purpose:** Build 100% customized HomeLab AI from Open WebUI source code

---

## YES - We Can Grab the Source! 🎯

**Open WebUI is fully open source:**
- **License:** MIT (permissive, commercial-friendly)
- **Repository:** https://github.com/open-webui/open-webui
- **Language:** Svelte (frontend) + Python FastAPI (backend)
- **Size:** ~10,000 files, active development

**This means:** 100% customization, no restrictions for internal use

---

## Repository Structure

```
open-webui/
├── src/                    # Frontend (SvelteKit)
│   ├── routes/            # Pages and API routes
│   ├── lib/               # Components and utilities
│   ├── app.html           # Main HTML template
│   └── app.css            # Global styles
├── backend/               # Backend (Python FastAPI)
│   ├── apps/              # Application modules
│   ├── data/              # Data directory (SQLite, uploads)
│   └── main.py            # FastAPI entry point
├── Dockerfile             # Build instructions
├── docker-compose.yaml    # Deployment config
├── package.json           # Frontend dependencies (npm)
└── requirements.txt       # Backend dependencies (pip)
```

**Tech Stack:**
- **Frontend:** SvelteKit + Vite + TailwindCSS
- **Backend:** Python 3.11 + FastAPI + SQLAlchemy
- **Database:** SQLite (default), PostgreSQL (optional)
- **Build:** Node.js 22 + Docker multi-stage build

---

## Build Process

### Standard Build (What They Ship)

```dockerfile
# Stage 1: Build frontend
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Python backend + serve frontend
FROM python:3.11-slim
COPY --from=build /app/build /app/build
COPY backend /app/backend
RUN pip install -r requirements.txt
CMD ["python", "backend/main.py"]
```

**Build time:** ~5-10 minutes (first build)

---

## Customization Levels

### Level 1: Simple Text/Logo Changes (30 minutes)

**What to change:**
- Application name
- Logo images
- Welcome messages
- Default system prompts
- Color scheme (TailwindCSS)

**Files to modify:**
- `src/app.html` - Page title, meta tags
- `src/lib/components/layout/Sidebar.svelte` - Logo, branding
- `src/lib/constants.ts` - App name, defaults
- `tailwind.config.js` - Color palette

**Example:**
```typescript
// src/lib/constants.ts
export const APP_NAME = 'HomeLab AI';
export const APP_DESCRIPTION = 'AI Assistant for HomeLab Infrastructure';
```

---

### Level 2: UI Customization (1-2 days)

**What to change:**
- Layout and navigation
- Chat interface styling
- Dashboard widgets
- Custom pages

**Files to modify:**
- `src/routes/+layout.svelte` - Main layout
- `src/routes/+page.svelte` - Homepage
- `src/lib/components/chat/` - Chat UI components

**Example: Add custom dashboard**
```svelte
<!-- src/routes/dashboard/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  let whisperStatus = 'loading...';

  onMount(async () => {
    // Fetch Whisper VM status
    const res = await fetch('http://10.0.1.201:11434/api/ps');
    const data = await res.json();
    whisperStatus = data.models.length + ' models running';
  });
</script>

<div class="homelab-dashboard">
  <h1>HomeLab Infrastructure</h1>
  <div class="status-card">
    <h2>Whisper VM</h2>
    <p>{whisperStatus}</p>
  </div>
</div>
```

---

### Level 3: Feature Addition (1-2 weeks)

**What to add:**
- Custom MCP integrations (native UI, not just tools)
- CCPM project management dashboard
- Infrastructure monitoring widgets
- Direct SSH terminal (xterm.js)
- File browser for Whisper VM

**New files to create:**
```
src/
  routes/
    homelab/
      +page.svelte              # HomeLab main page
      infrastructure/
        +page.svelte            # Infrastructure status
      whisper/
        terminal/+page.svelte   # SSH terminal
        models/+page.svelte     # Ollama model manager
```

**Backend API additions:**
```python
# backend/apps/homelab/__init__.py
from fastapi import APIRouter
import asyncssh

router = APIRouter(prefix="/api/homelab")

@router.get("/whisper/gpu")
async def get_gpu_status():
    async with asyncssh.connect('10.0.1.201', username='ccpm') as conn:
        result = await conn.run('nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv')
        return {"output": result.stdout}
```

---

## Fork Process

### Step 1: Fork on GitHub

```bash
# Option A: Fork via GitHub UI
# 1. Go to https://github.com/open-webui/open-webui
# 2. Click "Fork" button
# 3. Create fork under: unmanned-systems-uk/homelab-webui

# Option B: Fork via gh CLI
gh repo fork open-webui/open-webui --clone=false --remote=false
gh repo create unmanned-systems-uk/homelab-webui --public
```

---

### Step 2: Clone Fork

```bash
cd ~/ccpm-workspace/HomeLab
git clone https://github.com/unmanned-systems-uk/homelab-webui.git
cd homelab-webui

# Add upstream remote to track Open WebUI updates
git remote add upstream https://github.com/open-webui/open-webui.git
git fetch upstream
```

---

### Step 3: Make Customizations

**Quick branding update:**

```bash
# Change app name
sed -i 's/"open-webui"/"homelab-ai"/g' package.json
sed -i 's/Open WebUI/HomeLab AI/g' src/app.html

# Update title
echo 'export const APP_NAME = "HomeLab AI";' >> src/lib/constants.ts

# Commit changes
git add .
git commit -m "Rebrand to HomeLab AI"
git push origin main
```

---

### Step 4: Build Custom Image

```bash
# Build Docker image
docker build -t homelab-ai:latest .

# Or with specific features
docker build \
  --build-arg USE_CUDA=false \
  --build-arg USE_OLLAMA=true \
  -t homelab-ai:latest .
```

**Build time:** 5-10 minutes (first build), 1-2 minutes (rebuilds with cache)

---

### Step 5: Deploy Custom Image

```bash
# Stop current Open WebUI
ssh ccpm@10.0.1.202 "docker stop open-webui && docker rm open-webui"

# Deploy HomeLab AI
ssh ccpm@10.0.1.202 "docker run -d \
  --name homelab-ai \
  --network openwebui-net \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://10.0.1.201:11434 \
  -e WEBUI_NAME='HomeLab AI' \
  -v open-webui:/app/backend/data \
  homelab-ai:latest"

# Update Nginx to point to new container
# (or keep using 'open-webui' container name)
```

---

## Maintaining Your Fork

### Sync with Upstream Updates

```bash
cd ~/ccpm-workspace/HomeLab/homelab-webui

# Fetch upstream changes
git fetch upstream

# Merge upstream main into your fork
git merge upstream/main

# Resolve conflicts (if any)
# Test locally
# Push to your fork
git push origin main

# Rebuild Docker image
docker build -t homelab-ai:latest .
```

**Frequency:** Check for updates weekly, merge monthly

---

### Development Workflow

**Local development (hot reload):**

```bash
# Terminal 1: Start backend
cd backend
pip install -r requirements.txt
./start.sh

# Terminal 2: Start frontend dev server
npm install
npm run dev

# Access at http://localhost:5173
# Changes auto-reload
```

**Test before deploying:**
1. Make changes locally
2. Test in dev environment
3. Build Docker image
4. Test Docker image locally
5. Deploy to Harbor VM

---

## Customization Examples

### Example 1: HomeLab Green Theme

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f7f0',
          100: '#b3e6d1',
          500: '#00A86B',  // HomeLab green
          900: '#004d32',
        },
      },
    },
  },
};
```

### Example 2: Custom Sidebar Logo

```svelte
<!-- src/lib/components/layout/Sidebar.svelte -->
<script>
  const LOGO_URL = '/static/homelab-logo.svg';
  const APP_NAME = 'HomeLab AI';
</script>

<div class="sidebar-header">
  <img src={LOGO_URL} alt={APP_NAME} class="h-8 w-8" />
  <span class="text-xl font-bold">{APP_NAME}</span>
</div>
```

### Example 3: Add Infrastructure Page

```svelte
<!-- src/routes/infrastructure/+page.svelte -->
<script>
  import { onMount } from 'svelte';

  let vms = [];

  onMount(async () => {
    // Fetch from HomeLab MCP server
    const res = await fetch('http://10.0.1.202:8080/api/infrastructure/vms');
    vms = await res.json();
  });
</script>

<div class="container">
  <h1>HomeLab Infrastructure</h1>

  <div class="grid grid-cols-3 gap-4">
    {#each vms as vm}
      <div class="card">
        <h3>{vm.name}</h3>
        <p>Status: {vm.status}</p>
        <p>IP: {vm.ip}</p>
      </div>
    {/each}
  </div>
</div>
```

---

## Pros and Cons

### Advantages ✅

1. **100% Control**
   - Change anything and everything
   - Add HomeLab-specific features
   - Deep CCPM integration possible

2. **No Licensing Issues**
   - MIT license allows full modification
   - Can use for commercial purposes
   - No branding restrictions for internal use (<50 users)

3. **Learn the Codebase**
   - Understand how Open WebUI works
   - Contribute features upstream
   - Fix bugs yourself

4. **Custom Features**
   - Infrastructure monitoring
   - CCPM project dashboard
   - Direct VM controls
   - Whisper management UI

### Disadvantages ❌

1. **Maintenance Burden**
   - Must merge upstream updates manually
   - Conflicts need resolution
   - Security patches require attention

2. **Build Time**
   - First build: 5-10 minutes
   - Rebuilds: 1-2 minutes
   - Deployment slower than pulling image

3. **Complexity**
   - Need to understand Svelte + Python
   - Frontend build tools (Vite, TailwindCSS)
   - Debugging custom issues

4. **Update Lag**
   - Upstream gets new features first
   - Your fork needs manual merging
   - May fall behind if not maintained

---

## Recommended Approach

### Phase 1: Test with Upstream Image (Now)

**What:** Use official `ghcr.io/open-webui/open-webui:main`

**Why:**
- Fast to deploy
- Well-tested
- Easy updates
- Can customize via env vars and CSS

**Duration:** 1-2 weeks (MCP testing phase)

---

### Phase 2: Fork for Branding (If Needed)

**When:** After confirming Open WebUI meets our needs

**Changes:**
- Application name → "HomeLab AI"
- Logo and colors → HomeLab theme
- Remove/modify Open WebUI branding
- Add "HomeLab Edition" footer

**Effort:** 1-2 days

**Maintenance:** Low (only branding changes, rare conflicts)

---

### Phase 3: Custom Features (Long-term)

**When:** If we need features not available upstream

**Examples:**
- Native CCPM integration
- Infrastructure dashboard
- Whisper VM controls
- Custom authentication

**Effort:** 1-2 weeks per major feature

**Maintenance:** Ongoing (merge upstream monthly)

---

## Decision Matrix

| Approach | Effort | Control | Maintenance | Updates | Recommended For |
|----------|--------|---------|-------------|---------|-----------------|
| **Upstream Image** | None | Low | None | Auto | Testing, quick start |
| **Fork + Branding** | 1-2 days | Medium | Low | Manual | Custom look, same features |
| **Fork + Features** | Weeks | High | High | Manual | Unique requirements |

---

## My Recommendation

**Start with upstream, fork later if needed:**

1. **Now (Week 1-2):**
   - Use official Open WebUI image
   - Test MCP integration
   - Customize via env vars only
   - Document what works/doesn't

2. **Decision Point (Week 3):**
   - If MCP + env vars meet needs → **Stay on upstream** ✅
   - If we need heavy customization → **Fork and customize**

3. **Long-term:**
   - If upstream is sufficient → Track their releases, use stable tags
   - If we forked → Merge upstream monthly, maintain HomeLab fork

---

## Quick Start: Fork Now

**If you want to fork immediately:**

```bash
# 1. Create fork on GitHub
gh repo fork open-webui/open-webui \
  --org unmanned-systems-uk \
  --fork-name homelab-webui

# 2. Clone locally
cd ~/ccpm-workspace/HomeLab
git clone git@github.com:unmanned-systems-uk/homelab-webui.git

# 3. Make simple branding changes
cd homelab-webui
sed -i 's/Open WebUI/HomeLab AI/g' src/app.html package.json

# 4. Build custom image
docker build -t homelab-ai:latest .

# 5. Test locally
docker run -p 3000:8080 homelab-ai:latest

# 6. Deploy to Harbor
# (save image, load on Harbor, deploy)
```

---

## Next Steps

**Option A: Fork immediately** (if you want full control now)
**Option B: Test upstream first** (recommended - less work, evaluate needs)

**Your decision?**

