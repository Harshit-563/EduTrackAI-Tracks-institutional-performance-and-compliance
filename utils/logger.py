from __future__ import annotations

from logging import Logger

from src.core.logging import get_logger


def setup_logger(name: str) -> Logger:
    """Convenience wrapper used across services to obtain configured loggers."""
    return get_logger(name)
