# CC-Share Persistent Mount Configuration

**Last Updated:** 2026-01-08
**System:** homelab-EZbox (Ubuntu 24.04)
**NAS:** Synology DS1621 @ ccpm-nas.local (10.0.1.251)

---

## Overview

This document describes the configuration for automatically mounting the CC-Share SMB network share on system boot/user login.

**CC-Share** is a shared network storage location on the Synology NAS used for cross-system file sharing and collaboration.

---

## Mount Details

| Parameter | Value |
|-----------|-------|
| **Protocol** | SMB/CIFS (GVFS) |
| **Server** | ccpm-nas.local (10.0.1.251) |
| **Share Name** | cc-share |
| **Mount Point** | `/run/user/1000/gvfs/smb-share:server=ccpm-nas.local,share=cc-share` |
| **Symlink** | `~/cc-share` → GVFS mount point |
| **Project Folder** | `~/cc-share/HomeLab` |

---

## Configuration Components

### 1. Systemd User Service

**Service File:** `~/.config/systemd/user/cc-share-mount.service`

```ini
[Unit]
Description=Mount CC-Share from Synology NAS
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
# Mount the SMB share using gio (ignore if already mounted)
ExecStart=/bin/sh -c '/usr/bin/gio mount smb://ccpm-nas.local/cc-share || true'
# Unmount on stop (ignore errors)
ExecStop=/bin/sh -c '/usr/bin/gio mount -u smb://ccpm-nas.local/cc-share || true'

[Install]
WantedBy=default.target
```

**Status:**
- Enabled: Yes (auto-starts on user login)
- Active: Yes

### 2. Symlink

**Created:** 2026-01-07 01:10

```bash
~/cc-share -> /run/user/1000/gvfs/smb-share:server=ccpm-nas.local,share=cc-share
```

This symlink provides a consistent, easy-to-use path regardless of the GVFS mount point.

### 3. GNOME Bookmark

**File:** `~/.config/gtk-3.0/bookmarks`

```
smb://ccpm-nas.local/cc-share CC-Share
```

This bookmark makes CC-Share appear in the file manager sidebar for easy access.

---

## How It Works

### On System Boot / User Login:

1. **Network comes online** - `network-online.target` is reached
2. **systemd user service starts** - `cc-share-mount.service` is triggered
3. **GVFS mounts share** - `gio mount` connects to `smb://ccpm-nas.local/cc-share`
4. **Symlink resolves** - `~/cc-share` points to the mounted GVFS location
5. **File manager shows bookmark** - CC-Share appears in sidebar

**Total mount time:** ~2-5 seconds after user login

---

## Verification Commands

### Check Service Status

```bash
systemctl --user status cc-share-mount.service
```

Expected output: `Active: active (exited)`

### Check Mount Status

```bash
# List GVFS mounts
ls /run/user/$(id -u)/gvfs/

# Check symlink
readlink -f ~/cc-share

# Verify mount is working
ls ~/cc-share/HomeLab
```

### Check Service Logs

```bash
journalctl --user -u cc-share-mount.service -n 20
```

---

## Management Commands

### Restart Service

```bash
systemctl --user restart cc-share-mount.service
```

### Stop Service

```bash
systemctl --user stop cc-share-mount.service
```

### Disable Auto-Mount (temporary)

```bash
systemctl --user disable cc-share-mount.service
```

### Re-enable Auto-Mount

```bash
systemctl --user enable cc-share-mount.service
```

### Manual Mount

```bash
gio mount smb://ccpm-nas.local/cc-share
```

### Manual Unmount

```bash
gio mount -u smb://ccpm-nas.local/cc-share
```

---

## Troubleshooting

### Mount Not Available After Login

1. **Check service status:**
   ```bash
   systemctl --user status cc-share-mount.service
   ```

2. **Check network connectivity:**
   ```bash
   ping -c 3 ccpm-nas.local
   ping -c 3 10.0.1.251
   ```

3. **Manually trigger mount:**
   ```bash
   systemctl --user restart cc-share-mount.service
   ```

4. **Check logs:**
   ```bash
   journalctl --user -u cc-share-mount.service -n 50
   ```

### "Location is already mounted" Error

This is normal and expected if the share was already mounted. The service ignores this error (`|| true`) to ensure idempotent operation.

### Symlink Broken

If `~/cc-share` shows as broken:

1. **Check GVFS mount:**
   ```bash
   ls /run/user/$(id -u)/gvfs/
   ```

2. **Recreate symlink if needed:**
   ```bash
   rm ~/cc-share
   ln -s /run/user/$(id -u)/gvfs/smb-share:server=ccpm-nas.local,share=cc-share ~/cc-share
   ```

3. **Restart service:**
   ```bash
   systemctl --user restart cc-share-mount.service
   ```

### NAS Not Reachable

1. **Check NAS is online:**
   ```bash
   ping 10.0.1.251
   ```

2. **Check DNS resolution:**
   ```bash
   nslookup ccpm-nas.local
   ```

3. **Check SMB service on NAS:**
   - Access NAS web interface
   - Verify SMB service is running
   - Verify cc-share folder exists and has correct permissions

---

## CC-Share Slash Command

The `/cc-share` command can be used to copy files to the CC-Share:

```bash
/cc-share <file_path>
```

This uses the skill defined in `.claude/commands/cc-share.md`

---

## Directory Structure

### CC-Share Root

```
~/cc-share/
├── CCPM-V2/          # CCPM project files
├── Common/           # Shared resources
├── Git Repos/        # Repositories
├── Home Assistant/   # HA configurations
├── HomeLab/          # HomeLab project files
├── NEX-Cam/          # Camera files
├── SKILLS/           # Skills and automation
└── #recycle/         # Synology recycle bin
```

### HomeLab Project Folder

```
~/cc-share/HomeLab/
├── equipment/        # Equipment documentation
├── infrastructure/   # Infrastructure configs
├── network/          # Network diagrams/docs
├── overview/         # Project overviews
└── *.md             # Markdown documentation
```

---

## Related Configuration

### CLAUDE.md Reference

From `CLAUDE.md`:

```markdown
### Shared Folder (CC-Share)

| Parameter | Value |
|-----------|-------|
| **Local Path** | `~/cc-share` (symlink) |
| **Project Folder** | `~/cc-share/HomeLab` |
| **NAS Location** | `\\ccpm-nas.local\CC-Share` |
| **GVFS Mount** | `/run/user/1000/gvfs/smb-share:server=ccpm-nas.local,share=cc-share/` |
```

---

## Security Notes

- **Authentication:** Uses GNOME Keyring for storing SMB credentials
- **Credentials stored in:** GNOME Keyring (encrypted)
- **Access:** User-level mount (only accessible by homelab user)
- **Network:** Accessible only from 10.0.1.0/24 network

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-07 | Created symlink `~/cc-share` | Manual |
| 2026-01-08 | Identified mount not persistent after power event | HomeLab Agent |
| 2026-01-08 | Created systemd user service for auto-mount | HomeLab Agent |
| 2026-01-08 | Added GNOME bookmark for file manager | HomeLab Agent |
| 2026-01-08 | Verified mount working and persistent | HomeLab Agent |

---

*Configuration ensures CC-Share is always available after login/reboot*
