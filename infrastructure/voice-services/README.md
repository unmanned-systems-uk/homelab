# Voice Services Stack

Hybrid voice services architecture for HomeLab.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│ Home Assistant  │────▶│ Wyoming Services │ (Native)
└─────────────────┘     │  - piper (TTS)   │ :10200
                        │  - whisper (STT) │ :10300
┌─────────────────┐     └────────┬─────────┘
│ Claude CLI      │────┐         │
├─────────────────┤    │    ┌────▼─────────────┐
│ Apps            │────┴───▶│ OpenAI API       │ :8000
└─────────────────┘         │ (Wrapper)        │
                            └──────────────────┘
```

## Services

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Wyoming Piper | 10200 | Wyoming | TTS for Home Assistant |
| Wyoming Whisper | 10300 | Wyoming | STT for Home Assistant |
| Wyoming OpenWakeWord | 10400 | Wyoming | Wake word detection |
| OpenAI Voice API | 8000 | HTTP/REST | Universal API wrapper |
| Ollama | 11434 | HTTP/REST | LLM (existing) |

## Deployment

```bash
# From HomeLab machine
cd /home/homelab/HomeLab/infrastructure/voice-services
./deploy.sh
```

## Endpoints

### OpenAI-Compatible TTS
```bash
curl -X POST http://10.0.1.201:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello world","voice":"amy"}' \
  --output speech.wav
```

### Simple TTS
```bash
curl -X POST http://10.0.1.201:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world"}' \
  --output speech.wav
```

### OpenAI-Compatible STT
```bash
curl -X POST http://10.0.1.201:8000/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "language=en"
```

### Health Check
```bash
curl http://10.0.1.201:8000/health
```

### List Voices
```bash
curl http://10.0.1.201:8000/v1/voices
```

## Home Assistant Configuration

Add to `configuration.yaml`:

```yaml
# Wyoming integration (native)
# Configure via UI: Settings > Devices & Services > Add Integration > Wyoming
# Or add manually:
wyoming:
```

Then add Wyoming integrations via UI:
1. Settings > Devices & Services
2. Add Integration > Wyoming Protocol
3. Host: 10.0.1.201, Port: 10200 (Piper TTS)
4. Add Integration > Wyoming Protocol
5. Host: 10.0.1.201, Port: 10300 (Whisper STT)

## Claude CLI Hook

Create `~/.config/claude/hooks/tts.sh`:

```bash
#!/bin/bash
TEXT="$1"
curl -s -X POST http://10.0.1.201:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d "{\"input\":\"$TEXT\",\"voice\":\"amy\"}" | mpv --no-terminal -
```

## Available Voices

| OpenAI Name | Piper Voice |
|-------------|-------------|
| alloy | en_US-amy-medium |
| echo | en_US-ryan-medium |
| fable | en_GB-alan-medium |
| onyx | en_US-joe-medium |
| nova | en_US-lessac-medium |
| shimmer | en_GB-jenny_dioco-medium |
| amy | en_US-amy-medium (default) |

## Troubleshooting

### Check service status
```bash
ssh ccpm@10.0.1.201 'docker compose -f ~/voice-services/docker-compose.yml ps'
```

### View logs
```bash
ssh ccpm@10.0.1.201 'docker compose -f ~/voice-services/docker-compose.yml logs -f'
```

### Restart services
```bash
ssh ccpm@10.0.1.201 'docker compose -f ~/voice-services/docker-compose.yml restart'
```

## Resource Usage

- Wyoming Piper: ~500MB RAM
- Wyoming Whisper: ~1-2GB RAM
- OpenAI Wrapper: ~100MB RAM
- Total: ~2-3GB (leaves room for Ollama)

## Why This Architecture?

1. **Wyoming for HA** - Native integration, battle-tested
2. **OpenAI API for CLI** - Universal, works with anything
3. **Containerized** - Isolated, no GPU conflicts
4. **Lightweight wrapper** - Doesn't load models, just proxies
5. **Stable** - No more host crashes
