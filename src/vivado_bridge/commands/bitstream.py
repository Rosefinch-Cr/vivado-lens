"""Bitstream generation command."""

from __future__ import annotations

import time
from pathlib import Path

from vivado_bridge.config import VivadoConfig
from vivado_bridge.execution.local import LocalExecutor
from vivado_bridge.execution.tcl import TclBuilder
from vivado_bridge.models.base import CommandStatus, VivadoResult
from vivado_bridge.models.project import ProjectConfig


def run_bitstream(project_dir: Path, config: VivadoConfig) -> VivadoResult:
    """Generate bitstream from implementation checkpoint."""
    start = time.time()
    executor = LocalExecutor(config)
    p = project_dir.resolve()
    cfg = ProjectConfig.load(p)
    impl_dir = p / "impl"
    (p / "tcl").mkdir(exist_ok=True)

    dcp = impl_dir / f"{cfg.top}_impl.dcp"
    if not dcp.exists():
        return VivadoResult(
            status=CommandStatus.FAILED, command="bit",
            execution_time_s=0,
            errors=[f"No impl checkpoint: {dcp}. Run impl first."],
        )

    tcl_content = TclBuilder.bitstream_script(dcp, cfg.top, impl_dir)
    tcl_path = p / "tcl" / "bitstream.tcl"
    tcl_path.write_text(tcl_content)
    log_path = impl_dir / "vivado_bit.log"

    result = executor.run_batch(tcl_path, cwd=impl_dir, log_path=log_path, timeout=1200)

    bit_path = impl_dir / f"{cfg.top}.bit"

    if result.returncode != 0:
        return VivadoResult(
            status=CommandStatus.FAILED, command="bit",
            execution_time_s=round(time.time() - start, 1),
            errors=result.errors, warnings=result.warnings,
            log_tail=result.output[-2000:],
        )

    return VivadoResult(
        status=CommandStatus.SUCCESS, command="bit",
        execution_time_s=round(time.time() - start, 1),
        errors=result.errors, warnings=result.warnings,
        log_tail=str(bit_path) if bit_path.exists() else "bitstream not found",
    )
