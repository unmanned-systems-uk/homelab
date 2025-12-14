"""
HomeLab Infrastructure Database Access Layer.
Provides secure access to VMs, credentials, services, and network config.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

# Import encryption from infrastructure module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "infrastructure"))
from db.encryption import CredentialEncryption


class HomelabDB:
    """Database access layer for HomeLab infrastructure."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.environ.get(
            "HOMELAB_DB_PATH",
            str(Path(__file__).parent.parent.parent / "infrastructure" / "homelab.db")
        )
        self._encryption = None

    @property
    def encryption(self) -> CredentialEncryption:
        """Lazy-load encryption to ensure key is available."""
        if self._encryption is None:
            self._encryption = CredentialEncryption()
        return self._encryption

    @contextmanager
    def get_connection(self):
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _log_audit(self, conn: sqlite3.Connection, action: str,
                   target_type: str, target_id: int, user: str = "mcp-agent",
                   details: str = None, success: bool = True):
        """Log an audit entry for security-sensitive actions."""
        conn.execute("""
            INSERT INTO audit_log (action, target_type, target_id, user, details, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            action,
            target_type,
            target_id,
            user,
            details or f"success={success}",
            "local"
        ))
        conn.commit()

    # ==================== VM Methods ====================

    def list_vms(self, host_id: int = None, status: str = None) -> list[dict]:
        """List all virtual machines with optional filters."""
        with self.get_connection() as conn:
            query = """
                SELECT vm.*, h.node_name as host_name, h.ip_address as host_ip
                FROM virtual_machines vm
                LEFT JOIN proxmox_hosts h ON vm.host_id = h.id
                WHERE 1=1
            """
            params = []

            if host_id:
                query += " AND vm.host_id = ?"
                params.append(host_id)
            if status:
                query += " AND vm.status = ?"
                params.append(status)

            query += " ORDER BY vm.host_id, vm.vm_id"

            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_vm(self, vm_id: int = None, name: str = None) -> Optional[dict]:
        """Get VM by Proxmox VM ID or name."""
        with self.get_connection() as conn:
            if vm_id is not None:
                row = conn.execute("""
                    SELECT vm.*, h.node_name as host_name, h.ip_address as host_ip
                    FROM virtual_machines vm
                    LEFT JOIN proxmox_hosts h ON vm.host_id = h.id
                    WHERE vm.vm_id = ?
                """, (vm_id,)).fetchone()
            elif name:
                row = conn.execute("""
                    SELECT vm.*, h.node_name as host_name, h.ip_address as host_ip
                    FROM virtual_machines vm
                    LEFT JOIN proxmox_hosts h ON vm.host_id = h.id
                    WHERE vm.name = ?
                """, (name,)).fetchone()
            else:
                return None

            return dict(row) if row else None

    # ==================== Credential Methods ====================

    def get_credentials(self, target: str, user: str = "mcp-agent") -> Optional[dict]:
        """
        Get credentials for a target. SECURITY CRITICAL - all access is logged.

        Target format: "vm:100", "host:1", "service:name"
        """
        parts = target.split(":", 1)
        if len(parts) != 2:
            return {"error": "Invalid target format. Use 'type:id' (e.g., vm:100)"}

        target_type, target_id = parts

        with self.get_connection() as conn:
            # Find the credential
            if target_type == "vm":
                row = conn.execute("""
                    SELECT c.*, vm.ip_address, vm.name
                    FROM credentials c
                    JOIN virtual_machines vm ON c.target_id = vm.id
                    WHERE c.target_type = 'vm' AND vm.vm_id = ?
                """, (int(target_id),)).fetchone()
            elif target_type == "host":
                row = conn.execute("""
                    SELECT c.*, h.ip_address, h.node_name as name
                    FROM credentials c
                    JOIN proxmox_hosts h ON c.target_id = h.id
                    WHERE c.target_type = 'host' AND h.id = ?
                """, (int(target_id),)).fetchone()
            elif target_type == "service":
                row = conn.execute("""
                    SELECT c.*, s.url, s.service_name as name
                    FROM credentials c
                    JOIN services s ON c.target_id = s.id
                    WHERE c.target_type = 'service' AND s.service_name = ?
                """, (target_id,)).fetchone()
            else:
                self._log_audit(conn, "credential_access", target_type, 0, user,
                              f"invalid_type={target_type}", success=False)
                return {"error": f"Unknown target type: {target_type}"}

            if not row:
                self._log_audit(conn, "credential_access", target_type,
                              int(target_id) if target_id.isdigit() else 0, user,
                              "not_found", success=False)
                return {"error": f"No credentials found for {target}"}

            result = dict(row)

            # Decrypt sensitive fields
            if result.get("password_encrypted"):
                try:
                    result["password"] = self.encryption.decrypt(result["password_encrypted"])
                except Exception:
                    result["password"] = None
                del result["password_encrypted"]

            if result.get("api_token_encrypted"):
                try:
                    result["api_token"] = self.encryption.decrypt(result["api_token_encrypted"])
                except Exception:
                    result["api_token"] = None
                del result["api_token_encrypted"]

            # Log successful access
            self._log_audit(conn, "credential_access", target_type,
                          result.get("target_id", 0), user, "success", success=True)

            return {
                "target": target,
                "name": result.get("name"),
                "ip": result.get("ip_address"),
                "username": result.get("username"),
                "password": result.get("password"),
                "ssh_key": result.get("ssh_key_path"),
                "auth_type": result.get("auth_type"),
                "is_root": result.get("is_root", False)
            }

    # ==================== Service Methods ====================

    def list_services(self, vm_id: int = None) -> list[dict]:
        """List services, optionally filtered by VM."""
        with self.get_connection() as conn:
            query = """
                SELECT s.*, vm.name as vm_name, vm.ip_address as vm_ip
                FROM services s
                LEFT JOIN virtual_machines vm ON s.vm_id = vm.id
                WHERE 1=1
            """
            params = []

            if vm_id:
                query += " AND vm.vm_id = ?"
                params.append(vm_id)

            query += " ORDER BY s.service_name"

            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_service(self, service_id: int = None, name: str = None) -> Optional[dict]:
        """Get service by ID or name."""
        with self.get_connection() as conn:
            if service_id:
                row = conn.execute("""
                    SELECT s.*, vm.name as vm_name, vm.ip_address as vm_ip
                    FROM services s
                    LEFT JOIN virtual_machines vm ON s.vm_id = vm.id
                    WHERE s.id = ?
                """, (service_id,)).fetchone()
            elif name:
                row = conn.execute("""
                    SELECT s.*, vm.name as vm_name, vm.ip_address as vm_ip
                    FROM services s
                    LEFT JOIN virtual_machines vm ON s.vm_id = vm.id
                    WHERE s.service_name = ?
                """, (name,)).fetchone()
            else:
                return None

            return dict(row) if row else None

    def get_service_url(self, service_name: str) -> Optional[str]:
        """Get the full URL for a service."""
        service = self.get_service(name=service_name)
        if not service:
            return None

        if service.get("url"):
            return service["url"]

        # Build URL from components
        protocol = service.get("protocol", "http")
        ip = service.get("vm_ip")
        port = service.get("port")

        if ip and port:
            return f"{protocol}://{ip}:{port}"

        return None

    # ==================== Host Methods ====================

    def list_hosts(self) -> list[dict]:
        """List all Proxmox hosts."""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM proxmox_hosts ORDER BY node_name
            """).fetchall()
            return [dict(row) for row in rows]

    def get_host(self, host_id: int = None, name: str = None) -> Optional[dict]:
        """Get Proxmox host by ID or name."""
        with self.get_connection() as conn:
            if host_id:
                row = conn.execute(
                    "SELECT * FROM proxmox_hosts WHERE id = ?", (host_id,)
                ).fetchone()
            elif name:
                row = conn.execute(
                    "SELECT * FROM proxmox_hosts WHERE node_name = ?", (name,)
                ).fetchone()
            else:
                return None

            return dict(row) if row else None

    # ==================== Network Methods ====================

    def lookup_ip(self, ip: str) -> Optional[dict]:
        """Look up what's allocated to an IP address."""
        with self.get_connection() as conn:
            # Check network_config table
            row = conn.execute("""
                SELECT * FROM network_config WHERE ip_address = ?
            """, (ip,)).fetchone()

            if row:
                result = dict(row)
                result["source"] = "network_config"
                return result

            # Check VMs
            vm = conn.execute("""
                SELECT vm.*, h.node_name as host_name
                FROM virtual_machines vm
                LEFT JOIN proxmox_hosts h ON vm.host_id = h.id
                WHERE vm.ip_address = ?
            """, (ip,)).fetchone()

            if vm:
                return {
                    "ip_address": ip,
                    "allocated_to": f"vm:{dict(vm)['vm_id']} ({dict(vm)['name']})",
                    "hostname": dict(vm)["name"],
                    "source": "virtual_machines"
                }

            # Check hosts
            host = conn.execute("""
                SELECT * FROM proxmox_hosts WHERE ip_address = ?
            """, (ip,)).fetchone()

            if host:
                return {
                    "ip_address": ip,
                    "allocated_to": f"host:{dict(host)['id']} ({dict(host)['node_name']})",
                    "hostname": dict(host)["node_name"],
                    "source": "proxmox_hosts"
                }

            return {"ip_address": ip, "allocated_to": None, "status": "unallocated"}

    def list_ips(self, available_only: bool = False) -> list[dict]:
        """List IP allocations from network_config."""
        with self.get_connection() as conn:
            if available_only:
                rows = conn.execute("""
                    SELECT * FROM network_config
                    WHERE allocated_to IS NULL AND reserved = 0
                    ORDER BY ip_address
                """).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM network_config ORDER BY ip_address
                """).fetchall()

            return [dict(row) for row in rows]
