# Rigol DL3021A SCPI Reference

**Model:** Rigol DL3021A Programmable DC Electronic Load
**IP:** 10.0.1.105
**Port:** 5555
**Protocol:** Raw TCP/SCPI

## Overview

The DL3021A is a single-channel programmable DC electronic load with 150V/40A/200W capability. Supports CC, CV, CR, CP modes plus transient, list, OCP, and OPP testing.

## Specifications

| Parameter | Value |
|-----------|-------|
| Voltage | 0-150V |
| Current | 0-40A |
| Power | 0-200W |
| Resolution | 0.1mV, 0.1mA |

## Operating Modes

| Mode | Description |
|------|-------------|
| CC | Constant Current |
| CV | Constant Voltage |
| CR | Constant Resistance |
| CP | Constant Power |
| LIST | List/Sequence Mode |
| WAVE | Waveform Display |
| BATTERY | Battery Test |
| OCP | Over-Current Protection Test |
| OPP | Over-Power Protection Test |

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
| `*TST?` | Self-test |

### Input Control

| Command | Description |
|---------|-------------|
| `:SOURce:INPut:STATe ON|OFF` | Enable/disable input |
| `:SOURce:INPut:STATe?` | Query input state |
| `:SOURce:INPut:SHORt ON|OFF` | Short-circuit mode |

### Function Mode

| Command | Description |
|---------|-------------|
| `:SOURce:FUNCtion CURRent|RESistance|VOLTage|POWer` | Set static mode |
| `:SOURce:FUNCtion?` | Query current mode |
| `:SOURce:FUNCtion:MODE FIXed|LIST|WAVe|BATTery|OCP|OPP` | Set function mode |
| `:SOURce:FUNCtion:MODE?` | Query function mode |

### Trigger

| Command | Description |
|---------|-------------|
| `:TRIGger:SOURce BUS|EXTernal|MANUal` | Trigger source |
| `:TRIGger:SOURce?` | Query trigger source |
| `:SOURce:TRANsient ON|OFF` | Enable transient trigger |
| `*TRG` | Software trigger |

### Constant Current (CC) Mode

| Command | Description |
|---------|-------------|
| `:SOURce:CURRent:LEVel:IMMediate <A>` | Set load current |
| `:SOURce:CURRent:LEVel:IMMediate?` | Query load current |
| `:SOURce:CURRent:RANGe LOW|MIDDle|HIGH|MAX` | Set current range |
| `:SOURce:CURRent:RANGe?` | Query range |
| `:SOURce:CURRent:SLEW <A/us>` | Set slew rate |
| `:SOURce:CURRent:SLEW:POSitive <A/us>` | Rising slew rate |
| `:SOURce:CURRent:SLEW:NEGative <A/us>` | Falling slew rate |
| `:SOURce:CURRent:VON <V>` | Starting voltage |
| `:SOURce:CURRent:VLIMt <V>` | Voltage limit |
| `:SOURce:CURRent:ILIMt <A>` | Current limit |

### CC Transient Mode

| Command | Description |
|---------|-------------|
| `:SOURce:CURRent:TRANsient:MODE CONTinuous|PULSe|TOGGle` | Transient mode |
| `:SOURce:CURRent:TRANsient:ALEVel <A>` | Level A amplitude |
| `:SOURce:CURRent:TRANsient:BLEVel <A>` | Level B amplitude |
| `:SOURce:CURRent:TRANsient:AWIDth <s>` | Level A width |
| `:SOURce:CURRent:TRANsient:BWIDth <s>` | Level B width |
| `:SOURce:CURRent:TRANsient:FREQuency <Hz>` | Frequency (continuous) |
| `:SOURce:CURRent:TRANsient:PERiod <s>` | Period |
| `:SOURce:CURRent:TRANsient:ADUTy <pct>` | Duty cycle |

### Constant Voltage (CV) Mode

| Command | Description |
|---------|-------------|
| `:SOURce:VOLTage:LEVel:IMMediate <V>` | Set load voltage |
| `:SOURce:VOLTage:LEVel:IMMediate?` | Query load voltage |
| `:SOURce:VOLTage:RANGe LOW|HIGH|MAX` | Set voltage range |
| `:SOURce:VOLTage:VLIMt <V>` | Voltage limit |
| `:SOURce:VOLTage:ILIMt <A>` | Current limit |

### Constant Resistance (CR) Mode

| Command | Description |
|---------|-------------|
| `:SOURce:RESistance:LEVel:IMMediate <Ohm>` | Set load resistance |
| `:SOURce:RESistance:LEVel:IMMediate?` | Query resistance |
| `:SOURce:RESistance:RANGe LOW|MIDDle|HIGH|MAX` | Set range |
| `:SOURce:RESistance:VLIMt <V>` | Voltage limit |
| `:SOURce:RESistance:ILIMt <A>` | Current limit |

### Constant Power (CP) Mode

| Command | Description |
|---------|-------------|
| `:SOURce:POWer:LEVel:IMMediate <W>` | Set load power |
| `:SOURce:POWer:LEVel:IMMediate?` | Query power |
| `:SOURce:POWer:VLIMt <V>` | Voltage limit |
| `:SOURce:POWer:ILIMt <A>` | Current limit |

### OCP Test Mode

| Command | Description |
|---------|-------------|
| `:SOURce:OCP:RANGe LOW|HIGH|MAX` | Current range |
| `:SOURce:OCP:VON <V>` | Starting voltage |
| `:SOURce:OCP:VONDelay <s>` | Start delay |
| `:SOURce:OCP:ISET <A>` | Starting current |
| `:SOURce:OCP:ISTep <A>` | Current step |
| `:SOURce:OCP:IDELaystep <s>` | Step delay |
| `:SOURce:OCP:IMAX <A>` | Max current |
| `:SOURce:OCP:IMIN <A>` | Min current |
| `:SOURce:OCP:VOCP <V>` | Protection voltage |
| `:SOURce:OCP:TOCP <s>` | Max protection time |

### OPP Test Mode

| Command | Description |
|---------|-------------|
| `:SOURce:OPP:VON <V>` | Starting voltage |
| `:SOURce:OPP:VONDelay <s>` | Start delay |
| `:SOURce:OPP:PSET <W>` | Starting power |
| `:SOURce:OPP:PSTep <W>` | Power step |
| `:SOURce:OPP:PDELaystep <s>` | Step delay |
| `:SOURce:OPP:PMAX <W>` | Max power |
| `:SOURce:OPP:PMIN <W>` | Min power |
| `:SOURce:OPP:VOPP <V>` | Protection voltage |
| `:SOURce:OPP:TOPP <s>` | Max protection time |

### Measurements

| Command | Description |
|---------|-------------|
| `:MEASure:VOLTage?` | Measure voltage |
| `:MEASure:CURRent?` | Measure current |
| `:MEASure:POWer?` | Measure power |
| `:MEASure:RESistance?` | Measure resistance |
| `:MEASure:ALL?` | Measure V, I, P |
| `:FETCh:VOLTage?` | Fetch last voltage |
| `:FETCh:CURRent?` | Fetch last current |
| `:FETCh:POWer?` | Fetch last power |
| `:FETCh:CAPability?` | Fetch capability |

### Sense (Remote Voltage Sensing)

| Command | Description |
|---------|-------------|
| `:SOURce:SENSe ON|OFF` | Enable remote sense |
| `:SOURce:SENSe?` | Query sense state |
| `:REMote:SENSe:STATe ON|OFF` | (Undocumented) Enable remote sense |

### Waveform Display

| Command | Description |
|---------|-------------|
| `:SOURce:WAVe:TIMe <s>` | Window time |
| `:SOURce:WAVe:TSTep <s>` | Time step scale |

## Example Sequences

### Basic CC Load Test

```scpi
*RST
:SOURce:FUNCtion CURRent
:SOURce:CURRent:RANGe HIGH
:SOURce:CURRent:LEVel:IMMediate 1.0
:SOURce:INPut:STATe ON
:MEASure:ALL?
```

### CV Mode

```scpi
*RST
:SOURce:FUNCtion VOLTage
:SOURce:VOLTage:LEVel:IMMediate 5.0
:SOURce:INPut:STATe ON
:MEASure:ALL?
```

### Transient Test

```scpi
*RST
:SOURce:FUNCtion CURRent
:SOURce:CURRent:TRANsient:MODE CONTinuous
:SOURce:CURRent:TRANsient:ALEVel 0.5
:SOURce:CURRent:TRANsient:BLEVel 2.0
:SOURce:CURRent:TRANsient:FREQuency 1000
:SOURce:TRANsient ON
:SOURce:INPut:STATe ON
```

### OCP Test

```scpi
*RST
:SOURce:FUNCtion:MODE OCP
:SOURce:OCP:VON 12.0
:SOURce:OCP:ISET 0.1
:SOURce:OCP:ISTep 0.1
:SOURce:OCP:IMAX 5.0
:SOURce:INPut:STATe ON
```

## Known Quirks

1. **Remote sense:** Undocumented command `:REMote:SENSe:STATe` may be needed
2. **RS232 termination:** Uses `\r\n` (CRLF) not just `\n`
3. **Slew rate units:** A/us not A/s

## Proposed MCP Tools

| Tool | Description |
|------|-------------|
| `load_reset` | Reset to defaults |
| `load_input` | Enable/disable input (REQUIRES CONFIRMATION) |
| `load_cc` | Configure CC mode |
| `load_cv` | Configure CV mode |
| `load_cr` | Configure CR mode |
| `load_cp` | Configure CP mode |
| `load_transient` | Configure transient mode |
| `load_measure` | Read V, I, P measurements |
| `load_ocp_test` | Run OCP test sequence |
| `load_opp_test` | Run OPP test sequence |

## Sources

- [DL3000 Programming Manual](https://www.batronix.com/files/Rigol/Elektronische-Lasten/DL3000/DL3000_ProgrammingManual_EN.pdf)
- [rigol_dl3021a GitHub](https://github.com/charkster/rigol_dl3021a)
