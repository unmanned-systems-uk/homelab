# HomeLab Infrastructure MCP Server

MCP server providing Claude Code agents access to HomeLab VMs, credentials, services, and network configuration.

## Tools Available

| Tool | Description |
|------|-------------|
| `homelab_list_vms` | List all virtual machines |
| `homelab_get_vm` | Get VM details by ID or name |
| `homelab_get_credentials` | Get credentials (AUDIT LOGGED) |
| `homelab_list_services` | List all services |
| `homelab_check_service_health` | Check service health endpoint |
| `homelab_list_hosts` | List Proxmox hosts |
| `homelab_get_host` | Get host details |
| `homelab_lookup_ip` | Look up IP allocation |

## Installation

### Prerequisites

- Docker Desktop with MCP Toolkit enabled
- Claude Desktop or compatible MCP client

### Step 1: Build Docker Image

```bash
cd /home/anthony/ccpm-workspace/HomeLab/mcp-servers/homelab-infra
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

### Step 4: Configure Encryption Key (Optional)

For credential decryption, set the encryption key as a Docker secret:

```bash
# In Docker Desktop MCP Toolkit UI:
# Add secret HOMELAB_DB_KEY with value from ~/.homelab/.db_key
```

### Step 5: Restart Claude Desktop

The `homelab_*` tools should now appear in Claude Desktop.

## Usage Examples

### List VMs

```
Agent calls: homelab_list_vms()
Returns: [{vm_id: 100, name: "whisper", status: "running", ...}, ...]
```

### Get Credentials

```
Agent calls: homelab_get_credentials(target="vm:100")
Returns: {
  target: "vm:100",
  name: "whisper",
  ip: "10.0.1.201",
  username: "ccpm",
  password: "***",
  ssh_key: "~/.ssh/id_ed25519"
}
```

### Check Service Health

```
Agent calls: homelab_check_service_health(service_name="piper-tts")
Returns: {
  service: "piper-tts",
  status: "healthy",
  response_time_ms: 45
}
```

## Security

- All credential access is logged to `audit_log` table
- Credentials are encrypted with Fernet (AES-128)
- Container runs as non-root user
- Database mounted read-only

## Files

```
homelab-infra/
├── homelab_server.py     # MCP server with FastMCP
├── Dockerfile            # Container definition
├── catalog.yaml          # Docker MCP catalog
├── requirements.txt      # Python dependencies
├── infrastructure/db/    # Encryption module (copied for build)
└── README.md            # This file
```

## GitHub Issue

See [Issue #9](https://github.com/unmanned-systems-uk/homelab/issues/9) for full specification.
