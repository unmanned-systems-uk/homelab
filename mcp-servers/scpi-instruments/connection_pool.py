#!/usr/bin/env python3
"""
SCPI Connection Pool - Manages persistent connections to instruments.

Maintains TCP socket connections and reconnects automatically on error.
Prevents per-call connection overhead and instrument re-initialization.
"""

import logging
import threading
from typing import Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime

from scpi_transport import SCPISocket, SCPIConnectionError

logger = logging.getLogger(__name__)


@dataclass
class InstrumentConfig:
    """Configuration for a known instrument."""
    name: str
    ip: str
    port: int = 5555
    timeout: float = 10.0
    instrument_type: str = "generic"  # rsa5065n, mso8204, generic


@dataclass
class InstrumentState:
    """Runtime state for a connected instrument."""
    config: InstrumentConfig
    socket: Optional[SCPISocket] = None
    identity: Optional[str] = None
    connected_at: Optional[datetime] = None
    last_error: Optional[str] = None
    error_count: int = 0


# Default instrument registry
DEFAULT_INSTRUMENTS: Dict[str, InstrumentConfig] = {
    "rsa5065n": InstrumentConfig(
        name="rsa5065n",
        ip="10.0.1.85",
        port=5555,
        instrument_type="rsa5065n"
    ),
    "mso8204": InstrumentConfig(
        name="mso8204",
        ip="10.0.1.106",
        port=5555,
        instrument_type="mso8204"
    ),
}


class ConnectionPool:
    """
    Manages persistent SCPI connections to multiple instruments.

    Thread-safe connection pool that:
    - Maintains persistent TCP connections
    - Reconnects automatically on socket errors
    - Supports both named instruments and direct IP access
    """

    def __init__(self, instruments: Optional[Dict[str, InstrumentConfig]] = None):
        """
        Initialize connection pool.

        Args:
            instruments: Dict mapping instrument names to configs.
                        Defaults to DEFAULT_INSTRUMENTS if not provided.
        """
        self._instruments: Dict[str, InstrumentConfig] = instruments or DEFAULT_INSTRUMENTS.copy()
        self._connections: Dict[str, InstrumentState] = {}
        self._lock = threading.RLock()

    def register_instrument(self, name: str, ip: str, port: int = 5555,
                           instrument_type: str = "generic") -> None:
        """Register a new instrument or update existing config."""
        with self._lock:
            self._instruments[name] = InstrumentConfig(
                name=name,
                ip=ip,
                port=port,
                instrument_type=instrument_type
            )
            # Disconnect if already connected with old config
            if name in self._connections:
                self._disconnect(name)

    def _resolve_instrument(self, instrument: str) -> InstrumentConfig:
        """
        Resolve instrument identifier to config.

        Args:
            instrument: Either a registered name (e.g., "rsa5065n")
                       or an IP address (e.g., "10.0.1.85")

        Returns:
            InstrumentConfig for the instrument
        """
        # Check if it's a registered name
        if instrument in self._instruments:
            return self._instruments[instrument]

        # Treat as IP address
        # Check if we've seen this IP before
        for name, config in self._instruments.items():
            if config.ip == instrument:
                return config

        # Create ad-hoc config for IP
        return InstrumentConfig(
            name=instrument,
            ip=instrument,
            port=5555,
            instrument_type="generic"
        )

    def connect(self, instrument: str) -> dict:
        """
        Connect to an instrument.

        Args:
            instrument: Instrument name or IP address

        Returns:
            Dict with connection status and identity
        """
        with self._lock:
            config = self._resolve_instrument(instrument)
            key = config.name

            # Check if already connected
            if key in self._connections:
                state = self._connections[key]
                if state.socket and state.socket.connected:
                    return {
                        "connected": True,
                        "identity": state.identity,
                        "instrument": key,
                        "ip": config.ip,
                        "already_connected": True
                    }

            # Create new connection
            try:
                sock = SCPISocket(config.ip, config.port, config.timeout)
                identity = sock.connect()

                state = InstrumentState(
                    config=config,
                    socket=sock,
                    identity=identity,
                    connected_at=datetime.now(),
                    error_count=0
                )
                self._connections[key] = state

                logger.info("Connected to %s (%s): %s", key, config.ip, identity)

                return {
                    "connected": True,
                    "identity": identity,
                    "instrument": key,
                    "ip": config.ip,
                    "already_connected": False
                }

            except SCPIConnectionError as e:
                logger.error("Failed to connect to %s (%s): %s", key, config.ip, e)
                # Track failed attempt
                if key in self._connections:
                    self._connections[key].last_error = str(e)
                    self._connections[key].error_count += 1
                else:
                    self._connections[key] = InstrumentState(
                        config=config,
                        last_error=str(e),
                        error_count=1
                    )
                return {
                    "connected": False,
                    "error": str(e),
                    "instrument": key,
                    "ip": config.ip
                }

    def disconnect(self, instrument: str) -> dict:
        """
        Disconnect from an instrument.

        Args:
            instrument: Instrument name or IP address

        Returns:
            Dict with disconnection status
        """
        with self._lock:
            config = self._resolve_instrument(instrument)
            key = config.name
            return self._disconnect(key)

    def _disconnect(self, key: str) -> dict:
        """Internal disconnect by key (must hold lock)."""
        if key not in self._connections:
            return {"disconnected": False, "error": f"Not connected: {key}"}

        state = self._connections[key]
        if state.socket:
            try:
                state.socket.close()
            except Exception as e:
                logger.warning("Error closing socket for %s: %s", key, e)

        del self._connections[key]
        logger.info("Disconnected from %s", key)
        return {"disconnected": True, "instrument": key}

    def get_socket(self, instrument: str, auto_reconnect: bool = True) -> SCPISocket:
        """
        Get socket for an instrument, connecting if necessary.

        Args:
            instrument: Instrument name or IP address
            auto_reconnect: If True, reconnect on socket errors

        Returns:
            SCPISocket instance

        Raises:
            SCPIConnectionError: If connection fails
        """
        with self._lock:
            config = self._resolve_instrument(instrument)
            key = config.name

            # Check existing connection
            if key in self._connections:
                state = self._connections[key]
                if state.socket and state.socket.connected:
                    return state.socket

            # Need to connect
            if auto_reconnect:
                result = self.connect(instrument)
                if result["connected"]:
                    return self._connections[key].socket
                raise SCPIConnectionError(result.get("error", "Connection failed"))

            raise SCPIConnectionError(f"Not connected to {instrument}")

    def status(self) -> dict:
        """
        Get status of all instruments and connections.

        Returns:
            Dict with instrument statuses
        """
        with self._lock:
            instruments = []

            # Include all registered instruments
            all_keys = set(self._instruments.keys()) | set(self._connections.keys())

            for key in sorted(all_keys):
                config = self._instruments.get(key)
                state = self._connections.get(key)

                if config is None and state:
                    config = state.config

                info = {
                    "name": key,
                    "ip": config.ip if config else "unknown",
                    "port": config.port if config else 5555,
                    "type": config.instrument_type if config else "unknown",
                    "connected": False,
                    "identity": None
                }

                if state:
                    info["connected"] = state.socket is not None and state.socket.connected
                    info["identity"] = state.identity
                    if state.connected_at:
                        info["connected_at"] = state.connected_at.isoformat()
                    if state.last_error:
                        info["last_error"] = state.last_error
                    info["error_count"] = state.error_count

                instruments.append(info)

            return {"instruments": instruments}

    def disconnect_all(self) -> None:
        """Disconnect from all instruments."""
        with self._lock:
            for key in list(self._connections.keys()):
                self._disconnect(key)


# Global connection pool instance
_pool: Optional[ConnectionPool] = None


def get_pool() -> ConnectionPool:
    """Get or create the global connection pool."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool()
    return _pool


def init_pool(instruments: Optional[Dict[str, InstrumentConfig]] = None) -> ConnectionPool:
    """Initialize the global connection pool with custom instruments."""
    global _pool
    _pool = ConnectionPool(instruments)
    return _pool
