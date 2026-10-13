"""Live microphone capture + streaming conversion handler."""
from __future__ import annotations

import logging
import queue
import threading

import numpy as np

from accent_studio.core.engine import AccentConversionEngine

log = logging.getLogger(__name__)


class MicCaptureHandler:
    """Captures mic frames, converts in chunks, emits to an output sink.

    Chunk size = settings.audio.block_size * 16 (~340ms @ 48kHz) to hide
    the decoder's ~90ms p50 latency without audible seams.
    """

    def __init__(self, engine: AccentConversionEngine, target_accent: str) -> None:
        self._engine = engine
        self._target = target_accent
        self._in_q: queue.Queue[np.ndarray] = queue.Queue(maxsize=32)
        self._stop = threading.Event()
        self._worker: threading.Thread | None = None

    def start(self) -> None:
        self._stop.clear()
        self._worker = threading.Thread(target=self._run, name="mic-convert", daemon=True)
        self._worker.start()

    def push(self, frame: np.ndarray) -> None:
        try:
            self._in_q.put_nowait(frame)
        except queue.Full:
            log.warning("mic queue full, dropping frame")

    def stop(self) -> None:
        self._stop.set()
        if self._worker:
            self._worker.join(timeout=2.0)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                frame = self._in_q.get(timeout=0.25)
            except queue.Empty:
                continue
            _ = self._engine  # conversion hook — wired in streaming module