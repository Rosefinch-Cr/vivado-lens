"""Base result type for all vivado-bridge operations."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CommandStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class VivadoResult(BaseModel):
    """Base result returned by every vivado-bridge command."""

    status: CommandStatus
    command: str
    execution_time_s: float
    timestamp: datetime = Field(default_factory=datetime.now)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    log_tail: str = ""
