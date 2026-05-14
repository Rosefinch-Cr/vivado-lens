"""Simulation result models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from vivado_lens.models.base import VivadoResult


class SignalTrace(BaseModel):
    """A single signal's value changes over time."""

    name: str
    width: int = 1
    transitions: list[tuple[int, int]] = Field(default_factory=list)


class WaveformData(BaseModel):
    """Parsed VCD waveform data."""

    timescale: str = "1ns"
    signals: list[SignalTrace] = Field(default_factory=list)
    duration: int = 0


class SimResult(VivadoResult):
    """Result of a simulation run."""

    vcd_path: Optional[str] = None
    display_output: list[str] = Field(default_factory=list)
    pass_fail: Optional[bool] = None
    testbench_top: str = ""
    waveform: Optional[WaveformData] = None
