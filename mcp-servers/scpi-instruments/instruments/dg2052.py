#!/usr/bin/env python3
"""
DG2052 - Rigol Function/Arbitrary Waveform Generator Driver.

Dual channel, 50 MHz, 250 MSa/s, 16 Mpts arbitrary memory.
"""

import logging
import time
from typing import Optional, Dict, Any

from .base import BaseInstrument

logger = logging.getLogger(__name__)

# Waveform types
WAVEFORMS = {
    "sine": "SIN",
    "square": "SQU",
    "ramp": "RAMP",
    "pulse": "PULS",
    "noise": "NOIS",
    "dc": "DC",
    "arb": "ARB",
}


class DG2052(BaseInstrument):
    """
    Driver for Rigol DG2052 Function/Arbitrary Waveform Generator.

    Specifications:
    - Channels: 2
    - Sine: 1 μHz - 50 MHz
    - Square: 1 μHz - 15 MHz
    - Arb: 1 μHz - 10 MHz
    - Sample rate: 250 MSa/s
    - Memory: 16 Mpts
    """

    def get_type(self) -> str:
        return "dg2052"

    def post_reset(self) -> None:
        """Post-reset initialization."""
        time.sleep(0.5)
        # Ensure outputs are OFF after reset
        self.write(":OUTP1:STAT OFF")
        time.sleep(self.PACING)
        self.write(":OUTP2:STAT OFF")
        time.sleep(self.PACING)
        self.clear_errors()

    # ---- Output Control ----

    def output_state(self, channel: int, enabled: bool) -> dict:
        """
        Enable or disable channel output.

        CAUTION: Enabling output will produce signal on connected device.

        Args:
            channel: Channel number (1 or 2)
            enabled: True to enable, False to disable

        Returns:
            Dict with output state
        """
        self.write(f":OUTP{channel}:STAT {'ON' if enabled else 'OFF'}")
        time.sleep(self.PACING)

        actual = self.query(f":OUTP{channel}:STAT?").strip()
        return {
            "channel": channel,
            "output_enabled": actual in ["1", "ON"],
            "requested": enabled
        }

    def get_output_state(self, channel: int = 1) -> dict:
        """
        Query current output state.

        Args:
            channel: Channel number (1 or 2)

        Returns:
            Dict with output_enabled
        """
        state = self.query(f":OUTP{channel}:STAT?").strip()
        return {
            "channel": channel,
            "output_enabled": state in ["1", "ON"]
        }

    def set_load_impedance(self, channel: int, impedance: float) -> dict:
        """
        Set output load impedance.

        Args:
            channel: Channel number (1 or 2)
            impedance: Load impedance in Ohms (50, 75, etc.) or INF for high-Z

        Returns:
            Dict with impedance setting
        """
        if impedance > 10000:
            self.write(f":OUTP{channel}:LOAD INF")
        else:
            self.write(f":OUTP{channel}:LOAD {impedance}")
        time.sleep(self.PACING)

        return {
            "channel": channel,
            "load_impedance": self.query(f":OUTP{channel}:LOAD?").strip()
        }

    # ---- Basic Waveform Configuration ----

    def configure_waveform(
        self,
        channel: int,
        waveform: str,
        frequency_hz: float,
        amplitude_vpp: float,
        offset_v: float = 0,
        phase_deg: float = 0
    ) -> dict:
        """
        Configure basic waveform parameters.

        Args:
            channel: Channel number (1 or 2)
            waveform: Waveform type (sine, square, ramp, pulse, noise)
            frequency_hz: Frequency in Hz
            amplitude_vpp: Amplitude in Vpp
            offset_v: DC offset in Volts
            phase_deg: Phase in degrees (0-360)

        Returns:
            Dict with applied settings
        """
        ch = f":SOUR{channel}"
        wave_scpi = WAVEFORMS.get(waveform.lower(), waveform.upper())

        # Set waveform type
        self.write(f"{ch}:FUNC {wave_scpi}")
        time.sleep(self.PACING)

        # Set frequency
        self.write(f"{ch}:FREQ {frequency_hz}")
        time.sleep(self.PACING)

        # Set amplitude
        self.write(f"{ch}:VOLT {amplitude_vpp}")
        time.sleep(self.PACING)

        # Set offset
        self.write(f"{ch}:VOLT:OFFS {offset_v}")
        time.sleep(self.PACING)

        # Set phase
        self.write(f"{ch}:PHAS {phase_deg}")
        time.sleep(self.PACING)

        # Read back
        return {
            "channel": channel,
            "waveform": self.query(f"{ch}:FUNC?").strip(),
            "frequency_hz": float(self.query(f"{ch}:FREQ?")),
            "amplitude_vpp": float(self.query(f"{ch}:VOLT?")),
            "offset_v": float(self.query(f"{ch}:VOLT:OFFS?")),
            "phase_deg": float(self.query(f"{ch}:PHAS?")),
        }

    def configure_sine(
        self,
        channel: int,
        frequency_hz: float,
        amplitude_vpp: float,
        offset_v: float = 0,
        phase_deg: float = 0
    ) -> dict:
        """
        Configure sine wave output.

        Args:
            channel: Channel (1 or 2)
            frequency_hz: Frequency (1 μHz - 50 MHz)
            amplitude_vpp: Amplitude in Vpp
            offset_v: DC offset
            phase_deg: Phase (0-360)

        Returns:
            Dict with settings
        """
        return self.configure_waveform(
            channel, "sine", frequency_hz, amplitude_vpp, offset_v, phase_deg
        )

    def configure_square(
        self,
        channel: int,
        frequency_hz: float,
        amplitude_vpp: float,
        duty_cycle_pct: float = 50,
        offset_v: float = 0
    ) -> dict:
        """
        Configure square wave output.

        Args:
            channel: Channel (1 or 2)
            frequency_hz: Frequency (1 μHz - 15 MHz)
            amplitude_vpp: Amplitude in Vpp
            duty_cycle_pct: Duty cycle (0.01-99.99%)
            offset_v: DC offset

        Returns:
            Dict with settings
        """
        result = self.configure_waveform(
            channel, "square", frequency_hz, amplitude_vpp, offset_v
        )

        # Set duty cycle
        ch = f":SOUR{channel}"
        self.write(f"{ch}:FUNC:SQU:DCYC {duty_cycle_pct}")
        time.sleep(self.PACING)

        result["duty_cycle_pct"] = float(self.query(f"{ch}:FUNC:SQU:DCYC?"))
        return result

    def configure_pulse(
        self,
        channel: int,
        frequency_hz: float,
        amplitude_vpp: float,
        width_s: Optional[float] = None,
        duty_cycle_pct: Optional[float] = None,
        rise_time_s: Optional[float] = None,
        fall_time_s: Optional[float] = None,
        offset_v: float = 0
    ) -> dict:
        """
        Configure pulse output.

        Args:
            channel: Channel (1 or 2)
            frequency_hz: Frequency (1 μHz - 15 MHz)
            amplitude_vpp: Amplitude in Vpp
            width_s: Pulse width in seconds (alternative to duty_cycle)
            duty_cycle_pct: Duty cycle (alternative to width)
            rise_time_s: Rise time in seconds
            fall_time_s: Fall time in seconds
            offset_v: DC offset

        Returns:
            Dict with settings
        """
        result = self.configure_waveform(
            channel, "pulse", frequency_hz, amplitude_vpp, offset_v
        )

        ch = f":SOUR{channel}"

        if width_s is not None:
            self.write(f"{ch}:PULS:WIDT {width_s}")
            time.sleep(self.PACING)
        elif duty_cycle_pct is not None:
            self.write(f"{ch}:PULS:DCYC {duty_cycle_pct}")
            time.sleep(self.PACING)

        if rise_time_s is not None:
            self.write(f"{ch}:PULS:TRAN:LEAD {rise_time_s}")
            time.sleep(self.PACING)

        if fall_time_s is not None:
            self.write(f"{ch}:PULS:TRAN:TRA {fall_time_s}")
            time.sleep(self.PACING)

        result["pulse_width_s"] = float(self.query(f"{ch}:PULS:WIDT?"))
        return result

    def configure_ramp(
        self,
        channel: int,
        frequency_hz: float,
        amplitude_vpp: float,
        symmetry_pct: float = 50,
        offset_v: float = 0
    ) -> dict:
        """
        Configure ramp/triangle wave output.

        Args:
            channel: Channel (1 or 2)
            frequency_hz: Frequency (1 μHz - 1.5 MHz)
            amplitude_vpp: Amplitude in Vpp
            symmetry_pct: Symmetry (0-100%, 50% = triangle)
            offset_v: DC offset

        Returns:
            Dict with settings
        """
        result = self.configure_waveform(
            channel, "ramp", frequency_hz, amplitude_vpp, offset_v
        )

        ch = f":SOUR{channel}"
        self.write(f"{ch}:FUNC:RAMP:SYMM {symmetry_pct}")
        time.sleep(self.PACING)

        result["symmetry_pct"] = float(self.query(f"{ch}:FUNC:RAMP:SYMM?"))
        return result

    def configure_noise(
        self,
        channel: int,
        amplitude_vpp: float,
        offset_v: float = 0
    ) -> dict:
        """
        Configure noise output.

        Args:
            channel: Channel (1 or 2)
            amplitude_vpp: Amplitude in Vpp
            offset_v: DC offset

        Returns:
            Dict with settings
        """
        ch = f":SOUR{channel}"

        self.write(f"{ch}:FUNC NOIS")
        time.sleep(self.PACING)
        self.write(f"{ch}:VOLT {amplitude_vpp}")
        time.sleep(self.PACING)
        self.write(f"{ch}:VOLT:OFFS {offset_v}")
        time.sleep(self.PACING)

        return {
            "channel": channel,
            "waveform": "NOISE",
            "amplitude_vpp": float(self.query(f"{ch}:VOLT?")),
            "offset_v": float(self.query(f"{ch}:VOLT:OFFS?")),
        }

    # ---- Sweep Mode ----

    def configure_sweep(
        self,
        channel: int,
        start_hz: float,
        stop_hz: float,
        sweep_time_s: float,
        spacing: str = "linear"
    ) -> dict:
        """
        Configure frequency sweep.

        Args:
            channel: Channel (1 or 2)
            start_hz: Start frequency
            stop_hz: Stop frequency
            sweep_time_s: Sweep time in seconds
            spacing: Sweep spacing (linear or log)

        Returns:
            Dict with sweep settings
        """
        ch = f":SOUR{channel}"

        self.write(f"{ch}:SWE:STAT ON")
        time.sleep(self.PACING)
        self.write(f"{ch}:SWE:FREQ:STAR {start_hz}")
        time.sleep(self.PACING)
        self.write(f"{ch}:SWE:FREQ:STOP {stop_hz}")
        time.sleep(self.PACING)
        self.write(f"{ch}:SWE:TIME {sweep_time_s}")
        time.sleep(self.PACING)

        spacing_scpi = "LIN" if spacing.lower() == "linear" else "LOG"
        self.write(f"{ch}:SWE:SPAC {spacing_scpi}")
        time.sleep(self.PACING)

        return {
            "channel": channel,
            "sweep_enabled": True,
            "start_hz": float(self.query(f"{ch}:SWE:FREQ:STAR?")),
            "stop_hz": float(self.query(f"{ch}:SWE:FREQ:STOP?")),
            "sweep_time_s": float(self.query(f"{ch}:SWE:TIME?")),
            "spacing": self.query(f"{ch}:SWE:SPAC?").strip(),
        }

    def disable_sweep(self, channel: int) -> dict:
        """Disable sweep mode."""
        self.write(f":SOUR{channel}:SWE:STAT OFF")
        return {"channel": channel, "sweep_enabled": False}

    # ---- Burst Mode ----

    def configure_burst(
        self,
        channel: int,
        cycles: int,
        mode: str = "triggered",
        trigger_source: str = "internal",
        burst_period_s: Optional[float] = None
    ) -> dict:
        """
        Configure burst mode.

        Args:
            channel: Channel (1 or 2)
            cycles: Number of cycles per burst
            mode: Burst mode (triggered, gated, infinity)
            trigger_source: Trigger source (internal, external, manual)
            burst_period_s: Burst period for internal trigger

        Returns:
            Dict with burst settings
        """
        ch = f":SOUR{channel}"

        self.write(f"{ch}:BURS:STAT ON")
        time.sleep(self.PACING)

        mode_map = {"triggered": "TRIG", "gated": "GAT", "infinity": "INF"}
        self.write(f"{ch}:BURS:MODE {mode_map.get(mode.lower(), mode)}")
        time.sleep(self.PACING)

        self.write(f"{ch}:BURS:NCYC {cycles}")
        time.sleep(self.PACING)

        trig_map = {"internal": "INT", "external": "EXT", "manual": "MAN"}
        self.write(f"{ch}:BURS:TRIG:SOUR {trig_map.get(trigger_source.lower(), trigger_source)}")
        time.sleep(self.PACING)

        if burst_period_s is not None:
            self.write(f"{ch}:BURS:INT:PER {burst_period_s}")
            time.sleep(self.PACING)

        return {
            "channel": channel,
            "burst_enabled": True,
            "cycles": int(float(self.query(f"{ch}:BURS:NCYC?"))),
            "mode": self.query(f"{ch}:BURS:MODE?").strip(),
            "trigger_source": self.query(f"{ch}:BURS:TRIG:SOUR?").strip(),
        }

    def trigger_burst(self, channel: int) -> dict:
        """
        Trigger a burst (for manual trigger mode).

        Args:
            channel: Channel (1 or 2)

        Returns:
            Dict with ok status
        """
        self.write(f":SOUR{channel}:BURS:TRIG:IMM")
        return {"channel": channel, "triggered": True}

    def disable_burst(self, channel: int) -> dict:
        """Disable burst mode."""
        self.write(f":SOUR{channel}:BURS:STAT OFF")
        return {"channel": channel, "burst_enabled": False}

    # ---- Modulation ----

    def configure_am(
        self,
        channel: int,
        depth_pct: float,
        mod_frequency_hz: float,
        mod_waveform: str = "sine"
    ) -> dict:
        """
        Configure AM (Amplitude Modulation).

        Args:
            channel: Channel (1 or 2)
            depth_pct: Modulation depth (0-120%)
            mod_frequency_hz: Modulation frequency
            mod_waveform: Modulation waveform (sine, square, etc.)

        Returns:
            Dict with AM settings
        """
        ch = f":SOUR{channel}"

        self.write(f"{ch}:AM:STAT ON")
        time.sleep(self.PACING)
        self.write(f"{ch}:AM:SOUR INT")
        time.sleep(self.PACING)
        self.write(f"{ch}:AM:DEPT {depth_pct}")
        time.sleep(self.PACING)
        self.write(f"{ch}:AM:INT:FREQ {mod_frequency_hz}")
        time.sleep(self.PACING)

        wave_scpi = WAVEFORMS.get(mod_waveform.lower(), mod_waveform.upper())
        self.write(f"{ch}:AM:INT:FUNC {wave_scpi}")
        time.sleep(self.PACING)

        return {
            "channel": channel,
            "am_enabled": True,
            "depth_pct": float(self.query(f"{ch}:AM:DEPT?")),
            "mod_frequency_hz": float(self.query(f"{ch}:AM:INT:FREQ?")),
        }

    def configure_fm(
        self,
        channel: int,
        deviation_hz: float,
        mod_frequency_hz: float
    ) -> dict:
        """
        Configure FM (Frequency Modulation).

        Args:
            channel: Channel (1 or 2)
            deviation_hz: Frequency deviation
            mod_frequency_hz: Modulation frequency

        Returns:
            Dict with FM settings
        """
        ch = f":SOUR{channel}"

        self.write(f"{ch}:FM:STAT ON")
        time.sleep(self.PACING)
        self.write(f"{ch}:FM:DEV {deviation_hz}")
        time.sleep(self.PACING)
        self.write(f"{ch}:FM:INT:FREQ {mod_frequency_hz}")
        time.sleep(self.PACING)

        return {
            "channel": channel,
            "fm_enabled": True,
            "deviation_hz": float(self.query(f"{ch}:FM:DEV?")),
            "mod_frequency_hz": float(self.query(f"{ch}:FM:INT:FREQ?")),
        }

    def disable_modulation(self, channel: int) -> dict:
        """Disable all modulation modes."""
        ch = f":SOUR{channel}"
        self.write(f"{ch}:AM:STAT OFF")
        time.sleep(self.PACING)
        self.write(f"{ch}:FM:STAT OFF")
        time.sleep(self.PACING)
        self.write(f"{ch}:PM:STAT OFF")
        time.sleep(self.PACING)
        self.write(f"{ch}:PWM:STAT OFF")
        return {"channel": channel, "modulation_disabled": True}

    # ---- Phase Alignment ----

    def align_phases(self) -> dict:
        """
        Align phases of both channels.

        Returns:
            Dict with ok status
        """
        self.write(":PHAS:INIT")
        time.sleep(0.1)
        return {"phases_aligned": True}

    # ---- Dual Channel ----

    def configure_dual_channel(
        self,
        frequency_hz: float,
        amplitude_vpp: float,
        phase_offset_deg: float = 90
    ) -> dict:
        """
        Configure both channels with same frequency but phase offset.

        Args:
            frequency_hz: Frequency for both channels
            amplitude_vpp: Amplitude for both channels
            phase_offset_deg: Phase offset between channels

        Returns:
            Dict with dual channel settings
        """
        # Configure CH1
        self.configure_sine(1, frequency_hz, amplitude_vpp, phase_deg=0)

        # Configure CH2 with phase offset
        self.configure_sine(2, frequency_hz, amplitude_vpp, phase_deg=phase_offset_deg)

        # Align phases
        self.align_phases()

        return {
            "frequency_hz": frequency_hz,
            "amplitude_vpp": amplitude_vpp,
            "ch1_phase_deg": 0,
            "ch2_phase_deg": phase_offset_deg,
            "phases_aligned": True
        }
