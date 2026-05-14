"""Tcl script generation for Vivado batch operations."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


class TclBuilder:
    """Generates Tcl scripts for Vivado batch-mode operations."""

    @staticmethod
    def sim_script(vcd_path: Path, sim_time: Optional[str] = None) -> str:
        """Generate xsim tclbatch script."""
        lines = [
            f'open_vcd "{vcd_path.as_posix()}"',
            "log_vcd *",
            f"run {sim_time}" if sim_time else "run all",
            "close_vcd",
            "exit",
        ]
        return "\n".join(lines) + "\n"

    @staticmethod
    def synth_script_project(
        xpr_path: Path, synth_dir: Path
    ) -> str:
        """Generate synth Tcl for project mode (.xpr exists)."""
        return f"""open_project "{xpr_path.as_posix()}"
catch {{reset_run synth_1}}
launch_runs synth_1 -jobs 4
wait_on_run synth_1
open_run synth_1
report_timing_summary -file "{synth_dir.as_posix()}/timing_summary.rpt"
report_utilization -file "{synth_dir.as_posix()}/utilization.rpt"
close_design
close_project
"""

    @staticmethod
    def synth_script_nonproject(
        src_files: list[Path],
        xdc_files: list[Path],
        part: str,
        top: str,
        synth_dir: Path,
    ) -> str:
        """Generate synth Tcl for non-project mode."""
        read_cmds = "\n".join(
            f'read_verilog -sv "{f.as_posix()}"' if f.suffix == ".sv"
            else f'read_verilog "{f.as_posix()}"'
            for f in src_files
        )
        xdc_cmds = "\n".join(f'read_xdc "{f.as_posix()}"' for f in xdc_files)
        return f"""{read_cmds}
{xdc_cmds}
set_part {part}
synth_design -top {top} -part {part}
report_timing_summary -file "{synth_dir.as_posix()}/timing_summary.rpt"
report_utilization -file "{synth_dir.as_posix()}/utilization.rpt"
write_checkpoint -force "{synth_dir.as_posix()}/{top}_synth.dcp"
"""

    @staticmethod
    def impl_script_project(
        xpr_path: Path, impl_dir: Path
    ) -> str:
        """Generate impl Tcl for project mode."""
        return f"""open_project "{xpr_path.as_posix()}"
catch {{reset_run impl_1}}
launch_runs impl_1 -jobs 4
wait_on_run impl_1
open_run impl_1
report_timing_summary -file "{impl_dir.as_posix()}/timing_summary.rpt"
report_utilization -file "{impl_dir.as_posix()}/utilization.rpt"
report_power -file "{impl_dir.as_posix()}/power.rpt"
close_design
close_project
"""

    @staticmethod
    def impl_script_nonproject(
        synth_dcp: Path, top: str, impl_dir: Path
    ) -> str:
        """Generate impl Tcl for non-project mode."""
        return f"""open_checkpoint "{synth_dcp.as_posix()}"
opt_design
place_design
route_design
report_timing_summary -file "{impl_dir.as_posix()}/timing_summary.rpt"
report_utilization -file "{impl_dir.as_posix()}/utilization.rpt"
report_power -file "{impl_dir.as_posix()}/power.rpt"
write_checkpoint -force "{impl_dir.as_posix()}/{top}_impl.dcp"
"""

    @staticmethod
    def bitstream_script(impl_dcp: Path, top: str, impl_dir: Path) -> str:
        """Generate bitstream Tcl."""
        return f"""open_checkpoint "{impl_dcp.as_posix()}"
write_bitstream -force "{impl_dir.as_posix()}/{top}.bit"
"""

    @staticmethod
    def view_script(
        open_cmd: str, mode: str, highlight: Optional[str] = None, top: str = ""
    ) -> str:
        """Generate Tcl for opening Vivado GUI with a specific view."""
        view_tcl = {
            "device": "",
            "schematic": "show_schematic [concat [get_cells] [get_ports]]\n",
            "critical_path": (
                "set paths [get_timing_paths -max_paths 5 -setup]\n"
                "highlight_objects -color red $paths\n"
                "select_objects [get_cells -of_objects $paths]\n"
            ),
            "routing": (
                "set nets [get_nets -hierarchical -filter {ROUTE_STATUS != INTRASITE}]\n"
                "select_objects [lrange $nets 0 99]\n"
            ),
            "utilization": "report_utilization -hierarchical\n",
            "timing": "report_timing -setup -hold -max_paths 10 -return_string\n",
            "power": "report_power -return_string\n",
            "highlight_module": (
                f"select_objects [get_cells -hierarchical -filter {{NAME =~ *{highlight or top}*}}]\n"
                "highlight_objects -color yellow [get_selected_objects]\n"
            ),
        }
        return open_cmd + view_tcl.get(mode, "")
