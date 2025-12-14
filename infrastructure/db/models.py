"""
HomeLab Infrastructure Database - SQLite Schema and Models
Manages VMs, containers, credentials, services, and network configuration.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from .encryption import CredentialEncryption


class HomelabDB:
    """Main database interface for HomeLab infrastructure."""

    DEFAULT_DB_PATH = Path.home() / 'ccpm-workspace' / 'HomeLab' / 'infrastructure' / 'homelab.db'

    SCHEMA = """
    -- Proxmox Hosts
    CREATE TABLE IF NOT EXISTS proxmox_hosts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_name TEXT NOT NULL UNIQUE,
        ip_address TEXT NOT NULL,
        api_url TEXT,
        hardware_ref TEXT,
        total_cpu INTEGER,
        total_ram_gb INTEGER,
        gpus TEXT,
        status TEXT DEFAULT 'online',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Virtual Machines and LXC Containers
    CREATE TABLE IF NOT EXISTS virtual_machines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vm_id INTEGER NOT NULL,
        host_id INTEGER REFERENCES proxmox_hosts(id),
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('vm', 'lxc')) NOT NULL,
        ip_address TEXT,
        mac_address TEXT,
        os TEXT,
        cpu_cores INTEGER,
        ram_gb INTEGER,
        disk_gb INTEGER,
        gpu_passthrough TEXT,
        purpose TEXT,
        status TEXT DEFAULT 'stopped',
        template BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(host_id, vm_id)
    );

    -- Encrypted Credentials
    CREATE TABLE IF NOT EXISTS credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type TEXT NOT NULL,
        target_id INTEGER,
        target_name TEXT,
        username TEXT NOT NULL,
        password_encrypted TEXT,
        ssh_key_path TEXT,
        api_token_encrypted TEXT,
        auth_type TEXT CHECK(auth_type IN ('password', 'key', 'both', 'token')),
        is_root BOOLEAN DEFAULT FALSE,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Services Running on VMs
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vm_id INTEGER REFERENCES virtual_machines(id),
        service_name TEXT NOT NULL,
        port INTEGER,
        protocol TEXT DEFAULT 'http',
        url TEXT,
        health_endpoint TEXT,
        docker_container TEXT,
        systemd_unit TEXT,
        status TEXT DEFAULT 'unknown',
        auto_start BOOLEAN DEFAULT TRUE,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Network Configuration and IP Allocation
    CREATE TABLE IF NOT EXISTS network_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL UNIQUE,
        subnet TEXT DEFAULT '10.0.1.0/24',
        gateway TEXT DEFAULT '10.0.1.1',
        dns TEXT DEFAULT '10.0.1.1',
        vlan_id INTEGER DEFAULT 0,
        hostname TEXT,
        allocated_to TEXT,
        reserved BOOLEAN DEFAULT FALSE,
        dhcp_reservation BOOLEAN DEFAULT FALSE,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Backup Schedules
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vm_id INTEGER REFERENCES virtual_machines(id),
        backup_type TEXT CHECK(backup_type IN ('full', 'snapshot', 'vzdump')),
        schedule TEXT,
        retention_days INTEGER DEFAULT 7,
        storage_location TEXT,
        last_backup DATETIME,
        last_status TEXT,
        next_backup DATETIME,
        enabled BOOLEAN DEFAULT TRUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Security Audit Log
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        target_type TEXT,
        target_id INTEGER,
        user TEXT,
        details TEXT,
        ip_address TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_vm_host ON virtual_machines(host_id);
    CREATE INDEX IF NOT EXISTS idx_vm_status ON virtual_machines(status);
    CREATE INDEX IF NOT EXISTS idx_cred_target ON credentials(target_type, target_id);
    CREATE INDEX IF NOT EXISTS idx_service_vm ON services(vm_id);
    CREATE INDEX IF NOT EXISTS idx_network_ip ON network_config(ip_address);
    CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
    """

    def __init__(self, db_path: Path = None):
        """Initialize database connection and create schema if needed."""
        self.db_path = db_path or self.DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.encryption = CredentialEncryption()

        self._create_schema()
        self._set_secure_permissions()

    def _create_schema(self):
        """Create all tables and indexes."""
        self.cursor.executescript(self.SCHEMA)
        self.conn.commit()

    def _set_secure_permissions(self):
        """Set secure file permissions on database (600)."""
        import os
        os.chmod(self.db_path, 0o600)

    def _audit_log(self, action: str, target_type: str = None, target_id: int = None,
                   details: Dict = None, user: str = 'system'):
        """Log security-critical actions."""
        self.cursor.execute(
            """INSERT INTO audit_log (action, target_type, target_id, user, details)
               VALUES (?, ?, ?, ?, ?)""",
            (action, target_type, target_id, user, json.dumps(details) if details else None)
        )
        self.conn.commit()

    # ==================== Proxmox Hosts ====================

    def add_host(self, node_name: str, ip_address: str, **kwargs) -> int:
        """Add a Proxmox host."""
        fields = ['node_name', 'ip_address']
        values = [node_name, ip_address]

        for key in ['api_url', 'hardware_ref', 'total_cpu', 'total_ram_gb', 'gpus', 'notes']:
            if key in kwargs:
                fields.append(key)
                values.append(json.dumps(kwargs[key]) if key == 'gpus' and isinstance(kwargs[key], list) else kwargs[key])

        query = f"INSERT INTO proxmox_hosts ({', '.join(fields)}) VALUES ({', '.join(['?'] * len(values))})"
        self.cursor.execute(query, values)
        self.conn.commit()

        host_id = self.cursor.lastrowid
        self._audit_log('host_created', 'host', host_id, {'node_name': node_name})
        return host_id

    def get_hosts(self) -> List[Dict]:
        """Get all Proxmox hosts."""
        self.cursor.execute("SELECT * FROM proxmox_hosts ORDER BY node_name")
        return [dict(row) for row in self.cursor.fetchall()]

    # ==================== Virtual Machines ====================

    def add_vm(self, vm_id: int, host_id: int, name: str, vm_type: str, **kwargs) -> int:
        """Add a virtual machine or LXC container."""
        fields = ['vm_id', 'host_id', 'name', 'type']
        values = [vm_id, host_id, name, vm_type]

        for key in ['ip_address', 'mac_address', 'os', 'cpu_cores', 'ram_gb', 'disk_gb',
                    'gpu_passthrough', 'purpose', 'status', 'template']:
            if key in kwargs:
                fields.append(key)
                values.append(kwargs[key])

        query = f"INSERT INTO virtual_machines ({', '.join(fields)}) VALUES ({', '.join(['?'] * len(values))})"
        self.cursor.execute(query, values)
        self.conn.commit()

        db_id = self.cursor.lastrowid
        self._audit_log('vm_created', 'vm', db_id, {'vm_id': vm_id, 'name': name})
        return db_id

    def get_vms(self, host_id: int = None, status: str = None) -> List[Dict]:
        """Get virtual machines with optional filters."""
        query = "SELECT * FROM virtual_machines WHERE 1=1"
        params = []

        if host_id:
            query += " AND host_id = ?"
            params.append(host_id)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY vm_id"
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def update_vm_status(self, vm_id: int, status: str):
        """Update VM status."""
        self.cursor.execute(
            "UPDATE virtual_machines SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE vm_id = ?",
            (status, vm_id)
        )
        self.conn.commit()
        self._audit_log('vm_status_updated', 'vm', vm_id, {'status': status})

    def get_vm_by_id(self, vm_id: int) -> Optional[Dict]:
        """Get a specific VM by its Proxmox VM ID."""
        self.cursor.execute("SELECT * FROM virtual_machines WHERE vm_id = ?", (vm_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    # ==================== Credentials ====================

    def add_credential(self, target_type: str, target_id: int, username: str,
                      password: str = None, ssh_key_path: str = None,
                      api_token: str = None, **kwargs) -> int:
        """Add encrypted credentials."""
        password_enc = self.encryption.encrypt(password) if password else None
        token_enc = self.encryption.encrypt(api_token) if api_token else None

        # Determine auth type
        auth_type = kwargs.get('auth_type')
        if not auth_type:
            if password and ssh_key_path:
                auth_type = 'both'
            elif ssh_key_path:
                auth_type = 'key'
            elif api_token:
                auth_type = 'token'
            else:
                auth_type = 'password'

        self.cursor.execute(
            """INSERT INTO credentials
               (target_type, target_id, target_name, username, password_encrypted,
                ssh_key_path, api_token_encrypted, auth_type, is_root, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (target_type, target_id, kwargs.get('target_name'), username, password_enc,
             ssh_key_path, token_enc, auth_type, kwargs.get('is_root', False), kwargs.get('notes'))
        )
        self.conn.commit()

        cred_id = self.cursor.lastrowid
        self._audit_log('credential_added', target_type, target_id,
                       {'username': username, 'auth_type': auth_type})
        return cred_id

    def get_credential(self, target_type: str, target_id: int, username: str = None) -> Optional[Dict]:
        """Get and decrypt credentials (logs access for security)."""
        query = "SELECT * FROM credentials WHERE target_type = ? AND target_id = ?"
        params = [target_type, target_id]

        if username:
            query += " AND username = ?"
            params.append(username)

        self.cursor.execute(query, params)
        row = self.cursor.fetchone()

        if not row:
            return None

        cred = dict(row)

        # Decrypt sensitive fields
        if cred['password_encrypted']:
            cred['password'] = self.encryption.decrypt(cred['password_encrypted'])
        if cred['api_token_encrypted']:
            cred['api_token'] = self.encryption.decrypt(cred['api_token_encrypted'])

        # Log access
        self._audit_log('credential_accessed', target_type, target_id,
                       {'username': cred['username'], 'auth_type': cred['auth_type']})

        # Remove encrypted versions from returned dict
        del cred['password_encrypted']
        del cred['api_token_encrypted']

        return cred

    def list_credentials(self) -> List[Dict]:
        """List all credentials (without decryption)."""
        self.cursor.execute("""
            SELECT id, target_type, target_id, target_name, username, auth_type, is_root, created_at
            FROM credentials ORDER BY target_type, target_id
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    # ==================== Services ====================

    def add_service(self, vm_id: int, service_name: str, **kwargs) -> int:
        """Add a service running on a VM."""
        fields = ['vm_id', 'service_name']
        values = [vm_id, service_name]

        for key in ['port', 'protocol', 'url', 'health_endpoint', 'docker_container',
                    'systemd_unit', 'status', 'auto_start', 'notes']:
            if key in kwargs:
                fields.append(key)
                values.append(kwargs[key])

        query = f"INSERT INTO services ({', '.join(fields)}) VALUES ({', '.join(['?'] * len(values))})"
        self.cursor.execute(query, values)
        self.conn.commit()

        service_id = self.cursor.lastrowid
        self._audit_log('service_added', 'service', service_id, {'name': service_name, 'vm_id': vm_id})
        return service_id

    def get_services(self, vm_id: int = None) -> List[Dict]:
        """Get services, optionally filtered by VM."""
        if vm_id:
            self.cursor.execute("SELECT * FROM services WHERE vm_id = ? ORDER BY service_name", (vm_id,))
        else:
            self.cursor.execute("SELECT * FROM services ORDER BY vm_id, service_name")
        return [dict(row) for row in self.cursor.fetchall()]

    def update_service_status(self, service_id: int, status: str):
        """Update service status."""
        self.cursor.execute(
            "UPDATE services SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, service_id)
        )
        self.conn.commit()

    # ==================== Network Configuration ====================

    def reserve_ip(self, ip_address: str, hostname: str = None, allocated_to: str = None, **kwargs) -> int:
        """Reserve an IP address."""
        fields = ['ip_address', 'reserved']
        values = [ip_address, True]

        if hostname:
            fields.append('hostname')
            values.append(hostname)
        if allocated_to:
            fields.append('allocated_to')
            values.append(allocated_to)

        for key in ['subnet', 'gateway', 'dns', 'vlan_id', 'dhcp_reservation', 'notes']:
            if key in kwargs:
                fields.append(key)
                values.append(kwargs[key])

        query = f"INSERT INTO network_config ({', '.join(fields)}) VALUES ({', '.join(['?'] * len(values))})"
        self.cursor.execute(query, values)
        self.conn.commit()

        return self.cursor.lastrowid

    def get_ips(self, available_only: bool = False) -> List[Dict]:
        """Get IP allocations."""
        query = "SELECT * FROM network_config"
        if available_only:
            query += " WHERE reserved = FALSE"
        query += " ORDER BY ip_address"

        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]

    # ==================== Backups ====================

    def add_backup_schedule(self, vm_id: int, backup_type: str, schedule: str, **kwargs) -> int:
        """Add a backup schedule for a VM."""
        fields = ['vm_id', 'backup_type', 'schedule']
        values = [vm_id, backup_type, schedule]

        for key in ['retention_days', 'storage_location', 'enabled']:
            if key in kwargs:
                fields.append(key)
                values.append(kwargs[key])

        query = f"INSERT INTO backups ({', '.join(fields)}) VALUES ({', '.join(['?'] * len(values))})"
        self.cursor.execute(query, values)
        self.conn.commit()

        return self.cursor.lastrowid

    def get_backups(self, vm_id: int = None) -> List[Dict]:
        """Get backup schedules."""
        if vm_id:
            self.cursor.execute("SELECT * FROM backups WHERE vm_id = ?", (vm_id,))
        else:
            self.cursor.execute("SELECT * FROM backups ORDER BY vm_id")
        return [dict(row) for row in self.cursor.fetchall()]

    # ==================== Audit Log ====================

    def get_audit_log(self, limit: int = 100, action: str = None) -> List[Dict]:
        """Retrieve audit log entries."""
        query = "SELECT * FROM audit_log"
        params = []

        if action:
            query += " WHERE action = ?"
            params.append(action)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def close(self):
        """Close database connection."""
        self.conn.close()
