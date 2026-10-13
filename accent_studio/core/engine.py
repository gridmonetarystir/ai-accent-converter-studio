"""AccentConversionEngine — orchestrates the full conversion pipeline.

Pipeline stages:
  1. decode input to float32 mono @ settings.audio.sample_rate
  2. pitch track (CREPE-tiny ONNX)
  3. encode speaker + phoneme content (accent encoder ONNX)
  4. warp formants + rhoticity toward target profile
  5. decode to waveform (accent decoder ONNX)
  6. loudness-match and write output

All stages run on a single worker thread; the engine is not thread-safe
across concurrent convert() calls. Use BatchQueue for parallelism.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from accent_studio.config.settings import Settings
from accent_studio.core.model_registry import ModelRegistry
from accent_studio.dsp.formant_warp import warp_formants
from accent_studio.dsp.rhoticity import apply_rhoticity
from accent_studio.dsp.pitch import shift_pitch
from accent_studio.io.audio_io import read_audio, write_audio
from accent_studio.voices.profiles import AccentProfile, load_profile

log = logging.getLogger(__name__)


@dataclass
class ConversionRequest:
    input_path: Path
    output_path: Path
    source_accent: str
    target_accent: str
    preserve_timbre: bool = True


class AccentConversionEngine:
    def __init__(self, settings: Settings, registry: ModelRegistry) -> None:
        self._settings = settings
        self._registry = registry
        self._warm = False

    def warmup(self) -> None:
        if self._warm:
            return
        self._registry.load_all()
        self._warm = True

    def convert(self, req: ConversionRequest) -> Path:
        if not self._warm:
            self.warmup()

        log.info("convert %s -> %s (%s -> %s)",
                 req.input_path.name, req.output_path.name,
                 req.source_accent, req.target_accent)

        audio, sr = read_audio(req.input_path, target_sr=self._settings.audio.sample_rate)
        profile = load_profile(req.target_accent)

        f0 = self._registry.pitch_tracker.track(audio, sr)
        content = self._registry.encoder.encode(audio, sr, f0)

        content = warp_formants(content, profile.formant_ratio * self._settings.conversion.formant_warp)
        content = apply_rhoticity(content, profile.rhoticity, self._settings.conversion.rhoticity_strength)

        if not req.preserve_timbre:
            f0 = shift_pitch(f0, self._settings.conversion.pitch_shift_semitones)

        out = self._registry.decoder.decode(content, f0, sr)
        write_audio(req.output_path, out, sr)
        return req.output_path

    def release(self) -> None:
        self._registry.unload_all()
        self._warm = False