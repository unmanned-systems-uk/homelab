-- HomeLab Equipment Inventory Database Schema
-- Version: 1.0
-- Created: 2025-12-13

-- ============================================================================
-- Main Equipment Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,        -- compute, networking, storage, test_equipment, dev_board, sdr, peripheral
    subcategory TEXT,              -- server, workstation, sbc, oscilloscope, power_supply, mcu, router, switch, etc.
    manufacturer TEXT,
    model TEXT,
    serial_number TEXT,
    firmware_version TEXT,

    -- Network/SCPI fields
    ip_address TEXT,               -- for networked equipment
    scpi_port INTEGER,             -- for SCPI-enabled test equipment (typically 5025)
    mac_address TEXT,

    -- Physical tracking
    location TEXT,                 -- physical location/room
    storage_bin TEXT,              -- for small components
    rack_position TEXT,            -- for rack-mounted equipment

    -- Compute specs (for compute category)
    cpu TEXT,
    ram TEXT,
    storage TEXT,
    gpu TEXT,
    os TEXT,

    -- Test equipment specs
    specifications TEXT,           -- JSON or text description of specs

    -- Lifecycle tracking
    purchase_date DATE,
    warranty_expiry DATE,
    calibration_due DATE,          -- for test equipment
    last_calibrated DATE,

    -- Status
    status TEXT DEFAULT 'active',  -- active, storage, broken, retired, not_accessible
    purpose TEXT,                  -- what it's used for
    notes TEXT,

    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_category ON equipment(category);
CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_equipment_ip ON equipment(ip_address);
CREATE INDEX idx_equipment_calibration ON equipment(calibration_due);

-- ============================================================================
-- MikroE Click Boards (high volume items, needs dedicated table)
-- ============================================================================
CREATE TABLE IF NOT EXISTS click_boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    part_number TEXT,              -- MIKROE-xxxx
    category TEXT,                 -- sensors, interface, wireless, display, motor, storage, etc.
    subcategory TEXT,              -- temperature, humidity, pressure, uart, spi, bluetooth, oled, etc.
    interface TEXT,                -- SPI, I2C, UART, GPIO, Analog, PWM, etc.
    voltage TEXT,                  -- 3.3V, 5V, 3.3V/5V
    quantity INTEGER DEFAULT 1,
    location TEXT,
    storage_bin TEXT,

    -- Compatibility info
    compatible_mikrobus TEXT,      -- yes/no
    compatible_boards TEXT,        -- JSON array of compatible dev boards

    -- Documentation
    datasheet_url TEXT,
    product_url TEXT,
    notes TEXT,

    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_click_category ON click_boards(category);
CREATE INDEX idx_click_interface ON click_boards(interface);

-- ============================================================================
-- Equipment Relationships
-- ============================================================================
CREATE TABLE IF NOT EXISTS equipment_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    child_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,   -- contains, connected_to, requires, powers, hosts, etc.
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_relations_parent ON equipment_relations(parent_id);
CREATE INDEX idx_relations_child ON equipment_relations(child_id);
CREATE INDEX idx_relations_type ON equipment_relations(relation_type);

-- ============================================================================
-- Equipment History (track changes, calibrations, repairs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS equipment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,      -- calibration, repair, firmware_update, location_change, status_change, etc.
    event_date DATE NOT NULL,
    performed_by TEXT,
    description TEXT,
    cost REAL,                     -- optional cost tracking
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_history_equipment ON equipment_history(equipment_id);
CREATE INDEX idx_history_date ON equipment_history(event_date);
CREATE INDEX idx_history_type ON equipment_history(event_type);

-- ============================================================================
-- Projects (link equipment to specific projects)
-- ============================================================================
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',  -- active, completed, archived
    start_date DATE,
    end_date DATE,
    github_repo TEXT,              -- optional GitHub repo link
    ccpm_project_id INTEGER,       -- link to CCPM if applicable
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Equipment-Project Assignments
-- ============================================================================
CREATE TABLE IF NOT EXISTS equipment_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    role TEXT,                     -- what role this equipment plays in the project
    assigned_date DATE DEFAULT (date('now')),
    returned_date DATE,            -- when equipment was returned from project
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(equipment_id, project_id, assigned_date)
);

CREATE INDEX idx_eq_projects_equipment ON equipment_projects(equipment_id);
CREATE INDEX idx_eq_projects_project ON equipment_projects(project_id);

-- ============================================================================
-- Network Topology (track network connections)
-- ============================================================================
CREATE TABLE IF NOT EXISTS network_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    to_equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    connection_type TEXT,          -- ethernet, wifi, usb, serial, etc.
    port_from TEXT,                -- port on source device
    port_to TEXT,                  -- port on destination device
    vlan_id INTEGER,               -- VLAN if applicable
    speed TEXT,                    -- 1Gbps, 10Gbps, etc.
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_net_from ON network_connections(from_equipment_id);
CREATE INDEX idx_net_to ON network_connections(to_equipment_id);

-- ============================================================================
-- Calibration Schedule (for test equipment)
-- ============================================================================
CREATE TABLE IF NOT EXISTS calibration_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    interval_months INTEGER NOT NULL,  -- calibration interval in months
    last_calibration DATE,
    next_calibration DATE NOT NULL,
    calibration_provider TEXT,     -- who performs calibrations
    cost_estimate REAL,
    auto_alert_days INTEGER DEFAULT 30,  -- alert X days before due
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cal_equipment ON calibration_schedule(equipment_id);
CREATE INDEX idx_cal_next ON calibration_schedule(next_calibration);

-- ============================================================================
-- Metadata Table (for database versioning and config)
-- ============================================================================
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial metadata
INSERT OR IGNORE INTO metadata (key, value) VALUES ('schema_version', '1.0');
INSERT OR IGNORE INTO metadata (key, value) VALUES ('created_date', date('now'));
INSERT OR IGNORE INTO metadata (key, value) VALUES ('last_import', NULL);

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- View: SCPI-enabled test equipment
CREATE VIEW IF NOT EXISTS view_scpi_equipment AS
SELECT
    id,
    name,
    manufacturer,
    model,
    ip_address,
    scpi_port,
    serial_number,
    firmware_version,
    status,
    calibration_due
FROM equipment
WHERE scpi_port IS NOT NULL
  AND status = 'active'
ORDER BY name;

-- View: Equipment needing calibration soon (within 60 days)
CREATE VIEW IF NOT EXISTS view_calibration_due AS
SELECT
    e.id,
    e.name,
    e.manufacturer,
    e.model,
    e.serial_number,
    e.calibration_due,
    e.last_calibrated,
    julianday(e.calibration_due) - julianday('now') as days_until_due
FROM equipment e
WHERE e.calibration_due IS NOT NULL
  AND e.calibration_due <= date('now', '+60 days')
  AND e.status = 'active'
ORDER BY e.calibration_due;

-- View: Network inventory (all networked equipment)
CREATE VIEW IF NOT EXISTS view_network_inventory AS
SELECT
    id,
    name,
    category,
    subcategory,
    manufacturer,
    model,
    ip_address,
    mac_address,
    status,
    location
FROM equipment
WHERE ip_address IS NOT NULL
  AND status IN ('active', 'storage')
ORDER BY ip_address;

-- View: Equipment with relationships
CREATE VIEW IF NOT EXISTS view_equipment_tree AS
SELECT
    p.name as parent_name,
    p.category as parent_category,
    er.relation_type,
    c.name as child_name,
    c.category as child_category,
    er.notes
FROM equipment_relations er
JOIN equipment p ON er.parent_id = p.id
JOIN equipment c ON er.child_id = c.id
ORDER BY p.name, er.relation_type, c.name;
