"""Synthesis result models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from vivado_lens.models.base import VivadoResult


class ClockInfo(BaseModel):
    name: str
    period_ns: float
    frequency_mhz: float


class SlackInfo(BaseModel):
    setup_ns: float = 0.0
    hold_ns: float = 0.0
    pulse_width_ns: float = 0.0
    setup_failing: int = 0
    hold_failing: int = 0
    pw_failing: int = 0

    @property
    def all_met(self) -> bool:
        return self.setup_failing == 0 and self.hold_failing == 0 and self.pw_failing == 0


class CriticalPath(BaseModel):
    slack_ns: float
    source: str
    destination: str
    data_path_delay_ns: float
    logic_delay_ns: float
    logic_pct: float
    route_delay_ns: float
    route_pct: float


class TimingSummary(BaseModel):
    clocks: list[ClockInfo] = Field(default_factory=list)
    slack: Optional[SlackInfo] = None
    critical_path: Optional[CriticalPath] = None

    @property
    def timing_met(self) -> bool:
        return self.slack.all_met if self.slack else True


class ResourceUsage(BaseModel):
    name: str
    used: int
    available: int
    utilization_pct: float


class Utilization(BaseModel):
    slice_logic: list[ResourceUsage] = Field(default_factory=list)
    memory: list[ResourceUsage] = Field(default_factory=list)
    dsp: list[ResourceUsage] = Field(default_factory=list)
    io: list[ResourceUsage] = Field(default_factory=list)


class SynthResult(VivadoResult):
    """Result of a synthesis run."""

    timing: Optional[TimingSummary] = None
    utilization: Optional[Utilization] = None
    checkpoint_path: Optional[str] = None
