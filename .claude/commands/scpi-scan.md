# SCPI Equipment Scan

Scan all known SCPI equipment and report status.

---

## Execute Scan

```bash
echo "=== SCPI Equipment Status ==="
echo ""

# Define devices
declare -A DEVICES
DEVICES["10.0.1.101:5025"]="Keithley DMM6500"
DEVICES["10.0.1.105:5555"]="Rigol DL3021A (DC Load)"
DEVICES["10.0.1.106:5555"]="Rigol MSO8204 (Scope)"
DEVICES["10.0.1.111:5025"]="Rigol DP932A (PSU 1)"
DEVICES["10.0.1.120:5555"]="Rigol DG2052 (AWG)"
DEVICES["10.0.1.138:5025"]="Rigol DP932A (PSU 2)"

for addr in "${!DEVICES[@]}"; do
  ip=$(echo $addr | cut -d: -f1)
  port=$(echo $addr | cut -d: -f2)
  name=${DEVICES[$addr]}

  result=$(timeout 2 bash -c "echo '*IDN?' | nc $ip $port 2>/dev/null" | tr -d '\n')

  if [ -n "$result" ]; then
    echo "✓ $name ($addr)"
    echo "  $result"
  else
    echo "✗ $name ($addr) - OFFLINE"
  fi
  echo ""
done
```

---

## Report Format

Present results as:

| Device | IP:Port | Status | Identity |
|--------|---------|--------|----------|
| DMM | 10.0.1.101:5025 | Online/Offline | IDN response |
| ... | ... | ... | ... |
