#!/usr/bin/env python3
"""
Base Instrument - Abstract base class for SCPI instrument drivers.

Provides common functionality shared by all instrument types.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from scpi_transport import SCPISocket

logger = logging.getLogger(__name__)


class BaseInstrument(ABC):
    """
    Abstract base class for SCPI instrument drivers.

    Wraps an SCPISocket and provides common instrument operations.
    Subclasses implement instrument-specific commands.
    """

    # Inter-command pacing delay (seconds)
    PACING = 0.05  # 50 ms

    def __init__(self, socket: SCPISocket):
        """
        Initialize instrument with an existing socket connection.

        Args:
            socket: Connected SCPISocket instance
        """
        self._sock = socket

    @property
    def socket(self) -> SCPISocket:
        """Get the underlying socket."""
        return self._sock

    @property
    def identity(self) -> Optional[str]:
        """Get cached instrument identity."""
        return self._sock.identity

    @property
    def connected(self) -> bool:
        """Check if socket is connected."""
        return self._sock.connected

    # ---- Low-level SCPI ----

    def write(self, cmd: str) -> None:
        """Send SCPI command (no response)."""
        self._sock.write(cmd)

    def query(self, cmd: str) -> str:
        """Send SCPI query and return response."""
        return self._sock.query(cmd)

    def query_block(self, cmd: str) -> bytes:
        """Send SCPI query and return block data."""
        return self._sock.query_block(cmd)

    def query_opc(self) -> bool:
        """Wait for *OPC? to return '1'."""
        return self._sock.query_opc()

    # ---- Common operations ----

    def reset(self) -> dict:
        """
        Reset instrument to defaults.

        Returns:
            Dict with ok status and errors_drained count
        """
        self.write("*RST")
        time.sleep(1.0)  # Reset needs settling time
        self.query_opc()
        errors = self.clear_errors()
        return {"ok": True, "errors_drained": errors}

    def check_error(self) -> Tuple[int, str]:
        """
        Query error queue for one error.

        Returns:
            Tuple of (code, message). Code 0 means no error.
        """
        return self._sock.check_error()

    def clear_errors(self) -> int:
        """
        Drain error queue until empty.

        Returns:
            Number of errors cleared.
        """
        return self._sock.clear_errors()

    def screenshot(self, filename: str, fmt: str = "PNG") -> dict:
        """
        Capture instrument display screenshot.

        Args:
            filename: Output file path
            fmt: Image format ("PNG", "BMP", "JPEG")

        Returns:
            Dict with filename, size_bytes, format
        """
        size = self._sock.screenshot(filename, fmt)
        return {
            "filename": filename,
            "size_bytes": size,
            "format": fmt
        }

    # ---- Abstract methods for subclasses ----

    @abstractmethod
    def get_type(self) -> str:
        """Return instrument type identifier."""
        pass

    @abstractmethod
    def post_reset(self) -> None:
        """Perform instrument-specific post-reset initialization."""
        pass
