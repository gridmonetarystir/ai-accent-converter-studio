"""Wires config, model registry, engine, and the Qt main window together."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtWidgets import QApplication

from accent_studio.app.lifecycle import Lifecycle
from accent_studio.config.settings import Settings
from accent_studio.core.engine import AccentConversionEngine
from accent_studio.core.model_registry import ModelRegistry
from accent_studio.ui.main_window import MainWindow

log = logging.getLogger(__name__)


@dataclass
class Bootstrap:
    """Owns the object graph for a single app run.

    Constructs settings, registry, engine, then hands the engine to the
    UI. All heavy model loads happen lazily on first conversion so the
    window paints in under 400ms on a cold start.
    """

    settings: Settings = field(init=False)
    registry: ModelRegistry = field(init=False)
    engine: AccentConversionEngine = field(init=False)
    lifecycle: Lifecycle = field(init=False)

    def __post_init__(self) -> None:
        self.settings = Settings.load(Path("config/default.toml"))
        self.registry = ModelRegistry(self.settings)
        self.engine = AccentConversionEngine(self.settings, self.registry)
        self.lifecycle = Lifecycle(self.engine)

    def run(self, argv: list[str]) -> int:
        qt_app = QApplication(argv)
        qt_app.setApplicationName(self.settings.app.name)
        window = MainWindow(engine=self.engine, settings=self.settings)
        self.lifecycle.attach(window)
        window.show()
        return qt_app.exec()