# Energy Consumption Analysis - January 8, 2026

**Generated:** 2026-01-08 18:20 UTC
**Requested by:** User inquiry about Chapel circuit usage and overnight power cut

---

## Summary

### Power Cut Investigation
✅ **NO POWER CUT DETECTED**

- Continuous energy monitoring data from 00:00 to 18:20 UTC
- No gaps in sensor readings (gaps would indicate power loss)
- Main supply showed consistent 2.6-4.9 kW baseline throughout night
- UDM Pro: Online and operational
- Proxmox: Uptime 6h 36m (rebooted ~11:43 today - **not power-related**)

### Chapel Circuit Usage Today

| Circuit | Energy Today | Current Power | Status |
|---------|--------------|---------------|--------|
| **Chapel L3** | **10.30 kWh** | **~700W** | 🔥 **HIGH - AC Heating Office** |
| Chapel L1 | 5.33 kWh | ~200W | Normal |
| Chapel L2 | 0.69 kWh | ~50W | Low |

**Explanation:** User confirmed Chapel L3 high usage is due to AC system heating the office (feeling cold today).

---

## Detailed Analysis

### Chapel L3 - Office AC Heating

**Current Power Draw:** 680-715 W (as of 17:30-18:19 UTC)

Chapel L3 is consuming approximately **700 watts continuously** for office heating via AC system. This accounts for the elevated energy consumption:

- **10.3 kWh total today**
- At 700W constant: ~14.7 hours of operation
- Consistent high power draw throughout afternoon/evening

**Energy Cost Estimate** (assuming £0.25/kWh):
- Chapel L3 today: 10.3 kWh × £0.25 = **£2.58**
- Monthly (if sustained): ~£77

### Overall Energy Consumption Today

| Circuit | Energy (kWh) | % of Total | Rank |
|---------|--------------|------------|------|
| Studio | 11.42 | 30.2% | 1st |
| **Chapel L3** | **10.30** | **27.2%** | **2nd** |
| Chapel L1 | 5.33 | 14.1% | 3rd |
| Garden Flat | 4.39 | 11.6% | 4th |
| Cinema | 3.94 | 10.4% | 5th |
| Main House Lower | 2.35 | 6.2% | 6th |
| Main House Upper | 1.33 | 3.5% | 7th |
| Laundry | 0.89 | 2.4% | 8th |
| Chapel L2 | 0.69 | 1.8% | 9th |
| Balance | -2.10 | -5.5% | - |

**Total: 37.86 kWh**

### Overnight Power Consumption (Sample)

| Time (UTC) | Main Supply Power |
|------------|-------------------|
| 00:01 | 4,582 W |
| 00:15 | 3,564 W |
| 00:30 | 2,631 W |
| 01:00 | 2,769 W |
| 01:30 | 2,622 W |

Baseline overnight usage: **2.6-4.6 kW** (normal for property with heating, refrigeration, always-on equipment)

---

## Recommendations

### 1. Dedicated AC Energy Monitoring

**Problem:** Chapel L3 circuit includes both:
- Office AC system (high power when heating/cooling)
- Other office loads
- Cannot isolate AC consumption specifically

**Solutions:**

#### Option A: Split Circuit with Sub-Meter (Recommended)
- Install Emporia expansion module with CT clamps
- Add dedicated CT to AC supply line before it joins Chapel L3
- Cost: ~£40-60 for expansion + CT
- **Benefit:** Accurate AC-only monitoring without rewiring

#### Option B: Smart Plug with Energy Monitoring
- Install between AC unit and outlet
- Devices: Shelly Plug S, TP-Link Kasa, Sonoff POW
- Cost: £15-25 per unit
- **Limitation:** Only works if AC plugs into standard outlet

#### Option C: Dedicated Circuit Breaker
- Run separate breaker for AC from panel
- Install CT clamp on new circuit
- Cost: £100-200 (electrician required)
- **Benefit:** Permanent, professional solution

**Recommended Action:** Option A (Emporia expansion) - easiest to add to existing Vue system

### 2. Heating Efficiency

**Current Situation:**
- Using AC for heating in cold weather
- 700W continuous draw = 16.8 kWh/day if run 24/7
- £4.20/day or £126/month at current rate

**Alternatives to Consider:**
- Central heating (if available) - typically more efficient
- Oil-filled radiator - ~1500W but better heat retention
- Heat pump - more efficient but higher upfront cost
- Insulation improvements - reduce heat loss

**Note:** AC systems are generally **less efficient** for heating in cold weather (COP drops below 1.0 at low outdoor temps)

### 3. Energy Monitoring Dashboard

Current setup logs to:
- **Database:** homeassistant_thermal @ 10.0.1.251:5433
- **Retention:** 360 days
- **UI:** Home Assistant Energy Dashboard

**Enhancement Suggestions:**
1. Add Grafana dashboard for NAS database
2. Set up alerts for unusual consumption (>5kW on any circuit)
3. Create daily/weekly energy reports
4. Add cost tracking with tariff integration

### 4. Database Structure

Currently using Home Assistant's recorder (homeassistant_thermal database).

**New Energy Schema Created:**
- Location: `homelab_db.energy` @ 10.0.1.251:5433
- Purpose: Long-term analytics separate from HA
- Status: **Not yet populated** (pipeline needed)

**Future Enhancement:** Migrate to dedicated energy schema for:
- Custom analytics
- Multi-year trends
- Cost optimization analysis
- Load profiling

---

## Technical Notes

### Data Sources

1. **Home Assistant Emporia Vue Integration**
   - Integration: "Sunnybrae Energy" (Emporia Vue custom component v0.11.3)
   - Polling: Cloud-based (Emporia API)
   - Update Frequency: ~2 minutes
   - Circuits: 11 monitored

2. **Database Recording**
   - Primary: PostgreSQL (homeassistant_thermal @ NAS)
   - Fallback: SQLite (/config/home-assistant_v2.db on Pi)
   - Note: SQLite recorder appears to have stopped Jan 4th (unrelated to power)

3. **MCP Access**
   - Chapel energy sensors NOT exposed to voice assistant
   - Cannot query via Home Assistant MCP tool
   - Access via direct database queries or HA UI only

### Query Examples

```sql
-- Today's consumption by circuit
SELECT
    sm.entity_id,
    ROUND(s.state::numeric, 2) as energy_kwh,
    to_timestamp(s.last_updated_ts) as updated
FROM states s
JOIN states_meta sm ON s.metadata_id = sm.metadata_id
WHERE sm.entity_id LIKE '%energy_today%'
ORDER BY s.last_updated_ts DESC
LIMIT 11;

-- Chapel L3 power pattern
SELECT
    to_timestamp(last_updated_ts) as time,
    ROUND(s.state::numeric, 0) as power_watts
FROM states s
JOIN states_meta sm ON s.metadata_id = sm.metadata_id
WHERE sm.entity_id = 'sensor.chaple_l3_power_minute_average'
ORDER BY last_updated_ts DESC
LIMIT 50;
```

---

## Files Referenced

- Screenshot: `~/cc-share/"Home Assistant"/08-01-25-energy.png`
- Energy Schema: `infrastructure/database/schemas/energy_monitoring_schema.sql`
- HA Config: `docs/ha-configuration.md`
- Recorder Config: `thermal_recorder_postgresql.yaml` (on HA Pi5)

---

## Action Items

- [ ] Consider adding dedicated AC monitoring (Emporia expansion or smart plug)
- [ ] Evaluate heating alternatives for office
- [ ] Set up energy consumption alerts
- [ ] Expose Emporia entities to voice assistant for MCP access
- [ ] Optionally: Migrate to dedicated energy.* schema in homelab_db

---

*HomeLab Agent - Energy Analysis Report*
