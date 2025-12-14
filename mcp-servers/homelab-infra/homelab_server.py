#!/usr/bin/env python3
"""
HomeLab Infrastructure MCP Server.
Provides tool access to VMs, credentials, services, and network config.
"""

import os
import sys
import sqlite3
import logging
import httpx
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("homelab-mcp")

# Initialize MCP server
mcp = FastMCP("homelab-infra")

# Database path (mounted into container or local)
DB_PATH = os.environ.get(
    "HOMELAB_DB_PATH",
    "/data/homelab.db"
)

# Optional: Encryption key for credentials
DB_KEY = os.environ.get("HOMELAB_DB_KEY")


# ==================== Database Helpers ====================

@contextmanager
def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def log_audit(conn: sqlite3.Connection, action: str, target_type: str,
              target_id: int, user: str = "mcp-agent", details: str = None):
    """Log an audit entry for security-sensitive actions."""
    conn.execute("""
        INSERT INTO audit_log (action, target_type, target_id, user, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (action, target_type, target_id, user, details or "success", "docker"))
    conn.commit()


def get_encryption():
    """Get encryption instance if key is available."""
    if not DB_KEY:
        return None
    try:
        # Try importing from mounted infrastructure path
        sys.path.insert(0, "/app/infrastructure")
        from db.encryption import CredentialEncryption
        return CredentialEncryption(DB_KEY.encode() if isinstance(DB_KEY, str) else DB_KEY)
    except ImportError:
        logger.warning("Encryption module not available, credentials will be masked")
        return None


# ==================== VM Tools ====================

@mcp.tool()
def homelab_list_vms(status: str = None) -> list[dict]:
    """
    List all virtual machines in the HomeLab.

    Args:
        status: Optional filter by status (running, stopped, template)

    Returns:
        List of VMs with their details
    """
    with get_db() as conn:
        query = """
            SELECT vm.*, h.node_name as host_name, h.ip_address as host_ip
            FROM virtual_machines vm
            LEFT JOIN proxmox_hosts h ON vm.host_id = h.id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND vm.status = ?"
            params.append(status)

        query += " ORDER BY vm.host_id, vm.vm_id"
        rows = conn.execute(query, params).fetchall()

        return [dict(row) for row in rows]


@mcp.tool()
def homelab_get_vm(vm_id: int = None, name: str = None) -> dict:
    """
    Get detailed information about a specific VM.

    Args:
        vm_id: Proxmox VM ID (e.g., 100)
        name: VM name (e.g., "whisper")

    Returns:
        VM details including host info, or error if not found
    """
    if vm_id is None and name is None:
        return {"error": "Must provide either vm_id or name"}

    with get_db() as conn:
        if vm_id is not None:
            row = conn.execute("""
                SELECT vm.*, h.node_name as host_name, h.ip_address as host_ip
                FROM virtual_machines vm
                LEFT JOIN proxmox_hosts h ON vm.host_id = h.id
                WHERE vm.vm_id = ?
            """, (vm_id,)).fetchone()
        else:
            row = conn.execute("""
                SELECT vm.*, h.node_name as host_name, h.ip_address as host_ip
                FROM virtual_machines vm
                LEFT JOIN proxmox_hosts h ON vm.host_id = h.id
                WHERE vm.name = ?
            """, (name,)).fetchone()

        if row:
            return dict(row)
        return {"error": f"VM not found: {vm_id or name}"}


# ==================== Credential Tools ====================

@mcp.tool()
def homelab_get_credentials(target: str) -> dict:
    """
    Get credentials for a target. ALL ACCESS IS AUDIT LOGGED.

    Args:
        target: Target in format "type:id" (e.g., "vm:100", "host:1", "service:piper-tts")

    Returns:
        Credentials including username, password (decrypted), ssh_key, ip
    """
    parts = target.split(":", 1)
    if len(parts) != 2:
        return {"error": "Invalid target format. Use 'type:id' (e.g., vm:100)"}

    target_type, target_id = parts
    encryption = get_encryption()

    with get_db() as conn:
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
            log_audit(conn, "credential_access_failed", target_type, 0,
                     details=f"invalid_type={target_type}")
            return {"error": f"Unknown target type: {target_type}"}

        if not row:
            log_audit(conn, "credential_access_failed", target_type,
                     int(target_id) if target_id.isdigit() else 0,
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
        log_audit(conn, "credential_access", target_type,
                 result.get("target_id", 0), details="success")

        return {
            "target": target,
            "name": result.get("name"),
            "ip": result.get("ip_address"),
            "username": result.get("username"),
            "password": password,
            "ssh_key": result.get("ssh_key_path"),
            "auth_type": result.get("auth_type"),
            "is_root": bool(result.get("is_root", False))
        }


# ==================== Service Tools ====================

@mcp.tool()
def homelab_list_services(vm_id: int = None) -> list[dict]:
    """
    List all services in the HomeLab.

    Args:
        vm_id: Optional Proxmox VM ID to filter services

    Returns:
        List of services with their details
    """
    with get_db() as conn:
        query = """
            SELECT s.*, vm.name as vm_name, vm.ip_address as vm_ip, vm.vm_id
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
        row = conn.execute("""
            SELECT s.*, vm.ip_address as vm_ip
            FROM services s
            LEFT JOIN virtual_machines vm ON s.vm_id = vm.id
            WHERE s.service_name = ?
        """, (service_name,)).fetchone()

        if not row:
            return {"error": f"Service not found: {service_name}"}

        service = dict(row)

        # Build health check URL
        if service.get("health_endpoint"):
            health_url = service["health_endpoint"]
        elif service.get("url"):
            health_url = f"{service['url']}/health"
        elif service.get("vm_ip") and service.get("port"):
            protocol = service.get("protocol", "http")
            health_url = f"{protocol}://{service['vm_ip']}:{service['port']}/health"
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


# ==================== Host Tools ====================

@mcp.tool()
def homelab_list_hosts() -> list[dict]:
    """
    List all Proxmox hosts in the HomeLab.

    Returns:
        List of hosts with their details
    """
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM proxmox_hosts ORDER BY node_name
        """).fetchall()

        return [dict(row) for row in rows]


@mcp.tool()
def homelab_get_host(host_id: int = None, name: str = None) -> dict:
    """
    Get detailed information about a Proxmox host.

    Args:
        host_id: Host database ID
        name: Host node name

    Returns:
        Host details or error if not found
    """
    if host_id is None and name is None:
        return {"error": "Must provide either host_id or name"}

    with get_db() as conn:
        if host_id:
            row = conn.execute(
                "SELECT * FROM proxmox_hosts WHERE id = ?", (host_id,)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM proxmox_hosts WHERE node_name = ?", (name,)
            ).fetchone()

        if row:
            return dict(row)
        return {"error": f"Host not found: {host_id or name}"}


# ==================== Network Tools ====================

@mcp.tool()
def homelab_lookup_ip(ip: str) -> dict:
    """
    Look up what's allocated to an IP address.

    Args:
        ip: IP address to look up (e.g., "10.0.1.201")

    Returns:
        Allocation details including hostname and type
    """
    with get_db() as conn:
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
            vm_dict = dict(vm)
            return {
                "ip_address": ip,
                "allocated_to": f"vm:{vm_dict['vm_id']} ({vm_dict['name']})",
                "hostname": vm_dict["name"],
                "type": "virtual_machine",
                "source": "virtual_machines"
            }

        # Check hosts
        host = conn.execute("""
            SELECT * FROM proxmox_hosts WHERE ip_address = ?
        """, (ip,)).fetchone()

        if host:
            host_dict = dict(host)
            return {
                "ip_address": ip,
                "allocated_to": f"host:{host_dict['id']} ({host_dict['node_name']})",
                "hostname": host_dict["node_name"],
                "type": "proxmox_host",
                "source": "proxmox_hosts"
            }

        return {"ip_address": ip, "allocated_to": None, "status": "unallocated"}


# ==================== Run Server ====================

if __name__ == "__main__":
    import os
    port = int(os.environ.get("MCP_PORT", 8080))
    logger.info(f"Starting HomeLab MCP Server with DB: {DB_PATH} on port {port}")
    mcp.run(transport="sse", port=port, host="0.0.0.0")
