"""Progress update model for long-running operations."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ProgressUpdate(BaseModel):
    """Written to progress.json during synth/impl for agent polling."""

    elapsed_s: float
    phase: str
    errors: int = 0
    warnings: int = 0
    done: bool = False
    success: bool = True
