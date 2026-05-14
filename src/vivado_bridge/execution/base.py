"""Abstract executor interface for future SSH extensibility."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


@dataclass
class RunResult:
    """Raw result of running a Vivado process."""

    returncode: int
    output: str
    elapsed_s: float
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ExecutorBase(ABC):
    """Interface for executing Vivado commands."""

    @abstractmethod
    def run_batch(
        self,
        tcl_path: Path,
        cwd: Path,
        log_path: Path,
        timeout: int = 1200,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> RunResult:
        """Run Vivado in batch mode with a Tcl script."""
        ...

    @abstractmethod
    def run_tool(self, cmd: list[str], cwd: Path, timeout: int = 600) -> RunResult:
        """Run a Vivado sub-tool (xvlog, xelab, xsim)."""
        ...

    @abstractmethod
    def kill_processes(self, names: list[str]) -> None:
        """Kill named processes (for cleanup)."""
        ...
