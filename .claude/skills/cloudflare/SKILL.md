# Cloudflare Tunnel Skill

**Purpose:** Manage Cloudflare tunnels for secure external access to HomeLab services
**Account:** unmanned-systems.uk domain
**Dashboard:** https://one.dash.cloudflare.com (Zero Trust)

---

## Quick Reference

### Current Tunnels

| Tunnel | Status | Public URL | Routes To |
|--------|--------|------------|-----------|
| **homegate** | HEALTHY | https://homegate.unmanned-systems.uk | http://nginx:80 (Docker) |
| **unifi-mcp** | HEALTHY | https://mcp.unmanned-systems.uk | http://10.0.1.202:3001 |
| **unifi-mcp** | HEALTHY | https://homelab-mcp.unmanned-systems.uk | http://10.0.1.202:8080 |
| **unifi-mcp** | HEALTHY | https://github-mcp.unmanned-systems.uk | http://10.0.1.202:8082 |
| **unifi-mcp** | HEALTHY | https://ccpm-mcp.unmanned-systems.uk | http://10.0.1.202:9000 |
| **homeassist** | PENDING | https://homeassist.unmanned-systems.uk | http://10.0.1.150:8123 |

### Tunnel IDs

| Tunnel | Tunnel ID | Connector ID |
|--------|-----------|--------------|
| homegate | f424973c-5609-4e96-963c-4678906b093e | f817bdee-8ff3-4f92-b4e8-aefafed8a0a7 |
| unifi-mcp | 0b4a4e7a-670c-45ba-a013-1ca26a3af3f4 | 309dd334-c0bf-4e8a-9dbe-312576301d13 |
| homeassist | f765a485-bb0b-4d28-8084-c36f96027e7f | -- |

---

## Dashboard Navigation

**IMPORTANT:** Tunnels are in Zero Trust dashboard, NOT the domain dashboard!

### Step-by-Step Navigation

1. **Go to Zero Trust Dashboard**
   - Direct URL: https://one.dash.cloudflare.com
   - Or: dash.cloudflare.com → "Back to Domains" → Zero Trust

2. **Navigate to Tunnels**
   - Left sidebar: **Networks** → **Connectors**
   - URL: one.dash.cloudflare.com/networks/connectors

3. **Menu Structure (Zero Trust)**
   ```
   Overview
   Insights
   Team & Resources
   Networks ←─────────┐
     ├─ Overview      │
     ├─ Connectors ←──┘ TUNNELS ARE HERE
     ├─ Routes
     └─ Resolvers & Proxies
   Access controls
   Traffic policies
   ...
   ```

---

## Creating a New Tunnel

### Step 1: Select Tunnel Type
- Click **"+ Create a tunnel"**
- Choose **Cloudflared** (Recommended)
- Click "Select Cloudflared"

### Step 2: Name Your Tunnel
- Enter descriptive name (e.g., `homegate`, `my-service`)
- Click **"Save tunnel"**

### Step 3: Get the Token
- Select **Docker** environment
- Copy the command:
  ```bash
  docker run cloudflare/cloudflared:latest tunnel --no-autoupdate run --token eyJhIjoiZj...
  ```
- **THE TOKEN** is everything after `--token` (starts with `eyJ`)
- Click **"Next"**

### Step 4: Configure Route
- **Subdomain:** Your service name (e.g., `homegate`)
- **Domain:** Select `unmanned-systems.uk`
- **Type:** HTTP (or HTTPS if origin uses SSL)
- **URL:** Internal service address
  - Docker: Use container name (e.g., `nginx:80`)
  - Network: Use IP:port (e.g., `10.0.1.150:8123`)
- Click **"Complete setup"**

---

## Docker Deployment

### docker-compose.yml

```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: my-cloudflared
    restart: unless-stopped
    command: tunnel --no-autoupdate run
    environment:
      - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}
    networks:
      - app-network
    depends_on:
      - my-service
```

### .env file

```bash
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiZjI5MWQzOGU5YTM4OWE1Njcz...
```

### Two Ways to Pass Token

1. **Environment Variable (Recommended):**
   ```yaml
   command: tunnel --no-autoupdate run
   environment:
     - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}
   ```

2. **Command Flag:**
   ```yaml
   command: tunnel --no-autoupdate run --token eyJhIjoiZj...
   ```

### Docker Network Routing

When cloudflared is in the same Docker network as your service:
- Use container name as URL: `http://nginx:80`
- NOT localhost or 127.0.0.1

---

## Getting an Existing Token

1. Go to **Networks** → **Connectors**
2. Click on tunnel name (e.g., `homegate`)
3. Click **"Configure"** (or 3 dots → Configure)
4. On **Overview** tab, select **Docker** environment
5. Copy token from the command

### Token Format
- Starts with `eyJ` (Base64-encoded JWT)
- Example: `eyJhIjoiZjI5MWQzOGU5YTM4OWE1NjczNGUxYTkyZjg5ZGQyOGMi...`

### Refresh Token
- In tunnel config → "Refresh token" section
- **WARNING:** Invalidates previous token immediately
- Existing connections continue but new ones require new token

---

## Managing Routes

### View Routes
1. Click tunnel → **Configure**
2. Go to **Published application routes** tab

### Add Route
1. Click **"+ Add a published application route"**
2. Fill in:
   - Subdomain (optional)
   - Domain (required)
   - Path (optional)
   - Service Type (HTTP/HTTPS/TCP/etc.)
   - Service URL

### Edit Route
1. Click 3 dots next to route → **Edit**
2. Modify settings
3. Save

### Delete Route
1. Click 3 dots next to route → **Delete**
2. Confirm deletion

---

## Additional Application Settings

### HTTP Settings
| Setting | Purpose | Default |
|---------|---------|---------|
| HTTP Host Header | Override Host header sent to origin | null |
| Disable Chunked Encoding | For WSGI servers | Off |

### Connection Settings
| Setting | Purpose | Default |
|---------|---------|---------|
| Connect Timeout | TCP connection timeout | 30s |
| No Happy Eyeballs | Disable IPv4/IPv6 fallback | Off |
| Keep Alive Connections | Max idle connections | 100 |

### TLS Settings
| Setting | Purpose | When to Use |
|---------|---------|-------------|
| No TLS Verify | Skip origin cert verification | Self-signed certs |
| Origin Server Name | SNI for TLS | Virtual hosts |

---

## Troubleshooting

### Tunnel Shows "Inactive"
- **Cause:** No cloudflared connector running
- **Fix:** Start the cloudflared container/service with correct token

### 502 Bad Gateway
- **Cause:** Cloudflare can't reach origin
- **Fix:**
  - Check origin service is running
  - Verify URL in route configuration
  - Check Docker network connectivity

### 400 Bad Request
- **Cause:** Origin rejecting proxied request
- **Fix:**
  - Configure `trusted_proxies` on origin (e.g., Home Assistant)
  - Set HTTP Host Header in tunnel settings
  - Check if origin requires specific headers

### Connection Refused (Healthcheck)
- **Cause:** Often IPv6/IPv4 mismatch in Alpine containers
- **Fix:** Use `127.0.0.1` instead of `localhost` in healthchecks

### Token Not Working
- **Cause:** Token may have been refreshed
- **Fix:** Get new token from Cloudflare dashboard

---

## HomeLab Tunnel Tokens

### HomeGate Token
```
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiZjI5MWQzOGU5YTM4OWE1NjczNGUxYTkyZjg5ZGQyOGMiLCJ0IjoiZjQyNDk3M2MtNTYwOS00ZTk2LTk2M2MtNDY3ODkwNmIwOTNlIiwicyI6Ik1ESmlPVGsyTW1FdE5qUTNOQzAwTWpnekxXRXhNbUV0TVRreE5UUXpaV1ZqTURrMyJ9
```

### HomeAssist Token
```
eyJhIjoiZjI5MWQzOGU5YTM4OWE1NjczNGUxYTkyZjg5ZGQyOGMiLCJ0IjoiZjc2NWE0ODUtYmIwYi00ZDI4LTgwODQtYzM2Zjk2MDI3ZTdmIiwicyI6Ik56QXpZbUptTVRBdE9EVTNOeTAwTVRZekxXRXdZalF0T0RFd09UQTNOakV3WmpJMyJ9
```

---

## Best Practices

1. **One tunnel per project** - Easier to manage and troubleshoot
2. **Use descriptive names** - `homegate`, `homeassist`, not `tunnel1`
3. **Store tokens securely** - Use .env files, not hardcoded
4. **Use Docker networks** - Reference containers by name, not IP
5. **Set appropriate timeouts** - 30s default is usually fine
6. **Monitor tunnel status** - Check Cloudflare dashboard periodically
7. **Keep cloudflared updated** - Watch for version warnings

---

## Useful Commands

### Test Tunnel Locally
```bash
# Check if tunnel is running
docker logs <container-name>

# Look for: "Registered tunnel connection"
# 4 connections = healthy
```

### Test Public URL
```bash
curl -I https://homegate.unmanned-systems.uk
# Should return 200 OK
```

### Test Origin Directly
```bash
curl -H "Host: homegate.unmanned-systems.uk" http://localhost:80
# Tests if origin accepts the hostname
```

---

## Related Documentation

- Screenshots: `~/cc-share/HomeLab/cloudflair_skill_build/`
- Navigation Guide: `~/cc-share/HomeLab/cloudflair_skill_build/CLOUDFLARE_NAVIGATION.md`
- HomeGate docker-compose: `/home/homelab/HomeGate/docker-compose.yml`

---

*Last Updated: 2026-01-21*
*Skill Version: 1.0*
