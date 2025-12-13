# HomeLab Status Check

Quick status overview of the HomeLab environment.

---

## Step 1: CCPM Status

```bash
echo "=== CCPM Server ==="
curl -s http://localhost:8080/api/health | jq -r '.status // "DOWN"'
```

---

## Step 2: Sprint Status

```bash
echo ""
echo "=== Current Sprint ==="
curl -s "http://localhost:8080/api/sprints?project_id=5" | jq -r '.[] | select(.status == "active" or .status == "planned") | "Sprint \(.sprint_id): \(.sprint_name) [\(.status)]"'
```

---

## Step 3: Pending Tasks

```bash
echo ""
echo "=== Pending Tasks ==="
curl -s "http://localhost:8080/api/todos?project_id=5" | jq -r '.[] | select(.status != "status:complete") | "[\(.id)] \(.title) - \(.status)"'
```

---

## Step 4: GitHub Issues

```bash
echo ""
echo "=== Open GitHub Issues ==="
gh issue list --repo unmanned-systems-uk/homelab --state open --limit 5
```

---

## Step 5: Network Snapshot

```bash
echo ""
echo "=== Key Network Devices ==="
for ip in 1 53 113; do
  ping -c 1 -W 1 10.0.1.$ip &>/dev/null && echo "10.0.1.$ip: UP" || echo "10.0.1.$ip: DOWN"
done
```

---

## Report

Present a summary table:

| System | Status |
|--------|--------|
| CCPM Server | OK/DOWN |
| Sprint | Name (status) |
| Tasks | X pending |
| Issues | X open |
| Network | Key devices up/down |
