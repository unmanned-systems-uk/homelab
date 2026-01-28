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

# CCPM Database config (for piggyback messaging)
CCPM_DB_CONFIG = {
    "host": os.environ.get("CCPM_DB_HOST", "10.0.1.251"),
    "port": int(os.environ.get("CCPM_DB_PORT", 5433)),
    "database": os.environ.get("CCPM_DB_NAME", "ccpm_db"),
    "user": os.environ.get("CCPM_DB_USER", "ccpm"),
    "password": os.environ.get("CCPM_DB_PASSWORD", "CcpmDb2025Secure"),
}

# Agent ID for piggyback messaging
CCPM_AGENT_ID = os.environ.get("CCPM_AGENT_ID", "unknown")


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


# ==================== Piggyback Messaging Helpers ====================

@contextmanager
def get_ccpm_db():
    """Get CCPM database connection for piggyback messaging."""
    conn = psycopg2.connect(**CCPM_DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def fetch_pending_piggyback_messages(recipient: str) -> list[dict]:
    """
    Fetch and mark delivered all pending piggyback messages for a recipient.
    Uses atomic UPDATE...RETURNING to prevent duplicate delivery.

    Args:
        recipient: Agent ID to fetch messages for

    Returns:
        List of message dicts with id, from, message, priority, sent_at
    """
    try:
        with get_ccpm_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    UPDATE piggyback_messages
                    SET delivered_at = NOW()
                    WHERE recipient = %s AND delivered_at IS NULL
                    RETURNING id, sender, content, priority, created_at
                """, (recipient,))
                rows = cur.fetchall()
                conn.commit()

                if rows:
                    return [
                        {
                            "id": row["id"],
                            "from": row["sender"],
                            "message": row["content"],
                            "priority": row["priority"],
                            "sent_at": row["created_at"].isoformat() if row["created_at"] else None
                        }
                        for row in rows
                    ]
                return []
    except Exception as e:
        logger.warning(f"Failed to fetch piggyback messages: {e}")
        return []


def inject_piggyback_messages(result: dict, agent_id: str = None) -> dict:
    """
    Inject pending piggyback messages into a tool response.
    Call this at the end of any tool to include pending messages.

    Args:
        result: The tool's original response dict
        agent_id: Override agent ID (defaults to CCPM_AGENT_ID)

    Returns:
        Result dict with _inbox field if messages are pending
    """
    recipient = agent_id or CCPM_AGENT_ID
    if recipient == "unknown":
        return result

    messages = fetch_pending_piggyback_messages(recipient)
    if messages:
        if isinstance(result, dict):
            result["_inbox"] = messages
        else:
            result = {"result": result, "_inbox": messages}

    return result


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


# ==================== CCPM Integration ====================

# CCPM API endpoints
CCPM_TASK_API = os.environ.get("CCPM_TASK_API", "http://10.0.1.210:8000/api/v1")
CCPM_MESSAGING_API = os.environ.get("CCPM_MESSAGING_API", "http://10.0.1.210:8000/api/v1")

# Agent cache (5 minute TTL)
_agent_cache = {"data": None, "timestamp": None}
AGENT_CACHE_TTL = 300  # 5 minutes

def get_cached_agents(force_refresh: bool = False) -> dict:
    """Get cached agent list or fetch fresh if expired."""
    import time

    now = time.time()
    if (not force_refresh and
        _agent_cache["data"] is not None and
        _agent_cache["timestamp"] is not None and
        now - _agent_cache["timestamp"] < AGENT_CACHE_TTL):
        return _agent_cache["data"]

    # Fetch fresh data
    try:
        response = httpx.get(f"{CCPM_MESSAGING_API}/agents", timeout=10.0)
        response.raise_for_status()
        agents = response.json()

        # Update cache
        _agent_cache["data"] = {agent["name"]: agent for agent in agents}
        _agent_cache["timestamp"] = now
        return _agent_cache["data"]
    except Exception as e:
        logger.error(f"Failed to fetch agents: {e}")
        # Return stale cache if available
        if _agent_cache["data"]:
            logger.warning("Using stale agent cache due to fetch failure")
            return _agent_cache["data"]
        raise

def resolve_agent_id(agent_identifier: str) -> str:
    """
    Resolve agent name to UUID, or return UUID if already in UUID format.

    Args:
        agent_identifier: Agent name (e.g., "HomeLab-Agent") or UUID

    Returns:
        Agent UUID

    Raises:
        ValueError: If agent not found
    """
    # Check if already a UUID (contains hyphens and hex chars)
    if len(agent_identifier) == 36 and agent_identifier.count('-') == 4:
        return agent_identifier

    # Resolve name to UUID
    agents = get_cached_agents()
    if agent_identifier in agents:
        return agents[agent_identifier]["id"]

    # Try case-insensitive match
    for name, agent in agents.items():
        if name.lower() == agent_identifier.lower():
            return agent["id"]

    raise ValueError(f"Agent not found: {agent_identifier}")


# ==================== Agent Messaging Tools ====================

@mcp.tool()
def ccpm_list_agents(status: str = None, agent_type: str = None) -> list[dict]:
    """
    List all registered agents in the CCPM system.

    Args:
        status: Optional filter by status ("active", "idle")
        agent_type: Optional filter by type ("orchestrator", "backend", etc.)

    Returns:
        List of agents with their details
    """
    try:
        params = {}
        if status:
            params["status"] = status
        if agent_type:
            params["agent_type"] = agent_type

        response = httpx.get(f"{CCPM_MESSAGING_API}/agents", params=params, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_send_message(
    to_agent: str,
    subject: str,
    body: str,
    message_type: str = "info",
    priority: str = "normal",
    from_agent_id: str = None
) -> dict:
    """
    Send a message to another agent. Can use agent name (resolved to UUID) or direct UUID.

    Args:
        to_agent: Agent name (e.g., "HomeLab-Agent") or UUID
        subject: Message subject
        body: Message body
        message_type: Type of message (info, task_assignment, query, alert, etc.)
        priority: Message priority (low, normal, high)
        from_agent_id: Sender agent UUID (defaults to env CCPM_AGENT_ID)

    Returns:
        Success response with message ID or error
    """
    valid_types = [
        "task_assignment", "task_request", "feature_request", "bug_report",
        "status_request", "completion_signal", "alert", "info", "query", "response"
    ]

    if message_type not in valid_types:
        return {
            "success": False,
            "error": f"Invalid message_type. Must be one of: {', '.join(valid_types)}",
            "error_code": "INVALID_MESSAGE_TYPE"
        }

    try:
        # Resolve recipient
        to_agent_id = resolve_agent_id(to_agent)

        # Get sender ID
        sender_id = from_agent_id or os.environ.get("CCPM_AGENT_ID")
        if not sender_id:
            return {
                "success": False,
                "error": "No sender agent ID provided and CCPM_AGENT_ID not set",
                "error_code": "MISSING_SENDER_ID"
            }

        # Send message
        payload = {
            "to_agent_id": to_agent_id,
            "subject": subject,
            "body": body,
            "message_type": message_type,
            "priority": priority
        }

        response = httpx.post(
            f"{CCPM_MESSAGING_API}/agent-messages",
            params={"from_agent_id": sender_id},
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "AGENT_NOT_FOUND"
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code} - {e.response.text}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


# Broadcast UUID constant
BROADCAST_UUID = "ffffffff-ffff-ffff-ffff-ffffffffffff"


@mcp.tool()
def ccpm_broadcast_message(
    subject: str,
    body: str,
    message_type: str = "info",
    priority: str = "normal",
    exclude_self: bool = True
) -> dict:
    """
    Broadcast a message to ALL registered agents. Fans out to each agent individually.
    Use for announcements, protocol changes, system updates.

    Args:
        subject: Message subject
        body: Message body
        message_type: Type of message (info, alert, etc.) - default: info
        priority: Message priority (low, normal, high) - default: normal
        exclude_self: Don't send to self (default: True)

    Returns:
        Dict with success status, count of messages sent, and any failures
    """
    result = {
        "success": False,
        "broadcast_id": BROADCAST_UUID,
        "total_agents": 0,
        "sent_count": 0,
        "failed_count": 0,
        "sent_to": [],
        "failed": []
    }

    # Get sender ID
    sender_id = os.environ.get("CCPM_AGENT_ID")
    if not sender_id:
        return {
            "success": False,
            "error": "CCPM_AGENT_ID not set",
            "error_code": "MISSING_SENDER_ID"
        }

    try:
        # Get all agents
        agents_response = httpx.get(f"{CCPM_MESSAGING_API}/agents", timeout=10.0)
        agents_response.raise_for_status()
        agents = agents_response.json()

        result["total_agents"] = len(agents)

        # Send to each agent
        for agent in agents:
            agent_id = agent.get("id")
            agent_name = agent.get("name", "Unknown")

            # Skip self if requested
            if exclude_self and agent_id == sender_id:
                continue

            try:
                payload = {
                    "to_agent_id": agent_id,
                    "message_type": message_type,
                    "subject": subject,
                    "body": body,
                    "priority": priority
                }

                msg_response = httpx.post(
                    f"{CCPM_MESSAGING_API}/agent-messages?from_agent_id={sender_id}",
                    json=payload,
                    timeout=5.0
                )
                msg_response.raise_for_status()
                result["sent_count"] += 1
                result["sent_to"].append(agent_name)

            except Exception as e:
                result["failed_count"] += 1
                result["failed"].append({"agent": agent_name, "error": str(e)})

        result["success"] = result["sent_count"] > 0
        return result

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"Failed to fetch agents: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_check_inbox(
    agent_id: str = None,
    include_read: bool = False,
    auto_deliver: bool = True,
    auto_complete_info: bool = True
) -> dict:
    """
    Check inbox for pending messages. By default, auto-marks messages as delivered
    and auto-completes info/broadcast messages.

    Args:
        agent_id: Agent UUID (defaults to env CCPM_AGENT_ID)
        include_read: Whether to include read messages
        auto_deliver: Auto-mark fetched messages as delivered (default: True)
        auto_complete_info: Auto-complete 'info' type messages after fetch (default: True)

    Returns:
        Dict with messages list and lifecycle actions taken
    """
    result = {
        "success": True,
        "messages": [],
        "delivered_count": 0,
        "auto_completed_count": 0,
        "auto_completed_ids": []
    }

    try:
        # Get agent ID
        target_agent_id = agent_id or os.environ.get("CCPM_AGENT_ID")
        if not target_agent_id:
            return {
                "success": False,
                "error": "No agent ID provided and CCPM_AGENT_ID not set",
                "error_code": "MISSING_AGENT_ID"
            }

        params = {"agent_id": target_agent_id}
        if not include_read:
            params["status"] = "pending"

        response = httpx.get(
            f"{CCPM_MESSAGING_API}/agent-messages/inbox",
            params=params,
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        # Handle paginated response
        messages = data["items"] if isinstance(data, dict) and "items" in data else data
        result["messages"] = messages

        # Auto-mark as delivered
        if auto_deliver and messages:
            for msg in messages:
                msg_id = msg.get("id")
                if msg_id and msg.get("status") == "pending":
                    try:
                        httpx.post(
                            f"{CCPM_MESSAGING_API}/agent-messages/{msg_id}/delivered",
                            timeout=5.0
                        )
                        result["delivered_count"] += 1
                    except Exception as e:
                        logger.warning(f"Failed to mark message {msg_id} as delivered: {e}")

        # Auto-complete info messages
        if auto_complete_info and messages:
            for msg in messages:
                msg_id = msg.get("id")
                msg_type = msg.get("message_type")
                # Auto-complete info and broadcast messages
                if msg_id and msg_type == "info":
                    try:
                        # First mark read
                        httpx.post(
                            f"{CCPM_MESSAGING_API}/agent-messages/{msg_id}/read",
                            timeout=5.0
                        )
                        # Then mark complete
                        httpx.post(
                            f"{CCPM_MESSAGING_API}/agent-messages/{msg_id}/complete",
                            json={"response": "Auto-acknowledged info message"},
                            timeout=5.0
                        )
                        result["auto_completed_count"] += 1
                        result["auto_completed_ids"].append(msg_id)
                    except Exception as e:
                        logger.warning(f"Failed to auto-complete info message {msg_id}: {e}")

        return result

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_mark_message_read(message_id: str) -> dict:
    """
    Mark a message as read.

    Args:
        message_id: Message UUID

    Returns:
        Success response or error
    """
    try:
        response_obj = httpx.post(
            f"{CCPM_MESSAGING_API}/agent-messages/{message_id}/read",
            timeout=10.0
        )
        response_obj.raise_for_status()
        return response_obj.json()

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_mark_message_complete(
    message_id: str,
    response: str = None,
    auto_notify_sender: bool = True
) -> dict:
    """
    Mark a message as complete, optionally with a response.
    When a response is provided, automatically notifies the original sender.

    Args:
        message_id: Message UUID
        response: Optional response text
        auto_notify_sender: Send notification to original sender when response provided (default: True)

    Returns:
        Success response including notification status if response was sent
    """
    result = {
        "message_id": message_id,
        "completed": False,
        "notification_sent": False,
        "success": False
    }

    try:
        # Step 1: Get original message to find sender (only if we need to notify)
        original_msg = None
        if response and auto_notify_sender:
            try:
                msg_response = httpx.get(
                    f"{CCPM_MESSAGING_API}/agent-messages/{message_id}",
                    timeout=10.0
                )
                msg_response.raise_for_status()
                original_msg = msg_response.json()
            except Exception as e:
                logger.warning(f"Failed to fetch original message for notification: {e}")

        # Step 2: Mark message as complete
        payload = {}
        if response:
            payload["response"] = response

        complete_response = httpx.post(
            f"{CCPM_MESSAGING_API}/agent-messages/{message_id}/complete",
            json=payload,
            timeout=10.0
        )
        complete_response.raise_for_status()
        completed_msg = complete_response.json()
        result["completed"] = True
        result["message"] = completed_msg

        # Step 3: Auto-notify sender if response was provided
        if response and auto_notify_sender and original_msg:
            sender_id = original_msg.get("from_agent_id")
            sender_name = original_msg.get("sender_name", "Unknown")
            recipient_name = original_msg.get("recipient_name", "Agent")
            subject = original_msg.get("subject", "No subject")

            # Get our agent ID
            our_agent_id = CCPM_AGENT_ID

            if sender_id and our_agent_id and sender_id != our_agent_id:
                try:
                    # Truncate response for notification (first 200 chars)
                    response_preview = response[:200] + "..." if len(response) > 200 else response

                    notify_payload = {
                        "to_agent_id": sender_id,
                        "message_type": "response",
                        "subject": f"[Response] {subject}",
                        "body": f"{recipient_name} has responded to your message.\n\nOriginal: {subject}\n\nResponse:\n{response_preview}\n\n---\nView full response on message ID: {message_id}",
                        "priority": "normal",
                        "context": {"original_message_id": message_id}
                    }

                    notify_response = httpx.post(
                        f"{CCPM_MESSAGING_API}/agent-messages?from_agent_id={our_agent_id}",
                        json=notify_payload,
                        timeout=10.0
                    )
                    notify_response.raise_for_status()
                    result["notification_sent"] = True
                    result["notification_to"] = sender_name
                except Exception as e:
                    logger.warning(f"Failed to send auto-notification: {e}")
                    result["notification_error"] = str(e)

        result["success"] = result["completed"]
        return result

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_acknowledge_and_complete(
    message_id: str,
    response: str = None,
    auto_notify_sender: bool = True
) -> dict:
    """
    Mark a message as read AND complete in one call. Convenience helper.
    When a response is provided, automatically notifies the original sender.

    Args:
        message_id: Message UUID
        response: Optional response text
        auto_notify_sender: Send notification to original sender when response provided (default: True)

    Returns:
        Success response with both operations status and notification info
    """
    results = {
        "message_id": message_id,
        "read": False,
        "completed": False,
        "notification_sent": False,
        "success": False
    }

    # Step 0: Get original message for notification (if needed)
    original_msg = None
    if response and auto_notify_sender:
        try:
            msg_response = httpx.get(
                f"{CCPM_MESSAGING_API}/agent-messages/{message_id}",
                timeout=10.0
            )
            msg_response.raise_for_status()
            original_msg = msg_response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch original message for notification: {e}")

    # Step 1: Mark as read
    try:
        read_response = httpx.post(
            f"{CCPM_MESSAGING_API}/agent-messages/{message_id}/read",
            timeout=10.0
        )
        read_response.raise_for_status()
        results["read"] = True
    except Exception as e:
        results["read_error"] = str(e)

    # Step 2: Mark as complete
    try:
        payload = {}
        if response:
            payload["response"] = response

        complete_response = httpx.post(
            f"{CCPM_MESSAGING_API}/agent-messages/{message_id}/complete",
            json=payload,
            timeout=10.0
        )
        complete_response.raise_for_status()
        results["completed"] = True
    except Exception as e:
        results["complete_error"] = str(e)

    # Step 3: Auto-notify sender if response was provided
    if response and auto_notify_sender and original_msg and results["completed"]:
        sender_id = original_msg.get("from_agent_id")
        sender_name = original_msg.get("sender_name", "Unknown")
        recipient_name = original_msg.get("recipient_name", "Agent")
        subject = original_msg.get("subject", "No subject")
        our_agent_id = CCPM_AGENT_ID

        if sender_id and our_agent_id and sender_id != our_agent_id:
            try:
                response_preview = response[:200] + "..." if len(response) > 200 else response
                notify_payload = {
                    "to_agent_id": sender_id,
                    "message_type": "response",
                    "subject": f"[Response] {subject}",
                    "body": f"{recipient_name} has responded to your message.\n\nOriginal: {subject}\n\nResponse:\n{response_preview}\n\n---\nView full response on message ID: {message_id}",
                    "priority": "normal",
                    "context": {"original_message_id": message_id}
                }
                notify_response = httpx.post(
                    f"{CCPM_MESSAGING_API}/agent-messages?from_agent_id={our_agent_id}",
                    json=notify_payload,
                    timeout=10.0
                )
                notify_response.raise_for_status()
                results["notification_sent"] = True
                results["notification_to"] = sender_name
            except Exception as e:
                logger.warning(f"Failed to send auto-notification: {e}")
                results["notification_error"] = str(e)

    results["success"] = results["read"] and results["completed"]
    return results


# ==================== Task Management Tools ====================

@mcp.tool()
def ccpm_get_task(task_id: int) -> dict:
    """
    Get details of a specific task by ID.

    Args:
        task_id: Task ID

    Returns:
        Task details
    """
    try:
        response = httpx.get(f"{CCPM_TASK_API}/tasks/{task_id}", timeout=10.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_list_tasks(
    sprint_id: int = None,
    status: str = None,
    assignee: str = None
) -> list[dict]:
    """
    List tasks with optional filters.

    Args:
        sprint_id: Filter by sprint ID
        status: Filter by status (pending, in-progress, review, blocked, testing, done)
        assignee: Filter by assignee name

    Returns:
        List of tasks
    """
    try:
        params = {}
        if sprint_id is not None:
            params["sprint_id"] = sprint_id
        if status:
            params["status"] = status
        if assignee:
            params["assigned_to"] = assignee

        response = httpx.get(f"{CCPM_TASK_API}/tasks", params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        # Handle response format
        if isinstance(data, dict) and "tasks" in data:
            return data["tasks"]
        return data

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_update_task_status(
    task_id: int,
    status: str,
    blocked_reason: str = None
) -> dict:
    """
    Update task status. Agents can set: in-progress, review, blocked, testing.

    Args:
        task_id: Task ID
        status: New status (in-progress, review, blocked, testing)
        blocked_reason: Required if status is "blocked"

    Returns:
        Updated task or error
    """
    agent_allowed_statuses = ["in-progress", "review", "blocked", "testing"]

    if status not in agent_allowed_statuses:
        return {
            "success": False,
            "error": f"Agents can only set status to: {', '.join(agent_allowed_statuses)}",
            "error_code": "INVALID_STATUS"
        }

    if status == "blocked" and not blocked_reason:
        return {
            "success": False,
            "error": "blocked_reason is required when status is 'blocked'",
            "error_code": "MISSING_BLOCKED_REASON"
        }

    try:
        payload = {"status": status}
        if blocked_reason:
            payload["blocked_reason"] = blocked_reason

        response = httpx.put(
            f"{CCPM_TASK_API}/agent/tasks/{task_id}/status",
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


# ==================== Task Instructions Tools ====================

@mcp.tool()
def ccpm_get_task_instructions(task_id: str) -> dict:
    """
    Get all instructions for a task including injected and custom instructions.

    Args:
        task_id: Task UUID

    Returns:
        List of instructions with trigger_event, content, is_mandatory, is_custom fields
    """
    try:
        response = httpx.get(
            f"{CCPM_TASK_API}/tasks/{task_id}/instructions",
            timeout=10.0
        )
        response.raise_for_status()
        return {"success": True, "instructions": response.json()}
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_add_custom_instruction(
    task_id: str,
    content: str,
    trigger_event: str = "on_start"
) -> dict:
    """
    Add a custom instruction to a task.

    Args:
        task_id: Task UUID
        content: Instruction content text
        trigger_event: When to show instruction (on_start, on_complete, on_review, on_blocked)

    Returns:
        Created instruction details or error
    """
    valid_triggers = ["on_start", "on_complete", "on_review", "on_blocked"]
    if trigger_event not in valid_triggers:
        return {
            "success": False,
            "error": f"Invalid trigger_event. Must be one of: {valid_triggers}",
            "error_code": "VALIDATION_ERROR"
        }

    try:
        payload = {
            "content": content,
            "trigger_event": trigger_event
        }
        response = httpx.post(
            f"{CCPM_TASK_API}/tasks/{task_id}/instructions/custom",
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        return {"success": True, "instruction": response.json()}
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_submit_completion_report(
    task_id: int,
    report: str,
    submitted_by: str
) -> dict:
    """
    Submit a completion report for a task. Triggers GitHub posting and signal script.

    Args:
        task_id: Task ID
        report: Completion report text
        submitted_by: Agent name submitting the report

    Returns:
        Success response or error
    """
    try:
        payload = {
            "report": report,
            "submitted_by": submitted_by
        }

        response = httpx.post(
            f"{CCPM_TASK_API}/tasks/{task_id}/report",
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


# ==================== Sprint Management Tools ====================

@mcp.tool()
def ccpm_get_active_sprint() -> dict:
    """
    Get the currently active sprint with task counts.

    Returns:
        Active sprint details or error
    """
    try:
        response = httpx.get(
            f"{CCPM_TASK_API}/sprints",
            params={"status": "active"},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        # Return first active sprint
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        elif isinstance(data, dict) and "sprints" in data and len(data["sprints"]) > 0:
            return data["sprints"][0]

        return {
            "success": False,
            "error": "No active sprint found",
            "error_code": "NO_ACTIVE_SPRINT"
        }

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_list_sprints(status: str = None) -> list[dict]:
    """
    List sprints with optional status filter.

    Args:
        status: Filter by status (planning, active, completed)

    Returns:
        List of sprints
    """
    try:
        params = {}
        if status:
            params["status"] = status

        response = httpx.get(f"{CCPM_TASK_API}/sprints", params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        # Handle response format
        if isinstance(data, dict) and "sprints" in data:
            return data["sprints"]
        return data

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


# ==================== Session Logging Tools ====================
# Note: Session reports use /api/v1/session-reports endpoint (CCPM_MESSAGING_API)

@mcp.tool()
def ccpm_create_session(
    agent_id: str = None,
    agent_tag: str = "[HomeLab]",
    trigger_type: str = "manual",
    summary: str = None
) -> dict:
    """
    Create a new session report.

    Args:
        agent_id: UUID of the agent (defaults to CCPM_AGENT_ID env var)
        agent_tag: Agent tag for display (default: [HomeLab])
        trigger_type: How session was triggered (manual, scheduled)
        summary: Optional initial summary/description

    Returns:
        Created session report with id
    """
    from datetime import datetime, timezone

    aid = agent_id or CCPM_AGENT_ID
    if not aid:
        return {
            "success": False,
            "error": "agent_id required (set CCPM_AGENT_ID env var or pass explicitly)",
            "error_code": "MISSING_AGENT_ID"
        }

    valid_triggers = ["manual", "scheduled"]
    if trigger_type not in valid_triggers:
        return {
            "success": False,
            "error": f"Invalid trigger_type. Must be one of: {', '.join(valid_triggers)}",
            "error_code": "INVALID_TRIGGER_TYPE"
        }

    try:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        # API requires session_ended_at even for in-progress sessions (use placeholder)
        payload = {
            "agent_id": aid,
            "agent_tag": agent_tag,
            "trigger_type": trigger_type,
            "session_date": now.strftime("%Y-%m-%d"),
            "session_started_at": now.isoformat(),
            "session_ended_at": (now + timedelta(seconds=1)).isoformat(),  # Placeholder
            "duration_minutes": 0,
            "status": "in_progress"
        }
        if summary:
            payload["summary"] = summary

        response = httpx.post(
            f"{CCPM_MESSAGING_API}/session-reports",
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.json()
        except Exception:
            error_detail = e.response.text
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "detail": error_detail,
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_log_session_context(
    report_id: str,
    context_type: str,
    context_key: str,
    context_value: str = None,
    token_count: int = None
) -> dict:
    """
    Add a context item to a session report.

    Args:
        report_id: Session report UUID
        context_type: Type of context (file_read, tool_call, search, api_call)
        context_key: File path or identifier
        context_value: Optional description
        token_count: Optional token count for this context

    Returns:
        Created context entry or error
    """
    valid_types = ["file_read", "tool_call", "search", "api_call"]

    if context_type not in valid_types:
        return {
            "success": False,
            "error": f"Invalid context_type. Must be one of: {', '.join(valid_types)}",
            "error_code": "INVALID_CONTEXT_TYPE"
        }

    try:
        payload = {
            "context_type": context_type,
            "context_key": context_key
        }
        if context_value:
            payload["context_value"] = context_value
        if token_count:
            payload["token_count"] = token_count

        response = httpx.post(
            f"{CCPM_MESSAGING_API}/session-reports/{report_id}/contexts",
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_complete_session(
    report_id: str,
    summary: str,
    completed_items: list[str] = None,
    in_progress_items: list[str] = None,
    blockers: list[str] = None,
    handoff_notes: str = None,
    tasks_completed: int = 0,
    files_modified: int = 0,
    commits_made: int = 0,
    total_tokens: int = None
) -> dict:
    """
    Complete a session report with summary and metrics.

    Args:
        report_id: Session report UUID
        summary: Session summary text
        completed_items: List of completed task descriptions
        in_progress_items: List of in-progress items
        blockers: List of blockers encountered
        handoff_notes: Notes for next session
        tasks_completed: Number of tasks completed
        files_modified: Number of files modified
        commits_made: Number of git commits
        total_tokens: Total tokens used in session

    Returns:
        Updated session report or error
    """
    from datetime import datetime, timezone

    try:
        now = datetime.now(timezone.utc)
        payload = {
            "session_ended_at": now.isoformat(),
            "status": "completed",
            "summary": summary,
            "completed_items": completed_items or [],
            "in_progress_items": in_progress_items or [],
            "blockers": blockers or [],
            "tasks_completed": tasks_completed,
            "files_modified": files_modified,
            "commits_made": commits_made
        }
        if handoff_notes:
            payload["handoff_notes"] = handoff_notes
        if total_tokens:
            payload["total_tokens"] = total_tokens

        response = httpx.put(
            f"{CCPM_MESSAGING_API}/session-reports/{report_id}",
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_get_resume_context(agent_id: str = None) -> dict:
    """
    Get resume context from the most recent session.

    Args:
        agent_id: UUID of the agent (defaults to CCPM_AGENT_ID env var)

    Returns:
        Resume context from last session or error
    """
    aid = agent_id or CCPM_AGENT_ID
    if not aid:
        return {
            "success": False,
            "error": "agent_id required (set CCPM_AGENT_ID env var or pass explicitly)",
            "error_code": "MISSING_AGENT_ID"
        }

    try:
        response = httpx.get(
            f"{CCPM_MESSAGING_API}/session-reports/resume/{aid}",
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "success": False,
                "error": "No previous sessions found",
                "error_code": "NO_SESSIONS"
            }
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


# ==================== Piggyback Messaging Tools ====================

@mcp.tool()
def piggyback_send_message(
    recipient: str,
    message: str,
    priority: int = 5
) -> dict:
    """
    Send a piggyback message to another agent. Message will be delivered
    in their next MCP tool response.

    Args:
        recipient: Target agent ID (e.g., 'HomeLab-Agent', 'V2-Master', or UUID)
        message: Message content
        priority: 1-3 critical, 4-6 normal, 7-10 low (default: 5)

    Returns:
        Confirmation with message ID
    """
    if priority < 1 or priority > 10:
        return {
            "success": False,
            "error": "Priority must be between 1 and 10",
            "error_code": "VALIDATION_ERROR"
        }

    sender = CCPM_AGENT_ID
    if sender == "unknown":
        return {
            "success": False,
            "error": "CCPM_AGENT_ID not configured",
            "error_code": "CONFIG_ERROR"
        }

    try:
        with get_ccpm_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO piggyback_messages (sender, recipient, content, priority)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, created_at
                """, (sender, recipient, message, priority))
                row = cur.fetchone()
                conn.commit()

                return {
                    "success": True,
                    "message_id": row["id"],
                    "recipient": recipient,
                    "priority": priority,
                    "sent_at": row["created_at"].isoformat() if row["created_at"] else None
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "DB_ERROR"
        }


@mcp.tool()
def piggyback_check_messages(agent_id: str = None) -> dict:
    """
    Check for pending piggyback messages. Messages are marked as delivered
    when fetched (atomic operation prevents duplicates).

    Args:
        agent_id: Agent ID to check (defaults to this agent's ID)

    Returns:
        List of pending messages with id, from, message, priority, sent_at
    """
    recipient = agent_id or CCPM_AGENT_ID
    if recipient == "unknown":
        return {
            "success": False,
            "error": "Agent ID not configured or provided",
            "error_code": "CONFIG_ERROR"
        }

    messages = fetch_pending_piggyback_messages(recipient)
    return {
        "success": True,
        "agent_id": recipient,
        "message_count": len(messages),
        "messages": messages
    }


@mcp.tool()
def piggyback_acknowledge_message(message_id: int) -> dict:
    """
    Mark a piggyback message as read/acknowledged.

    Args:
        message_id: ID of the message to acknowledge

    Returns:
        Confirmation status
    """
    try:
        with get_ccpm_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE piggyback_messages
                    SET read_at = NOW()
                    WHERE id = %s AND read_at IS NULL
                    RETURNING id
                """, (message_id,))
                row = cur.fetchone()
                conn.commit()

                if row:
                    return {
                        "success": True,
                        "message_id": message_id,
                        "status": "acknowledged"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Message not found or already acknowledged",
                        "error_code": "NOT_FOUND"
                    }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "DB_ERROR"
        }


@mcp.tool()
def piggyback_list_sent_messages(limit: int = 20) -> dict:
    """
    List messages sent by this agent.

    Args:
        limit: Maximum number of messages to return (default: 20)

    Returns:
        List of sent messages with delivery status
    """
    sender = CCPM_AGENT_ID
    if sender == "unknown":
        return {
            "success": False,
            "error": "CCPM_AGENT_ID not configured",
            "error_code": "CONFIG_ERROR"
        }

    try:
        with get_ccpm_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, recipient, content, priority, created_at,
                           delivered_at, read_at
                    FROM piggyback_messages
                    WHERE sender = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (sender, limit))
                rows = cur.fetchall()

                messages = [
                    {
                        "id": row["id"],
                        "to": row["recipient"],
                        "message": row["content"],
                        "priority": row["priority"],
                        "sent_at": row["created_at"].isoformat() if row["created_at"] else None,
                        "delivered_at": row["delivered_at"].isoformat() if row["delivered_at"] else None,
                        "read_at": row["read_at"].isoformat() if row["read_at"] else None,
                        "status": "read" if row["read_at"] else ("delivered" if row["delivered_at"] else "pending")
                    }
                    for row in rows
                ]

                return {
                    "success": True,
                    "sender": sender,
                    "count": len(messages),
                    "messages": messages
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "DB_ERROR"
        }


# ==================== Completion Signaling ====================

# V2-Master UUID for completion notifications
V2_MASTER_UUID = "4c714f40-d15c-4f0e-bb34-410f2e7e1806"


@mcp.tool()
def ccpm_signal_completion(
    agent_tag: str,
    task_id: str,
    description: str
) -> dict:
    """
    Signal task completion to V2-Master. Updates task status and sends notification.

    Args:
        agent_tag: WHO tag e.g. "[NEX-Backend]", "[V2-Frontend]", "[HomeLab]"
        task_id: Task UUID
        description: Brief description of completed work

    Returns:
        Result with task update and message status
    """
    results = {
        "task_update": None,
        "message_sent": None,
        "success": False
    }

    # Step 1: Update task status to 'review'
    try:
        task_response = httpx.put(
            f"{CCPM_TASK_API}/tasks/{task_id}",
            json={"status": "review"},
            timeout=10.0
        )
        task_response.raise_for_status()
        results["task_update"] = {"success": True, "status": "review"}
    except httpx.HTTPStatusError as e:
        results["task_update"] = {
            "success": False,
            "error": f"API error: {e.response.status_code}"
        }
    except Exception as e:
        results["task_update"] = {"success": False, "error": str(e)}

    # Step 2: Send completion_signal message to V2-Master
    try:
        from_agent = CCPM_AGENT_ID
        if not from_agent:
            results["message_sent"] = {
                "success": False,
                "error": "CCPM_AGENT_ID not set"
            }
        else:
            msg_payload = {
                "to_agent_id": V2_MASTER_UUID,
                "message_type": "completion_signal",
                "subject": f"{agent_tag} Task Complete: {description}",
                "body": f"Task {task_id} completed by {agent_tag}.\n\nDescription: {description}",
                "priority": "normal",
                "context": {"task_id": task_id}
            }

            msg_response = httpx.post(
                f"{CCPM_MESSAGING_API}/agent-messages?from_agent_id={from_agent}",
                json=msg_payload,
                timeout=10.0
            )
            msg_response.raise_for_status()
            msg_data = msg_response.json()
            results["message_sent"] = {
                "success": True,
                "message_id": msg_data.get("id")
            }
    except httpx.HTTPStatusError as e:
        results["message_sent"] = {
            "success": False,
            "error": f"API error: {e.response.status_code}"
        }
    except Exception as e:
        results["message_sent"] = {"success": False, "error": str(e)}

    # Overall success if both operations succeeded
    results["success"] = (
        results["task_update"] and results["task_update"].get("success") and
        results["message_sent"] and results["message_sent"].get("success")
    )

    return results


# ==================== Lessons Learned System ====================

# Lessons API endpoints use the same base URL as messaging
# Base: http://10.0.1.210:8000/api/v1/lessons

@mcp.tool()
def ccpm_list_lessons(
    severity: str = None,
    tags: str = None,
    category: str = None
) -> dict:
    """
    List lessons from the CCPM Lessons Learned system.

    Args:
        severity: Filter by severity (comma-separated: critical,high,medium,low)
        tags: Filter by tags (comma-separated)
        category: Filter by category (solution, principle, error, pattern)

    Returns:
        List of lessons with their details
    """
    try:
        params = {}
        if severity:
            params["severity"] = severity
        if tags:
            params["tags"] = tags
        if category:
            params["category"] = category

        response = httpx.get(
            f"{CCPM_MESSAGING_API}/lessons",
            params=params,
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        # Handle both list and paginated response formats
        lessons = data if isinstance(data, list) else data.get("items", data.get("lessons", []))

        return {
            "success": True,
            "count": len(lessons),
            "lessons": lessons
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_get_lesson(lesson_id: str) -> dict:
    """
    Get detailed information about a specific lesson.

    Args:
        lesson_id: UUID of the lesson to retrieve

    Returns:
        Lesson details including title, description, category, severity, tags
    """
    try:
        response = httpx.get(
            f"{CCPM_MESSAGING_API}/lessons/{lesson_id}",
            timeout=10.0
        )
        response.raise_for_status()
        lesson = response.json()

        return {
            "success": True,
            "lesson": lesson
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "success": False,
                "error": f"Lesson {lesson_id} not found",
                "error_code": "NOT_FOUND"
            }
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_create_lesson(
    title: str,
    description: str,
    category: str,
    severity: str,
    tags: list[str] = None,
    source_type: str = "agent"
) -> dict:
    """
    Create a new lesson in the CCPM Lessons Learned system.

    Args:
        title: Brief descriptive title
        description: Detailed explanation with examples (include BAD and GOOD patterns)
        category: One of: solution, principle, error, pattern
        severity: One of: critical, high, medium, low
        tags: List of relevant tags for searchability
        source_type: Source type (default: agent)

    Returns:
        Created lesson with ID
    """
    # Validate category
    valid_categories = ["solution", "principle", "error", "pattern"]
    if category not in valid_categories:
        return {
            "success": False,
            "error": f"Invalid category. Must be one of: {', '.join(valid_categories)}",
            "error_code": "VALIDATION_ERROR"
        }

    # Validate severity
    valid_severities = ["critical", "high", "medium", "low"]
    if severity not in valid_severities:
        return {
            "success": False,
            "error": f"Invalid severity. Must be one of: {', '.join(valid_severities)}",
            "error_code": "VALIDATION_ERROR"
        }

    try:
        payload = {
            "title": title,
            "description": description,
            "category": category,
            "severity": severity,
            "source_type": source_type
        }
        if tags:
            payload["tags"] = tags

        response = httpx.post(
            f"{CCPM_MESSAGING_API}/lessons",
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        lesson = response.json()

        return {
            "success": True,
            "lesson_id": lesson.get("id"),
            "lesson": lesson,
            "message": "Lesson created. Use ccpm_generate_lesson_statuses to notify all agents."
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "details": e.response.text if hasattr(e.response, 'text') else None,
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_get_my_lesson_status(
    agent_id: str = None,
    status: str = None
) -> dict:
    """
    Get lesson statuses for an agent. Shows which lessons are pending/acknowledged/implemented.

    Args:
        agent_id: Agent UUID (defaults to CCPM_AGENT_ID from environment)
        status: Filter by status (pending, acknowledged, implemented, rejected, not_applicable)

    Returns:
        List of agent-lesson status records
    """
    aid = agent_id or CCPM_AGENT_ID
    if aid == "unknown":
        return {
            "success": False,
            "error": "Agent ID not configured. Set CCPM_AGENT_ID or provide agent_id parameter.",
            "error_code": "CONFIG_ERROR"
        }

    try:
        params = {"agent_id": aid}
        if status:
            params["status"] = status

        response = httpx.get(
            f"{CCPM_MESSAGING_API}/agent-lesson-status",
            params=params,
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        # Handle both list and paginated response formats
        statuses = data if isinstance(data, list) else data.get("items", data.get("statuses", []))

        return {
            "success": True,
            "agent_id": aid,
            "count": len(statuses),
            "statuses": statuses
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_acknowledge_lesson(
    lesson_id: str,
    agent_id: str = None,
    notes: str = None
) -> dict:
    """
    Acknowledge a lesson (mark as read and understood).

    Args:
        lesson_id: UUID of the lesson to acknowledge
        agent_id: Agent UUID (defaults to CCPM_AGENT_ID)
        notes: Optional notes about acknowledgment

    Returns:
        Updated or created status record
    """
    aid = agent_id or CCPM_AGENT_ID
    if aid == "unknown":
        return {
            "success": False,
            "error": "Agent ID not configured. Set CCPM_AGENT_ID or provide agent_id parameter.",
            "error_code": "CONFIG_ERROR"
        }

    try:
        # First check if status record exists
        check_response = httpx.get(
            f"{CCPM_MESSAGING_API}/agent-lesson-status",
            params={"agent_id": aid, "lesson_id": lesson_id},
            timeout=10.0
        )
        check_response.raise_for_status()
        check_data = check_response.json()
        existing = check_data if isinstance(check_data, list) else check_data.get("items", [])

        if existing and len(existing) > 0:
            # Update existing record
            status_id = existing[0].get("id")
            payload = {"status": "acknowledged"}
            if notes:
                payload["notes"] = notes

            response = httpx.put(
                f"{CCPM_MESSAGING_API}/agent-lesson-status/{status_id}",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "action": "updated",
                "status_id": status_id,
                "status": result
            }
        else:
            # Create new record
            payload = {
                "agent_id": aid,
                "lesson_id": lesson_id,
                "status": "acknowledged"
            }
            if notes:
                payload["notes"] = notes

            response = httpx.post(
                f"{CCPM_MESSAGING_API}/agent-lesson-status",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "action": "created",
                "status_id": result.get("id"),
                "status": result
            }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "details": e.response.text if hasattr(e.response, 'text') else None,
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_implement_lesson(
    lesson_id: str,
    agent_id: str = None,
    notes: str = None
) -> dict:
    """
    Mark a lesson as implemented (applied to work).

    Args:
        lesson_id: UUID of the lesson that was implemented
        agent_id: Agent UUID (defaults to CCPM_AGENT_ID)
        notes: Notes about how the lesson was applied

    Returns:
        Updated status record
    """
    aid = agent_id or CCPM_AGENT_ID
    if aid == "unknown":
        return {
            "success": False,
            "error": "Agent ID not configured. Set CCPM_AGENT_ID or provide agent_id parameter.",
            "error_code": "CONFIG_ERROR"
        }

    try:
        # Find existing status record
        check_response = httpx.get(
            f"{CCPM_MESSAGING_API}/agent-lesson-status",
            params={"agent_id": aid, "lesson_id": lesson_id},
            timeout=10.0
        )
        check_response.raise_for_status()
        check_data = check_response.json()
        existing = check_data if isinstance(check_data, list) else check_data.get("items", [])

        if existing and len(existing) > 0:
            # Update existing record
            status_id = existing[0].get("id")
            payload = {"status": "implemented"}
            if notes:
                payload["notes"] = notes

            response = httpx.put(
                f"{CCPM_MESSAGING_API}/agent-lesson-status/{status_id}",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "action": "updated",
                "status_id": status_id,
                "status": result
            }
        else:
            # Create new record with implemented status
            payload = {
                "agent_id": aid,
                "lesson_id": lesson_id,
                "status": "implemented"
            }
            if notes:
                payload["notes"] = notes

            response = httpx.post(
                f"{CCPM_MESSAGING_API}/agent-lesson-status",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "action": "created",
                "status_id": result.get("id"),
                "status": result
            }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "details": e.response.text if hasattr(e.response, 'text') else None,
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


@mcp.tool()
def ccpm_generate_lesson_statuses(lesson_id: str) -> dict:
    """
    Generate pending status records for all active agents for a new lesson.
    Call this after creating a new lesson to notify all agents.

    Args:
        lesson_id: UUID of the lesson to generate statuses for

    Returns:
        Number of status records created
    """
    try:
        response = httpx.post(
            f"{CCPM_MESSAGING_API}/agent-lesson-status/generate/lesson/{lesson_id}",
            timeout=10.0
        )
        response.raise_for_status()
        result = response.json()

        return {
            "success": True,
            "lesson_id": lesson_id,
            "result": result,
            "message": "Pending status records created for all active agents"
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "success": False,
                "error": f"Lesson {lesson_id} not found",
                "error_code": "NOT_FOUND"
            }
        return {
            "success": False,
            "error": f"API error: {e.response.status_code}",
            "details": e.response.text if hasattr(e.response, 'text') else None,
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED"
        }


# ==================== Run Server ====================

if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 8080))
    logger.info(f"Starting HomeLab MCP Server")
    logger.info(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    logger.info(f"CCPM Task API: {CCPM_TASK_API}")
    logger.info(f"CCPM Messaging API: {CCPM_MESSAGING_API}")
    logger.info(f"Listening on port {port}")
    mcp.run(transport="sse", port=port, host="0.0.0.0")
