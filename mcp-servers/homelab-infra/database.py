"""
HomeLab Infrastructure Database Access Layer.
Provides secure access to devices, credentials, services, and network config.
Uses PostgreSQL database (homelab_db) on NAS.
"""

import os
import logging
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class HomelabDB:
    """Database access layer for HomeLab infrastructure."""

    def __init__(self, db_config: dict = None):
        """
        Initialize database connection settings.

        Args:
            db_config: Optional dict with host, port, database, user, password.
                      Defaults to environment variables or hardcoded values.
        """
        self.db_config = db_config or {
            "host": os.environ.get("HOMELAB_DB_HOST", "10.0.1.251"),
            "port": int(os.environ.get("HOMELAB_DB_PORT", 5433)),
            "database": os.environ.get("HOMELAB_DB_NAME", "homelab_db"),
            "user": os.environ.get("HOMELAB_DB_USER", "ccpm"),
            "password": os.environ.get("HOMELAB_DB_PASSWORD", "CcpmDb2025Secure"),
        }
        self._encryption = None

    @property
    def encryption(self):
        """Lazy-load encryption to ensure key is available."""
        if self._encryption is None:
            try:
                from infrastructure.db.encryption import CredentialEncryption
                self._encryption = CredentialEncryption()
            except ImportError:
                logger.warning("Encryption module not available")
                self._encryption = None
        return self._encryption

    @contextmanager
    def get_connection(self):
        """Get PostgreSQL database connection."""
        conn = psycopg2.connect(**self.db_config)
        try:
            yield conn
        finally:
            conn.close()

    def _log_audit(self, conn, action: str, target_type: str,
                   target_id: str, user: str = "mcp-agent",
                   details: str = None, success: bool = True):
        """Log an audit entry for security-sensitive actions."""
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO audit.system_events
                    (event_type, severity, source, message, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    action,
                    'INFO' if success else 'WARNING',
                    'homelab-db',
                    f"{action} on {target_type}:{target_id}",
                    {"user": user, "details": details or f"success={success}",
                     "target_type": target_type, "target_id": str(target_id)}
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to log audit: {e}")

    # ==================== Device Methods ====================

    def list_devices(self, category: str = None, status: str = None) -> list[dict]:
        """List all devices with optional filters."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT device_id, device_name, device_type, category, model,
                           manufacturer, primary_ip, status, location, notes, metadata
                    FROM infrastructure.devices
                    WHERE 1=1
                """
                params = []

                if category:
                    query += " AND category = %s"
                    params.append(category)
                if status:
                    query += " AND status = %s"
                    params.append(status)

                query += " ORDER BY category, device_name"
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]

    def get_device(self, name: str = None, ip: str = None) -> Optional[dict]:
        """Get device by name or IP address."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if name:
                    cur.execute("""
                        SELECT * FROM infrastructure.devices WHERE device_name = %s
                    """, (name,))
                elif ip:
                    cur.execute("""
                        SELECT * FROM infrastructure.devices WHERE primary_ip = %s
                    """, (ip,))
                else:
                    return None

                row = cur.fetchone()
                return dict(row) if row else None

    # ==================== Credential Methods ====================

    def get_credentials(self, target: str, user: str = "mcp-agent") -> Optional[dict]:
        """
        Get credentials for a target. SECURITY CRITICAL - all access is logged.

        Target format: "device:<name>" or "service:<name>"
        """
        parts = target.split(":", 1)
        if len(parts) != 2:
            return {"error": "Invalid target format. Use 'device:<name>' or 'service:<name>'"}

        target_type, target_name = parts

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if target_type == "device":
                    cur.execute("""
                        SELECT c.*, d.device_name, d.primary_ip
                        FROM credentials.system_credentials c
                        JOIN infrastructure.devices d ON c.device_id = d.device_id
                        WHERE d.device_name = %s
                    """, (target_name,))
                elif target_type == "service":
                    cur.execute("""
                        SELECT c.*, s.service_name, d.primary_ip
                        FROM credentials.system_credentials c
                        JOIN infrastructure.services s ON c.service_id = s.service_id
                        JOIN infrastructure.devices d ON s.device_id = d.device_id
                        WHERE s.service_name = %s
                    """, (target_name,))
                else:
                    self._log_audit(conn, "credential_access", target_type, target_name,
                                   user, f"invalid_type={target_type}", success=False)
                    return {"error": f"Unknown target type: {target_type}"}

                row = cur.fetchone()
                if not row:
                    self._log_audit(conn, "credential_access", target_type, target_name,
                                   user, "not_found", success=False)
                    return {"error": f"No credentials found for {target}"}

                result = dict(row)

                # Decrypt sensitive fields
                if result.get("password_encrypted") and self.encryption:
                    try:
                        result["password"] = self.encryption.decrypt(result["password_encrypted"])
                    except Exception:
                        result["password"] = None
                    del result["password_encrypted"]

                # Log successful access
                self._log_audit(conn, "credential_access", target_type,
                               target_name, user, "success", success=True)

                return {
                    "target": target,
                    "name": result.get("device_name") or result.get("service_name"),
                    "ip": str(result.get("primary_ip")) if result.get("primary_ip") else None,
                    "username": result.get("username"),
                    "password": result.get("password"),
                    "ssh_key": result.get("ssh_key_path"),
                    "auth_type": result.get("auth_type"),
                }

    # ==================== Service Methods ====================

    def list_services(self, device_name: str = None) -> list[dict]:
        """List services, optionally filtered by device."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT s.*, d.device_name, d.primary_ip as device_ip
                    FROM infrastructure.services s
                    LEFT JOIN infrastructure.devices d ON s.device_id = d.device_id
                    WHERE 1=1
                """
                params = []

                if device_name:
                    query += " AND d.device_name = %s"
                    params.append(device_name)

                query += " ORDER BY s.service_name"
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]

    def get_service(self, name: str) -> Optional[dict]:
        """Get service by name."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT s.*, d.device_name, d.primary_ip as device_ip
                    FROM infrastructure.services s
                    LEFT JOIN infrastructure.devices d ON s.device_id = d.device_id
                    WHERE s.service_name = %s
                """, (name,))

                row = cur.fetchone()
                return dict(row) if row else None

    # ==================== SCPI Equipment Methods ====================

    def list_scpi_equipment(self, instrument_type: str = None) -> list[dict]:
        """List all SCPI equipment with optional type filter."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT d.device_name, d.model, d.manufacturer, d.primary_ip, d.status,
                           e.scpi_address, e.instrument_type, e.measurement_capabilities,
                           e.max_voltage, e.max_current, e.max_power, e.channels
                    FROM scpi.equipment e
                    JOIN infrastructure.devices d ON e.equipment_id = d.device_id
                    WHERE 1=1
                """
                params = []

                if instrument_type:
                    query += " AND e.instrument_type = %s"
                    params.append(instrument_type)

                query += " ORDER BY d.device_name"
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]

    # ==================== Network Methods ====================

    def lookup_ip(self, ip: str) -> Optional[dict]:
        """Look up what's allocated to an IP address."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT device_id, device_name, device_type, category, status
                    FROM infrastructure.devices
                    WHERE primary_ip = %s
                """, (ip,))

                row = cur.fetchone()
                if row:
                    device = dict(row)
                    return {
                        "ip_address": ip,
                        "allocated_to": device["device_name"],
                        "device_type": device["device_type"],
                        "category": device["category"],
                        "status": device["status"]
                    }

                return {"ip_address": ip, "allocated_to": None, "status": "unallocated"}

    def list_networks(self) -> list[dict]:
        """List all networks/VLANs."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT network_id, network_name, vlan_id, subnet, gateway,
                           purpose, security_zone, notes
                    FROM network.networks
                    ORDER BY COALESCE(vlan_id, 0), network_name
                """)
                return [dict(row) for row in cur.fetchall()]
