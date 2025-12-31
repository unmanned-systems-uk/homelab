# HomeLab Infrastructure MCP Server

MCP server providing Claude Code agents access to HomeLab devices, credentials, services, SCPI equipment, and network configuration.

## Database

**PostgreSQL** database `homelab_db` hosted on NAS (10.0.1.251:5433).

### Schema Overview

| Schema | Tables | Purpose |
|--------|--------|---------|
| `infrastructure` | devices, services | All hardware devices and services |
| `scpi` | equipment, measurements | Test equipment with SCPI control |
| `network` | networks, firewall_rules | VLANs and firewall configuration |
| `credentials` | system_credentials | Encrypted credentials (audit logged) |
| `audit` | system_events | Security audit trail |

## Tools Available

| Tool | Description |
|------|-------------|
| `homelab_list_devices` | List all devices (filter by category/status/type) |
| `homelab_get_device` | Get device details by name or IP |
| `homelab_list_scpi_equipment` | List SCPI-enabled test equipment |
| `homelab_get_scpi_connection` | Get SCPI connection details for a device |
| `homelab_list_services` | List all services |
| `homelab_check_service_health` | Check service health endpoint |
| `homelab_list_networks` | List networks/VLANs |
| `homelab_list_firewall_rules` | List firewall rules |
| `homelab_lookup_ip` | Look up IP allocation |
| `homelab_get_credentials` | Get credentials (AUDIT LOGGED) |
| `homelab_infrastructure_summary` | Get infrastructure summary |

## Installation

### Prerequisites

- Docker Desktop with MCP Toolkit enabled
- Claude Desktop or compatible MCP client
- Network access to NAS (10.0.1.251:5433)

### Step 1: Build Docker Image

```bash
cd /home/homelab/HomeLab/mcp-servers/homelab-infra
docker build -t homelab-infra:latest .
```

### Step 2: Create Custom Catalog

Copy catalog to Docker MCP directory:

```bash
mkdir -p ~/.docker/mcp/catalogs
cp catalog.yaml ~/.docker/mcp/catalogs/homelab.yaml
```

### Step 3: Add to Registry

Edit `~/.docker/mcp/registry.yaml`:

```yaml
homelab-infra:
  catalog: homelab
  enabled: true
```

### Step 4: Configure Database Password

Set via Docker secrets or environment:

```bash
# In Docker Desktop MCP Toolkit UI:
# Add secret HOMELAB_DB_PASSWORD with database password
```

### Step 5: Restart Claude Desktop

The `homelab_*` tools should now appear in Claude Desktop.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOMELAB_DB_HOST` | 10.0.1.251 | PostgreSQL host |
| `HOMELAB_DB_PORT` | 5433 | PostgreSQL port |
| `HOMELAB_DB_NAME` | homelab_db | Database name |
| `HOMELAB_DB_USER` | ccpm | Database user |
| `HOMELAB_DB_PASSWORD` | - | Database password (required) |
| `HOMELAB_DB_KEY` | - | Encryption key for credentials (optional) |

## Usage Examples

### List Devices

```
Agent calls: homelab_list_devices(category="SCPI")
Returns: [{device_name: "DMM-Keithley", primary_ip: "10.0.1.101", status: "online", ...}, ...]
```

### Get SCPI Connection

```
Agent calls: homelab_get_scpi_connection(device_name="Load-DC")
Returns: {
  device: "Load-DC",
  model: "DL3021A",
  ip: "10.0.1.105",
  port: 5555,
  protocol: "SOCKET",
  type: "Electronic Load"
}
```

### Get Credentials

```
Agent calls: homelab_get_credentials(target="device:ccpm-nas")
Returns: {
  target: "device:ccpm-nas",
  name: "ccpm-nas",
  ip: "10.0.1.251",
  username: "admin",
  password: "***",
  auth_type: "password"
}
```

### Infrastructure Summary

```
Agent calls: homelab_infrastructure_summary()
Returns: {
  device_stats: [{category: "Compute", status: "online", count: 5}, ...],
  scpi_stats: [{status: "online", count: 2}, {status: "offline", count: 4}],
  service_count: 8,
  network_count: 4,
  online_devices: [{device_name: "UDM-Pro", primary_ip: "10.0.1.1"}, ...]
}
```

## Security

- All credential access is logged to `audit.system_events` table
- Credentials can be encrypted with Fernet (AES-128) using `HOMELAB_DB_KEY`
- Container runs as non-root user
- Database connection uses parameterized queries (SQL injection safe)

## Files

```
homelab-infra/
├── homelab_server.py     # MCP server with FastMCP (PostgreSQL)
├── database.py           # Database access layer
├── Dockerfile            # Container definition
├── catalog.yaml          # Docker MCP catalog
├── requirements.txt      # Python dependencies
├── infrastructure/db/    # Encryption module
└── README.md            # This file
```

## GitHub Issue

See [Issue #9](https://github.com/unmanned-systems-uk/homelab/issues/9) for full specification.
