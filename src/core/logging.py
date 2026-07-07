from __future__ import annotations

import logging
from pathlib import Path

from src.core.config import settings


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    log_dir = settings.project_root / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_dir / "backend.log"))
    except OSError:
        pass

    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format=LOG_FORMAT,
        handlers=handlers,
    )


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
