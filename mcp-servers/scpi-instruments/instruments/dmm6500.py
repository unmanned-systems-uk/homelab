#!/usr/bin/env python3
"""
DMM6500 - Keithley 6½-Digit Multimeter Driver.

6.5-digit resolution, multiple measurement functions.
Supports SCPI command set.
"""

import logging
import time
from typing import Optional, Dict, Any, List

from .base import BaseInstrument

logger = logging.getLogger(__name__)

# Measurement function mapping
FUNCTIONS = {
    "dcv": "VOLT:DC",
    "acv": "VOLT:AC",
    "dci": "CURR:DC",
    "aci": "CURR:AC",
    "res": "RES",
    "fres": "FRES",
    "temp": "TEMP",
    "freq": "FREQ",
    "per": "PER",
    "diode": "DIOD",
    "cont": "CONT",
    "cap": "CAP",
}

# NPLC values for integration time
NPLC_VALUES = [0.0005, 0.0015, 0.005, 0.01, 0.1, 1, 10, 15]


class DMM6500(BaseInstrument):
    """
    Driver for Keithley DMM6500 6½-Digit Multimeter.

    Resolution: 6.5 digits
    Functions: DCV, ACV, DCI, ACI, 2W/4W Resistance, Temperature,
               Frequency, Period, Diode, Continuity, Capacitance
    """

    # DMM uses 5025 port and needs less pacing
    PACING = 0.03  # 30ms between commands

    def get_type(self) -> str:
        return "dmm6500"

    def post_reset(self) -> None:
        """Post-reset initialization."""
        time.sleep(0.3)
        self.clear_errors()

    # ---- Configuration ----

    def configure(
        self,
        function: str,
        range_val: Optional[float] = None,
        nplc: Optional[float] = None,
        auto_range: bool = True,
        auto_zero: bool = True
    ) -> dict:
        """
        Configure measurement function.

        Args:
            function: Measurement function (dcv, acv, dci, aci, res, fres, temp, freq, cap)
            range_val: Manual range value (None for auto)
            nplc: Integration time in power line cycles (0.0005-15)
            auto_range: Enable auto-ranging
            auto_zero: Enable auto-zero

        Returns:
            Dict with applied settings
        """
        # Map friendly name to SCPI function
        func_scpi = FUNCTIONS.get(function.lower(), function.upper())

        # Set function
        self.write(f':SENS:FUNC "{func_scpi}"')
        time.sleep(self.PACING)

        # Get the function prefix for subsequent commands
        func_prefix = func_scpi.replace(":", "")

        # Range configuration
        if range_val is not None:
            self.write(f":SENS:{func_scpi}:RANG {range_val}")
            time.sleep(self.PACING)
            self.write(f":SENS:{func_scpi}:RANG:AUTO OFF")
        elif auto_range:
            self.write(f":SENS:{func_scpi}:RANG:AUTO ON")
        time.sleep(self.PACING)

        # NPLC (integration time)
        if nplc is not None:
            self.write(f":SENS:{func_scpi}:NPLC {nplc}")
            time.sleep(self.PACING)

        # Auto-zero
        if func_scpi in ["VOLT:DC", "CURR:DC", "RES", "FRES"]:
            self.write(f":SENS:{func_scpi}:AZER {'ON' if auto_zero else 'OFF'}")
            time.sleep(self.PACING)

        # Read back actual settings
        actual_func = self.query(":SENS:FUNC?").strip().strip('"')

        result = {
            "function": actual_func,
        }

        # Query range
        try:
            result["range"] = float(self.query(f":SENS:{func_scpi}:RANG?"))
            result["auto_range"] = self.query(f":SENS:{func_scpi}:RANG:AUTO?").strip() == "1"
        except Exception:
            pass

        # Query NPLC
        try:
            result["nplc"] = float(self.query(f":SENS:{func_scpi}:NPLC?"))
        except Exception:
            pass

        return result

    # ---- Measurement ----

    def measure(self) -> dict:
        """
        Take a single measurement with current configuration.

        Returns:
            Dict with value and function
        """
        try:
            reading = self.query(":READ?")
            value = float(reading)

            func = self.query(":SENS:FUNC?").strip().strip('"')

            return {
                "value": value,
                "function": func,
                "unit": self._get_unit(func)
            }
        except Exception as e:
            logger.error("Measurement failed: %s", e)
            return {"error": str(e)}

    def _get_unit(self, func: str) -> str:
        """Get unit string for a function."""
        units = {
            "VOLT:DC": "V",
            "VOLT:AC": "Vrms",
            "CURR:DC": "A",
            "CURR:AC": "Arms",
            "RES": "Ω",
            "FRES": "Ω",
            "TEMP": "°C",
            "FREQ": "Hz",
            "PER": "s",
            "DIOD": "V",
            "CONT": "Ω",
            "CAP": "F",
        }
        return units.get(func, "")

    def measure_dcv(self, range_val: Optional[float] = None, nplc: float = 1) -> dict:
        """
        Quick DC voltage measurement.

        Args:
            range_val: Manual range (None for auto)
            nplc: Integration time (default 1)

        Returns:
            Dict with voltage_v
        """
        self.configure("dcv", range_val=range_val, nplc=nplc)
        result = self.measure()
        if "error" not in result:
            result["voltage_v"] = result.pop("value")
        return result

    def measure_dci(self, range_val: Optional[float] = None, nplc: float = 1) -> dict:
        """
        Quick DC current measurement.

        Args:
            range_val: Manual range (None for auto)
            nplc: Integration time (default 1)

        Returns:
            Dict with current_a
        """
        self.configure("dci", range_val=range_val, nplc=nplc)
        result = self.measure()
        if "error" not in result:
            result["current_a"] = result.pop("value")
        return result

    def measure_resistance(
        self,
        four_wire: bool = False,
        range_val: Optional[float] = None,
        nplc: float = 1
    ) -> dict:
        """
        Quick resistance measurement.

        Args:
            four_wire: Use 4-wire measurement
            range_val: Manual range (None for auto)
            nplc: Integration time (default 1)

        Returns:
            Dict with resistance_ohm
        """
        func = "fres" if four_wire else "res"
        self.configure(func, range_val=range_val, nplc=nplc)
        result = self.measure()
        if "error" not in result:
            result["resistance_ohm"] = result.pop("value")
            result["four_wire"] = four_wire
        return result

    def measure_temperature(self, sensor: str = "RTD", rtd_type: str = "PT100") -> dict:
        """
        Quick temperature measurement.

        Args:
            sensor: Sensor type (RTD, THER, TC)
            rtd_type: RTD type if using RTD (PT100, PT385, PT3916)

        Returns:
            Dict with temperature_c
        """
        self.write(':SENS:FUNC "TEMP"')
        time.sleep(self.PACING)

        if sensor.upper() == "RTD":
            self.write(":SENS:TEMP:TRAN FRTD")
            time.sleep(self.PACING)
            self.write(f":SENS:TEMP:RTD:FOUR {rtd_type}")
        elif sensor.upper() == "THER":
            self.write(":SENS:TEMP:TRAN THER")
        time.sleep(self.PACING)

        result = self.measure()
        if "error" not in result:
            result["temperature_c"] = result.pop("value")
            result["sensor"] = sensor
        return result

    def measure_frequency(self, range_val: Optional[float] = None) -> dict:
        """
        Measure frequency.

        Args:
            range_val: Expected frequency range

        Returns:
            Dict with frequency_hz
        """
        self.configure("freq", range_val=range_val)
        result = self.measure()
        if "error" not in result:
            result["frequency_hz"] = result.pop("value")
        return result

    def measure_capacitance(self, range_val: Optional[float] = None) -> dict:
        """
        Measure capacitance.

        Args:
            range_val: Expected capacitance range

        Returns:
            Dict with capacitance_f
        """
        self.configure("cap", range_val=range_val)
        result = self.measure()
        if "error" not in result:
            result["capacitance_f"] = result.pop("value")
        return result

    def measure_diode(self) -> dict:
        """
        Diode test measurement.

        Returns:
            Dict with forward_v
        """
        self.write(':SENS:FUNC "DIOD"')
        time.sleep(self.PACING)
        result = self.measure()
        if "error" not in result:
            result["forward_v"] = result.pop("value")
        return result

    def measure_continuity(self) -> dict:
        """
        Continuity test measurement.

        Returns:
            Dict with resistance_ohm and continuity (bool)
        """
        self.write(':SENS:FUNC "CONT"')
        time.sleep(self.PACING)
        result = self.measure()
        if "error" not in result:
            val = result.pop("value")
            result["resistance_ohm"] = val
            result["continuity"] = val < 10  # Typically <10Ω is "continuous"
        return result

    # ---- Display ----

    def display_text(self, line1: str = "", line2: str = "") -> dict:
        """
        Set user text on display.

        Args:
            line1: Text for line 1 (max ~20 chars)
            line2: Text for line 2 (max ~20 chars)

        Returns:
            Dict with ok status
        """
        if line1:
            self.write(f':DISP:USER1:TEXT "{line1}"')
            time.sleep(self.PACING)
        if line2:
            self.write(f':DISP:USER2:TEXT "{line2}"')
            time.sleep(self.PACING)

        self.write(":DISP:SCREEN USER")
        return {"ok": True, "line1": line1, "line2": line2}

    def display_clear(self) -> dict:
        """
        Clear display and return to home screen.

        Returns:
            Dict with ok status
        """
        self.write(":DISP:CLEAR")
        time.sleep(self.PACING)
        self.write(":DISP:SCREEN HOME")
        return {"ok": True}

    # ---- System ----

    def get_line_frequency(self) -> dict:
        """
        Query detected line frequency.

        Returns:
            Dict with line_freq_hz (50 or 60)
        """
        freq = self.query(":SYST:LFR?")
        return {"line_freq_hz": int(float(freq))}
