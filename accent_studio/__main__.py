"""Bootstrap entry point for the desktop app."""
from __future__ import annotations

import sys
import logging

from accent_studio.app.bootstrap import Bootstrap
from accent_studio.utils.logging_setup import configure_logging


def main() -> int:
    configure_logging()
    log = logging.getLogger("accent_studio")
    log.info("AI Accent Converter Studio starting (pid=%s)", __import__("os").getpid())
    try:
        app = Bootstrap()
        return app.run(sys.argv)
    except Exception:
        log.exception("fatal during startup")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())