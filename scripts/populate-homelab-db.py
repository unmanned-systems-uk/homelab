#!/usr/bin/env python3
"""
HomeLab Database Population Script
Populates homelab_db @ 10.0.1.251:5433 with infrastructure data
"""

import psycopg2
from datetime import datetime, timezone
import sys

# Database connection parameters
DB_CONFIG = {
    'host': '10.0.1.251',
    'port': 5433,
    'dbname': 'homelab_db',
    'user': 'homelab_app',
    'password': 'CHANGE_ME_APP_PASSWORD',
}

# Encryption key for credentials
ENCRYPTION_KEY = '8zB&Fwb!?WtPVP+1Z.C_+vAc.714%8Lg4OpyhKL"$,k]v@d4X)~/[%UHOW^IIl^V'

def connect_db():
    """Connect to the database and set encryption key"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=10)
        cur = conn.cursor()
        # Set encryption key for this session
        cur.execute(f"SET app.encryption_key = '{ENCRYPTION_KEY}'")
        conn.commit()
        print("✅ Connected to homelab_db @ 10.0.1.251:5433")
        return conn, cur
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def populate_infrastructure_devices(cur):
    """Phase 1: Populate infrastructure.devices"""
    print("\n=== Phase 1: Infrastructure Devices ===")

    devices = [
        # Network infrastructure
        ('UDM-Pro', 'physical', 'gateway', 'Ubiquiti', 'UniFi Dream Machine Pro',
         None, None, '10.0.1.1', 'Rack', '1U', 'online',
         '{"wan_ports": 2, "lan_ports": 8, "sfp_ports": 2, "management": "UniFi Network"}'),

        ('NAS-ccpm-nas', 'physical', 'nas', 'Synology', 'DS1621',
         None, None, '10.0.1.251', 'Rack', '4U', 'online',
         '{"bays": 6, "capacity_tb": 44, "raid": "SHR", "shares": ["CC-Share", "ccpm-database"]}'),

        # Compute infrastructure
        ('Proxmox-Host', 'physical', 'server', 'Custom', 'Proxmox VE Host',
         None, None, '10.0.1.200', 'Rack', '2U', 'online',
         '{"cpu": "AMD Ryzen", "ram_gb": 128, "storage_tb": 4, "role": "hypervisor"}'),

        ('Whisper-VM', 'vm', 'server', 'Proxmox', 'VM-100',
         None, None, '10.0.1.201', 'Proxmox', 'VM', 'online',
         '{"vcpu": 8, "ram_gb": 16, "disk_gb": 500, "gpu": "RTX 3090", "services": ["Ollama", "Whisper"]}'),

        ('Harbor-VM', 'vm', 'server', 'Proxmox', 'VM-101',
         None, None, '10.0.1.202', 'Proxmox', 'VM', 'online',
         '{"vcpu": 4, "ram_gb": 8, "disk_gb": 200, "services": ["Open WebUI", "MCP Server", "Portainer"]}'),

        ('CCPM-Server', 'vm', 'server', 'Proxmox', 'VM-102',
         None, None, '10.0.1.210', 'Proxmox', 'VM', 'online',
         '{"vcpu": 4, "ram_gb": 16, "disk_gb": 200, "services": ["CCPM V2", "Session Logging API"]}'),

        # Edge devices
        ('Pi5-DPM', 'physical', 'sbc', 'Raspberry Pi', 'Raspberry Pi 5',
         None, None, '10.0.1.53', 'Desk', None, 'online',
         '{"ram_gb": 8, "role": "development"}'),

        ('Jetson-Orin-NX', 'physical', 'sbc', 'NVIDIA', 'Jetson Orin NX',
         None, None, '10.0.1.113', 'Desk', None, 'online',
         '{"ram_gb": 16, "gpu": "Ampere", "role": "edge_ai"}'),

        # SCPI Test Equipment
        ('DMM-Keithley', 'physical', 'scpi', 'Keithley', 'DMM6500',
         None, None, '10.0.1.101', 'Bench', None, 'offline',
         '{"port": 5025, "type": "multimeter", "channels": 1}'),

        ('DC-Load-Rigol', 'physical', 'scpi', 'Rigol', 'DL3021A',
         None, None, '10.0.1.105', 'Bench', None, 'offline',
         '{"port": 5555, "type": "electronic_load", "max_power_w": 300}'),

        ('Scope-Rigol', 'physical', 'scpi', 'Rigol', 'MSO8204',
         None, None, '10.0.1.106', 'Bench', None, 'offline',
         '{"port": 5555, "type": "oscilloscope", "channels": 4, "bandwidth_mhz": 200}'),

        ('PSU-1-Rigol', 'physical', 'scpi', 'Rigol', 'DP932A',
         None, None, '10.0.1.111', 'Bench', None, 'offline',
         '{"port": 5025, "type": "power_supply", "channels": 3, "max_voltage_v": 30}'),

        ('AWG-Rigol', 'physical', 'scpi', 'Rigol', 'DG2052',
         None, None, '10.0.1.120', 'Bench', None, 'offline',
         '{"port": 5555, "type": "waveform_generator", "channels": 2, "max_freq_mhz": 50}'),

        ('PSU-2-Rigol', 'physical', 'scpi', 'Rigol', 'DP932A',
         None, None, '10.0.1.138', 'Bench', None, 'offline',
         '{"port": 5025, "type": "power_supply", "channels": 3, "max_voltage_v": 30}'),
    ]

    insert_sql = """
        INSERT INTO infrastructure.devices
        (device_name, device_type, category, manufacturer, model,
         serial_number, mac_address, primary_ip, location, rack_position,
         status, metadata, created_by, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
        ON CONFLICT (device_name) DO UPDATE SET
            device_type = EXCLUDED.device_type,
            category = EXCLUDED.category,
            primary_ip = EXCLUDED.primary_ip,
            status = EXCLUDED.status,
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        RETURNING device_id, device_name;
    """

    inserted = 0
    for device_data in devices:
        device_with_meta = device_data + ('homelab-agent', None)
        try:
            cur.execute(insert_sql, device_with_meta)
            device_id, device_name = cur.fetchone()
            print(f"  ✓ {device_name} ({device_id})")
            inserted += 1
        except Exception as e:
            print(f"  ✗ Failed to insert {device_data[0]}: {e}")

    print(f"\n✅ Inserted/Updated {inserted}/{len(devices)} devices")
    return inserted

def populate_networks(cur):
    """Phase 2: Populate network.networks"""
    print("\n=== Phase 2: Network VLANs ===")

    networks = [
        ('Default', None, '10.0.1.0/24', '10.0.1.1', 'corporate', True,
         '{"description": "Main network", "dhcp_range": "10.0.1.100-10.0.1.200"}'),

        ('Management', 10, '10.0.10.0/24', '10.0.10.1', 'management', True,
         '{"description": "Management network for infrastructure", "dhcp_range": "10.0.10.100-10.0.10.200"}'),

        ('Media', 20, '10.0.20.0/24', '10.0.20.1', 'corporate', True,
         '{"description": "Media streaming and storage", "dhcp_range": "10.0.20.100-10.0.20.200"}'),

        ('IoT', 30, '10.0.30.0/24', '10.0.30.1', 'iot', True,
         '{"description": "IoT devices and home automation", "dhcp_range": "10.0.30.100-10.0.30.200"}'),

        ('Lab', 50, '10.0.50.0/24', '10.0.50.1', 'management', True,
         '{"description": "Lab and testing network", "dhcp_range": "10.0.50.100-10.0.50.200"}'),
    ]

    insert_sql = """
        INSERT INTO network.networks
        (network_name, vlan_id, subnet, gateway, purpose, dhcp_enabled, metadata)
        VALUES (%s, %s, %s::cidr, %s::inet, %s, %s, %s::jsonb)
        ON CONFLICT (network_name) DO UPDATE SET
            subnet = EXCLUDED.subnet,
            gateway = EXCLUDED.gateway,
            dhcp_enabled = EXCLUDED.dhcp_enabled,
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        RETURNING network_id, network_name;
    """

    inserted = 0
    for network_data in networks:
        try:
            cur.execute(insert_sql, network_data)
            network_id, network_name = cur.fetchone()
            print(f"  ✓ {network_name} (VLAN {network_data[1] or 'untagged'}) - {network_data[2]}")
            inserted += 1
        except Exception as e:
            print(f"  ✗ Failed to insert {network_data[0]}: {e}")

    print(f"\n✅ Inserted/Updated {inserted}/{len(networks)} networks")
    return inserted

def populate_credentials(cur):
    """Phase 3: Populate encrypted credentials"""
    print("\n=== Phase 3: System Credentials (Encrypted) ===")
    print("  ✓ Permissions granted by database agent - proceeding with INSERT")

    credentials = [
        # NAS
        ('NAS-ccpm-nas', 'nas', 'homelab-agent', 'Homelab053210', None, None,
         '//10.0.1.251/CC-Share', 445, 'smb', 'CC-Share access'),

        # Proxmox - skipping, need password from user
        # ('Proxmox-Host', 'proxmox', 'root', 'ASK_USER', None, None,
        #  'https://10.0.1.200:8006', 8006, 'https', 'Proxmox VE management'),

        # UDM Pro
        ('UDM-Pro', 'unifi', 'HomeLab-Agent', 'HomeAdman2350', None, None,
         'https://10.0.1.1', 443, 'https', 'UniFi Network Controller'),

        # CCPM Server
        ('CCPM-Server', 'vm', 'ccpm', '053210', None, None,
         'ssh://10.0.1.210', 22, 'ssh', 'CCPM V2 server access'),

        # Database
        ('homelab_db', 'database', 'homelab_app', 'CHANGE_ME_APP_PASSWORD', None, None,
         'postgresql://10.0.1.251:5433/homelab_db', 5433, 'postgresql', 'HomeLab database'),
    ]

    insert_sql = """
        INSERT INTO credentials.system_credentials
        (system_name, system_type, username, password_encrypted, ssh_key, api_key_encrypted,
         access_url, port, protocol, notes)
        VALUES (%s, %s, %s, credentials.encrypt_password(%s), %s, %s, %s, %s, %s, %s)
        ON CONFLICT (system_name) DO UPDATE SET
            username = EXCLUDED.username,
            password_encrypted = credentials.encrypt_password(%s),
            access_url = EXCLUDED.access_url,
            updated_at = NOW()
        RETURNING credential_id, system_name;
    """

    inserted = 0
    for cred_data in credentials:
        # Add password again for UPDATE clause
        cred_data_with_update = cred_data + (cred_data[3],)

        try:
            cur.execute(insert_sql, cred_data_with_update)
            cred_id, system_name = cur.fetchone()
            print(f"  ✓ {system_name} ({cred_data[1]}) - {cred_data[2]}@{cred_data[6]}")
            inserted += 1
        except Exception as e:
            print(f"  ✗ Failed to insert {cred_data[0]}: {e}")

    print(f"\n✅ Inserted/Updated {inserted}/{len(credentials)} credentials")
    return inserted

def populate_scpi_equipment(cur):
    """Phase 4: Populate SCPI equipment"""
    print("\n=== Phase 4: SCPI Equipment ===")

    # Get SCPI device info from infrastructure.devices
    cur.execute("""
        SELECT device_id, device_name, primary_ip, metadata
        FROM infrastructure.devices
        WHERE category = 'scpi'
        ORDER BY device_name;
    """)

    scpi_devices = cur.fetchall()

    insert_sql = """
        INSERT INTO scpi.equipment
        (scpi_address, scpi_protocol, instrument_type, measurement_capabilities,
         max_voltage, max_current, max_power, channels, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        RETURNING equipment_id, scpi_address;
    """

    inserted = 0
    for device_id, device_name, ip, metadata_json in scpi_devices:
        metadata = metadata_json if metadata_json else {}

        equipment_type = metadata.get('type', 'unknown')
        port = metadata.get('port', 5025)
        channels = metadata.get('channels', 1)
        max_power = metadata.get('max_power_w', None)
        max_voltage = metadata.get('max_voltage_v', None)

        scpi_address = f"{ip}:{port}"

        # Determine capabilities based on type
        capabilities_map = {
            'multimeter': ['MEASURE:VOLTAGE:DC', 'MEASURE:CURRENT:DC', 'MEASURE:RESISTANCE'],
            'electronic_load': ['SOURCE:CURRENT', 'SOURCE:POWER', 'MEASURE:VOLTAGE'],
            'oscilloscope': ['MEASURE:VOLTAGE', 'ACQUIRE:WAVEFORM', 'TRIGGER'],
            'power_supply': ['SOURCE:VOLTAGE', 'SOURCE:CURRENT', 'OUTPUT'],
            'waveform_generator': ['SOURCE:FREQUENCY', 'SOURCE:FUNCTION', 'OUTPUT:WAVEFORM']
        }

        capabilities = capabilities_map.get(equipment_type, ['*IDN?'])

        import json
        equipment_data = (
            scpi_address, 'SCPI', equipment_type, capabilities,
            max_voltage, None, max_power, channels, json.dumps(metadata)
        )

        try:
            cur.execute(insert_sql, equipment_data)
            result = cur.fetchone()
            if result:
                eq_id, eq_addr = result
                print(f"  ✓ {device_name} ({equipment_type}) - {scpi_address}")
                inserted += 1
            else:
                print(f"  ⊘ {device_name} - already exists")
        except Exception as e:
            print(f"  ✗ Failed to insert {device_name}: {e}")

    print(f"\n✅ Inserted {inserted}/{len(scpi_devices)} SCPI devices")
    return inserted

def populate_proxmox_vms(cur):
    """Phase 5: Populate Proxmox VMs"""
    print("\n=== Phase 5: Proxmox VMs ===")

    # Get VM info from infrastructure.devices
    cur.execute("""
        SELECT device_name, metadata, primary_ip
        FROM infrastructure.devices
        WHERE device_type = 'vm'
        ORDER BY device_name;
    """)

    vms = cur.fetchall()

    insert_sql = """
        INSERT INTO virtualization.proxmox_vms
        (proxmox_vmid, proxmox_host, vm_type, cpu_cores, memory_mb,
         disk_size_gb, os_type, template, auto_start, backup_enabled,
         gpu_passthrough, gpu_device, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        RETURNING vm_id, proxmox_vmid;
    """

    inserted = 0
    vm_id_map = {'Whisper-VM': 100, 'Harbor-VM': 101, 'CCPM-Server': 102}

    for device_name, metadata_json, ip in vms:
        metadata = metadata_json if metadata_json else {}

        proxmox_vmid = vm_id_map.get(device_name, 999)
        vcpus = metadata.get('vcpu', 4)
        ram_gb = metadata.get('ram_gb', 8)
        disk_gb = metadata.get('disk_gb', 200)
        gpu = metadata.get('gpu', None)

        import json
        vm_data = (
            proxmox_vmid, 'pve', 'qemu', vcpus, ram_gb * 1024,
            disk_gb, 'linux', False, True, True,
            gpu is not None, gpu, json.dumps(metadata)
        )

        try:
            cur.execute(insert_sql, vm_data)
            result = cur.fetchone()
            if result:
                vm_id, vmid = result
                print(f"  ✓ VM {vmid} - {device_name} ({vcpus} vCPU, {ram_gb}GB RAM)")
                inserted += 1
            else:
                print(f"  ⊘ {device_name} - already exists")
        except Exception as e:
            print(f"  ✗ Failed to insert {device_name}: {e}")

    print(f"\n✅ Inserted {inserted}/{len(vms)} VMs")
    return inserted

def populate_ollama_models(cur):
    """Phase 6: Populate Ollama models"""
    print("\n=== Phase 6: Ollama AI Models ===")

    # Get Whisper VM device ID
    cur.execute("SELECT device_id FROM infrastructure.devices WHERE device_name = 'Whisper-VM'")
    result = cur.fetchone()
    if not result:
        print("  ⚠ Whisper-VM not found, skipping Ollama models")
        return 0

    whisper_device_id = result[0]

    models = [
        # (model_name, model_tag, base_model, size_bytes, parameter_count, quantization, purpose, notes)
        ('llama3:8b', 'latest', 'llama3', 4700000000, 8000000000, 'Q4_0',
         'General purpose language model',
         'Llama 3 8B parameter model from Meta'),

        ('claude-refiner', 'latest', 'llama3', 4700000000, 8000000000, 'Q4_0',
         'Claude prompt refinement',
         'Custom fine-tune for refining Claude API prompts'),

        ('requirements-agent', 'latest', 'llama3', 4700000000, 8000000000, 'Q4_0',
         'Requirements analysis',
         'Custom fine-tune for software requirements analysis'),

        ('mistral:7b', 'latest', 'mistral', 4100000000, 7000000000, 'Q4_0',
         'General purpose language model',
         'Mistral 7B parameter model from Mistral AI'),
    ]

    insert_sql = """
        INSERT INTO ai_ml.ollama_models
        (device_id, model_name, model_tag, base_model, size_bytes, parameter_count,
         quantization, purpose, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING model_id, model_name;
    """

    inserted = 0
    for model_data in models:
        full_data = (whisper_device_id,) + model_data
        try:
            cur.execute(insert_sql, full_data)
            result = cur.fetchone()
            if result:
                model_id, model_name = result
                print(f"  ✓ {model_name} ({model_data[2]}) - {model_data[4] / 1e9:.0f}B parameters, {model_data[3] / 1e9:.1f}GB")
                inserted += 1
            else:
                print(f"  ⊘ {model_data[0]} - already exists")
        except Exception as e:
            print(f"  ✗ Failed to insert {model_data[0]}: {e}")

    print(f"\n✅ Inserted {inserted}/{len(models)} Ollama models")
    return inserted

def verify_population(cur):
    """Verify all data was populated correctly"""
    print("\n=== Verification ===")

    checks = [
        ("Infrastructure Devices", "SELECT COUNT(*) FROM infrastructure.devices"),
        ("Network VLANs", "SELECT COUNT(*) FROM network.networks"),
        ("System Credentials", "SELECT COUNT(*) FROM credentials.system_credentials"),
        ("SCPI Equipment", "SELECT COUNT(*) FROM scpi.equipment"),
        ("Proxmox VMs", "SELECT COUNT(*) FROM virtualization.proxmox_vms"),
        ("Ollama Models", "SELECT COUNT(*) FROM ai_ml.ollama_models"),
    ]

    for check_name, sql in checks:
        cur.execute(sql)
        count = cur.fetchone()[0]
        print(f"  {check_name}: {count}")

    print("\n✅ Database population complete!")

def main():
    """Main execution"""
    print("=" * 60)
    print("HomeLab Database Population Script")
    print("=" * 60)

    conn, cur = connect_db()

    try:
        # Run all population phases
        populate_infrastructure_devices(cur)
        populate_networks(cur)
        populate_credentials(cur)  # Now has INSERT permissions
        populate_scpi_equipment(cur)
        populate_proxmox_vms(cur)
        populate_ollama_models(cur)

        # Commit all changes
        conn.commit()
        print("\n✅ All changes committed to database")

        # Verify
        verify_population(cur)

    except Exception as e:
        print(f"\n❌ Error during population: {e}")
        conn.rollback()
        print("⚠ All changes rolled back")
        raise

    finally:
        cur.close()
        conn.close()
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
