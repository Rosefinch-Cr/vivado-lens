"""Implementation result models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from vivado_lens.models.base import VivadoResult
from vivado_lens.models.synth import TimingSummary, Utilization


class PowerComponent(BaseModel):
    name: str
    watts: float
    pct_of_dynamic: float = 0.0


class PowerReport(BaseModel):
    total_w: float = 0.0
    dynamic_w: float = 0.0
    static_w: float = 0.0
    junction_temp_c: float = 0.0
    confidence: str = ""
    components: list[PowerComponent] = Field(default_factory=list)


class ImplResult(VivadoResult):
    """Result of an implementation run."""

    timing: Optional[TimingSummary] = None
    utilization: Optional[Utilization] = None
    power: Optional[PowerReport] = None
    checkpoint_path: Optional[str] = None
    bitstream_path: Optional[str] = None
