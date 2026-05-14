"""View command: launch Vivado GUI for spatial inspection."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from vivado_lens.config import VivadoConfig
from vivado_lens.execution.tcl import TclBuilder
from vivado_lens.models.base import CommandStatus, VivadoResult
from vivado_lens.models.project import ProjectConfig


def open_view(
    project_dir: Path,
    config: VivadoConfig,
    mode: str = "device",
    stage: str = "impl",
    highlight: Optional[str] = None,
) -> VivadoResult:
    """Launch Vivado GUI with a specific view mode."""
    p = project_dir.resolve()
    cfg = ProjectConfig.load(p)
    (p / "tcl").mkdir(exist_ok=True)

    # Build open command
    if cfg.xpr_path and Path(cfg.xpr_path).exists():
        xpr = Path(cfg.xpr_path).as_posix()
        run_name = "impl_1" if stage == "impl" else "synth_1"
        open_cmd = f'open_project "{xpr}"\nopen_run {run_name}\n'
    else:
        dcp_map = {
            "impl": p / "impl" / f"{cfg.top}_impl.dcp",
            "synth": p / "synth" / f"{cfg.top}_synth.dcp",
        }
        dcp = dcp_map.get(stage)
        if not dcp or not dcp.exists():
            return VivadoResult(
                status=CommandStatus.FAILED, command="view",
                execution_time_s=0,
                errors=[f"No {stage} checkpoint found: {dcp}"],
            )
        open_cmd = f'open_checkpoint "{dcp.as_posix()}"\n'

    # Generate Tcl
    tcl_content = TclBuilder.view_script(open_cmd, mode, highlight, cfg.top)
    tcl_path = p / "tcl" / "view.tcl"
    tcl_path.write_text(tcl_content)

    # Launch Vivado GUI (fire-and-forget)
    vivado = config.vivado
    subprocess.Popen(
        f'"{vivado}" -mode gui -source "{tcl_path}"',
        shell=True, cwd=str(p),
    )

    return VivadoResult(
        status=CommandStatus.SUCCESS, command="view",
        execution_time_s=0,
        errors=[], warnings=[],
        log_tail=f"Vivado GUI launched: {stage}/{mode}",
    )
