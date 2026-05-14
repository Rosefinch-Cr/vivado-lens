"""Implementation command: place & route, parse reports."""

from __future__ import annotations

import time
from pathlib import Path

from vivado_lens.config import VivadoConfig
from vivado_lens.execution.local import LocalExecutor
from vivado_lens.execution.tcl import TclBuilder
from vivado_lens.models.base import CommandStatus
from vivado_lens.models.impl import ImplResult
from vivado_lens.models.project import ProjectConfig
from vivado_lens.parsers.power import parse_power_report
from vivado_lens.parsers.timing import parse_timing_report
from vivado_lens.parsers.utilization import parse_utilization_report


def run_impl(project_dir: Path, config: VivadoConfig) -> ImplResult:
    """Run implementation and return structured result."""
    start = time.time()
    executor = LocalExecutor(config)
    p = project_dir.resolve()
    cfg = ProjectConfig.load(p)
    synth_dir = p / "synth"
    impl_dir = p / "impl"
    impl_dir.mkdir(exist_ok=True)
    (p / "tcl").mkdir(exist_ok=True)

    # Generate Tcl
    if cfg.xpr_path and Path(cfg.xpr_path).exists():
        tcl_content = TclBuilder.impl_script_project(Path(cfg.xpr_path), impl_dir)
    else:
        dcp = synth_dir / f"{cfg.top}_synth.dcp"
        if not dcp.exists():
            return ImplResult(
                status=CommandStatus.FAILED, command="impl",
                execution_time_s=0,
                errors=[f"No synth checkpoint: {dcp}. Run synth first."],
            )
        tcl_content = TclBuilder.impl_script_nonproject(dcp, cfg.top, impl_dir)

    tcl_path = p / "tcl" / "impl.tcl"
    tcl_path.write_text(tcl_content)
    log_path = impl_dir / "vivado_impl.log"

    # Run
    result = executor.run_batch(tcl_path, cwd=impl_dir, log_path=log_path, timeout=1800)

    if result.returncode != 0:
        return ImplResult(
            status=CommandStatus.FAILED, command="impl",
            execution_time_s=round(time.time() - start, 1),
            errors=result.errors, warnings=result.warnings,
            log_tail=result.output[-2000:],
        )

    # Parse reports
    timing = None
    timing_rpt = impl_dir / "timing_summary.rpt"
    if timing_rpt.exists():
        timing = parse_timing_report(timing_rpt.read_text(errors="replace"))

    utilization = None
    util_rpt = impl_dir / "utilization.rpt"
    if util_rpt.exists():
        utilization = parse_utilization_report(util_rpt.read_text(errors="replace"))

    power = None
    power_rpt = impl_dir / "power.rpt"
    if power_rpt.exists():
        power = parse_power_report(power_rpt.read_text(errors="replace"))

    checkpoint = impl_dir / f"{cfg.top}_impl.dcp"

    return ImplResult(
        status=CommandStatus.SUCCESS, command="impl",
        execution_time_s=round(time.time() - start, 1),
        errors=result.errors, warnings=result.warnings,
        timing=timing, utilization=utilization, power=power,
        checkpoint_path=str(checkpoint) if checkpoint.exists() else None,
    )
