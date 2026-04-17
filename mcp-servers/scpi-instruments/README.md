# SCPI Instruments MCP Server

MCP server providing tool access to SCPI-enabled test equipment via raw TCP sockets.

## Instruments (7 Total)

| Instrument | Model | IP | Port | Type |
|------------|-------|-----|------|------|
| Spectrum Analyser | Rigol RSA5065N | 10.0.1.85 | 5555 | Real-time spectrum analyser |
| Oscilloscope | Rigol MSO8204 | 10.0.1.106 | 5555 | 4-ch mixed signal oscilloscope |
| Multimeter | Keithley DMM6500 | 10.0.1.101 | 5025 | 6.5-digit multimeter |
| DC Load | Rigol DL3021A | 10.0.1.105 | 5555 | 150V/40A/200W electronic load |
| AWG | Rigol DG2052 | 10.0.1.120 | 5555 | 50MHz dual-ch function generator |
| PSU-1 | Rigol DP932A | 10.0.1.111 | 5025 | Triple output power supply |
| PSU-2 | Rigol DP932A | 10.0.1.138 | 5025 | Triple output power supply |

## MCP Tools (60 total)

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

### MSO8204 - Oscilloscope (15)

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
| `scope_counter` | Hardware frequency counter (accurate) |
| `scope_characterise_channel` | Full signal characterisation |
| `scope_characterise_dual` | Dual channel + phase measurement |
| `scope_reference_status` | Query reference clock source (INT/EXT) |

### DMM6500 - Multimeter (7)

| Tool | Description |
|------|-------------|
| `dmm_reset` | Reset to defaults |
| `dmm_configure` | Configure measurement function, range, NPLC |
| `dmm_measure` | Single measurement with current config |
| `dmm_measure_dcv` | Quick DC voltage measurement |
| `dmm_measure_dci` | Quick DC current measurement |
| `dmm_measure_resistance` | 2-wire or 4-wire resistance |
| `dmm_measure_temperature` | Temperature (RTD/thermocouple) |

### DL3021A - DC Electronic Load (8)

| Tool | Description |
|------|-------------|
| `load_reset` | Reset to defaults (input OFF) |
| `load_input` | Enable/disable input |
| `load_cc` | Configure Constant Current mode |
| `load_cv` | Configure Constant Voltage mode |
| `load_cr` | Configure Constant Resistance mode |
| `load_cp` | Configure Constant Power mode |
| `load_measure` | Read V, I, P measurements |
| `load_transient` | Configure transient/dynamic mode |

### DG2052 - Function Generator (10)

| Tool | Description |
|------|-------------|
| `awg_reset` | Reset to defaults (outputs OFF) |
| `awg_output` | Enable/disable channel output |
| `awg_sine` | Configure sine wave |
| `awg_square` | Configure square wave |
| `awg_pulse` | Configure pulse |
| `awg_ramp` | Configure ramp/triangle |
| `awg_noise` | Configure noise output |
| `awg_sweep` | Configure frequency sweep |
| `awg_burst` | Configure burst mode |
| `awg_dual_channel` | Dual-channel with phase offset |

### DP932A - Power Supply (9)

| Tool | Description |
|------|-------------|
| `psu_reset` | Reset to defaults (outputs OFF) |
| `psu_output` | Enable/disable channel output |
| `psu_all_off` | Disable all outputs |
| `psu_set_channel` | Set voltage and current |
| `psu_measure` | Read V, I, P for channel |
| `psu_measure_all` | Read all channels |
| `psu_protection` | Configure OVP/OCP |
| `psu_tracking` | Set tracking mode (series/parallel) |
| `psu_quick_output` | Configure and enable in one call |

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
  -e DMM6500_IP=10.0.1.101 \
  -e DL3021A_IP=10.0.1.105 \
  -e DG2052_IP=10.0.1.120 \
  -e DP932A_1_IP=10.0.1.111 \
  -e DP932A_2_IP=10.0.1.138 \
  scpi-instruments
```

### Local

```bash
# Install dependencies
pip install -r requirements.txt

# Run
export RSA5065N_IP=10.0.1.85
export MSO8204_IP=10.0.1.106
export DMM6500_IP=10.0.1.101
export DL3021A_IP=10.0.1.105
export DG2052_IP=10.0.1.120
export DP932A_1_IP=10.0.1.111
export DP932A_2_IP=10.0.1.138
python scpi_mcp.py
```

### MCP Configuration

Add to `.mcp.json` (local network):

```json
{
  "mcpServers": {
    "scpi-instruments": {
      "type": "streamable-http",
      "url": "http://10.0.1.202:8081/mcp"
    }
  }
}
```

Via Cloudflare Tunnel (external):

```json
{
  "mcpServers": {
    "scpi-instruments": {
      "type": "streamable-http",
      "url": "https://scpi-mcp.unmanned-systems.uk/mcp"
    }
  }
}
```

## Transport Protocol

- **Protocol:** Raw TCP socket (NOT pyvisa, NOT VXI-11, NOT HiSLIP)
- **Ports:** 5555 for Rigol instruments, 5025 for Keithley/PSU
- **Line termination:** `\n` on send; responses may omit trailing `\n`
- **Pacing:** 50 ms minimum delay between commands (critical for Rigol!)
- **Quiet timeout:** 0.5 s to detect unterminated responses
- **Block data:** IEEE 488.2 definite-length format (`#<d><count><payload>`)

## Architecture

```
scpi-instruments/
├── scpi_mcp.py           # Main MCP server (59 tools)
├── scpi_transport.py     # Low-level TCP SCPI transport
├── connection_pool.py    # Persistent connection management
├── instruments/
│   ├── base.py           # BaseInstrument ABC
│   ├── rsa5065n.py       # RSA5065N spectrum analyser driver
│   ├── mso8204.py        # MSO8204 oscilloscope driver
│   ├── dmm6500.py        # DMM6500 multimeter driver
│   ├── dl3021a.py        # DL3021A electronic load driver
│   ├── dg2052.py         # DG2052 function generator driver
│   └── dp932a.py         # DP932A power supply driver
├── docs/
│   ├── dmm6500-scpi-reference.md
│   ├── dl3021a-scpi-reference.md
│   ├── dg2052-scpi-reference.md
│   └── dp932a-scpi-reference.md
├── Dockerfile
└── requirements.txt
```

## Safety Notes

**CRITICAL:** Several tools can enable outputs that apply voltage/current:

| Tool | Risk | Mitigation |
|------|------|------------|
| `load_input` | Sinks current from source | Verify source can handle load |
| `awg_output` | Produces signal | Verify connected device tolerance |
| `psu_output` | Applies voltage | Verify load can handle voltage |
| `psu_quick_output` | Applies voltage immediately | Use with caution |

Always verify configuration before enabling outputs.

## Known Quirks

1. **50 ms pacing** - Commands silently dropped without inter-command delay
2. **RSA5065N `*RST` → RTSA mode** - Must switch to SA mode after reset
3. **RSA5065N frequency writes** - Use `:FREQ:` not `:SENS:FREQ:`
4. **RSA5065N attenuation** - `:POW:ATT` not `:INP:ATT`, minimum 10 dB
5. **`:FORM:DATA` persists across `*RST`** - Always set explicitly
6. **Quiet timeout** - 0.5 s for responses missing `\n` terminator
7. **DMM6500 port** - Uses 5025, not 5555
8. **DP932A port** - Uses 5025, not 5555
