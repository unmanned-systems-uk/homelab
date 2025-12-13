# SCPI Automation Skill

**Skill Name:** scpi-automation
**Version:** 1.0.0

---

## Purpose

This skill provides patterns for controlling SCPI-enabled test equipment on the HomeLab network.

---

## Allowed Tools

- Read, Write, Edit
- Bash (nc, timeout, network commands)
- Grep, Glob

---

## Equipment Reference

| Device | IP | Port | Model | Commands |
|--------|-----|------|-------|----------|
| DMM | 10.0.1.101 | 5025 | Keithley DMM6500 | SCPI + Keithley extensions |
| Oscilloscope | 10.0.1.106 | 5555 | Rigol MSO8204 | SCPI + Rigol extensions |
| Signal Gen | 10.0.1.120 | 5555 | Rigol DG2052 | SCPI standard |
| DC Load | 10.0.1.105 | 5555 | Rigol DL3021A | SCPI standard |
| PSU 1 | 10.0.1.111 | 5025 | Rigol DP932A | SCPI standard |
| PSU 2 | 10.0.1.138 | 5025 | Rigol DP932A | SCPI standard |

---

## SCPI Basics

### Common Commands (IEEE 488.2)

| Command | Description |
|---------|-------------|
| `*IDN?` | Query instrument identity |
| `*RST` | Reset to default state |
| `*CLS` | Clear status |
| `*OPC?` | Operation complete query |
| `*WAI` | Wait for operation complete |

### Query Pattern

```bash
# Basic query (using netcat)
echo "*IDN?" | nc -w 2 10.0.1.101 5025

# With timeout wrapper
timeout 3 bash -c 'echo "*IDN?" | nc 10.0.1.101 5025'
```

### Command Pattern

```bash
# Send command (no response expected)
echo "COMMAND:SETTING VALUE" | nc -w 1 10.0.1.111 5025

# Send command and verify
echo "COMMAND:SETTING VALUE; *OPC?" | nc -w 2 10.0.1.111 5025
```

---

## Device-Specific Patterns

### Keithley DMM6500

```bash
# Read DC voltage
echo "MEAS:VOLT:DC?" | nc -w 2 10.0.1.101 5025

# Read DC current
echo "MEAS:CURR:DC?" | nc -w 2 10.0.1.101 5025

# Read resistance
echo "MEAS:RES?" | nc -w 2 10.0.1.101 5025
```

### Rigol DP932A (PSU)

```bash
# Query output state
echo ":OUTP:STAT? CH1" | nc -w 2 10.0.1.111 5025

# Set voltage
echo ":SOUR:VOLT 5.0,CH1" | nc -w 1 10.0.1.111 5025

# Set current limit
echo ":SOUR:CURR 1.0,CH1" | nc -w 1 10.0.1.111 5025

# Enable output
echo ":OUTP:STAT ON,CH1" | nc -w 1 10.0.1.111 5025

# Measure actual voltage
echo ":MEAS:VOLT? CH1" | nc -w 2 10.0.1.111 5025
```

### Rigol DL3021A (DC Load)

```bash
# Set to constant current mode
echo ":SOUR:FUNC CURR" | nc -w 1 10.0.1.105 5555

# Set current
echo ":SOUR:CURR:LEV:IMM 1.0" | nc -w 1 10.0.1.105 5555

# Enable input
echo ":SOUR:INP:STAT ON" | nc -w 1 10.0.1.105 5555

# Measure voltage
echo ":MEAS:VOLT?" | nc -w 2 10.0.1.105 5555
```

### Rigol DG2052 (Signal Generator)

```bash
# Set frequency
echo ":SOUR1:FREQ 1000" | nc -w 1 10.0.1.120 5555

# Set amplitude
echo ":SOUR1:VOLT 1.0" | nc -w 1 10.0.1.120 5555

# Set waveform
echo ":SOUR1:FUNC SIN" | nc -w 1 10.0.1.120 5555

# Enable output
echo ":OUTP1:STAT ON" | nc -w 1 10.0.1.120 5555
```

### Rigol MSO8204 (Oscilloscope)

```bash
# Auto scale
echo ":AUT" | nc -w 1 10.0.1.106 5555

# Set timebase
echo ":TIM:SCAL 0.001" | nc -w 1 10.0.1.106 5555

# Measure frequency on CH1
echo ":MEAS:FREQ? CHAN1" | nc -w 2 10.0.1.106 5555

# Measure Vpp
echo ":MEAS:VPP? CHAN1" | nc -w 2 10.0.1.106 5555
```

---

## Automation Scripts

### Equipment Discovery

```bash
#!/bin/bash
# discover-scpi.sh - Find SCPI devices on network

HOSTS="101 105 106 111 120 138"
PORTS="5025 5555"

for host in $HOSTS; do
  for port in $PORTS; do
    result=$(timeout 2 bash -c "echo '*IDN?' | nc 10.0.1.$host $port 2>/dev/null")
    if [ -n "$result" ]; then
      echo "10.0.1.$host:$port - $result"
    fi
  done
done
```

### Measurement Logger

```bash
#!/bin/bash
# log-measurement.sh - Log DMM reading with timestamp

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
READING=$(echo "MEAS:VOLT:DC?" | nc -w 2 10.0.1.101 5025)
echo "$TIMESTAMP,$READING" >> measurements.csv
```

---

## Safety Rules

1. **NEVER** enable outputs without explicit user confirmation
2. **ALWAYS** verify settings before enabling power outputs
3. **ALWAYS** set current limits before voltage on PSUs
4. **LOG** all commands sent to equipment
5. **TIMEOUT** all network commands (2-3 seconds max)

---

## Error Handling

```bash
# Wrapper function for safe SCPI commands
scpi_query() {
  local ip=$1
  local port=$2
  local cmd=$3

  result=$(timeout 3 bash -c "echo '$cmd' | nc $ip $port 2>/dev/null")

  if [ -z "$result" ]; then
    echo "ERROR: No response from $ip:$port"
    return 1
  fi

  echo "$result"
  return 0
}

# Usage
scpi_query 10.0.1.101 5025 "*IDN?"
```

---

## Future: MCP Integration

When SCPI MCP server is built, it will provide:
- Tool-based equipment access
- Automatic safety checks
- Measurement history
- Equipment state tracking

---

## Resources

- Keithley DMM6500 Programming Manual
- Rigol DP900 Series Programming Guide
- Rigol DL3000 Series Programming Guide
- Rigol DG2000 Series Programming Guide
- Rigol MSO8000 Series Programming Guide
