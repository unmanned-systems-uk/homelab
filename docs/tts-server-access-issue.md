# [Infrastructure] Lost SSH Access to Whisper TTS Server

**Status:** Blocked
**Priority:** High
**Labels:** infrastructure, blocked, security

---

## Problem

SSH access to the Whisper TTS server has been lost. Cannot access the VM to manage voice services.

## Server Details

| Property | Value |
|----------|-------|
| VM ID | 100 (on pve-ai) |
| IP | 10.0.1.204 (was 10.0.1.201, now 10.0.1.204) |
| Hostname | whisper-tts |
| OS | Ubuntu 24.04 Server |
| User | ccpm |
| GPU | GTX 1080 Ti (passthrough) |

## Issue

- SSH authentication fails (no working password or SSH key)
- QEMU guest agent not configured (cannot use Proxmox guest exec)
- Password stored in database is encrypted and cannot be decrypted (key mismatch)
- No documentation found with plain-text credentials

## Impact

- Cannot manage voice services (Whisper STT, Piper TTS)
- OpenAI-compatible wrapper at port 8000 returning errors
- Wyoming services on ports 10200/10300/10400 not externally accessible
- Voice transcription for HomeGate currently non-functional

## Attempted Solutions

1. ✗ SSH with keys from homelab_db
2. ✗ SSH with standard ccpm password (053210)
3. ✗ SSH with found password (PORTAdman2350!@)
4. ✗ Proxmox guest exec (guest agent not installed)
5. ✗ Cloud-init password reset (does not affect running VM)
6. ✗ Decrypt database credentials (encryption key mismatch)

## Workaround

**Temporary:** Using Groq cloud API for voice transcription in HomeGate

## Resolution Needed

**Option A - Console Access:**
- Access Proxmox web UI console for VM 100
- Login with original credentials (unknown)
- Add SSH public key to authorized_keys
- Restart/fix voice services

**Option B - VM Rebuild:**
- Document current VM configuration
- Rebuild VM with known credentials
- Redeploy voice services
- Update homelab_db

**Option C - Password Recovery:**
- Boot VM in rescue mode via Proxmox
- Reset ccpm password
- Install qemu-guest-agent for future access

## SSH Key to Add

Once console access is regained, add this public key:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOhKhVNzXcI5iedgzWetVRiTjcisol8lnGZ4DskwKghw homelab-agent@ezbox
```

## Related

- Created during session: 2025-12-14
- Reference: docs/session-summary-2025-12-14.md
- HomeGate voice integration

---

**Created:** 2026-01-17
**Session:** HomeLab Voice Integration
