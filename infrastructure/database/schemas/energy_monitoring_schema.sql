-- Energy Monitoring Schema for homelab_db
-- Purpose: Track electricity consumption across all monitored circuits
-- Created: 2026-01-08

-- Create energy schema
CREATE SCHEMA IF NOT EXISTS energy;

-- ============================================================================
-- 1. ENERGY MONITORS (Devices like Emporia Vue)
-- ============================================================================

CREATE TABLE IF NOT EXISTS energy.monitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_name VARCHAR(100) NOT NULL UNIQUE,
    device_type VARCHAR(50) NOT NULL,  -- 'emporia_vue', 'shelly_em', etc.
    device_id VARCHAR(100),             -- Manufacturer device ID
    location VARCHAR(100),
    ha_entity_prefix VARCHAR(100),      -- Home Assistant entity prefix
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'offline')),
    firmware_version VARCHAR(50),
    installed_date DATE,
    metadata JSONB,                     -- Additional device-specific data
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE energy.monitors IS 'Energy monitoring devices (Emporia Vue, Shelly EM, etc.)';

-- ============================================================================
-- 2. CIRCUITS (Individual monitored circuits)
-- ============================================================================

CREATE TABLE IF NOT EXISTS energy.circuits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    monitor_id UUID NOT NULL REFERENCES energy.monitors(id) ON DELETE CASCADE,
    circuit_name VARCHAR(100) NOT NULL,
    circuit_number INTEGER,             -- Physical circuit number
    description TEXT,
    location VARCHAR(100),
    circuit_type VARCHAR(50),           -- 'single_phase', 'three_phase', 'main', 'branch'
    phase VARCHAR(10),                  -- 'L1', 'L2', 'L3', 'N' for three-phase systems
    rated_amperage INTEGER,             -- Circuit breaker rating
    ha_power_entity VARCHAR(200),       -- Home Assistant power sensor entity_id
    ha_energy_entity VARCHAR(200),      -- Home Assistant energy sensor entity_id
    alert_threshold_watts NUMERIC(10,2), -- Alert if power exceeds this
    alert_threshold_kwh_daily NUMERIC(10,3), -- Alert if daily usage exceeds this
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'disabled')),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(monitor_id, circuit_name)
);

COMMENT ON TABLE energy.circuits IS 'Individual monitored circuits/loads';

CREATE INDEX idx_circuits_monitor ON energy.circuits(monitor_id);
CREATE INDEX idx_circuits_phase ON energy.circuits(phase) WHERE phase IS NOT NULL;

-- ============================================================================
-- 3. POWER READINGS (Real-time power in watts)
-- ============================================================================

CREATE TABLE IF NOT EXISTS energy.power_readings (
    id BIGSERIAL,
    circuit_id UUID NOT NULL REFERENCES energy.circuits(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    power_watts NUMERIC(10,2) NOT NULL,
    voltage_volts NUMERIC(6,2),
    current_amps NUMERIC(8,3),
    power_factor NUMERIC(4,3),          -- Power factor (0.0 to 1.0)
    frequency_hz NUMERIC(5,2),
    metadata JSONB,                     -- Additional readings
    PRIMARY KEY (circuit_id, timestamp)
) PARTITION BY RANGE (timestamp);

COMMENT ON TABLE energy.power_readings IS 'Real-time power readings per circuit';

-- Create partitions for current and next month
CREATE TABLE IF NOT EXISTS energy.power_readings_2026_01
    PARTITION OF energy.power_readings
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE IF NOT EXISTS energy.power_readings_2026_02
    PARTITION OF energy.power_readings
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE INDEX idx_power_readings_timestamp ON energy.power_readings(timestamp DESC);
CREATE INDEX idx_power_readings_circuit_time ON energy.power_readings(circuit_id, timestamp DESC);

-- ============================================================================
-- 4. ENERGY CONSUMPTION (Cumulative energy in kWh)
-- ============================================================================

CREATE TABLE IF NOT EXISTS energy.consumption (
    id BIGSERIAL,
    circuit_id UUID NOT NULL REFERENCES energy.circuits(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    energy_kwh NUMERIC(12,6) NOT NULL,  -- Cumulative energy reading
    energy_delta_kwh NUMERIC(10,6),     -- Change since last reading
    cost_estimate NUMERIC(10,2),        -- Estimated cost based on tariff
    metadata JSONB,
    PRIMARY KEY (circuit_id, timestamp)
) PARTITION BY RANGE (timestamp);

COMMENT ON TABLE energy.consumption IS 'Cumulative energy consumption readings';

-- Create partitions
CREATE TABLE IF NOT EXISTS energy.consumption_2026_01
    PARTITION OF energy.consumption
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE IF NOT EXISTS energy.consumption_2026_02
    PARTITION OF energy.consumption
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE INDEX idx_consumption_timestamp ON energy.consumption(timestamp DESC);
CREATE INDEX idx_consumption_circuit_time ON energy.consumption(circuit_id, timestamp DESC);

-- ============================================================================
-- 5. AGGREGATED STATISTICS (Pre-computed for fast queries)
-- ============================================================================

CREATE TABLE IF NOT EXISTS energy.hourly_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circuit_id UUID NOT NULL REFERENCES energy.circuits(id) ON DELETE CASCADE,
    hour_start TIMESTAMP NOT NULL,
    avg_power_watts NUMERIC(10,2),
    min_power_watts NUMERIC(10,2),
    max_power_watts NUMERIC(10,2),
    total_energy_kwh NUMERIC(10,6),
    cost_estimate NUMERIC(10,2),
    samples_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(circuit_id, hour_start)
);

CREATE INDEX idx_hourly_stats_circuit_time ON energy.hourly_stats(circuit_id, hour_start DESC);

CREATE TABLE IF NOT EXISTS energy.daily_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circuit_id UUID NOT NULL REFERENCES energy.circuits(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    avg_power_watts NUMERIC(10,2),
    min_power_watts NUMERIC(10,2),
    max_power_watts NUMERIC(10,2),
    peak_power_watts NUMERIC(10,2),
    peak_time TIMESTAMP,
    total_energy_kwh NUMERIC(10,6),
    cost_estimate NUMERIC(10,2),
    samples_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(circuit_id, date)
);

CREATE INDEX idx_daily_stats_circuit_date ON energy.daily_stats(circuit_id, date DESC);

-- ============================================================================
-- 6. ELECTRICITY TARIFFS (For cost calculations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS energy.tariffs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tariff_name VARCHAR(100) NOT NULL,
    supplier VARCHAR(100),
    rate_type VARCHAR(50) NOT NULL CHECK (rate_type IN ('flat', 'time_of_use', 'tiered')),
    base_rate_per_kwh NUMERIC(8,4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    effective_from DATE NOT NULL,
    effective_to DATE,
    metadata JSONB,                     -- ToU schedules, tier definitions, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE energy.tariffs IS 'Electricity pricing tariffs for cost calculations';

-- ============================================================================
-- 7. ALERTS (Energy consumption alerts)
-- ============================================================================

CREATE TABLE IF NOT EXISTS energy.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circuit_id UUID REFERENCES energy.circuits(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,    -- 'power_spike', 'daily_threshold', 'unusual_pattern'
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    message TEXT NOT NULL,
    triggered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    value NUMERIC(12,3),                -- The value that triggered the alert
    threshold NUMERIC(12,3),            -- The threshold that was exceeded
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alerts_circuit ON energy.alerts(circuit_id);
CREATE INDEX idx_alerts_triggered ON energy.alerts(triggered_at DESC);
CREATE INDEX idx_alerts_unresolved ON energy.alerts(resolved) WHERE NOT resolved;

-- ============================================================================
-- 8. UTILITY FUNCTIONS
-- ============================================================================

-- Function to get current power for a circuit
CREATE OR REPLACE FUNCTION energy.get_current_power(p_circuit_id UUID)
RETURNS NUMERIC AS $$
    SELECT power_watts
    FROM energy.power_readings
    WHERE circuit_id = p_circuit_id
    ORDER BY timestamp DESC
    LIMIT 1;
$$ LANGUAGE SQL STABLE;

-- Function to get daily consumption for a circuit
CREATE OR REPLACE FUNCTION energy.get_daily_consumption(p_circuit_id UUID, p_date DATE)
RETURNS NUMERIC AS $$
    SELECT total_energy_kwh
    FROM energy.daily_stats
    WHERE circuit_id = p_circuit_id
    AND date = p_date;
$$ LANGUAGE SQL STABLE;

-- Function to calculate energy cost
CREATE OR REPLACE FUNCTION energy.calculate_cost(p_kwh NUMERIC, p_tariff_id UUID)
RETURNS NUMERIC AS $$
    SELECT (p_kwh * base_rate_per_kwh)::NUMERIC(10,2)
    FROM energy.tariffs
    WHERE id = p_tariff_id
    AND CURRENT_DATE BETWEEN effective_from AND COALESCE(effective_to, '2099-12-31');
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 9. AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

CREATE OR REPLACE FUNCTION energy.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_monitors_timestamp
    BEFORE UPDATE ON energy.monitors
    FOR EACH ROW EXECUTE FUNCTION energy.update_timestamp();

CREATE TRIGGER update_circuits_timestamp
    BEFORE UPDATE ON energy.circuits
    FOR EACH ROW EXECUTE FUNCTION energy.update_timestamp();

CREATE TRIGGER update_tariffs_timestamp
    BEFORE UPDATE ON energy.tariffs
    FOR EACH ROW EXECUTE FUNCTION energy.update_timestamp();

-- ============================================================================
-- 10. VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Current power usage across all circuits
CREATE OR REPLACE VIEW energy.v_current_power AS
SELECT
    m.device_name AS monitor,
    c.circuit_name,
    c.phase,
    pr.power_watts,
    pr.voltage_volts,
    pr.current_amps,
    pr.timestamp AS last_reading
FROM energy.circuits c
JOIN energy.monitors m ON c.monitor_id = m.id
JOIN LATERAL (
    SELECT power_watts, voltage_volts, current_amps, timestamp
    FROM energy.power_readings
    WHERE circuit_id = c.id
    ORDER BY timestamp DESC
    LIMIT 1
) pr ON true
WHERE c.status = 'active' AND m.status = 'active';

-- Today's consumption by circuit
CREATE OR REPLACE VIEW energy.v_today_consumption AS
SELECT
    m.device_name AS monitor,
    c.circuit_name,
    c.phase,
    ds.total_energy_kwh,
    ds.avg_power_watts,
    ds.peak_power_watts,
    ds.peak_time,
    ds.cost_estimate
FROM energy.circuits c
JOIN energy.monitors m ON c.monitor_id = m.id
LEFT JOIN energy.daily_stats ds ON c.id = ds.circuit_id AND ds.date = CURRENT_DATE
WHERE c.status = 'active' AND m.status = 'active';

-- Active unresolved alerts
CREATE OR REPLACE VIEW energy.v_active_alerts AS
SELECT
    a.id,
    m.device_name AS monitor,
    c.circuit_name,
    a.alert_type,
    a.severity,
    a.message,
    a.value,
    a.threshold,
    a.triggered_at,
    EXTRACT(EPOCH FROM (NOW() - a.triggered_at))/3600 AS hours_active
FROM energy.alerts a
LEFT JOIN energy.circuits c ON a.circuit_id = c.id
LEFT JOIN energy.monitors m ON c.monitor_id = m.id
WHERE NOT a.resolved
ORDER BY a.triggered_at DESC;

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT USAGE ON SCHEMA energy TO ccpm;
GRANT ALL ON ALL TABLES IN SCHEMA energy TO ccpm;
GRANT ALL ON ALL SEQUENCES IN SCHEMA energy TO ccpm;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA energy TO ccpm;

-- ============================================================================
-- NOTES
-- ============================================================================

COMMENT ON SCHEMA energy IS 'Energy monitoring and electricity consumption tracking schema';

/*
USAGE EXAMPLES:

-- Insert a monitor (Emporia Vue)
INSERT INTO energy.monitors (device_name, device_type, location, ha_entity_prefix)
VALUES ('Emporia Vue', 'emporia_vue', 'Main Breaker Panel', 'sensor.emporia_vue');

-- Insert circuits
INSERT INTO energy.circuits (monitor_id, circuit_name, description, phase, ha_power_entity)
VALUES
    ('...uuid...', 'Chaple L1', 'Chapel Line 1', 'L1', 'sensor.emporia_vue_chaple_l1_power'),
    ('...uuid...', 'Chaple L2', 'Chapel Line 2', 'L2', 'sensor.emporia_vue_chaple_l2_power'),
    ('...uuid...', 'Chaple L3', 'Chapel Line 3', 'L3', 'sensor.emporia_vue_chaple_l3_power');

-- Log power reading
INSERT INTO energy.power_readings (circuit_id, power_watts, voltage_volts, current_amps)
VALUES ('...uuid...', 1250.5, 240.2, 5.21);

-- Check today's consumption
SELECT * FROM energy.v_today_consumption WHERE circuit_name LIKE 'Chaple%';

-- Get current power across all Chapel circuits
SELECT circuit_name, power_watts, last_reading
FROM energy.v_current_power
WHERE circuit_name LIKE 'Chaple%'
ORDER BY circuit_name;
*/
