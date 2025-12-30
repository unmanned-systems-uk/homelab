# HomeLab PostgreSQL Database Schema

**Version:** 1.0.0
**Date:** 2025-12-30
**Purpose:** Comprehensive logging and state management for HomeLab infrastructure

---

## Overview

This database replaces the old SQLite database with a comprehensive PostgreSQL schema designed to log ALL homelab data including:
- Network infrastructure state and events
- SCPI equipment measurements and test results
- Proxmox VMs and container metrics
- Docker services and health checks
- Ollama model performance and usage
- Test execution results
- System events and alerts

---

## Design Principles

1. **Time-series optimized**: Partitioned tables for historical data
2. **Relational integrity**: Foreign keys and constraints
3. **Audit trail**: All changes logged with timestamps and actors
4. **Scalability**: Indexed for performance with large datasets
5. **Extensibility**: JSON columns for flexible metadata
6. **Security**: Encrypted credentials storage with access control

---

## Database Structure

### Schema Organization

```
homelab_db
├── infrastructure     # Core infrastructure tables
├── credentials        # Encrypted credentials and secrets
├── network           # Network state and events
├── scpi              # SCPI equipment and measurements
├── virtualization    # Proxmox, Docker, VMs
├── ai_ml             # Ollama, model performance
├── testing           # Test execution and results
└── audit             # Change tracking and events
```

---

## Core Infrastructure Tables

### 1. `infrastructure.devices`

**Purpose:** Master inventory of all physical and virtual devices

```sql
CREATE TABLE infrastructure.devices (
    device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_name VARCHAR(255) NOT NULL UNIQUE,
    device_type VARCHAR(50) NOT NULL, -- 'physical', 'vm', 'container', 'network'
    category VARCHAR(100), -- 'gateway', 'switch', 'ap', 'server', 'scpi', etc.
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    serial_number VARCHAR(255),
    mac_address MACADDR,
    primary_ip INET,
    location VARCHAR(255),
    rack_position VARCHAR(50),
    status VARCHAR(50) DEFAULT 'unknown', -- 'online', 'offline', 'maintenance', 'unknown'
    metadata JSONB, -- Flexible additional data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100),
    notes TEXT
);

CREATE INDEX idx_devices_type ON infrastructure.devices(device_type);
CREATE INDEX idx_devices_status ON infrastructure.devices(status);
CREATE INDEX idx_devices_primary_ip ON infrastructure.devices(primary_ip);
CREATE INDEX idx_devices_metadata ON infrastructure.devices USING GIN(metadata);
```

**Sample Data:**
- UDM Pro (10.0.1.1)
- Proxmox Host (10.0.1.200)
- Whisper VM (10.0.1.201)
- Harbor VM (10.0.1.202)
- All SCPI equipment
- All UniFi devices

---

### 2. `infrastructure.services`

**Purpose:** Catalog all software services running on devices

```sql
CREATE TABLE infrastructure.services (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES infrastructure.devices(device_id) ON DELETE CASCADE,
    service_name VARCHAR(255) NOT NULL,
    service_type VARCHAR(100), -- 'docker', 'systemd', 'vm', 'ollama_model'
    port INTEGER,
    protocol VARCHAR(20), -- 'http', 'https', 'tcp', 'udp', 'scpi'
    endpoint VARCHAR(500),
    health_check_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'unknown', -- 'running', 'stopped', 'error', 'unknown'
    auto_start BOOLEAN DEFAULT false,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_services_device ON infrastructure.services(device_id);
CREATE INDEX idx_services_type ON infrastructure.services(service_type);
CREATE INDEX idx_services_status ON infrastructure.services(status);
CREATE UNIQUE INDEX idx_services_device_name ON infrastructure.services(device_id, service_name);
```

**Sample Data:**
- Open WebUI (Harbor VM, port 3000/3443)
- Ollama (Whisper VM, port 11434)
- HomeLab MCP (Harbor VM, port 8080)
- Portainer (Harbor VM, port 9443)

---

## Credentials & Secrets Tables

### 3. `credentials.system_credentials`

**Purpose:** Secure storage of all HomeLab system credentials

**Security Features:**
- Passwords encrypted using pgcrypto
- Access restricted to homelab_admin role
- Audit trail for credential access
- Automatic password rotation tracking

```sql
-- Enable pgcrypto extension for encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE credentials.system_credentials (
    credential_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_name VARCHAR(255) NOT NULL UNIQUE,
    system_type VARCHAR(100) NOT NULL, -- 'nas', 'proxmox', 'vm', 'docker', 'unifi', 'scpi'
    device_id UUID REFERENCES infrastructure.devices(device_id) ON DELETE CASCADE,
    username VARCHAR(255) NOT NULL,
    password_encrypted BYTEA NOT NULL, -- Encrypted password
    ssh_key TEXT, -- SSH private key (if applicable)
    api_key_encrypted BYTEA, -- Encrypted API key
    access_url VARCHAR(500),
    port INTEGER,
    protocol VARCHAR(50), -- 'ssh', 'https', 'smb', 'scpi'
    additional_config JSONB, -- Additional connection parameters
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,
    rotation_required BOOLEAN DEFAULT false,
    rotation_date DATE,
    notes TEXT,
    CONSTRAINT valid_system_type CHECK (system_type IN ('nas', 'proxmox', 'vm', 'docker', 'unifi', 'scpi', 'database', 'service', 'other'))
);

CREATE INDEX idx_credentials_system_type ON credentials.system_credentials(system_type);
CREATE INDEX idx_credentials_device ON credentials.system_credentials(device_id);

-- Function to encrypt password
CREATE OR REPLACE FUNCTION credentials.encrypt_password(plain_password TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(plain_password, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to decrypt password (restricted access)
CREATE OR REPLACE FUNCTION credentials.decrypt_password(encrypted_password BYTEA)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(encrypted_password, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Insert initial credentials (examples - replace with actual secure values)
INSERT INTO credentials.system_credentials (system_name, system_type, username, password_encrypted, access_url, port, protocol) VALUES
('NAS-ccpm-nas', 'nas', 'homelab-agent', credentials.encrypt_password('Homelab053210'), '//10.0.1.251/CC-Share', 445, 'smb'),
('Proxmox-Host', 'proxmox', 'root', credentials.encrypt_password('[CURRENT_PASSWORD]'), 'https://10.0.1.200:8006', 8006, 'https'),
('UDM-Pro', 'unifi', 'HomeLab-Agent', credentials.encrypt_password('HomeAdman2350'), 'https://10.0.1.1', 443, 'https'),
('CCPM-Server', 'vm', 'ccpm', credentials.encrypt_password('053210'), 'ssh://10.0.1.210', 22, 'ssh');
```

**Sample Data to Store:**
- NAS (10.0.1.251): homelab-agent / Homelab053210
- Proxmox: root / [password]
- UDM Pro: HomeLab-Agent / HomeAdman2350
- CCPM Server (10.0.1.210): ccpm / 053210
- Whisper VM (10.0.1.201): ccpm / [password]
- Harbor VM (10.0.1.202): ccpm / [password]
- Docker registries: credentials
- SCPI equipment: any password-protected devices
- Database: PostgreSQL admin credentials

---

### 4. `credentials.credential_access_log`

**Purpose:** Audit trail for credential access

```sql
CREATE TABLE credentials.credential_access_log (
    log_id BIGSERIAL PRIMARY KEY,
    credential_id UUID REFERENCES credentials.system_credentials(credential_id) ON DELETE CASCADE,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accessed_by VARCHAR(100) NOT NULL,
    access_method VARCHAR(100), -- 'api', 'manual', 'automated_script'
    purpose TEXT,
    success BOOLEAN DEFAULT true,
    source_ip INET,
    metadata JSONB
);

CREATE INDEX idx_credential_access_timestamp ON credentials.credential_access_log(accessed_at DESC);
CREATE INDEX idx_credential_access_credential ON credentials.credential_access_log(credential_id);
```

---

### 5. `credentials.encryption_keys`

**Purpose:** Store encryption key metadata (NOT the keys themselves)

```sql
CREATE TABLE credentials.encryption_keys (
    key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_name VARCHAR(255) NOT NULL UNIQUE,
    key_type VARCHAR(50) NOT NULL, -- 'symmetric', 'asymmetric'
    algorithm VARCHAR(50), -- 'AES-256', 'RSA-2048'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    rotated_at TIMESTAMP WITH TIME ZONE,
    next_rotation_date DATE,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'rotated', 'deprecated'
    notes TEXT
);

-- NOTE: Actual encryption keys should be stored in environment variables
-- or external secret management systems (HashiCorp Vault, AWS Secrets Manager, etc.)
-- This table only tracks key metadata for auditing
```

---

## Network Tables

### 3. `network.networks`

**Purpose:** VLAN and subnet configuration

```sql
CREATE TABLE network.networks (
    network_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    network_name VARCHAR(255) NOT NULL UNIQUE,
    vlan_id INTEGER,
    subnet CIDR NOT NULL,
    gateway INET NOT NULL,
    dhcp_enabled BOOLEAN DEFAULT true,
    dhcp_start INET,
    dhcp_end INET,
    domain_name VARCHAR(255),
    dns_servers INET[],
    purpose VARCHAR(100), -- 'corporate', 'guest', 'iot', 'management'
    security_zone VARCHAR(100),
    igmp_snooping BOOLEAN DEFAULT false,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_networks_vlan ON network.networks(vlan_id);
CREATE INDEX idx_networks_purpose ON network.networks(purpose);
```

**Sample Data:**
- Default (10.0.1.0/24, no VLAN)
- Management (10.0.10.0/24, VLAN 10)
- Media (10.0.20.0/24, VLAN 20)
- IoT (10.0.30.0/24, VLAN 30)
- Lab (10.0.50.0/24, VLAN 50)

---

### 4. `network.device_network_assignments`

**Purpose:** Track which devices are on which networks

```sql
CREATE TABLE network.device_network_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES infrastructure.devices(device_id) ON DELETE CASCADE,
    network_id UUID REFERENCES network.networks(network_id) ON DELETE CASCADE,
    ip_address INET NOT NULL,
    is_static BOOLEAN DEFAULT true,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_device_network_device ON network.device_network_assignments(device_id);
CREATE INDEX idx_device_network_network ON network.device_network_assignments(network_id);
CREATE UNIQUE INDEX idx_device_network_unique ON network.device_network_assignments(device_id, network_id, ip_address);
```

---

### 5. `network.health_history`

**Purpose:** Time-series network health metrics (PARTITIONED)

```sql
CREATE TABLE network.health_history (
    measurement_id BIGSERIAL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    subsystem VARCHAR(50) NOT NULL, -- 'wan', 'wlan', 'lan', 'vpn'
    status VARCHAR(50), -- 'ok', 'warning', 'error'
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    metadata JSONB,
    PRIMARY KEY (measurement_id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions (example for 2025)
CREATE TABLE network.health_history_2025_12 PARTITION OF network.health_history
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE INDEX idx_health_timestamp ON network.health_history(timestamp DESC);
CREATE INDEX idx_health_subsystem ON network.health_history(subsystem);
```

---

### 6. `network.firewall_rules`

**Purpose:** Document all firewall rules and policies

```sql
CREATE TABLE network.firewall_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(255) NOT NULL,
    unifi_rule_id VARCHAR(255), -- External ID from UniFi
    enabled BOOLEAN DEFAULT true,
    action VARCHAR(50) NOT NULL, -- 'accept', 'drop', 'reject'
    protocol VARCHAR(20), -- 'tcp', 'udp', 'icmp', 'any'
    source_network VARCHAR(255),
    source_port VARCHAR(100),
    destination_network VARCHAR(255),
    destination_port VARCHAR(100),
    direction VARCHAR(20), -- 'in', 'out', 'both'
    ruleset VARCHAR(100), -- 'WAN_IN', 'LAN_LOCAL', etc.
    rule_index INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_firewall_enabled ON network.firewall_rules(enabled);
CREATE INDEX idx_firewall_ruleset ON network.firewall_rules(ruleset);
```

---

## SCPI Equipment Tables

### 7. `scpi.equipment`

**Purpose:** SCPI test equipment inventory (extends infrastructure.devices)

```sql
CREATE TABLE scpi.equipment (
    equipment_id UUID PRIMARY KEY REFERENCES infrastructure.devices(device_id) ON DELETE CASCADE,
    scpi_address VARCHAR(255) NOT NULL, -- e.g., "10.0.1.101:5025"
    scpi_protocol VARCHAR(50) DEFAULT 'SOCKET', -- 'SOCKET', 'VISA', 'USBTMC'
    instrument_type VARCHAR(100), -- 'DMM', 'SCOPE', 'PSU', 'LOAD', 'AWG'
    idn_response TEXT, -- Response to *IDN? query
    measurement_capabilities TEXT[],
    max_voltage NUMERIC,
    max_current NUMERIC,
    max_power NUMERIC,
    channels INTEGER DEFAULT 1,
    last_calibration_date DATE,
    calibration_due_date DATE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_scpi_type ON scpi.equipment(instrument_type);
```

---

### 8. `scpi.measurements`

**Purpose:** Time-series measurement data (PARTITIONED)

```sql
CREATE TABLE scpi.measurements (
    measurement_id BIGSERIAL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    equipment_id UUID REFERENCES scpi.equipment(equipment_id) ON DELETE CASCADE,
    test_session_id UUID REFERENCES testing.test_sessions(session_id), -- Optional FK
    measurement_type VARCHAR(100) NOT NULL, -- 'voltage', 'current', 'resistance', 'frequency'
    channel INTEGER DEFAULT 1,
    value NUMERIC NOT NULL,
    unit VARCHAR(50) NOT NULL, -- 'V', 'A', 'Ω', 'Hz', 'W'
    range_setting VARCHAR(50),
    integration_time NUMERIC,
    metadata JSONB,
    PRIMARY KEY (measurement_id, timestamp)
) PARTITION BY RANGE (timestamp);

CREATE TABLE scpi.measurements_2025_12 PARTITION OF scpi.measurements
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE INDEX idx_measurements_timestamp ON scpi.measurements(timestamp DESC);
CREATE INDEX idx_measurements_equipment ON scpi.measurements(equipment_id);
CREATE INDEX idx_measurements_type ON scpi.measurements(measurement_type);
```

---

### 9. `scpi.equipment_status_log`

**Purpose:** Track equipment online/offline status changes

```sql
CREATE TABLE scpi.equipment_status_log (
    log_id BIGSERIAL PRIMARY KEY,
    equipment_id UUID REFERENCES scpi.equipment(equipment_id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    previous_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL, -- 'online', 'offline', 'error'
    trigger_source VARCHAR(100), -- 'automated_scan', 'manual_check', 'test_script'
    error_message TEXT,
    metadata JSONB
);

CREATE INDEX idx_scpi_status_timestamp ON scpi.equipment_status_log(timestamp DESC);
CREATE INDEX idx_scpi_status_equipment ON scpi.equipment_status_log(equipment_id);
```

---

## Virtualization Tables

### 10. `virtualization.proxmox_vms`

**Purpose:** Proxmox VM inventory and configuration

```sql
CREATE TABLE virtualization.proxmox_vms (
    vm_id UUID PRIMARY KEY REFERENCES infrastructure.devices(device_id) ON DELETE CASCADE,
    proxmox_vmid INTEGER NOT NULL,
    proxmox_host VARCHAR(255) NOT NULL,
    vm_type VARCHAR(50), -- 'qemu', 'lxc'
    cpu_cores INTEGER,
    memory_mb INTEGER,
    disk_size_gb INTEGER,
    os_type VARCHAR(100),
    template BOOLEAN DEFAULT false,
    auto_start BOOLEAN DEFAULT false,
    backup_enabled BOOLEAN DEFAULT true,
    gpu_passthrough BOOLEAN DEFAULT false,
    gpu_device VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_proxmox_host ON virtualization.proxmox_vms(proxmox_host);
CREATE INDEX idx_proxmox_vmid ON virtualization.proxmox_vms(proxmox_vmid);
```

---

### 11. `virtualization.vm_metrics`

**Purpose:** VM resource usage metrics (PARTITIONED)

```sql
CREATE TABLE virtualization.vm_metrics (
    metric_id BIGSERIAL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    vm_id UUID REFERENCES virtualization.proxmox_vms(vm_id) ON DELETE CASCADE,
    cpu_usage_percent NUMERIC,
    memory_used_mb NUMERIC,
    disk_read_mbps NUMERIC,
    disk_write_mbps NUMERIC,
    network_rx_mbps NUMERIC,
    network_tx_mbps NUMERIC,
    uptime_seconds BIGINT,
    PRIMARY KEY (metric_id, timestamp)
) PARTITION BY RANGE (timestamp);

CREATE TABLE virtualization.vm_metrics_2025_12 PARTITION OF virtualization.vm_metrics
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE INDEX idx_vm_metrics_timestamp ON virtualization.vm_metrics(timestamp DESC);
CREATE INDEX idx_vm_metrics_vm ON virtualization.vm_metrics(vm_id);
```

---

### 12. `virtualization.docker_containers`

**Purpose:** Docker container inventory

```sql
CREATE TABLE virtualization.docker_containers (
    container_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID REFERENCES infrastructure.services(service_id) ON DELETE CASCADE,
    container_name VARCHAR(255) NOT NULL,
    image VARCHAR(500) NOT NULL,
    image_tag VARCHAR(100),
    container_hash VARCHAR(255),
    ports_mapping JSONB, -- [{"host": 3000, "container": 8080, "protocol": "tcp"}]
    volumes JSONB,
    environment JSONB,
    restart_policy VARCHAR(50),
    network_mode VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_containers_service ON virtualization.docker_containers(service_id);
```

---

## AI/ML Tables

### 13. `ai_ml.ollama_models`

**Purpose:** Ollama model registry

```sql
CREATE TABLE ai_ml.ollama_models (
    model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES infrastructure.devices(device_id) ON DELETE CASCADE,
    model_name VARCHAR(255) NOT NULL,
    model_tag VARCHAR(100) DEFAULT 'latest',
    base_model VARCHAR(255),
    size_bytes BIGINT,
    parameter_count BIGINT,
    quantization VARCHAR(50),
    purpose TEXT, -- 'general', 'code', 'requirements-extraction', 'json-translation'
    modelfile TEXT,
    system_prompt TEXT,
    temperature NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_ollama_device ON ai_ml.ollama_models(device_id);
CREATE UNIQUE INDEX idx_ollama_model_unique ON ai_ml.ollama_models(device_id, model_name, model_tag);
```

---

### 14. `ai_ml.model_inference_log`

**Purpose:** Track model usage and performance (PARTITIONED)

```sql
CREATE TABLE ai_ml.model_inference_log (
    inference_id BIGSERIAL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    model_id UUID REFERENCES ai_ml.ollama_models(model_id) ON DELETE CASCADE,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    inference_time_ms INTEGER,
    tokens_per_second NUMERIC,
    input_preview TEXT, -- First 500 chars of input
    output_preview TEXT, -- First 500 chars of output
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    metadata JSONB,
    PRIMARY KEY (inference_id, timestamp)
) PARTITION BY RANGE (timestamp);

CREATE TABLE ai_ml.model_inference_log_2025_12 PARTITION OF ai_ml.model_inference_log
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE INDEX idx_inference_timestamp ON ai_ml.model_inference_log(timestamp DESC);
CREATE INDEX idx_inference_model ON ai_ml.model_inference_log(model_id);
```

---

## Testing Tables

### 15. `testing.test_sessions`

**Purpose:** Track test execution sessions

```sql
CREATE TABLE testing.test_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_name VARCHAR(255),
    test_type VARCHAR(100), -- 'infrastructure', 'scpi_automated', 'integration', 'manual'
    trigger_source VARCHAR(100), -- 'automated', 'manual', 'ci_cd', 'scheduled'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    total_tests INTEGER,
    passed_tests INTEGER,
    failed_tests INTEGER,
    skipped_tests INTEGER,
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'failed', 'aborted'
    metadata JSONB,
    executed_by VARCHAR(100)
);

CREATE INDEX idx_test_sessions_started ON testing.test_sessions(started_at DESC);
CREATE INDEX idx_test_sessions_type ON testing.test_sessions(test_type);
CREATE INDEX idx_test_sessions_status ON testing.test_sessions(status);
```

---

### 16. `testing.test_results`

**Purpose:** Individual test results within sessions

```sql
CREATE TABLE testing.test_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES testing.test_sessions(session_id) ON DELETE CASCADE,
    test_name VARCHAR(255) NOT NULL,
    test_category VARCHAR(100), -- 'network', 'scpi', 'vm', 'service'
    device_id UUID REFERENCES infrastructure.devices(device_id) ON DELETE SET NULL,
    service_id UUID REFERENCES infrastructure.services(service_id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL, -- 'PASS', 'FAIL', 'SKIP'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    expected_result TEXT,
    actual_result TEXT,
    error_message TEXT,
    metadata JSONB
);

CREATE INDEX idx_test_results_session ON testing.test_results(session_id);
CREATE INDEX idx_test_results_status ON testing.test_results(status);
CREATE INDEX idx_test_results_device ON testing.test_results(device_id);
```

---

## Audit Tables

### 17. `audit.change_log`

**Purpose:** Audit trail for all database changes

```sql
CREATE TABLE audit.change_log (
    log_id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    table_name VARCHAR(255) NOT NULL,
    record_id UUID,
    operation VARCHAR(50) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    changed_by VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    change_reason TEXT
);

CREATE INDEX idx_change_log_timestamp ON audit.change_log(timestamp DESC);
CREATE INDEX idx_change_log_table ON audit.change_log(table_name);
CREATE INDEX idx_change_log_record ON audit.change_log(record_id);
```

---

### 18. `audit.system_events`

**Purpose:** System-level events and alerts (PARTITIONED)

```sql
CREATE TABLE audit.system_events (
    event_id BIGSERIAL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    event_type VARCHAR(100) NOT NULL, -- 'device_status', 'service_status', 'alert', 'maintenance'
    severity VARCHAR(50), -- 'info', 'warning', 'error', 'critical'
    source VARCHAR(255), -- 'homelab_agent', 'test_script', 'monitoring', 'manual'
    device_id UUID REFERENCES infrastructure.devices(device_id) ON DELETE SET NULL,
    service_id UUID REFERENCES infrastructure.services(service_id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    metadata JSONB,
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by VARCHAR(100),
    PRIMARY KEY (event_id, timestamp)
) PARTITION BY RANGE (timestamp);

CREATE TABLE audit.system_events_2025_12 PARTITION OF audit.system_events
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE INDEX idx_system_events_timestamp ON audit.system_events(timestamp DESC);
CREATE INDEX idx_system_events_type ON audit.system_events(event_type);
CREATE INDEX idx_system_events_severity ON audit.system_events(severity);
```

---

## Views

### 19. `view_device_summary`

**Purpose:** Quick overview of all devices and their status

```sql
CREATE VIEW view_device_summary AS
SELECT
    d.device_id,
    d.device_name,
    d.device_type,
    d.category,
    d.primary_ip,
    d.status,
    COUNT(DISTINCT s.service_id) as service_count,
    MAX(s.updated_at) as last_service_check,
    d.updated_at as last_device_update
FROM infrastructure.devices d
LEFT JOIN infrastructure.services s ON d.device_id = s.device_id
GROUP BY d.device_id, d.device_name, d.device_type, d.category,
         d.primary_ip, d.status, d.updated_at
ORDER BY d.device_name;
```

---

### 20. `view_network_topology`

**Purpose:** Complete network topology view

```sql
CREATE VIEW view_network_topology AS
SELECT
    n.network_name,
    n.vlan_id,
    n.subnet,
    n.gateway,
    n.purpose,
    COUNT(DISTINCT dna.device_id) as device_count,
    jsonb_agg(
        jsonb_build_object(
            'device_name', d.device_name,
            'ip_address', dna.ip_address,
            'status', d.status
        ) ORDER BY dna.ip_address
    ) as devices
FROM network.networks n
LEFT JOIN network.device_network_assignments dna ON n.network_id = dna.network_id
LEFT JOIN infrastructure.devices d ON dna.device_id = d.device_id
GROUP BY n.network_id, n.network_name, n.vlan_id, n.subnet, n.gateway, n.purpose
ORDER BY COALESCE(n.vlan_id, 0);
```

---

### 21. `view_test_history_summary`

**Purpose:** Test execution summary by day

```sql
CREATE VIEW view_test_history_summary AS
SELECT
    DATE(started_at) as test_date,
    test_type,
    COUNT(*) as session_count,
    SUM(total_tests) as total_tests,
    SUM(passed_tests) as total_passed,
    SUM(failed_tests) as total_failed,
    SUM(skipped_tests) as total_skipped,
    ROUND(AVG(duration_seconds), 2) as avg_duration_seconds
FROM testing.test_sessions
WHERE status = 'completed'
GROUP BY DATE(started_at), test_type
ORDER BY test_date DESC, test_type;
```

---

## Functions & Triggers

### Auto-update Timestamp Trigger

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON infrastructure.devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON infrastructure.services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Repeat for other tables...
```

---

### Device Status Change Logger

```sql
CREATE OR REPLACE FUNCTION log_device_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO audit.system_events (
            event_type, severity, source, device_id, title, description, metadata
        ) VALUES (
            'device_status',
            CASE
                WHEN NEW.status = 'offline' THEN 'warning'
                WHEN NEW.status = 'error' THEN 'error'
                ELSE 'info'
            END,
            'database_trigger',
            NEW.device_id,
            'Device status changed: ' || NEW.device_name,
            'Status changed from ' || COALESCE(OLD.status, 'unknown') || ' to ' || NEW.status,
            jsonb_build_object('old_status', OLD.status, 'new_status', NEW.status)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER device_status_change_trigger
AFTER UPDATE ON infrastructure.devices
FOR EACH ROW EXECUTE FUNCTION log_device_status_change();
```

---

## Indexes Strategy

### B-Tree Indexes
- Primary keys (auto-created)
- Foreign keys
- Status columns (for filtering)
- Timestamp columns (for sorting)

### GIN Indexes
- JSONB columns (metadata fields)
- Array columns
- Full-text search columns

### Partial Indexes
```sql
-- Only index active devices
CREATE INDEX idx_devices_active ON infrastructure.devices(status)
WHERE status = 'online';

-- Only index recent events
CREATE INDEX idx_events_recent ON audit.system_events(timestamp DESC)
WHERE timestamp > NOW() - INTERVAL '30 days';
```

---

## Partitioning Strategy

### Monthly Partitions (Time-series tables)
- `network.health_history`
- `scpi.measurements`
- `virtualization.vm_metrics`
- `ai_ml.model_inference_log`
- `audit.system_events`

### Automatic Partition Management
```sql
-- Function to create next month's partition
CREATE OR REPLACE FUNCTION create_next_month_partitions()
RETURNS void AS $$
DECLARE
    next_month DATE;
    following_month DATE;
    partition_name TEXT;
BEGIN
    next_month := DATE_TRUNC('month', NOW() + INTERVAL '1 month');
    following_month := next_month + INTERVAL '1 month';

    -- Create partitions for each time-series table
    partition_name := 'network.health_history_' || TO_CHAR(next_month, 'YYYY_MM');
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF network.health_history FOR VALUES FROM (%L) TO (%L)',
                   partition_name, next_month, following_month);

    -- Repeat for other partitioned tables...
END;
$$ LANGUAGE plpgsql;
```

---

## Migration from Old Database

### Data Migration Script Outline

```sql
-- 1. Migrate devices
INSERT INTO infrastructure.devices (device_name, device_type, primary_ip, metadata)
SELECT name, type, ip_address, metadata
FROM old_database.equipment;

-- 2. Migrate services
INSERT INTO infrastructure.services (device_id, service_name, port, endpoint)
SELECT d.device_id, s.name, s.port, s.endpoint
FROM old_database.services s
JOIN infrastructure.devices d ON s.equipment_id = d.legacy_id;

-- 3. Migrate historical data with time-based filtering
-- (Only recent data, archive old data separately)
```

---

## Backup & Maintenance

### Daily Backups
```bash
# Logical backup
pg_dump -Fc homelab_db > homelab_db_$(date +%Y%m%d).dump

# Partition-specific backup (for large time-series data)
pg_dump -Fc -t network.health_history_2025_12 homelab_db > health_2025_12.dump
```

### Partition Maintenance
```sql
-- Drop old partitions (after archiving)
DROP TABLE IF EXISTS network.health_history_2024_01;

-- Vacuum and analyze
VACUUM ANALYZE;
```

---

## Access Control

### Roles

```sql
-- Application role (read/write)
CREATE ROLE homelab_app WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE homelab_db TO homelab_app;
GRANT USAGE ON SCHEMA infrastructure, network, scpi, virtualization, ai_ml, testing, audit TO homelab_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA infrastructure, network, scpi, virtualization, ai_ml, testing, audit TO homelab_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA infrastructure, network, scpi, virtualization, ai_ml, testing, audit TO homelab_app;

-- Read-only role (reporting, dashboards)
CREATE ROLE homelab_readonly WITH LOGIN PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE homelab_db TO homelab_readonly;
GRANT USAGE ON SCHEMA infrastructure, network, scpi, virtualization, ai_ml, testing, audit TO homelab_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA infrastructure, network, scpi, virtualization, ai_ml, testing, audit TO homelab_readonly;

-- Admin role (full access)
CREATE ROLE homelab_admin WITH LOGIN PASSWORD 'admin_password' SUPERUSER;
```

---

## Performance Tuning

### Connection Pooling
Use PgBouncer for connection pooling:
```
[databases]
homelab_db = host=localhost port=5432 dbname=homelab_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
```

### Query Optimization
```sql
-- Analyze query plans
EXPLAIN ANALYZE SELECT * FROM view_device_summary WHERE status = 'online';

-- Optimize for common queries
CREATE MATERIALIZED VIEW mv_daily_test_summary AS
SELECT * FROM view_test_history_summary;

-- Refresh materialized view daily
CREATE OR REPLACE FUNCTION refresh_daily_summaries()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_daily_test_summary;
END;
$$ LANGUAGE plpgsql;
```

---

## Example Queries

### Current Infrastructure Status
```sql
SELECT
    device_type,
    status,
    COUNT(*) as count
FROM infrastructure.devices
GROUP BY device_type, status
ORDER BY device_type, status;
```

### SCPI Equipment Uptime
```sql
SELECT
    e.equipment_id,
    d.device_name,
    d.status,
    COUNT(CASE WHEN sl.new_status = 'online' THEN 1 END) as online_events,
    COUNT(CASE WHEN sl.new_status = 'offline' THEN 1 END) as offline_events,
    MAX(sl.timestamp) as last_status_change
FROM scpi.equipment e
JOIN infrastructure.devices d ON e.equipment_id = d.device_id
LEFT JOIN scpi.equipment_status_log sl ON e.equipment_id = sl.equipment_id
WHERE sl.timestamp > NOW() - INTERVAL '7 days'
GROUP BY e.equipment_id, d.device_name, d.status;
```

### Test Success Rate (Last 30 Days)
```sql
SELECT
    test_type,
    COUNT(*) as total_sessions,
    SUM(passed_tests) as total_passed,
    SUM(failed_tests) as total_failed,
    ROUND(100.0 * SUM(passed_tests) / NULLIF(SUM(total_tests), 0), 2) as success_rate_percent
FROM testing.test_sessions
WHERE started_at > NOW() - INTERVAL '30 days'
    AND status = 'completed'
GROUP BY test_type
ORDER BY test_type;
```

### Ollama Model Performance
```sql
SELECT
    m.model_name,
    COUNT(*) as inference_count,
    AVG(l.tokens_per_second) as avg_tokens_per_second,
    AVG(l.total_tokens) as avg_total_tokens,
    SUM(CASE WHEN l.success = false THEN 1 ELSE 0 END) as error_count
FROM ai_ml.model_inference_log l
JOIN ai_ml.ollama_models m ON l.model_id = m.model_id
WHERE l.timestamp > NOW() - INTERVAL '7 days'
GROUP BY m.model_id, m.model_name
ORDER BY inference_count DESC;
```

---

## Implementation Checklist

- [ ] Create database and schemas
- [ ] Create all tables in correct order (respect foreign keys)
- [ ] Create indexes
- [ ] Create views
- [ ] Create functions and triggers
- [ ] Create initial partitions (current month + next month)
- [ ] Create roles and grant permissions
- [ ] Migrate data from old database
- [ ] Test all views and queries
- [ ] Set up automated backups
- [ ] Set up partition management cron job
- [ ] Create database agent integration
- [ ] Document API endpoints for database access

---

**End of Schema Documentation**

This schema provides a comprehensive foundation for logging all HomeLab data. The database agent can now build this schema and create necessary migration scripts.
