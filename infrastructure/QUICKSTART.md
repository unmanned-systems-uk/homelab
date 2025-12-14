# HomeLab Database - Quick Start Guide

## Installation (Already Done)

✓ Virtual environment: `/home/anthony/ccpm-workspace/HomeLab/.venv`
✓ Database: `/home/anthony/ccpm-workspace/HomeLab/infrastructure/homelab.db`
✓ Encryption key: `~/.homelab/.db_key`

## Common Commands

### View Current State

```bash
cd /home/anthony/ccpm-workspace/HomeLab/infrastructure

# Show overview
./homelab-db info

# List everything
./homelab-db host list
./homelab-db vm list
./homelab-db cred list
./homelab-db service list
./homelab-db ip list
```

### Add a New VM

```bash
./homelab-db vm add \
  --vmid 101 \
  --host-id 1 \
  --name "myvm" \
  --type vm \
  --ip 10.0.1.151 \
  --os "Ubuntu 24.04" \
  --cpu 4 \
  --ram 8 \
  --disk 50 \
  --purpose "Development Server" \
  --status running
```

### Add Credentials for a VM

**Interactive (secure):**

```bash
./homelab-db cred add --target vm:100 --user anthony --password
```

**Python (for scripts):**

```python
from db import HomelabDB

db = HomelabDB()
db.add_credential(
    target_type='vm',
    target_id=100,
    username='anthony',
    password='MyPassword123',
    ssh_key_path='~/.ssh/id_rsa'
)
db.close()
```

### Retrieve Credentials

⚠️ **WARNING:** This decrypts and logs access

```bash
./homelab-db cred get vm:100 --user anthony
```

### Add a Service

```bash
./homelab-db service add \
  --vm 1 \
  --name nginx \
  --port 80 \
  --protocol http \
  --systemd nginx.service
```

### Reserve an IP

```bash
./homelab-db ip reserve 10.0.1.151 \
  --hostname myvm \
  --allocated-to vm:101 \
  --dhcp
```

### View Audit Log

```bash
# Recent activity
./homelab-db audit log --limit 20

# Credential access only
./homelab-db audit log --action credential_accessed
```

## Security Reminders

1. **Credentials are encrypted** using Fernet (symmetric encryption)
2. **All credential access is logged** in the audit log
3. **Database is chmod 600** (owner read/write only)
4. **Encryption key is chmod 600** and stored in `~/.homelab/.db_key`

## Testing

Run the test suite:

```bash
cd /home/anthony/ccpm-workspace/HomeLab/infrastructure
./test_database.py
```

Should output:
```
✓ All tests passed successfully!
```

## Python API Example

```python
#!/home/anthony/ccpm-workspace/HomeLab/.venv/bin/python3
from db import HomelabDB

db = HomelabDB()

# Add VM
vm_id = db.add_vm(
    vm_id=102, host_id=1, name='testvm', vm_type='vm',
    ip_address='10.0.1.152', status='running'
)

# Add credentials
db.add_credential('vm', 102, 'root', password='Secret123!')

# Get credentials (decrypted + audited)
cred = db.get_credential('vm', 102, 'root')
print(f"Password: {cred['password']}")

# Add service
db.add_service(vm_id, 'nginx', port=80, status='running')

# Reserve IP
db.reserve_ip('10.0.1.152', hostname='testvm', allocated_to='vm:102')

# View audit log
for log in db.get_audit_log(limit=10):
    print(f"[{log['timestamp']}] {log['action']}")

db.close()
```

## Current Infrastructure

**Host:** homelab-pve (10.0.1.130)
- 16 CPU cores, 32 GB RAM
- GPUs: GTX 1080 Ti, Quadro P620

**VMs:**
- VM 100: whisper (running)
  - Ubuntu Server 24.04
  - 6 cores, 24 GB RAM, 100 GB disk
  - GPU: GTX 1080 Ti
  - Purpose: Voice Server - TTS API

## Troubleshooting

**Database locked?**
```bash
killall homelab-db
```

**Permission denied?**
```bash
chmod 600 ~/ccpm-workspace/HomeLab/infrastructure/homelab.db
chmod 600 ~/.homelab/.db_key
```

**Missing dependencies?**
```bash
cd /home/anthony/ccpm-workspace/HomeLab
.venv/bin/pip install -r requirements.txt
```

## Next Steps

1. Add more VMs as you create them in Proxmox
2. Store credentials for SSH/API access
3. Track services running on each VM
4. Reserve IPs in DHCP to match database
5. Set up backup schedules
6. Monitor audit log for security

## Full Documentation

See `README.md` for complete documentation.
