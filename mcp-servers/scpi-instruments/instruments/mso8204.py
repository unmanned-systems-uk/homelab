#!/usr/bin/env python3
"""
MSO8204 - Rigol Mixed Signal Oscilloscope Driver.

4 analog channels + 16 digital channels.
2 GHz bandwidth, 10 GSa/s sample rate.
"""

import logging
import time
from typing import List, Optional, Dict, Any

from .base import BaseInstrument

logger = logging.getLogger(__name__)

# Available measurements
MEASUREMENTS = [
    "FREQuency", "PERiod", "VPP", "VMAX", "VMIN", "VAMPlitude",
    "VTOP", "VBASe", "VAVerage", "VRMS", "OVERshoot", "PREShoot",
    "RISetime", "FALLtime", "PDUTy", "NDUTy", "PWIDth", "NWIDth"
]

# Measurements for full characterisation
CHARACTERISE_MEASUREMENTS = [
    "FREQuency", "PERiod", "VPP", "VAMPlitude", "VTOP", "VBASe",
    "VRMS", "VMAX", "VMIN", "RISetime", "FALLtime", "PDUTy", "NDUTy",
    "OVERshoot", "PREShoot"
]


class MSO8204(BaseInstrument):
    """
    Driver for Rigol MSO8204 Mixed Signal Oscilloscope.

    Channels: 4 analog (CHANnel1-4) + 16 digital (D0-D15)
    Bandwidth: 2 GHz
    Sample rate: 10 GSa/s
    """

    def get_type(self) -> str:
        return "mso8204"

    def post_reset(self) -> None:
        """Post-reset initialization."""
        time.sleep(0.5)
        self.clear_errors()

    # ---- Channel Configuration ----

    def channel_config(
        self,
        channel: int,
        enabled: bool = True,
        scale_v_div: Optional[float] = None,
        offset_v: Optional[float] = None,
        coupling: Optional[str] = None,
        probe_ratio: Optional[float] = None,
        bw_limit: Optional[bool] = None
    ) -> dict:
        """
        Configure an oscilloscope channel.

        Args:
            channel: Channel number (1-4)
            enabled: Enable/disable channel display
            scale_v_div: Vertical scale (V/div)
            offset_v: Vertical offset (V)
            coupling: Input coupling ("AC", "DC", "GND")
            probe_ratio: Probe attenuation ratio (1, 10, 100, etc.)
            bw_limit: Enable 20 MHz bandwidth limit

        Returns:
            Dict with applied settings
        """
        ch = f":CHANnel{channel}"

        # Enable/disable
        self.write(f"{ch}:DISPlay {'ON' if enabled else 'OFF'}")
        time.sleep(self.PACING)

        if scale_v_div is not None:
            self.write(f"{ch}:SCALe {scale_v_div}")
            time.sleep(self.PACING)

        if offset_v is not None:
            self.write(f"{ch}:OFFSet {offset_v}")
            time.sleep(self.PACING)

        if coupling is not None:
            self.write(f"{ch}:COUPling {coupling}")
            time.sleep(self.PACING)

        if probe_ratio is not None:
            self.write(f"{ch}:PROBe {probe_ratio}")
            time.sleep(self.PACING)

        if bw_limit is not None:
            self.write(f"{ch}:BWLimit {'20M' if bw_limit else 'OFF'}")
            time.sleep(self.PACING)

        # Read back settings
        return {
            "channel": channel,
            "enabled": self.query(f"{ch}:DISPlay?").strip() == "1",
            "scale_v_div": float(self.query(f"{ch}:SCALe?")),
            "offset_v": float(self.query(f"{ch}:OFFSet?")),
            "coupling": self.query(f"{ch}:COUPling?").strip(),
            "probe_ratio": float(self.query(f"{ch}:PROBe?")),
            "bw_limit": self.query(f"{ch}:BWLimit?").strip()
        }

    # ---- Timebase Configuration ----

    def timebase(
        self,
        scale_s_div: float,
        offset_s: float = 0,
        mode: str = "MAIN"
    ) -> dict:
        """
        Configure the timebase.

        Args:
            scale_s_div: Time scale (s/div)
            offset_s: Horizontal offset (s)
            mode: Timebase mode ("MAIN", "ZOOM", "ROLL")

        Returns:
            Dict with applied settings
        """
        self.write(f":TIMebase:MODE {mode}")
        time.sleep(self.PACING)
        self.write(f":TIMebase:MAIN:SCALe {scale_s_div}")
        time.sleep(self.PACING)
        self.write(f":TIMebase:MAIN:OFFSet {offset_s}")
        time.sleep(self.PACING)

        return {
            "scale_s_div": float(self.query(":TIMebase:MAIN:SCALe?")),
            "offset_s": float(self.query(":TIMebase:MAIN:OFFSet?")),
            "mode": self.query(":TIMebase:MODE?").strip()
        }

    # ---- Trigger Configuration ----

    def trigger(
        self,
        mode: str = "EDGE",
        source: str = "CHANnel1",
        level_v: float = 0,
        slope: str = "POSitive",
        sweep: str = "NORMal"
    ) -> dict:
        """
        Configure the trigger.

        Args:
            mode: Trigger mode ("EDGE", "PULSe", "SLOPe", etc.)
            source: Trigger source ("CHANnel1"-"CHANnel4", "EXT")
            level_v: Trigger level (V)
            slope: Trigger slope ("POSitive", "NEGative", "RFALl")
            sweep: Sweep mode ("AUTO", "NORMal", "SINGle")

        Returns:
            Dict with trigger settings
        """
        self.write(f":TRIGger:MODE {mode}")
        time.sleep(self.PACING)
        self.write(f":TRIGger:SWEep {sweep}")
        time.sleep(self.PACING)

        if mode.upper() == "EDGE":
            self.write(f":TRIGger:EDGe:SOURce {source}")
            time.sleep(self.PACING)
            self.write(f":TRIGger:EDGe:LEVel {level_v}")
            time.sleep(self.PACING)
            self.write(f":TRIGger:EDGe:SLOPe {slope}")
            time.sleep(self.PACING)

        return {
            "mode": self.query(":TRIGger:MODE?").strip(),
            "source": self.query(":TRIGger:EDGe:SOURce?").strip(),
            "level_v": float(self.query(":TRIGger:EDGe:LEVel?")),
            "slope": self.query(":TRIGger:EDGe:SLOPe?").strip(),
            "sweep": self.query(":TRIGger:SWEep?").strip(),
            "status": self.query(":TRIGger:STATus?").strip()
        }

    # ---- Acquisition Control ----

    def autoscale(self) -> dict:
        """
        Run autoscale on all active channels.

        Returns:
            Dict with ok status
        """
        self.write(":AUToscale")
        time.sleep(0.5)  # Autoscale takes time
        self.query_opc()
        return {"ok": True}

    def acquire(self, mode: str = "RUN") -> dict:
        """
        Control acquisition (run/stop/single).

        Args:
            mode: "RUN", "STOP", or "SINGle"

        Returns:
            Dict with mode and trigger_status
        """
        if mode.upper() == "RUN":
            self.write(":RUN")
        elif mode.upper() == "STOP":
            self.write(":STOP")
        elif mode.upper() == "SINGLE":
            self.write(":SINGle")
        else:
            return {"error": f"Invalid mode: {mode}"}

        time.sleep(self.PACING)
        return {
            "mode": mode.upper(),
            "trigger_status": self.query(":TRIGger:STATus?").strip()
        }

    # ---- Measurements ----

    def measure(self, channel: int, measurements: List[str]) -> dict:
        """
        Take measurements on a channel.

        Args:
            channel: Channel number (1-4)
            measurements: List of measurement names (e.g., ["FREQuency", "VPP"])

        Returns:
            Dict with channel and results mapping
        """
        self.write(f":MEASure:SOURce CHANnel{channel}")
        time.sleep(self.PACING)

        results = {}
        for m in measurements:
            try:
                val = self.query(f":MEASure:{m}?")
                results[m] = float(val)
            except (ValueError, Exception) as e:
                logger.warning("Measurement %s failed: %s", m, e)
                results[m] = None

        return {
            "channel": channel,
            "results": results
        }

    def measure_phase(self, source_a: int, source_b: int) -> dict:
        """
        Measure phase relationship between two channels.

        Args:
            source_a: First channel (1-4)
            source_b: Second channel (1-4)

        Returns:
            Dict with phase measurements in degrees
        """
        self.write(f":MEASure:SetUp:PSA CHANnel{source_a}")
        time.sleep(self.PACING)
        self.write(f":MEASure:SetUp:PSB CHANnel{source_b}")
        time.sleep(self.PACING)

        try:
            rphase = float(self.query(":MEASure:RPHase?"))
        except ValueError:
            rphase = None

        try:
            fphase = float(self.query(":MEASure:FPHase?"))
        except ValueError:
            fphase = None

        return {
            "source_a": source_a,
            "source_b": source_b,
            "phase_rising_deg": rphase,
            "phase_falling_deg": fphase
        }

    # ---- Waveform Data ----

    def waveform(
        self,
        channel: int,
        mode: str = "NORMal",
        fmt: str = "ASCii",
        points: Optional[int] = None
    ) -> dict:
        """
        Capture raw waveform data from a channel.

        Args:
            channel: Channel number (1-4)
            mode: Data mode ("NORMal" = screen, "RAW" = full memory)
            fmt: Data format ("ASCii", "BYTE", "WORD")
            points: Number of points to read (optional)

        Returns:
            Dict with waveform data and scaling parameters
        """
        self.write(f":WAVeform:SOURce CHANnel{channel}")
        time.sleep(self.PACING)
        self.write(f":WAVeform:MODE {mode}")
        time.sleep(self.PACING)
        self.write(f":WAVeform:FORMat {fmt}")
        time.sleep(self.PACING)

        if points is not None:
            self.write(f":WAVeform:POINts {points}")
            time.sleep(self.PACING)

        # Get scaling parameters
        xinc = float(self.query(":WAVeform:XINCrement?"))
        xorig = float(self.query(":WAVeform:XORigin?"))
        yinc = float(self.query(":WAVeform:YINCrement?"))
        yorig = float(self.query(":WAVeform:YORigin?"))
        yref = float(self.query(":WAVeform:YREFerence?"))

        # Get sample rate
        try:
            srate = float(self.query(":ACQuire:SRATe?"))
        except ValueError:
            srate = 1.0 / xinc if xinc > 0 else None

        # Get data
        if fmt.upper() == "ASCII":
            text = self.query(":WAVeform:DATA?")
            # ASCII format returns comma-separated values
            if text.startswith("#"):
                # Block header, strip it
                d = int(text[1])
                text = text[2 + d:]
            raw_values = [float(v) for v in text.split(",") if v.strip()]
            # Convert to voltage
            data = [(v - yref - yorig) * yinc for v in raw_values]
        else:
            # Binary format - return as base64
            import base64
            raw_data = self.query_block(":WAVeform:DATA?")
            data = base64.b64encode(raw_data).decode("ascii")

        actual_points = int(self.query(":WAVeform:POINts?"))

        return {
            "channel": channel,
            "points": actual_points,
            "xinc_s": xinc,
            "xorig_s": xorig,
            "yinc_v": yinc,
            "yorig_v": yorig,
            "yref": yref,
            "sample_rate": srate,
            "format": fmt,
            "data": data
        }

    # ---- FFT ----

    def fft(
        self,
        source_channel: int,
        window: str = "HANNing",
        unit: str = "DB"
    ) -> dict:
        """
        Configure and enable FFT math display.

        Args:
            source_channel: Source channel (1-4)
            window: Window function ("RECTangle", "HANNing", "HAMMing", "BLACkman", "FLATtop")
            unit: Vertical unit ("DB", "VRMS")

        Returns:
            Dict with FFT configuration
        """
        self.write(":MATH:DISPlay ON")
        time.sleep(self.PACING)
        self.write(":MATH:OPERator FFT")
        time.sleep(self.PACING)
        self.write(f":MATH:SOURce1 CHANnel{source_channel}")
        time.sleep(self.PACING)
        self.write(f":MATH:FFT:WINDow {window}")
        time.sleep(self.PACING)
        self.write(f":MATH:FFT:UNIT {unit}")
        time.sleep(self.PACING)

        return {
            "enabled": True,
            "source": source_channel,
            "window": window,
            "unit": unit
        }

    # ---- Screenshot ----

    def screenshot(self, filename: str, fmt: str = "PNG") -> dict:
        """
        Capture oscilloscope display screenshot.

        Args:
            filename: Output file path
            fmt: Image format ("PNG", "BMP", "JPEG")

        Returns:
            Dict with filename, size_bytes, format
        """
        try:
            data = self.query_block(f":DISPlay:DATA? ON,OFF,{fmt}")
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

    # ---- Composite / Workflow Tools ----

    def characterise_channel(self, channel: int, autoscale: bool = True) -> dict:
        """
        Full signal characterisation on one channel.

        Args:
            channel: Channel number (1-4)
            autoscale: Run autoscale before measuring

        Returns:
            Comprehensive measurement results
        """
        # Enable channel
        self.write(f":CHANnel{channel}:DISPlay ON")
        time.sleep(self.PACING)

        if autoscale:
            self.autoscale()

        # Set up trigger
        self.write(":TRIGger:MODE EDGE")
        time.sleep(self.PACING)
        self.write(f":TRIGger:EDGe:SOURce CHANnel{channel}")
        time.sleep(self.PACING)
        self.write(":TRIGger:SWEep NORMal")
        time.sleep(self.PACING)

        # Single acquisition
        self.write(":SINGle")
        time.sleep(0.5)
        self.query_opc()

        # Take measurements
        self.write(f":MEASure:SOURce CHANnel{channel}")
        time.sleep(self.PACING)

        results = {
            "channel": channel,
            "coupling": self.query(f":CHANnel{channel}:COUPling?").strip(),
            "probe_ratio": float(self.query(f":CHANnel{channel}:PROBe?"))
        }

        # Measure all parameters
        for m in CHARACTERISE_MEASUREMENTS:
            try:
                val = float(self.query(f":MEASure:{m}?"))
                # Map SCPI names to result keys
                key_map = {
                    "FREQuency": "frequency_hz",
                    "PERiod": "period_s",
                    "VPP": "vpp_v",
                    "VAMPlitude": "amplitude_v",
                    "VTOP": "vtop_v",
                    "VBASe": "vbase_v",
                    "VRMS": "vrms_v",
                    "VMAX": "vmax_v",
                    "VMIN": "vmin_v",
                    "RISetime": "rise_time_s",
                    "FALLtime": "fall_time_s",
                    "PDUTy": "duty_cycle_pos_pct",
                    "NDUTy": "duty_cycle_neg_pct",
                    "OVERshoot": "overshoot_pct",
                    "PREShoot": "preshoot_pct"
                }
                results[key_map.get(m, m.lower())] = val
            except (ValueError, Exception):
                results[m.lower()] = None

        # Infer waveform shape from measurements
        results["waveform_shape"] = self._infer_waveform_shape(results)

        return results

    def _infer_waveform_shape(self, measurements: dict) -> str:
        """Infer waveform shape from duty cycle and edge times."""
        duty = measurements.get("duty_cycle_pos_pct")
        rise = measurements.get("rise_time_s")
        fall = measurements.get("fall_time_s")
        period = measurements.get("period_s")

        if duty is None or rise is None or fall is None or period is None:
            return "UNKNOWN"

        # Calculate edge time ratio to period
        edge_ratio = (rise + fall) / period if period > 0 else 0

        if 45 < duty < 55:  # ~50% duty cycle
            if edge_ratio < 0.1:
                return "SQUARE"
            else:
                return "SINE"
        elif duty < 45:
            if edge_ratio < 0.1:
                return "PULSE"
            else:
                return "TRIANGLE"
        else:
            return "UNKNOWN"

    def characterise_dual(
        self,
        channel_a: int,
        channel_b: int,
        autoscale: bool = True
    ) -> dict:
        """
        Full characterisation of two channels plus phase relationship.

        Args:
            channel_a: First channel (1-4)
            channel_b: Second channel (1-4)
            autoscale: Run autoscale before measuring

        Returns:
            Dict with both channel results and phase measurements
        """
        result_a = self.characterise_channel(channel_a, autoscale)
        result_b = self.characterise_channel(channel_b, False)  # Don't autoscale again
        phase = self.measure_phase(channel_a, channel_b)

        return {
            "channel_a": result_a,
            "channel_b": result_b,
            "phase_rising_deg": phase["phase_rising_deg"],
            "phase_falling_deg": phase["phase_falling_deg"]
        }
