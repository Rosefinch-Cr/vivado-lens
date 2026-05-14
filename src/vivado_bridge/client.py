"""VivadoBridge: unified facade for all operations."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from vivado_bridge.config import VivadoConfig
from vivado_bridge.models.base import VivadoResult
from vivado_bridge.models.impl import ImplResult
from vivado_bridge.models.project import ProjectConfig
from vivado_bridge.models.sim import SimResult
from vivado_bridge.models.synth import SynthResult


class VivadoBridge:
    """Main entry point for vivado-bridge operations.

    Usage:
        bridge = VivadoBridge.local()
        result = bridge.simulate(Path("my_project"))
    """

    def __init__(self, config: VivadoConfig | None = None):
        self.config = config or VivadoConfig()

    @classmethod
    def local(cls, vivado_bin: str | Path | None = None) -> "VivadoBridge":
        """Create a bridge for local Vivado execution."""
        config = VivadoConfig()
        if vivado_bin:
            config.vivado_bin = Path(vivado_bin)
        return cls(config=config)

    def open_project(self, xpr_path: Path) -> ProjectConfig:
        from vivado_bridge.commands.project import open_project
        return open_project(xpr_path)

    def init_project(self, project_dir: Path, part: str, top: str = "top") -> ProjectConfig:
        from vivado_bridge.commands.project import init_project
        return init_project(project_dir, part, top)

    def simulate(
        self,
        project_dir: Path,
        tb_top: Optional[str] = None,
        sim_time: Optional[str] = None,
        parse_waveform: bool = False,
    ) -> SimResult:
        from vivado_bridge.commands.simulate import run_sim
        return run_sim(project_dir, self.config, tb_top, sim_time, parse_waveform)

    def synthesize(self, project_dir: Path) -> SynthResult:
        from vivado_bridge.commands.synthesize import run_synth
        return run_synth(project_dir, self.config)

    def implement(self, project_dir: Path) -> ImplResult:
        from vivado_bridge.commands.implement import run_impl
        return run_impl(project_dir, self.config)

    def view(
        self,
        project_dir: Path,
        mode: str = "device",
        stage: str = "impl",
        highlight: Optional[str] = None,
    ) -> VivadoResult:
        from vivado_bridge.commands.view import open_view
        return open_view(project_dir, self.config, mode, stage, highlight)

    def bitstream(self, project_dir: Path) -> VivadoResult:
        from vivado_bridge.commands.bitstream import run_bitstream
        return run_bitstream(project_dir, self.config)

