# HL-Master Task Routing Rules

**Version:** 1.0.0
**For:** HL-Master agent

---

## Routing Decision Tree

```
Task Received
│
├─ Analyze keywords and context
├─ Match to domain
├─ Check if multi-domain
│
└─> Route to specialist OR handle directly
```

---

## Routing Table

### 1. HL-Network (Network Infrastructure)

**Keywords:**
- network, networking, lan, wan
- vlan, subnet, dhcp, dns, gateway
- firewall, security rule, port forwarding
- unifi, udm, dream machine
- switch, access point, ap
- wifi, wireless, ssid
- client, device connectivity
- ip address, mac address
- bandwidth, speed, latency

**Example Tasks:**
- "Configure new VLAN for lab equipment"
- "Add firewall rule to allow SCPI traffic"
- "Find all connected clients on network"
- "Why is 10.0.1.150 unreachable?"
- "List all UniFi devices"
- "Check network bandwidth usage"

**UUID:** `11111111-aaaa-bbbb-cccc-000000000002`

---

### 2. HL-SCPI (Test Equipment)

**Keywords:**
- scpi, test equipment, instrument
- dmm, multimeter, keithley
- scope, oscilloscope, mso
- psu, power supply, dp932a
- awg, waveform generator, dg2052
- dc load, dl3021a
- measurement, reading, data logging
- voltage, current, resistance, frequency
- calibration, verification

**Equipment Names:**
- dmm, dmm6500, keithley
- scope, mso8204, oscilloscope
- psu, psu-1, psu-2, dp932a
- awg, dg2052, waveform
- load, dc load, dl3021a

**Example Tasks:**
- "Scan SCPI equipment and report status"
- "Measure voltage on PSU-1"
- "Take 100 readings from DMM at 1Hz"
- "Configure AWG for sine wave output"
- "Check if scope is responding"
- "Log temperature data from DMM"

**UUID:** `11111111-aaaa-bbbb-cccc-000000000003`

---

### 3. HL-Infra (Infrastructure & Virtualization)

**Keywords:**
- proxmox, pve, vm, virtual machine
- lxc, container, docker, podman
- ansible, playbook, automation
- infrastructure, iac, infrastructure as code
- backup, restore, snapshot
- nas, synology, storage
- harbor, registry
- deployment, provisioning
- system update, patching

**VM/Host Names:**
- proxmox, pve, pve-ai
- harbor, ccpm-v2, whisper-tts
- vm 101, vm 102, vmid
- nas, synology, 10.0.1.251

**Example Tasks:**
- "Create new VM for testing"
- "Check Proxmox VM status"
- "Deploy Docker container on Harbor"
- "Run Ansible playbook for system updates"
- "Backup all VMs to NAS"
- "Check disk usage on Proxmox"
- "Restart Harbor VM"

**UUID:** `11111111-aaaa-bbbb-cccc-000000000004`

---

### 4. HL-Home (Home Automation)

**Keywords:**
- home assistant, ha, haos
- smart home, automation, scene
- light, bulb, switch, dimmer
- wiz, zigbee, z-wave
- sensor, motion, temperature
- energy, power monitoring, emporia
- voice assistant, assist
- integration, addon
- device, entity

**System Names:**
- home assistant, ha, ha-pi5
- 10.0.1.150, ha server
- wiz bulb, smart light

**Example Tasks:**
- "Configure Home Assistant integration"
- "Turn on living room lights"
- "Create automation for sunrise"
- "Check Home Assistant status"
- "Add new Wiz bulb"
- "Set up Emporia energy monitoring"
- "List all offline devices"

**UUID:** `11111111-aaaa-bbbb-cccc-000000000005`

---

### 5. HL-AI (AI/ML Operations)

**Keywords:**
- gpu, cuda, vram, graphics card
- model, training, fine-tuning, inference
- ollama, llm, language model
- whisper, tts, text to speech, stt
- jetson, orin, edge ai
- ml, machine learning, deep learning
- pytorch, tensorflow, training
- ai service, ml pipeline

**Hardware Names:**
- gtx 1080, rtx a2000
- jetson, orin nx
- gpu, graphics card

**Example Tasks:**
- "Check GPU availability"
- "Deploy Ollama model"
- "Train model on GPU"
- "Configure Jetson for inference"
- "Check Whisper TTS service"
- "List available Ollama models"
- "Monitor GPU utilization"

**UUID:** `11111111-aaaa-bbbb-cccc-000000000006`

---

### 6. HL-Gate (HomeGate Project)

**Keywords:**
- homegate, home gate, dashboard
- hg-, hg-001, hg-002 (issue numbers)
- web dashboard, web ui
- ssh terminal, persistent terminal
- infrastructure dashboard
- i3 host, i3 mini pc
- 10.0.1.50

**GitHub Issues:**
- Any issue starting with HG-
- Issues in unmanned-systems-uk/homegate repo

**Example Tasks:**
- "Implement HG-002 database schema"
- "Work on HomeGate frontend"
- "Create SSH terminal component"
- "Deploy HomeGate to i3 host"
- "Check HomeGate GitHub issues"
- "Design user authentication"

**UUID:** `11111111-aaaa-bbbb-cccc-000000000007`

---

## Multi-Domain Tasks

**Handle Directly by HL-Master** when task involves multiple domains:

### Pattern: Sequential Coordination

**Example:** "Set up new VM for Home Assistant testing"

```
1. HL-Infra: Create VM on Proxmox
   ↓
2. Wait for VM creation
   ↓
3. HL-Home: Install and configure Home Assistant
   ↓
4. HL-Network: Configure firewall rules
   ↓
5. Aggregate results and report to user
```

### Pattern: Parallel Coordination

**Example:** "Prepare lab for power supply testing"

```
1. HL-Network: Verify SCPI VLAN connectivity
2. HL-SCPI: Check PSU availability
3. HL-Infra: Prepare data logging VM

(All in parallel)

4. Aggregate results
5. Report readiness to user
```

---

## Routing Algorithm (Pseudocode)

```python
def route_task(user_request: str) -> str:
    """
    Analyze user request and return target agent UUID.
    Returns HL-Master UUID if multi-domain or unclear.
    """

    # Normalize request
    request_lower = user_request.lower()

    # Check for domain keywords (priority order)

    # 1. HomeGate (most specific)
    if any(k in request_lower for k in ['homegate', 'hg-', 'dashboard ssh']):
        return "HL-Gate (11111111-aaaa-bbbb-cccc-000000000007)"

    # 2. SCPI (specific equipment)
    if any(k in request_lower for k in ['scpi', 'dmm', 'scope', 'psu', 'awg', 'measurement']):
        return "HL-SCPI (11111111-aaaa-bbbb-cccc-000000000003)"

    # 3. Home Assistant (specific system)
    if any(k in request_lower for k in ['home assistant', 'ha ', ' ha', 'smart home', 'wiz']):
        return "HL-Home (11111111-aaaa-bbbb-cccc-000000000005)"

    # 4. AI/ML (specific workloads)
    if any(k in request_lower for k in ['gpu', 'ollama', 'model', 'jetson', 'training']):
        return "HL-AI (11111111-aaaa-bbbb-cccc-000000000006)"

    # 5. Network (broad keywords, check last)
    if any(k in request_lower for k in ['network', 'vlan', 'firewall', 'unifi', 'client', 'switch']):
        return "HL-Network (11111111-aaaa-bbbb-cccc-000000000002)"

    # 6. Infrastructure (broad keywords)
    if any(k in request_lower for k in ['proxmox', 'vm', 'docker', 'container', 'ansible']):
        return "HL-Infra (11111111-aaaa-bbbb-cccc-000000000004)"

    # 7. Check for multi-domain indicators
    domain_matches = count_domain_matches(request_lower)
    if domain_matches > 1:
        return "HL-Master (multi-domain coordination required)"

    # 8. Default: Handle directly
    return "HL-Master (unclear or general task)"
```

---

## Special Cases

### Session Management
**Always:** HL-Master handles directly
- `/eod` - End of day report
- `/update-session-database` - Session checkpoint
- Session summaries
- Cross-agent status reports

### GitHub Issue Triage
**Always:** HL-Master handles first, then delegates

```bash
# Check issue labels and content
gh issue view 42 --repo unmanned-systems-uk/homelab --json title,body,labels

# Analyze and route
# Add agent label
gh issue edit 42 --add-label "agent:hl-network" --repo unmanned-systems-uk/homelab

# Delegate to specialist
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000001" ...
```

### Emergency Alerts
**Always:** HL-Master receives and broadcasts

If specialist sends critical alert:
1. Forward to human immediately
2. Broadcast to relevant agents
3. Log in session report

---

## Routing Examples

### Example 1: Simple Single-Domain

**User:** "List all clients connected to UniFi"

**Analysis:**
- Keywords: "clients", "unifi"
- Domain: Network
- Multi-domain: No

**Route:** HL-Network

**Action:**
```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages?from_agent_id=11111111-aaaa-bbbb-cccc-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "to_agent_id": "11111111-aaaa-bbbb-cccc-000000000002",
    "message_type": "task",
    "subject": "List UniFi Clients",
    "body": "List all clients connected to UniFi controller. Include:\n- Client name\n- IP address\n- MAC address\n- Connection type (wired/wireless)",
    "priority": "normal",
    "metadata": {"task_id": "HL-TASK-2026-01-13-001"}
  }'
```

---

### Example 2: Multi-Domain Coordination

**User:** "Set up isolated network for SCPI equipment testing"

**Analysis:**
- Keywords: "network" (HL-Network), "scpi equipment" (HL-SCPI)
- Domain: Multi-domain
- Coordination: Sequential

**Route:** HL-Master (coordinate both agents)

**Action:**
```
1. Delegate to HL-Network:
   - Create new VLAN (10.0.50.0/24)
   - Configure firewall rules

2. Wait for HL-Network completion

3. Delegate to HL-SCPI:
   - Reconfigure equipment for new subnet
   - Verify connectivity

4. Aggregate results and report
```

---

### Example 3: Unclear/General

**User:** "What's the status of everything?"

**Analysis:**
- Keywords: General query
- Domain: All domains
- Multi-domain: Yes

**Route:** HL-Master (handle directly)

**Action:**
- Query each specialist for status (via messaging)
- Aggregate responses
- Present unified status report

---

## Confidence Scoring

Use confidence scoring for borderline cases:

```python
def calculate_confidence(request: str, agent: str) -> float:
    """Return 0.0-1.0 confidence score for routing"""
    keywords = AGENT_KEYWORDS[agent]
    matches = sum(1 for k in keywords if k in request.lower())
    return min(matches / 3.0, 1.0)  # 3+ matches = 100% confidence

# Route to agent with highest confidence
# If top score < 0.5, handle directly (unclear)
```

---

## When in Doubt

**Default Action:** Handle directly in HL-Master

Better to coordinate directly than mis-route to wrong specialist.

**User Clarification:** If truly unclear, ask user:
```
"This task could involve [network/scpi/infra].
Which area should I focus on?"
```

---

*Routing rules are guidelines, not absolute. Use judgment and ask user if unclear.*
