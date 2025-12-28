#!/usr/bin/env python3
"""
HomeLab Alert Agent
Monitors network devices and speaks alerts via Whisper TTS when issues detected.
"""

import asyncio
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Add whisper to path for TTS
sys.path.insert(0, '/home/anthony/whisper')

# Device inventory
CRITICAL_DEVICES = {
    "UDM Pro": "10.0.1.1",
    "NAS": "10.0.1.251",
}

MONITORED_DEVICES = {
    "Jetson": "10.0.1.113",
    "Pi 5": "10.0.1.53",
    "Proxmox": "10.0.1.130",
}

SCPI_DEVICES = {
    "DMM": ("10.0.1.101", 5025),
    "Scope": ("10.0.1.106", 5555),
    "PSU 1": ("10.0.1.111", 5025),
}

# Track device states to avoid repeat alerts
device_states = {}
last_alert_time = {}
ALERT_COOLDOWN = 300  # 5 minutes between repeat alerts


def ping_device(ip: str, timeout: int = 1) -> bool:
    """Ping a device and return True if reachable."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            capture_output=True,
            timeout=timeout + 1
        )
        return result.returncode == 0
    except:
        return False


def check_scpi_port(ip: str, port: int, timeout: int = 1) -> bool:
    """Check if SCPI port is open."""
    try:
        result = subprocess.run(
            ["timeout", str(timeout), "bash", "-c", f"echo > /dev/tcp/{ip}/{port}"],
            capture_output=True,
            timeout=timeout + 1
        )
        return result.returncode == 0
    except:
        return False


def speak_alert(message: str, priority: str = "normal"):
    """Speak an alert using Whisper TTS."""
    try:
        # Activate whisper venv and speak
        cmd = f'cd /home/anthony/whisper && source venv/bin/activate && python speak.py "{message}"'
        subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
        print(f"🔊 SPOKE: {message}")
    except Exception as e:
        print(f"TTS Error: {e}")
        # Fallback to espeak if available
        try:
            subprocess.run(["spd-say", message], timeout=10)
        except:
            pass


def should_alert(device_name: str) -> bool:
    """Check if we should alert for this device (cooldown check)."""
    now = time.time()
    last = last_alert_time.get(device_name, 0)
    if now - last > ALERT_COOLDOWN:
        last_alert_time[device_name] = now
        return True
    return False


def check_all_devices():
    """Check all devices and return list of issues."""
    issues = []
    recovered = []

    # Check critical devices
    for name, ip in CRITICAL_DEVICES.items():
        is_up = ping_device(ip)
        was_up = device_states.get(name, True)
        device_states[name] = is_up

        if not is_up and was_up:
            issues.append(("critical", name, ip))
        elif is_up and not was_up:
            recovered.append(name)

    # Check monitored devices
    for name, ip in MONITORED_DEVICES.items():
        is_up = ping_device(ip)
        was_up = device_states.get(name, True)
        device_states[name] = is_up

        if not is_up and was_up:
            issues.append(("warning", name, ip))
        elif is_up and not was_up:
            recovered.append(name)

    # Check SCPI devices
    for name, (ip, port) in SCPI_DEVICES.items():
        is_up = check_scpi_port(ip, port)
        was_up = device_states.get(name, True)
        device_states[name] = is_up

        if not is_up and was_up:
            issues.append(("info", name, f"{ip}:{port}"))
        elif is_up and not was_up:
            recovered.append(name)

    return issues, recovered


def generate_alert_message(issues: list, recovered: list) -> str:
    """Generate spoken alert message."""
    messages = []

    # Critical issues first
    critical = [i for i in issues if i[0] == "critical"]
    if critical:
        devices = ", ".join([i[1] for i in critical])
        messages.append(f"Critical alert! {devices} is offline!")

    # Warnings
    warnings = [i for i in issues if i[0] == "warning"]
    if warnings:
        devices = ", ".join([i[1] for i in warnings])
        messages.append(f"Warning. {devices} is not responding.")

    # Recoveries
    if recovered:
        devices = ", ".join(recovered)
        messages.append(f"Good news. {devices} is back online.")

    return " ".join(messages)


async def monitor_loop(interval: int = 30, run_once: bool = False):
    """Main monitoring loop."""
    print("=" * 50)
    print("🏠 HomeLab Alert Agent Started")
    print(f"⏱️  Check interval: {interval}s")
    print(f"📢 TTS: Whisper (CUDA)")
    print("=" * 50)

    # Initial announcement
    speak_alert("HomeLab Alert Agent started. Monitoring network.")

    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] Checking devices...")

        issues, recovered = check_all_devices()

        # Count status
        total = len(CRITICAL_DEVICES) + len(MONITORED_DEVICES) + len(SCPI_DEVICES)
        up = sum(1 for v in device_states.values() if v)

        print(f"Status: {up}/{total} devices online")

        if issues or recovered:
            # Generate and speak alert
            message = generate_alert_message(issues, recovered)
            if message:
                speak_alert(message)
        else:
            print("✓ All monitored devices stable")

        if run_once:
            break

        await asyncio.sleep(interval)


def main():
    """Entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="HomeLab Alert Agent")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--test", action="store_true", help="Test TTS and exit")
    args = parser.parse_args()

    if args.test:
        print("Testing TTS...")
        speak_alert("This is a test of the HomeLab alert system.")
        return

    try:
        asyncio.run(monitor_loop(interval=args.interval, run_once=args.once))
    except KeyboardInterrupt:
        print("\n\n👋 Alert Agent stopped.")
        speak_alert("Alert Agent stopped. Goodbye.")


if __name__ == "__main__":
    main()
