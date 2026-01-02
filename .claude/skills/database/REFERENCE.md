# HomeLab Database Reference

## CRITICAL: Two Databases

**ALWAYS check which database you need:**

| Database | Purpose | When to Use |
|----------|---------|-------------|
| `homelab_db` | **Infrastructure** | Devices, credentials, equipment, VMs, network config |
| `ccpm_db` | **Session Reports** | EOD reports, session_commits, agent tracking |

---

## Connection Details

Both databases share the same connection parameters:

| Parameter | Value |
|-----------|-------|
| **Host** | 10.0.1.251 |
| **Port** | 5433 |
| **User** | ccpm |
| **Password** | CcpmDb2025Secure |

### Quick Connect Commands

```bash
# Infrastructure data - USE THIS FOR DEVICES/CREDENTIALS
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d homelab_db

# Session reports - USE THIS FOR EOD/SESSION TRACKING
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d ccpm_db
```

---

## homelab_db Schemas

| Schema | Tables | Purpose |
|--------|--------|---------|
| `infrastructure` | devices, services | Hardware inventory |
| `credentials` | system_credentials, encryption_keys, credential_access_log | Secrets management |
| `network` | networks, device_network_assignments | VLAN config |
| `virtualization` | proxmox_vms | VM tracking |
| `scpi` | equipment | Test instruments |
| `ai_ml` | ollama_models | AI/ML resources |
| `audit` | system_events | Event logging |
| `testing` | test_results | Test tracking |

---

## Common Queries (homelab_db)

### List All Devices

```sql
SELECT device_name, primary_ip, device_type, status
FROM infrastructure.devices
ORDER BY device_name;
```

### Get Device Details

```sql
SELECT device_name, primary_ip, metadata, notes
FROM infrastructure.devices
WHERE device_name = 'HA-Pi5';
```

### List Credentials

```sql
SELECT system_name, system_type, port, protocol, access_url
FROM credentials.system_credentials;
```

### Update Device Metadata

```sql
UPDATE infrastructure.devices
SET
    metadata = metadata || '{"new_key": "value"}'::jsonb,
    notes = 'Updated notes',
    updated_at = NOW()
WHERE device_name = 'DeviceName'
RETURNING device_name, metadata;
```

### Add New Credential

```sql
INSERT INTO credentials.system_credentials (
    system_name, system_type, device_id, username, password_encrypted,
    ssh_key, access_url, port, protocol, notes
) VALUES (
    'SystemName',
    'other',  -- nas, proxmox, vm, docker, unifi, scpi, database, service, other
    'device-uuid-here',
    'username',
    '\x00'::bytea,
    '/path/to/key',
    'ssh://hostname',
    22,
    'ssh',
    'Description'
);
```

---

## ccpm_db Tables (Session Reports)

### session_reports

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Report ID |
| agent_id | uuid | Agent UUID |
| agent_tag | varchar | `[HomeLab]` or `[HomeAssistant]` |
| session_date | date | Date of session |
| status | varchar | draft, processed |
| commits_made | int | Git commits |
| files_modified | int | Files changed |
| summary | text | Session summary |

### Agent IDs

| Agent | ID | Tag |
|-------|-------|-----|
| HomeLab | `aaaaaaaa-bbbb-cccc-dddd-222222222222` | `[HomeLab]` |
| HomeAssistant | `aaaaaaaa-bbbb-cccc-dddd-333333333333` | `[HomeAssistant]` |

### Session Report Queries

```sql
-- Check today's session
SELECT id, status, commits_made, files_modified
FROM session_reports
WHERE agent_tag = '[HomeLab]'
  AND session_date = CURRENT_DATE;

-- Insert new session
INSERT INTO session_reports (
    id, agent_id, agent_tag, trigger_type, session_date,
    session_started_at, status, summary,
    commits_made, files_modified, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    'aaaaaaaa-bbbb-cccc-dddd-222222222222',
    '[HomeLab]',
    'manual',
    CURRENT_DATE,
    NOW(),
    'draft',
    'Session summary here',
    0, 0, NOW(), NOW()
);
```

---

## Decision Tree

```
Need to query/update something?
│
├── Device info, IP, metadata? → homelab_db.infrastructure.devices
├── SSH keys, passwords, API tokens? → homelab_db.credentials.system_credentials
├── VLAN, network config? → homelab_db.network.*
├── VM info? → homelab_db.virtualization.proxmox_vms
├── SCPI equipment? → homelab_db.scpi.equipment
├── EOD session report? → ccpm_db.session_reports
└── Session commits? → ccpm_db.session_commits
```

---

## Troubleshooting

### "relation does not exist"

You're probably using the wrong database. Check:
- `homelab_db` has infrastructure schemas
- `ccpm_db` has session_reports table

### "column does not exist"

Check table structure:
```bash
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d homelab_db -c "\d infrastructure.devices"
```

---

*HomeLab Database Reference - Always check which database you need!*
