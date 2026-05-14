"""CLI entry point for vivado-bridge."""

from __future__ import annotations

import json
from pathlib import Path

import click

from vivado_bridge import __version__


def _output(result, fmt: str) -> None:
    """Output a result in the requested format."""
    if fmt == "json":
        click.echo(result.model_dump_json(indent=2))
    elif fmt == "summary":
        status = result.status.value.upper()
        t = result.execution_time_s
        errs = len(result.errors)
        warns = len(getattr(result, "warnings", []))
        click.echo(f"[{status}] {result.command} in {t:.1f}s ({errs} errors, {warns} warnings)")
    elif fmt == "text":
        _output_rich(result)
    else:
        click.echo(result.model_dump_json(indent=2))


def _output_rich(result) -> None:
    """Render result as rich tables for human reading."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text

    console = Console()
    status_color = "green" if result.status.value == "success" else "red"
    header = Text(f" {result.command.upper()} ", style=f"bold {status_color}")
    header.append(f" {result.execution_time_s:.1f}s", style="dim")
    if result.errors:
        header.append(f"  {len(result.errors)} errors", style="red")
    if result.warnings:
        header.append(f"  {len(result.warnings)} warnings", style="yellow")
    console.print(header)

    data = result.model_dump(exclude={"timestamp", "log_tail", "waveform"})

    # Timing table
    timing = getattr(result, "timing", None)
    if timing:
        t = Table(title="Timing", show_header=True, header_style="bold cyan")
        t.add_column("Check", style="white")
        t.add_column("Slack (ns)", justify="right")
        t.add_column("Status", justify="center")
        if timing.slack:
            s = timing.slack
            for name, val, fail in [
                ("Setup", s.setup_ns, s.setup_failing),
                ("Hold", s.hold_ns, s.hold_failing),
                ("Pulse Width", s.pulse_width_ns, s.pw_failing),
            ]:
                color = "green" if fail == 0 else "red"
                status_txt = "MET" if fail == 0 else f"FAIL({fail})"
                t.add_row(name, f"{val:+.3f}", f"[{color}]{status_txt}[/{color}]")
        if timing.clocks:
            for clk in timing.clocks:
                t.add_row(f"Clock: {clk.name}", f"{clk.period_ns} ns", f"{clk.frequency_mhz} MHz")
        console.print(t)

        if timing.critical_path:
            cp = timing.critical_path
            console.print(f"  Critical path: [cyan]{cp.source}[/] → [cyan]{cp.destination}[/]")
            console.print(f"  Delay: {cp.data_path_delay_ns}ns (logic {cp.logic_pct:.0f}% / route {cp.route_pct:.0f}%)")

    # Utilization table
    utilization = getattr(result, "utilization", None)
    if utilization:
        t = Table(title="Utilization", show_header=True, header_style="bold cyan")
        t.add_column("Resource", style="white")
        t.add_column("Used", justify="right")
        t.add_column("Available", justify="right")
        t.add_column("%", justify="right")
        for group in [utilization.slice_logic, utilization.memory, utilization.dsp, utilization.io]:
            for r in group:
                if r.used > 0:
                    color = "green" if r.utilization_pct < 50 else "yellow" if r.utilization_pct < 80 else "red"
                    t.add_row(r.name, str(r.used), str(r.available), f"[{color}]{r.utilization_pct:.1f}[/{color}]")
        if t.row_count > 0:
            console.print(t)

    # Power table
    power = getattr(result, "power", None)
    if power:
        t = Table(title="Power", show_header=True, header_style="bold cyan")
        t.add_column("Component", style="white")
        t.add_column("Watts", justify="right")
        t.add_column("% Dynamic", justify="right")
        t.add_row("[bold]Total[/bold]", f"{power.total_w:.3f}", "")
        t.add_row("  Dynamic", f"{power.dynamic_w:.3f}", "")
        t.add_row("  Static", f"{power.static_w:.3f}", "")
        for comp in power.components:
            t.add_row(f"  {comp.name}", f"{comp.watts:.3f}", f"{comp.pct_of_dynamic:.0f}%")
        console.print(t)
        console.print(f"  Junction Temp: {power.junction_temp_c}°C | Confidence: {power.confidence}")

    # Sim-specific
    display_output = getattr(result, "display_output", None)
    if display_output:
        console.print(Panel("\n".join(display_output), title="Simulation Output", border_style="cyan"))
        pf = getattr(result, "pass_fail", None)
        if pf is True:
            console.print("[bold green]PASS[/bold green]")
        elif pf is False:
            console.print("[bold red]FAIL[/bold red]")


@click.group()
@click.version_option(__version__)
def main():
    """vivado-bridge: Agent-native Vivado automation."""
    pass


@main.command()
@click.option("--project", required=True, help="Project directory")
def status(project: str):
    """Check progress of a running operation."""
    project_dir = Path(project)
    for stage in ["synth", "impl"]:
        progress_file = project_dir / stage / "progress.json"
        if progress_file.exists():
            click.echo(progress_file.read_text())
            return
    click.echo(json.dumps({"done": True, "phase": "idle"}))


@main.command("open")
@click.option("--xpr", required=True, help="Path to .xpr file")
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "summary", "text"]))
def cmd_open(xpr: str, fmt: str):
    """Open an existing Vivado .xpr project."""
    from vivado_bridge.client import VivadoBridge

    bridge = VivadoBridge.local()
    cfg = bridge.open_project(Path(xpr))
    if fmt == "summary":
        click.echo(f"Opened: part={cfg.part}, top={cfg.top}, {len(cfg.src_files)} sources")
    else:
        click.echo(cfg.model_dump_json(indent=2))


@main.command()
@click.option("--project", required=True)
@click.option("--part", required=True)
@click.option("--top", default="top")
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "summary", "text"]))
def init(project: str, part: str, top: str, fmt: str):
    """Initialize a new project."""
    from vivado_bridge.client import VivadoBridge

    bridge = VivadoBridge.local()
    cfg = bridge.init_project(Path(project), part, top)
    if fmt == "summary":
        click.echo(f"Initialized: {project}, part={part}, top={top}")
    else:
        click.echo(cfg.model_dump_json(indent=2))


@main.command()
@click.option("--project", required=True)
@click.option("--tb-top", default=None)
@click.option("--time", "sim_time", default=None)
@click.option("--parse-waveform", is_flag=True, default=False)
@click.option("--open-waveform", is_flag=True, default=False)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "summary", "text"]))
def sim(project: str, tb_top: str, sim_time: str, parse_waveform: bool, open_waveform: bool, fmt: str):
    """Run simulation."""
    import subprocess
    from vivado_bridge.client import VivadoBridge
    from vivado_bridge.config import VivadoConfig

    bridge = VivadoBridge.local()
    result = bridge.simulate(Path(project), tb_top, sim_time, parse_waveform)
    _output(result, fmt)

    if open_waveform and result.vcd_path:
        config = VivadoConfig()
        if config.surfer_exe.exists():
            subprocess.Popen([str(config.surfer_exe), result.vcd_path])


@main.command()
@click.option("--project", required=True)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "summary", "text"]))
def synth(project: str, fmt: str):
    """Run synthesis."""
    from vivado_bridge.client import VivadoBridge

    bridge = VivadoBridge.local()
    result = bridge.synthesize(Path(project))
    _output(result, fmt)


@main.command()
@click.option("--project", required=True)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "summary", "text"]))
def impl(project: str, fmt: str):
    """Run implementation."""
    from vivado_bridge.client import VivadoBridge

    bridge = VivadoBridge.local()
    result = bridge.implement(Path(project))
    _output(result, fmt)


@main.command()
@click.option("--project", required=True)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "summary", "text"]))
def bit(project: str, fmt: str):
    """Generate bitstream."""
    from vivado_bridge.client import VivadoBridge

    bridge = VivadoBridge.local()
    result = bridge.bitstream(Path(project))
    _output(result, fmt)


@main.command()
@click.option("--project", required=True)
@click.option("--mode", required=True,
              type=click.Choice(["device", "schematic", "critical_path", "routing",
                                 "utilization", "timing", "power", "highlight_module"]))
@click.option("--stage", default="impl", type=click.Choice(["synth", "impl"]))
@click.option("--highlight", default=None, help="Module/cell name pattern to highlight")
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "summary", "text"]))
def view(project: str, mode: str, stage: str, highlight: str, fmt: str):
    """Open Vivado GUI with a specific view."""
    from vivado_bridge.client import VivadoBridge

    bridge = VivadoBridge.local()
    result = bridge.view(Path(project), mode, stage, highlight)
    _output(result, fmt)


@main.command()
@click.option("--project", required=True)
@click.option("--type", "rtype", required=True, type=click.Choice(["timing", "utilization", "power"]))
@click.option("--stage", default="impl", type=click.Choice(["synth", "impl"]))
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "text"]))
def report(project: str, rtype: str, stage: str, fmt: str):
    """Read and parse a report."""
    from vivado_bridge.parsers.timing import parse_timing_report
    from vivado_bridge.parsers.utilization import parse_utilization_report
    from vivado_bridge.parsers.power import parse_power_report

    project_dir = Path(project)
    if rtype == "timing":
        rpt_path = project_dir / stage / "timing_summary.rpt"
    elif rtype == "utilization":
        rpt_path = project_dir / stage / "utilization.rpt"
    elif rtype == "power":
        rpt_path = project_dir / stage / "power.rpt"
    else:
        rpt_path = project_dir / stage / f"{rtype}.rpt"

    if not rpt_path.exists():
        click.echo(json.dumps({"error": f"Report not found: {rpt_path}"}))
        raise SystemExit(1)

    content = rpt_path.read_text(errors="replace")
    if fmt == "text":
        click.echo(content[-4000:])
        return

    if rtype == "timing":
        click.echo(parse_timing_report(content).model_dump_json(indent=2))
    elif rtype == "utilization":
        click.echo(parse_utilization_report(content).model_dump_json(indent=2))
    elif rtype == "power":
        click.echo(parse_power_report(content).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
