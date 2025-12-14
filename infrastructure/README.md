# HomeLab Infrastructure Database

A secure SQLite database for managing Proxmox VMs, containers, encrypted credentials, services, and network configuration.

## Features

- **VM/Container Management** - Track Proxmox VMs and LXC containers
- **Encrypted Credentials** - Fernet-based encryption for passwords and API tokens
- **Service Tracking** - Monitor services running on each VM
- **Network Management** - IP allocation and DHCP reservation tracking
- **Backup Scheduling** - Manage backup schedules and retention
- **Security Audit Log** - Track all credential access and system changes

## Quick Start

### Installation

1. Virtual environment is already set up at `/home/anthony/ccpm-workspace/HomeLab/.venv`
2. Database location: `/home/anthony/ccpm-workspace/HomeLab/infrastructure/homelab.db`
3. Encryption key: `~/.homelab/.db_key` (auto-generated, chmod 600)

### Initialize Database

```bash
cd /home/anthony/ccpm-workspace/HomeLab/infrastructure
./homelab-db init
```

This creates:
- Proxmox host: `homelab-pve` (10.0.1.130)
- First VM: `whisper` (VMID 100, Voice Server)

### Basic Commands

```bash
# Show database info
./homelab-db info

# List all VMs
./homelab-db vm list

# Show detailed VM info
./homelab-db vm show 100

# List Proxmox hosts
./homelab-db host list
```

## Command Reference

### VM Management

```bash
# Add a new VM
./homelab-db vm add \
  --vmid 101 \
  --host-id 1 \
  --name "myvm" \
  --type vm \
  --ip 10.0.1.151 \
  --os "Ubuntu 24.04" \
  --cpu 4 \
  --ram 16 \
  --disk 100 \
  --purpose "Web Server"

# Update VM status
./homelab-db vm update 101 --status running

# Show VM details
./homelab-db vm show 101

# List VMs by status
./homelab-db vm list --status running

# List VMs on specific host
./homelab-db vm list --host 1
```

### Host Management

```bash
# Add a Proxmox host
./homelab-db host add \
  --name homelab-pve \
  --ip 10.0.1.130 \
  --api-url https://10.0.1.130:8006 \
  --hardware "Legacy-i7" \
  --cpu 16 \
  --ram 32 \
  --gpus "GTX 1080 Ti,Quadro P620"

# List all hosts
./homelab-db host list
```

### Credential Management

**SECURITY WARNING:** Credential retrieval is audited and logged.

```bash
# Add credentials (interactive password prompt)
./homelab-db cred add --target vm:100 --user anthony --password

# Add credentials with SSH key
./homelab-db cred add --target vm:100 --user anthony --ssh-key ~/.ssh/id_rsa

# Add API token
./homelab-db cred add --target host:1 --user root --api-token

# Get credentials (decrypted)
./homelab-db cred get vm:100 --user anthony

# List all credentials (no decryption)
./homelab-db cred list
```

### Service Management

```bash
# Add a service
./homelab-db service add \
  --vm 1 \
  --name whisper-tts \
  --port 8000 \
  --protocol http \
  --url http://10.0.1.150:8000 \
  --docker whisper-server

# List all services
./homelab-db service list

# List services on specific VM
./homelab-db service list --vm 1

# Update service status
./homelab-db service status 1 running
```

### Network Management

```bash
# Reserve an IP
./homelab-db ip reserve 10.0.1.150 \
  --hostname whisper \
  --allocated-to vm:100 \
  --dhcp

# List all IP allocations
./homelab-db ip list

# List available IPs
./homelab-db ip list --available
```

### Audit Log

```bash
# View recent audit log
./homelab-db audit log --limit 50

# Filter by action type
./homelab-db audit log --action credential_accessed
```

## Database Schema

### Tables

1. **proxmox_hosts** - Physical Proxmox nodes
2. **virtual_machines** - VMs and LXC containers
3. **credentials** - Encrypted credentials (Fernet)
4. **services** - Services running on VMs
5. **network_config** - IP allocations and DHCP
6. **backups** - Backup schedules
7. **audit_log** - Security audit trail

See [GitHub Issue #8](https://github.com/unmanned-systems-uk/homelab/issues/8) for complete schema.

## Security

### Encryption

- **Algorithm:** Fernet (symmetric encryption)
- **Key Location:** `~/.homelab/.db_key` (chmod 600)
- **Key Generation:** Automatic on first use
- **Environment Override:** Set `HOMELAB_DB_KEY` to use custom key

### Database Permissions

- Database file: `chmod 600` (owner read/write only)
- Encryption key: `chmod 600` (owner read/write only)
- Key directory: `chmod 700` (owner access only)

### Audit Logging

All security-critical actions are logged:
- `credential_added` - New credential stored
- `credential_accessed` - Credential decrypted (who, when, target)
- `vm_created` - VM added to database
- `host_created` - Host added
- `vm_status_updated` - VM status changed

View logs with: `./homelab-db audit log`

## Python API

Use the database programmatically:

```python
from db import HomelabDB

db = HomelabDB()

# Add a VM
vm_id = db.add_vm(
    vm_id=102,
    host_id=1,
    name='testvm',
    vm_type='vm',
    ip_address='10.0.1.152',
    cpu_cores=4,
    ram_gb=8,
    status='running'
)

# Add encrypted credentials
cred_id = db.add_credential(
    target_type='vm',
    target_id=102,
    username='admin',
    password='SuperSecret123!',
    target_name='vm:102'
)

# Retrieve (decrypted + audited)
cred = db.get_credential('vm', 102, 'admin')
print(cred['password'])  # Decrypted

# Add a service
service_id = db.add_service(
    vm_id=vm_id,
    service_name='nginx',
    port=80,
    protocol='http',
    systemd_unit='nginx.service'
)

# Reserve an IP
db.reserve_ip(
    ip_address='10.0.1.152',
    hostname='testvm',
    allocated_to='vm:102'
)

db.close()
```

## Current Infrastructure

As of initialization:

**Host:**
- `homelab-pve` (ID: 1)
  - IP: 10.0.1.130
  - CPUs: 16 cores
  - RAM: 32 GB
  - GPUs: GTX 1080 Ti, Quadro P620

**VMs:**
- `whisper` (VMID: 100)
  - Type: VM
  - OS: Ubuntu Server 24.04
  - CPUs: 6 cores
  - RAM: 24 GB
  - Disk: 100 GB
  - GPU: GTX 1080 Ti (passthrough)
  - Purpose: Voice Server - TTS API
  - Status: running

## Integration

### CCPM Integration

Link VMs to CCPM projects:

```sql
-- Future: Add project_id column to virtual_machines
ALTER TABLE virtual_machines ADD COLUMN project_id INTEGER;
```

### Proxmox API Sync

Future enhancement: Automatically sync VM status from Proxmox API.

```python
# Example sync script
from db import HomelabDB
import requests

db = HomelabDB()
# Fetch from Proxmox API and update VM status
```

## Troubleshooting

### Missing Encryption Key

If you see "Encryption: ⚠ Using environment key":

```bash
# Generate a new key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Save to environment
export HOMELAB_DB_KEY="<key>"

# Or let the system auto-generate on next use
```

### Database Locked

If you get "database is locked" errors:

```bash
# Close all connections
killall homelab-db

# Check for lock files
ls -la /home/anthony/ccpm-workspace/HomeLab/infrastructure/*.db*
```

### Permission Denied

Database should be owner-only:

```bash
chmod 600 /home/anthony/ccpm-workspace/HomeLab/infrastructure/homelab.db
chmod 600 ~/.homelab/.db_key
chmod 700 ~/.homelab
```

## Development

### Adding New Tables

Edit `db/models.py` and add table schema to `SCHEMA` constant:

```python
SCHEMA = """
    ...existing tables...

    CREATE TABLE IF NOT EXISTS my_new_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ...
    );
"""
```

### Adding CLI Commands

Edit `homelab-db` and add new Click command groups:

```python
@cli.group()
def mygroup():
    """My new command group"""
    pass

@mygroup.command('mycommand')
@click.pass_context
def my_command(ctx):
    """My command description"""
    db = ctx.obj['db']
    # ... implementation
```

## Files

```
infrastructure/
├── homelab.db              # SQLite database (chmod 600)
├── homelab-db              # CLI tool (executable)
├── db/
│   ├── __init__.py         # Package init
│   ├── models.py           # Database schema and ORM (chmod 600)
│   └── encryption.py       # Fernet encryption (chmod 600)
└── README.md               # This file

~/.homelab/
└── .db_key                 # Encryption key (chmod 600)
```

## License

Part of the HomeLab project - Internal use only.

## Support

- GitHub Issues: https://github.com/unmanned-systems-uk/homelab/issues
- Documentation: See issue #8 for schema details
- Security Issues: Report privately to project maintainer
