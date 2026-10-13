"""Sequential batch conversion queue with progress callbacks."""
from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass

from accent_studio.core.engine import AccentConversionEngine, ConversionRequest

log = logging.getLogger(__name__)


@dataclass
class BatchItem:
    request: ConversionRequest
    status: str = "pending"   # pending | running | done | failed
    error: str | None = None


class BatchQueue:
    def __init__(self, engine: AccentConversionEngine,
                 on_progress: Callable[[int, int, BatchItem], None] | None = None) -> None:
        self._engine = engine
        self._items: list[BatchItem] = []
        self._on_progress = on_progress
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None

    def add(self, request: ConversionRequest) -> None:
        with self._lock:
            self._items.append(BatchItem(request=request))

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._drain, name="batch-queue", daemon=True)
        self._thread.start()

    def _drain(self) -> None:
        with self._lock:
            items = list(self._items)
        total = len(items)
        for idx, item in enumerate(items, start=1):
            item.status = "running"
            if self._on_progress:
                self._on_progress(idx, total, item)
            try:
                self._engine.convert(item.request)
                item.status = "done"
            except Exception as exc:
                log.exception("batch item failed: %s", item.request.input_path)
                item.status = "failed"
                item.error = str(exc)
            if self._on_progress:
                self._on_progress(idx, total, item)
</｜｜DSML｜｜ parameter>