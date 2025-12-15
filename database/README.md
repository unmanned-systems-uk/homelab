# HomeLab Database System

**Location:** `/home/anthony/ccpm-workspace/HomeLab/database/`

This directory contains TWO separate SQLite databases for HomeLab management:

1. **homelab.db** - Infrastructure management (VMs, network, services)
2. **homelab_inventory.db** - Equipment inventory with automation support

---

## Database 1: homelab.db (Infrastructure Management)

**Purpose:** VM/infrastructure management for Proxmox environment

**Tables:**
- audit_log, credentials, proxmox_hosts, virtual_machines
- backups, network_config, services

**Records:** 21 total (as of 2025-12-15)

---

## Database 2: homelab_inventory.db (Equipment Inventory)

**Purpose:** Equipment cataloging, calibration tracking, network topology

This database system replaces the markdown-based inventory with a queryable SQLite database that supports:

- Equipment cataloging (compute, networking, storage, test equipment, SDR, etc.)
- SCPI-enabled test equipment tracking
- Network topology management
- Calibration tracking for test equipment
- Equipment relationships and dependencies
- Project assignments
- Auto-generation of markdown documentation

## Database Schema

The database includes the following tables:

- **equipment** - Main equipment catalog
- **click_boards** - MikroE Click boards (high-volume items)
- **equipment_relations** - Parent/child relationships between equipment
- **equipment_history** - Change tracking, calibrations, repairs
- **projects** - Project definitions
- **equipment_projects** - Equipment-to-project assignments
- **network_connections** - Network topology
- **calibration_schedule** - Calibration tracking
- **metadata** - Database versioning and configuration

### Views

Pre-built views for common queries:
- `view_scpi_equipment` - SCPI-enabled test equipment
- `view_calibration_due` - Equipment needing calibration soon
- `view_network_inventory` - All networked equipment
- `view_equipment_tree` - Equipment relationships

## Quick Start

### 1. Import Existing Inventory

Import data from the markdown inventory:

```bash
cd /home/anthony/ccpm-workspace/HomeLab/database
python3 import_inventory.py
```

This will:
- Create `homelab_inventory.db`
- Initialize the schema
- Import all equipment from `docs/hardware-inventory.md`
- Display import summary

### 2. Query the Database

Use the query tool for common operations:

```bash
# List all equipment
python3 query_inventory.py list

# List by category
python3 query_inventory.py list --category test_equipment

# Search for equipment
python3 query_inventory.py search rigol

# Show details for specific equipment
python3 query_inventory.py show 5

# List SCPI-enabled equipment
python3 query_inventory.py scpi

# List networked equipment
python3 query_inventory.py network

# Check calibration status
python3 query_inventory.py calibration

# Show database statistics
python3 query_inventory.py stats

# Output as JSON
python3 query_inventory.py list --format json
```

### 3. Export to Markdown

Generate markdown documentation from the database:

```bash
python3 export_markdown.py
```

This creates `docs/hardware-inventory-auto.md` from the database.

## Files

- `schema.sql` - Database schema definition
- `import_inventory.py` - Import from markdown to database
- `query_inventory.py` - CLI query tool
- `export_markdown.py` - Export database to markdown
- `homelab_inventory.db` - SQLite database (created by import)
- `README.md` - This file

## Dependencies

Python packages required:

```bash
pip install tabulate
```

## Use Cases

### SCPI Automation

Query SCPI-enabled equipment for automated testing:

```bash
# Get all SCPI equipment with IP addresses
python3 query_inventory.py scpi --format json

# Use in automation scripts
python3 -c "
import sqlite3
conn = sqlite3.connect('homelab_inventory.db')
cursor = conn.cursor()
cursor.execute('SELECT name, ip_address, scpi_port FROM view_scpi_equipment')
for name, ip, port in cursor.fetchall():
    print(f'{name}: {ip}:{port}')
"
```

### Network Management

Track all networked devices:

```bash
python3 query_inventory.py network
```

### Calibration Tracking

Monitor calibration due dates:

```bash
python3 query_inventory.py calibration
```

## Advanced Usage

### Direct SQL Queries

```bash
sqlite3 homelab_inventory.db

# Example queries
.mode column
.headers on

-- All Rigol equipment
SELECT name, model, ip_address FROM equipment WHERE manufacturer = 'Rigol';

-- Equipment needing calibration
SELECT * FROM view_calibration_due;

-- Network topology
SELECT * FROM view_network_inventory ORDER BY ip_address;
```

### Adding Equipment Manually

```sql
INSERT INTO equipment (name, category, subcategory, manufacturer, model, ip_address)
VALUES ('New-DMM', 'test_equipment', 'multimeter', 'Keysight', '34461A', '10.0.1.150');
```

### Adding Relationships

```sql
-- GPU belongs to workstation
INSERT INTO equipment_relations (parent_id, child_id, relation_type)
SELECT
    (SELECT id FROM equipment WHERE name = 'DEV-PC-Ubuntu'),
    (SELECT id FROM equipment WHERE name = 'RTX-A2000'),
    'contains';
```

### Tracking Calibration

```sql
-- Record a calibration event
INSERT INTO equipment_history (equipment_id, event_type, event_date, description, performed_by)
VALUES (
    (SELECT id FROM equipment WHERE name = 'DMM-Keithley'),
    'calibration',
    date('now'),
    'Annual calibration performed',
    'Cal Lab Inc.'
);

-- Update next calibration date
UPDATE equipment
SET calibration_due = date('now', '+1 year')
WHERE name = 'DMM-Keithley';
```

## Integration Points

### CCPM Integration

Link equipment to CCPM projects:

```sql
-- Create CCPM project link
INSERT INTO projects (name, ccpm_project_id, github_repo)
VALUES ('DPM-V2', 3, 'unmanned-systems-uk/payload-manager');

-- Assign equipment to project
INSERT INTO equipment_projects (equipment_id, project_id, role)
VALUES (
    (SELECT id FROM equipment WHERE name = 'DPM-Air'),
    (SELECT id FROM projects WHERE name = 'DPM-V2'),
    'Air-side computer'
);
```

### MCP Server (Future)

The database is structured for future MCP server integration:
- REST API endpoints for equipment queries
- SCPI equipment auto-discovery
- Network topology visualization
- Calibration alerts

## Maintenance

### Backup Database

```bash
cp homelab_inventory.db homelab_inventory.db.backup-$(date +%Y%m%d)
```

### Update from Markdown

If you update the markdown file manually:

```bash
# Re-import (will prompt for confirmation)
python3 import_inventory.py
```

### Re-generate Markdown

After making database changes:

```bash
python3 export_markdown.py
mv docs/hardware-inventory-auto.md docs/hardware-inventory.md
```

## Schema Version

Current schema version: 1.0

Check version:
```bash
sqlite3 homelab_inventory.db "SELECT value FROM metadata WHERE key = 'schema_version';"
```

## License

Part of the HomeLab project - see repository root for license.
