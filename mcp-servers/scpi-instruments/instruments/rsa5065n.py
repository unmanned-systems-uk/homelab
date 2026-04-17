#!/usr/bin/env python3
"""
RSA5065N - Rigol Real-Time Spectrum Analyser Driver.

Handles all RSA5065N-specific SCPI commands and quirks:
- *RST resets to RTSA mode (must switch to SA)
- :FREQ: not :SENS:FREQ: for frequency writes
- 50 ms pacing required between commands
- :POW:ATT (not :INP:ATT), minimum 10 dB
- FORM:DATA persists across *RST
"""

import logging
import time
from typing import List, Optional

from .base import BaseInstrument
from scpi_transport import SCPISocket

logger = logging.getLogger(__name__)

# Valid sweep point counts for RSA5065N
VALID_POINTS = [201, 401, 601, 801, 1001, 1601, 2001, 3201, 4001, 8001]


class RSA5065N(BaseInstrument):
    """
    Driver for Rigol RSA5065N Real-Time Spectrum Analyser.

    Frequency range: 9 kHz - 6.5 GHz
    Modes: SA (swept), RTSA (real-time)
    """

    def get_type(self) -> str:
        return "rsa5065n"

    def post_reset(self) -> None:
        """Switch to SA mode after reset (RST leaves in RTSA mode)."""
        self.write(":INST:SEL SA")
        time.sleep(1.5)  # Mode switch needs settling
        self.write(":FORM:DATA ASC")  # Force ASCII format
        time.sleep(self.PACING)

    def reset(self) -> dict:
        """Reset and initialize for swept SA mode."""
        result = super().reset()
        self.post_reset()
        return result

    # ---- Sweep Configuration ----

    def configure_sweep(
        self,
        start_hz: float,
        stop_hz: float,
        rbw_hz: float = 10e3,
        vbw_hz: float = 10e3,
        ref_level_dbm: float = -20.0,
        att_db: float = 0,
        points: int = 1001
    ) -> dict:
        """
        Configure the RSA5065N for a swept spectrum measurement.

        Args:
            start_hz: Start frequency in Hz
            stop_hz: Stop frequency in Hz
            rbw_hz: Resolution bandwidth in Hz
            vbw_hz: Video bandwidth in Hz
            ref_level_dbm: Reference level in dBm
            att_db: Input attenuation in dB (10, 20, 30...). 0 = auto.
            points: Number of sweep points (will be rounded to valid value)

        Returns:
            Dict with actual_points, actual_rbw_hz, actual_vbw_hz
        """
        logger.info(
            "Configuring sweep: %.1f-%.1f MHz, RBW %.1f kHz, %d points",
            start_hz / 1e6, stop_hz / 1e6, rbw_hz / 1e3, points
        )

        # Ensure SA (swept) mode
        self.write(":INST:SEL SA")
        time.sleep(1.5)

        # Force ASCII trace format (NOT reset by *RST)
        self.write(":FORM:DATA ASC")
        time.sleep(self.PACING)

        # Frequency span - use :FREQ: not :SENS:FREQ:
        self.write(f":FREQ:STAR {start_hz:.0f}")
        time.sleep(self.PACING)
        self.write(f":FREQ:STOP {stop_hz:.0f}")
        time.sleep(self.PACING)

        # Bandwidth
        self.write(f":SENS:BAND:RES {rbw_hz:.0f}")
        time.sleep(self.PACING)
        self.write(f":SENS:BAND:VID {vbw_hz:.0f}")
        time.sleep(self.PACING)

        # Reference level
        self.write(f":DISP:WIND:TRAC:Y:RLEV {ref_level_dbm:.1f}")
        time.sleep(self.PACING)

        # Attenuation: :POW:ATT not :INP:ATT, min 10 dB
        if att_db > 0:
            self.write(f":POW:ATT {int(att_db)}")
        else:
            self.write(":POW:ATT:AUTO ON")
        time.sleep(self.PACING)

        # Sweep points (instrument rounds to valid values)
        self.write(f":SENS:SWE:POIN {points}")
        time.sleep(self.PACING)
        self.clear_errors()  # Absorb any rounding errors

        # Read back actual values
        actual_points = int(self.query(":SENS:SWE:POIN?"))
        actual_rbw = float(self.query(":SENS:BAND:RES?"))
        actual_vbw = float(self.query(":SENS:BAND:VID?"))

        if actual_points != points:
            logger.warning(
                "Requested %d points, instrument rounded to %d",
                points, actual_points
            )

        # Verify frequency settings
        actual_start = float(self.query(":FREQ:STAR?"))
        actual_stop = float(self.query(":FREQ:STOP?"))

        if abs(actual_start - start_hz) > 1e3 or abs(actual_stop - stop_hz) > 1e3:
            logger.warning(
                "Frequency mismatch: got %.0f-%.0f Hz, wanted %.0f-%.0f Hz",
                actual_start, actual_stop, start_hz, stop_hz
            )

        return {
            "actual_points": actual_points,
            "actual_rbw_hz": actual_rbw,
            "actual_vbw_hz": actual_vbw,
            "start_hz": actual_start,
            "stop_hz": actual_stop
        }

    def single_sweep(self) -> dict:
        """
        Trigger a single sweep and wait for completion.

        Returns:
            Dict with elapsed_s
        """
        self.write(":INIT:CONT OFF")  # Single sweep mode
        t0 = time.time()
        self.write(":INIT:IMM")  # Trigger sweep
        self.query_opc()  # Wait for completion
        elapsed = time.time() - t0
        logger.info("Sweep completed in %.3fs", elapsed)
        return {"elapsed_s": elapsed}

    def get_trace(self, trace: int = 1) -> dict:
        """
        Read trace data from instrument.

        Args:
            trace: Trace number (1, 2, or 3)

        Returns:
            Dict with trace_dbm (list of floats) and points count
        """
        cmd = f":TRAC:DATA? TRACE{trace}"
        text = self.query(cmd)
        values = [float(v) for v in text.split(",")]

        logger.info(
            "Trace %d: %d points, min=%.1f dBm, max=%.1f dBm",
            trace, len(values), min(values), max(values)
        )

        return {
            "trace_dbm": values,
            "points": len(values),
            "min_dbm": min(values),
            "max_dbm": max(values)
        }

    def sweep(self, trace: int = 1) -> dict:
        """
        Execute single sweep and return trace data.

        Args:
            trace: Trace number to read (1-3)

        Returns:
            Dict with trace_dbm, points, elapsed_s
        """
        sweep_result = self.single_sweep()
        trace_result = self.get_trace(trace)
        return {
            **trace_result,
            "elapsed_s": sweep_result["elapsed_s"]
        }

    def capture_burst(
        self,
        n: int,
        start_hz: float,
        stop_hz: float,
        rbw_hz: float = 10e3,
        points: int = 1001
    ) -> dict:
        """
        Capture N consecutive sweeps.

        Args:
            n: Number of sweeps to capture
            start_hz: Start frequency in Hz
            stop_hz: Stop frequency in Hz
            rbw_hz: Resolution bandwidth in Hz
            points: Sweep points

        Returns:
            Dict with sweeps list and actual_points
        """
        config = self.configure_sweep(
            start_hz=start_hz,
            stop_hz=stop_hz,
            rbw_hz=rbw_hz,
            points=points
        )

        sweeps = []
        for i in range(n):
            logger.info("Capturing sweep %d/%d", i + 1, n)
            ts = time.time()
            self.single_sweep()
            trace = self.get_trace(1)
            sweeps.append({
                "timestamp": ts,
                "trace_dbm": trace["trace_dbm"]
            })

        return {
            "sweeps": sweeps,
            "actual_points": config["actual_points"],
            "count": n
        }

    def screenshot(self, filename: str, fmt: str = "BMP") -> dict:
        """
        Capture RSA5065N display screenshot.

        RSA5065N uses :PRIV:SNAP? BMP as primary command.
        """
        try:
            data = self.query_block(f":PRIV:SNAP? {fmt}")
        except Exception:
            logger.info("PRIV:SNAP failed, trying DISP:DATA")
            try:
                data = self.query_block(":DISP:DATA?")
            except Exception as e:
                return {"error": f"Screenshot failed: {e}"}

        with open(filename, "wb") as f:
            f.write(data)

        logger.info("Screenshot saved: %s (%d bytes)", filename, len(data))
        return {
            "filename": filename,
            "size_bytes": len(data),
            "format": fmt
        }

    # ---- Query methods ----

    def get_frequency_range(self) -> dict:
        """Get current frequency range."""
        return {
            "start_hz": float(self.query(":FREQ:STAR?")),
            "stop_hz": float(self.query(":FREQ:STOP?")),
            "center_hz": float(self.query(":FREQ:CENT?")),
            "span_hz": float(self.query(":FREQ:SPAN?"))
        }

    def get_sweep_config(self) -> dict:
        """Get current sweep configuration."""
        return {
            "points": int(self.query(":SENS:SWE:POIN?")),
            "rbw_hz": float(self.query(":SENS:BAND:RES?")),
            "vbw_hz": float(self.query(":SENS:BAND:VID?")),
            "ref_level_dbm": float(self.query(":DISP:WIND:TRAC:Y:RLEV?")),
            "attenuation_db": float(self.query(":POW:ATT?"))
        }

    def get_mode(self) -> str:
        """Get current instrument mode (SA or RTSA)."""
        return self.query(":INST:SEL?").strip()
