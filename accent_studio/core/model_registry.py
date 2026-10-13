"""Lazy loader for ONNX models. Keeps peak RSS under ~1.4GB."""
from __future__ import annotations

import logging
from pathlib import Path

import onnxruntime as ort

from accent_studio.config.settings import Settings

log = logging.getLogger(__name__)


class _OnnxHandle:
    def __init__(self, path: Path) -> None:
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.intra_op_num_threads = 2
        self._session = ort.InferenceSession(str(path), sess_options=opts,
                                             providers=["CPUExecutionProvider"])

    def run(self, *inputs):
        names = [i.name for i in self._session.get_inputs()]
        return self._session.run(None, dict(zip(names, inputs)))


class ModelRegistry:
    """Holds encoder, decoder, pitch tracker. Lazy, unloadable."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._encoder: _OnnxHandle | None = None
        self._decoder: _OnnxHandle | None = None
        self._pitch: _OnnxHandle | None = None

    def load_all(self) -> None:
        if self._encoder is None:
            log.info("loading encoder %s", self._settings.models.encoder)
            self._encoder = _OnnxHandle(Path(self._settings.models.encoder))
        if self._decoder is None:
            log.info("loading decoder %s", self._settings.models.decoder)
            self._decoder = _OnnxHandle(Path(self._settings.models.decoder))
        if self._pitch is None:
            log.info("loading pitch tracker %s", self._settings.models.pitch_tracker)
            self._pitch = _OnnxHandle(Path(self._settings.models.pitch_tracker))

    def unload_all(self) -> None:
        self._encoder = self._decoder = self._pitch = None

    @property
    def encoder(self) -> _OnnxHandle:
        assert self._encoder is not None, "call load_all() first"
        return self._encoder

    @property
    def decoder(self) -> _OnnxHandle:
        assert self._decoder is not None, "call load_all() first"
        return self._decoder

    @property
    def pitch_tracker(self) -> _OnnxHandle:
        assert self._pitch is not None, "call load_all() first"
        return self._pitch