# SCPI Instruments MCP Server

MCP server providing tool access to SCPI-enabled test equipment via raw TCP sockets.

## Instruments

| Instrument | Model | IP | Port | Type |
|------------|-------|-----|------|------|
| Spectrum Analyser | Rigol RSA5065N | 10.0.1.85 | 5555 | Real-time spectrum analyser |
| Oscilloscope | Rigol MSO8204 | 10.0.1.106 | 5555 | 4-ch mixed signal oscilloscope |

## MCP Tools (24 total)

### Connection Management (3)

| Tool | Description |
|------|-------------|
| `scpi_connect` | Connect to instrument by name or IP |
| `scpi_disconnect` | Disconnect from instrument |
| `scpi_status` | List connected instruments |

### Raw SCPI Access (3)

| Tool | Description |
|------|-------------|
| `scpi_write` | Send SCPI command (no response) |
| `scpi_query` | Send query, return text response |
| `scpi_query_block` | Send query, return binary block (base64) |

### RSA5065N - Spectrum Analyser (5)

| Tool | Description |
|------|-------------|
| `rsa_reset` | Reset to SA mode, ASCII format |
| `rsa_configure_sweep` | Configure frequency, RBW, VBW, points |
| `rsa_sweep` | Execute single sweep, return trace |
| `rsa_capture_burst` | Capture N consecutive sweeps |
| `rsa_screenshot` | Capture display (BMP) |

### MSO8204 - Oscilloscope (11)

| Tool | Description |
|------|-------------|
| `scope_reset` | Reset to defaults |
| `scope_channel_config` | Configure channel (scale, coupling, etc.) |
| `scope_timebase` | Configure timebase |
| `scope_trigger` | Configure trigger (edge, level, slope) |
| `scope_autoscale` | Run autoscale |
| `scope_acquire` | Run/stop/single acquisition |
| `scope_measure` | Take measurements (frequency, VPP, etc.) |
| `scope_measure_phase` | Phase between two channels |
| `scope_waveform` | Capture raw waveform data |
| `scope_screenshot` | Capture display (PNG/BMP/JPEG) |
| `scope_fft` | Configure FFT display |

### Composite Tools (2)

| Tool | Description |
|------|-------------|
| `scope_characterise_channel` | Full signal characterisation |
| `scope_characterise_dual` | Dual channel + phase measurement |

## Quick Start

### Docker

```bash
# Build
docker build -t scpi-instruments .

# Run
docker run -d \
  --name scpi-mcp \
  -p 8081:8081 \
  -e RSA5065N_IP=10.0.1.85 \
  -e MSO8204_IP=10.0.1.106 \
  scpi-instruments
```

### Local

```bash
# Install dependencies
pip install -r requirements.txt

# Run
export RSA5065N_IP=10.0.1.85
export MSO8204_IP=10.0.1.106
python scpi_mcp.py
```

### MCP Configuration

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "scpi-instruments": {
      "command": "python3",
      "args": ["/path/to/scpi_mcp.py"],
      "env": {
        "RSA5065N_IP": "10.0.1.85",
        "MSO8204_IP": "10.0.1.106",
        "SCPI_PORT": "5555"
      }
    }
  }
}
```

Or for SSE transport:

```json
{
  "mcpServers": {
    "scpi-instruments": {
      "type": "sse",
      "url": "http://10.0.1.202:8081/sse"
    }
  }
}
```

## Transport Protocol

- **Protocol:** Raw TCP socket (NOT pyvisa, NOT VXI-11, NOT HiSLIP)
- **Port:** 5555 for all instruments
- **Line termination:** `\n` on send; responses may omit trailing `\n`
- **Pacing:** 50 ms minimum delay between commands (critical!)
- **Quiet timeout:** 0.5 s to detect unterminated responses
- **Block data:** IEEE 488.2 definite-length format (`#<d><count><payload>`)

## Architecture

```
scpi-instruments/
├── scpi_mcp.py           # Main MCP server (24 tools)
├── scpi_transport.py     # Low-level TCP SCPI transport
├── connection_pool.py    # Persistent connection management
├── instruments/
│   ├── base.py           # BaseInstrument ABC
│   ├── rsa5065n.py       # RSA5065N spectrum analyser driver
│   └── mso8204.py        # MSO8204 oscilloscope driver
├── Dockerfile
└── requirements.txt
```

## Known Quirks

1. **50 ms pacing** - Commands silently dropped without inter-command delay
2. **RSA5065N `*RST` → RTSA mode** - Must switch to SA mode after reset
3. **RSA5065N frequency writes** - Use `:FREQ:` not `:SENS:FREQ:`
4. **RSA5065N attenuation** - `:POW:ATT` not `:INP:ATT`, minimum 10 dB
5. **`:FORM:DATA` persists across `*RST`** - Always set explicitly
6. **Quiet timeout** - 0.5 s for responses missing `\n` terminator

## Example Usage

```python
# Via MCP tools

# Connect to spectrum analyser
scpi_connect("rsa5065n")

# Configure 2.4 GHz sweep
rsa_configure_sweep(
    start_hz=2.4e9,
    stop_hz=2.4835e9,
    rbw_hz=100e3,
    points=1001
)

# Capture trace
result = rsa_sweep(trace=1)
# result["trace_dbm"] = [-80.1, -79.5, ...]

# Screenshot
rsa_screenshot("/tmp/spectrum.bmp")

# Connect to oscilloscope
scpi_connect("mso8204")

# Full characterisation
result = scope_characterise_channel(channel=1, autoscale=True)
# result = {
#   "frequency_hz": 1000.0,
#   "vpp_v": 3.3,
#   "rise_time_s": 1.2e-6,
#   "waveform_shape": "SQUARE",
#   ...
# }
```
