"""Typed settings loaded from TOML with sensible defaults."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomli


@dataclass(frozen=True)
class AppSection:
    name: str
    version: str
    year: int


@dataclass(frozen=True)
class AudioSection:
    sample_rate: int
    block_size: int
    dtype: str
    max_input_seconds: int


@dataclass(frozen=True)
class ConversionSection:
    default_source_accent: str
    default_target_accent: str
    preserve_timbre: bool
    rhoticity_strength: float
    prosody_transfer: float
    pitch_shift_semitones: float
    formant_warp: float


@dataclass(frozen=True)
class ModelsSection:
    voicepack_dir: str
    encoder: str
    decoder: str
    pitch_tracker: str


@dataclass(frozen=True)
class Settings:
    app: AppSection
    audio: AudioSection
    conversion: ConversionSection
    models: ModelsSection
    raw: dict

    @classmethod
    def load(cls, path: Path) -> "Settings":
        with path.open("rb") as fh:
            data = tomli.load(fh)
        return cls(
            app=AppSection(**data["app"]),
            audio=AudioSection(**data["audio"]),
            conversion=ConversionSection(**data["conversion"]),
            models=ModelsSection(**data["models"]),
            raw=data,
        )