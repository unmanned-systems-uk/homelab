#!/usr/bin/env python3
"""
SCPI Instruments MCP Server.

Provides MCP tool access to SCPI-enabled test equipment:
- RSA5065N Real-Time Spectrum Analyser
- MSO8204 Mixed Signal Oscilloscope

Transport: Raw TCP socket (not VISA/VXI-11)
Protocol: SSE for MCP communication
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
from instruments import RSA5065N, MSO8204

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("scpi-mcp")

# Initialize MCP server
mcp = FastMCP("scpi-instruments")

# Initialize connection pool with environment config
INSTRUMENTS = {
    "rsa5065n": InstrumentConfig(
        name="rsa5065n",
        ip=os.environ.get("RSA5065N_IP", "10.0.1.85"),
        port=int(os.environ.get("SCPI_PORT", "5555")),
        instrument_type="rsa5065n"
    ),
    "mso8204": InstrumentConfig(
        name="mso8204",
        ip=os.environ.get("MSO8204_IP", "10.0.1.106"),
        port=int(os.environ.get("SCPI_PORT", "5555")),
        instrument_type="mso8204"
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
# MSO8204 - Oscilloscope Tools (11)
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


# ==============================================================================
# Run Server
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 8081))
    logger.info("Starting SCPI Instruments MCP Server")
    logger.info("RSA5065N: %s", INSTRUMENTS["rsa5065n"].ip)
    logger.info("MSO8204: %s", INSTRUMENTS["mso8204"].ip)
    logger.info("Listening on port %d", port)
    mcp.run(transport="sse", port=port, host="0.0.0.0")
