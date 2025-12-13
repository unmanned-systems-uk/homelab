# HomeLab Learning Hub

**Purpose:** Central resource for learning AI/ML, infrastructure, and automation
**Status:** Growing document - add resources as discovered
**Last Updated:** 2025-12-13

---

## Table of Contents

1. [AI/ML Fundamentals](#aiml-fundamentals)
2. [GPU Knowledge](#gpu-knowledge)
3. [Server Infrastructure](#server-infrastructure)
4. [Automation & Workflows](#automation--workflows)
5. [Voice & TTS](#voice--tts)
6. [Tools & Platforms](#tools--platforms)
7. [Learning Path](#learning-path)

---

## AI/ML Fundamentals

### Key Concepts to Learn

| Concept | Description | Why It Matters |
|---------|-------------|----------------|
| **Inference** | Running a trained model to get predictions | What you do most often |
| **Training** | Teaching a model from scratch using data | Compute intensive, needs lots of data |
| **Fine-tuning** | Adapting a pre-trained model to your data | Best balance of effort vs results |
| **LoRA/QLoRA** | Efficient fine-tuning techniques | Train large models on smaller GPUs |
| **Quantization** | Reducing model precision (FP32→INT8) | Run bigger models on less VRAM |
| **Parameters** | Model size (7B = 7 billion params) | Bigger = smarter but needs more VRAM |

### VRAM Requirements by Task

| Task | VRAM Needed | Example |
|------|-------------|---------|
| Inference (7B quantized) | 6-8GB | Running Mistral 7B Q4 |
| Inference (7B full) | 14-16GB | Running Mistral 7B FP16 |
| Fine-tuning with LoRA | 12-18GB | Adapting model to your data |
| Fine-tuning full | 24-48GB+ | Updating all model weights |
| Training from scratch | 48GB+ or multi-GPU | Building new model architecture |

### Model Sizes Reference

| Size | Examples | Use Case |
|------|----------|----------|
| < 1B | Phi-1, TinyLlama | Edge devices, fast inference |
| 1-3B | Phi-2, StableLM | Good balance, fine-tunable |
| 7B | Mistral, Llama 7B | General purpose, popular |
| 13B | Llama 13B | Better reasoning |
| 70B+ | Llama 70B, Mixtral 8x22B | Best quality, needs serious hardware |

---

## GPU Knowledge

### Jetson vs Desktop GPU

| Aspect | Jetson Orin NX | Desktop GPU (RTX 3090) |
|--------|----------------|------------------------|
| **Type** | System-on-Chip (SoC) | Discrete PCIe card |
| **GPU Cores** | 1024 CUDA cores | 10496 CUDA cores |
| **Memory** | 8-16GB Unified (shared with CPU) | 24GB Dedicated VRAM |
| **Memory Bandwidth** | 102 GB/s | 936 GB/s |
| **Power** | 10-25W | 350W |
| **Best For** | Edge inference, deployment | Training, fine-tuning |

### Memory Architecture

```
Jetson (Unified Memory):
┌─────────────────────────┐
│    Shared Memory Pool   │
│    CPU ←→ GPU share     │
└─────────────────────────┘
  Pro: No copy overhead
  Con: Lower bandwidth

Desktop (Discrete):
┌──────────┐   ┌──────────┐
│ CPU RAM  │   │ GPU VRAM │
│  32GB+   │   │   24GB   │
└──────────┘   └──────────┘
  Pro: High bandwidth, dedicated
  Con: Must copy data to GPU
```

### GPU Selection Guide (Used Market 2025)

| GPU | Type | VRAM | Price | Best For |
|-----|------|------|-------|----------|
| RTX 3090 | Gaming | 24GB | £300-400 | **Best value for AI** |
| RTX 3090 Ti | Gaming | 24GB | £450-550 | Slightly faster |
| RTX 4090 | Gaming | 24GB | £1400-1600 | Performance king |
| RTX A5000 | Workstation | 24GB | £900-1100 | Blower cooling, rack-friendly |
| RTX A6000 | Workstation | 48GB | £2500-3500 | Large models |
| Jetson Orin NX | Edge | 16GB | £500-700 | Deployment, always-on |

### Buy vs Rent Analysis

| GPU | Buy Price | Cloud Equiv/hr | Break-Even |
|-----|-----------|----------------|------------|
| RTX 3090 | £350 | £0.50 | ~700 hours |
| RTX A6000 | £3000 | £1.50 | ~2000 hours |

**Rule of thumb:** If training > 30 days total, buy the GPU.

---

## Server Infrastructure

### Proxmox VE

**What:** Open-source hypervisor for VMs and containers
**Why:** Free, mature, great web UI, ZFS support

```
Proxmox Architecture:
┌────────────────────────────────────────┐
│         Proxmox VE (Bare Metal)        │
├──────────┬──────────┬──────────────────┤
│   VMs    │   LXC    │   Storage (ZFS)  │
│ (Full OS)│(Containers)│                │
└──────────┴──────────┴──────────────────┘
```

**Resources:**
- Website: https://www.proxmox.com/en/proxmox-ve
- Docs: https://pve.proxmox.com/wiki/Main_Page

### Pulse (Proxmox Monitoring)

**What:** Real-time monitoring dashboard for Proxmox
**Repo:** https://github.com/rcourtman/Pulse

| Feature | Description |
|---------|-------------|
| Real-time metrics | CPU, RAM, network across nodes |
| VM/Container status | Hyperlinks to Proxmox console |
| Docker monitoring | Optional agent for containers |
| Alerts | Downtime, high load notifications |

**Install:** `curl -fsSL https://github.com/rcourtman/Pulse/releases/latest/download/install.sh | bash`
**Port:** 7655
**Resources:** 1 vCPU, 1GB RAM, 4GB storage

### Portainer (Docker Management)

**What:** Web UI for managing Docker containers
**Website:** https://www.portainer.io/

**Why use it:**
- Visual container management
- Easy deployment from templates
- Stack management (docker-compose)
- User access control

### Home Assistant

**What:** Open-source home automation
**Website:** https://www.home-assistant.io/

**Deployment options:**
- Home Assistant OS (VM) - Recommended for Proxmox
- Docker container
- Supervised install

---

## Automation & Workflows

### n8n - Workflow Automation

**What:** Self-hosted workflow automation (like Zapier, but open-source)
**Repo:** https://github.com/n8n-io/n8n
**Website:** https://n8n.io/
**License:** Fair-code (free for self-hosting)

#### Why n8n?

| Feature | Description |
|---------|-------------|
| Visual workflow builder | Drag-and-drop node editor |
| 400+ integrations | APIs, databases, services |
| Self-hosted | Your data stays local |
| AI nodes | OpenAI, local LLMs, embeddings |
| Webhooks | Trigger from external events |
| Code nodes | Custom JavaScript/Python |

#### n8n + HomeLab Use Cases

| Workflow | Description |
|----------|-------------|
| **SCPI automation** | Trigger test sequences, log results |
| **Home Assistant** | Complex automations beyond HA capability |
| **AI pipelines** | Chain LLM calls, process data |
| **Alerts** | Monitor systems, notify on issues |
| **Data sync** | Move data between services |
| **MCP coordination** | Orchestrate MCP server actions |

#### Installation (Docker)

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

#### n8n + AI Integration

n8n has native nodes for:
- OpenAI / ChatGPT
- Local LLMs (Ollama)
- Embeddings
- Vector stores
- AI agents

**Example workflow:**
```
Webhook → Process Text → Local LLM → Store Result → Notify
```

**Resources:**
- Docs: https://docs.n8n.io/
- Templates: https://n8n.io/workflows/
- Community: https://community.n8n.io/

---

## Voice & TTS

### Chatterbox TTS

**What:** Open-source text-to-speech with voice cloning
**Repo:** https://github.com/resemble-ai/chatterbox
**By:** Resemble AI

#### Requirements

| Use Case | VRAM |
|----------|------|
| Inference | 6-7GB |
| Fine-tuning (GRPO) | 12GB+ |
| Fine-tuning (LoRA) | 18GB+ |

#### Features

- 0.5B parameter Llama backbone
- Voice cloning from samples
- High quality output
- Streaming support

#### Related Projects

| Project | Description | Link |
|---------|-------------|------|
| Chatterbox Server | Web UI + API server | https://github.com/devnen/Chatterbox-TTS-Server |
| Chatterbox Streaming | Real-time + fine-tuning | https://github.com/davidbrowne17/chatterbox-streaming |
| Chatterbox TTS API | OpenAI-compatible API | https://github.com/travisvn/chatterbox-tts-api |

---

## Tools & Platforms

### MCP (Model Context Protocol)

**What:** Protocol for AI assistants to access external tools/data
**By:** Anthropic
**Docs:** https://modelcontextprotocol.io/

#### HomeLab MCP Servers (Planned)

| MCP Server | Purpose | Status |
|------------|---------|--------|
| UniFi MCP | Network visibility/control | Planned |
| SCPI MCP | Test equipment control | Future |
| Custom MCPs | Home automation, etc. | Future |

#### UniFi MCP Options

| Server | Repo | Notes |
|--------|------|-------|
| unifi-network-mcp | https://github.com/sirkirby/unifi-network-mcp | Efficient, lazy loading |
| mcp-unifi-network | https://github.com/gilberth/mcp-unifi-network | Full featured |

### SDR (Software Defined Radio)

#### HomeLab SDR Equipment

| Device | Frequency | Purpose |
|--------|-----------|---------|
| HackRF One/Pro | 1MHz - 6GHz | Wideband TX/RX |
| Nooelec NESDR Smart | 25MHz - 1.75GHz | Dedicated receivers |
| Ham It Up v2 | HF upconverter | HF reception |
| Opera Cake | Antenna switch | Multi-antenna |

#### SDR Software

| Software | Purpose | Link |
|----------|---------|------|
| GNU Radio | Signal processing | https://www.gnuradio.org/ |
| SDR++ | General receiver | https://github.com/AlexandreRouworksique/SDRPlusPlus |
| dump1090 | ADS-B decoding | https://github.com/flightaware/dump1090 |

---

## Learning Path

### Phase 1: Foundation (Current)

- [x] Document hardware inventory
- [x] Understand GPU differences (Jetson vs Desktop)
- [x] Plan server architecture
- [ ] Setup Proxmox on R640
- [ ] Deploy basic VMs

### Phase 2: Infrastructure

- [ ] Setup Docker host with Portainer
- [ ] Deploy Pulse monitoring
- [ ] Migrate Home Assistant
- [ ] Setup n8n for workflows
- [ ] Configure VLANs

### Phase 3: AI Basics

- [ ] Acquire GPU (RTX 3090)
- [ ] Setup GPU passthrough
- [ ] Run inference with existing models
- [ ] Deploy Chatterbox TTS
- [ ] Experiment with local LLMs (Ollama)

### Phase 4: AI Development

- [ ] Learn fine-tuning with LoRA
- [ ] Create custom dataset
- [ ] Fine-tune a model
- [ ] Deploy to Jetson for edge inference
- [ ] Build AI-powered automations with n8n

### Phase 5: Integration

- [ ] Setup MCP servers
- [ ] SCPI test automation
- [ ] Voice-controlled lab
- [ ] Custom AI models for specific tasks

---

## Resources & Links

### Official Documentation

| Topic | Link |
|-------|------|
| Proxmox VE | https://pve.proxmox.com/wiki/Main_Page |
| n8n | https://docs.n8n.io/ |
| Home Assistant | https://www.home-assistant.io/docs/ |
| Chatterbox | https://github.com/resemble-ai/chatterbox |
| NVIDIA Jetson | https://developer.nvidia.com/embedded-computing |

### Learning Resources

| Topic | Resource |
|-------|----------|
| ML Fundamentals | https://course.fast.ai/ (fast.ai) |
| LLM Fine-tuning | https://huggingface.co/docs/transformers/training |
| LoRA/QLoRA | https://huggingface.co/docs/peft |
| Proxmox | YouTube: Learn Linux TV, Craft Computing |

### Communities

| Community | Link |
|-----------|------|
| Proxmox Forum | https://forum.proxmox.com/ |
| r/homelab | https://reddit.com/r/homelab |
| r/LocalLLaMA | https://reddit.com/r/LocalLLaMA |
| n8n Community | https://community.n8n.io/ |

---

## Notes

*Add notes and discoveries as you learn:*

-

---

*Document created during HomeLab planning session 2025-12-13*
