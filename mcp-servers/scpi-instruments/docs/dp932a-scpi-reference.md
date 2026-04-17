# Rigol DP932A SCPI Reference

**Model:** Rigol DP932A Programmable Linear DC Power Supply
**IPs:** 10.0.1.111 (PSU-1), 10.0.1.138 (PSU-2)
**Port:** 5025
**Protocol:** Raw TCP/SCPI

## Overview

The DP932A is a 3-channel programmable linear DC power supply with 212W total power, low ripple, and high resolution.

## Specifications

| Channel | Voltage | Current | Power |
|---------|---------|---------|-------|
| CH1 | 0-32V | 0-3A | 96W |
| CH2 | 0-32V | 0-3A | 96W |
| CH3 | 0-6V | 0-3A | 18W |
| **Total** | - | - | **212W** |

## Core SCPI Commands

### System/IEEE 488.2

| Command | Description |
|---------|-------------|
| `*IDN?` | Query identity |
| `*RST` | Reset to defaults |
| `*CLS` | Clear status |
| `*OPC?` | Operation complete |
| `*ESE <n>` | Event status enable |
| `*ESR?` | Event status register |
| `*STB?` | Status byte |
| `*SAV <n>` | Save state (1-10) |
| `*RCL <n>` | Recall state (1-10) |

### Channel Selection

| Command | Description |
|---------|-------------|
| `:INSTrument[:SELect] CH1|CH2|CH3` | Select active channel |
| `:INSTrument[:SELect]?` | Query active channel |
| `:INSTrument:NSELect 1|2|3` | Select by number |
| `:INSTrument:NSELect?` | Query channel number |

### Output Control

| Command | Description |
|---------|-------------|
| `:OUTPut[:STATe] ON|OFF[,CH1|CH2|CH3]` | Enable/disable output |
| `:OUTPut[:STATe]? [CH1|CH2|CH3]` | Query output state |
| `:OUTPut:TRACK 0|1|2` | Tracking mode (0=ind, 1=ser, 2=par) |
| `:OUTPut:TRACK?` | Query tracking mode |
| `:OUTPut:OCP[:STATe] ON|OFF[,CH1|CH2|CH3]` | OCP enable |
| `:OUTPut:OCP:VALue <A>[,CH1|CH2|CH3]` | OCP value |
| `:OUTPut:OCP:DELay <ms>[,CH1|CH2|CH3]` | OCP delay (0-1000 ms) |
| `:OUTPut:OVP[:STATe] ON|OFF[,CH1|CH2|CH3]` | OVP enable |
| `:OUTPut:OVP:VALue <V>[,CH1|CH2|CH3]` | OVP value |

### Voltage Settings

| Command | Description |
|---------|-------------|
| `[:SOURce]:VOLTage <V>[,CH1|CH2|CH3]` | Set voltage |
| `[:SOURce]:VOLTage? [CH1|CH2|CH3]` | Query set voltage |
| `[:SOURce]:VOLTage:STEP <V>` | Set voltage step |
| `[:SOURce]:VOLTage:STEP?` | Query voltage step |
| `[:SOURce]:VOLTage:PROTection <V>[,CH1|CH2|CH3]` | OVP voltage |
| `[:SOURce]:VOLTage:PROTection:CLEar` | Clear OVP trip |

### Current Settings

| Command | Description |
|---------|-------------|
| `[:SOURce]:CURRent <A>[,CH1|CH2|CH3]` | Set current limit |
| `[:SOURce]:CURRent? [CH1|CH2|CH3]` | Query current limit |
| `[:SOURce]:CURRent:STEP <A>` | Set current step |
| `[:SOURce]:CURRent:STEP?` | Query current step |
| `[:SOURce]:CURRent:PROTection <A>[,CH1|CH2|CH3]` | OCP current |
| `[:SOURce]:CURRent:PROTection:CLEar` | Clear OCP trip |

### Measurements

| Command | Description |
|---------|-------------|
| `:MEASure:VOLTage? [CH1|CH2|CH3]` | Measure voltage |
| `:MEASure:CURRent? [CH1|CH2|CH3]` | Measure current |
| `:MEASure:POWer? [CH1|CH2|CH3]` | Measure power |
| `:MEASure:ALL? [CH1|CH2|CH3]` | Measure V, I, P |

### Direct Channel Commands (Preferred)

These commands specify the channel directly without needing `:INST`:

| Command | Description |
|---------|-------------|
| `:VOLT <V>,CH1` | Set CH1 voltage |
| `:CURR <A>,CH2` | Set CH2 current |
| `:MEAS:VOLT? CH3` | Measure CH3 voltage |
| `:OUTP ON,CH1` | Enable CH1 output |

### Timer/Delay

| Command | Description |
|---------|-------------|
| `:TIMer[:STATe] ON|OFF[,CH1|CH2|CH3]` | Enable timer |
| `:TIMer:CYCLes <n>` | Number of cycles (1-99999, INF) |
| `:TIMer:ENDState LAST|OFF` | End state |
| `:TIMer:GROups <n>` | Number of groups (1-2048) |
| `:TIMer:PARAmeters <g>,<v>,<i>,<t>` | Set group params |

### Analyzer (Waveform Recording)

| Command | Description |
|---------|-------------|
| `:ANALyzer[:STATe] ON|OFF` | Enable analyzer |
| `:ANALyzer:CURRent:STARt` | Start current recording |
| `:ANALyzer:VOLTage:STARt` | Start voltage recording |
| `:ANALyzer:STOP` | Stop recording |

### System

| Command | Description |
|---------|-------------|
| `:SYSTem:ERRor?` | Query error |
| `:SYSTem:VERSion?` | Query firmware |
| `:SYSTem:LOCal` | Set to local mode |
| `:SYSTem:REMote` | Set to remote mode |
| `:SYSTem:RWLock` | Lock front panel |

### Memory

| Command | Description |
|---------|-------------|
| `:MEMory:LOCK <n>,ON|OFF` | Lock/unlock file |
| `:MEMory:DELete <n>` | Delete file |
| `:MEMory:RECall <n>` | Recall file |
| `:MEMory:SAVE <n>` | Save to file |

## Example Sequences

### Basic Single Channel Output

```scpi
*RST
:VOLT 12.0,CH1
:CURR 1.0,CH1
:OUTP ON,CH1
:MEAS:ALL? CH1
```

### Multiple Channels

```scpi
*RST
:VOLT 5.0,CH1
:CURR 2.0,CH1
:VOLT 3.3,CH2
:CURR 1.0,CH2
:VOLT 1.8,CH3
:CURR 0.5,CH3
:OUTP ON,CH1
:OUTP ON,CH2
:OUTP ON,CH3
```

### With OVP/OCP Protection

```scpi
*RST
:VOLT 12.0,CH1
:CURR 2.0,CH1
:OUTP:OVP ON,CH1
:OUTP:OVP:VAL 14.0,CH1
:OUTP:OCP ON,CH1
:OUTP:OCP:VAL 2.5,CH1
:OUTP ON,CH1
```

### Tracking Mode (Series)

```scpi
*RST
:OUTP:TRACK 1
:VOLT 12.0,CH1
:CURR 1.0,CH1
:OUTP ON,CH1
:OUTP ON,CH2
```
*Note: In series mode, CH1 and CH2 outputs combine for 0-64V*

### Query All Measurements

```scpi
:MEAS:VOLT? CH1
:MEAS:CURR? CH1
:MEAS:POW? CH1
:MEAS:VOLT? CH2
:MEAS:CURR? CH2
:MEAS:POW? CH2
:MEAS:VOLT? CH3
:MEAS:CURR? CH3
:MEAS:POW? CH3
```

## Known Quirks

1. **Channel parameter:** Direct commands with `,CH<n>` are faster than `:INST` switching
2. **Default port:** 5025 (not 5555 like other Rigol instruments)
3. **Power-on state:** Configurable via `:PROJect:POWEron:OUTPut`
4. **Front panel lock:** Use `:SYST:RWLock` to prevent local changes

## Safety Considerations

**CRITICAL:** Enabling outputs can damage connected equipment.

1. Always verify voltage/current settings before enabling output
2. Use OVP/OCP protection where possible
3. Verify measurements after enabling

## Proposed MCP Tools

| Tool | Description |
|------|-------------|
| `psu_reset` | Reset to defaults |
| `psu_output` | Enable/disable output (REQUIRES CONFIRMATION) |
| `psu_set_channel` | Configure V/I for a channel |
| `psu_measure` | Read V/I/P measurements |
| `psu_protection` | Configure OVP/OCP |
| `psu_tracking` | Configure tracking mode |
| `psu_all_off` | Disable all outputs |

## Sources

- [DP900 Programming Guide](https://www.batronix.com/files/Rigol/Labornetzteile/DP900/DP900_ProgrammingGuide_en.pdf)
- [DP800 Programming Guide](https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DP800_ProgrammingGuide_EN.pdf)
- [dp832-multitool GitHub](https://github.com/marcusfolkesson/dp832-multitool)
