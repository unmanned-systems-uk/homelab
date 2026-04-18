# DMM6500 TSP Command Reference

TSP (Test Script Processor) is a Lua-based scripting language for Keithley instruments. This document covers TSP mode for the DMM6500 6½-digit multimeter.

## Switching to TSP Mode

TSP mode must be set from the front panel:
1. Press **MENU**
2. Navigate to **System** → **Settings**
3. Select **Command Set** → **TSP**
4. Instrument will prompt to reboot - confirm

**Note:** You cannot combine SCPI and TSP commands. Choose one mode.

## MCP Tools (19 total)

### Basic Measurements (7 tools)

| Tool | Description |
|------|-------------|
| `dmm_tsp_reset` | Reset DMM to defaults |
| `dmm_tsp_configure` | Configure measurement function, range, NPLC |
| `dmm_tsp_measure` | Single measurement with current config |
| `dmm_tsp_measure_dcv` | Quick DC voltage measurement |
| `dmm_tsp_measure_dci` | Quick DC current measurement |
| `dmm_tsp_measure_resistance` | 2W/4W resistance measurement |
| `dmm_tsp_measure_temperature` | Temperature (RTD/thermistor) |

### Digitizing - High-Speed Sampling (3 tools)

| Tool | Description |
|------|-------------|
| `dmm_tsp_digitize_configure` | Set function, sample rate, count |
| `dmm_tsp_digitize_read` | Read captured samples from buffer |
| `dmm_tsp_digitize_trigger` | Configure analog trigger for capture |

### Buffers (4 tools)

| Tool | Description |
|------|-------------|
| `dmm_tsp_buffer_create` | Create named reading buffer |
| `dmm_tsp_buffer_read` | Read buffer contents |
| `dmm_tsp_buffer_clear` | Clear buffer |
| `dmm_tsp_buffer_stats` | Get min, max, mean, stddev |

### Trigger Model (3 tools)

| Tool | Description |
|------|-------------|
| `dmm_tsp_trigger_load` | Load trigger model template |
| `dmm_tsp_trigger_initiate` | Start trigger model |
| `dmm_tsp_trigger_abort` | Abort running trigger model |

### Scripting (2 tools)

| Tool | Description |
|------|-------------|
| `dmm_tsp_execute` | Execute arbitrary TSP Lua script |
| `dmm_tsp_query` | Execute expression and return result |

---

## TSP Command Syntax

### Function Constants

| Friendly Name | TSP Constant |
|---------------|--------------|
| `dcv` | `dmm.FUNC_DC_VOLTAGE` |
| `acv` | `dmm.FUNC_AC_VOLTAGE` |
| `dci` | `dmm.FUNC_DC_CURRENT` |
| `aci` | `dmm.FUNC_AC_CURRENT` |
| `res` | `dmm.FUNC_RESISTANCE` |
| `fres` | `dmm.FUNC_4W_RESISTANCE` |
| `temp` | `dmm.FUNC_TEMPERATURE` |
| `freq` | `dmm.FUNC_FREQUENCY` |
| `cap` | `dmm.FUNC_CAPACITANCE` |
| `diode` | `dmm.FUNC_DIODE` |
| `cont` | `dmm.FUNC_CONTINUITY` |

### Digitize Function Constants

| Friendly Name | TSP Constant |
|---------------|--------------|
| `dcv` | `dmm.FUNC_DIGITIZE_VOLTAGE` |
| `dci` | `dmm.FUNC_DIGITIZE_CURRENT` |

---

## Common TSP Commands

### Basic Measurement

```lua
-- Reset instrument
reset()

-- Configure DC voltage measurement
dmm.measure.func = dmm.FUNC_DC_VOLTAGE
dmm.measure.autorange = dmm.ON
dmm.measure.nplc = 1

-- Take reading
reading = dmm.measure.read()
print(reading)
```

### High-Speed Digitizing

```lua
-- Configure digitize
dmm.digitize.func = dmm.FUNC_DIGITIZE_VOLTAGE
dmm.digitize.range = 10
dmm.digitize.samplerate = 50000  -- 50 kSa/s
dmm.digitize.count = 10000       -- 10k samples

-- Configure trigger
dmm.digitize.analogtrigger.mode = dmm.MODE_EDGE
dmm.digitize.analogtrigger.edge.level = 1.0
dmm.digitize.analogtrigger.edge.slope = dmm.SLOPE_RISING

-- Capture
trigger.model.load("SimpleLoop", 1)
trigger.model.initiate()
waitcomplete()

-- Read results
printbuffer(1, defbuffer1.n, defbuffer1.readings)
```

### Buffer Operations

```lua
-- Create custom buffer
mybuffer = buffer.make(5000, buffer.STYLE_STANDARD)

-- Configure to use buffer
dmm.measure.func = dmm.FUNC_DC_VOLTAGE
dmm.measure.count = 100
dmm.measure.read(mybuffer)

-- Get statistics
stats = buffer.getstats(mybuffer)
print(stats.mean, stats.stddev, stats.min, stats.max)

-- Read buffer data
printbuffer(1, mybuffer.n, mybuffer.readings)

-- Clear buffer
mybuffer.clear()
```

### Trigger Model Templates

| Template | Description |
|----------|-------------|
| `SimpleLoop` | Take N readings in a loop |
| `DurationLoop` | Take readings for X seconds |
| `GradeBinning` | Grade/sort readings into bins |
| `Empty` | Custom trigger model (add blocks manually) |

```lua
-- Simple loop: take 100 readings
trigger.model.load("SimpleLoop", 100)
trigger.model.initiate()
waitcomplete()

-- Duration loop: measure for 5 seconds
trigger.model.load("DurationLoop", 5)
trigger.model.initiate()
waitcomplete()
```

---

## Key TSP Objects

| Object | Purpose |
|--------|---------|
| `dmm.measure` | Standard measurement config |
| `dmm.digitize` | High-speed sampling config |
| `buffer` | Buffer management |
| `defbuffer1` | Default reading buffer |
| `trigger.model` | Sequenced operations |
| `localnode` | Instrument info (model, serial, etc.) |
| `eventlog` | Error/event logging |

---

## Auto-Detection

The MCP server auto-detects TSP vs SCPI mode on first connection:
1. Tries SCPI `*IDN?` command
2. If fails, tries TSP `print(localnode.model)`
3. Logs detected mode

If DMM is in SCPI mode but you call TSP tools, you'll get errors.

---

## Sources

- [Tektronix DMM6500 Reference Manual](https://www.tek.com/en/tektronix-and-keithley-digital-multimeter/dmm6500-manual/model-dmm6500-6-1-2-digit-multimeter-3)
- [TSP Application Note](https://download.tek.com/document/1KW-61540-0_Script_with_TSP_Application_Note_031121.pdf)

---

*Last Updated: 2026-04-18*
