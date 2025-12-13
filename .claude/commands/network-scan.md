# Network Scan

Scan the 10.0.1.x subnet for live hosts.

---

## Quick Scan

```bash
echo "=== Scanning 10.0.1.x subnet ==="
echo "This may take 30-60 seconds..."
echo ""

for i in {1..254}; do
  (ping -c 1 -W 1 10.0.1.$i &>/dev/null && echo "10.0.1.$i") &
done 2>/dev/null | sort -t. -k4 -n
wait

echo ""
echo "Scan complete."
```

---

## Known Devices Reference

Cross-reference results with known devices:

| IP | Known Device |
|----|--------------|
| 10.0.1.1 | Gateway (USG-Pro-4) |
| 10.0.1.53 | Pi5 (DPM-Air) |
| 10.0.1.92 | Android H16 (DPM Ground) |
| 10.0.1.101 | Keithley DMM6500 |
| 10.0.1.105 | Rigol DL3021A |
| 10.0.1.106 | Rigol MSO8204 |
| 10.0.1.111 | Rigol DP932A |
| 10.0.1.113 | Jetson Orin NX |
| 10.0.1.120 | Rigol DG2052 |
| 10.0.1.138 | Rigol DP932A |
