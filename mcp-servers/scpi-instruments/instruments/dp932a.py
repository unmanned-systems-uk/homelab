#!/usr/bin/env python3
"""
DP932A - Rigol Programmable Linear DC Power Supply Driver.

3-channel power supply: CH1 (32V/3A), CH2 (32V/3A), CH3 (6V/3A).
Total power: 212W.
"""

import logging
import time
from typing import Optional, Dict, Any, List

from .base import BaseInstrument

logger = logging.getLogger(__name__)


class DP932A(BaseInstrument):
    """
    Driver for Rigol DP932A Programmable Linear DC Power Supply.

    Specifications:
    - CH1: 0-32V, 0-3A, 96W
    - CH2: 0-32V, 0-3A, 96W
    - CH3: 0-6V, 0-3A, 18W
    - Total: 212W
    - Resolution: 1mV, 1mA
    """

    # DP932A uses 5025 port
    PACING = 0.03  # 30ms between commands

    def get_type(self) -> str:
        return "dp932a"

    def post_reset(self) -> None:
        """Post-reset initialization."""
        time.sleep(0.5)
        # Ensure all outputs are OFF after reset
        self.write(":OUTP OFF,CH1")
        time.sleep(self.PACING)
        self.write(":OUTP OFF,CH2")
        time.sleep(self.PACING)
        self.write(":OUTP OFF,CH3")
        time.sleep(self.PACING)
        self.clear_errors()

    # ---- Output Control ----

    def output_state(self, channel: int, enabled: bool) -> dict:
        """
        Enable or disable channel output.

        CAUTION: Enabling output will apply voltage to connected load.

        Args:
            channel: Channel number (1, 2, or 3)
            enabled: True to enable, False to disable

        Returns:
            Dict with output state
        """
        self.write(f":OUTP {'ON' if enabled else 'OFF'},CH{channel}")
        time.sleep(self.PACING)

        actual = self.query(f":OUTP? CH{channel}").strip()
        return {
            "channel": channel,
            "output_enabled": actual in ["1", "ON"],
            "requested": enabled
        }

    def get_output_state(self, channel: int) -> dict:
        """
        Query current output state.

        Args:
            channel: Channel number (1, 2, or 3)

        Returns:
            Dict with output_enabled
        """
        state = self.query(f":OUTP? CH{channel}").strip()
        return {
            "channel": channel,
            "output_enabled": state in ["1", "ON"]
        }

    def all_outputs_off(self) -> dict:
        """
        Disable all outputs.

        Returns:
            Dict with ok status
        """
        self.write(":OUTP OFF,CH1")
        time.sleep(self.PACING)
        self.write(":OUTP OFF,CH2")
        time.sleep(self.PACING)
        self.write(":OUTP OFF,CH3")
        time.sleep(self.PACING)

        return {
            "all_off": True,
            "ch1": self.query(":OUTP? CH1").strip() in ["0", "OFF"],
            "ch2": self.query(":OUTP? CH2").strip() in ["0", "OFF"],
            "ch3": self.query(":OUTP? CH3").strip() in ["0", "OFF"],
        }

    # ---- Channel Configuration ----

    def set_channel(
        self,
        channel: int,
        voltage_v: float,
        current_a: float
    ) -> dict:
        """
        Set voltage and current for a channel.

        Args:
            channel: Channel number (1, 2, or 3)
            voltage_v: Output voltage in Volts
            current_a: Current limit in Amps

        Returns:
            Dict with applied settings
        """
        # Set voltage
        self.write(f":VOLT {voltage_v},CH{channel}")
        time.sleep(self.PACING)

        # Set current limit
        self.write(f":CURR {current_a},CH{channel}")
        time.sleep(self.PACING)

        # Read back
        actual_v = float(self.query(f":VOLT? CH{channel}"))
        actual_i = float(self.query(f":CURR? CH{channel}"))

        return {
            "channel": channel,
            "voltage_v": actual_v,
            "current_a": actual_i
        }

    def set_voltage(self, channel: int, voltage_v: float) -> dict:
        """
        Set voltage for a channel.

        Args:
            channel: Channel number (1, 2, or 3)
            voltage_v: Output voltage in Volts

        Returns:
            Dict with voltage setting
        """
        self.write(f":VOLT {voltage_v},CH{channel}")
        time.sleep(self.PACING)

        actual = float(self.query(f":VOLT? CH{channel}"))
        return {
            "channel": channel,
            "voltage_v": actual
        }

    def set_current(self, channel: int, current_a: float) -> dict:
        """
        Set current limit for a channel.

        Args:
            channel: Channel number (1, 2, or 3)
            current_a: Current limit in Amps

        Returns:
            Dict with current setting
        """
        self.write(f":CURR {current_a},CH{channel}")
        time.sleep(self.PACING)

        actual = float(self.query(f":CURR? CH{channel}"))
        return {
            "channel": channel,
            "current_a": actual
        }

    # ---- Protection ----

    def set_ovp(self, channel: int, enabled: bool, voltage_v: Optional[float] = None) -> dict:
        """
        Configure Over-Voltage Protection.

        Args:
            channel: Channel number (1, 2, or 3)
            enabled: Enable/disable OVP
            voltage_v: OVP threshold voltage

        Returns:
            Dict with OVP settings
        """
        self.write(f":OUTP:OVP {'ON' if enabled else 'OFF'},CH{channel}")
        time.sleep(self.PACING)

        if voltage_v is not None and enabled:
            self.write(f":OUTP:OVP:VAL {voltage_v},CH{channel}")
            time.sleep(self.PACING)

        return {
            "channel": channel,
            "ovp_enabled": self.query(f":OUTP:OVP? CH{channel}").strip() in ["1", "ON"],
            "ovp_voltage_v": float(self.query(f":OUTP:OVP:VAL? CH{channel}")) if enabled else None
        }

    def set_ocp(
        self,
        channel: int,
        enabled: bool,
        current_a: Optional[float] = None,
        delay_ms: Optional[int] = None
    ) -> dict:
        """
        Configure Over-Current Protection.

        Args:
            channel: Channel number (1, 2, or 3)
            enabled: Enable/disable OCP
            current_a: OCP threshold current
            delay_ms: OCP delay in milliseconds (0-1000)

        Returns:
            Dict with OCP settings
        """
        self.write(f":OUTP:OCP {'ON' if enabled else 'OFF'},CH{channel}")
        time.sleep(self.PACING)

        if current_a is not None and enabled:
            self.write(f":OUTP:OCP:VAL {current_a},CH{channel}")
            time.sleep(self.PACING)

        if delay_ms is not None and enabled:
            self.write(f":OUTP:OCP:DEL {delay_ms},CH{channel}")
            time.sleep(self.PACING)

        return {
            "channel": channel,
            "ocp_enabled": self.query(f":OUTP:OCP? CH{channel}").strip() in ["1", "ON"],
            "ocp_current_a": float(self.query(f":OUTP:OCP:VAL? CH{channel}")) if enabled else None
        }

    def clear_protection(self, channel: int) -> dict:
        """
        Clear protection trip status.

        Args:
            channel: Channel number (1, 2, or 3)

        Returns:
            Dict with ok status
        """
        self.write(f":OUTP:PROT:CLE CH{channel}")
        return {"channel": channel, "protection_cleared": True}

    # ---- Measurements ----

    def measure(self, channel: int) -> dict:
        """
        Read voltage, current, and power for a channel.

        Args:
            channel: Channel number (1, 2, or 3)

        Returns:
            Dict with voltage_v, current_a, power_w
        """
        voltage = float(self.query(f":MEAS:VOLT? CH{channel}"))
        current = float(self.query(f":MEAS:CURR? CH{channel}"))
        power = float(self.query(f":MEAS:POW? CH{channel}"))

        return {
            "channel": channel,
            "voltage_v": voltage,
            "current_a": current,
            "power_w": power
        }

    def measure_all(self) -> dict:
        """
        Read measurements for all channels.

        Returns:
            Dict with ch1, ch2, ch3 measurements
        """
        return {
            "ch1": self.measure(1),
            "ch2": self.measure(2),
            "ch3": self.measure(3)
        }

    def measure_voltage(self, channel: int) -> dict:
        """Read voltage only."""
        return {
            "channel": channel,
            "voltage_v": float(self.query(f":MEAS:VOLT? CH{channel}"))
        }

    def measure_current(self, channel: int) -> dict:
        """Read current only."""
        return {
            "channel": channel,
            "current_a": float(self.query(f":MEAS:CURR? CH{channel}"))
        }

    # ---- Tracking Mode ----

    def set_tracking(self, mode: int) -> dict:
        """
        Set tracking mode.

        Args:
            mode: 0=Independent, 1=Series (CH1+CH2), 2=Parallel (CH1||CH2)

        Returns:
            Dict with tracking mode
        """
        self.write(f":OUTP:TRACK {mode}")
        time.sleep(self.PACING)

        actual = int(self.query(":OUTP:TRACK?"))
        mode_names = {0: "independent", 1: "series", 2: "parallel"}

        return {
            "tracking_mode": mode_names.get(actual, str(actual)),
            "mode_value": actual
        }

    # ---- State Save/Recall ----

    def save_state(self, slot: int) -> dict:
        """
        Save current state to memory slot.

        Args:
            slot: Memory slot (1-10)

        Returns:
            Dict with ok status
        """
        self.write(f"*SAV {slot}")
        time.sleep(0.2)
        return {"saved_to_slot": slot}

    def recall_state(self, slot: int) -> dict:
        """
        Recall state from memory slot.

        Args:
            slot: Memory slot (1-10)

        Returns:
            Dict with ok status
        """
        self.write(f"*RCL {slot}")
        time.sleep(0.2)
        return {"recalled_from_slot": slot}

    # ---- Convenience Methods ----

    def configure_channel_safe(
        self,
        channel: int,
        voltage_v: float,
        current_a: float,
        enable_ovp: bool = True,
        enable_ocp: bool = True
    ) -> dict:
        """
        Configure channel with protection enabled.

        Sets voltage, current, and enables OVP/OCP with sensible margins.

        Args:
            channel: Channel number (1, 2, or 3)
            voltage_v: Output voltage
            current_a: Current limit
            enable_ovp: Enable over-voltage protection
            enable_ocp: Enable over-current protection

        Returns:
            Dict with full configuration
        """
        # Set voltage and current
        result = self.set_channel(channel, voltage_v, current_a)

        # Enable OVP at 110% of set voltage
        if enable_ovp:
            ovp_v = voltage_v * 1.1
            # Cap at channel maximum
            if channel == 3:
                ovp_v = min(ovp_v, 6.6)  # CH3 max is 6V
            else:
                ovp_v = min(ovp_v, 35.2)  # CH1/2 max is 32V
            self.set_ovp(channel, True, ovp_v)
            result["ovp_voltage_v"] = ovp_v

        # Enable OCP at 110% of set current
        if enable_ocp:
            ocp_a = min(current_a * 1.1, 3.3)  # Max is 3A
            self.set_ocp(channel, True, ocp_a)
            result["ocp_current_a"] = ocp_a

        return result

    def quick_output(
        self,
        channel: int,
        voltage_v: float,
        current_a: float
    ) -> dict:
        """
        Configure and enable output in one call.

        CAUTION: This will apply voltage immediately.

        Args:
            channel: Channel number (1, 2, or 3)
            voltage_v: Output voltage
            current_a: Current limit

        Returns:
            Dict with configuration and measurements
        """
        # Configure
        config = self.set_channel(channel, voltage_v, current_a)

        # Enable
        self.output_state(channel, True)

        # Small delay for output to stabilize
        time.sleep(0.1)

        # Measure
        meas = self.measure(channel)

        return {
            **config,
            "output_enabled": True,
            "measured_voltage_v": meas["voltage_v"],
            "measured_current_a": meas["current_a"],
            "measured_power_w": meas["power_w"]
        }
