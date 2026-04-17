# Keithley DMM6500 SCPI Reference

**Model:** Keithley DMM6500 6½-Digit Multimeter
**IP:** 10.0.1.101
**Port:** 5025
**Protocol:** Raw TCP/SCPI

## Overview

The DMM6500 is a bench/system digital multimeter with 6.5-digit resolution and scanning capabilities. It supports both SCPI and TSP command sets.

## Connection

- **Interface:** LXI/Ethernet (TCP/IP)
- **Default Port:** 5025
- **Line Termination:** `\n` (LF)

## Measurement Functions

| Function | SCPI Value | Description |
|----------|------------|-------------|
| DC Voltage | `VOLT:DC` | DC voltage measurement |
| AC Voltage | `VOLT:AC` | AC voltage (RMS) |
| DC Current | `CURR:DC` | DC current measurement |
| AC Current | `CURR:AC` | AC current (RMS) |
| 2-Wire Resistance | `RES` | 2-wire resistance |
| 4-Wire Resistance | `FRES` | 4-wire resistance |
| Temperature | `TEMP` | Temperature (RTD/thermocouple) |
| Frequency | `FREQ` | Frequency measurement |
| Period | `PER` | Period measurement |
| Diode | `DIOD` | Diode test |
| Continuity | `CONT` | Continuity test |
| Capacitance | `CAP` | Capacitance measurement |

## Core SCPI Commands

### System Commands

| Command | Description |
|---------|-------------|
| `*IDN?` | Query instrument identity |
| `*RST` | Reset to default state |
| `*CLS` | Clear status registers |
| `*OPC?` | Operation complete query |
| `*WAI` | Wait for operation complete |
| `:SYST:ERR:NEXT?` | Query next error |
| `:SYST:ERR:ALL?` | Query all errors |
| `:SYST:CLEAR` | Clear system log |
| `:SYST:LFR?` | Query line frequency (50/60 Hz) |

### Measurement Configuration

| Command | Description |
|---------|-------------|
| `:SENS:FUNC "<func>"` | Set measurement function |
| `:SENS:FUNC?` | Query current function |
| `:CONF:<func>` | Configure for measurement |
| `:MEAS:<func>?` | Configure, trigger, and read |
| `:READ?` | Trigger and read |
| `:FETC?` | Fetch last reading |

### Range Settings

| Command | Description |
|---------|-------------|
| `:SENS:<func>:RANG <value>` | Set measurement range |
| `:SENS:<func>:RANG?` | Query current range |
| `:SENS:<func>:RANG:AUTO ON|OFF` | Auto-range enable |
| `:SENS:<func>:RANG:AUTO?` | Query auto-range state |

### Integration Time (NPLC)

| Command | Description |
|---------|-------------|
| `:SENS:<func>:NPLC <value>` | Set NPLC (0.0005 to 15) |
| `:SENS:<func>:NPLC?` | Query NPLC setting |

NPLC values: 0.0005, 0.0015, 0.005, 0.01, 0.1, 1, 10, 15

### Auto-Zero

| Command | Description |
|---------|-------------|
| `:SENS:<func>:AZER ON|OFF` | Enable/disable auto-zero |
| `:SENS:<func>:AZER?` | Query auto-zero state |

### Display

| Command | Description |
|---------|-------------|
| `:DISP:CLEAR` | Clear user display |
| `:DISP:USER1:TEXT "<text>"` | Set user text line 1 |
| `:DISP:USER2:TEXT "<text>"` | Set user text line 2 |
| `:DISP:SCREEN HOME|USER` | Set display screen |

### Triggering

| Command | Description |
|---------|-------------|
| `:TRIG:SOUR IMM|EXT|BUS|TIM` | Set trigger source |
| `:TRIG:COUN <n>` | Set trigger count |
| `:TRIG:DEL <seconds>` | Set trigger delay |
| `:INIT` | Initiate measurement |
| `*TRG` | Send bus trigger |

### Data Format

| Command | Description |
|---------|-------------|
| `:FORM:DATA ASC|REAL` | Set data format |
| `:FORM:ELEM READ,UNIT,TSTAMP` | Set reading elements |

## Example Sequences

### Basic DC Voltage Measurement

```scpi
*RST
:SENS:FUNC "VOLT:DC"
:SENS:VOLT:DC:RANG:AUTO ON
:SENS:VOLT:DC:NPLC 1
:READ?
```

### High-Accuracy Measurement

```scpi
*RST
:SENS:FUNC "VOLT:DC"
:SENS:VOLT:DC:RANG 10
:SENS:VOLT:DC:NPLC 10
:SENS:VOLT:DC:AZER ON
:INIT
*OPC?
:FETC?
```

### 4-Wire Resistance

```scpi
*RST
:SENS:FUNC "FRES"
:SENS:FRES:RANG:AUTO ON
:SENS:FRES:NPLC 1
:READ?
```

### Temperature (RTD)

```scpi
*RST
:SENS:FUNC "TEMP"
:SENS:TEMP:TRAN FRTD
:SENS:TEMP:RTD:FOUR PT100
:READ?
```

## Known Quirks

1. **Line frequency detection:** Use `:SYST:LFR?` to verify 50/60 Hz for NPLC calculations
2. **Buffer operations:** Default buffer is `defbuffer1`
3. **Emulation modes:** Supports Keysight 34401A and Keithley 2000 command sets

## Proposed MCP Tools

| Tool | Description |
|------|-------------|
| `dmm_reset` | Reset to defaults |
| `dmm_configure` | Configure measurement function, range, NPLC |
| `dmm_measure` | Single measurement with current config |
| `dmm_measure_dcv` | Quick DC voltage measurement |
| `dmm_measure_dcl` | Quick DC current measurement |
| `dmm_measure_res` | Quick resistance measurement |
| `dmm_measure_temp` | Quick temperature measurement |

## Sources

- [Keithley DMM6500 Reference Manual](https://download.tek.com/manual/DMM6500-901-01B_Sept_2019_Ref.pdf)
- [py-DMM6500 GitHub](https://github.com/kasper64/py-DMM6500)
