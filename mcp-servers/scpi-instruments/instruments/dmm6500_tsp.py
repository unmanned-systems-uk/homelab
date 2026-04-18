#!/usr/bin/env python3
"""
DMM6500 TSP Driver - Keithley 6½-Digit Multimeter (TSP Mode).

Test Script Processor (TSP) is a Lua-based scripting language for
advanced instrument automation. This driver provides TSP command
access when the DMM6500 is set to TSP mode.

TSP mode is set from front panel: System → Settings → Command Set → TSP
"""

import logging
import time
import json
from typing import Optional, Dict, Any, List, Union

from .base import BaseInstrument

logger = logging.getLogger(__name__)

# TSP function constants
TSP_FUNCTIONS = {
    "dcv": "dmm.FUNC_DC_VOLTAGE",
    "acv": "dmm.FUNC_AC_VOLTAGE",
    "dci": "dmm.FUNC_DC_CURRENT",
    "aci": "dmm.FUNC_AC_CURRENT",
    "res": "dmm.FUNC_RESISTANCE",
    "fres": "dmm.FUNC_4W_RESISTANCE",
    "temp": "dmm.FUNC_TEMPERATURE",
    "freq": "dmm.FUNC_FREQUENCY",
    "cap": "dmm.FUNC_CAPACITANCE",
    "diode": "dmm.FUNC_DIODE",
    "cont": "dmm.FUNC_CONTINUITY",
}

# TSP digitize function constants
TSP_DIGITIZE_FUNCTIONS = {
    "dcv": "dmm.FUNC_DIGITIZE_VOLTAGE",
    "dci": "dmm.FUNC_DIGITIZE_CURRENT",
}

# Units for functions
UNITS = {
    "dmm.FUNC_DC_VOLTAGE": "V",
    "dmm.FUNC_AC_VOLTAGE": "Vrms",
    "dmm.FUNC_DC_CURRENT": "A",
    "dmm.FUNC_AC_CURRENT": "Arms",
    "dmm.FUNC_RESISTANCE": "Ω",
    "dmm.FUNC_4W_RESISTANCE": "Ω",
    "dmm.FUNC_TEMPERATURE": "°C",
    "dmm.FUNC_FREQUENCY": "Hz",
    "dmm.FUNC_CAPACITANCE": "F",
    "dmm.FUNC_DIODE": "V",
    "dmm.FUNC_CONTINUITY": "Ω",
}


class DMM6500_TSP(BaseInstrument):
    """
    Driver for Keithley DMM6500 6½-Digit Multimeter in TSP mode.

    TSP (Test Script Processor) uses Lua-based commands for advanced
    automation including buffers, triggers, and high-speed digitizing.

    Key TSP objects:
    - dmm.measure - Standard measurement configuration
    - dmm.digitize - High-speed sampling
    - buffer - Data storage
    - trigger.model - Sequenced operations
    """

    PACING = 0.03  # 30ms between commands

    def get_type(self) -> str:
        return "dmm6500_tsp"

    def post_reset(self) -> None:
        """Post-reset initialization for TSP mode."""
        time.sleep(0.5)
        # Clear event log
        self.tsp_write("eventlog.clear()")

    # ========================================================================
    # TSP Command Interface
    # ========================================================================

    def tsp_write(self, cmd: str) -> None:
        """
        Send a TSP command (no response expected).

        Args:
            cmd: TSP Lua command (e.g., "dmm.measure.func = dmm.FUNC_DC_VOLTAGE")
        """
        self._sock.write(cmd)
        time.sleep(self.PACING)
        logger.debug("TSP WRITE: %s", cmd)

    def tsp_query(self, expr: str) -> str:
        """
        Query a TSP expression and return the result.

        Wraps expression in print() to get the value back.

        Args:
            expr: TSP Lua expression (e.g., "dmm.measure.read()")

        Returns:
            String response from instrument
        """
        # Wrap in print() if not already
        if not expr.strip().startswith("print"):
            cmd = f"print({expr})"
        else:
            cmd = expr

        response = self._sock.query(cmd)
        logger.debug("TSP QUERY: %s -> %s", expr, response[:80] if len(response) > 80 else response)
        return response

    def tsp_execute(self, script: str) -> dict:
        """
        Execute arbitrary TSP Lua script.

        Args:
            script: Multi-line TSP Lua code

        Returns:
            Dict with ok status and any output
        """
        try:
            # Split into lines and send each
            lines = script.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('--'):
                    self.tsp_write(line)

            return {"ok": True, "lines_executed": len(lines)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========================================================================
    # Reset and Identification
    # ========================================================================

    def reset(self) -> dict:
        """
        Reset DMM to default state.

        Returns:
            Dict with ok status
        """
        self.tsp_write("reset()")
        time.sleep(1.0)  # Reset needs settling time
        self.post_reset()
        return {"ok": True, "mode": "tsp"}

    def get_identity(self) -> dict:
        """
        Get instrument identity in TSP mode.

        Returns:
            Dict with model, serial, firmware
        """
        model = self.tsp_query("localnode.model")
        serial = self.tsp_query("localnode.serialno")
        firmware = self.tsp_query("localnode.revision")

        return {
            "model": model,
            "serial": serial,
            "firmware": firmware,
            "mode": "tsp"
        }

    # ========================================================================
    # Basic Measurement Configuration
    # ========================================================================

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
        # Map friendly name to TSP function
        func_tsp = TSP_FUNCTIONS.get(function.lower())
        if not func_tsp:
            return {"error": f"Unknown function: {function}"}

        # Set function
        self.tsp_write(f"dmm.measure.func = {func_tsp}")

        # Range configuration
        if range_val is not None:
            self.tsp_write(f"dmm.measure.range = {range_val}")
            self.tsp_write("dmm.measure.autorange = dmm.OFF")
        elif auto_range:
            self.tsp_write("dmm.measure.autorange = dmm.ON")

        # NPLC (integration time)
        if nplc is not None:
            self.tsp_write(f"dmm.measure.nplc = {nplc}")

        # Auto-zero (only for applicable functions)
        if function.lower() in ["dcv", "dci", "res", "fres"]:
            az_val = "dmm.ON" if auto_zero else "dmm.OFF"
            self.tsp_write(f"dmm.measure.autozero.enable = {az_val}")

        # Read back settings
        actual_func = self.tsp_query("dmm.measure.func")
        actual_range = self.tsp_query("dmm.measure.range")
        actual_nplc = self.tsp_query("dmm.measure.nplc")

        return {
            "function": actual_func,
            "range": float(actual_range) if actual_range else None,
            "nplc": float(actual_nplc) if actual_nplc else None,
            "mode": "tsp"
        }

    # ========================================================================
    # Basic Measurements
    # ========================================================================

    def measure(self) -> dict:
        """
        Take a single measurement with current configuration.

        Returns:
            Dict with value, function, and unit
        """
        try:
            reading = self.tsp_query("dmm.measure.read()")
            value = float(reading)

            func = self.tsp_query("dmm.measure.func")
            unit = UNITS.get(func, "")

            return {
                "value": value,
                "function": func,
                "unit": unit,
                "mode": "tsp"
            }
        except Exception as e:
            return {"error": str(e)}

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
            result["voltage_v"] = result.get("value")
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
            result["current_a"] = result.get("value")
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
            result["resistance_ohm"] = result.get("value")
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
        self.tsp_write("dmm.measure.func = dmm.FUNC_TEMPERATURE")

        if sensor.upper() == "RTD":
            self.tsp_write("dmm.measure.transducer = dmm.TRANS_FOURRTD")
            rtd_map = {"PT100": "dmm.RTD_PT100", "PT385": "dmm.RTD_PT385", "PT3916": "dmm.RTD_PT3916"}
            rtd_const = rtd_map.get(rtd_type.upper(), "dmm.RTD_PT100")
            self.tsp_write(f"dmm.measure.fourrtd = {rtd_const}")
        elif sensor.upper() == "THER":
            self.tsp_write("dmm.measure.transducer = dmm.TRANS_THERMISTOR")

        result = self.measure()
        if "error" not in result:
            result["temperature_c"] = result.get("value")
            result["sensor"] = sensor
        return result

    # ========================================================================
    # Digitizing (High-Speed Sampling)
    # ========================================================================

    def digitize_configure(
        self,
        function: str = "dcv",
        sample_rate: int = 1000,
        count: int = 1000,
        range_val: Optional[float] = None
    ) -> dict:
        """
        Configure digitizing mode for high-speed sampling.

        Args:
            function: Digitize function (dcv or dci)
            sample_rate: Samples per second (1 to 1,000,000)
            count: Number of samples to capture
            range_val: Manual range (None for auto)

        Returns:
            Dict with configuration
        """
        func_tsp = TSP_DIGITIZE_FUNCTIONS.get(function.lower())
        if not func_tsp:
            return {"error": f"Unknown digitize function: {function}. Use 'dcv' or 'dci'"}

        self.tsp_write(f"dmm.digitize.func = {func_tsp}")
        self.tsp_write(f"dmm.digitize.samplerate = {sample_rate}")
        self.tsp_write(f"dmm.digitize.count = {count}")

        if range_val is not None:
            self.tsp_write(f"dmm.digitize.range = {range_val}")
        else:
            self.tsp_write("dmm.digitize.range = dmm.RANGE_AUTO")

        return {
            "function": func_tsp,
            "sample_rate": sample_rate,
            "count": count,
            "range": range_val,
            "mode": "tsp"
        }

    def digitize_read(self, buffer_name: str = "defbuffer1") -> dict:
        """
        Read digitized samples from buffer.

        Args:
            buffer_name: Buffer to read from (default "defbuffer1")

        Returns:
            Dict with samples list and statistics
        """
        try:
            # Get buffer size
            n = int(float(self.tsp_query(f"{buffer_name}.n")))

            if n == 0:
                return {"error": "Buffer is empty", "count": 0}

            # Read all data
            samples = []
            # Read in chunks to avoid timeout
            chunk_size = 100
            for start in range(1, n + 1, chunk_size):
                end = min(start + chunk_size - 1, n)
                data = self.tsp_query(f"printbuffer({start}, {end}, {buffer_name}.readings)")
                values = [float(x) for x in data.split(',')]
                samples.extend(values)

            return {
                "samples": samples,
                "count": len(samples),
                "min": min(samples),
                "max": max(samples),
                "avg": sum(samples) / len(samples),
                "buffer": buffer_name,
                "mode": "tsp"
            }
        except Exception as e:
            return {"error": str(e)}

    def digitize_trigger(
        self,
        edge_level: float,
        slope: str = "rising",
        pre_trigger: int = 0
    ) -> dict:
        """
        Configure analog trigger for digitizing.

        Args:
            edge_level: Trigger level (voltage or current)
            slope: Trigger slope ("rising" or "falling")
            pre_trigger: Number of pre-trigger samples

        Returns:
            Dict with trigger configuration
        """
        slope_tsp = "dmm.SLOPE_RISING" if slope.lower() == "rising" else "dmm.SLOPE_FALLING"

        self.tsp_write("dmm.digitize.analogtrigger.mode = dmm.MODE_EDGE")
        self.tsp_write(f"dmm.digitize.analogtrigger.edge.level = {edge_level}")
        self.tsp_write(f"dmm.digitize.analogtrigger.edge.slope = {slope_tsp}")

        if pre_trigger > 0:
            # Configure trigger model for pre-trigger
            self.tsp_write(f'trigger.model.load("Empty")')
            # Additional trigger model config would go here

        return {
            "trigger_mode": "edge",
            "level": edge_level,
            "slope": slope,
            "pre_trigger": pre_trigger,
            "mode": "tsp"
        }

    # ========================================================================
    # Buffer Operations
    # ========================================================================

    def buffer_create(
        self,
        name: str,
        capacity: int = 1000,
        style: str = "standard"
    ) -> dict:
        """
        Create a reading buffer.

        Args:
            name: Buffer variable name
            capacity: Number of readings to store
            style: Buffer style ("standard", "writable", "compact")

        Returns:
            Dict with buffer info
        """
        style_map = {
            "standard": "buffer.STYLE_STANDARD",
            "writable": "buffer.STYLE_WRITABLE",
            "compact": "buffer.STYLE_COMPACT",
        }
        style_tsp = style_map.get(style.lower(), "buffer.STYLE_STANDARD")

        self.tsp_write(f"{name} = buffer.make({capacity}, {style_tsp})")

        return {
            "buffer": name,
            "capacity": capacity,
            "style": style,
            "mode": "tsp"
        }

    def buffer_read(
        self,
        buffer_name: str = "defbuffer1",
        start: int = 1,
        count: Optional[int] = None
    ) -> dict:
        """
        Read data from a buffer.

        Args:
            buffer_name: Buffer to read from
            start: Starting index (1-based)
            count: Number of readings (None for all)

        Returns:
            Dict with readings list
        """
        try:
            n = int(float(self.tsp_query(f"{buffer_name}.n")))
            if n == 0:
                return {"readings": [], "count": 0, "buffer": buffer_name}

            end = n if count is None else min(start + count - 1, n)

            data = self.tsp_query(f"printbuffer({start}, {end}, {buffer_name}.readings)")
            readings = [float(x) for x in data.split(',')]

            return {
                "readings": readings,
                "count": len(readings),
                "buffer": buffer_name,
                "start": start,
                "end": end,
                "mode": "tsp"
            }
        except Exception as e:
            return {"error": str(e)}

    def buffer_clear(self, buffer_name: str = "defbuffer1") -> dict:
        """
        Clear a buffer.

        Args:
            buffer_name: Buffer to clear

        Returns:
            Dict with ok status
        """
        self.tsp_write(f"{buffer_name}.clear()")
        return {"ok": True, "buffer": buffer_name, "mode": "tsp"}

    def buffer_stats(self, buffer_name: str = "defbuffer1") -> dict:
        """
        Get buffer statistics.

        Args:
            buffer_name: Buffer to analyze

        Returns:
            Dict with min, max, avg, count
        """
        try:
            n = int(float(self.tsp_query(f"{buffer_name}.n")))
            if n == 0:
                return {"count": 0, "buffer": buffer_name, "mode": "tsp"}

            # Use buffer statistics functions
            stats_min = float(self.tsp_query(f"buffer.getstats({buffer_name}).min"))
            stats_max = float(self.tsp_query(f"buffer.getstats({buffer_name}).max"))
            stats_mean = float(self.tsp_query(f"buffer.getstats({buffer_name}).mean"))
            stats_stddev = float(self.tsp_query(f"buffer.getstats({buffer_name}).stddev"))

            return {
                "count": n,
                "min": stats_min,
                "max": stats_max,
                "mean": stats_mean,
                "stddev": stats_stddev,
                "buffer": buffer_name,
                "mode": "tsp"
            }
        except Exception as e:
            return {"error": str(e)}

    # ========================================================================
    # Trigger Model
    # ========================================================================

    def trigger_load(
        self,
        template: str,
        count: int = 1,
        **kwargs
    ) -> dict:
        """
        Load a trigger model template.

        Args:
            template: Template name ("SimpleLoop", "DurationLoop", "LoopUntilEvent", etc.)
            count: Number of readings/loops
            **kwargs: Additional template parameters

        Returns:
            Dict with trigger model info
        """
        # Build template call
        if template == "SimpleLoop":
            self.tsp_write(f'trigger.model.load("SimpleLoop", {count})')
        elif template == "DurationLoop":
            duration = kwargs.get("duration", 10)
            self.tsp_write(f'trigger.model.load("DurationLoop", {duration})')
        elif template == "GradeBinning":
            self.tsp_write(f'trigger.model.load("GradeBinning")')
        elif template == "Empty":
            self.tsp_write('trigger.model.load("Empty")')
        else:
            return {"error": f"Unknown template: {template}"}

        return {
            "template": template,
            "count": count,
            "mode": "tsp"
        }

    def trigger_initiate(self) -> dict:
        """
        Start the trigger model.

        Returns:
            Dict with ok status
        """
        self.tsp_write("trigger.model.initiate()")
        return {"ok": True, "action": "initiated", "mode": "tsp"}

    def trigger_abort(self) -> dict:
        """
        Abort the running trigger model.

        Returns:
            Dict with ok status
        """
        self.tsp_write("trigger.model.abort()")
        return {"ok": True, "action": "aborted", "mode": "tsp"}

    def trigger_wait(self, timeout_s: float = 10.0) -> dict:
        """
        Wait for trigger model to complete.

        Args:
            timeout_s: Maximum wait time in seconds

        Returns:
            Dict with completion status
        """
        # waitcomplete() blocks until done
        self.tsp_write(f"waitcomplete({timeout_s})")
        state = self.tsp_query("trigger.model.state()")

        return {
            "state": state,
            "completed": "IDLE" in state.upper(),
            "mode": "tsp"
        }

    # ========================================================================
    # Error Handling
    # ========================================================================

    def get_errors(self) -> dict:
        """
        Read event log errors.

        Returns:
            Dict with error list
        """
        errors = []
        count = int(float(self.tsp_query("eventlog.getcount(eventlog.SEV_ERROR)")))

        for _ in range(min(count, 10)):  # Max 10 errors
            entry = self.tsp_query("eventlog.next()")
            if entry:
                errors.append(entry)

        return {"errors": errors, "count": len(errors), "mode": "tsp"}

    def clear_errors(self) -> int:
        """
        Clear event log.

        Returns:
            Number of errors cleared
        """
        count = int(float(self.tsp_query("eventlog.getcount(eventlog.SEV_ERROR)")))
        self.tsp_write("eventlog.clear()")
        return count
