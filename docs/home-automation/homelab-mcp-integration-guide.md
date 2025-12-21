# HomeLab MCP Integration Guide
## Model Context Protocol for Home Automation Access

**Date:** 2025-12-21
**Purpose:** Enable AI agent access to Home Assistant and HomeSeer via MCP

---

## What is MCP (Model Context Protocol)?

**Definition:** MCP is an open standard (like USB-C for LLMs) that defines how AI models communicate with external systems.

**Created By:** Anthropic (November 2024)
**Purpose:** Universal format for LLMs to connect with external systems and data

**Think of it as:** HTTP for AI - standardized protocol for AI ↔ Application communication

---

## Available MCP Servers for Home Automation

### ✅ Home Assistant - EXCELLENT MCP Support

#### Option 1: Official Home Assistant MCP Server (RECOMMENDED)

**Built-in:** Home Assistant 2025.2+
**URL:** https://www.home-assistant.io/integrations/mcp_server/

**Features:**
- ✅ Native integration (no external server needed)
- ✅ Exposed via `/api/mcp` endpoint
- ✅ Uses Home Assistant Assist API
- ✅ Control which devices are exposed (exposed entities page)
- ✅ Long-lived access token authentication
- ✅ Supports remote MCP clients (Claude Desktop, etc.)

**What You Can Do:**
- Control lights, switches, sensors from Claude
- Query device states
- Execute automations
- Get smart home summaries
- Create guided conversations
- Troubleshoot issues

**Setup:**
1. Update Home Assistant to 2025.2 or newer
2. Enable MCP Server integration in HA
3. Generate Long-lived Access Token (Settings → Security)
4. Configure exposed entities (what Claude can access)
5. Add to Claude Desktop MCP config

**Configuration Example:**
```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-home-assistant",
        "--url",
        "http://10.0.1.150:8123",
        "--token",
        "YOUR_LONG_LIVED_ACCESS_TOKEN"
      ]
    }
  }
}
```

#### Option 2: tevonsb/homeassistant-mcp

**GitHub:** https://github.com/tevonsb/homeassistant-mcp
**Type:** Standalone MCP server (Node.js)

**Features:**
- ✅ Comprehensive API coverage
- ✅ Device control (lights, switches, climate, etc.)
- ✅ Service calls with parameters (brightness, color, temperature)
- ✅ Historical data queries
- ✅ Custom event firing
- ✅ System administration

**Installation:**
```bash
# Clone repository
git clone https://github.com/tevonsb/homeassistant-mcp.git
cd homeassistant-mcp

# Install dependencies
npm install

# Configure (create .env file)
cat > .env << EOF
HASS_URL=http://10.0.1.150:8123
HASS_TOKEN=YOUR_LONG_LIVED_ACCESS_TOKEN
EOF

# Run server
npm start
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "node",
      "args": ["/path/to/homeassistant-mcp/index.js"]
    }
  }
}
```

#### Option 3: voska/hass-mcp (Docker)

**GitHub:** https://github.com/voska/hass-mcp
**Type:** Docker container
**Best For:** Easy deployment, isolation

**Features:**
- ✅ Docker-based (easy to deploy)
- ✅ Query device states and sensors
- ✅ Control entities (lights, switches, etc.)
- ✅ Get smart home summaries
- ✅ Troubleshoot automations
- ✅ Search for specific entities
- ✅ Guided conversations for common tasks

**Docker Deployment:**
```bash
# Run with Docker
docker run -d \
  --name hass-mcp \
  -e HASS_URL=http://10.0.1.150:8123 \
  -e HASS_TOKEN=YOUR_LONG_LIVED_ACCESS_TOKEN \
  -p 3000:3000 \
  voska/hass-mcp
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "homeassistant": {
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

#### Option 4: allenporter/mcp-server-home-assistant

**GitHub:** https://github.com/allenporter/mcp-server-home-assistant
**Type:** Python-based MCP server
**Best For:** Custom integrations, educational

**Features:**
- ✅ Python implementation (easy to customize)
- ✅ Well-documented (educational resource)
- ✅ Standard MCP protocol
- ✅ Home Assistant REST API integration

**Installation:**
```bash
# Clone repository
git clone https://github.com/allenporter/mcp-server-home-assistant.git
cd mcp-server-home-assistant

# Install
pip install -e .

# Run
mcp-server-home-assistant \
  --url http://10.0.1.150:8123 \
  --token YOUR_LONG_LIVED_ACCESS_TOKEN
```

#### Option 5: cronus42/homeassistant-mcp

**GitHub:** https://github.com/cronus42/homeassistant-mcp
**Type:** Comprehensive API coverage

**Features:**
- ✅ Extensive API coverage
- ✅ Advanced features
- ✅ Well-maintained

---

### ❌ HomeSeer - NO Native MCP Support

**Status:** No HomeSeer MCP server currently exists

**Why?**
- HomeSeer is a commercial, closed platform
- MCP is new (Nov 2024), HomeSeer hasn't implemented it
- HomeSeer uses proprietary JSON/ASCII protocols
- Smaller developer community compared to Home Assistant

**Available HomeSeer APIs:**
- JSON API (requires enable in Tools → Setup → Network)
- ASCII API (legacy)
- mcsMQTT plugin (MQTT, REST, TCP, UDP, WebSocket)
- HTTP JSON requests for commands

---

## Recommended Hybrid Architecture

### Strategy: Bridge HomeSeer to Home Assistant, Use HA MCP Server

```
┌─────────────────────┐
│   Claude Desktop    │
│   (MCP Client)      │
└──────────┬──────────┘
           │ MCP Protocol
           ▼
┌─────────────────────┐
│  Home Assistant     │
│  MCP Server         │
│  10.0.1.150:8123    │
└──────────┬──────────┘
           │
           │ MQTT Bridge
           │ (Mosquitto)
           ▼
┌─────────────────────┐
│    HomeSeer         │
│  (mcsMQTT Plugin)   │
│  10.0.1.XXX         │
└──────────┬──────────┘
           │
           ▼
  Physical Devices
```

### How It Works

1. **HomeSeer devices** exposed via mcsMQTT to MQTT broker
2. **Home Assistant** subscribes to MQTT topics (sees HomeSeer devices)
3. **MCP Server** in Home Assistant exposes all devices (HA + HS) to Claude
4. **Claude** can control both HA and HS devices via single MCP interface

**Advantages:**
- ✅ Single MCP endpoint for all devices
- ✅ Claude doesn't need to know about HomeSeer
- ✅ HA acts as unified API layer
- ✅ Future-proof (MCP support in HA, not HS)

---

## Alternative: Custom HomeSeer MCP Server (Future)

**If you want to build a custom HomeSeer MCP server:**

### HomeSeer JSON API Endpoints

HomeSeer provides these HTTP JSON endpoints:
```
GET  /JSON?request=getstatus&ref=123     # Get device status
POST /JSON?request=controldevicebyvalue&ref=123&value=50  # Set device
GET  /JSON?request=getdevices            # List all devices
POST /JSON?request=runscriptfunction&scriptname=test.vb&functionname=Main
```

### MCP Server Architecture

```python
# Pseudo-code for custom HomeSeer MCP server
from mcp.server import Server
import requests

class HomeSeerMCPServer(Server):
    def __init__(self, homeseer_url, username, password):
        self.hs_url = homeseer_url
        self.auth = (username, password)

    @tool()
    async def get_device_status(self, device_ref: int):
        """Get status of HomeSeer device"""
        response = requests.get(
            f"{self.hs_url}/JSON",
            params={"request": "getstatus", "ref": device_ref},
            auth=self.auth
        )
        return response.json()

    @tool()
    async def control_device(self, device_ref: int, value: float):
        """Control HomeSeer device"""
        response = requests.post(
            f"{self.hs_url}/JSON",
            params={
                "request": "controldevicebyvalue",
                "ref": device_ref,
                "value": value
            },
            auth=self.auth
        )
        return response.json()

    @tool()
    async def list_devices(self):
        """List all HomeSeer devices"""
        response = requests.get(
            f"{self.hs_url}/JSON",
            params={"request": "getdevices"},
            auth=self.auth
        )
        return response.json()
```

**Resources for Building:**
- MCP SDK: https://github.com/modelcontextprotocol/servers
- MCP Specification: https://spec.modelcontextprotocol.io/
- HomeSeer JSON API docs (in HomeSeer documentation)

---

## Recommended Setup for Your HomeLab

### Phase 1: Home Assistant MCP (Immediate)

**When HA VM is deployed (Issue #16):**

1. **Install Home Assistant 2025.2+** on VM 10.0.1.150
2. **Enable MCP Server** integration in HA
3. **Generate Long-lived Access Token:**
   - Settings → Profile → Security
   - Create token named "Claude MCP Access"
   - Save token securely
4. **Configure Exposed Entities:**
   - Settings → Voice Assistants → Expose
   - Select which devices Claude can control
   - Start with lights, switches (safe devices)
5. **Add to Claude Desktop:**
   ```json
   {
     "mcpServers": {
       "homeassistant": {
         "command": "npx",
         "args": [
           "-y",
           "@modelcontextprotocol/server-home-assistant",
           "--url",
           "http://10.0.1.150:8123",
           "--token",
           "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
         ]
       }
     }
   }
   ```

### Phase 2: MQTT Bridge Setup (Week 2-3)

**Connect HomeSeer to Home Assistant:**

1. **Install mcsMQTT plugin** in HomeSeer
2. **Configure MQTT broker** (Mosquitto on HA)
3. **Expose HomeSeer devices** to MQTT topics
4. **Subscribe in Home Assistant** to HomeSeer topics
5. **Verify Claude can see HomeSeer devices** via HA MCP

### Phase 3: Test Claude Access (Week 3-4)

**Test Commands in Claude Desktop:**

```
User: "Show me the status of all lights in my home"
Claude: [Uses HA MCP to query all light entities]

User: "Turn on the living room lights to 50% brightness"
Claude: [Uses HA MCP to call light.turn_on service]

User: "What's the temperature in the bedroom?"
Claude: [Uses HA MCP to query sensor state]

User: "Run my morning routine automation"
Claude: [Uses HA MCP to trigger automation]
```

### Phase 4: Advanced Integration (Future)

**Optional Enhancements:**

1. **Custom MCP Tools:**
   - Build specialized tools for your specific automations
   - Voice command translation to HomeSeer scripts
   - Complex multi-step routines

2. **CCPM Integration:**
   - Add MCP servers to CCPM configuration
   - Allow CCPM agents to control home automation
   - Integrate with task workflows (e.g., "Turn off all lights when sprint ends")

3. **Monitoring & Analytics:**
   - MCP tools for energy monitoring
   - Device health checks
   - Automation performance analysis

---

## Security Considerations

### Authentication

**Home Assistant Long-lived Tokens:**
- ✅ Generate unique token for Claude MCP
- ✅ Don't share token in Git repositories
- ✅ Rotate tokens quarterly
- ✅ Revoke immediately if compromised

**Network Security:**
- Consider running MCP over VPN or Cloudflare tunnel
- Don't expose HA directly to internet
- Use HTTPS for remote access
- Implement firewall rules (allow only local network)

### Access Control

**Exposed Entities:**
- Start with non-critical devices (lights, switches)
- Gradually expand to sensors, climate
- Avoid exposing security systems initially
- Don't expose garage doors/locks without testing

**Permissions:**
- Claude asks permission before calling tools
- Review permissions in Claude Desktop settings
- Monitor MCP access logs in Home Assistant

---

## Troubleshooting

### Issue: Claude Can't Connect to Home Assistant

**Check:**
1. Home Assistant is running: `http://10.0.1.150:8123`
2. MCP Server integration enabled
3. Long-lived token is valid
4. Network connectivity (ping 10.0.1.150)
5. Firewall not blocking port 8123

**Fix:**
```bash
# Test HA API manually
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://10.0.1.150:8123/api/

# Should return: {"message": "API running."}
```

### Issue: Claude Can't See HomeSeer Devices

**Check:**
1. MQTT bridge is working
2. HomeSeer devices published to MQTT
3. Home Assistant subscribed to MQTT topics
4. Devices visible in HA UI
5. Devices exposed in HA MCP settings

**Fix:**
```bash
# Check MQTT messages
mosquitto_sub -h 10.0.1.150 -t "homeseer/#" -v

# Verify HA sees MQTT devices
# Home Assistant UI → Integrations → MQTT
```

### Issue: MCP Tools Not Showing in Claude

**Check:**
1. Claude Desktop MCP config syntax correct
2. MCP server process running
3. Claude Desktop restarted after config change
4. Logs in Claude Desktop (View → Developer → Show Logs)

**Fix:**
```json
// Validate JSON syntax
// Check file location: ~/.config/Claude/claude_desktop_config.json
// Restart Claude Desktop completely
```

---

## Resources

### MCP Documentation
- **MCP Official Docs:** https://docs.claude.com/en/docs/agents-and-tools/remote-mcp-servers
- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **MCP Server Examples:** https://github.com/modelcontextprotocol/servers
- **What is MCP:** https://claude.com/blog/what-is-model-context-protocol

### Home Assistant MCP
- **Official Integration:** https://www.home-assistant.io/integrations/mcp_server/
- **tevonsb/homeassistant-mcp:** https://github.com/tevonsb/homeassistant-mcp
- **voska/hass-mcp:** https://github.com/voska/hass-mcp
- **allenporter MCP Server:** https://github.com/allenporter/mcp-server-home-assistant
- **Setup Guide:** https://skywork.ai/blog/how-to-set-up-mcp-server-home-assistant-mcp-agent/

### HomeSeer API
- **mcsMQTT Plugin:** https://shop.homeseer.com/products/michael-mcsharry-mcsmqtt-software-plugin-for-hs4
- **HomeSeer Forums:** https://forums.homeseer.com/
- **HA Integration:** https://github.com/marthoc/homeseer

### Community
- **Home Assistant Community:** https://community.home-assistant.io/
- **MCP Servers Directory:** https://mcpservers.org/
- **Awesome MCP Servers:** https://github.com/punkpeye/awesome-mcp-servers

---

## Implementation Checklist

### Prerequisites
- [ ] Home Assistant VM deployed (10.0.1.150)
- [ ] Home Assistant updated to 2025.2+
- [ ] Claude Desktop installed on your machine
- [ ] HomeSeer running with mcsMQTT plugin (if bridging)

### Home Assistant MCP Setup
- [ ] Enable MCP Server integration in HA
- [ ] Generate Long-lived Access Token
- [ ] Configure exposed entities (start with lights)
- [ ] Test HA API with token
- [ ] Add MCP server to Claude Desktop config
- [ ] Restart Claude Desktop
- [ ] Test basic commands ("list all lights")

### MQTT Bridge (Optional for HomeSeer)
- [ ] Install Mosquitto on HA VM
- [ ] Configure mcsMQTT in HomeSeer
- [ ] Test MQTT communication
- [ ] Subscribe HA to HomeSeer topics
- [ ] Verify devices appear in HA
- [ ] Expose bridged devices in HA MCP

### Testing & Validation
- [ ] Test light control via Claude
- [ ] Test sensor queries via Claude
- [ ] Test automation triggers via Claude
- [ ] Test HomeSeer devices (if bridged)
- [ ] Monitor for errors in HA logs
- [ ] Document working commands

### Security Hardening
- [ ] Review exposed entities (minimize surface)
- [ ] Set up token rotation schedule
- [ ] Configure firewall rules
- [ ] Test permission prompts in Claude
- [ ] Document security policies

---

## Next Steps

1. **Deploy Home Assistant VM** (Issue #16)
2. **Update to HA 2025.2+**
3. **Enable MCP Server integration**
4. **Configure Claude Desktop**
5. **Test basic home control from Claude**
6. **Set up MQTT bridge** for HomeSeer devices
7. **Document working commands and workflows**
8. **Consider custom MCP tools** for specialized needs

---

## Summary

**Home Assistant:** ✅ Excellent MCP support (multiple options)
**HomeSeer:** ❌ No native MCP support (bridge via HA + MQTT)

**Recommended Approach:**
1. Use Home Assistant as primary MCP interface
2. Bridge HomeSeer devices via MQTT
3. Claude accesses everything through HA MCP Server
4. Future: Consider building custom HomeSeer MCP server if needed

**Result:** Full AI control of home automation via standardized MCP protocol! 🎯
