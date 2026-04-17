#!/usr/bin/env python3
"""
DL3021A - Rigol DC Electronic Load Driver.

Single channel, 150V/40A/200W DC electronic load.
Supports CC, CV, CR, CP modes plus transient and OCP/OPP testing.
"""

import logging
import time
from typing import Optional, Dict, Any

from .base import BaseInstrument

logger = logging.getLogger(__name__)

# Operating modes
MODES = {
    "cc": "CURRent",
    "cv": "VOLTage",
    "cr": "RESistance",
    "cp": "POWer",
}

# Function modes
FUNCTION_MODES = {
    "fixed": "FIXed",
    "list": "LIST",
    "wave": "WAVe",
    "battery": "BATTery",
    "ocp": "OCP",
    "opp": "OPP",
}


class DL3021A(BaseInstrument):
    """
    Driver for Rigol DL3021A DC Electronic Load.

    Specifications:
    - Voltage: 0-150V
    - Current: 0-40A
    - Power: 0-200W
    - Modes: CC, CV, CR, CP, Transient, OCP, OPP
    """

    def get_type(self) -> str:
        return "dl3021a"

    def post_reset(self) -> None:
        """Post-reset initialization."""
        time.sleep(0.5)
        # Ensure input is OFF after reset
        self.write(":SOUR:INP:STAT OFF")
        time.sleep(self.PACING)
        self.clear_errors()

    # ---- Input Control ----

    def input_state(self, enabled: bool) -> dict:
        """
        Enable or disable the load input.

        CAUTION: Enabling input will sink current from connected source.

        Args:
            enabled: True to enable, False to disable

        Returns:
            Dict with input state
        """
        self.write(f":SOUR:INP:STAT {'ON' if enabled else 'OFF'}")
        time.sleep(self.PACING)

        actual = self.query(":SOUR:INP:STAT?").strip()
        return {
            "input_enabled": actual in ["1", "ON"],
            "requested": enabled
        }

    def get_input_state(self) -> dict:
        """
        Query current input state.

        Returns:
            Dict with input_enabled
        """
        state = self.query(":SOUR:INP:STAT?").strip()
        return {"input_enabled": state in ["1", "ON"]}

    # ---- Mode Configuration ----

    def set_mode(self, mode: str) -> dict:
        """
        Set operating mode (CC, CV, CR, CP).

        Args:
            mode: Mode name (cc, cv, cr, cp)

        Returns:
            Dict with applied mode
        """
        mode_scpi = MODES.get(mode.lower(), mode.upper())
        self.write(f":SOUR:FUNC {mode_scpi}")
        time.sleep(self.PACING)

        actual = self.query(":SOUR:FUNC?").strip()
        return {"mode": actual}

    def set_function_mode(self, func_mode: str) -> dict:
        """
        Set function mode (fixed, list, wave, battery, ocp, opp).

        Args:
            func_mode: Function mode name

        Returns:
            Dict with applied function mode
        """
        mode_scpi = FUNCTION_MODES.get(func_mode.lower(), func_mode.upper())
        self.write(f":SOUR:FUNC:MODE {mode_scpi}")
        time.sleep(self.PACING)

        actual = self.query(":SOUR:FUNC:MODE?").strip()
        return {"function_mode": actual}

    # ---- Constant Current (CC) Mode ----

    def configure_cc(
        self,
        current_a: float,
        slew_rate: Optional[float] = None,
        voltage_limit: Optional[float] = None,
        von_voltage: Optional[float] = None
    ) -> dict:
        """
        Configure Constant Current mode.

        Args:
            current_a: Load current in Amps
            slew_rate: Current slew rate in A/us
            voltage_limit: Maximum voltage limit
            von_voltage: Starting voltage threshold

        Returns:
            Dict with applied settings
        """
        self.write(":SOUR:FUNC CURRent")
        time.sleep(self.PACING)

        self.write(f":SOUR:CURR:LEV:IMM {current_a}")
        time.sleep(self.PACING)

        if slew_rate is not None:
            self.write(f":SOUR:CURR:SLEW {slew_rate}")
            time.sleep(self.PACING)

        if voltage_limit is not None:
            self.write(f":SOUR:CURR:VLIM {voltage_limit}")
            time.sleep(self.PACING)

        if von_voltage is not None:
            self.write(f":SOUR:CURR:VON {von_voltage}")
            time.sleep(self.PACING)

        # Read back
        return {
            "mode": "CC",
            "current_a": float(self.query(":SOUR:CURR:LEV:IMM?")),
            "voltage_limit_v": float(self.query(":SOUR:CURR:VLIM?")),
        }

    # ---- Constant Voltage (CV) Mode ----

    def configure_cv(
        self,
        voltage_v: float,
        current_limit: Optional[float] = None
    ) -> dict:
        """
        Configure Constant Voltage mode.

        Args:
            voltage_v: Load voltage in Volts
            current_limit: Maximum current limit

        Returns:
            Dict with applied settings
        """
        self.write(":SOUR:FUNC VOLTage")
        time.sleep(self.PACING)

        self.write(f":SOUR:VOLT:LEV:IMM {voltage_v}")
        time.sleep(self.PACING)

        if current_limit is not None:
            self.write(f":SOUR:VOLT:ILIM {current_limit}")
            time.sleep(self.PACING)

        return {
            "mode": "CV",
            "voltage_v": float(self.query(":SOUR:VOLT:LEV:IMM?")),
            "current_limit_a": float(self.query(":SOUR:VOLT:ILIM?")),
        }

    # ---- Constant Resistance (CR) Mode ----

    def configure_cr(
        self,
        resistance_ohm: float,
        current_limit: Optional[float] = None
    ) -> dict:
        """
        Configure Constant Resistance mode.

        Args:
            resistance_ohm: Load resistance in Ohms
            current_limit: Maximum current limit

        Returns:
            Dict with applied settings
        """
        self.write(":SOUR:FUNC RESistance")
        time.sleep(self.PACING)

        self.write(f":SOUR:RES:LEV:IMM {resistance_ohm}")
        time.sleep(self.PACING)

        if current_limit is not None:
            self.write(f":SOUR:RES:ILIM {current_limit}")
            time.sleep(self.PACING)

        return {
            "mode": "CR",
            "resistance_ohm": float(self.query(":SOUR:RES:LEV:IMM?")),
            "current_limit_a": float(self.query(":SOUR:RES:ILIM?")),
        }

    # ---- Constant Power (CP) Mode ----

    def configure_cp(
        self,
        power_w: float,
        current_limit: Optional[float] = None
    ) -> dict:
        """
        Configure Constant Power mode.

        Args:
            power_w: Load power in Watts
            current_limit: Maximum current limit

        Returns:
            Dict with applied settings
        """
        self.write(":SOUR:FUNC POWer")
        time.sleep(self.PACING)

        self.write(f":SOUR:POW:LEV:IMM {power_w}")
        time.sleep(self.PACING)

        if current_limit is not None:
            self.write(f":SOUR:POW:ILIM {current_limit}")
            time.sleep(self.PACING)

        return {
            "mode": "CP",
            "power_w": float(self.query(":SOUR:POW:LEV:IMM?")),
            "current_limit_a": float(self.query(":SOUR:POW:ILIM?")),
        }

    # ---- Transient Mode ----

    def configure_transient(
        self,
        mode: str = "continuous",
        level_a: float = 0.5,
        level_b: float = 1.0,
        frequency_hz: Optional[float] = None,
        width_a_s: Optional[float] = None,
        width_b_s: Optional[float] = None
    ) -> dict:
        """
        Configure transient (dynamic) mode.

        Args:
            mode: Transient mode (continuous, pulse, toggle)
            level_a: Level A current in Amps
            level_b: Level B current in Amps
            frequency_hz: Frequency for continuous mode
            width_a_s: Level A width in seconds (for pulse)
            width_b_s: Level B width in seconds (for pulse)

        Returns:
            Dict with applied settings
        """
        # Set CC mode first
        self.write(":SOUR:FUNC CURRent")
        time.sleep(self.PACING)

        # Set transient mode
        mode_map = {"continuous": "CONT", "pulse": "PULS", "toggle": "TOGG"}
        mode_scpi = mode_map.get(mode.lower(), mode.upper())
        self.write(f":SOUR:CURR:TRAN:MODE {mode_scpi}")
        time.sleep(self.PACING)

        # Set levels
        self.write(f":SOUR:CURR:TRAN:ALEV {level_a}")
        time.sleep(self.PACING)
        self.write(f":SOUR:CURR:TRAN:BLEV {level_b}")
        time.sleep(self.PACING)

        # Set timing
        if frequency_hz is not None:
            self.write(f":SOUR:CURR:TRAN:FREQ {frequency_hz}")
            time.sleep(self.PACING)

        if width_a_s is not None:
            self.write(f":SOUR:CURR:TRAN:AWID {width_a_s}")
            time.sleep(self.PACING)

        if width_b_s is not None:
            self.write(f":SOUR:CURR:TRAN:BWID {width_b_s}")
            time.sleep(self.PACING)

        # Enable transient
        self.write(":SOUR:TRAN ON")
        time.sleep(self.PACING)

        return {
            "transient_mode": self.query(":SOUR:CURR:TRAN:MODE?").strip(),
            "level_a": float(self.query(":SOUR:CURR:TRAN:ALEV?")),
            "level_b": float(self.query(":SOUR:CURR:TRAN:BLEV?")),
            "enabled": True
        }

    def disable_transient(self) -> dict:
        """
        Disable transient mode.

        Returns:
            Dict with ok status
        """
        self.write(":SOUR:TRAN OFF")
        return {"transient_enabled": False}

    # ---- Measurements ----

    def measure(self) -> dict:
        """
        Read all measurements (voltage, current, power, resistance).

        Returns:
            Dict with voltage_v, current_a, power_w
        """
        voltage = float(self.query(":MEAS:VOLT?"))
        current = float(self.query(":MEAS:CURR?"))
        power = float(self.query(":MEAS:POW?"))

        return {
            "voltage_v": voltage,
            "current_a": current,
            "power_w": power
        }

    def measure_voltage(self) -> dict:
        """Read voltage only."""
        return {"voltage_v": float(self.query(":MEAS:VOLT?"))}

    def measure_current(self) -> dict:
        """Read current only."""
        return {"current_a": float(self.query(":MEAS:CURR?"))}

    def measure_power(self) -> dict:
        """Read power only."""
        return {"power_w": float(self.query(":MEAS:POW?"))}

    # ---- OCP Test ----

    def configure_ocp_test(
        self,
        start_current_a: float,
        step_current_a: float,
        max_current_a: float,
        step_delay_s: float = 0.1,
        von_voltage_v: float = 5.0,
        protection_voltage_v: float = 0.5
    ) -> dict:
        """
        Configure Over-Current Protection (OCP) test.

        Args:
            start_current_a: Starting current
            step_current_a: Current step increment
            max_current_a: Maximum current to test
            step_delay_s: Delay between steps
            von_voltage_v: Starting voltage threshold
            protection_voltage_v: OCP trigger voltage

        Returns:
            Dict with OCP test configuration
        """
        self.write(":SOUR:FUNC:MODE OCP")
        time.sleep(self.PACING)

        self.write(f":SOUR:OCP:VON {von_voltage_v}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OCP:ISET {start_current_a}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OCP:ISTEP {step_current_a}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OCP:IMAX {max_current_a}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OCP:IDELAYSTEP {step_delay_s}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OCP:VOCP {protection_voltage_v}")
        time.sleep(self.PACING)

        return {
            "mode": "OCP",
            "start_current_a": start_current_a,
            "step_current_a": step_current_a,
            "max_current_a": max_current_a,
            "step_delay_s": step_delay_s,
            "von_voltage_v": von_voltage_v,
            "protection_voltage_v": protection_voltage_v
        }

    # ---- OPP Test ----

    def configure_opp_test(
        self,
        start_power_w: float,
        step_power_w: float,
        max_power_w: float,
        step_delay_s: float = 0.1,
        von_voltage_v: float = 5.0,
        protection_voltage_v: float = 0.5
    ) -> dict:
        """
        Configure Over-Power Protection (OPP) test.

        Args:
            start_power_w: Starting power
            step_power_w: Power step increment
            max_power_w: Maximum power to test
            step_delay_s: Delay between steps
            von_voltage_v: Starting voltage threshold
            protection_voltage_v: OPP trigger voltage

        Returns:
            Dict with OPP test configuration
        """
        self.write(":SOUR:FUNC:MODE OPP")
        time.sleep(self.PACING)

        self.write(f":SOUR:OPP:VON {von_voltage_v}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OPP:PSET {start_power_w}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OPP:PSTEP {step_power_w}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OPP:PMAX {max_power_w}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OPP:PDELAYSTEP {step_delay_s}")
        time.sleep(self.PACING)
        self.write(f":SOUR:OPP:VOPP {protection_voltage_v}")
        time.sleep(self.PACING)

        return {
            "mode": "OPP",
            "start_power_w": start_power_w,
            "step_power_w": step_power_w,
            "max_power_w": max_power_w,
            "step_delay_s": step_delay_s,
            "von_voltage_v": von_voltage_v,
            "protection_voltage_v": protection_voltage_v
        }

    # ---- Remote Sense ----

    def set_sense(self, enabled: bool) -> dict:
        """
        Enable/disable remote voltage sensing.

        Args:
            enabled: True for remote sense, False for local

        Returns:
            Dict with sense state
        """
        self.write(f":SOUR:SENS {'ON' if enabled else 'OFF'}")
        time.sleep(self.PACING)

        actual = self.query(":SOUR:SENS?").strip()
        return {"remote_sense": actual in ["1", "ON"]}

    # ---- Short Circuit Mode ----

    def short_circuit(self, enabled: bool) -> dict:
        """
        Enable/disable short circuit mode.

        CAUTION: This will sink maximum current from source.

        Args:
            enabled: True to enable short, False to disable

        Returns:
            Dict with short state
        """
        self.write(f":SOUR:INP:SHOR {'ON' if enabled else 'OFF'}")
        time.sleep(self.PACING)

        actual = self.query(":SOUR:INP:SHOR?").strip()
        return {"short_circuit": actual in ["1", "ON"]}
