#!/usr/bin/env python3
"""
HomeLab Network Monitor Agent
Uses Claude Agent SDK to monitor network devices and SCPI equipment.
"""

import asyncio
import subprocess
from claude_agent_sdk import query, ClaudeAgentOptions

# HomeLab device inventory
DEVICES = {
    "UDM-Pro": "10.0.1.1",
    "NAS": "10.0.1.251",
    "Jetson": "10.0.1.113",
    "Pi5-DPM": "10.0.1.53",
    "Proxmox": "10.0.1.130",
}

SCPI_DEVICES = {
    "DMM": ("10.0.1.101", 5025),
    "Load": ("10.0.1.105", 5555),
    "Scope": ("10.0.1.106", 5555),
    "PSU1": ("10.0.1.111", 5025),
    "AWG": ("10.0.1.120", 5555),
    "PSU2": ("10.0.1.138", 5025),
}


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


def get_network_status() -> str:
    """Get status of all network devices."""
    lines = ["## Network Devices\n"]
    for name, ip in DEVICES.items():
        status = "UP" if ping_device(ip) else "DOWN"
        emoji = "✓" if status == "UP" else "✗"
        lines.append(f"- {emoji} {name} ({ip}): {status}")

    lines.append("\n## SCPI Equipment\n")
    online = 0
    for name, (ip, port) in SCPI_DEVICES.items():
        status = "UP" if check_scpi_port(ip, port) else "DOWN"
        if status == "UP":
            online += 1
        emoji = "✓" if status == "UP" else "✗"
        lines.append(f"- {emoji} {name} ({ip}:{port}): {status}")

    lines.append(f"\n**Summary:** {online}/{len(SCPI_DEVICES)} SCPI devices online")
    return "\n".join(lines)


async def run_monitor_agent():
    """Run the network monitor agent."""

    # Get current network status
    status = get_network_status()

    print("=" * 50)
    print("HomeLab Network Monitor Agent")
    print("=" * 50)
    print(status)
    print("=" * 50)

    # Ask Claude to analyze and provide recommendations
    prompt = f"""You are the HomeLab Network Monitor Agent.

Here is the current network status:

{status}

Analyze this status and:
1. Identify any issues (devices that are DOWN)
2. Suggest troubleshooting steps for any offline devices
3. Note any patterns or concerns

Keep your response concise and actionable."""

    print("\n🤖 Agent Analysis:\n")

    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                max_turns=1,  # Single analysis, no tool use
            )
        ):
            if hasattr(message, 'content'):
                print(message.content)
            elif isinstance(message, str):
                print(message)
    except Exception as e:
        print(f"Agent error: {e}")
        print("\nNote: Ensure ANTHROPIC_API_KEY is set")


if __name__ == "__main__":
    asyncio.run(run_monitor_agent())
