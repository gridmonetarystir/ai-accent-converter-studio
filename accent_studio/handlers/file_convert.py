"""Single-file conversion handler."""
from __future__ import annotations

import logging
from pathlib import Path

from accent_studio.core.engine import AccentConversionEngine, ConversionRequest

log = logging.getLogger(__name__)


class FileConvertHandler:
    def __init__(self, engine: AccentConversionEngine) -> None:
        self._engine = engine

    def handle(self, input_path: str, output_path: str,
               source: str, target: str, preserve_timbre: bool = True) -> Path:
        req = ConversionRequest(
            input_path=Path(input_path),
            output_path=Path(output_path),
            source_accent=source,
            target_accent=target,
            preserve_timbre=preserve_timbre,
        )
        return self._engine.convert(req)