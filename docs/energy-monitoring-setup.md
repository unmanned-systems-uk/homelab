# Energy Monitoring Setup

**Created:** 2026-01-08
**Status:** Database Ready - Integration Pending Configuration
**Priority:** HIGH - User requested ASAP implementation

---

## Summary

Energy consumption monitoring infrastructure has been created in `homelab_db`, but the Emporia Vue integration requires configuration in Home Assistant before data collection can begin.

---

## Current Status

### ✅ Completed

1. **Database Schema Created** - `energy` schema in `homelab_db` @ 10.0.1.251:5433
2. **Emporia Vue Monitor Registered** - Device record created in database
3. **11 Circuits Configured** - All circuits including Chapel L1/L2/L3 registered
4. **Custom Component Installed** - `emporia_vue` present in HA custom_components

### ❌ Pending

1. **Emporia Integration Configuration** - Needs login credentials in Home Assistant UI
2. **Entity Verification** - Confirm entities are being created
3. **Data Logging Pipeline** - Automated logging from HA to homelab_db
4. **Historical Data** - No data available until integration is active

---

## Hardware

### Emporia Vue Energy Monitor

| Property | Value |
|----------|-------|
| **Location** | Main Breaker Panel |
| **Host System** | Home Assistant (HA-Pi5 @ 10.0.1.150) |
| **Circuits Monitored** | 11 total |
| **Integration** | Custom Component @ `/config/custom_components/emporia_vue` |

### Monitored Circuits

| Circuit | Description | Phase | Alert Threshold |
|---------|-------------|-------|-----------------|
| Main Supply | 3-phase main supply | - | 15,000 W |
| Studio | Studio power | - | 3,000 W |
| **Chaple L1** | **Chapel Line 1** | **L1** | **5,000 W** |
| **Chaple L2** | **Chapel Line 2** | **L2** | **5,000 W** |
| **Chaple L3** | **Chapel Line 3** | **L3** | **5,000 W** |
| Cinema | Cinema room | - | 3,000 W |
| Garden Flat | Garden flat power | - | 3,000 W |
| Laundry | Laundry room | - | 3,000 W |
| Main House Upper | Main house upper floor | - | 5,000 W |
| Main House Lower | Main house lower floor | - | 5,000 W |
| Balance | Calculated balance | - | - |

---

## Database Schema

### Location
- **Database:** `homelab_db` @ 10.0.1.251:5433
- **Schema:** `energy`
- **Script:** `infrastructure/database/schemas/energy_monitoring_schema.sql`

### Tables

| Table | Purpose | Partitioned |
|-------|---------|-------------|
| `energy.monitors` | Energy monitoring devices | No |
| `energy.circuits` | Individual monitored circuits | No |
| `energy.power_readings` | Real-time power (W) | Yes (monthly) |
| `energy.consumption` | Cumulative energy (kWh) | Yes (monthly) |
| `energy.hourly_stats` | Aggregated hourly data | No |
| `energy.daily_stats` | Aggregated daily data | No |
| `energy.tariffs` | Electricity pricing | No |
| `energy.alerts` | Consumption alerts | No |

### Useful Views

```sql
-- Current power across all circuits
SELECT * FROM energy.v_current_power;

-- Today's consumption by circuit
SELECT * FROM energy.v_today_consumption;

-- Active alerts
SELECT * FROM energy.v_active_alerts;

-- Chapel circuits specifically
SELECT * FROM energy.v_current_power WHERE circuit_name LIKE 'Chaple%';
```

### Quick Queries

```sql
-- List all circuits
SELECT circuit_name, phase, alert_threshold_watts
FROM energy.circuits
WHERE status = 'active'
ORDER BY circuit_name;

-- Get Chapel circuit IDs (for data insertion)
SELECT id, circuit_name, phase, ha_power_entity
FROM energy.circuits
WHERE circuit_name LIKE 'Chaple%'
ORDER BY phase;
```

---

## Next Steps

### 1. Configure Emporia Vue in Home Assistant

**Priority:** CRITICAL - Required to start data collection

**Steps:**

1. Access Home Assistant UI: `http://10.0.1.150:8123`
2. Navigate to: **Settings > Devices & Services**
3. Find **Emporia Vue** integration (should be listed under custom components)
4. Click **Configure** and enter Emporia cloud credentials:
   - Email: (user's Emporia account email)
   - Password: (user's Emporia account password)
5. Verify all 11 circuits appear as entities

**Expected Entities:**

```
sensor.emporia_vue_chaple_l1_power
sensor.emporia_vue_chaple_l1_energy
sensor.emporia_vue_chaple_l2_power
sensor.emporia_vue_chaple_l2_energy
sensor.emporia_vue_chaple_l3_power
sensor.emporia_vue_chaple_l3_energy
... (and 8 other circuits)
```

### 2. Expose Entities to Voice Assistant

Once entities are confirmed:

1. **Settings > Voice Assistants > Assist**
2. Select **Exposed Entities**
3. Enable all Emporia power and energy sensors
4. This allows MCP integration to query them

### 3. Create Data Logging Pipeline

**Options:**

#### Option A: Home Assistant Automation (Recommended)
- Create automation to log readings every 5-15 minutes
- Use `shell_command` or custom Python script
- Write directly to `homelab_db` via PostgreSQL

#### Option B: Node-RED Flow
- Use Node-RED integration (already installed)
- Create flow: HA State Change → PostgreSQL node → homelab_db
- More visual and easier to debug

#### Option C: AppDaemon
- Python-based HA automation
- More complex but most powerful
- Direct database access with psycopg2

### 4. Set Up Alerting

Once data is flowing:

```sql
-- Create alert for Chapel L1 over 5kW
INSERT INTO energy.alerts (circuit_id, alert_type, severity, message, value, threshold)
SELECT
    id,
    'power_spike',
    'warning',
    'Chapel L1 power usage exceeds 5kW',
    5200.00,
    5000.00
FROM energy.circuits
WHERE circuit_name = 'Chaple L1';
```

---

## User's Original Request

> "Can you look at the energy consumption database and see if you can see any notable increase for today within the Chaple L1, L2 or L3"

### Current Answer

**No historical data is available yet** because the Emporia Vue integration has not been configured in Home Assistant. The hardware is installed and the database is ready, but the integration needs credentials to start collecting data.

### Once Configured

After configuration, you can query today's consumption with:

```sql
SELECT
    circuit_name,
    phase,
    total_energy_kwh,
    avg_power_watts,
    peak_power_watts,
    peak_time
FROM energy.v_today_consumption
WHERE circuit_name IN ('Chaple L1', 'Chaple L2', 'Chaple L3')
ORDER BY phase;
```

Or check for unusual spikes:

```sql
SELECT
    ds.date,
    c.circuit_name,
    ds.peak_power_watts,
    ds.peak_time,
    ds.total_energy_kwh
FROM energy.daily_stats ds
JOIN energy.circuits c ON ds.circuit_id = c.id
WHERE c.circuit_name IN ('Chaple L1', 'Chaple L2', 'Chaple L3')
    AND ds.date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY ds.date DESC, c.phase;
```

---

## Related Issues

- **GitHub Issue #34:** HA: Emporia Energy Monitor Integration
  - Status: OPEN
  - Blocking data collection
  - Requires Emporia cloud credentials

---

## Documentation References

- **Hardware:** `docs/hardware-inventory.md` - Line mentioning Emporia Vue (11 circuits)
- **HA Config:** `docs/ha-configuration.md` - Connection details and circuit list
- **Database QRC:** `docs/database-qrc.md` - Quick database reference
- **Schema:** `infrastructure/database/schemas/energy_monitoring_schema.sql`

---

## Quick Database Connection

```bash
# Interactive session
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d homelab_db

# Quick query
PGPASSWORD="CcpmDb2025Secure" psql -h 10.0.1.251 -p 5433 -U ccpm -d homelab_db -c "SELECT * FROM energy.circuits WHERE phase IS NOT NULL;"
```

---

## Contact

- **Integration Setup:** Requires user's Emporia cloud credentials
- **GitHub Issue:** #34 (HA: Emporia Energy Monitor Integration)
- **Agent:** HomeLab Agent

---

*Energy monitoring infrastructure ready - awaiting integration configuration*
