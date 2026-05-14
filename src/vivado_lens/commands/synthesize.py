"""Synthesis command: generate Tcl, run Vivado, parse reports."""

from __future__ import annotations

import time
from pathlib import Path

from vivado_lens.config import VivadoConfig
from vivado_lens.execution.local import LocalExecutor
from vivado_lens.execution.tcl import TclBuilder
from vivado_lens.models.base import CommandStatus
from vivado_lens.models.project import ProjectConfig
from vivado_lens.models.synth import SynthResult
from vivado_lens.parsers.timing import parse_timing_report
from vivado_lens.parsers.utilization import parse_utilization_report


def run_synth(project_dir: Path, config: VivadoConfig) -> SynthResult:
    """Run synthesis and return structured result."""
    start = time.time()
    executor = LocalExecutor(config)
    p = project_dir.resolve()
    cfg = ProjectConfig.load(p)
    synth_dir = p / "synth"
    synth_dir.mkdir(exist_ok=True)
    (p / "tcl").mkdir(exist_ok=True)

    # Generate Tcl
    if cfg.xpr_path and Path(cfg.xpr_path).exists():
        tcl_content = TclBuilder.synth_script_project(Path(cfg.xpr_path), synth_dir)
    else:
        src_files = [Path(f) for f in cfg.src_files if Path(f).exists()]
        if not src_files:
            src_files = list((p / "src").glob("*.v")) + list((p / "src").glob("*.sv"))
        xdc_files = [Path(f) for f in cfg.xdc_files if Path(f).exists()]
        if not xdc_files:
            xdc_files = list((p / "src").glob("*.xdc"))
        if not src_files:
            return SynthResult(
                status=CommandStatus.FAILED, command="synth",
                execution_time_s=0, errors=["No source files found"],
            )
        tcl_content = TclBuilder.synth_script_nonproject(
            src_files, xdc_files, cfg.part, cfg.top, synth_dir
        )

    tcl_path = p / "tcl" / "synth.tcl"
    tcl_path.write_text(tcl_content)
    log_path = synth_dir / "vivado_synth.log"

    # Run
    result = executor.run_batch(tcl_path, cwd=synth_dir, log_path=log_path, timeout=1200)

    if result.returncode != 0:
        return SynthResult(
            status=CommandStatus.FAILED, command="synth",
            execution_time_s=round(time.time() - start, 1),
            errors=result.errors, warnings=result.warnings,
            log_tail=result.output[-2000:],
        )

    # Parse reports
    timing = None
    timing_rpt = synth_dir / "timing_summary.rpt"
    if timing_rpt.exists():
        timing = parse_timing_report(timing_rpt.read_text(errors="replace"))

    utilization = None
    util_rpt = synth_dir / "utilization.rpt"
    if util_rpt.exists():
        utilization = parse_utilization_report(util_rpt.read_text(errors="replace"))

    checkpoint = synth_dir / f"{cfg.top}_synth.dcp"

    return SynthResult(
        status=CommandStatus.SUCCESS, command="synth",
        execution_time_s=round(time.time() - start, 1),
        errors=result.errors, warnings=result.warnings,
        timing=timing, utilization=utilization,
        checkpoint_path=str(checkpoint) if checkpoint.exists() else None,
    )
