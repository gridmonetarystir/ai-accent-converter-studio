"""App lifecycle hooks: warmup, shutdown, crash-safe teardown."""
from __future__ import annotations

import logging
import atexit

from accent_studio.core.engine import AccentConversionEngine

log = logging.getLogger(__name__)


class Lifecycle:
    """Tracks window close, engine warmup, and process exit."""

    def __init__(self, engine: AccentConversionEngine) -> None:
        self._engine = engine
        self._window = None
        atexit.register(self._on_exit)

    def attach(self, window) -> None:
        self._window = window
        window.destroyed.connect(self._on_window_destroyed)

    def warmup(self) -> None:
        log.info("warming engine (lazy model load)")
        self._engine.warmup()

    def _on_window_destroyed(self, *_args) -> None:
        log.info("window destroyed, releasing engine")
        self._engine.release()

    def _on_exit(self) -> None:
        try:
            self._engine.release()
        except Exception:
            log.exception("engine release failed during atexit")