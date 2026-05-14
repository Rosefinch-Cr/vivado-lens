"""Simulation command: compile, elaborate, simulate, parse results."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from vivado_lens.config import VivadoConfig
from vivado_lens.execution.local import LocalExecutor
from vivado_lens.execution.tcl import TclBuilder
from vivado_lens.models.base import CommandStatus
from vivado_lens.models.project import ProjectConfig
from vivado_lens.models.sim import SimResult
from vivado_lens.parsers.log import extract_display_output
from vivado_lens.parsers.vcd import parse_vcd


def run_sim(
    project_dir: Path,
    config: VivadoConfig,
    tb_top: Optional[str] = None,
    sim_time: Optional[str] = None,
    parse_waveform: bool = False,
) -> SimResult:
    """Run simulation and return structured result."""
    start = time.time()
    executor = LocalExecutor(config)
    p = project_dir.resolve()
    cfg = ProjectConfig.load(p)
    sim_dir = p / "sim"
    sim_dir.mkdir(exist_ok=True)

    # Collect source files
    if cfg.src_files:
        all_files = [Path(f) for f in cfg.src_files + cfg.tb_files]
    else:
        all_files = (
            list((p / "src").glob("*.v")) + list((p / "src").glob("*.sv"))
            + list((p / "tb").glob("*.v")) + list((p / "tb").glob("*.sv"))
        )
    all_files = [f for f in all_files if f.exists()]

    if not all_files:
        return SimResult(
            status=CommandStatus.FAILED, command="sim",
            execution_time_s=0, errors=["No Verilog/SV files found"],
            testbench_top=tb_top or "",
        )

    tb = tb_top or cfg.sim_top or f"tb_{cfg.top}"

    # xvlog
    sv_flags = "--sv" if any(f.suffix == ".sv" for f in all_files) else ""
    file_list = " ".join(f'"{f}"' for f in all_files)
    xvlog_cmd = f'"{config.xvlog}" {sv_flags} {file_list} --work work --log "{sim_dir}/xvlog.log"'
    result = executor.run_tool([xvlog_cmd], cwd=sim_dir)
    if result.returncode != 0:
        return SimResult(
            status=CommandStatus.FAILED, command="sim",
            execution_time_s=time.time() - start,
            errors=["xvlog compilation failed"], log_tail=result.output[-2000:],
            testbench_top=tb,
        )

    # xelab
    xelab_cmd = (
        f'"{config.xelab}" work.{tb} -s {tb}_sim --debug all '
        f'--timescale 1ns/1ps --log "{sim_dir}/xelab.log"'
    )
    result = executor.run_tool([xelab_cmd], cwd=sim_dir)
    if result.returncode != 0:
        return SimResult(
            status=CommandStatus.FAILED, command="sim",
            execution_time_s=time.time() - start,
            errors=["xelab elaboration failed"], log_tail=result.output[-2000:],
            testbench_top=tb,
        )

    # xsim
    vcd_path = sim_dir / "dump.vcd"
    sim_tcl = sim_dir / "run_sim.tcl"
    sim_tcl.write_text(TclBuilder.sim_script(vcd_path, sim_time))

    xsim_cmd = (
        f'"{config.xsim}" {tb}_sim --tclbatch "{sim_tcl.as_posix()}" '
        f'--log "{sim_dir.as_posix()}/xsim.log"'
    )
    result = executor.run_tool([xsim_cmd], cwd=sim_dir, timeout=600)
    if result.returncode != 0:
        return SimResult(
            status=CommandStatus.FAILED, command="sim",
            execution_time_s=time.time() - start,
            errors=["xsim simulation failed"], log_tail=result.output[-2000:],
            testbench_top=tb,
        )

    # Parse results
    display_output: list[str] = []
    log_path = sim_dir / "xsim.log"
    if log_path.exists():
        display_output = extract_display_output(log_path.read_text(errors="replace"))

    pass_fail = None
    for line in display_output:
        if "PASS" in line.upper():
            pass_fail = True
        elif "FAIL" in line.upper() and pass_fail is None:
            pass_fail = False

    waveform = None
    if parse_waveform and vcd_path.exists():
        waveform = parse_vcd(vcd_path)

    return SimResult(
        status=CommandStatus.SUCCESS,
        command="sim",
        execution_time_s=round(time.time() - start, 1),
        vcd_path=str(vcd_path) if vcd_path.exists() else None,
        display_output=display_output,
        pass_fail=pass_fail,
        testbench_top=tb,
        waveform=waveform,
    )
