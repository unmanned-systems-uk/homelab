# Database Quick Reference Card (QRC)

**Last Updated:** 2026-01-08

---

## CCPM Database (ccpm_db)

### Connection Details

```bash
# Full connection string
postgresql://ccpm:CcpmDb2025Secure@10.0.1.251:5433/ccpm_db

# Connection components
Host:     10.0.1.251 (Synology NAS)
Port:     5433
Database: ccpm_db
User:     ccpm
Password: CcpmDb2025Secure
```

### Quick Connect via psql

```bash
# Interactive session
PGPASSWORD=CcpmDb2025Secure psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db

# Quick query
PGPASSWORD=CcpmDb2025Secure psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c "SELECT COUNT(*) FROM tasks;"

# Show table structure
PGPASSWORD=CcpmDb2025Secure psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c "\d tasks"

# List all tables
PGPASSWORD=CcpmDb2025Secure psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c "\dt"

# Check migration version
PGPASSWORD=CcpmDb2025Secure psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db -c "SELECT * FROM alembic_version;"
```

### Key Tables

| Table | Purpose |
|-------|---------|
| `projects` | Project definitions (HomeLab, Home Assistant, etc.) |
| `sprints` | Sprint planning and tracking |
| `tasks` | Individual work items |
| `agents` | Agent registry |
| `session_reports` | EOD session summaries |

### Common Queries

```sql
-- List all projects
SELECT name, slug, status FROM projects;

-- HomeLab project ID
SELECT id, name FROM projects WHERE slug = 'homelab';
-- Result: 23c4bc1f-e8c4-4ce6-b3f7-218524c04764

-- List HomeLab tasks
SELECT t.title, t.status, t.priority, s.name as sprint
FROM tasks t
LEFT JOIN sprints s ON t.sprint_id = s.id
WHERE t.project_id = '23c4bc1f-e8c4-4ce6-b3f7-218524c04764'
ORDER BY t.created_at DESC;

-- List all sprints
SELECT name, status, start_date, end_date FROM sprints ORDER BY start_date DESC;

-- Tasks by status
SELECT status, COUNT(*) FROM tasks GROUP BY status;

-- Recent session reports
SELECT agent_tag, session_date, status, summary
FROM session_reports
ORDER BY session_date DESC LIMIT 5;
```

### Project IDs

| Project | UUID |
|---------|------|
| HomeLab | `23c4bc1f-e8c4-4ce6-b3f7-218524c04764` |
| Home Assistant | `15a25f74-b74a-41cd-8250-0abd61e304ca` |
| CCPM V2 | `bc5b6879-8475-45b1-b067-ad40427961e8` |

---

## HomeLab Database (homelab_db)

### Connection Details

```bash
# Full connection string
postgresql://ccpm:CcpmDb2025Secure@10.0.1.251:5433/homelab_db

# Connection components
Host:     10.0.1.251 (Synology NAS)
Port:     5433
Database: homelab_db
User:     ccpm
Password: CcpmDb2025Secure
```

### Quick Connect via psql

```bash
# Interactive session
PGPASSWORD=CcpmDb2025Secure psql -h 10.0.1.251 -p 5433 -U ccpm -d homelab_db

# List schemas
PGPASSWORD=CcpmDb2025Secure psql -h 10.0.1.251 -p 5433 -U ccpm -d homelab_db -c "\dn"

# List tables in infrastructure schema
PGPASSWORD=CcpmDb2025Secure psql -h 10.0.1.251 -p 5433 -U ccpm -d homelab_db -c "\dt infrastructure.*"
```

### Schemas

| Schema | Purpose |
|--------|---------|
| `infrastructure` | Devices, services |
| `credentials` | System credentials, SSH keys |
| `network` | Network assignments, VLANs |
| `virtualization` | Proxmox VMs |
| `scpi` | Test equipment |
| `ai_ml` | Ollama models, GPU tracking |
| `audit` | System events log |

### Common Queries

```sql
-- List all devices
SELECT device_name, primary_ip, status FROM infrastructure.devices;

-- Get device metadata
SELECT device_name, metadata FROM infrastructure.devices WHERE device_name = 'HA-Pi5';

-- List credentials
SELECT system_name, system_type, port FROM credentials.system_credentials;

-- List services
SELECT service_name, status FROM infrastructure.services;
```

---

## Python Connection (Alternative)

```bash
# From CCPM server
cd /home/ccpm/ccpm-v2/src/backend
poetry run python -c "import psycopg2; conn = psycopg2.connect(host='10.0.1.251', port=5433, user='ccpm', password='CcpmDb2025Secure', database='ccpm_db'); print('Connected!'); conn.close()"
```

```python
# Python snippet
import psycopg2

conn = psycopg2.connect(
    host='10.0.1.251',
    port=5433,
    user='ccpm',
    password='CcpmDb2025Secure',
    database='ccpm_db'  # or 'homelab_db'
)
cursor = conn.cursor()
cursor.execute("SELECT name, status FROM projects;")
for row in cursor.fetchall():
    print(row)
conn.close()
```

---

## Environment Variables

For scripts, set these environment variables:

```bash
export PGHOST=10.0.1.251
export PGPORT=5433
export PGUSER=ccpm
export PGPASSWORD=CcpmDb2025Secure
export PGDATABASE=ccpm_db  # or homelab_db

# Then connect without parameters
psql
```

---

## Useful psql Commands

| Command | Description |
|---------|-------------|
| `\dt` | List tables |
| `\d tablename` | Describe table |
| `\dn` | List schemas |
| `\l` | List databases |
| `\du` | List users |
| `\x` | Toggle expanded output |
| `\timing` | Toggle query timing |
| `\q` | Quit |

---

*Generated for HomeLab Agent - 2026-01-08*
