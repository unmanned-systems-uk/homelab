# Audio Transcoding Proxy

OpenAI-compatible audio transcoding proxy for the Whisper TTS server. Accepts any audio format and automatically converts to WAV before forwarding to Whisper.

## Features

- **Universal Format Support**: Accepts WebM, Ogg, MP3, WAV, FLAC, M4A, and more
- **Automatic Conversion**: Uses FFmpeg to convert to 16kHz mono WAV
- **Stream Processing**: No disk I/O, all processing in memory
- **OpenAI Compatible**: Drop-in replacement for OpenAI Whisper API
- **Production Ready**: Runs with Gunicorn, includes health checks
- **Secure**: Runs as non-root user

## Endpoints

### POST /v1/audio/transcriptions
OpenAI-compatible transcription endpoint.

**Parameters:**
- `file` (required): Audio file in any format
- `model` (optional): Model name (default: "whisper-1")
- `language` (optional): Language code (e.g., "en")
- `prompt` (optional): Transcription prompt
- `response_format` (optional): Response format (json, text, srt, vtt)
- `temperature` (optional): Sampling temperature

**Example:**
```bash
curl -X POST http://localhost:8001/v1/audio/transcriptions \
  -F "file=@audio.webm" \
  -F "model=whisper-1" \
  -F "language=en"
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "audio-transcoding-proxy",
  "whisper_url": "http://localhost:8000/v1/audio/transcriptions"
}
```

## Building

```bash
docker build -t transcoding-proxy:latest .
```

## Running

### Standalone
```bash
docker run -d \
  --name transcoding-proxy \
  -p 8001:8001 \
  --network voice-network \
  transcoding-proxy:latest
```

### With Docker Compose
Add to the voice-services `docker-compose.yml`:

```yaml
transcoding-proxy:
  build: ./transcoding-proxy
  container_name: transcoding-proxy
  ports:
    - "8001:8001"
  networks:
    - voice-network
  restart: unless-stopped
  depends_on:
    - whisper
```

## Architecture

```
Client (HomeGate)
    |
    | WebM/Ogg/MP3/etc.
    v
Transcoding Proxy :8001
    |
    | FFmpeg conversion to 16kHz WAV
    |
    | WAV data
    v
Whisper Server :8000
    |
    | Transcription
    v
Response to Client
```

## Configuration

The proxy forwards requests to `http://localhost:8000/v1/audio/transcriptions` by default. This assumes the Whisper server is on the same Docker network.

To change the Whisper URL, modify `WHISPER_URL` in `app.py` or set via environment variable (future enhancement).

## Logs

View logs:
```bash
docker logs -f transcoding-proxy
```

## Testing

```bash
# Test with a WebM file
curl -X POST http://localhost:8001/v1/audio/transcriptions \
  -F "file=@test.webm" \
  -F "response_format=json"

# Test health endpoint
curl http://localhost:8001/health
```

## Dependencies

- Python 3.11
- Flask 3.0.0
- FFmpeg
- Gunicorn 21.2.0
- Requests 2.31.0

## Performance

- **Workers**: 2 Gunicorn workers
- **Timeout**: 120 seconds (for long audio files)
- **Memory**: Streaming processing, minimal memory footprint
- **Throughput**: Limited by FFmpeg conversion speed and Whisper inference

## Security

- Runs as non-root user (`proxyuser`)
- No file system writes
- Input validation on all endpoints
- Timeout protection on forwarded requests

## Monitoring

The service includes a built-in health check that runs every 30 seconds:
```bash
docker inspect --format='{{json .State.Health}}' transcoding-proxy
```
