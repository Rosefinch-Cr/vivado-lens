"""Parse Vivado log files for phases, errors, and warnings."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class LogSummary:
    """Parsed summary of a Vivado log file."""

    phases: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    tail: str = ""

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


_PHASE_RE = re.compile(r"(Phase \d+|Starting|Finished)", re.IGNORECASE)


def parse_vivado_log(content: str, tail_lines: int = 20) -> LogSummary:
    """Parse a Vivado log for phases, errors, and warnings."""
    phases: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("ERROR:") or "] ERROR:" in line:
            errors.append(stripped)
        if stripped.startswith("WARNING:") or "] WARNING:" in line or "CRITICAL WARNING:" in line:
            warnings.append(stripped)
        if _PHASE_RE.search(line):
            phases.append(stripped)

    lines = content.splitlines()
    tail = "\n".join(lines[-tail_lines:]) if len(lines) > tail_lines else content

    return LogSummary(phases=phases, errors=errors, warnings=warnings, tail=tail)


def extract_display_output(content: str) -> list[str]:
    """Extract $display/$write messages from xsim log."""
    display_lines: list[str] = []
    for line in content.splitlines():
        if line.startswith(("##", "#", "source", "INFO:", "Vivado Sim", "Time res")):
            continue
        if line.startswith(("---", "***")):
            continue
        if line.strip():
            display_lines.append(line.strip())
    return display_lines
