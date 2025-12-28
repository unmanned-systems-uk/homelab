# HomeLab Status Check

Quick status overview of the HomeLab environment.

---

## Step 1: GitHub Issues

```bash
echo "=== Open GitHub Issues ==="
gh issue list --repo unmanned-systems-uk/homelab --state open --limit 10
```

---

## Step 2: SCPI Equipment

```bash
echo ""
echo "=== SCPI Equipment ==="
for addr in "101:5025:DMM" "105:5555:Load" "106:5555:Scope" "111:5025:PSU1" "120:5555:AWG" "138:5025:PSU2"; do
  ip="10.0.1.${addr%%:*}"
  rest="${addr#*:}"
  port="${rest%%:*}"
  name="${rest#*:}"
  timeout 1 bash -c "echo > /dev/tcp/$ip/$port" 2>/dev/null && echo "$name ($ip): UP" || echo "$name ($ip): DOWN"
done
```

---

## Step 3: Key Network Devices

```bash
echo ""
echo "=== Network Devices ==="
for entry in "1:UDM-Pro" "53:Pi5-DPM" "113:Jetson" "251:NAS"; do
  ip="10.0.1.${entry%%:*}"
  name="${entry#*:}"
  ping -c 1 -W 1 $ip &>/dev/null && echo "$name ($ip): UP" || echo "$name ($ip): DOWN"
done
```

---

## Step 4: Recent Sessions

```bash
echo ""
echo "=== Recent Session Summaries ==="
ls -1 docs/session-summary-*.md 2>/dev/null | tail -3 || echo "None found"
```

---

## Report

Present a summary table:

| Category | Status |
|----------|--------|
| GitHub Issues | X open |
| SCPI Equipment | X/6 online |
| Network Devices | Key devices up/down |
| Last Session | Date or None |
