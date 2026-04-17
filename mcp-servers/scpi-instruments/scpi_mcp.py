#!/usr/bin/env python3
"""
SCPI Instruments MCP Server.

Provides MCP tool access to SCPI-enabled test equipment:
- RSA5065N Real-Time Spectrum Analyser
- MSO8204 Mixed Signal Oscilloscope
- DMM6500 6.5-Digit Multimeter
- DL3021A DC Electronic Load
- DG2052 Function/Arbitrary Waveform Generator
- DP932A Programmable DC Power Supply (x2)

Transport: Raw TCP socket (not VISA/VXI-11)
Protocol: Streamable HTTP for MCP communication (/mcp endpoint)
"""

import os
import sys
import base64
import logging
from typing import Optional, List

from fastmcp import FastMCP

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scpi_transport import SCPISocket, SCPIError, SCPIConnectionError
from connection_pool import ConnectionPool, InstrumentConfig, get_pool, init_pool
from instruments import RSA5065N, MSO8204, DMM6500, DL3021A, DG2052, DP932A

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("scpi-mcp")

# Initialize MCP server
mcp = FastMCP("scpi-instruments")

# Initialize connection pool with environment config
INSTRUMENTS = {
    # Spectrum Analyser
    "rsa5065n": InstrumentConfig(
        name="rsa5065n",
        ip=os.environ.get("RSA5065N_IP", "10.0.1.85"),
        port=int(os.environ.get("SCPI_PORT", "5555")),
        instrument_type="rsa5065n"
    ),
    # Oscilloscope
    "mso8204": InstrumentConfig(
        name="mso8204",
        ip=os.environ.get("MSO8204_IP", "10.0.1.106"),
        port=int(os.environ.get("SCPI_PORT", "5555")),
        instrument_type="mso8204"
    ),
    # Multimeter
    "dmm6500": InstrumentConfig(
        name="dmm6500",
        ip=os.environ.get("DMM6500_IP", "10.0.1.101"),
        port=int(os.environ.get("DMM_PORT", "5025")),
        instrument_type="dmm6500"
    ),
    # DC Electronic Load
    "dl3021a": InstrumentConfig(
        name="dl3021a",
        ip=os.environ.get("DL3021A_IP", "10.0.1.105"),
        port=int(os.environ.get("SCPI_PORT", "5555")),
        instrument_type="dl3021a"
    ),
    # Function Generator / AWG
    "dg2052": InstrumentConfig(
        name="dg2052",
        ip=os.environ.get("DG2052_IP", "10.0.1.120"),
        port=int(os.environ.get("SCPI_PORT", "5555")),
        instrument_type="dg2052"
    ),
    # Power Supply 1
    "dp932a-1": InstrumentConfig(
        name="dp932a-1",
        ip=os.environ.get("DP932A_1_IP", "10.0.1.111"),
        port=int(os.environ.get("PSU_PORT", "5025")),
        instrument_type="dp932a"
    ),
    # Power Supply 2
    "dp932a-2": InstrumentConfig(
        name="dp932a-2",
        ip=os.environ.get("DP932A_2_IP", "10.0.1.138"),
        port=int(os.environ.get("PSU_PORT", "5025")),
        instrument_type="dp932a"
    ),
}

# Initialize pool on import
init_pool(INSTRUMENTS)


def get_instrument(name: str):
    """Get instrument driver instance."""
    pool = get_pool()
    sock = pool.get_socket(name)

    # Get config to determine type
    config = pool._resolve_instrument(name)

    if config.instrument_type == "rsa5065n":
        return RSA5065N(sock)
    elif config.instrument_type == "mso8204":
        return MSO8204(sock)
    elif config.instrument_type == "dmm6500":
        return DMM6500(sock)
    elif config.instrument_type == "dl3021a":
        return DL3021A(sock)
    elif config.instrument_type == "dg2052":
        return DG2052(sock)
    elif config.instrument_type == "dp932a":
        return DP932A(sock)
    else:
        raise ValueError(f"Unknown instrument type: {config.instrument_type}")


# ==============================================================================
# Connection Management Tools (3)
# ==============================================================================

@mcp.tool()
def scpi_connect(instrument: str, port: int = 5555) -> dict:
    """
    Connect to an instrument by name or IP.

    Args:
        instrument: Instrument name ("rsa5065n", "mso8204") or IP address
        port: SCPI port (default 5555)

    Returns:
        Dict with identity, connected status, and instrument info
    """
    pool = get_pool()

    # If IP address provided, register it first
    if instrument not in INSTRUMENTS and "." in instrument:
        pool.register_instrument(instrument, instrument, port, "generic")

    return pool.connect(instrument)


@mcp.tool()
def scpi_disconnect(instrument: str) -> dict:
    """
    Disconnect from an instrument.

    Args:
        instrument: Instrument name or IP address

    Returns:
        Dict with disconnected status
    """
    return get_pool().disconnect(instrument)


@mcp.tool()
def scpi_status() -> dict:
    """
    List connected instruments and their status.

    Returns:
        Dict with list of instruments and their connection status
    """
    return get_pool().status()


# ==============================================================================
# Raw SCPI Access Tools (3)
# ==============================================================================

@mcp.tool()
def scpi_write(instrument: str, command: str) -> dict:
    """
    Send a SCPI command (no response expected).

    Args:
        instrument: Instrument name or IP
        command: SCPI command to send

    Returns:
        Dict with ok status
    """
    try:
        sock = get_pool().get_socket(instrument)
        sock.write(command)
        return {"ok": True, "command": command}
    except SCPIError as e:
        return {"ok": False, "error": str(e), "command": command}


@mcp.tool()
def scpi_query(instrument: str, command: str) -> dict:
    """
    Send a SCPI query and return the text response.

    Args:
        instrument: Instrument name or IP
        command: SCPI query command (should end with ?)

    Returns:
        Dict with response text
    """
    try:
        sock = get_pool().get_socket(instrument)
        response = sock.query(command)
        return {"response": response, "command": command}
    except SCPIError as e:
        return {"error": str(e), "command": command}


@mcp.tool()
def scpi_query_block(instrument: str, command: str) -> dict:
    """
    Send a SCPI query and return binary block data (base64 encoded).

    Args:
        instrument: Instrument name or IP
        command: SCPI query command for block data

    Returns:
        Dict with base64-encoded data and size
    """
    try:
        sock = get_pool().get_socket(instrument)
        data = sock.query_block(command)
        return {
            "data_b64": base64.b64encode(data).decode("ascii"),
            "size_bytes": len(data),
            "command": command
        }
    except SCPIError as e:
        return {"error": str(e), "command": command}


# ==============================================================================
# RSA5065N - Spectrum Analyser Tools (5)
# ==============================================================================

@mcp.tool()
def rsa_reset() -> dict:
    """
    Reset the RSA5065N to known state (SA mode, ASCII format, errors drained).

    Returns:
        Dict with ok status and errors_drained count
    """
    try:
        rsa = get_instrument("rsa5065n")
        return rsa.reset()
    except Exception as e:
        return {"ok": False, "error": str(e)}


@mcp.tool()
def rsa_configure_sweep(
    start_hz: float,
    stop_hz: float,
    rbw_hz: float = 10e3,
    vbw_hz: float = 10e3,
    ref_level_dbm: float = -20.0,
    att_db: float = 0,
    points: int = 1001
) -> dict:
    """
    Configure a swept spectrum analysis.

    Args:
        start_hz: Start frequency in Hz
        stop_hz: Stop frequency in Hz
        rbw_hz: Resolution bandwidth in Hz (default 10 kHz)
        vbw_hz: Video bandwidth in Hz (default 10 kHz)
        ref_level_dbm: Reference level in dBm (default -20)
        att_db: Attenuation in dB (0 = auto, min 10 dB)
        points: Sweep points (default 1001). Valid: 201, 401, 601, 801, 1001, etc.

    Returns:
        Dict with actual_points, actual_rbw_hz, actual_vbw_hz
    """
    try:
        rsa = get_instrument("rsa5065n")
        return rsa.configure_sweep(
            start_hz=start_hz,
            stop_hz=stop_hz,
            rbw_hz=rbw_hz,
            vbw_hz=vbw_hz,
            ref_level_dbm=ref_level_dbm,
            att_db=att_db,
            points=points
        )
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def rsa_sweep(trace: int = 1) -> dict:
    """
    Execute a single sweep and return trace data.

    Args:
        trace: Trace number (1-3, default 1)

    Returns:
        Dict with trace_dbm (list of dBm values), points, elapsed_s
    """
    try:
        rsa = get_instrument("rsa5065n")
        return rsa.sweep(trace)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def rsa_capture_burst(
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
        rbw_hz: Resolution bandwidth in Hz (default 10 kHz)
        points: Sweep points (default 1001)

    Returns:
        Dict with sweeps list (each has timestamp and trace_dbm), actual_points
    """
    try:
        rsa = get_instrument("rsa5065n")
        return rsa.capture_burst(n, start_hz, stop_hz, rbw_hz, points)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def rsa_screenshot(filename: str) -> dict:
    """
    Capture the RSA5065N display.

    Args:
        filename: Output file path (BMP format)

    Returns:
        Dict with filename, size_bytes, format
    """
    try:
        rsa = get_instrument("rsa5065n")
        return rsa.screenshot(filename, "BMP")
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# MSO8204 - Oscilloscope Tools (12)
# ==============================================================================

@mcp.tool()
def scope_reset() -> dict:
    """
    Reset the MSO8204 to known state.

    Returns:
        Dict with ok status and errors_drained count
    """
    try:
        scope = get_instrument("mso8204")
        return scope.reset()
    except Exception as e:
        return {"ok": False, "error": str(e)}


@mcp.tool()
def scope_channel_config(
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
        Dict with applied channel settings
    """
    try:
        scope = get_instrument("mso8204")
        return scope.channel_config(
            channel=channel,
            enabled=enabled,
            scale_v_div=scale_v_div,
            offset_v=offset_v,
            coupling=coupling,
            probe_ratio=probe_ratio,
            bw_limit=bw_limit
        )
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_timebase(
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
        Dict with applied timebase settings
    """
    try:
        scope = get_instrument("mso8204")
        return scope.timebase(scale_s_div, offset_s, mode)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_trigger(
    mode: str = "EDGE",
    source: str = "CHANnel1",
    level_v: float = 0,
    slope: str = "POSitive",
    sweep: str = "NORMal"
) -> dict:
    """
    Configure the trigger.

    Args:
        mode: Trigger mode ("EDGE", "PULSe", "SLOPe")
        source: Trigger source ("CHANnel1"-"CHANnel4", "EXT")
        level_v: Trigger level (V)
        slope: Trigger slope ("POSitive", "NEGative", "RFALl")
        sweep: Sweep mode ("AUTO", "NORMal", "SINGle")

    Returns:
        Dict with trigger settings
    """
    try:
        scope = get_instrument("mso8204")
        return scope.trigger(mode, source, level_v, slope, sweep)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_autoscale() -> dict:
    """
    Run autoscale on all active channels.

    Returns:
        Dict with ok status
    """
    try:
        scope = get_instrument("mso8204")
        return scope.autoscale()
    except Exception as e:
        return {"ok": False, "error": str(e)}


@mcp.tool()
def scope_acquire(mode: str = "RUN") -> dict:
    """
    Start acquisition (run/stop/single).

    Args:
        mode: "RUN", "STOP", or "SINGle"

    Returns:
        Dict with mode and trigger_status
    """
    try:
        scope = get_instrument("mso8204")
        return scope.acquire(mode)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_measure(channel: int, measurements: List[str]) -> dict:
    """
    Take measurements on a channel.

    Args:
        channel: Channel number (1-4)
        measurements: List of measurement names, e.g.:
            ["FREQuency", "VPP", "VRMS", "RISetime", "FALLtime", "PDUTy", "OVERshoot"]

    Returns:
        Dict with channel and results mapping measurement names to values
    """
    try:
        scope = get_instrument("mso8204")
        return scope.measure(channel, measurements)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_measure_phase(source_a: int, source_b: int) -> dict:
    """
    Measure phase relationship between two channels.

    Args:
        source_a: First channel (1-4)
        source_b: Second channel (1-4)

    Returns:
        Dict with phase_rising_deg and phase_falling_deg
    """
    try:
        scope = get_instrument("mso8204")
        return scope.measure_phase(source_a, source_b)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_waveform(
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
        Dict with waveform data, scaling parameters, and sample rate
    """
    try:
        scope = get_instrument("mso8204")
        return scope.waveform(channel, mode, fmt, points)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_screenshot(filename: str, fmt: str = "PNG") -> dict:
    """
    Capture the oscilloscope display.

    Args:
        filename: Output file path
        fmt: Image format ("PNG", "BMP", "JPEG")

    Returns:
        Dict with filename, size_bytes, format
    """
    try:
        scope = get_instrument("mso8204")
        return scope.screenshot(filename, fmt)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_fft(
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
    try:
        scope = get_instrument("mso8204")
        return scope.fft(source_channel, window, unit)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_counter(channel: int) -> dict:
    """
    Read frequency using the hardware frequency counter.

    Uses the MSO8204's dedicated hardware counter which is more accurate than
    the waveform-based :MEASure:FREQuency? (which has ~0.4% error at typical
    timebases). The hardware counter uses hardware gating for exact frequency
    measurement.

    IMPORTANT: Always prefer this tool over scope_measure(FREQuency) for
    accurate frequency readings.

    Args:
        channel: Channel number (1-4)

    Returns:
        Dict with frequency_hz (authoritative), source, and method
    """
    try:
        scope = get_instrument("mso8204")
        return scope.counter(channel)
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# Composite / Workflow Tools (2)
# ==============================================================================

@mcp.tool()
def scope_characterise_channel(channel: int, autoscale: bool = True) -> dict:
    """
    Full signal characterisation on one channel.

    Runs autoscale (optional), then measures all key parameters:
    frequency, period, Vpp, amplitude, Vtop, Vbase, Vrms, Vmax, Vmin,
    rise time, fall time, duty cycles, overshoot, preshoot.

    Also infers waveform shape (SINE, SQUARE, PULSE, TRIANGLE).

    Args:
        channel: Channel number (1-4)
        autoscale: Run autoscale before measuring (default true)

    Returns:
        Comprehensive dict with all measurement results
    """
    try:
        scope = get_instrument("mso8204")
        return scope.characterise_channel(channel, autoscale)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_characterise_dual(
    channel_a: int,
    channel_b: int,
    autoscale: bool = True
) -> dict:
    """
    Full characterisation of two channels plus phase relationship.

    Args:
        channel_a: First channel (1-4)
        channel_b: Second channel (1-4)
        autoscale: Run autoscale before measuring (default true)

    Returns:
        Dict with channel_a results, channel_b results, and phase measurements
    """
    try:
        scope = get_instrument("mso8204")
        return scope.characterise_dual(channel_a, channel_b, autoscale)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def scope_reference_status() -> dict:
    """
    Query oscilloscope reference clock source and lock status.

    Tries multiple SCPI command variants since MSO8000 documentation
    is ambiguous. Returns whichever command responds.

    FALLBACK: If all commands timeout, use scope_counter with a known
    10 MHz reference signal - exact 10.000000 MHz confirms external lock.

    Returns:
        Dict with source (INT/EXT), working_command, tested_commands
    """
    try:
        scope = get_instrument("mso8204")
        return scope.reference_status()
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# DMM6500 - Multimeter Tools (7)
# ==============================================================================

@mcp.tool()
def dmm_reset() -> dict:
    """
    Reset the DMM6500 to known state.

    Returns:
        Dict with ok status and errors_drained count
    """
    try:
        dmm = get_instrument("dmm6500")
        return dmm.reset()
    except Exception as e:
        return {"ok": False, "error": str(e)}


@mcp.tool()
def dmm_configure(
    function: str,
    range_val: Optional[float] = None,
    nplc: Optional[float] = None,
    auto_range: bool = True
) -> dict:
    """
    Configure DMM measurement function.

    Args:
        function: Measurement function (dcv, acv, dci, aci, res, fres, temp, freq, cap)
        range_val: Manual range value (None for auto)
        nplc: Integration time in power line cycles (0.0005-15)
        auto_range: Enable auto-ranging

    Returns:
        Dict with applied settings
    """
    try:
        dmm = get_instrument("dmm6500")
        return dmm.configure(function, range_val, nplc, auto_range)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def dmm_measure() -> dict:
    """
    Take a single measurement with current configuration.

    Returns:
        Dict with value, function, and unit
    """
    try:
        dmm = get_instrument("dmm6500")
        return dmm.measure()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def dmm_measure_dcv(range_val: Optional[float] = None, nplc: float = 1) -> dict:
    """
    Quick DC voltage measurement.

    Args:
        range_val: Manual range (None for auto)
        nplc: Integration time (default 1)

    Returns:
        Dict with voltage_v
    """
    try:
        dmm = get_instrument("dmm6500")
        return dmm.measure_dcv(range_val, nplc)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def dmm_measure_dci(range_val: Optional[float] = None, nplc: float = 1) -> dict:
    """
    Quick DC current measurement.

    Args:
        range_val: Manual range (None for auto)
        nplc: Integration time (default 1)

    Returns:
        Dict with current_a
    """
    try:
        dmm = get_instrument("dmm6500")
        return dmm.measure_dci(range_val, nplc)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def dmm_measure_resistance(four_wire: bool = False, range_val: Optional[float] = None) -> dict:
    """
    Resistance measurement (2-wire or 4-wire).

    Args:
        four_wire: Use 4-wire measurement for high accuracy
        range_val: Manual range (None for auto)

    Returns:
        Dict with resistance_ohm
    """
    try:
        dmm = get_instrument("dmm6500")
        return dmm.measure_resistance(four_wire, range_val)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def dmm_measure_temperature(sensor: str = "RTD", rtd_type: str = "PT100") -> dict:
    """
    Temperature measurement.

    Args:
        sensor: Sensor type (RTD, THER, TC)
        rtd_type: RTD type if using RTD (PT100, PT385, PT3916)

    Returns:
        Dict with temperature_c
    """
    try:
        dmm = get_instrument("dmm6500")
        return dmm.measure_temperature(sensor, rtd_type)
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# DL3021A - DC Electronic Load Tools (8)
# ==============================================================================

@mcp.tool()
def load_reset() -> dict:
    """
    Reset the DL3021A to known state (input OFF).

    Returns:
        Dict with ok status
    """
    try:
        load = get_instrument("dl3021a")
        return load.reset()
    except Exception as e:
        return {"ok": False, "error": str(e)}


@mcp.tool()
def load_input(enabled: bool) -> dict:
    """
    Enable or disable load input.

    CAUTION: Enabling input will sink current from connected source.

    Args:
        enabled: True to enable, False to disable

    Returns:
        Dict with input state
    """
    try:
        load = get_instrument("dl3021a")
        return load.input_state(enabled)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def load_cc(current_a: float, slew_rate: Optional[float] = None, voltage_limit: Optional[float] = None) -> dict:
    """
    Configure Constant Current mode.

    Args:
        current_a: Load current in Amps (0-40A)
        slew_rate: Current slew rate in A/us
        voltage_limit: Maximum voltage limit

    Returns:
        Dict with CC mode settings
    """
    try:
        load = get_instrument("dl3021a")
        return load.configure_cc(current_a, slew_rate, voltage_limit)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def load_cv(voltage_v: float, current_limit: Optional[float] = None) -> dict:
    """
    Configure Constant Voltage mode.

    Args:
        voltage_v: Load voltage in Volts (0-150V)
        current_limit: Maximum current limit

    Returns:
        Dict with CV mode settings
    """
    try:
        load = get_instrument("dl3021a")
        return load.configure_cv(voltage_v, current_limit)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def load_cr(resistance_ohm: float, current_limit: Optional[float] = None) -> dict:
    """
    Configure Constant Resistance mode.

    Args:
        resistance_ohm: Load resistance in Ohms
        current_limit: Maximum current limit

    Returns:
        Dict with CR mode settings
    """
    try:
        load = get_instrument("dl3021a")
        return load.configure_cr(resistance_ohm, current_limit)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def load_cp(power_w: float, current_limit: Optional[float] = None) -> dict:
    """
    Configure Constant Power mode.

    Args:
        power_w: Load power in Watts (0-200W)
        current_limit: Maximum current limit

    Returns:
        Dict with CP mode settings
    """
    try:
        load = get_instrument("dl3021a")
        return load.configure_cp(power_w, current_limit)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def load_measure() -> dict:
    """
    Read voltage, current, and power measurements.

    Returns:
        Dict with voltage_v, current_a, power_w
    """
    try:
        load = get_instrument("dl3021a")
        return load.measure()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def load_transient(
    mode: str = "continuous",
    level_a: float = 0.5,
    level_b: float = 1.0,
    frequency_hz: Optional[float] = None
) -> dict:
    """
    Configure transient (dynamic) mode.

    Args:
        mode: Transient mode (continuous, pulse, toggle)
        level_a: Level A current in Amps
        level_b: Level B current in Amps
        frequency_hz: Frequency for continuous mode

    Returns:
        Dict with transient settings
    """
    try:
        load = get_instrument("dl3021a")
        return load.configure_transient(mode, level_a, level_b, frequency_hz)
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# DG2052 - Function Generator Tools (10)
# ==============================================================================

@mcp.tool()
def awg_reset() -> dict:
    """
    Reset the DG2052 to known state (outputs OFF).

    Returns:
        Dict with ok status
    """
    try:
        awg = get_instrument("dg2052")
        return awg.reset()
    except Exception as e:
        return {"ok": False, "error": str(e)}


@mcp.tool()
def awg_output(channel: int, enabled: bool) -> dict:
    """
    Enable or disable channel output.

    CAUTION: Enabling output will produce signal on connected device.

    Args:
        channel: Channel number (1 or 2)
        enabled: True to enable, False to disable

    Returns:
        Dict with output state
    """
    try:
        awg = get_instrument("dg2052")
        return awg.output_state(channel, enabled)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def awg_sine(
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
        Dict with waveform settings
    """
    try:
        awg = get_instrument("dg2052")
        return awg.configure_sine(channel, frequency_hz, amplitude_vpp, offset_v, phase_deg)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def awg_square(
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
        Dict with waveform settings
    """
    try:
        awg = get_instrument("dg2052")
        return awg.configure_square(channel, frequency_hz, amplitude_vpp, duty_cycle_pct, offset_v)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def awg_pulse(
    channel: int,
    frequency_hz: float,
    amplitude_vpp: float,
    width_s: Optional[float] = None,
    duty_cycle_pct: Optional[float] = None,
    offset_v: float = 0
) -> dict:
    """
    Configure pulse output.

    Args:
        channel: Channel (1 or 2)
        frequency_hz: Frequency
        amplitude_vpp: Amplitude in Vpp
        width_s: Pulse width in seconds (alternative to duty_cycle)
        duty_cycle_pct: Duty cycle (alternative to width)
        offset_v: DC offset

    Returns:
        Dict with pulse settings
    """
    try:
        awg = get_instrument("dg2052")
        return awg.configure_pulse(channel, frequency_hz, amplitude_vpp, width_s, duty_cycle_pct, offset_v=offset_v)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def awg_ramp(
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
        Dict with ramp settings
    """
    try:
        awg = get_instrument("dg2052")
        return awg.configure_ramp(channel, frequency_hz, amplitude_vpp, symmetry_pct, offset_v)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def awg_noise(channel: int, amplitude_vpp: float, offset_v: float = 0) -> dict:
    """
    Configure noise output.

    Args:
        channel: Channel (1 or 2)
        amplitude_vpp: Amplitude in Vpp
        offset_v: DC offset

    Returns:
        Dict with noise settings
    """
    try:
        awg = get_instrument("dg2052")
        return awg.configure_noise(channel, amplitude_vpp, offset_v)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def awg_sweep(
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
    try:
        awg = get_instrument("dg2052")
        return awg.configure_sweep(channel, start_hz, stop_hz, sweep_time_s, spacing)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def awg_burst(
    channel: int,
    cycles: int,
    mode: str = "triggered",
    trigger_source: str = "manual"
) -> dict:
    """
    Configure burst mode.

    Args:
        channel: Channel (1 or 2)
        cycles: Number of cycles per burst
        mode: Burst mode (triggered, gated, infinity)
        trigger_source: Trigger source (internal, external, manual)

    Returns:
        Dict with burst settings
    """
    try:
        awg = get_instrument("dg2052")
        return awg.configure_burst(channel, cycles, mode, trigger_source)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def awg_dual_channel(
    frequency_hz: float,
    amplitude_vpp: float,
    phase_offset_deg: float = 90
) -> dict:
    """
    Configure both channels with same frequency but phase offset.

    Useful for quadrature signals, I/Q generation, etc.

    Args:
        frequency_hz: Frequency for both channels
        amplitude_vpp: Amplitude for both channels
        phase_offset_deg: Phase offset between channels (default 90°)

    Returns:
        Dict with dual channel settings
    """
    try:
        awg = get_instrument("dg2052")
        return awg.configure_dual_channel(frequency_hz, amplitude_vpp, phase_offset_deg)
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# DP932A - Power Supply Tools (9)
# ==============================================================================

@mcp.tool()
def psu_reset(psu: str = "dp932a-1") -> dict:
    """
    Reset the power supply to known state (outputs OFF).

    Args:
        psu: PSU name ("dp932a-1" or "dp932a-2")

    Returns:
        Dict with ok status
    """
    try:
        supply = get_instrument(psu)
        return supply.reset()
    except Exception as e:
        return {"ok": False, "error": str(e)}


@mcp.tool()
def psu_output(psu: str, channel: int, enabled: bool) -> dict:
    """
    Enable or disable channel output.

    CAUTION: Enabling output will apply voltage to connected load.

    Args:
        psu: PSU name ("dp932a-1" or "dp932a-2")
        channel: Channel number (1, 2, or 3)
        enabled: True to enable, False to disable

    Returns:
        Dict with output state
    """
    try:
        supply = get_instrument(psu)
        return supply.output_state(channel, enabled)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def psu_all_off(psu: str = "dp932a-1") -> dict:
    """
    Disable all outputs on a power supply.

    Args:
        psu: PSU name ("dp932a-1" or "dp932a-2")

    Returns:
        Dict with all channels off status
    """
    try:
        supply = get_instrument(psu)
        return supply.all_outputs_off()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def psu_set_channel(psu: str, channel: int, voltage_v: float, current_a: float) -> dict:
    """
    Set voltage and current for a channel.

    Args:
        psu: PSU name ("dp932a-1" or "dp932a-2")
        channel: Channel number (1, 2, or 3)
        voltage_v: Output voltage (CH1/2: 0-32V, CH3: 0-6V)
        current_a: Current limit (0-3A)

    Returns:
        Dict with applied settings
    """
    try:
        supply = get_instrument(psu)
        return supply.set_channel(channel, voltage_v, current_a)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def psu_measure(psu: str, channel: int) -> dict:
    """
    Read voltage, current, and power for a channel.

    Args:
        psu: PSU name ("dp932a-1" or "dp932a-2")
        channel: Channel number (1, 2, or 3)

    Returns:
        Dict with voltage_v, current_a, power_w
    """
    try:
        supply = get_instrument(psu)
        return supply.measure(channel)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def psu_measure_all(psu: str = "dp932a-1") -> dict:
    """
    Read measurements for all channels.

    Args:
        psu: PSU name ("dp932a-1" or "dp932a-2")

    Returns:
        Dict with ch1, ch2, ch3 measurements
    """
    try:
        supply = get_instrument(psu)
        return supply.measure_all()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def psu_protection(
    psu: str,
    channel: int,
    ovp_enabled: bool = True,
    ovp_voltage_v: Optional[float] = None,
    ocp_enabled: bool = True,
    ocp_current_a: Optional[float] = None
) -> dict:
    """
    Configure over-voltage and over-current protection.

    Args:
        psu: PSU name ("dp932a-1" or "dp932a-2")
        channel: Channel number (1, 2, or 3)
        ovp_enabled: Enable OVP
        ovp_voltage_v: OVP threshold voltage
        ocp_enabled: Enable OCP
        ocp_current_a: OCP threshold current

    Returns:
        Dict with protection settings
    """
    try:
        supply = get_instrument(psu)
        result = {}
        if ovp_enabled is not None:
            result["ovp"] = supply.set_ovp(channel, ovp_enabled, ovp_voltage_v)
        if ocp_enabled is not None:
            result["ocp"] = supply.set_ocp(channel, ocp_enabled, ocp_current_a)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def psu_tracking(psu: str, mode: int) -> dict:
    """
    Set tracking mode for CH1 and CH2.

    Args:
        psu: PSU name ("dp932a-1" or "dp932a-2")
        mode: 0=Independent, 1=Series (CH1+CH2=0-64V), 2=Parallel (CH1||CH2=0-6A)

    Returns:
        Dict with tracking mode
    """
    try:
        supply = get_instrument(psu)
        return supply.set_tracking(mode)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def psu_quick_output(psu: str, channel: int, voltage_v: float, current_a: float) -> dict:
    """
    Configure and enable output in one call.

    CAUTION: This will apply voltage immediately.

    Args:
        psu: PSU name ("dp932a-1" or "dp932a-2")
        channel: Channel number (1, 2, or 3)
        voltage_v: Output voltage
        current_a: Current limit

    Returns:
        Dict with configuration and live measurements
    """
    try:
        supply = get_instrument(psu)
        return supply.quick_output(channel, voltage_v, current_a)
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# Run Server
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 8081))
    logger.info("Starting SCPI Instruments MCP Server")
    logger.info("Instruments configured:")
    for name, config in INSTRUMENTS.items():
        logger.info("  %s: %s:%d", name, config.ip, config.port)
    logger.info("Listening on port %d", port)
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
