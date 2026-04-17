# Rigol DG2052 SCPI Reference

**Model:** Rigol DG2052 Function/Arbitrary Waveform Generator
**IP:** 10.0.1.120
**Port:** 5555
**Protocol:** Raw TCP/SCPI

## Overview

The DG2052 is a dual-channel function/arbitrary waveform generator with 50 MHz max frequency, 250 MSa/s sample rate, and 16 Mpts arbitrary waveform memory.

## Specifications

| Parameter | Value |
|-----------|-------|
| Channels | 2 |
| Sine | 1 μHz - 50 MHz |
| Square | 1 μHz - 15 MHz |
| Ramp | 1 μHz - 1.5 MHz |
| Pulse | 1 μHz - 15 MHz |
| Noise | 100 MHz bandwidth |
| Arb | 1 μHz - 10 MHz |
| Sample Rate | 250 MSa/s |
| Memory | 16 Mpts |

## Waveform Types

| Type | SCPI Value | Description |
|------|------------|-------------|
| Sine | `SIN` | Sine wave |
| Square | `SQU` | Square wave |
| Ramp | `RAMP` | Ramp/triangle |
| Pulse | `PULS` | Pulse |
| Noise | `NOIS` | White noise |
| DC | `DC` | DC level |
| Arbitrary | `ARB` | User-defined |
| Harmonic | `HARM` | Harmonic synthesis |

## Core SCPI Commands

### System/IEEE 488.2

| Command | Description |
|---------|-------------|
| `*IDN?` | Query identity |
| `*RST` | Reset to defaults |
| `*CLS` | Clear status |
| `*OPC?` | Operation complete |

### Output Control

| Command | Description |
|---------|-------------|
| `:OUTPut[1|2]:STATe ON|OFF` | Enable/disable output |
| `:OUTPut[1|2]:STATe?` | Query output state |
| `:OUTPut[1|2]:LOAD <ohm>|INF|DEF` | Set load impedance |
| `:OUTPut[1|2]:LOAD?` | Query load |
| `:OUTPut[1|2]:POLarity NORMal|INVerted` | Output polarity |
| `:OUTPut[1|2]:SYNC ON|OFF` | Sync output enable |

### Basic Waveform Configuration

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:FUNCtion <type>` | Set waveform type |
| `:SOURce[1|2]:FUNCtion?` | Query waveform type |
| `:SOURce[1|2]:FREQuency <Hz>` | Set frequency |
| `:SOURce[1|2]:FREQuency?` | Query frequency |
| `:SOURce[1|2]:PHASe <deg>` | Set phase (0-360) |
| `:SOURce[1|2]:PHASe?` | Query phase |

### Amplitude/Offset

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:VOLTage <Vpp>` | Set amplitude (Vpp) |
| `:SOURce[1|2]:VOLTage?` | Query amplitude |
| `:SOURce[1|2]:VOLTage:OFFSet <V>` | Set DC offset |
| `:SOURce[1|2]:VOLTage:OFFSet?` | Query offset |
| `:SOURce[1|2]:VOLTage:HIGH <V>` | Set high level |
| `:SOURce[1|2]:VOLTage:LOW <V>` | Set low level |
| `:SOURce[1|2]:VOLTage:UNIT VPP|VRMS|DBM` | Amplitude unit |

### Square Wave

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:FUNCtion:SQUare:DCYCle <pct>` | Set duty cycle |
| `:SOURce[1|2]:FUNCtion:SQUare:DCYCle?` | Query duty cycle |

### Ramp Wave

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:FUNCtion:RAMP:SYMMetry <pct>` | Set symmetry |
| `:SOURce[1|2]:FUNCtion:RAMP:SYMMetry?` | Query symmetry |

### Pulse

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:PULSe:DCYCle <pct>` | Duty cycle |
| `:SOURce[1|2]:PULSe:WIDTh <s>` | Pulse width |
| `:SOURce[1|2]:PULSe:TRANsition:LEADing <s>` | Rise time |
| `:SOURce[1|2]:PULSe:TRANsition:TRAiling <s>` | Fall time |

### Modulation - AM

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:AM:STATe ON|OFF` | Enable AM |
| `:SOURce[1|2]:AM:SOURce INTernal|EXTernal` | Modulation source |
| `:SOURce[1|2]:AM:DEPTh <pct>` | Modulation depth (0-120%) |
| `:SOURce[1|2]:AM:INTernal:FREQuency <Hz>` | Internal mod freq |
| `:SOURce[1|2]:AM:INTernal:FUNCtion <type>` | Internal mod shape |

### Modulation - FM

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:FM:STATe ON|OFF` | Enable FM |
| `:SOURce[1|2]:FM:DEViation <Hz>` | Frequency deviation |
| `:SOURce[1|2]:FM:INTernal:FREQuency <Hz>` | Internal mod freq |
| `:SOURce[1|2]:FM:INTernal:FUNCtion <type>` | Internal mod shape |

### Modulation - PM

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:PM:STATe ON|OFF` | Enable PM |
| `:SOURce[1|2]:PM:DEViation <deg>` | Phase deviation |
| `:SOURce[1|2]:PM:INTernal:FREQuency <Hz>` | Internal mod freq |

### Modulation - PWM

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:PWM:STATe ON|OFF` | Enable PWM |
| `:SOURce[1|2]:PWM:DEViation <pct>` | Duty cycle deviation |
| `:SOURce[1|2]:PWM:INTernal:FREQuency <Hz>` | Internal mod freq |

### Sweep

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:SWEep:STATe ON|OFF` | Enable sweep |
| `:SOURce[1|2]:SWEep:TIME <s>` | Sweep time |
| `:SOURce[1|2]:SWEep:FREQuency:STARt <Hz>` | Start frequency |
| `:SOURce[1|2]:SWEep:FREQuency:STOP <Hz>` | Stop frequency |
| `:SOURce[1|2]:SWEep:FREQuency:CENTer <Hz>` | Center frequency |
| `:SOURce[1|2]:SWEep:FREQuency:SPAN <Hz>` | Frequency span |
| `:SOURce[1|2]:SWEep:SPACing LINear|LOG` | Sweep spacing |
| `:SOURce[1|2]:SWEep:TRIGger:SOURce INTernal|EXTernal|MANual` | Trigger source |
| `:SOURce[1|2]:SWEep:HTIMe <s>` | Hold time |
| `:SOURce[1|2]:SWEep:RTIMe <s>` | Return time |

### Burst

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:BURSt:STATe ON|OFF` | Enable burst |
| `:SOURce[1|2]:BURSt:MODE TRIGgered|GATed|INFinity` | Burst mode |
| `:SOURce[1|2]:BURSt:NCYCles <n>` | Number of cycles |
| `:SOURce[1|2]:BURSt:INTernal:PERiod <s>` | Burst period |
| `:SOURce[1|2]:BURSt:PHASe <deg>` | Start phase |
| `:SOURce[1|2]:BURSt:TRIGger:SOURce INT|EXT|MAN` | Trigger source |
| `:SOURce[1|2]:BURSt:IDLe BOTTOM|CENTER|TOP` | Idle level |
| `:SOURce[1|2]:BURSt:GATE:POLarity NORMal|INVerted` | Gate polarity |
| `:SOURce[1|2]:BURSt:TRIGger:IMMediate` | Force trigger |

### Arbitrary Waveform

| Command | Description |
|---------|-------------|
| `:SOURce[1|2]:FUNCtion:ARBitrary <name>` | Load arb waveform |
| `:SOURce[1|2]:FUNCtion:ARBitrary?` | Query arb name |
| `:DATA:VOLatile:CLEar` | Clear volatile memory |
| `:DATA:ARBitrary <name>,<data>` | Upload arb data |

### Channel Coupling

| Command | Description |
|---------|-------------|
| `:COUPling:FREQuency:STATe ON|OFF` | Frequency coupling |
| `:COUPling:FREQuency:MODE RATIO|DEViation` | Coupling mode |
| `:COUPling:FREQuency:RATio <n>` | Frequency ratio |
| `:COUPling:PHASe:STATe ON|OFF` | Phase coupling |
| `:COUPling:AMPLitude:STATe ON|OFF` | Amplitude coupling |

### Phase Alignment

| Command | Description |
|---------|-------------|
| `:PHASe:INITiate` | Align phases (CH1 and CH2) |

## Example Sequences

### Basic 1 kHz Sine Wave

```scpi
*RST
:SOURce1:FUNCtion SIN
:SOURce1:FREQuency 1000
:SOURce1:VOLTage 1.0
:SOURce1:VOLTage:OFFSet 0
:OUTPut1:STATe ON
```

### Square Wave with 25% Duty Cycle

```scpi
*RST
:SOURce1:FUNCtion SQU
:SOURce1:FREQuency 10000
:SOURce1:VOLTage 3.3
:SOURce1:FUNCtion:SQUare:DCYCle 25
:OUTPut1:STATe ON
```

### Frequency Sweep

```scpi
*RST
:SOURce1:FUNCtion SIN
:SOURce1:VOLTage 1.0
:SOURce1:SWEep:STATe ON
:SOURce1:SWEep:FREQuency:STARt 100
:SOURce1:SWEep:FREQuency:STOP 100000
:SOURce1:SWEep:TIME 1.0
:SOURce1:SWEep:SPACing LOG
:OUTPut1:STATe ON
```

### Burst Mode (10 cycles)

```scpi
*RST
:SOURce1:FUNCtion SIN
:SOURce1:FREQuency 1000
:SOURce1:VOLTage 2.0
:SOURce1:BURSt:STATe ON
:SOURce1:BURSt:MODE TRIGgered
:SOURce1:BURSt:NCYCles 10
:SOURce1:BURSt:TRIGger:SOURce MAN
:OUTPut1:STATe ON
:SOURce1:BURSt:TRIGger:IMMediate
```

### AM Modulation

```scpi
*RST
:SOURce1:FUNCtion SIN
:SOURce1:FREQuency 100000
:SOURce1:VOLTage 2.0
:SOURce1:AM:STATe ON
:SOURce1:AM:SOURce INTernal
:SOURce1:AM:DEPTh 80
:SOURce1:AM:INTernal:FREQuency 1000
:SOURce1:AM:INTernal:FUNCtion SIN
:OUTPut1:STATe ON
```

### Dual Channel with Phase Offset

```scpi
*RST
:SOURce1:FUNCtion SIN
:SOURce1:FREQuency 1000
:SOURce1:VOLTage 1.0
:SOURce1:PHASe 0
:SOURce2:FUNCtion SIN
:SOURce2:FREQuency 1000
:SOURce2:VOLTage 1.0
:SOURce2:PHASe 90
:PHASe:INITiate
:OUTPut1:STATe ON
:OUTPut2:STATe ON
```

## Known Quirks

1. **Phase alignment:** Use `:PHASe:INITiate` after setting phase values
2. **Output impedance:** Default 50Ω, affects amplitude calculation
3. **Frequency limits:** Different limits per waveform type

## Proposed MCP Tools

| Tool | Description |
|------|-------------|
| `awg_reset` | Reset to defaults |
| `awg_output` | Enable/disable output (REQUIRES CONFIRMATION) |
| `awg_sine` | Configure sine wave |
| `awg_square` | Configure square wave |
| `awg_pulse` | Configure pulse |
| `awg_ramp` | Configure ramp/triangle |
| `awg_noise` | Configure noise output |
| `awg_sweep` | Configure frequency sweep |
| `awg_burst` | Configure burst mode |
| `awg_modulation` | Configure AM/FM/PM/PWM |
| `awg_dual_channel` | Configure dual-channel output |

## Sources

- [DG2000 Programming Guide](https://tw.rigol.com/tw/Images/DG2000_ProgrammingGuide_EN_tcm17-2836.pdf)
- [DG2000 User Guide](https://www.batronix.com/files/Rigol/Funktionsgeneratoren/DG2000/DG2000_UserGuide_EN.pdf)
