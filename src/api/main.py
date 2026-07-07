"""
Backward-compatible API entrypoint.

This module intentionally re-exports the canonical FastAPI app from src.main
so older run commands keep working without maintaining a second application.
"""

from src.main import app

__all__ = ["app"]
