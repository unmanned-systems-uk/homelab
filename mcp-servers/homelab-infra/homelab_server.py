#!/usr/bin/env python3
"""
HomeLab Infrastructure MCP Server.
Provides tool access to devices, credentials, services, SCPI equipment, and network config.
Uses PostgreSQL database (homelab_db) on NAS.
"""

import os
import sys
import logging
import httpx
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("homelab-mcp")

# Initialize MCP server
# Note: SSE transport has known issues with stale sessions after restart
# See: https://github.com/modelcontextprotocol/python-sdk/issues/423
# Clients may need to reconnect after server restart
mcp = FastMCP("homelab-infra")

# PostgreSQL connection settings
DB_CONFIG = {
    "host": os.environ.get("HOMELAB_DB_HOST", "10.0.1.251"),
    "port": int(os.environ.get("HOMELAB_DB_PORT", 5433)),
    "database": os.environ.get("HOMELAB_DB_NAME", "homelab_db"),
    "user": os.environ.get("HOMELAB_DB_USER", "ccpm"),
    "password": os.environ.get("HOMELAB_DB_PASSWORD", "CcpmDb2025Secure"),
}

# Optional: Encryption key for credentials
DB_KEY = os.environ.get("HOMELAB_DB_KEY")


# ==================== Database Helpers ====================

@contextmanager
def get_db():
    """Get PostgreSQL database connection with dict cursor."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def log_audit(conn, action: str, target_type: str, target_id: str,
              user: str = "mcp-agent", details: str = None):
    """Log an audit entry for security-sensitive actions."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO audit.system_events (event_type, severity, source, message, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                action,
                'INFO',
                'homelab-mcp',
                f"{action} on {target_type}:{target_id}",
                {"user": user, "details": details or "success", "target_type": target_type, "target_id": str(target_id)}
            ))
            conn.commit()
    except Exception as e:
        logger.warning(f"Failed to log audit event: {e}")


def get_encryption():
    """Get encryption instance if key is available."""
    if not DB_KEY:
        return None
    try:
        sys.path.insert(0, "/app/infrastructure")
        from db.encryption import CredentialEncryption
        return CredentialEncryption(DB_KEY.encode() if isinstance(DB_KEY, str) else DB_KEY)
    except ImportError:
        logger.warning("Encryption module not available, credentials will be masked")
        return None


# ==================== Device Tools ====================

@mcp.tool()
def homelab_list_devices(category: str = None, status: str = None, device_type: str = None) -> list[dict]:
    """
    List all devices in the HomeLab infrastructure.

    Args:
        category: Filter by category (Compute, SCPI, Network, Storage, AI/ML)
        status: Filter by status (online, offline, unknown)
        device_type: Filter by type (server, sbc, router, nas, test-equipment, etc.)

    Returns:
        List of devices with their details
    """
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT device_id, device_name, device_type, category, model, manufacturer,
                       primary_ip, status, location, notes, metadata, created_at
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
            if device_type:
                query += " AND device_type = %s"
                params.append(device_type)

            query += " ORDER BY category, device_name"
            cur.execute(query, params)
            rows = cur.fetchall()

            return [dict(row) for row in rows]


@mcp.tool()
def homelab_get_device(name: str = None, ip: str = None) -> dict:
    """
    Get detailed information about a specific device.

    Args:
        name: Device name (e.g., "HA-Pi5", "DMM-Keithley")
        ip: Device IP address (e.g., "10.0.1.150")

    Returns:
        Device details including metadata, or error if not found
    """
    if name is None and ip is None:
        return {"error": "Must provide either name or ip"}

    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if name:
                cur.execute("""
                    SELECT * FROM infrastructure.devices WHERE device_name = %s
                """, (name,))
            else:
                cur.execute("""
                    SELECT * FROM infrastructure.devices WHERE primary_ip = %s
                """, (ip,))

            row = cur.fetchone()
            if row:
                return dict(row)
            return {"error": f"Device not found: {name or ip}"}


# ==================== SCPI Equipment Tools ====================

@mcp.tool()
def homelab_list_scpi_equipment(instrument_type: str = None) -> list[dict]:
    """
    List all SCPI-enabled test equipment.

    Args:
        instrument_type: Filter by type (DMM, Oscilloscope, AWG, Electronic Load, Power Supply)

    Returns:
        List of SCPI equipment with connection details and capabilities
    """
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT d.device_name, d.model, d.manufacturer, d.primary_ip, d.status,
                       e.scpi_address, e.scpi_protocol, e.instrument_type,
                       e.measurement_capabilities, e.max_voltage, e.max_current,
                       e.max_power, e.channels, e.metadata
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
            rows = cur.fetchall()

            return [dict(row) for row in rows]


@mcp.tool()
def homelab_get_scpi_connection(device_name: str) -> dict:
    """
    Get SCPI connection details for a test equipment device.

    Args:
        device_name: Name of the SCPI device (e.g., "DMM-Keithley", "Load-DC")

    Returns:
        Connection details including IP, port, protocol
    """
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT d.device_name, d.model, d.primary_ip, d.status,
                       e.scpi_address, e.scpi_protocol, e.instrument_type,
                       (d.metadata->>'scpi_port')::int as scpi_port
                FROM scpi.equipment e
                JOIN infrastructure.devices d ON e.equipment_id = d.device_id
                WHERE d.device_name = %s
            """, (device_name,))

            row = cur.fetchone()
            if row:
                result = dict(row)
                return {
                    "device": result["device_name"],
                    "model": result["model"],
                    "ip": str(result["primary_ip"]) if result["primary_ip"] else None,
                    "port": result["scpi_port"],
                    "protocol": result["scpi_protocol"],
                    "status": result["status"],
                    "type": result["instrument_type"],
                    "connection_string": result["scpi_address"]
                }
            return {"error": f"SCPI device not found: {device_name}"}


# ==================== Service Tools ====================

@mcp.tool()
def homelab_list_services(device_name: str = None, service_type: str = None) -> list[dict]:
    """
    List all services in the HomeLab.

    Args:
        device_name: Filter by hosting device name
        service_type: Filter by service type (automation, database, management, etc.)

    Returns:
        List of services with their details
    """
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT s.service_id, s.service_name, s.service_type, s.port, s.protocol,
                       s.endpoint, s.health_check_url, s.status, s.notes,
                       d.device_name, d.primary_ip as device_ip
                FROM infrastructure.services s
                LEFT JOIN infrastructure.devices d ON s.device_id = d.device_id
                WHERE 1=1
            """
            params = []

            if device_name:
                query += " AND d.device_name = %s"
                params.append(device_name)
            if service_type:
                query += " AND s.service_type = %s"
                params.append(service_type)

            query += " ORDER BY s.service_name"
            cur.execute(query, params)
            rows = cur.fetchall()

            return [dict(row) for row in rows]


@mcp.tool()
def homelab_check_service_health(service_name: str) -> dict:
    """
    Check the health of a service by calling its health endpoint.

    Args:
        service_name: Name of the service to check

    Returns:
        Health status including response time
    """
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT s.*, d.primary_ip as device_ip
                FROM infrastructure.services s
                LEFT JOIN infrastructure.devices d ON s.device_id = d.device_id
                WHERE s.service_name = %s
            """, (service_name,))

            row = cur.fetchone()
            if not row:
                return {"error": f"Service not found: {service_name}"}

            service = dict(row)

            # Build health check URL
            if service.get("health_check_url"):
                health_url = service["health_check_url"]
            elif service.get("endpoint"):
                health_url = f"{service['endpoint']}/health"
            elif service.get("device_ip") and service.get("port"):
                protocol = service.get("protocol", "http")
                health_url = f"{protocol}://{service['device_ip']}:{service['port']}/health"
            else:
                return {
                    "service": service_name,
                    "status": "unknown",
                    "error": "No health endpoint configured"
                }

            # Perform health check
            try:
                start = datetime.now()
                response = httpx.get(health_url, timeout=5.0)
                elapsed = (datetime.now() - start).total_seconds() * 1000

                return {
                    "service": service_name,
                    "url": health_url,
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": round(elapsed, 2)
                }
            except httpx.TimeoutException:
                return {
                    "service": service_name,
                    "url": health_url,
                    "status": "timeout",
                    "error": "Request timed out after 5s"
                }
            except Exception as e:
                return {
                    "service": service_name,
                    "url": health_url,
                    "status": "error",
                    "error": str(e)
                }


# ==================== Network Tools ====================

@mcp.tool()
def homelab_list_networks() -> list[dict]:
    """
    List all networks/VLANs in the HomeLab.

    Returns:
        List of networks with VLAN IDs, subnets, and purposes
    """
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT network_id, network_name, vlan_id, subnet, gateway,
                       dhcp_enabled, purpose, security_zone, notes
                FROM network.networks
                ORDER BY COALESCE(vlan_id, 0), network_name
            """)
            rows = cur.fetchall()

            return [dict(row) for row in rows]


@mcp.tool()
def homelab_list_firewall_rules() -> list[dict]:
    """
    List firewall rules configured in the HomeLab.

    Returns:
        List of firewall rules with source/destination and actions
    """
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT rule_id, rule_name, enabled, action, protocol,
                       source_network, destination_network, rule_index, notes
                FROM network.firewall_rules
                ORDER BY rule_index
            """)
            rows = cur.fetchall()

            return [dict(row) for row in rows]


@mcp.tool()
def homelab_lookup_ip(ip: str) -> dict:
    """
    Look up what's allocated to an IP address.

    Args:
        ip: IP address to look up (e.g., "10.0.1.150")

    Returns:
        Allocation details including device name and type
    """
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check devices table
            cur.execute("""
                SELECT device_id, device_name, device_type, category, status, notes
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
                    "status": device["status"],
                    "notes": device["notes"]
                }

            return {"ip_address": ip, "allocated_to": None, "status": "unallocated"}


# ==================== Credential Tools ====================

@mcp.tool()
def homelab_get_credentials(target: str) -> dict:
    """
    Get credentials for a target device or service. ALL ACCESS IS AUDIT LOGGED.

    Args:
        target: Target in format "device:<name>" or "service:<name>"
                (e.g., "device:ccpm-nas", "service:PostgreSQL")

    Returns:
        Credentials including username, password (if decryption key available)
    """
    parts = target.split(":", 1)
    if len(parts) != 2:
        return {"error": "Invalid target format. Use 'device:<name>' or 'service:<name>'"}

    target_type, target_name = parts
    encryption = get_encryption()

    with get_db() as conn:
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
                log_audit(conn, "credential_access_failed", target_type, target_name,
                         details=f"invalid_type={target_type}")
                return {"error": f"Unknown target type: {target_type}. Use 'device' or 'service'"}

            row = cur.fetchone()
            if not row:
                log_audit(conn, "credential_access_failed", target_type, target_name,
                         details="not_found")
                return {"error": f"No credentials found for {target}"}

            result = dict(row)

            # Decrypt password if encryption available
            password = None
            if result.get("password_encrypted"):
                if encryption:
                    try:
                        password = encryption.decrypt(result["password_encrypted"])
                    except Exception as e:
                        logger.error(f"Decryption failed: {e}")
                        password = "[DECRYPTION_FAILED]"
                else:
                    password = "[ENCRYPTED - KEY NOT AVAILABLE]"

            # Log successful access
            log_audit(conn, "credential_access", target_type, target_name, details="success")

            return {
                "target": target,
                "name": result.get("device_name") or result.get("service_name"),
                "ip": str(result.get("primary_ip")) if result.get("primary_ip") else None,
                "username": result.get("username"),
                "password": password,
                "ssh_key": result.get("ssh_key_path"),
                "auth_type": result.get("auth_type"),
            }


# ==================== Summary Tools ====================

@mcp.tool()
def homelab_infrastructure_summary() -> dict:
    """
    Get a summary of all HomeLab infrastructure.

    Returns:
        Summary with device counts, online status, and key systems
    """
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Device counts by category
            cur.execute("""
                SELECT category, status, COUNT(*) as count
                FROM infrastructure.devices
                GROUP BY category, status
                ORDER BY category, status
            """)
            device_stats = cur.fetchall()

            # SCPI equipment status
            cur.execute("""
                SELECT d.status, COUNT(*) as count
                FROM scpi.equipment e
                JOIN infrastructure.devices d ON e.equipment_id = d.device_id
                GROUP BY d.status
            """)
            scpi_stats = cur.fetchall()

            # Service count
            cur.execute("SELECT COUNT(*) as count FROM infrastructure.services")
            service_count = cur.fetchone()["count"]

            # Network count
            cur.execute("SELECT COUNT(*) as count FROM network.networks")
            network_count = cur.fetchone()["count"]

            # Online devices with IPs
            cur.execute("""
                SELECT device_name, device_type, primary_ip
                FROM infrastructure.devices
                WHERE status = 'online' AND primary_ip IS NOT NULL
                ORDER BY primary_ip
            """)
            online_devices = cur.fetchall()

            return {
                "device_stats": [dict(r) for r in device_stats],
                "scpi_stats": [dict(r) for r in scpi_stats],
                "service_count": service_count,
                "network_count": network_count,
                "online_devices": [dict(r) for r in online_devices],
                "database": {
                    "host": DB_CONFIG["host"],
                    "port": DB_CONFIG["port"],
                    "name": DB_CONFIG["database"]
                }
            }


# ==================== Run Server ====================

if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 8080))
    logger.info(f"Starting HomeLab MCP Server (Infrastructure Only)")
    logger.info(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    logger.info(f"Listening on port {port}")
    mcp.run(transport="sse", port=port, host="0.0.0.0")
