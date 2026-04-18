#!/usr/bin/env python3
"""
SCPISocket - Instrument-agnostic raw TCP SCPI transport.

Handles all Rigol quirks: missing terminators, 50 ms pacing,
IEEE 488.2 block data, and quiet timeout for unterminated responses.

Usage:
    from scpi_transport import SCPISocket

    with SCPISocket("10.0.1.106") as inst:
        idn = inst.query("*IDN?")
        inst.write(":CHANnel1:DISPlay ON")
        vpp = inst.query(":MEASure:VPP?")
        screenshot = inst.query_block(":DISPlay:DATA? ON,OFF,PNG")
"""

import socket
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Transport constants
PACING_DELAY = 0.05       # 50 ms inter-command pacing (CRITICAL)
QUIET_TIMEOUT = 1.0       # seconds - detect unterminated response (raised from 0.5 for large traces)
DEFAULT_TIMEOUT = 10.0    # seconds - wait for first byte
DEFAULT_PORT = 5555

# TCP keepalive settings (detect dead peers in <90s instead of ~2h)
KEEPALIVE_IDLE = 60       # seconds before first probe
KEEPALIVE_INTERVAL = 10   # seconds between probes
KEEPALIVE_COUNT = 3       # probes before giving up


class SCPIError(Exception):
    """Base SCPI transport error."""
    pass


class SCPIConnectionError(SCPIError):
    """Connection or network error."""
    pass


class SCPITimeoutError(SCPIError):
    """Response timeout."""
    pass


class SCPISocket:
    """
    Raw TCP socket SCPI transport for Rigol instruments.

    Shared transport layer for RSA5065N, MSO8204, and other instruments.
    Handles all known Rigol TCP SCPI quirks:

    1. 50 ms pacing between commands (silent drops without it)
    2. Quiet timeout for responses missing trailing newline
    3. IEEE 488.2 definite-length block data parsing
    """

    def __init__(self, ip: str, port: int = DEFAULT_PORT,
                 timeout: float = DEFAULT_TIMEOUT,
                 pacing: float = PACING_DELAY):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.pacing = pacing
        self._sock: Optional[socket.socket] = None
        self._idn: Optional[str] = None

    # ---- Connection management ----

    def connect(self) -> str:
        """Open TCP socket and query *IDN?. Return identity string."""
        if self._sock is not None:
            self.close()

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.timeout)

        try:
            self._sock.connect((self.ip, self.port))
            # Enable TCP keepalive to detect dead peers quickly
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, KEEPALIVE_IDLE)
            self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, KEEPALIVE_INTERVAL)
            self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, KEEPALIVE_COUNT)
        except socket.timeout:
            self._sock = None
            raise SCPIConnectionError(
                f"Connection timed out ({self.timeout}s) to {self.ip}:{self.port}")
        except ConnectionRefusedError:
            self._sock = None
            raise SCPIConnectionError(
                f"Connection refused by {self.ip}:{self.port}")
        except OSError as e:
            self._sock = None
            raise SCPIConnectionError(
                f"Network error connecting to {self.ip}:{self.port}: {e}")

        self._idn = self.query("*IDN?")
        logger.info("Connected to: %s", self._idn)
        return self._idn

    def close(self) -> None:
        """Close socket cleanly."""
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
            self._idn = None
            logger.info("Connection closed")

    @property
    def connected(self) -> bool:
        return self._sock is not None

    @property
    def identity(self) -> Optional[str]:
        return self._idn

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    # ---- Low-level transport ----

    def _send(self, data: bytes) -> None:
        """Send raw bytes."""
        if self._sock is None:
            raise SCPIConnectionError("Not connected")
        try:
            self._sock.sendall(data)
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            self._sock = None
            raise SCPIConnectionError(f"Send failed: {e}")

    def _recv_until(self, terminator: bytes = b"\n",
                    max_bytes: int = 65536) -> bytes:
        """
        Read until terminator or quiet timeout.

        Phase 1: Wait up to self.timeout for first byte.
        Phase 2: Once data arrives, use QUIET_TIMEOUT for subsequent reads.
                 If no data within QUIET_TIMEOUT, response is complete.
        """
        if self._sock is None:
            raise SCPIConnectionError("Not connected")

        buf = b""
        while terminator not in buf:
            if len(buf) > max_bytes:
                raise SCPIError(
                    f"Response exceeded {max_bytes} bytes without terminator")
            timeout = QUIET_TIMEOUT if buf else self.timeout
            self._sock.settimeout(timeout)
            try:
                chunk = self._sock.recv(4096)
            except socket.timeout:
                if buf:
                    break  # quiet after data = response complete
                self._sock = None  # Bug fix: null socket on timeout to trigger reconnect
                raise SCPITimeoutError(
                    f"Read timed out after {self.timeout}s (no data received)")
            if not chunk:
                if buf:
                    break
                self._sock = None  # Bug fix: null socket on close to trigger reconnect
                raise SCPIConnectionError("Connection closed by instrument")
            buf += chunk

        return buf

    def _recv_exact(self, n: int) -> bytes:
        """Read exactly n bytes from socket."""
        if self._sock is None:
            raise SCPIConnectionError("Not connected")

        buf = b""
        remaining = n
        while remaining > 0:
            try:
                chunk = self._sock.recv(min(remaining, 65536))
            except socket.timeout:
                self._sock = None  # Bug fix: null socket on timeout to trigger reconnect
                raise SCPITimeoutError(
                    f"Read timed out. Expected {n} bytes, received {len(buf)}.")
            if not chunk:
                self._sock = None  # Bug fix: null socket on close to trigger reconnect
                raise SCPIConnectionError(
                    f"Socket closed during read. Expected {n} bytes, got {len(buf)}.")
            buf += chunk
            remaining -= len(chunk)

        return buf

    def _recv_block(self) -> bytes:
        """
        Read IEEE 488.2 definite-length block data.

        Format: #<d><count><payload>
        """
        if self._sock is None:
            raise SCPIConnectionError("Not connected")

        # Read '#'
        self._sock.settimeout(self.timeout)
        header = b""
        while len(header) < 2:
            try:
                chunk = self._sock.recv(2 - len(header))
            except socket.timeout:
                self._sock = None  # Bug fix: null socket on timeout
                raise SCPITimeoutError("Timeout reading block header")
            if not chunk:
                self._sock = None  # Bug fix: null socket on close
                raise SCPIConnectionError("Connection closed reading block header")
            header += chunk

        if header[0:1] != b"#":
            raise SCPIError(f"Expected '#' block header, got: {header!r}")

        d = int(header[1:2])
        if d == 0:
            raise SCPIError("Indefinite-length block not supported")

        # Read count digits
        count_buf = b""
        while len(count_buf) < d:
            try:
                chunk = self._sock.recv(d - len(count_buf))
            except socket.timeout:
                self._sock = None  # Bug fix: null socket on timeout
                raise SCPITimeoutError("Timeout reading block count")
            if not chunk:
                self._sock = None  # Bug fix: null socket on close
                raise SCPIConnectionError("Connection closed reading block count")
            count_buf += chunk

        payload_len = int(count_buf)
        logger.debug("Block data: %d bytes expected", payload_len)

        # Read payload
        payload = b""
        while len(payload) < payload_len:
            remaining = payload_len - len(payload)
            try:
                chunk = self._sock.recv(min(remaining, 65536))
            except socket.timeout:
                self._sock = None  # Bug fix: null socket on timeout
                raise SCPITimeoutError(
                    f"Timeout during block read ({len(payload)}/{payload_len} bytes)")
            if not chunk:
                self._sock = None  # Bug fix: null socket on close
                raise SCPIConnectionError(
                    f"Connection closed during block read "
                    f"({len(payload)}/{payload_len} bytes)")
            payload += chunk

        # Consume trailing newline if present
        self._sock.settimeout(0.2)
        try:
            self._sock.recv(1)
        except socket.timeout:
            pass

        return payload

    # ---- SCPI commands ----

    def write(self, cmd: str) -> None:
        """Send a SCPI command (no response expected). Applies pacing delay."""
        self._send((cmd + "\n").encode())
        time.sleep(self.pacing)
        logger.debug("WRITE: %s", cmd)

    def query(self, cmd: str) -> str:
        """Send a SCPI query and return the text response (stripped)."""
        self._send((cmd + "\n").encode())
        time.sleep(self.pacing)
        response = self._recv_until().decode("ascii", errors="replace").strip()
        logger.debug("QUERY: %s -> %s", cmd, response[:80] if len(response) > 80 else response)
        return response

    def query_block(self, cmd: str) -> bytes:
        """Send a SCPI query and return IEEE 488.2 block data (binary)."""
        self._send((cmd + "\n").encode())
        time.sleep(self.pacing)
        data = self._recv_block()
        logger.debug("BLOCK: %s -> %d bytes", cmd, len(data))
        return data

    def query_opc(self) -> bool:
        """Wait for *OPC? to return '1'."""
        resp = self.query("*OPC?")
        return resp.strip() == "1"

    # ---- Convenience methods ----

    def reset(self) -> None:
        """Send *RST, wait for OPC, drain error queue."""
        self.write("*RST")
        time.sleep(1.0)  # RST needs settling time
        self.query_opc()
        n = self.clear_errors()
        if n > 0:
            logger.info("Drained %d post-reset errors", n)

    def check_error(self) -> tuple:
        """Query :SYST:ERR? and return (code, message)."""
        resp = self.query(":SYST:ERR?")
        # Parse: <code>,"<message>"
        parts = resp.split(",", 1)
        code = int(parts[0])
        msg = parts[1].strip().strip('"') if len(parts) > 1 else ""
        return (code, msg)

    def clear_errors(self) -> int:
        """Drain error queue until empty. Return number of errors drained."""
        count = 0
        while True:
            code, msg = self.check_error()
            if code == 0:
                break
            logger.warning("Error %d: %s", code, msg)
            count += 1
            if count > 50:
                logger.error("Error queue stuck after 50 reads")
                break
        return count

    def screenshot(self, filename: str, fmt: str = "PNG") -> int:
        """
        Capture instrument display and save to file.

        Args:
            filename: Output file path
            fmt: Image format - "PNG", "BMP", or "JPEG"

        Returns:
            Number of bytes written.

        Tries multiple SCPI screenshot commands for compatibility across
        Rigol instrument families.
        """
        commands = [
            f":DISPlay:DATA? ON,OFF,{fmt}",  # MSO8204 style
            f":PRIV:SNAP? {fmt}",             # RSA5065N style
            ":DISPlay:DATA?",                 # Generic fallback
        ]

        for cmd in commands:
            try:
                data = self.query_block(cmd)
                with open(filename, "wb") as f:
                    f.write(data)
                logger.info("Screenshot saved: %s (%d bytes)", filename, len(data))
                return len(data)
            except SCPIError:
                logger.debug("Screenshot command failed: %s", cmd)
                continue

        raise SCPIError("All screenshot commands failed")

    def measure(self, channel: int, *measurements: str) -> dict:
        """
        Run multiple measurements on a channel (oscilloscope).

        Args:
            channel: Channel number (1-4)
            *measurements: Measurement names, e.g. "FREQuency", "VPP", "RISetime"

        Returns:
            Dict mapping measurement name to float value.

        Example:
            results = inst.measure(1, "FREQuency", "VPP", "VRMS", "RISetime")
        """
        self.write(f":MEASure:SOURce CHANnel{channel}")
        results = {}
        for m in measurements:
            try:
                val = self.query(f":MEASure:{m}?")
                results[m] = float(val)
            except (ValueError, SCPIError) as e:
                logger.warning("Measurement %s failed: %s", m, e)
                results[m] = None
        return results
