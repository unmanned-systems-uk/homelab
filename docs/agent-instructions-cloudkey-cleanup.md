# Agent Instructions: CloudKey DHCP Cleanup & Backup

**Task:** Clean up DHCP reservations on CloudKey Gen1 before UDM Pro migration
**Agent:** Claude Code CLI with UniFi MCP access
**Priority:** HIGH - Must complete before migration
**Estimated Time:** 30-60 minutes

---

## Overview

The current CloudKey has 213 DHCP static reservations, but only ~30% are active. We need to remove stale entries before creating a clean backup for UDM Pro migration.

**Goal:** Reduce from 213 → ~40-50 active reservations

---

## Phase 1: Analysis & Documentation

### Step 1.1: Export Current State (BEFORE any changes)

```
Task: Create safety backup of current DHCP reservations

Actions:
1. Use UniFi MCP to list all static DHCP clients
2. Save complete list to: docs/dhcp-reservations-before-cleanup.json
3. Create human-readable summary: docs/dhcp-reservations-before-cleanup.md
4. Commit both files to git

Output Format (markdown):
- Total count
- Group by IP range (10.0.1.x, 192.168.x.x, other)
- List: IP, MAC, Hostname, Last Seen, Status (online/offline)
```

### Step 1.2: Identify Stale Entries

```
Task: Categorize DHCP reservations for deletion

Categories to DELETE:

Category A: Old Subnet (192.168.x.x)
- Match: Any IP starting with "192.168"
- Reason: Deprecated subnet from previous config
- Expected count: ~20 entries

Category B: Deprecated Hardware
- Sky boxes (look for "sky" in hostname)
- Netgear devices (look for "netgear" in hostname/MAC)
- Old Dell servers (look for "dell" in hostname)
- Expected count: ~15 entries

Category C: IoT Devices (moving to VLAN 30)
- All Wiz bulbs (MACs: 98:77:d5, a8:bb:50, cc:40:85, 44:4f:8e, 6c:29:90)
- Google Nest devices (MAC: 14:c1:4e, cc:a7:c1)
- Ring Doorbell (MAC: 64:9a:63)
- Echo devices (MAC: fc:d7:49)
- Emporia (MAC: 34:94:54)
- Nixplay (MAC: c0:e7:bf)
- ESP devices (MAC: 18:de:50)
- Sonos (MAC: 00:0e:58)
- Samsung TV (MAC: fc:03:9f)
- Onkyo (MAC: 00:09:b0)
- Expected count: ~28 entries

Category D: Offline/Stale (not seen in 90+ days)
- Check last_seen timestamp
- Exclude from critical list (see Step 1.3)
- Expected count: ~50+ entries

Create file: docs/dhcp-cleanup-plan.md
List all entries to delete by category
```

### Step 1.3: Identify CRITICAL Entries to KEEP

```
Task: Mark entries that MUST NOT be deleted

CRITICAL Infrastructure (DO NOT DELETE):
- 10.0.1.2 - UniFi CloudKey (MAC: 78:8a:20:df:04:77)
- 10.0.1.251 - Synology NAS (MAC: 90:09:d0:11:b4:b3)
- 10.0.1.200 - Proxmox (MAC: 40:16:7e:a5:0d:51)
- 10.0.1.210 - ubuntu-server/CCPM (MAC: bc:24:11:59:92:15)
- 10.0.1.159 - MCP Container (MAC: bc:24:11:2d:4a:b8)
- 10.0.1.40 - Gaming Server (MAC: 50:eb:f6:82:3e:92)

SCPI Test Equipment (DO NOT DELETE):
- 10.0.1.101 - Keithley DMM6500 (MAC: 08:00:11:23:73:27)
- 10.0.1.105 - Rigol DL3021A (MAC: 00:19:af:73:09:bc)
- 10.0.1.106 - Rigol MSO8204 (MAC: 00:19:af:7e:05:5b)
- 10.0.1.111 - Rigol DP932A-1 (MAC: 00:19:af:93:06:46)
- 10.0.1.112 - Rigol DP832A (MAC: 00:19:af:5b:b4:23)
- 10.0.1.120 - Rigol DG2052 (MAC: 00:19:af:8a:00:3e)
- 10.0.1.138 - Rigol DP932A-2 (MAC: 00:19:af:93:04:f5)

Development Hardware (DO NOT DELETE):
- 10.0.1.83 - DEV-PC-Ubuntu (MAC: d8:bb:c1:9a:e1:0c)
- 10.0.1.37 - Dev-Office-PC-1 (MAC: 70:4d:7b:62:a0:de)
- 10.0.1.98 - RF-WEB Pi4 (MAC: dc:a6:32:c8:b8:b9)

UniFi Network Devices (DO NOT DELETE):
- All switches (MACs starting with fc:ec:da, 78:8a:20, b4:fb:e4, d0:21:f9)
- All access points (MACs starting with fc:ec:da, e0:63:da, 60:22:32)

Mark these in cleanup plan as: [KEEP - CRITICAL]
```

---

## Phase 2: Execution (IRREVERSIBLE - Proceed with caution)

### Step 2.1: User Confirmation Checkpoint

```
Task: Present cleanup plan for user approval

Actions:
1. Display summary:
   - Total entries: 213
   - To DELETE: ~X entries
   - To KEEP: ~Y entries
   - Final count: ~Y entries

2. Show breakdown by category:
   - Category A (192.168.x): X entries
   - Category B (Deprecated HW): X entries
   - Category C (IoT to VLAN 30): X entries
   - Category D (Stale/Offline): X entries

3. List first 10 entries to delete (preview)

4. WAIT for explicit user approval before proceeding
   Required response: "APPROVED - PROCEED WITH CLEANUP"

DO NOT PROCEED without user approval!
```

### Step 2.2: Execute Deletion (After Approval)

```
Task: Delete DHCP reservations via UniFi MCP

Actions:
1. For each entry in deletion list:
   - Use UniFi MCP to delete static DHCP client
   - Log: "Deleted: [IP] [MAC] [Hostname] [Reason]"
   
2. Delete in order:
   - Category A first (192.168.x)
   - Category B second (deprecated)
   - Category C third (IoT devices)
   - Category D fourth (stale/offline)

3. After each category, verify count reduced
4. Save deletion log to: docs/dhcp-cleanup-execution-log.md

Error handling:
- If deletion fails, log error but continue
- Track failed deletions separately
- Report all failures at end
```

### Step 2.3: Verification

```
Task: Verify cleanup completed successfully

Actions:
1. Re-query all DHCP static clients
2. Compare before/after counts
3. Verify all CRITICAL entries still present
4. Check no 192.168.x entries remain
5. Verify IoT device entries removed

Create report: docs/dhcp-cleanup-verification.md
Include:
- Before count: 213
- After count: ~X
- Entries deleted: ~Y
- Critical entries verified: ~40
- Errors encountered: X
```

---

## Phase 3: Clean Backup Creation

### Step 3.1: Trigger CloudKey Backup

```
Task: Create clean backup via UniFi MCP

Actions:
1. Trigger backup creation on CloudKey
   - Type: "Settings Only" (no history/stats)
   - Format: .unf file
   
2. Wait for backup to complete (check status)
3. Verify backup file created successfully
4. Note backup filename and timestamp

If UniFi MCP cannot trigger backup directly:
- Provide manual instructions for user
- CloudKey Web UI: Settings → System → Backup → Download
- Select: "Settings Only"
```

### Step 3.2: Document Backup Details

```
Task: Record backup information

Create file: docs/cloudkey-clean-backup-info.md

Contents:
- Backup date/time: [timestamp]
- Backup filename: [name].unf
- CloudKey version: 7.2.97
- DHCP reservations in backup: ~X
- Networks configured: [list]
- VLANs configured: [list]
- WiFi SSIDs: [list with passwords]
- Firewall rules: [count]
- Port forwards: [count]

SHA256 checksum of backup file (if accessible)
```

---

## Phase 4: Final Documentation

### Step 4.1: Generate Summary Report

```
Task: Create comprehensive cleanup report

File: docs/CLOUDKEY_CLEANUP_COMPLETE.md

Contents:
1. Executive Summary
   - Cleanup date
   - Before/after counts
   - Success/failure rate
   
2. What Was Removed
   - By category with counts
   - Full list in appendix
   
3. What Was Kept
   - Critical infrastructure (list)
   - SCPI equipment (list)
   - Dev hardware (list)
   - Network devices (list)
   
4. Backup Information
   - Backup file details
   - How to restore
   - Migration readiness status
   
5. Next Steps
   - Ready for UDM Pro migration
   - Reference migration plan
   
6. Rollback Procedure (if needed)
   - How to restore from before-cleanup backup
   - Emergency contact info
```

### Step 4.2: Commit All Documentation

```
Task: Save all work to git

Actions:
1. Git add all new/modified files:
   - docs/dhcp-reservations-before-cleanup.*
   - docs/dhcp-cleanup-plan.md
   - docs/dhcp-cleanup-execution-log.md
   - docs/dhcp-cleanup-verification.md
   - docs/cloudkey-clean-backup-info.md
   - docs/CLOUDKEY_CLEANUP_COMPLETE.md

2. Git commit:
   "CloudKey DHCP cleanup complete - reduced from 213 to ~X reservations
   
   - Removed deprecated 192.168.x entries
   - Removed stale/offline devices
   - Removed IoT devices (migrating to VLAN 30)
   - Kept critical infrastructure
   - Created clean backup for UDM Pro migration
   
   Backup file: [filename].unf
   Ready for migration to UDM Pro"

3. Git push to origin
```

---

## Safety Protocols

### Before Starting
- ✅ Verify UniFi MCP connection active
- ✅ Verify write access to CloudKey
- ✅ Export safety backup first
- ✅ Review critical entries list

### During Execution
- ⚠️ Do NOT delete anything in CRITICAL list
- ⚠️ WAIT for user approval before deletions
- ⚠️ Log every deletion
- ⚠️ Stop immediately if errors exceed 5

### After Completion
- ✅ Verify critical entries intact
- ✅ Verify backup created
- ✅ Commit all documentation
- ✅ Report to user

---

## Error Handling

### If Deletion Fails
```
1. Log the error
2. Skip that entry
3. Continue with next
4. Report all failures at end
5. User can manually delete failures
```

### If Backup Creation Fails
```
1. Log error
2. Provide manual backup instructions
3. Do NOT proceed to migration until backup exists
```

### If Critical Entry Accidentally Deleted
```
1. STOP immediately
2. Report to user
3. Restore from before-cleanup backup
4. Restart cleanup process
```

---

## Success Criteria

✅ DHCP reservations reduced from 213 → ~40-50
✅ All 192.168.x entries removed
✅ All IoT devices removed
✅ All critical infrastructure intact
✅ Clean backup created
✅ All documentation committed to git
✅ Zero errors on critical entries

---

## Completion Checklist

- [ ] Phase 1: Analysis complete
- [ ] Phase 1: Before-cleanup backup saved
- [ ] Phase 1: Cleanup plan generated
- [ ] Phase 1: Critical entries identified
- [ ] Phase 2: User approval received
- [ ] Phase 2: Deletions executed
- [ ] Phase 2: Verification passed
- [ ] Phase 3: Clean backup created
- [ ] Phase 3: Backup documented
- [ ] Phase 4: Summary report generated
- [ ] Phase 4: All files committed to git
- [ ] Phase 4: Ready for UDM Pro migration

---

**Status:** ⏳ Awaiting agent execution
**Next Step:** Run this instruction set via Claude Code CLI
**Estimated Duration:** 30-60 minutes
**Risk Level:** MEDIUM (reversible via safety backup)

---

## How to Execute

### Option 1: Direct Agent Call

```bash
# Start Claude Code CLI
claude-code

# In CLI, say:
"Execute the CloudKey cleanup instructions in 
docs/agent-instructions-cloudkey-cleanup.md

Use UniFi MCP to:
1. Export current DHCP reservations (safety backup)
2. Analyze and categorize entries
3. Present cleanup plan for my approval
4. After approval, delete stale entries
5. Create clean backup
6. Document everything

STOP and wait for my approval before deleting anything."
```

### Option 2: Step-by-Step

Run each phase separately, reviewing results before proceeding to next phase.

---

*Agent Instructions Version 1.0*
*Created: 2024-12-27*
*For: USG Pro 4 → UDM Pro Migration*
