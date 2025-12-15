# Synology NAS Service Architecture & Capabilities

**Created:** 2025-12-15
**NAS:** ccpm-nas (10.0.1.251)
**DSM Version:** 7.3.1-86003
**Storage:** ~45TB
**Status:** Production (24/7 operation)

---

## Executive Summary

The Synology NAS is a critical infrastructure component with significant untapped potential. Current usage is limited to file storage and Proxmox backups, but the platform supports:

1. **Container Manager (Docker)** - Full Docker deployment capability
2. **Native MCP Server** - AI assistant integration for NAS management
3. **Database Hosting** - PostgreSQL for centralized CCPM database
4. **Application Packages** - DSM package ecosystem
5. **Service Hosting** - 24/7 availability for critical services

**Strategic Value:** Offload services from resource-constrained VMs (32GB total RAM) to dedicated NAS infrastructure with RAID protection and lower power consumption.

---

## Discovery: Synology MCP Servers

### Existing MCP Server Implementations

Two production-ready MCP servers exist for Synology NAS integration:

#### 1. mcp-server-synology (atom2ueki)

**Repository:** https://github.com/atom2ueki/mcp-server-synology

**Capabilities:**
- Secure authentication (RSA encrypted password transmission)
- File system operations (create, delete, list, search)
- Download Station management (torrents, downloads)
- Docker deployment support
- Auto-authentication
- AI assistant integration (Claude, Cursor, Continue)

**Tools Provided:**
- `login` - Authenticate with Synology NAS
- `logout` - Terminate session
- `list_folders` / `list_shares` - Directory browsing
- `get_file` - Read file contents
- `upload_file` - Upload files to NAS
- `download_file` - Download files from NAS
- `create_folder` - Create directories
- `delete_item` - Delete files/folders
- `move_item` / `rename_item` - File operations
- `search_files` - Search file system
- `create_share_link` - Generate sharing links
- `get_server_info` - Server status and quotas

**Compatibility:** DSM 6.0+

**Deployment:**
```bash
# Docker deployment
docker run -d \
  --name synology-mcp \
  -p 3000:3000 \
  -e SYNOLOGY_HOST=10.0.1.251 \
  -e SYNOLOGY_PORT=5000 \
  atom2ueki/mcp-server-synology
```

**Integration with Open WebUI:**
- Add as MCP server (Streamable HTTP)
- URL: http://synology-mcp:3000/sse
- Tools available in chat interface

---

#### 2. MCP-SynoLink (Do-Boo)

**Repository:** https://github.com/Do-Boo/MCP-SynoLink

**Capabilities:**
- Similar feature set to mcp-server-synology
- Emphasis on secure connection
- File operation focus
- DSM 6.0+ support

**Documentation:** https://skywork.ai/blog/mcp-synolink-synology-nas-ai-assistant-server/

---

## Container Manager (Docker) Capabilities

### Current Status
- ✅ Container Manager installed (Docker rebranded in DSM 7.2+)
- ✅ Full Docker CLI and Compose support
- ✅ GUI management via DSM interface
- ✅ Registry access (Docker Hub, private registries)

### Recommended Deployments

#### 1. PostgreSQL (Priority: HIGH)

**Purpose:** Centralized database for CCPM, Open WebUI, MCP servers

**Deployment:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:16
    container_name: ccpm-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ccpm
      POSTGRES_USER: ccpm
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - /volume1/docker/postgresql/data:/var/lib/postgresql/data
      - /volume1/docker/postgresql/backups:/backups
    networks:
      - homelab-net
```

**Storage:** /volume1/docker/postgresql (~500MB estimated, grows with usage)
**Network:** Accessible at 10.0.1.251:5432
**Backups:** Hyper Backup (daily automated)

**Migration Plan:**
1. Deploy PostgreSQL container
2. Export SQLite: `sqlite3 ccpm.db .dump > ccpm_export.sql`
3. Convert to PostgreSQL format
4. Import to PostgreSQL
5. Update CCPM connection string
6. Test Open WebUI multi-user access

---

#### 2. Private Container Registry (Priority: MEDIUM)

**Purpose:** Host private Docker images for HomeLab

**Deployment:**
```yaml
services:
  registry:
    image: registry:2
    container_name: homelab-registry
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY: /var/lib/registry
      REGISTRY_AUTH: htpasswd
      REGISTRY_AUTH_HTPASSWD_PATH: /auth/htpasswd
      REGISTRY_AUTH_HTPASSWD_REALM: HomeLab Registry
    volumes:
      - /volume1/docker/registry/data:/var/lib/registry
      - /volume1/docker/registry/auth:/auth
```

**Benefits:**
- Store custom CCPM images
- MCP server images
- No Docker Hub rate limits
- Faster pulls (local network)

**Usage:**
```bash
# Tag image for private registry
docker tag ccpm-server:latest 10.0.1.251:5000/ccpm-server:latest

# Push to registry
docker push 10.0.1.251:5000/ccpm-server:latest

# Pull from VMs
docker pull 10.0.1.251:5000/ccpm-server:latest
```

---

#### 3. Monitoring Stack (Priority: MEDIUM)

**Purpose:** Infrastructure visibility and alerting

**Deployment:**
```yaml
services:
  prometheus:
    image: prom/prometheus
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - /volume1/docker/prometheus/config:/etc/prometheus
      - /volume1/docker/prometheus/data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - /volume1/docker/grafana/data:/var/lib/grafana
    depends_on:
      - prometheus

  node_exporter:
    image: prom/node-exporter
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
```

**Monitored Resources:**
- NAS health (CPU, RAM, disk, network)
- VM status (via node_exporter on each VM)
- Container health
- CCPM server metrics
- PostgreSQL performance

**Dashboards:**
- System overview
- Container resource usage
- Database performance
- Network traffic

---

#### 4. Uptime Kuma (Priority: LOW)

**Purpose:** Service availability monitoring

**Deployment:**
```yaml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:latest
    container_name: uptime-kuma
    ports:
      - "3001:3001"
    volumes:
      - /volume1/docker/uptime-kuma:/app/data
    restart: unless-stopped
```

**Monitors:**
- CCPM server (http://localhost:8080/api/health)
- Open WebUI (https://10.0.1.202:3443)
- Whisper TTS (http://10.0.1.201:8000/health)
- Ollama API (http://10.0.1.201:11434)
- PostgreSQL (10.0.1.251:5432)

**Alerts:** Email, Discord, Slack notifications on downtime

---

#### 5. Homer Dashboard (Priority: LOW)

**Purpose:** Centralized HomeLab service dashboard

**Deployment:**
```yaml
services:
  homer:
    image: b4bz/homer
    container_name: homer
    ports:
      - "8080:8080"
    volumes:
      - /volume1/docker/homer/assets:/www/assets
    restart: unless-stopped
```

**Dashboard Services:**
- CCPM Server
- Open WebUI
- Grafana Dashboards
- Uptime Kuma
- PostgreSQL Admin
- Synology DSM

---

## DSM Native Packages

### Available Packages (DSM 7.3.1)

**Development:**
- Git Server - Version control hosting
- Node.js - JavaScript runtime
- Python - Python runtime (limited)
- MariaDB 10 - MySQL-compatible database (alternative to PostgreSQL)

**Productivity:**
- Synology Drive - File sync and collaboration
- Note Station - Note-taking platform
- Calendar - Shared calendars

**Utilities:**
- Docker (Container Manager) - Already installed
- Virtual Machine Manager - KVM hypervisor (if supported by model)
- Hyper Backup - Backup automation
- Snapshot Replication - ZFS-like snapshots (if supported)

**Multimedia:**
- Video Station - Media server
- Audio Station - Music streaming
- Photo Station - Photo management

**Network:**
- VPN Server - OpenVPN, L2TP/IPSec
- DNS Server - Internal DNS
- DHCP Server - Network management

---

## Resource Allocation

### NAS Specifications (Estimated)

**CPU:** Intel Celeron/Atom or AMD (model-specific)
**RAM:** Varies by model (typically 2-8GB expandable)
**Storage:** ~45TB across multiple drives (RAID configuration)
**Network:** Gigabit Ethernet (possibly 10GbE)

**Current Usage:**
- DSM operating system
- File sharing (SMB)
- Proxmox backup target
- Minimal load

**Available Capacity:**
- Docker containers (CPU/RAM dependent on model)
- Database hosting (PostgreSQL)
- Monitoring services
- MCP servers

**Recommendation:** Query NAS model number to determine exact CPU/RAM specs for capacity planning.

---

## Network Architecture

### Current Network

```
10.0.1.0/24 - HomeLab Network
├── 10.0.1.251 - Synology NAS (ccpm-nas.local)
├── 10.0.1.200 - Proxmox Host (pve-ai)
├── 10.0.1.201 - Whisper VM (TTS + Ollama)
└── 10.0.1.202 - Harbor VM (Open WebUI + Docker)
```

### Services Deployment Map

**Synology NAS (10.0.1.251):**
- PostgreSQL: 5432
- Private Registry: 5000
- Grafana: 3000
- Prometheus: 9090
- Uptime Kuma: 3001
- Homer Dashboard: 8080
- Synology MCP: 3002

**Harbor VM (10.0.1.202):**
- Open WebUI: 3443 (HTTPS)
- HomeLab MCP: 8080 (existing)
- CCPM MCP: 8081 (planned)

**Whisper VM (10.0.1.201):**
- Whisper TTS: 8000
- Ollama API: 11434
- Ollama Models: requirements-agent, claude-refiner, llama3:8b

---

## Security Considerations

### Access Control

**NAS Access:**
- DSM admin account (secure password)
- Container Manager access restricted
- SSH disabled (unless needed)
- Firewall rules (allow only HomeLab network)

**Database Security:**
- PostgreSQL password authentication
- Network access limited to 10.0.1.0/24
- Regular backups (daily automated)
- Connection encryption (SSL/TLS)

**Container Security:**
- Non-root containers where possible
- Read-only mounts for configs
- Resource limits (CPU/RAM caps)
- Regular image updates

**Network Security:**
- No external exposure (behind firewall)
- Internal network only (10.0.1.x)
- VPN required for remote access
- HTTPS for web interfaces

---

## Backup Strategy

### Hyper Backup Configuration

**PostgreSQL Backups:**
- Schedule: Daily at 2 AM
- Retention: 30 days
- Target: External USB drive or cloud (B2, S3)
- Test restoration: Monthly

**Container Configs:**
- Backup: /volume1/docker/ directory
- Version control: Git repository
- Frequency: After any config change

**DSM System:**
- System backup via Hyper Backup
- Configuration export: Monthly
- Update rollback: Snapshot before updates

---

## MCP Integration Strategy

### Phase 1: Synology NAS MCP Server

**Deploy Existing MCP Server:**

```bash
# On NAS (Container Manager)
docker run -d \
  --name synology-mcp \
  --network bridge \
  -p 3002:3000 \
  -e SYNOLOGY_HOST=localhost \
  -e SYNOLOGY_PORT=5000 \
  -e SYNOLOGY_HTTPS=false \
  atom2ueki/mcp-server-synology
```

**Configure in Open WebUI:**
1. Admin Settings → External Tools
2. Add MCP Server:
   - Name: Synology NAS Management
   - Type: MCP (Streamable HTTP)
   - Server URL: http://10.0.1.251:3002/sse
   - Description: File management, downloads, NAS operations

**Available Capabilities:**
- Ask AI to upload/download files to NAS
- Search NAS file system conversationally
- Manage Download Station tasks
- Create share links
- Check NAS status and quotas

---

### Phase 2: Custom HomeLab MCP Enhancement

**Extend HomeLab MCP Server with NAS Tools:**

```python
# In existing homelab_server.py
@mcp.tool()
def nas_get_container_status() -> list:
    """Get status of all Docker containers on NAS"""
    # Query Container Manager API

@mcp.tool()
def nas_deploy_service(service_name: str, config: dict) -> dict:
    """Deploy new Docker service on NAS"""
    # Use Docker API to deploy container

@mcp.tool()
def nas_backup_database(database: str) -> dict:
    """Trigger PostgreSQL backup on NAS"""
    # Execute pg_dump via Docker exec
```

**Integration:**
- Single MCP server for all HomeLab operations
- NAS management alongside VM management
- Unified conversational interface

---

## Deployment Roadmap

### Phase 1: Database Migration (Week 1-2)

**Tasks:**
1. Deploy PostgreSQL container on NAS
2. Configure backups (Hyper Backup)
3. Export CCPM SQLite database
4. Convert and import to PostgreSQL
5. Update CCPM connection string
6. Test Open WebUI multi-user access

**Success Criteria:**
- CCPM server connects to PostgreSQL on NAS
- All 120+ tables migrated successfully
- Open WebUI can access database
- Backups running daily

---

### Phase 2: Monitoring Stack (Week 3)

**Tasks:**
1. Deploy Prometheus + Grafana
2. Configure node exporters on VMs
3. Create dashboards (system, containers, DB)
4. Deploy Uptime Kuma
5. Configure alerts (email/Discord)

**Success Criteria:**
- Real-time infrastructure visibility
- Alerts on service downtime
- Historical metrics for capacity planning

---

### Phase 3: MCP Integration (Week 4)

**Tasks:**
1. Deploy Synology MCP server
2. Configure in Open WebUI
3. Test file operations via chat
4. Extend HomeLab MCP with NAS tools
5. Document conversational workflows

**Success Criteria:**
- AI can manage NAS files conversationally
- NAS status visible via MCP tools
- Integrated with existing MCP ecosystem

---

### Phase 4: Service Consolidation (Ongoing)

**Tasks:**
1. Deploy private container registry
2. Migrate select services from VMs to NAS
3. Optimize VM resource allocation
4. Deploy Homer dashboard
5. Performance tuning

**Success Criteria:**
- Reduced VM resource pressure
- Centralized container storage
- Improved service reliability

---

## Cost-Benefit Analysis

### Benefits

**Resource Efficiency:**
- Free up VM RAM (8-16GB freed by moving DB + monitoring)
- Reduce VM CPU load
- Better resource utilization (NAS underutilized)

**Reliability:**
- RAID protection for databases
- 24/7 NAS availability (already running)
- Automated backups (Hyper Backup)
- Lower failure risk (fewer VMs to maintain)

**Performance:**
- Local network access (NAS → VMs faster than VM → VM)
- SSD cache (if NAS has cache drive)
- Dedicated database server

**Operational:**
- Centralized management (DSM interface)
- Easier backups (one location)
- Simplified disaster recovery
- Lower power consumption (fewer VMs running)

---

### Costs

**Complexity:**
- More services to manage
- Network dependencies (NAS failure affects all VMs)
- Learning curve (DSM + Docker management)

**Performance Constraints:**
- NAS CPU/RAM limits (model-dependent)
- Shared storage bandwidth
- Potential bottleneck for high I/O workloads

**Security:**
- Larger attack surface (more services exposed)
- Single point of failure for critical services
- Need robust backup strategy

---

## Recommendations

### Immediate Actions (This Week)

1. **Query NAS Model Number**
   - Determine exact CPU/RAM specs
   - Verify Container Manager limits
   - Check for Virtual Machine Manager support

2. **Deploy PostgreSQL Container**
   - Start with database migration (highest value)
   - Test with CCPM in parallel (keep SQLite as fallback)
   - Monitor performance for 1 week

3. **Install Synology MCP Server**
   - Quick win for AI-NAS integration
   - Test conversational file management
   - Evaluate value before extending HomeLab MCP

---

### Medium-Term (Next Month)

4. **Deploy Monitoring Stack**
   - Prometheus + Grafana for visibility
   - Uptime Kuma for service alerts
   - Establish baseline metrics

5. **Private Registry Setup**
   - Store CCPM images locally
   - Host MCP server images
   - Reduce Docker Hub dependency

---

### Long-Term (Q1 2026)

6. **Service Consolidation**
   - Move non-GPU services to NAS
   - Optimize VM resource allocation
   - Evaluate VM count reduction (3 → 2?)

7. **Advanced Integration**
   - Extend HomeLab MCP with NAS tools
   - Automate deployments (GitOps)
   - CI/CD pipeline on NAS

---

## Questions for User

1. **NAS Model Number:** What is the exact Synology model? (e.g., DS920+, DS1621+, RS1221+)
   - Determines CPU/RAM capacity
   - Confirms Container Manager capabilities
   - Identifies upgrade paths

2. **Storage Configuration:** What RAID level is configured?
   - Affects available capacity
   - Performance characteristics
   - Redundancy level

3. **Network Speed:** Gigabit or 10 Gigabit Ethernet?
   - Impacts database performance
   - Affects container registry throughput
   - Important for high-bandwidth services

4. **Current Load:** What services are already running on NAS?
   - SMB/NFS file sharing
   - Synology packages (Photo Station, etc.)
   - Existing containers

5. **Backup Infrastructure:** Is external backup configured?
   - USB drive, cloud storage (B2, S3)?
   - Bandwidth available for backups
   - Budget for cloud storage

---

## References

**Synology MCP Servers:**
- [Synology MCP (atom2ueki)](https://github.com/atom2ueki/mcp-server-synology)
- [MCP-SynoLink (Do-Boo)](https://github.com/Do-Boo/MCP-SynoLink)
- [MCP Market - Synology](https://mcpmarket.com/server/synology)
- [Skywork AI Blog - MCP-SynoLink](https://skywork.ai/blog/mcp-synolink-synology-nas-ai-assistant-server/)

**Documentation:**
- Synology Container Manager Guide
- Docker on Synology Best Practices
- PostgreSQL on Synology Tutorial
- Hyper Backup Configuration

**Related HomeLab Documents:**
- `homelab-mcp-server-structure.md` - Current MCP server architecture
- `ccpm-ai-enhancement-plan.md` - CCPM AI enhancement strategy
- `hardware-inventory.md` - Equipment catalog

---

**Status:** Research Complete - Ready for Implementation Planning
**Next Steps:** Obtain NAS model number, deploy PostgreSQL, test Synology MCP server

