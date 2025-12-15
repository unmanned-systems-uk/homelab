# Open WebUI Customization Guide - HomeLab

**Created:** 2025-12-15
**Purpose:** Document customization capabilities for making Open WebUI "ours"

---

## Current Setup

**Deployment:**
- Container: `ghcr.io/open-webui/open-webui:main` (latest)
- Location: Harbor VM (10.0.1.202)
- Access: https://10.0.1.202:3443 (HTTPS via Nginx)
- Data: `/app/backend/data` (SQLite database + uploads)

**Version:** v0.6.31+ (includes MCP support)

---

## Customization Levels

### Level 1: Admin Settings (No Code Required) ✅

**What You Can Do:**
- Configure models and connections
- User management and permissions
- Add external tools (MCP servers, functions, tools)
- System prompts and model parameters
- API keys and integrations

**How:** Admin Panel → Settings (accessible from UI)

**Limitations:**
- Cannot change branding/logo
- Cannot modify UI layout
- Cannot customize colors/themes

---

### Level 2: Environment Variables (Config Only) ⚠️

**What You Can Do:**
- Set default user roles
- Configure authentication providers (OIDC, LDAP)
- Enable/disable features
- Set rate limits
- Configure file upload sizes

**How:** Modify `docker run` command or docker-compose.yml

**Example Environment Variables:**
```bash
-e ENABLE_SIGNUP=false                    # Disable new user signups
-e DEFAULT_USER_ROLE=pending              # New users need approval
-e WEBUI_NAME="HomeLab AI"                # Page title (NOT logo)
-e ENABLE_RAG_WEB_SEARCH=true             # Enable web search
-e ENABLE_IMAGE_GENERATION=false          # Disable image gen
-e MAX_FILE_SIZE_MB=25                    # Upload size limit
```

**Limitations:**
- Cannot change visual appearance
- Basic configuration only

---

### Level 3: Custom CSS Injection (Medium Difficulty) ⚙️

**What You Can Do:**
- Change colors (background, text, accents)
- Modify fonts and typography
- Adjust spacing and layout
- Hide/show UI elements
- Add custom branding elements

**How:** Inject CSS file into Docker container

**Approach:**
```bash
# 1. Create custom.css file
cat > /tmp/custom.css << 'EOF'
/* Custom HomeLab branding */
:root {
  --color-primary: #00A86B;      /* HomeLab green */
  --color-secondary: #1E3A8A;    /* Dark blue */
}

/* Hide default logo, add custom text */
.logo-container {
  background-image: url('data:image/svg+xml;base64,...');
}

/* Customize chat interface */
.chat-message {
  border-left: 3px solid var(--color-primary);
}
EOF

# 2. Copy into container
ssh ccpm@10.0.1.202 "docker cp /tmp/custom.css open-webui:/app/backend/static/custom.css"

# 3. Inject via environment variable
# WEBUI_CUSTOM_CSS="/app/backend/static/custom.css"
```

**Limitations:**
- CSS only (no HTML structure changes)
- May break with Open WebUI updates
- Requires Docker restart

---

### Level 4: Custom Docker Build (High Difficulty) 🔨

**What You Can Do:**
- Full UI customization (React components)
- Add custom features and pages
- Modify backend logic
- Complete branding replacement
- Add custom integrations

**How:** Fork repository, modify code, build custom image

**Process:**
```bash
# 1. Fork repository
git clone https://github.com/open-webui/open-webui.git
cd open-webui

# 2. Make changes
# - Modify frontend: /frontend/src/
# - Modify backend: /backend/
# - Change branding: logos, colors, text

# 3. Build custom image
docker build -t homelab-webui:latest .

# 4. Deploy custom image
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  homelab-webui:latest
```

**Advantages:**
- ✅ Complete control over UI and functionality
- ✅ Can add custom features not available upstream
- ✅ Full branding customization

**Disadvantages:**
- ❌ High maintenance burden (track upstream updates)
- ❌ Requires React and Python knowledge
- ❌ Longer build times
- ❌ Need to manage custom update process

---

## Licensing Considerations

### Open Source (Free) - Community Edition

**Allowed for HomeLab (≤50 users):**
- ✅ Fully rebrand if you want
- ✅ Modify source code
- ✅ Deploy internally
- ✅ Add custom features

**Branding Protection (April 2025):**
- For deployments with **>50 users**, must keep Open WebUI branding
- HomeLab is internal, <50 users → **Full customization allowed**

**License:** MIT License (permissive)

**Sources:**
- [Open WebUI License](https://docs.openwebui.com/license/)
- [Logo customization discussion](https://github.com/open-webui/open-webui/discussions/7503)

### Enterprise Edition (Paid)

**Additional Features:**
- Built-in custom branding UI (no code needed)
- SLA support
- LTS versions
- Priority support

**Pricing:** Contact Open WebUI team

---

## Recommended Approach for HomeLab

### Option A: Minimal Customization (Recommended) ⭐

**Strategy:** Use Open WebUI as-is, customize via admin settings only

**Pros:**
- ✅ No maintenance burden
- ✅ Easy updates (just pull latest image)
- ✅ Stable and well-tested
- ✅ MCP integration works out of box

**Cons:**
- ⚠️ Generic branding (Open WebUI logo)
- ⚠️ Limited color customization

**Best For:** Quick deployment, focus on functionality over aesthetics

---

### Option B: CSS Customization (Moderate)

**Strategy:** Add custom CSS for HomeLab branding

**What to Customize:**
```css
/* HomeLab theme example */
:root {
  /* Colors */
  --color-primary: #00A86B;           /* HomeLab green */
  --color-gray-50: #1a1a1a;           /* Dark theme background */

  /* Typography */
  --font-primary: 'Inter', sans-serif;
}

/* Add "HomeLab Edition" text */
.sidebar-footer::after {
  content: "HomeLab Edition";
  font-size: 0.75rem;
  opacity: 0.5;
}
```

**Implementation:**
1. Create `homelab-theme.css`
2. Mount as volume in docker-compose.yml
3. Set environment variable pointing to CSS file

**Pros:**
- ✅ Custom colors and fonts
- ✅ Lightweight (no full rebuild)
- ✅ Can update Open WebUI easily

**Cons:**
- ⚠️ CSS may break with major updates
- ⚠️ Limited to visual changes only

**Best For:** Branding without heavy customization

---

### Option C: Custom Fork (Advanced)

**Strategy:** Fork Open WebUI, add HomeLab-specific features

**What to Add:**
- Custom dashboard showing HomeLab infrastructure status
- Integration with CCPM project management
- Whisper VM controls (native UI, not just MCP tools)
- Custom authentication (integrate with existing systems)

**Pros:**
- ✅ Complete control
- ✅ Can add HomeLab-specific workflows
- ✅ Deep CCPM integration possible

**Cons:**
- ❌ High maintenance (merge upstream updates)
- ❌ Requires React + Python expertise
- ❌ Longer deployment cycle

**Best For:** Long-term platform with unique requirements

---

## Quick Customization Test

### Test 1: Change Page Title (Easy)

**Without rebuilding:**
```bash
ssh ccpm@10.0.1.202 "docker stop open-webui && docker rm open-webui"
ssh ccpm@10.0.1.202 "docker run -d \
  --name open-webui \
  --network openwebui-net \
  -p 3000:8080 \
  -e WEBUI_NAME='HomeLab AI Assistant' \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main"
```

**Result:** Browser tab shows "HomeLab AI Assistant" instead of "Open WebUI"

---

### Test 2: Disable User Signups (Easy)

**Prevent random users from creating accounts:**
```bash
-e ENABLE_SIGNUP=false
-e DEFAULT_USER_ROLE=pending    # Require admin approval
```

---

### Test 3: Custom Welcome Message (Medium)

**Add custom system prompt:**
1. Login as admin
2. Settings → System Prompts
3. Add default prompt:
   ```
   You are HomeLab AI Assistant, helping with infrastructure management,
   CCPM project tasks, and AI model development. You have access to tools
   for managing Whisper VM, Ollama models, and system resources.
   ```

---

## What I Recommend for HomeLab

**Short-term (Now):**
1. ✅ Keep current Open WebUI deployment (latest image)
2. ✅ Add MCP server integration (testing phase)
3. ✅ Use admin settings for customization
4. ✅ Set `WEBUI_NAME="HomeLab AI"` for page title

**Medium-term (After MCP testing):**
5. Add custom CSS theme (HomeLab colors/fonts)
6. Create custom welcome dashboard page (CSS injection)
7. Add HomeLab logo via CSS background-image

**Long-term (If needed):**
8. Evaluate custom fork if we need features not available upstream
9. Consider Enterprise license if we expand beyond 50 users

---

## Technical Details

### Docker Compose Configuration (Recommended)

```yaml
version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    network_mode: bridge
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_BASE_URL=http://10.0.1.201:11434
      - WEBUI_NAME=HomeLab AI Assistant
      - ENABLE_SIGNUP=false
      - DEFAULT_USER_ROLE=pending
      - ENABLE_RAG_WEB_SEARCH=true
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}  # Generate with: openssl rand -hex 32
    volumes:
      - open-webui:/app/backend/data
      - ./custom-theme.css:/app/backend/static/custom.css:ro  # Optional: custom CSS
    restart: unless-stopped

  nginx-ssl:
    image: nginx:alpine
    container_name: nginx-ssl
    ports:
      - "3443:3443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - open-webui
    restart: unless-stopped

volumes:
  open-webui:
```

### Environment Variables Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `WEBUI_NAME` | "Open WebUI" | Page title (browser tab) |
| `ENABLE_SIGNUP` | true | Allow new user registration |
| `DEFAULT_USER_ROLE` | "user" | Role for new users (user/pending/admin) |
| `OLLAMA_BASE_URL` | - | Ollama API endpoint |
| `ENABLE_RAG_WEB_SEARCH` | false | Enable web search in RAG |
| `ENABLE_IMAGE_GENERATION` | false | Enable image generation |
| `MAX_FILE_SIZE_MB` | 25 | Max upload size |
| `WEBUI_SECRET_KEY` | auto-generated | Session encryption key |

---

## Next Steps

**To customize Open WebUI for HomeLab:**

1. **Test simple customization** (5 minutes):
   - Change page title to "HomeLab AI"
   - Disable public signups
   - Add custom welcome message

2. **Evaluate CSS theming** (1 hour):
   - Create custom CSS with HomeLab colors
   - Test injection method
   - Document update process

3. **Decide on long-term approach** (after testing):
   - Stay with community edition + CSS?
   - Consider custom fork?
   - Evaluate Enterprise license?

---

## Resources

- [Open WebUI Documentation](https://docs.openwebui.com/)
- [GitHub Repository](https://github.com/open-webui/open-webui)
- [Custom Themes Guide](https://dev.to/code42cate/how-to-build-custom-open-webui-themes-55hh)
- [License Information](https://docs.openwebui.com/license/)
- [Logo Discussion](https://github.com/open-webui/open-webui/discussions/7503)

---

**Status:** Ready for testing
**Recommendation:** Start with Option A (minimal) + simple env var changes
